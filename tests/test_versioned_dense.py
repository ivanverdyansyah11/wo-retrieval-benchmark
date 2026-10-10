"""No neural imports/inference: version binding, incremental assembly and safety."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from wo_retrieval import versioned_dense as dense
from wo_retrieval.dense.index import load_vectors
from wo_retrieval.retrieval.lexical import digest, read_protocol

ROOT = Path(__file__).resolve().parents[1]
CONFIG = read_protocol(ROOT)


def vector(axis):
    value = np.zeros((1, 1024), np.float32)
    value[0, axis] = 1
    return value


def fixture(root):
    rows = [{"chunk_id": f"C{i}", "document_id": "D", "text_sha256": f"new{i}"} for i in range(3)]
    mapping = [{"chunk_id": r["chunk_id"], "document_id": "D", "serialized_text_sha256": r["text_sha256"], "token_length": 5} for r in rows]
    identity = {"row_mapping_hash": digest(mapping), "model_id": "SYNTHETIC_FIXTURE", "model_revision": "fixture",
        "precision": "float16", "device": "cuda:0", "max_length": 640, "normalization": "L2", "dimension": 1024}
    source = np.concatenate([vector(0), vector(1), vector(2)])
    receipts = [{"chunk_id": r["chunk_id"], "document_id": "D", "v1_row_index": i, "v2_row_index": i,
        "v1_input_sha256": r["text_sha256"] if i == 0 else f"old{i}", "v2_input_sha256": r["text_sha256"],
        "vector_raw_float32_sha256": sha256(source[i].tobytes()).hexdigest(),
        "status": "REUSABLE_VERIFIED" if i == 0 else "REQUIRES_REEMBEDDING"} for i, r in enumerate(rows)]
    new = {r["chunk_id"]: {**{k: identity[k] for k in ("model_id", "model_revision", "precision", "device", "max_length", "normalization", "dimension")},
        "input_sha256": r["text_sha256"], "actual_tokens": 5, "truncation": False, "vector": vector(i + 3)} for i, r in enumerate(rows) if i > 0}
    context = {"root": root, "binding": {"r3_index": "experiments/indexes/v2_ai_corrected/R3", "eligibility_manifest_sha256": "fixture"},
        "rows": rows, "mapping": mapping, "identity": identity, "source_vectors": source,
        "audit": {"rows": receipts, "source_manifest_sha256": "fixture"}}
    return context, new


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "experiments/configs").mkdir(parents=True)
        (self.root / "experiments/configs/dense_v2_binding.json").write_text("fixture")
        self.context, self.new = fixture(self.root)

    def assemble(self):
        c = self.context
        return dense.assemble(c["rows"], c["mapping"], c["identity"], c["source_vectors"], c["audit"]["rows"], self.new)

    def test_merge_preserves_reused_bytes_and_new_order(self):
        final = self.assemble()
        self.assertEqual(final.shape, (3, 1024))
        self.assertEqual(final[0].tobytes(), self.context["source_vectors"][0].tobytes())
        np.testing.assert_array_equal(final[1], self.new["C1"]["vector"][0])
        np.testing.assert_array_equal(final[2], self.new["C2"]["vector"][0])

    def test_input_hash_mismatch_rejected(self):
        self.new["C1"]["input_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "input/token"):
            self.assemble()

    def test_new_model_revision_precision_config_mismatch_rejected(self):
        for key in ("model_id", "model_revision", "precision", "device", "normalization", "max_length", "dimension"):
            saved = self.new["C1"][key]
            self.new["C1"][key] = "wrong"
            with self.assertRaisesRegex(ValueError, "contract mismatch"):
                self.assemble()
            self.new["C1"][key] = saved

    def test_bad_new_vectors_rejected(self):
        for invalid in (np.zeros((1, 1024), np.float32), np.ones((1, 1024), np.float32),
                        np.full((1, 1024), np.nan, np.float32), np.full((1, 1024), np.inf, np.float32),
                        vector(1).astype(np.float64), np.ones((1, 1000), np.float32)):
            self.new["C1"]["vector"] = invalid
            with self.assertRaises(ValueError):
                self.assemble()

    def test_missing_extra_new_vector_rejected(self):
        removed = self.new.pop("C1")
        with self.assertRaisesRegex(ValueError, "Missing/extra"):
            self.assemble()
        self.new["C1"] = removed
        self.new["UNKNOWN"] = removed
        with self.assertRaisesRegex(ValueError, "Missing/extra"):
            self.assemble()

    def test_missing_duplicate_unordered_mapping_rejected(self):
        original = copy.deepcopy(self.context)
        for field in ("mapping", "rows"):
            self.context = copy.deepcopy(original)
            self.context[field] = self.context[field][:-1]
            with self.assertRaises(ValueError):
                self.assemble()
        self.context = copy.deepcopy(original)
        self.context["rows"][1]["chunk_id"] = "C0"
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.assemble()

    def test_reuse_source_and_hash_mismatch_rejected(self):
        self.context["audit"]["rows"][0]["v1_input_sha256"] = "changed"
        with self.assertRaisesRegex(ValueError, "Reusable input"):
            self.assemble()
        self.context["audit"]["rows"][0]["v1_input_sha256"] = "new0"
        self.context["source_vectors"][0] = vector(7)[0]
        with self.assertRaisesRegex(ValueError, "source vector"):
            self.assemble()

    def test_truncation_and_token_mismatch_rejected(self):
        self.new["C1"]["truncation"] = True
        with self.assertRaises(ValueError):
            self.assemble()
        self.new["C1"]["truncation"] = False
        self.new["C1"]["actual_tokens"] = 4
        with self.assertRaises(ValueError):
            self.assemble()

    def test_atomic_complete_readback_no_overwrite(self):
        directory = self.root / self.context["binding"]["r3_index"]
        calls = []
        def verify():
            self.assertFalse(directory.exists())
            calls.append(True)
        manifest = dense.publish(self.context, self.new, verify)
        self.assertEqual(calls, [True])
        self.assertEqual(manifest["completion_status"], "COMPLETE")
        matrix, saved = load_vectors(directory, self.context["identity"], self.context["mapping"])
        np.testing.assert_array_equal(matrix, self.assemble())
        self.assertEqual(saved["reused_verified_vectors"], 1)
        with self.assertRaises(FileExistsError):
            dense.publish(self.context, self.new, verify)

    def test_failed_final_verification_leaves_incomplete_unpublished(self):
        def failure():
            raise ValueError("fixture source changed")
        with self.assertRaisesRegex(ValueError, "source changed"):
            dense.publish(self.context, self.new, failure)
        self.assertFalse((self.root / self.context["binding"]["r3_index"]).exists())
        staging = next((self.root / "experiments/indexes/v2_ai_corrected").glob("R3.incomplete-*"))
        self.assertEqual(json.loads((staging / "manifest.json").read_text())["completion_status"], "INCOMPLETE")
        with self.assertRaises(ValueError):
            load_vectors(staging, self.context["identity"], self.context["mapping"])

    def test_exact_search_fixture_finite_ties_correct_snapshot(self):
        result = dense.offline_sanity(self.context["rows"], self.assemble(), "V2_FIXTURE")
        self.assertEqual(result["mode"], "synthetic_basis_vector_fixture_not_query_embedding")
        self.assertEqual([r["chunk_id"] for r in result["results"]], ["C0", "C1", "C2"])
        self.assertEqual([r["score"] for r in result["results"]], [1, 0, 0])
        self.assertTrue(all(r["snapshot_id"] == "V2_FIXTURE" for r in result["results"]))


class VersionSafetyTests(unittest.TestCase):
    def test_default_v1_delegates_unchanged(self):
        with patch.object(dense, "load_v1_components", return_value="v1") as loader:
            self.assertEqual(dense.load_components(ROOT, v1_dense_index="fixture"), "v1")
            loader.assert_called_once()

    def test_invalid_version_or_v2_v1_path_rejected(self):
        for version, path in (("v3", None), ("v1", None), ("v2", "V1_CACHE")):
            with self.assertRaises(ValueError):
                dense.load_components(ROOT, version, path)

    def test_missing_v2_never_falls_back(self):
        with patch.object(dense, "prepare_v2", return_value={"binding": {"r3_index": "MISSING"}, "identity": {}, "mapping": []}), \
                patch.object(dense, "load_v1_components") as old:
            with self.assertRaises(FileNotFoundError):
                dense.load_components(ROOT, "v2")
            old.assert_not_called()

    def test_wrong_snapshot_binding_and_protocol_hash_rejected(self):
        binding = json.loads((ROOT / "experiments/configs/dense_v2_binding.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "experiments/configs/dense_v2_binding.json"
            path.parent.mkdir(parents=True)
            bad = {**binding, "snapshot_fingerprint": "wrong"}
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "binding"):
                dense.read_binding(root)
        self.assertEqual(dense.read_binding(ROOT)[0], binding)

    def test_gate_fail_prevents_encoder_and_retry(self):
        sample = {"available_ram_bytes": int(4.25 * 1024**3), "commit_headroom_bytes": 10 * 1024**3,
            "memory_load_percent": 74, "disk_free_bytes": {"C:/": 13 * 1024**3, "D:/": 800 * 1024**3}}
        gpu = {"free_mib": 4000, "used_mib": 0}
        with tempfile.TemporaryDirectory() as tmp, patch.object(dense, "read_protocol", return_value=CONFIG), \
                patch.object(dense, "resource", return_value=sample), patch.object(dense, "gpu_resource", return_value=gpu), \
                patch.object(dense, "BGEEncoder") as encoder, patch.object(dense, "prepare_v2") as prepare:
            with self.assertRaisesRegex(RuntimeError, "below 5 GiB"):
                dense.complete_v2(Path(tmp), True, "fixture approval")
            encoder.assert_not_called()
            prepare.assert_not_called()

    def test_default_6_and_approved_5_gate_unchanged(self):
        sample = {"available_ram_bytes": int(5.5 * 1024**3), "commit_headroom_bytes": 10 * 1024**3,
            "memory_load_percent": 65, "disk_free_bytes": {"C:/": 13 * 1024**3, "D:/": 800 * 1024**3}}
        gpu = {"free_mib": 4000, "used_mib": 0}
        with self.assertRaisesRegex(RuntimeError, "below 6 GiB"):
            dense.gate(sample, gpu, CONFIG["hardware"], False)
        dense.gate(sample, gpu, CONFIG["hardware"], True)

    def test_missing_approval_rejected(self):
        with self.assertRaisesRegex(ValueError, "approval"):
            dense.complete_v2(ROOT)

    def test_final_post_import_gate_prevents_weights_loading(self):
        sample = {"available_ram_bytes": int(5.5 * 1024**3), "commit_headroom_bytes": 10 * 1024**3,
            "memory_load_percent": 65, "disk_free_bytes": {"C:/": 13 * 1024**3, "D:/": 800 * 1024**3}}
        low = {**sample, "available_ram_bytes": int(4.9 * 1024**3)}
        torch = MagicMock()
        torch.__version__ = "2.12.1+cu126"
        torch.cuda.is_available.return_value = True
        torch.cuda.get_device_capability.return_value = (6, 1)
        torch.cuda.get_arch_list.return_value = ["sm_61"]
        torch.cuda.get_device_name.return_value = "FIXTURE"
        torch.version.cuda = "12.6"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = copy.deepcopy(CONFIG)
            config["R3"]["cache"]["root"] = str(root)
            context, _ = fixture(root)
            context.update(config=config, local=root)
            context["binding"]["changed_chunk_ids"] = ["C1", "C2"]
            for row in context["rows"]:
                row["text"] = "synthetic"
            with patch.object(dense, "read_protocol", return_value=config), \
                    patch.object(dense, "resource", side_effect=[sample, low, low]), \
                    patch.object(dense, "gpu_resource", return_value={"free_mib": 4000, "used_mib": 0}), \
                    patch.object(dense, "prepare_v2", return_value=context), \
                    patch.object(dense, "BGEEncoder") as encoder, patch.object(dense, "Monitor") as monitor, \
                    patch.object(dense, "other_model_processes", return_value=[]), \
                    patch.dict("sys.modules", {"torch": torch, "FlagEmbedding": MagicMock()}):
                encoder.return_value.tokens.return_value = {"input_ids": [0]*5}
                monitor.return_value.summary = {}
                with self.assertRaisesRegex(RuntimeError, "below 5 GiB"):
                    dense.complete_v2(root, True, "fixture explicit approval")
                encoder.return_value.load.assert_not_called()
                encoder.return_value.encode.assert_not_called()
                encoder.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
