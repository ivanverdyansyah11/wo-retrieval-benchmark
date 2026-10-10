"""Hash-bound R3 cache, sequential checkpoints and exact float32 cosine."""

from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import statistics
import sys
from time import perf_counter
from uuid import uuid4

import numpy as np

from wo_retrieval.retrieval.lexical import (
    RetrievalResult, audit as lexical_audit, code_hashes, digest, file_hash,
    prepare, write_json,
)
from wo_retrieval.retrieval.text import normalize
from .model import unit_vectors, validate_config


def atomic_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + ".tmp")
    write_json(temporary, value)
    temporary.replace(path)


def atomic_vector(path: Path, vector: np.ndarray) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        np.save(stream, vector, allow_pickle=False)
        stream.flush()
    temporary.replace(path)


def token_audit(rows: list[dict], encoder) -> tuple[list[dict], dict]:
    mapping = []
    for row in rows:
        length = len(encoder.tokens(row["text"])["input_ids"])
        if length > 640:
            raise ValueError(f"Chunk {row['chunk_id']} exceeds token cap; STOP before inference")
        mapping.append({"chunk_id": row["chunk_id"], "document_id": row["document_id"],
                        "serialized_text_sha256": row["text_sha256"], "token_length": length})
    lengths = sorted(row["token_length"] for row in mapping)
    return mapping, {"chunks": len(lengths), "min": min(lengths), "median": statistics.median(lengths),
                     "mean": statistics.mean(lengths), "p95_nearest_rank": lengths[int(np.ceil(.95 * len(lengths))) - 1],
                     "max": max(lengths), "max_length": 640, "special_tokens_included": True,
                     "truncation": False, "truncation_count": 0}


def cache_identity(root: Path, config: dict, statistics: dict, hashes: dict, mapping: list[dict]) -> dict:
    validate_config(config)
    package_names = ("torch", "FlagEmbedding", "transformers", "tokenizers", "sentencepiece", "numpy", "psutil", "safetensors", "huggingface-hub")
    flag_root = root / ".venv-ml/Lib/site-packages/FlagEmbedding"
    implementation_paths = ("inference/embedder/encoder_only/m3.py", "finetune/embedder/encoder_only/m3/modeling.py", "finetune/embedder/encoder_only/m3/runner.py")
    return {"snapshot_id": config["snapshot"]["id"], "snapshot_sha256": config["snapshot"]["manifest_sha256"],
            "snapshot_fingerprint": config["snapshot"]["aggregate_fingerprint"], "method_id": "R3",
            "chunks_sha256": config["snapshot"]["artifact_sha256"][config["snapshot"]["chunks_path"]],
            "protocol_sha256": file_hash(root / "experiments/configs/retrieval_protocol_v1.toml"),
            "config_fingerprint": digest({key: config[key] for key in ("R3", "serialization", "ranking")}),
            "serializer_version": config["serialization"]["policy_id"], "serialization_policy_hash": digest(config["serialization"]),
            "serialized_inputs_hash": statistics["serialized_inputs_hash"], "universe_hash": statistics["universe_hash"],
            "model_id": config["R3"]["model_id"], "model_revision": config["R3"]["revision"],
            "precision": "float16", "storage_dtype": "float32", "dimension": 1024, "max_length": 640,
            "device": "cuda:0", "batch_size": 1, "normalization": config["R3"]["normalization"],
            "vector_search": "NumPy CPU float32 normalized inner product, exhaustive",
            "tokenizer": "XLMRobertaTokenizerFast; local_files_only; no truncation; special tokens included",
            "model_file_hashes": hashes, "row_mapping_hash": digest(mapping),
            "dependency_versions": {name: version(name) for name in package_names},
            "ml_environment_manifest_sha256": file_hash(root / "experiments/configs/ml_environment.lock.json"),
            "shared_code_file_hashes": code_hashes(),
            "dense_code_file_hashes": {path.name: file_hash(path) for path in sorted(Path(__file__).parent.glob("*.py"))},
            "official_inference_file_hashes": {relative: file_hash(flag_root / relative) for relative in implementation_paths}}


