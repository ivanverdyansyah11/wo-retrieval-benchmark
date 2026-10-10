"""CPU-only V2 lexical preparation and dense reuse audit; never load weights.

Uses the existing serializer, tokenizer, fitters and cache validators. Frozen
protocol and source modules stay unchanged; snapshot binding is an in-memory
overlay, not a new experimental parameter. Existing production CLIs remain V1.
"""
import argparse
import copy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from uuid import uuid4

import numpy as np
from scipy import sparse
from rank_bm25 import BM25Okapi

from wo_retrieval.retrieval.lexical import (
    LexicalRetriever, checked_path, digest, file_hash, identity, load,
    prepare, read_protocol, verify_snapshot, write_json,
)
from wo_retrieval.dense.index import cache_identity, cache_paths, validate_matrix
from wo_retrieval.query_vectors.offline import load_components


VERSION = Path("data/versions/v2_ai_corrected")
SNAPSHOT = "WO-CORPUS-V2-AI-CORRECTED-PILOT-001"
FINGERPRINT = "78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6"
INDEX_VERSION = "v2_ai_corrected"


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines()]


def bind_v2(root):
    config = copy.deepcopy(read_protocol(root))
    parent = verify_snapshot(root, config)
    for relative, expected in parent["source_document_sha256"].items():
        if file_hash(checked_path(root, relative)) != expected:
            raise ValueError("V1 source checksum mismatch: " + relative)
    relative = (VERSION / "validation/pilot_snapshot.json").as_posix()
    snapshot = json.loads((root / relative).read_text(encoding="utf8"))
    if (snapshot["snapshot_id"] != SNAPSHOT or snapshot["aggregate_fingerprint"]["value"] != FINGERPRINT
            or snapshot["parent_fingerprint"] != parent["aggregate_fingerprint"]["value"]):
        raise ValueError("Unexpected V2 snapshot or parent")
    config["snapshot"].update(id=SNAPSHOT, corpus_version=snapshot["corpus_version"],
        validation_status=snapshot["validation_status"], manifest_path=relative,
        manifest_sha256=file_hash(root / relative), aggregate_fingerprint=FINGERPRINT,
        artifact_sha256=snapshot["artifact_sha256"], chunks_path=(VERSION / "chunks/chunks.jsonl").as_posix())
    verify_snapshot(root, config)
    for relative, expected in snapshot["source_file_sha256"].items():
        if file_hash(checked_path(root, relative)) != expected:
            raise ValueError("V2 source checksum mismatch: " + relative)
    documents = jsonl(root / VERSION / "processed/documents.jsonl")
    chunks = jsonl(root / config["snapshot"]["chunks_path"])
    ids = [row["document_id"] for row in documents]
    if (len(ids) != 50 or len(set(ids)) != 50 or len(chunks) != 371
            or {row["document_id"] for row in chunks} != set(ids)):
        raise ValueError("Invalid V2 canonical universe")
    # prepare checks V1 canonical IDs too; V2 canonical contents are verified above.
    # It serializes only config.snapshot.chunks_path, never V1 document text.
    rows, statistics = prepare(root, config)
    saved = jsonl(root / VERSION / "reports/serialized_inputs.jsonl")
    if {r["chunk_id"]: r["text"] for r in rows} != {r["chunk_id"]: r["text"] for r in saved}:
        raise ValueError("Shared serializer differs from frozen V2 audit")
    qrels = json.loads((root / VERSION / "benchmark/development_qrels_ai_silver_v2_manifest.json").read_text(encoding="utf8"))
    if qrels["snapshot_id"] != SNAPSHOT or qrels["snapshot_fingerprint"] != FINGERPRINT:
        raise ValueError("V2 query/qrels binding mismatch")
    for relative, expected in qrels["artifact_sha256"].items():
        if file_hash(checked_path(root, relative)) != expected:
            raise ValueError("V2 benchmark artifact checksum mismatch")
    queries = jsonl(root / qrels["query_dataset_path"])
    if file_hash(root / qrels["query_dataset_path"]) != qrels["query_dataset_sha256"] or len(queries) != 18:
        raise ValueError("Original development query checksum/count mismatch")
    return config, rows, statistics


