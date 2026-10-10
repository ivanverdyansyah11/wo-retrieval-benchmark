from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from wo_retrieval.dense.index import (
    DenseRetriever, atomic_json, checkpoint_rows, embed_sequential, inspect_inputs,
    load_vectors, token_audit, validate_matrix,
)
from wo_retrieval.dense.model import BGEEncoder, unit_vectors, validate_config
from wo_retrieval.dense.resources import gate, unsafe
from wo_retrieval.retrieval.lexical import digest, prepare, read_protocol, verify_snapshot


ROOT = Path(__file__).resolve().parents[1]
CONFIG = read_protocol(ROOT)


def vector(x=1, y=0):
    values = np.zeros((1, 1024), dtype=np.float32)
    values[0, :2] = [x, y]
    return values


class FakeEncoder:
    def __init__(self, fail_after=None):
        self.calls, self.fail_after = [], fail_after

    def tokens(self, text):
        return {"input_ids": [0] * (len(text.split()) + 2)}

    def encode(self, text):
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise RuntimeError("fixture OOM; no retry")
        self.calls.append(text)
        return vector(3, 4)


def fixture():
    rows = [{"chunk_id": f"C{i}", "document_id": f"D{i}", "text": f"vendor WO {i}", "text_sha256": digest(i)} for i in range(3)]
    mapping, _ = token_audit(rows, FakeEncoder())
    identity = {"model_revision": CONFIG["R3"]["revision"], "row_mapping_hash": digest(mapping), "dimension": 1024}
    return rows, mapping, identity


class DenseMathTests(unittest.TestCase):
    def test_normalization_dimensions_finite_zero(self):
        np.testing.assert_allclose(unit_vectors(vector(3, 4))[0, :2], [.6, .8], rtol=1e-6)
        for invalid in (np.zeros((1, 1024)), np.ones((1, 3)), np.ones(1024), vector(float("nan")), vector(float("inf"))):
            with self.assertRaises(ValueError):
                unit_vectors(invalid)
        with self.assertRaises(ValueError):
            validate_matrix(vector().astype(np.float64), 1)
        with self.assertRaises(ValueError):
            validate_matrix(vector(3, 4), 1)

    def test_exact_cosine_all_finite_candidates_and_ties(self):
        rows = [{"chunk_id": chunk, "document_id": "D"} for chunk in ("C", "B", "A", "Z")]
        vectors = np.concatenate([vector(1), vector(0, 1), vector(1), vector(-1)])
        encoder = FakeEncoder()
        encoder.encode = lambda _: vector(1)
        retriever = DenseRetriever(rows, vectors, encoder, "SNAP")
        results = retriever.retrieve("koordinasi WO", 999)
        self.assertEqual([r.chunk_id for r in results], ["A", "C", "B", "Z"])
        self.assertEqual([r.score for r in results], [1, 1, 0, -1])
        self.assertEqual([r.rank for r in results], [1, 2, 3, 4])
        self.assertEqual(len({r.chunk_id for r in results}), 4)
        self.assertEqual(set(asdict(results[0])), {"method_id", "chunk_id", "document_id", "rank", "score", "snapshot_id"})
        self.assertEqual(results[0].method_id, "R3")
        self.assertEqual(len(retriever.retrieve("vendor", 1)), 1)

    def test_invalid_and_empty_query_without_model_calls(self):
        encoder = FakeEncoder()
        retriever = DenseRetriever([{"chunk_id": "A", "document_id": "D"}], vector(), encoder, "SNAP")
        for query in ("", " \r\n "):
            self.assertEqual(retriever.retrieve(query, 5), [])
        self.assertEqual(encoder.calls, [])
        for top_k in (0, -1, True, 1.5, "5"):
            with self.assertRaises(ValueError):
                retriever.retrieve("WO", top_k)
        for query in (None, 123, []):
            with self.assertRaises(ValueError):
                retriever.retrieve(query, 5)
        with self.assertRaises(ValueError):
            DenseRetriever([{"chunk_id": "A"}] * 2, np.concatenate([vector(), vector()]), encoder, "SNAP")

    def test_query_normalization_no_instruction_and_no_cache(self):
        encoder = FakeEncoder()
        retriever = DenseRetriever([{"chunk_id": "A", "document_id": "D"}], vector(), encoder, "SNAP")
        for _ in range(2):
            retriever.retrieve("  cafe\u0301\r\nWO  ", 1)
        self.assertEqual(encoder.calls, ["café\nWO", "café\nWO"])
        encoder.encode = lambda _: np.concatenate([vector(), vector()])
        with self.assertRaises(ValueError):
            retriever.retrieve("WO", 1)

    def test_token_overflow_stops_before_embedding(self):
        rows, _, _ = fixture()
        encoder = FakeEncoder()
        encoder.tokens = lambda _: {"input_ids": [1] * 641}
        with self.assertRaises(ValueError):
            token_audit(rows, encoder)
        self.assertEqual(encoder.calls, [])

    def test_model_config_mismatch(self):
        import copy
        altered = copy.deepcopy(CONFIG)
        altered["R3"]["revision"] = "wrong"
        with self.assertRaises(ValueError):
            validate_config(altered)

    def test_actual_encoder_token_contract_without_model(self):
        encoder = BGEEncoder.__new__(BGEEncoder)
        encoder.config = CONFIG
        calls = []
        def tokenizer(text, **kwargs):
            calls.append((text, kwargs))
            return {"input_ids": [1] * 640}
        encoder.tokenizer = tokenizer
        self.assertEqual(len(encoder.tokens("  WO\r\n  ")["input_ids"]), 640)
        self.assertEqual(calls, [("WO", {"add_special_tokens": True, "truncation": False, "padding": False})])
        encoder.tokenizer = lambda *args, **kwargs: {"input_ids": [1] * 641}
        with self.assertRaises(ValueError):
            encoder.tokens("WO")


class DenseCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.directory, self.partial = self.root / "complete", self.root / "incomplete"
        self.rows, self.mapping, self.identity = fixture()

    def tearDown(self):
        self.temporary.cleanup()

    def build(self, encoder=None, resume=False):
        return embed_sequential(self.rows, self.mapping, self.identity, encoder or FakeEncoder(), self.directory, self.partial, resume)

    def test_full_build_roundtrip_shape_mapping_and_no_pickle(self):
        manifest = self.build()
        vectors, loaded = load_vectors(self.directory, self.identity, self.mapping)
        self.assertEqual(loaded, manifest)
        self.assertEqual(vectors.shape, (3, 1024))
        self.assertEqual(vectors.dtype, np.float32)
        np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1, rtol=0, atol=1e-6)
        self.assertEqual(manifest["resumed_verified_rows"], 0)
        self.assertEqual(manifest["missing_chunks"], 0)
        self.assertEqual(manifest["duplicate_chunk_ids"], 0)

    def test_incomplete_not_published_no_retry_explicit_resume(self):
        encoder = FakeEncoder(fail_after=1)
        with self.assertRaisesRegex(RuntimeError, "fixture OOM"):
            self.build(encoder)
        self.assertEqual(len(encoder.calls), 1)
        self.assertFalse(self.directory.exists())
        state = json.loads((self.partial / "progress.json").read_text())
        self.assertEqual(state["completion_status"], "INCOMPLETE")
        self.assertEqual(len(state["completed"]), 1)
        with self.assertRaises(RuntimeError):
            self.build()
        second = FakeEncoder()
        manifest = self.build(second, resume=True)
        self.assertEqual(len(second.calls), 2)
        self.assertEqual(manifest["resumed_verified_rows"], 1)

    def test_resume_corruption_or_changed_identity_rejected(self):
        with self.assertRaises(RuntimeError):
            self.build(FakeEncoder(fail_after=1))
        changed = {**self.identity, "model_revision": "other"}
        with self.assertRaises(ValueError):
            checkpoint_rows(self.partial, changed, self.mapping, True)
        path = self.partial / "0000.npy"
        path.write_bytes(path.read_bytes() + b"corrupt")
        with self.assertRaises(ValueError):
            checkpoint_rows(self.partial, self.identity, self.mapping, True)

    def test_incomplete_mismatched_or_corrupted_complete_rejected(self):
        self.build()
        path = self.directory / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["completion_status"] = "INCOMPLETE"
        atomic_json(path, manifest)
        with self.assertRaises(ValueError):
            load_vectors(self.directory, self.identity, self.mapping)
        manifest["completion_status"] = "COMPLETE"
        atomic_json(path, manifest)
        with self.assertRaises(ValueError):
            load_vectors(self.directory, {**self.identity, "model_revision": "other"}, self.mapping)
        vector_path = self.directory / "vectors.npy"
        vector_path.write_bytes(vector_path.read_bytes() + b"bad")
        with self.assertRaisesRegex(ValueError, "Corrupted"):
            load_vectors(self.directory, self.identity, self.mapping)

    def test_duplicate_row_mapping_and_failed_final_integrity_gate(self):
        duplicate = [self.mapping[0]] * 3
        identity = {**self.identity, "row_mapping_hash": digest(duplicate)}
        with self.assertRaises(ValueError):
            embed_sequential(self.rows, duplicate, identity, FakeEncoder(), self.directory, self.partial)
        self.assertFalse(self.directory.exists())
        other = self.root / "another"
        with self.assertRaisesRegex(RuntimeError, "snapshot changed"):
            embed_sequential(self.rows, self.mapping, self.identity, FakeEncoder(), self.directory, other,
                             verify_before_publish=lambda: (_ for _ in ()).throw(RuntimeError("snapshot changed")))
        self.assertFalse(self.directory.exists())

    def test_rebuild_vector_and_mapping_payload_identity(self):
        first = self.build()
        second = embed_sequential(self.rows, self.mapping, self.identity, FakeEncoder(), self.root / "repeat", self.root / "repeat-partial")
        self.assertEqual(first["artifact_sha256"], second["artifact_sha256"])


