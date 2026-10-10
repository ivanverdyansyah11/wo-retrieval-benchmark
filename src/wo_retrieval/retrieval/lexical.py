"""Exact lexical scoring and hash-bound, non-pickle derived indexes."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
from time import perf_counter
import tomllib
from typing import Protocol
from uuid import uuid4

import numpy as np
from rank_bm25 import BM25Okapi
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from .text import LexicalTokenizer, serialize


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value) -> str:
    return sha256(canonical(value)).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_bytes(canonical(value) + b"\n")


def dependencies() -> dict:
    return {name: version(name) for name in ("scikit-learn", "rank-bm25", "numpy", "scipy", "joblib", "threadpoolctl")}


def code_hashes() -> dict:
    return {path.name: file_hash(path) for path in sorted(Path(__file__).parent.glob("*.py"))}


def checked_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Artifact path escapes repository")
    return path


def read_protocol(root: Path) -> dict:
    with (root / "experiments/configs/retrieval_protocol_v1.toml").open("rb") as stream:
        config = tomllib.load(stream)
    if config["serialization"]["policy_id"] != "wo_operational_context_dedup_v1":
        raise ValueError("Unsupported serialization policy")
    if config["serialization"]["trailing_newline"] or config["lexical"]["stop_words"] or config["lexical"]["stemming"] or config["lexical"]["lemmatization"] or config["lexical"]["accent_stripping"]:
        raise ValueError("Unsupported text policy; review implementation before changing protocol")
    return config


def verify_snapshot(root: Path, config: dict) -> dict:
    spec = config["snapshot"]
    path = checked_path(root, spec["manifest_path"])
    if file_hash(path) != spec["manifest_sha256"]:
        raise ValueError("Snapshot manifest hash mismatch")
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot["snapshot_id"] != spec["id"] or snapshot["artifact_sha256"] != spec["artifact_sha256"]:
        raise ValueError("Snapshot identity/artifact mismatch")
    if digest(snapshot["artifact_sha256"]) != spec["aggregate_fingerprint"] or snapshot["aggregate_fingerprint"]["value"] != spec["aggregate_fingerprint"]:
        raise ValueError("Snapshot fingerprint mismatch")
    for relative, expected in spec["artifact_sha256"].items():
        if file_hash(checked_path(root, relative)) != expected:
            raise ValueError(f"Protected artifact hash mismatch: {relative}")
    return snapshot


def prepare(root: Path, config: dict) -> tuple[list[dict], dict]:
    verify_snapshot(root, config)
    chunks = [json.loads(line) for line in checked_path(root, config["snapshot"]["chunks_path"]).read_text(encoding="utf-8").splitlines()]
    if len(chunks) != config["snapshot"]["chunks"]:
        raise ValueError("Frozen chunk count mismatch")
    ids = [chunk["chunk_id"] for chunk in chunks]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("Invalid/duplicate frozen chunk ID")
    documents = [json.loads(line) for line in checked_path(root, "data/processed/documents.jsonl").read_text(encoding="utf-8").splitlines()]
    document_ids = {document["document_id"] for document in documents}
    if len(documents) != config["snapshot"]["canonical_documents"] or len(document_ids) != len(documents) or {chunk["document_id"] for chunk in chunks} != document_ids:
        raise ValueError("Canonical document universe mismatch")
    tokenizer = LexicalTokenizer(config["lexical"])
    rows, emitted = [], Counter()
    for chunk in sorted(chunks, key=lambda item: item["chunk_id"]):
        text, selected = serialize(chunk, config["serialization"])
        emitted.update(selected)
        tokens = tokenizer(text)
        if not tokens:
            raise ValueError(f"Empty lexical document: {chunk['chunk_id']}")
        rows.append({"chunk_id": chunk["chunk_id"], "document_id": chunk["document_id"], "text": text,
                     "text_sha256": sha256(text.encode("utf-8")).hexdigest(), "tokens": tokens,
                     "source_file": chunk["source_file"], "source_locator": chunk["source_locator"],
                     "format": chunk["metadata"]["format"]})
    statistics = {
        "chunks": len(rows), "format_distribution": dict(Counter(row["format"] for row in rows)),
        "emitted_fields": dict(emitted), "empty_documents": 0,
        "duplicate_serialized_documents": len(rows) - len({row["text_sha256"] for row in rows}),
        "xlsx_with_guide_context": sum(chunk["metadata"]["format"] == "XLSX" and bool(chunk["metadata"].get("guide_context")) for chunk in chunks),
        "lexical_tokens_min": min(len(row["tokens"]) for row in rows),
        "lexical_tokens_max": max(len(row["tokens"]) for row in rows),
        "lexical_tokens_total": sum(len(row["tokens"]) for row in rows),
        "universe_hash": digest([row["chunk_id"] for row in rows]),
        "serialized_inputs_hash": digest([{key: row[key] for key in ("chunk_id", "text_sha256")} for row in rows]),
        "tokenized_inputs_hash": digest([{key: row[key] for key in ("chunk_id", "tokens")} for row in rows]),
    }
    expected = config["serialization"]["audit"]
    if any(emitted[field] != expected[f"{field}_emitted"] for field in ("title", "heading", "category")):
        raise ValueError("Serialization emission counts differ from approved audit")
    return rows, statistics


@dataclass(frozen=True)
class RetrievalResult:
    method_id: str
    chunk_id: str
    document_id: str
    rank: int
    score: float
    snapshot_id: str


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int) -> list[RetrievalResult]: ...


class LexicalRetriever:
    def __init__(self, method: str, rows: list[dict], config: dict):
        if method not in ("R1", "R2"):
            raise ValueError("Only R1 and R2 are implemented")
        if not rows or len({row["chunk_id"] for row in rows}) != len(rows):
            raise ValueError("Empty/duplicate document universe")
        self.method, self.rows, self.config = method, rows, config
        self.tokenizer = LexicalTokenizer(config["lexical"])
        self.manifest = None

    def vectorizer(self, vocabulary=None) -> TfidfVectorizer:
        cfg = self.config["R1"]
        if cfg["max_features"] != "unlimited" or cfg["dtype"] != "float64":
            raise ValueError("Unsupported R1 representation")
        return TfidfVectorizer(tokenizer=self.tokenizer, token_pattern=None, lowercase=False,
                               strip_accents=None, preprocessor=None, vocabulary=vocabulary,
                               ngram_range=tuple(cfg["ngram_range"]), min_df=cfg["min_df"], max_df=cfg["max_df"],
                               max_features=None, binary=cfg["binary"], sublinear_tf=cfg["sublinear_tf"],
                               use_idf=cfg["use_idf"], smooth_idf=cfg["smooth_idf"], norm=cfg["norm"], dtype=np.float64)

    def fit(self):
        if self.method == "R1":
            self.model = self.vectorizer()
            self.matrix = self.model.fit_transform([row["text"] for row in self.rows]).tocsr()
        else:
            cfg = self.config["R2"]
            self.model = BM25Okapi([row["tokens"] for row in self.rows], tokenizer=None, k1=cfg["k1"], b=cfg["b"], epsilon=cfg["epsilon"])
            if not np.isfinite(self.model.average_idf) or self.model.average_idf <= 0:
                raise ValueError(f"BM25 mean raw IDF is unsafe: {self.model.average_idf}")
        return self

    def retrieve(self, query: str, top_k: int) -> list[RetrievalResult]:
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        tokens = self.tokenizer(query)
        if not tokens:
            return []
        if self.method == "R1":
            scores = (self.matrix @ self.model.transform([query]).T).toarray().ravel()
        else:
            scores = self.model.get_scores(tokens)
        return self.rank(scores, top_k)

    def rank(self, scores, top_k: int) -> list[RetrievalResult]:
        scores = np.asarray(scores, dtype=np.float64)
        if scores.shape != (len(self.rows),) or not np.isfinite(scores).all():
            raise ValueError("Invalid/nonfinite score vector")
        candidates = sorted((i for i, score in enumerate(scores) if score > 0), key=lambda i: (-scores[i], self.rows[i]["chunk_id"]))
        return [RetrievalResult(self.method, self.rows[i]["chunk_id"], self.rows[i]["document_id"], rank, float(scores[i]), self.config["snapshot"]["id"])
                for rank, i in enumerate(candidates[:top_k], 1)]


def identity(root: Path, config: dict, method: str) -> dict:
    return {"snapshot_id": config["snapshot"]["id"], "snapshot_sha256": config["snapshot"]["manifest_sha256"],
            "snapshot_fingerprint": config["snapshot"]["aggregate_fingerprint"],
            "artifact_sha256": config["snapshot"]["artifact_sha256"], "method_id": method,
            "protocol_sha256": file_hash(root / "experiments/configs/retrieval_protocol_v1.toml"),
            "config_fingerprint": digest({key: config[key] for key in ("serialization", "lexical", "ranking", method)}),
            "serializer_version": config["serialization"]["policy_id"], "tokenizer_version": LexicalTokenizer.version,
            "serialization_policy_hash": digest(config["serialization"]), "normalization_rules": config["lexical"],
            "method_parameters": config[method],
            "environment_lock_sha256": file_hash(root / "experiments/configs/lexical_environment.lock.txt"),
            "dependency_versions": dependencies(), "python_version": platform.python_version(), "code_file_hashes": code_hashes()}


def index_path(root: Path, method: str, name: str | None = None) -> Path:
    if method not in ("R1", "R2"):
        raise ValueError("Only R1/R2 indexes are supported")
    if name is not None and (not name or Path(name).name != name or name in (".", "..")):
        raise ValueError("Index name must be one directory name")
    base = (root / "experiments/indexes").resolve()
    path = (base / (name or method)).resolve()
    if not base.is_relative_to(root.resolve()) or not path.is_relative_to(base) or path == base:
        raise ValueError("Derived index path escapes experiments/indexes")
    return path


def build(root: Path, method: str, name: str | None = None) -> dict:
    started = perf_counter()
    root = root.resolve()
    config = read_protocol(root)
    target = index_path(root, method, name)
    if target.exists():
        retriever = load(root, method, name)
        return {**retriever.manifest, "reused_verified_index": True}
    rows, statistics = prepare(root, config)
    retriever = LexicalRetriever(method, rows, config).fit()
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + ".incomplete-" + uuid4().hex)
    staging.mkdir()
    write_json(staging / "documents.json", rows)
    if method == "R1":
        sparse.save_npz(staging / "matrix.npz", retriever.matrix)
        write_json(staging / "model.json", {"vocabulary": retriever.model.vocabulary_, "idf": retriever.model.idf_.tolist()})
        model_statistics = {"vocabulary_size": len(retriever.model.vocabulary_), "matrix_shape": list(retriever.matrix.shape), "nonzero_entries": retriever.matrix.nnz}
    else:
        state = {key: getattr(retriever.model, key) for key in ("doc_freqs", "idf", "doc_len", "avgdl", "corpus_size", "average_idf", "k1", "b", "epsilon")}
        write_json(staging / "model.json", state)
        model_statistics = {"vocabulary_size": len(state["idf"]), "average_raw_idf": state["average_idf"], "average_document_length": state["avgdl"], "min_effective_idf": min(state["idf"].values())}
    manifest = {**identity(root, config, method), "completion_status": "COMPLETE", "indexed_chunks": len(rows),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(), "serialization_statistics": statistics,
                "model_statistics": model_statistics, "device": "cpu", "neural_model_loaded": False,
                "code_revision": "explicit_uncommitted_no_git_repository", "hardware": platform.platform(),
                "warnings": ["Preliminary snapshot; practitioner validation pending", "Development queries remain draft_pending_expert_review"],
                "artifact_sha256_derived": {p.name: file_hash(p) for p in sorted(staging.iterdir())},
                "indexing_seconds_before_manifest_publish": perf_counter() - started}
    write_json(staging / "manifest.json", manifest)
    verify_snapshot(root, config)
    staging.rename(target)
    return manifest


def load(root: Path, method: str, name: str | None = None) -> LexicalRetriever:
    root = root.resolve()
    config = read_protocol(root)
    target = index_path(root, method, name)
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    expected = identity(root, config, method)
    if manifest.get("completion_status") != "COMPLETE" or any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Stale/incompatible index metadata; build a new named index")
    rows, statistics = prepare(root, config)
    required = {"documents.json", "model.json"} | ({"matrix.npz"} if method == "R1" else set())
    if set(manifest["artifact_sha256_derived"]) != required:
        raise ValueError("Incomplete derived index artifact set")
    for filename, expected_hash in manifest["artifact_sha256_derived"].items():
        if file_hash(target / filename) != expected_hash:
            raise ValueError(f"Derived artifact hash mismatch: {filename}")
    if json.loads((target / "documents.json").read_text(encoding="utf-8")) != rows or manifest["serialization_statistics"] != statistics:
        raise ValueError("Index rows differ from frozen serialized corpus")
    state = json.loads((target / "model.json").read_text(encoding="utf-8"))
    retriever = LexicalRetriever(method, rows, config)
    if method == "R1":
        retriever.model = retriever.vectorizer(state["vocabulary"])
        retriever.model.idf_ = np.asarray(state["idf"], dtype=np.float64)
        retriever.matrix = sparse.load_npz(target / "matrix.npz").tocsr()
        if retriever.matrix.shape != (len(rows), len(state["idf"])) or not np.isfinite(retriever.matrix.data).all():
            raise ValueError("Invalid TF-IDF matrix")
    else:
        retriever.model = BM25Okapi.__new__(BM25Okapi)
        retriever.model.__dict__.update(state)
        if state["corpus_size"] != len(rows) or len(state["doc_freqs"]) != len(rows) or state["average_idf"] <= 0:
            raise ValueError("Invalid BM25 state")
    retriever.manifest = manifest
    return retriever


def audit(root: Path) -> dict:
    retrievers = {method: load(root, method) for method in ("R1", "R2")}
    summaries = {method: retriever.manifest["serialization_statistics"] for method, retriever in retrievers.items()}
    if summaries["R1"] != summaries["R2"]:
        raise ValueError("R1/R2 document universe or serialized inputs differ")
    return {"status": "PASS", "shared_inputs": summaries["R1"], "indexes": {method: retriever.manifest for method, retriever in retrievers.items()}}
