"""Verified existing corpus loaders without tokenizer or neural runtime imports."""

import json
from pathlib import Path

from wo_retrieval.dense.index import DenseRetriever, cache_identity, cache_paths, load_vectors
from wo_retrieval.dense.model import model_files
from wo_retrieval.hybrid.retrieval import HybridRetriever, validate_policy
from wo_retrieval.retrieval.lexical import digest, load, read_protocol
from .artifacts import CachedEncoder, contract


def load_components(root, corpus_index):
    root, corpus_index = Path(root).resolve(), Path(corpus_index).resolve()
    config = read_protocol(root)
    validate_policy(config)
    base = Path(config["R3"]["cache"]["root"]).resolve() / "R3"
    if corpus_index.parent != base:
        raise ValueError("Use an existing complete index in the approved R3 cache")
    bm25 = load(root, "R2")
    mapping = json.loads((corpus_index / "rows.json").read_text(encoding="utf-8"))
    if len(mapping) != len(bm25.rows):
        raise ValueError("Corpus row count mismatch")
    for row, mapped in zip(bm25.rows, mapping, strict=True):
        if (row["chunk_id"], row["document_id"], row["text_sha256"]) != (
                mapped["chunk_id"], mapped["document_id"], mapped["serialized_text_sha256"]):
            raise ValueError("Corpus serialization/mapping mismatch")
        if type(mapped["token_length"]) is not int or not 0 < mapped["token_length"] <= config["R3"]["max_length"]:
            raise ValueError("Corpus token mapping mismatch")
    token_hash = digest([{"chunk_id": m["chunk_id"], "text_sha256": m["serialized_text_sha256"],
                          "tokens": m["token_length"]} for m in mapping])
    if token_hash != config["serialization"]["audit"]["fingerprint"]:
        raise ValueError("Corpus token audit fingerprint mismatch")
    local, hashes = model_files(root, config)
    identity = cache_identity(root, config, bm25.manifest["serialization_statistics"], hashes, mapping)
    if cache_paths(config, identity)[0] != corpus_index:
        raise ValueError("Stale/incompatible corpus index path")
    vectors, manifest = load_vectors(corpus_index, identity, mapping)
    return bm25, vectors, manifest, config, local


def retrievers(components, artifact, query_id, query):
    bm25, vectors, manifest, config, _ = components
    encoder = CachedEncoder(artifact, contract(manifest), query_id, query)
    dense = DenseRetriever(bm25.rows, vectors, encoder, config["snapshot"]["id"])
    hybrid = HybridRetriever(bm25, dense, manifest, config)
    return dense, hybrid