def cache_paths(config: dict, identity: dict) -> tuple[Path, Path]:
    base = Path(config["R3"]["cache"]["root"]).resolve()
    if base != Path("D:/ModelCache/wo-retrieval-benchmark").resolve():
        raise ValueError("Unsupported cache root; artifacts must remain in approved D: cache")
    directory = base / "R3" / digest(identity)
    return directory, directory.with_name(directory.name + ".incomplete")


def validate_matrix(vectors, count: int, dimension: int = 1024) -> np.ndarray:
    if vectors.dtype != np.float32 or vectors.shape != (count, dimension) or not np.isfinite(vectors).all():
        raise ValueError("Invalid dense index shape/dtype/finite values")
    if not np.allclose(np.linalg.norm(vectors, axis=1), 1, rtol=0, atol=1e-5):
        raise ValueError("Index vector normalization mismatch")
    return vectors


def load_vectors(directory: Path, identity: dict, mapping: list[dict]) -> tuple[np.ndarray, dict]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("completion_status") != "COMPLETE" or manifest.get("identity") != identity:
        raise ValueError("Incomplete/incompatible R3 index; model/config fingerprint mismatch")
    if set(manifest["artifact_sha256"]) != {"vectors.npy", "rows.json"}:
        raise ValueError("Invalid dense artifact set")
    for name, expected in manifest["artifact_sha256"].items():
        if file_hash(directory / name) != expected:
            raise ValueError(f"Corrupted dense index: {name}")
    if json.loads((directory / "rows.json").read_text(encoding="utf-8")) != mapping or digest(mapping) != identity["row_mapping_hash"]:
        raise ValueError("Dense row mapping mismatch")
    ids = [row["chunk_id"] for row in mapping]
    if len(set(ids)) != len(ids) or ids != sorted(ids):
        raise ValueError("Duplicate/unordered dense chunk IDs")
    vectors = validate_matrix(np.load(directory / "vectors.npy", allow_pickle=False), len(mapping))
    if manifest["indexed_chunks"] != len(mapping):
        raise ValueError("Dense index count mismatch")
    return vectors, manifest


def checkpoint_rows(partial: Path, identity: dict, mapping: list[dict], resume: bool) -> tuple[dict, list[np.ndarray]]:
    if partial.exists():
        if not resume:
            raise RuntimeError("Incomplete cache exists; inspect failure and explicitly approve --resume, no automatic retry")
        state = json.loads((partial / "progress.json").read_text(encoding="utf-8"))
        if state["completion_status"] != "INCOMPLETE" or state["identity"] != identity or state["mapping"] != mapping:
            raise ValueError("Partial identity/model/input/dimension/order mismatch; cannot resume")
    else:
        if resume:
            raise ValueError("No matching partial cache to resume")
        partial.mkdir(parents=True)
        state = {"completion_status": "INCOMPLETE", "identity": identity, "mapping": mapping, "completed": []}
        atomic_json(partial / "progress.json", state)
    if len(state["completed"]) > len(mapping):
        raise ValueError("Partial completed count exceeds corpus")
    vectors = []
    for i, completed in enumerate(state["completed"]):
        path = partial / f"{i:04d}.npy"
        if completed["chunk_id"] != mapping[i]["chunk_id"] or file_hash(path) != completed["sha256"]:
            raise ValueError("Partial chunk mapping/checksum mismatch")
        vectors.append(validate_matrix(np.load(path, allow_pickle=False), 1))
    return state, vectors


