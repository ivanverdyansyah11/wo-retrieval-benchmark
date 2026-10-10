"""CPU-only V2 isolation, serialization, persistence and reuse checks."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_v2_indexes", ROOT / "scripts/prepare_v2_indexes.py")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)


class V2PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.rows, cls.stats = v2.bind_v2(ROOT)

    def test_snapshot_overlay_preserves_parameters_and_protocol(self):
        original = v2.read_protocol(ROOT)
        for key in original.keys() - {"snapshot"}:
            self.assertEqual(original[key], self.config[key])
        self.assertNotEqual(original["snapshot"], self.config["snapshot"])
        self.assertEqual(original["snapshot"]["id"], "WO-CORPUS-V1-DRAFT-PILOT-001")
        self.assertEqual(self.config["snapshot"]["id"], v2.SNAPSHOT)

    def test_exact_serialization_parity_all_chunks(self):
        old, _ = v2.prepare(ROOT, v2.read_protocol(ROOT))
        changed = [b["chunk_id"] for a, b in zip(old, self.rows, strict=True) if a["text"] != b["text"]]
        self.assertEqual(changed, ["WO-DOC-024-C003", "WO-DOC-027-C009"])
        self.assertEqual(self.stats["chunks"], 371)
        self.assertEqual(self.stats["xlsx_with_guide_context"], 53)
        self.assertEqual(self.stats["empty_documents"], 0)
        self.assertEqual(self.stats["duplicate_serialized_documents"], 0)

    def test_serialization_excludes_audit_metadata(self):
        from wo_retrieval.retrieval.text import serialize
        original = v2.jsonl(ROOT / v2.VERSION / "chunks/chunks.jsonl")
        for chunk in original:
            poisoned = copy.deepcopy(chunk)
            for key in ("validation_status", "source_file", "query_evidence", "qrels"):
                poisoned[key] = "SHOULD_NOT_BE_RETRIEVABLE"
            self.assertEqual(serialize(chunk, self.config["serialization"]), serialize(poisoned, self.config["serialization"]))

    def test_roundtrip_both_indexes_and_version_isolation(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v1_dir = root / "experiments/indexes/R1"
            v1_dir.mkdir(parents=True)
            sentinel = v1_dir / "sentinel"
            sentinel.write_bytes(b"immutable-v1")
            for relative in ("experiments/configs/retrieval_protocol_v1.toml", "experiments/configs/lexical_environment.lock.txt"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / relative).read_bytes())
            # Snapshot trust boundary is tested separately against both real manifests.
            with patch.object(v2, "verify_snapshot"):
                for method in ("R1", "R2"):
                    result = v2.build_index(root, method, self.rows, self.config, self.stats)
                    directory = Path(result["path"])
                    identity = v2.identity(root, self.config, method)
                    loaded = v2.verify_index(directory, self.rows, self.config, identity, self.stats)
                    fresh = v2.LexicalRetriever(method, self.rows, self.config).fit()
                    self.assertEqual(loaded.retrieve("vendor akad", 5), fresh.retrieve("vendor akad", 5))
                    self.assertTrue(all(r.snapshot_id == v2.SNAPSHOT for r in loaded.retrieve("vendor", 5)))
                    wrong = copy.deepcopy(identity)
                    wrong["snapshot_id"] = "WO-CORPUS-V1-DRAFT-PILOT-001"
                    with self.assertRaises(ValueError):
                        v2.verify_index(directory, self.rows, self.config, wrong, self.stats)
                    with self.assertRaises(FileExistsError):
                        v2.build_index(root, method, self.rows, self.config, self.stats)
                    artifact = directory / "documents.json"
                    artifact.write_bytes(artifact.read_bytes() + b" ")
                    with self.assertRaises(ValueError):
                        v2.verify_index(directory, self.rows, self.config, identity, self.stats)
            self.assertEqual(sentinel.read_bytes(), b"immutable-v1")

    def test_reuse_requires_exact_inputs_contract_and_mapping(self):
        old = {"chunk_id": "C1", "document_id": "D1", "text": "original", "text_sha256": "hash1"}
        mapped = {"chunk_id": "C1", "document_id": "D1", "serialized_text_sha256": "hash1"}
        vector = np.zeros((1, 1024), np.float32)
        vector[0, 0] = 1
        self.assertEqual(v2.eligible(old, old, mapped, vector)["status"], "REUSABLE_VERIFIED")
        cases = [({**old, "text": "changed"}, mapped, True),
                 ({**old, "text_sha256": "changed"}, mapped, True),
                 (old, {**mapped, "document_id": "wrong"}, True), (old, mapped, False)]
        for new, source, contract in cases:
            self.assertEqual(v2.eligible(old, new, source, vector, contract)["status"], "REQUIRES_REEMBEDDING")

    def test_bad_vectors_cannot_be_reused(self):
        old = {"chunk_id": "C", "document_id": "D", "text": "text", "text_sha256": "h"}
        mapped = {"chunk_id": "C", "document_id": "D", "serialized_text_sha256": "h"}
        for vector in (np.zeros((1, 1024), np.float32), np.ones((1, 1024), np.float32),
                       np.full((1, 1024), np.nan, np.float32), np.full((1, 1024), np.inf, np.float32),
                       np.zeros((1, 1023), np.float32), np.zeros((1, 1024), np.float64)):
            self.assertEqual(v2.eligible(old, old, mapped, vector)["status"], "REQUIRES_REEMBEDDING")


if __name__ == "__main__":
    unittest.main()