def verify_index(directory, rows, config, expected_identity, statistics):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf8"))
    if (manifest.get("completion_status") != "COMPLETE"
            or any(manifest.get(k) != v for k, v in expected_identity.items())
            or manifest.get("index_fingerprint") != digest({k: v for k, v in manifest.items() if k != "index_fingerprint"})
            or manifest.get("serialization_statistics") != statistics or manifest.get("indexed_chunks") != len(rows)):
        raise ValueError("Index identity/status/fingerprint mismatch")
    method = expected_identity["method_id"]
    required = {"documents.json", "model.json"} | ({"matrix.npz"} if method == "R1" else set())
    if set(manifest["artifact_sha256_derived"]) != required:
        raise ValueError("Incomplete index artifact set")
    for name, expected in manifest["artifact_sha256_derived"].items():
        if file_hash(directory / name) != expected:
            raise ValueError("Index artifact checksum mismatch")
    if json.loads((directory / "documents.json").read_text(encoding="utf8")) != rows:
        raise ValueError("Index serialized inputs mismatch")
    state = json.loads((directory / "model.json").read_text(encoding="utf8"))
    retriever = LexicalRetriever(method, rows, config)
    if method == "R1":
        retriever.model = retriever.vectorizer(state["vocabulary"])
        retriever.model.idf_ = np.asarray(state["idf"], dtype=np.float64)
        retriever.matrix = sparse.load_npz(directory / "matrix.npz").tocsr()
        if (retriever.matrix.shape != (len(rows), len(state["idf"]))
                or not np.isfinite(retriever.matrix.data).all()
                or not np.allclose(sparse.linalg.norm(retriever.matrix, axis=1), 1, atol=1e-12)):
            raise ValueError("Invalid TF-IDF matrix")
    else:
        retriever.model = BM25Okapi.__new__(BM25Okapi)
        retriever.model.__dict__.update(state)
        if (state["corpus_size"] != len(rows) or len(state["doc_freqs"]) != len(rows)
                or not np.isfinite(state["average_idf"]) or state["average_idf"] <= 0
                or any(state[k] != config["R2"][k] for k in ("k1", "b", "epsilon"))):
            raise ValueError("Invalid BM25 state")
    retriever.manifest = manifest
    return retriever


def build_index(root, method, rows, config, statistics):
    target = root / "experiments/indexes" / INDEX_VERSION / method
    if target.exists():
        raise FileExistsError("Never overwrite V2 index: " + str(target))
    started = perf_counter()
    retriever = LexicalRetriever(method, rows, config).fit()
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(method + ".incomplete-" + uuid4().hex)
    staging.mkdir()
    write_json(staging / "documents.json", rows)
    if method == "R1":
        sparse.save_npz(staging / "matrix.npz", retriever.matrix)
        write_json(staging / "model.json", {"vocabulary": retriever.model.vocabulary_, "idf": retriever.model.idf_.tolist()})
    else:
        write_json(staging / "model.json", {k: getattr(retriever.model, k) for k in
            ("doc_freqs", "idf", "doc_len", "avgdl", "corpus_size", "average_idf", "k1", "b", "epsilon")})
    expected = identity(root, config, method)
    manifest = {**expected, "completion_status": "COMPLETE", "indexed_chunks": len(rows),
        "serialization_statistics": statistics, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "device": "cpu", "neural_model_loaded": False, "index_binding_version": "v2_development_overlay_v1",
        "builder_sha256": file_hash(Path(__file__)), "validation_status": config["snapshot"]["validation_status"],
        "artifact_sha256_derived": {p.name: file_hash(p) for p in sorted(staging.iterdir())},
        "indexing_seconds_before_validation_publish": perf_counter() - started}
    manifest["index_fingerprint"] = digest(manifest)
    write_json(staging / "manifest.json", manifest)
    verify_index(staging, rows, config, expected, statistics)
    verify_snapshot(root, config)
    staging.rename(target)
    return {"path": str(target), "index_fingerprint": manifest["index_fingerprint"],
        "indexed_chunks": len(rows), "indexing_seconds_before_validation_publish": manifest["indexing_seconds_before_validation_publish"],
        "total_build_validation_publish_seconds": perf_counter() - started,
        "bytes": sum(p.stat().st_size for p in target.iterdir())}