class DenseIntegrationTests(unittest.TestCase):
    def test_cli_dispatch_without_loading_neural_model(self):
        from wo_retrieval.dense.cli import main, run as dense_run
        with patch("sys.argv", ["wo-dense", "retrieve", "--query", "koordinasi WO", "--top-k", "3"]), patch("wo_retrieval.dense.cli.run", return_value=[]) as run:
            main()
            self.assertEqual(run.call_args.args[1:4], ("retrieve", "koordinasi WO", 3))
        with patch("sys.argv", ["wo-dense", "retrieve"]), self.assertRaises(SystemExit):
            main()
        with patch("wo_retrieval.dense.cli.resource", side_effect=AssertionError("no model/resource call")):
            self.assertEqual(dense_run(ROOT, "retrieve", "  \r\n "), [])

    def test_snapshot_and_all_371_shared_serialized_inputs(self):
        verify_snapshot(ROOT, CONFIG)
        rows, statistics = inspect_inputs(ROOT, CONFIG)
        lexical_rows, lexical_statistics = prepare(ROOT, CONFIG)
        self.assertEqual(rows, lexical_rows)
        self.assertEqual(statistics, lexical_statistics)
        self.assertEqual(len(rows), 371)
        self.assertEqual(len({row["chunk_id"] for row in rows}), 371)

    def test_resource_gate_and_critical_thresholds(self):
        sample = {"available_ram_bytes": 6 * 1024**3, "commit_headroom_bytes": 10 * 1024**3,
                  "memory_load_percent": 60, "disk_free_bytes": {"C:/": 14 * 1024**3, "D:/": 800 * 1024**3}}
        gpu = {"free_mib": 4007, "used_mib": 0}
        gate(sample, gpu, CONFIG["hardware"], False)
        sample["available_ram_bytes"] = int(5.5 * 1024**3)
        with self.assertRaises(RuntimeError):
            gate(sample, gpu, CONFIG["hardware"], False)
        gate(sample, gpu, CONFIG["hardware"], True)
        sample["available_ram_bytes"] = 700 * 1024**2
        self.assertTrue(unsafe(sample, CONFIG["hardware"]))
        with self.assertRaises(RuntimeError):
            gate(sample, gpu, CONFIG["hardware"], True)


if __name__ == "__main__":
    unittest.main()
