"""One hash-bound query, with the original encoder output preserved verbatim."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from uuid import uuid4

import numpy as np

from wo_retrieval.dense.index import atomic_json, atomic_vector
from wo_retrieval.dense.model import unit_vectors
from wo_retrieval.retrieval.lexical import digest, file_hash
from wo_retrieval.retrieval.text import normalize


def text_hash(text):
    normalize(text)  # Reject non-string input without changing its exact hash.
    return sha256(text.encode("utf-8")).hexdigest()


def contract(dense_manifest):
    identity = dense_manifest["identity"]
    return {"schema_version": "wo_query_vector_v1",
            "corpus_index_manifest_sha256_canonical": digest(dense_manifest),
            "dense_identity": identity,
            "query_input_contract": "shared_normalize_v1: NFC, CRLF/CR to LF, outer strip; no prompt",
            "dimension": 1024, "dtype": "float32", "shape": [1, 1024],
            "vector_stage": "BGEEncoder.encode output before project unit_vectors",
            "normalization": "official normalized CLS; project float32 L2 once inside DenseRetriever"}


def validate_vector(vector):
    if not isinstance(vector, np.ndarray) or vector.dtype != np.float32 or vector.shape != (1, 1024):
        raise ValueError("Query vector dimension/shape/dtype mismatch")
    unit_vectors(vector)  # Existing finite/nonzero/finite-norm checks; do not replace raw bytes.
    return vector


def validate_manifest(manifest, expected, query_id, query):
    if not isinstance(manifest, dict):
        raise ValueError("Query manifest must be an object")
    if not isinstance(query_id, str) or not query_id.strip() or not normalize(query):
        raise ValueError("Nonempty query ID and query text required")
    if (manifest.get("completion_status") != "COMPLETE" or manifest.get("contract") != expected
            or manifest.get("query_id") != query_id
            or manifest.get("query_text_sha256") != text_hash(query)
            or manifest.get("effective_input_sha256") != text_hash(normalize(query))):
        raise ValueError("Incomplete/stale query artifact or query/model/config/hash mismatch")
    if set(manifest.get("artifact_sha256", {})) != {"vector.npy"}:
        raise ValueError("Invalid query artifact set")
    created = datetime.fromisoformat(manifest["created_at_utc"])
    if created.utcoffset() is None or created.utcoffset().total_seconds() != 0:
        raise ValueError("Query timestamp must be UTC")
    provenance = manifest["encoding"]
    if not isinstance(provenance, dict):
        raise ValueError("Query encoding provenance must be an object")
    identity = expected["dense_identity"]
    for key in ("device", "precision", "batch_size", "max_length"):
        if provenance.get(key) != identity[key]:
            raise ValueError("Query encoding provenance mismatch: " + key)
    tokens = provenance.get("actual_tokens_including_special")
    if type(tokens) is not int or not 0 < tokens <= identity["max_length"] or provenance.get("truncation") is not False:
        raise ValueError("Invalid query token length/truncation provenance")


def load_artifact(directory, expected, query_id, query):
    directory = Path(directory)
    try:
        manifest_path, vector_path = directory / "manifest.json", directory / "vector.npy"
        if manifest_path.stat().st_size > 256 * 1024 or vector_path.stat().st_size > 16 * 1024:
            raise ValueError("Oversized query artifact")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_manifest(manifest, expected, query_id, query)
        if file_hash(vector_path) != manifest["artifact_sha256"]["vector.npy"]:
            raise ValueError("Corrupted query vector checksum")
        vector = validate_vector(np.load(vector_path, allow_pickle=False))
        vector.setflags(write=False)
        return vector, manifest
    except (OSError, KeyError, TypeError, OverflowError, EOFError) as error:
        raise ValueError("Missing/malformed query artifact") from error


def publish(directory, expected, query_id, query, vector, encoding):
    directory = Path(directory)
    validate_vector(vector)
    if directory.exists():
        raise FileExistsError("Query artifact exists; never overwrite or silently regenerate")
    staging = directory.with_name(directory.name + ".incomplete-" + uuid4().hex)
    staging.mkdir(parents=True)
    manifest = {"completion_status": "INCOMPLETE", "contract": expected, "query_id": query_id,
                "query_text_sha256": text_hash(query), "effective_input_sha256": text_hash(normalize(query)),
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "encoding": encoding}
    atomic_json(staging / "manifest.json", manifest)
    atomic_vector(staging / "vector.npy", vector)
    manifest.update(completion_status="COMPLETE", artifact_sha256={"vector.npy": file_hash(staging / "vector.npy")})
    validate_manifest(manifest, expected, query_id, query)
    atomic_json(staging / "manifest.json", manifest)
    load_artifact(staging, expected, query_id, query)
    staging.rename(directory)
    return manifest


class CachedEncoder:
    def __init__(self, directory, expected, query_id, query):
        self.vector, self.manifest = load_artifact(directory, expected, query_id, query)
        self.text = normalize(query)

    def encode(self, text):
        if text != self.text:
            raise ValueError("Cached encoder input mismatch")
        return self.vector