def embed_sequential(rows: list[dict], mapping: list[dict], identity: dict, encoder,
                     directory: Path, partial: Path, resume: bool = False, verify_before_publish=None) -> dict:
    ids = [row["chunk_id"] for row in mapping]
    if (len(rows) != len(mapping) or len(set(ids)) != len(ids) or ids != sorted(ids)
            or any(row["chunk_id"] != mapped["chunk_id"] or row["document_id"] != mapped["document_id"]
                   or row["text_sha256"] != mapped["serialized_text_sha256"] for row, mapped in zip(rows, mapping, strict=True))):
        raise ValueError("Invalid/missing/duplicate embedding input mapping")
    state, vectors = checkpoint_rows(partial, identity, mapping, resume)
    initial_rows = len(vectors)
    elapsed_forward = 0.0
    started = perf_counter()
    try:
        for i in range(len(vectors), len(rows)):
            forward_started = perf_counter()
            vector = unit_vectors(encoder.encode(rows[i]["text"]))
            validate_matrix(vector, 1)
            elapsed_forward += perf_counter() - forward_started
            path = partial / f"{i:04d}.npy"
            atomic_vector(path, vector)
            state["completed"].append({"chunk_id": mapping[i]["chunk_id"], "sha256": file_hash(path)})
            atomic_json(partial / "progress.json", state)
            vectors.append(vector)
            print(json.dumps({"event": "embedded", "completed": i + 1, "total": len(rows), "chunk_id": mapping[i]["chunk_id"], "token_length": mapping[i]["token_length"]}), file=sys.stderr, flush=True)
        matrix = validate_matrix(np.concatenate(vectors, axis=0), len(rows))
        staging = directory.with_name(directory.name + ".finalizing-" + uuid4().hex)
        staging.mkdir()
        atomic_vector(staging / "vectors.npy", matrix)
        write_json(staging / "rows.json", mapping)
        manifest = {"completion_status": "COMPLETE", "identity": identity, "indexed_chunks": len(rows),
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(), "shape": list(matrix.shape),
                    "missing_chunks": 0, "duplicate_chunk_ids": 0, "finite": True,
                    "embedding_computation_seconds": elapsed_forward,
                    "embedding_checkpoint_finalize_seconds": perf_counter() - started,
                    "resumed_verified_rows": initial_rows,
                    "artifact_sha256": {name: file_hash(staging / name) for name in ("vectors.npy", "rows.json")}}
        write_json(staging / "manifest.json", manifest)
        load_vectors(staging, identity, mapping)
        if verify_before_publish is not None:
            verify_before_publish()
        staging.rename(directory)
        state["published_complete_index"] = str(directory)
        atomic_json(partial / "progress.json", state)
        return manifest
    except BaseException as error:
        state["last_error"] = {"type": type(error).__name__, "message": str(error), "completed_rows": len(state["completed"])}
        atomic_json(partial / "progress.json", state)
        raise


class DenseRetriever:
    def __init__(self, rows: list[dict], vectors: np.ndarray, encoder, snapshot_id: str):
        if not rows or len({row["chunk_id"] for row in rows}) != len(rows):
            raise ValueError("Empty/duplicate dense chunk mapping")
        self.rows, self.vectors = rows, validate_matrix(vectors, len(rows))
        self.encoder, self.snapshot_id = encoder, snapshot_id

    def retrieve(self, query: str, top_k: int) -> list[RetrievalResult]:
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        text = normalize(query)
        if not text:
            return []
        query_vector = unit_vectors(self.encoder.encode(text))
        if query_vector.shape != (1, 1024):
            raise ValueError("Expected one query vector")
        scores = self.vectors @ query_vector[0]
        if not np.isfinite(scores).all():
            raise ValueError("Nonfinite cosine scores")
        order = sorted(range(len(self.rows)), key=lambda i: (-float(scores[i]), self.rows[i]["chunk_id"]))
        return [RetrievalResult("R3", self.rows[i]["chunk_id"], self.rows[i]["document_id"], rank, float(scores[i]), self.snapshot_id)
                for rank, i in enumerate(order[:top_k], 1)]


def inspect_inputs(root: Path, config: dict):
    rows, statistics = prepare(root, config)
    lexical = lexical_audit(root)
    if lexical["shared_inputs"] != statistics:
        raise ValueError("R3 serialization differs from R1/R2")
    return rows, statistics
