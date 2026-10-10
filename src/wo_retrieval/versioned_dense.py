"""Explicit V1/V2 R3 selection and one-shot, resource-gated V2 completion.

Additive module: source files bound by immutable snapshots and V1 CLI defaults
stay untouched. V2 selects a separate binding file, never a metadata fallback.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import perf_counter
import traceback
from uuid import uuid4

import numpy as np

from .dense.index import (DenseRetriever, atomic_json, atomic_vector, cache_identity,
                          load_vectors, validate_matrix)
from .dense.model import BGEEncoder, offline_environment, unit_vectors
from .dense.resources import Monitor, gate, gpu_resource, resource, unsafe
from .query_vectors.offline import load_components as load_v1_components
from .retrieval.lexical import checked_path, digest, file_hash, read_protocol, verify_snapshot, write_json


def other_model_processes():
    import psutil
    matches = []
    for process in psutil.process_iter(["name", "cmdline"]):
        if process.pid == psutil.Process().pid:
            continue
        command = " ".join(process.info.get("cmdline") or []).casefold()
        if any(tag in command for tag in ("wo_retrieval.dense.cli", "wo_retrieval.hybrid.cli", "wo_retrieval.query_vectors", "wo_retrieval.versioned_dense", "baai/bge-m3")):
            matches.append({"pid": process.pid, "name": process.info.get("name")})
    return matches


def read_binding(root):
    path = root / "experiments/configs/dense_v2_binding.json"
    binding = json.loads(path.read_text(encoding="utf8"))
    if (binding.get("schema_version") != "wo_dense_version_binding_v1"
            or binding.get("corpus_version") != "v2"
            or binding.get("snapshot_id") != "WO-CORPUS-V2-AI-CORRECTED-PILOT-001"
            or binding.get("snapshot_fingerprint") != "78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6"
            or binding.get("r3_index") != "experiments/indexes/v2_ai_corrected/R3"):
        raise ValueError("Unsupported explicit V2 binding")
    for key, hash_key in (("snapshot_manifest", "snapshot_sha256"), ("parent_protocol", "parent_protocol_sha256"),
                           ("preparation_script", "preparation_script_sha256"), ("eligibility_manifest", "eligibility_manifest_sha256")):
        if file_hash(checked_path(root, binding[key])) != binding[hash_key]:
            raise ValueError("Binding checksum mismatch: " + key)
    # Reuse the checksum-bound 9A.8 builder/validator rather than duplicating it.
    spec = importlib.util.spec_from_file_location("wo_v2_index_preparation", checked_path(root, binding["preparation_script"]))
    preparation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preparation)
    return binding, preparation


def prepare_v2(root):
    root = Path(root).resolve()
    binding, preparation = read_binding(root)
    config, rows, statistics = preparation.bind_v2(root)
    for key in ("id", "manifest_sha256", "aggregate_fingerprint"):
        expected = binding[{"id": "snapshot_id", "manifest_sha256": "snapshot_sha256", "aggregate_fingerprint": "snapshot_fingerprint"}[key]]
        if config["snapshot"][key] != expected:
            raise ValueError("Explicit snapshot binding differs from verified dataset")
    bm25 = None
    for method, path_key in (("R1", "r1_index"), ("R2", "r2_index")):
        index = checked_path(root, binding[path_key])
        manifest = json.loads((index / "manifest.json").read_text(encoding="utf8"))
        if manifest.get("builder_sha256") != binding["preparation_script_sha256"]:
            raise ValueError("Lexical builder provenance mismatch")
        verified = preparation.verify_index(index, rows, config, preparation.identity(root, config, method), statistics)
        if method == "R2":
            bm25 = verified
    audit = json.loads(checked_path(root, binding["eligibility_manifest"]).read_text(encoding="utf8"))
    if (audit["audit_fingerprint"] != digest({k: v for k, v in audit.items() if k != "audit_fingerprint"})
            or audit["snapshot_fingerprint"] != binding["snapshot_fingerprint"]
            or audit["snapshot_id"] != binding["snapshot_id"]):
        raise ValueError("Dense eligibility audit fingerprint mismatch")
    source = Path(binding["v1_dense_index"]).resolve()
    if str(source) != str(Path(audit["source_index_path"]).resolve()):
        raise ValueError("V1 source index path mismatch")
    old_bm25, vectors, manifest, _, local = load_v1_components(root, source)
    if file_hash(source / "manifest.json") != audit["source_manifest_sha256"] or digest(manifest) != audit["source_index_fingerprint"]:
        raise ValueError("V1 source index fingerprint mismatch")
    mapping = audit["target_row_mapping"]
    if len(mapping) != len(rows) or len(audit["rows"]) != len(rows):
        raise ValueError("Missing Dense mapping/receipt")
    old_mapping = json.loads((source / "rows.json").read_text(encoding="utf8"))
    changed = []
    for i, (old, new, mapped, receipt) in enumerate(zip(old_bm25.rows, rows, mapping, audit["rows"], strict=True)):
        verdict = preparation.eligible(old, new, old_mapping[i], vectors[i:i+1])
        if (receipt["chunk_id"] != new["chunk_id"] or receipt["document_id"] != new["document_id"]
                or receipt["v1_row_index"] != i or receipt["v2_row_index"] != i
                or receipt["v1_input_sha256"] != old["text_sha256"] or receipt["v2_input_sha256"] != new["text_sha256"]
                or receipt["status"] != verdict["status"] or receipt["reasons"] != verdict["reasons"]
                or receipt["vector_raw_float32_sha256"] != sha256(vectors[i].tobytes()).hexdigest()
                or (mapped["chunk_id"], mapped["document_id"], mapped["serialized_text_sha256"]) !=
                   (new["chunk_id"], new["document_id"], new["text_sha256"])):
            raise ValueError("Stale reuse receipt or mapping")
        if receipt["status"] == "REQUIRES_REEMBEDDING":
            changed.append(new["chunk_id"])
    if changed != binding["changed_chunk_ids"] or len(changed) != 2 or len(rows) != 371:
        raise ValueError("Unexpected regeneration set; STOP")
    target_identity = cache_identity(root, config, statistics, manifest["identity"]["model_file_hashes"], mapping)
    if target_identity != audit["target_identity"]:
        raise ValueError("Dense model/config/tokenizer/precision identity changed since reuse audit")
    return {"root": root, "binding": binding, "config": config, "rows": rows, "mapping": mapping,
            "bm25": bm25, "source_vectors": vectors, "source_manifest": manifest,
            "audit": audit, "identity": target_identity, "local": local}


def load_components(root, corpus_version="v1", v1_dense_index=None):
    """Read-only, explicit version selection. Never load a neural model."""
    root = Path(root).resolve()
    if corpus_version == "v1":
        if v1_dense_index is None:
            raise ValueError("V1 selection requires an explicit existing Dense cache path")
        return load_v1_components(root, Path(v1_dense_index).resolve())
    if corpus_version != "v2" or v1_dense_index is not None:
        raise ValueError("Unsupported version/path combination; no fallback")
    context = prepare_v2(root)
    directory = checked_path(root, context["binding"]["r3_index"])
    vectors, manifest = load_vectors(directory, context["identity"], context["mapping"])
    if manifest.get("version_binding_sha256") != file_hash(root / "experiments/configs/dense_v2_binding.json"):
        raise ValueError("Dense V2 binding checksum mismatch")
    if manifest.get("completion_code_sha256") != file_hash(Path(__file__)):
        raise ValueError("Dense V2 completion code checksum mismatch")
    return context["bm25"], vectors, manifest, context["config"], context["local"]


def assemble(rows, mapping, identity, source_vectors, receipts, new_records):
    """No inference here; merge only fully validated input-bound vectors."""
    count = len(rows)
    validate_matrix(source_vectors, count)
    if len(mapping) != count or len(receipts) != count or digest(mapping) != identity["row_mapping_hash"]:
        raise ValueError("Missing/mismatched mapping")
    ids = [row["chunk_id"] for row in rows]
    if len(set(ids)) != count or ids != sorted(ids):
        raise ValueError("Duplicate/unordered canonical chunk IDs")
    wanted = {row["chunk_id"] for row in receipts if row["status"] == "REQUIRES_REEMBEDDING"}
    if set(new_records) != wanted:
        raise ValueError("Missing/extra new embeddings")
    merged = []
    for i, (row, mapped, receipt) in enumerate(zip(rows, mapping, receipts, strict=True)):
        if (row["chunk_id"], row["document_id"], row["text_sha256"]) != (
                mapped["chunk_id"], mapped["document_id"], mapped["serialized_text_sha256"]):
            raise ValueError("Input hash/document mapping mismatch")
        if (receipt["chunk_id"] != row["chunk_id"] or receipt["document_id"] != row["document_id"]
                or receipt["v1_row_index"] != i or receipt["v2_row_index"] != i
                or receipt["v2_input_sha256"] != row["text_sha256"]
                or receipt["vector_raw_float32_sha256"] != sha256(source_vectors[i].tobytes()).hexdigest()):
            raise ValueError("Reuse receipt/source vector mismatch")
        if receipt["status"] == "REUSABLE_VERIFIED":
            if receipt["v1_input_sha256"] != row["text_sha256"]:
                raise ValueError("Reusable input hash mismatch")
            merged.append(source_vectors[i:i+1])
        elif receipt["status"] == "REQUIRES_REEMBEDDING":
            record = new_records[row["chunk_id"]]
            for key in ("model_id", "model_revision", "precision", "device", "max_length", "normalization", "dimension"):
                if record.get(key) != identity[key]:
                    raise ValueError("New embedding contract mismatch: " + key)
            if (record.get("input_sha256") != row["text_sha256"] or record.get("truncation") is not False
                    or record.get("actual_tokens") != mapped["token_length"] or not 0 < mapped["token_length"] <= 640):
                raise ValueError("New embedding input/token hash mismatch")
            merged.append(validate_matrix(record["vector"], 1))
        else:
            raise ValueError("Unsupported reuse status")
    matrix = validate_matrix(np.concatenate(merged), count)
    for i, receipt in enumerate(receipts):
        if receipt["status"] == "REUSABLE_VERIFIED" and matrix[i].tobytes() != source_vectors[i].tobytes():
            raise ValueError("Reusable vector bytes changed")
    return matrix


def publish(context, new_records, verify_before_publish):
    root, binding = context["root"], context["binding"]
    directory = checked_path(root, binding["r3_index"])
    if directory.exists():
        raise FileExistsError("Never overwrite an existing R3 V2 index")
    matrix = assemble(context["rows"], context["mapping"], context["identity"], context["source_vectors"], context["audit"]["rows"], new_records)
    staging = directory.with_name(directory.name + ".incomplete-" + uuid4().hex)
    staging.mkdir(parents=True)
    atomic_json(staging / "manifest.json", {"completion_status": "INCOMPLETE", "identity": context["identity"]})
    atomic_vector(staging / "vectors.npy", matrix)
    write_json(staging / "rows.json", context["mapping"])
    manifest = {"completion_status": "COMPLETE", "identity": context["identity"],
        "indexed_chunks": len(matrix), "shape": list(matrix.shape), "missing_chunks": 0, "duplicate_chunk_ids": 0,
        "finite": True, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "version_binding_sha256": file_hash(root / "experiments/configs/dense_v2_binding.json"),
        "completion_code_sha256": file_hash(Path(__file__)), "reused_verified_vectors": len(matrix) - len(new_records),
        "new_vectors": len(new_records), "source_index_manifest_sha256": context["audit"]["source_manifest_sha256"],
        "eligibility_manifest_sha256": binding["eligibility_manifest_sha256"],
        "new_embedding_metadata": {k: {f: v for f, v in item.items() if f != "vector"} for k, item in new_records.items()},
        "artifact_sha256": {name: file_hash(staging / name) for name in ("vectors.npy", "rows.json")}}
    try:
        # Validate COMPLETE payload in unpublished staging, then recheck sources.
        atomic_json(staging / "manifest.json", manifest)
        load_vectors(staging, context["identity"], context["mapping"])
        verify_before_publish()
        staging.rename(directory)
    except BaseException:
        atomic_json(staging / "manifest.json", {**manifest, "completion_status": "INCOMPLETE"})
        raise
    return manifest


def complete_v2(root, approved_low_memory=False, approval_note=None):
    if not approval_note or not approval_note.strip():
        raise ValueError("One-shot completion requires explicit approval note")
    root = Path(root).resolve()
    offline_environment()
    config = read_protocol(root)
    policy = {**config["hardware"], "stop_available_ram_mib": 2048, "stop_sustained_seconds": 0}
    run_dir = root / "experiments/indexes/v2_ai_corrected" / ("R3.run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    run_dir.mkdir(parents=True)
    report = {"status": "INCOMPLETE", "loading": "NOT RUN", "embedding": "NOT RUN", "index": "INCOMPLETE",
        "approved_low_memory": approved_low_memory, "approval_note": approval_note,
        "loading_gate_gib": 5 if approved_low_memory else 6, "effective_resource_policy": policy,
        "automatic_retry": False, "cpu_fallback": "NOT RUN", "started_at_utc": datetime.now(timezone.utc).isoformat()}
    encoder, legacy_lock, monitor = None, None, Monitor(policy, run_dir)
    started = perf_counter()
    try:
        report["initial_resource"], report["initial_gpu"] = resource(), gpu_resource()
        gate(report["initial_resource"], report["initial_gpu"], policy, approved_low_memory)
        with monitor:
            context = prepare_v2(root)
            if checked_path(root, context["binding"]["r3_index"]).exists():
                raise FileExistsError("R3 V2 already exists; no model loading")
            encoder = BGEEncoder(context["local"], context["config"])
            changed = [r for r in context["rows"] if r["chunk_id"] in context["binding"]["changed_chunk_ids"]]
            for row in changed:
                if len(encoder.tokens(row["text"])["input_ids"]) != next(m["token_length"] for m in context["mapping"] if m["chunk_id"] == row["chunk_id"]):
                    raise ValueError("Actual tokenizer differs from verified V2 mapping")
            # Import preparation before the final gate; never infer readiness from startup RAM.
            import torch
            from FlagEmbedding import BGEM3FlagModel
            if (torch.__version__ != context["config"]["R3"]["torch_version"] or not torch.cuda.is_available()
                    or torch.cuda.get_device_capability(0) != (6, 1) or "sm_61" not in torch.cuda.get_arch_list()):
                raise RuntimeError("Pinned CUDA/Pascal readiness mismatch")
            report["other_model_processes"] = other_model_processes()
            if report["other_model_processes"]:
                raise RuntimeError("Another model-capable process is active; no model loading")
            # Hold the legacy lock too; BGEEncoder.load acquires the newer shared lock.
            import msvcrt
            legacy_lock = (Path(config["R3"]["cache"]["root"]) / "gpu-inference.lock").open("a+b")
            legacy_lock.seek(0)
            try:
                msvcrt.locking(legacy_lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                legacy_lock.close()
                legacy_lock = None
                raise RuntimeError("Legacy GPU inference process holds the model lock") from None
            report["cuda_readiness"] = {"version": torch.__version__, "runtime": torch.version.cuda,
                "device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0))}
            report["before_weights"], report["before_weights_gpu"] = resource(), gpu_resource()
            gate(report["before_weights"], report["before_weights_gpu"], policy, approved_low_memory)
            atomic_json(run_dir / "run.json", report)
            report["loading"] = "RUNNING"
            encoder.load(Path(config["R3"]["cache"]["root"]) / "GPU_MODEL.lock")
            report["loading"] = "PASS"
            if unsafe(resource(), policy):
                raise RuntimeError("Unsafe resources after model loading")
            report["embedding"] = "RUNNING"
            records = {}
            report["new_embedding_results"] = []
            for row in changed:
                if unsafe(resource(), policy):
                    raise RuntimeError("Unsafe resources before encoding")
                before = perf_counter()
                vector = unit_vectors(encoder.encode(row["text"]))
                elapsed = perf_counter() - before
                validate_matrix(vector, 1)
                if unsafe(resource(), policy):
                    raise RuntimeError("Unsafe resources after encoding")
                path = run_dir / (row["chunk_id"] + ".npy")
                atomic_vector(path, vector)
                record = {key: context["identity"][key] for key in
                    ("model_id", "model_revision", "precision", "device", "max_length", "normalization", "dimension")}
                record.update(input_sha256=row["text_sha256"], actual_tokens=len(encoder.tokens(row["text"])["input_ids"]),
                    truncation=False, vector_file=str(path), vector_file_sha256=file_hash(path),
                    embedding_seconds=elapsed, created_at_utc=datetime.now(timezone.utc).isoformat())
                atomic_json(path.with_suffix(".json"), record)
                records[row["chunk_id"]] = {**record, "vector": vector}
                report["new_embedding_results"].append({"chunk_id": row["chunk_id"], **record})
                atomic_json(run_dir / "run.json", report)
            report["embedding"] = "PASS"
            report["model_metrics"] = encoder.metrics()
            def reverify():
                verify_snapshot(root, context["config"])
                fresh = prepare_v2(root)
                if fresh["identity"] != context["identity"] or unsafe(resource(), policy):
                    raise RuntimeError("Source identity/resources changed before publication")
            report["index_manifest"] = publish(context, records, reverify)
            report["index"] = "COMPLETE"
            # No additional query/model forward; use an explicit synthetic scoring probe.
            report["offline_sanity"] = offline_sanity(context["rows"], load_components(root, "v2")[1], context["config"]["snapshot"]["id"])
            report["live_query_sanity"] = "NOT RUN; no extra query encoding or second model load"
            report["status"] = "PASS"
    except BaseException:
        report["status"] = "FAIL"
        report["error"] = traceback.format_exc()
        for key in ("loading", "embedding"):
            if report[key] == "RUNNING":
                report[key] = "FAIL"
        raise
    finally:
        if encoder is not None:
            encoder.close()
        if legacy_lock is not None:
            import msvcrt
            legacy_lock.seek(0)
            msvcrt.locking(legacy_lock.fileno(), msvcrt.LK_UNLCK, 1)
            legacy_lock.close()
        report["resource_monitor"] = monitor.summary
        report["final_resource"] = resource()
        report["total_seconds"] = perf_counter() - started
        atomic_json(run_dir / "run.json", report)
    return report


def offline_sanity(rows, vectors, snapshot_id):
    """Synthetic basis-vector scoring probe; never represents a real query."""
    class FixtureEncoder:
        def encode(self, text):
            vector = np.zeros((1, 1024), dtype=np.float32)
            vector[0, 0] = 1
            return vector
    retriever = DenseRetriever(rows, vectors, FixtureEncoder(), snapshot_id)
    results = retriever.retrieve("OFFLINE SYNTHETIC VECTOR PROBE", 5)
    if len(results) != min(5, len(rows)) or any(r.snapshot_id != snapshot_id for r in results):
        raise ValueError("Offline Dense scoring sanity failure")
    return {"status": "PASS", "mode": "synthetic_basis_vector_fixture_not_query_embedding",
            "results": [asdict(r) for r in results], "live_query_inference": "NOT RUN"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "complete"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--corpus-version", choices=("v1", "v2"), default="v1")
    parser.add_argument("--v1-dense-index", type=Path)
    parser.add_argument("--approved-low-memory", action="store_true")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    if args.command == "complete":
        if args.corpus_version != "v2" or args.v1_dense_index:
            parser.error("Incremental completion requires explicit --corpus-version v2")
        result = complete_v2(args.root, args.approved_low_memory, args.approval_note)
    else:
        if args.approved_low_memory or args.approval_note:
            parser.error("inspect does not accept inference approval flags")
        _, vectors, manifest, config, _ = load_components(args.root, args.corpus_version, args.v1_dense_index)
        result = {"status": "PASS", "version": args.corpus_version, "shape": list(vectors.shape),
                  "snapshot_id": config["snapshot"]["id"], "index_manifest": manifest, "model_loaded": False}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