def eligible(old, new, mapped, vector, same_contract=True):
    reasons = []
    if not same_contract:
        reasons.append("model/tokenizer/serialization/precision contract mismatch")
    if (old["chunk_id"], old["document_id"], old["text_sha256"]) != (
            mapped["chunk_id"], mapped["document_id"], mapped["serialized_text_sha256"]):
        reasons.append("V1 vector mapping mismatch")
    if old["text"] != new["text"] or old["text_sha256"] != new["text_sha256"]:
        reasons.append("exact serialized input changed")
    if (old["chunk_id"], old["document_id"]) != (new["chunk_id"], new["document_id"]):
        reasons.append("chunk/document mapping changed")
    try:
        validate_matrix(vector, 1)
    except ValueError:
        reasons.append("vector shape/dtype/finiteness/L2 invalid")
    return {"status": "REQUIRES_REEMBEDDING" if reasons else "REUSABLE_VERIFIED", "reasons": reasons}


def run(root, corpus_index, verify_only=False):
    started = perf_counter()
    config, rows, statistics = bind_v2(root)
    v1 = {m: load(root, m) for m in ("R1", "R2")}
    old_rows = v1["R2"].rows
    if v1["R1"].rows != old_rows:
        raise ValueError("V1 lexical parity mismatch")
    if [r["chunk_id"] for r in rows] != [r["chunk_id"] for r in old_rows]:
        raise ValueError("Chunk universe/order mismatch")
    bm25, vectors, dense_manifest, _, local = load_components(root, corpus_index)
    if bm25.rows != old_rows:
        raise ValueError("Dense/lexical V1 input mismatch")
    mapped = json.loads((corpus_index / "rows.json").read_text(encoding="utf8"))
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(local / "tokenizer.json"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    lengths = json.loads((root / VERSION / "reports/tokenizer_lengths.json").read_text(encoding="utf8"))
    length_by_id = {r["chunk_id"]: r for r in lengths}
    mapping, reuse = [], []
    for i, (old, new, source) in enumerate(zip(old_rows, rows, mapped, strict=True)):
        token_count = len(tokenizer.encode(new["text"], add_special_tokens=True).ids)
        if (token_count > 640 or token_count != length_by_id[new["chunk_id"]]["serialized_tokens"]
                or new["text_sha256"] != length_by_id[new["chunk_id"]]["serialized_text_sha256"]):
            raise ValueError("V2 tokenizer audit mismatch/truncation")
        if len(tokenizer.encode(old["text"], add_special_tokens=True).ids) != source["token_length"]:
            raise ValueError("V1 tokenizer mapping mismatch")
        mapping.append({"chunk_id": new["chunk_id"], "document_id": new["document_id"],
            "serialized_text_sha256": new["text_sha256"], "token_length": token_count})
        receipt = eligible(old, new, source, vectors[i:i+1])
        reuse.append({"chunk_id": new["chunk_id"], "document_id": new["document_id"],
            "v1_row_index": i, "v2_row_index": i, "v1_input_sha256": old["text_sha256"],
            "v2_input_sha256": new["text_sha256"], "v1_token_length": source["token_length"],
            "v2_token_length": token_count, "vector_raw_float32_sha256": sha256(vectors[i].tobytes()).hexdigest(),
            **receipt})
    target_identity = cache_identity(root, config, statistics, dense_manifest["identity"]["model_file_hashes"], mapping)
    for key in ("model_id", "model_revision", "precision", "storage_dtype", "dimension", "max_length",
                "normalization", "tokenizer", "serializer_version", "serialization_policy_hash", "config_fingerprint",
                "model_file_hashes", "dependency_versions", "official_inference_file_hashes"):
        if target_identity[key] != dense_manifest["identity"][key]:
            raise ValueError("Dense reuse contract mismatch: " + key)
    changed = [r["chunk_id"] for r in reuse if r["status"] == "REQUIRES_REEMBEDDING"]
    frozen_mapping = json.loads((root / VERSION / "reports/v1_v2_chunk_mapping.json").read_text(encoding="utf8"))["rows"]
    if len(frozen_mapping) != len(rows):
        raise ValueError("Frozen V1/V2 mapping count mismatch")
    for old, new, mapped_row in zip(old_rows, rows, frozen_mapping, strict=True):
        if (mapped_row["v1_chunk_id"], mapped_row["v2_chunk_id"], mapped_row["v1_serialized_hash"], mapped_row["v2_serialized_hash"]) != (
                old["chunk_id"], new["chunk_id"], old["text_sha256"], new["text_sha256"]):
            raise ValueError("Frozen V1/V2 mapping differs from current serialized inputs")
    result = {"status": "PASS", "snapshot_id": SNAPSHOT, "snapshot_fingerprint": FINGERPRINT,
        "validation_status": config["snapshot"]["validation_status"], "serialization": statistics,
        "unchanged_serialized_inputs": sum(a["text"] == b["text"] for a, b in zip(old_rows, rows, strict=True)),
        "changed_serialized_inputs": [b["chunk_id"] for a, b in zip(old_rows, rows, strict=True) if a["text"] != b["text"]],
        "reusable_vectors": len(reuse) - len(changed), "requires_reembedding": changed,
        "tokenizer_max": max(r["token_length"] for r in mapping), "truncated": 0,
        "model_loaded": False, "gpu_used": False}
    if verify_only:
        for method in ("R1", "R2"):
            verify_index(root / "experiments/indexes" / INDEX_VERSION / method, rows, config,
                identity(root, config, method), statistics)
        return result
    destinations = root / "experiments/indexes" / INDEX_VERSION
    for name in ("R1", "R2", "dense_reuse_eligibility.json", "dense_completion_plan.json"):
        if (destinations / name).exists():
            raise FileExistsError("Refusing overwrite: " + name)
    result["lexical_indexes"] = {m: build_index(root, m, rows, config, statistics) for m in ("R1", "R2")}
    audit = {**result, "artifact_type": "DENSE_REUSE_ELIGIBILITY_AUDIT_NOT_INDEX", "completion_status": "AUDIT_COMPLETE",
        "r3_v2_ready": False, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_index_path": str(corpus_index), "source_manifest_sha256": file_hash(corpus_index / "manifest.json"),
        "source_index_fingerprint": digest(dense_manifest), "source_identity_fingerprint": digest(dense_manifest["identity"]),
        "source_artifact_sha256": dense_manifest["artifact_sha256"], "source_identity": dense_manifest["identity"],
        "target_identity": target_identity, "target_row_mapping": mapping, "rows": reuse,
        "builder_sha256": file_hash(Path(__file__))}
    audit["audit_fingerprint"] = digest(audit)
    write_json(destinations / "dense_reuse_eligibility.json", audit)
    complete, partial = cache_paths(config, target_identity)
    write_json(destinations / "dense_completion_plan.json", {
        "artifact_type": "PLAN_ONLY_NO_VECTORS", "completion_status": "INCOMPLETE", "r3_v2_ready": False,
        "snapshot_id": SNAPSHOT, "snapshot_fingerprint": FINGERPRINT,
        "eligibility_manifest_sha256": file_hash(destinations / "dense_reuse_eligibility.json"),
        "target_identity": target_identity, "target_identity_fingerprint": digest(target_identity),
        "planned_complete_cache_path": str(complete), "planned_partial_cache_path": str(partial),
        "reusable_count": len(reuse) - len(changed), "requires_reembedding": changed,
        "steps": ["Reverify both snapshots, source index and every eligibility hash before reuse.",
            "After separate approval: resource-gated pinned CUDA FP16 batch1 encoding of changed serialized inputs only, no truncation.",
            "Copy eligible float32 rows bit-for-bit; use existing unit_vectors only for new encoder outputs.",
            "Merge by target_row_mapping (chunk_id sorted); compare to canonical V2 chunk ID set.",
            "Validate 371x1024 float32, finite unit rows; copied row bytes must remain identical.",
            "Write new rows/vectors/COMPLETE manifest with target identity and fresh artifact checksums, then atomic publish after readback.",
            "Reject all partial outputs; no placeholder zero/NaN rows or V1 metadata relabeling."],
        "loader_work_required": ["Explicit V2 snapshot binding and versioned R2 selection; leave V1 defaults intact.",
            "Validate V2 tokenizer mapping against V2 audit, not protocol's historical V1 serialization.audit.fingerprint.",
            "Update approved offline corpus path validation to admit only complete verified V2 cache identity.",
            "Bind shared query artifact contract to completed V2 dense manifest; V1 query cache is not automatically accepted."],
        "retrieval_parameters_changed": False, "gpu_authorized_in_this_task": False})
    verify_snapshot(root, config)
    if any(name in sys.modules for name in ("torch", "transformers", "FlagEmbedding")):
        raise RuntimeError("Unexpected neural runtime import")
    result["neural_runtime_imported"] = False
    result["total_preparation_seconds"] = perf_counter() - started
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--v1-dense-index", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.root.resolve(), args.v1_dense_index.resolve(), args.verify_only), ensure_ascii=False, indent=2))
