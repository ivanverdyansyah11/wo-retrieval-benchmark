"""V2 runtime regressions. Synthetic fixtures here are never research/Kaggle evidence."""
import argparse
import ast
from contextlib import nullcontext
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from wo_retrieval import e5_portable_v2 as e

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "experiments/portable/e5_cpu_smoke_v2"
spec = importlib.util.spec_from_file_location("portable_cli_v2", ROOT / "scripts/e5_portable_v2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def snapshot(base):
    path = Path(base) / "models--intfloat--multilingual-e5-small/snapshots" / e.REVISION
    path.mkdir(parents=True)
    files = dict(e.binding(BUNDLE)["files"])
    for name in files:
        contents = json.dumps({"hidden_size": 384, "max_position_embeddings": 512}) if name == "config.json" else "SYNTHETIC NOT MODEL WEIGHTS"
        (path / name).write_text(contents)
        files[name] = e.file_hash(path / name)
    return path, {"model_id": e.MODEL, "revision": e.REVISION, "files": files}


class SnapshotTests(unittest.TestCase):
    def test_partial_and_corrupt_cache_do_not_shadow_complete_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            partial, expected = snapshot(base / "partial")
            complete, _ = snapshot(base / "complete")
            (partial / "model.safetensors").unlink()
            diagnostics = []
            with patch.object(e, "cache_roots", return_value=[base / "partial", base / "complete"]):
                self.assertEqual(e.select_snapshot(base, expected, diagnostics=diagnostics), complete)
            self.assertEqual(diagnostics[0]["rejected"], "FileNotFoundError")
            (partial / "model.safetensors").write_text("CORRUPT")
            with patch.object(e, "cache_roots", return_value=[base / "partial", base / "complete"]):
                self.assertEqual(e.select_snapshot(base, expected), complete)
                with self.assertRaisesRegex(ValueError, "SHA256"):
                    e.select_snapshot(base, expected, explicit=partial)

    def test_all_six_files_revision_and_model_config_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, expected = snapshot(tmp)
            self.assertEqual(e.verify_snapshot(path, expected), path)
            for name in expected["files"]:
                original = (path / name).read_bytes()
                (path / name).write_bytes(b"corrupt")
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "SHA256"):
                    e.verify_snapshot(path, expected)
                (path / name).write_bytes(original)
            with self.assertRaisesRegex(ValueError, "basename"):
                e.verify_snapshot(path.parent, expected)
            (path / "config.json").write_text('{"hidden_size":1024,"max_position_embeddings":512}')
            expected["files"]["config.json"] = e.file_hash(path / "config.json")
            with self.assertRaisesRegex(ValueError, "dimension"):
                e.verify_snapshot(path, expected)

    def test_huggingface_env_caches_and_workspace_are_discovered(self):
        roots = e.cache_roots("/workspace", {"HF_HUB_CACHE": "/explicit", "HF_HOME": "/home-hf", "XDG_CACHE_HOME": "/xdg"}, "/user")
        self.assertEqual(roots[:3], [Path("/explicit").absolute(), Path("/home-hf/hub").absolute(), Path("/xdg/huggingface/hub").absolute()])
        self.assertIn(Path("/workspace/.cache/huggingface/hub").absolute(), roots)

    def test_no_verified_cache_is_blocked_without_network_fallback(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(e, "cache_roots", return_value=[Path(tmp)]):
            with self.assertRaises(e.Blocked):
                e.select_snapshot(tmp, e.binding(BUNDLE))


class SafetyTests(unittest.TestCase):
    def test_session_closes_active_encoder_and_rejects_second_model(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(e, "resource_gate"), patch.object(e, "process_safety"):
            encoder = e.Encoder("synthetic", {}, BUNDLE)
            with e.inference_session(tmp):
                encoder.model = Mock()
                e._ACTIVE_ENCODER = encoder
                with self.assertRaises(e.Blocked):
                    e.Encoder("synthetic", {}, BUNDLE).load()
            self.assertIsNone(encoder.model)
            self.assertIsNone(e._ACTIVE_ENCODER)
            self.assertFalse(e._LOCK.locked())

    def test_host_ram_pressure_and_strict_commit_boundaries(self):
        safe = {"available_ram_bytes": 3 * 1024**3, "memory_percent": 89.9, "commit_headroom_bytes": None}
        with patch.object(e, "memory_sample", return_value=safe):
            self.assertIs(e.resource_gate(loading=True), safe)
        for changes in ({"available_ram_bytes": 3 * 1024**3 - 1}, {"memory_percent": 90}, {"commit_headroom_bytes": 2 * 1024**3 - 1}):
            with patch.object(e, "memory_sample", return_value={**safe, **changes}), self.assertRaises(e.Blocked):
                e.resource_gate(loading=True)
        with patch.object(e, "memory_sample", return_value={**safe, "available_ram_bytes": int(1.5 * 1024**3)}):
            e.resource_gate()

    def test_nested_cgroup_v2_and_v1_visible_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); group = base / "team/job"; group.mkdir(parents=True)
            (base / "memory.max").write_text("9000"); (base / "memory.current").write_text("1000")
            (group / "memory.max").write_text("4000"); (group / "memory.current").write_text("3000")
            proc = base / "proc"; proc.write_text("0::/team/job\n")
            self.assertEqual(sorted(e.cgroup_headrooms(base, proc)), [1000, 8000])
            v1 = base / "memory/job"; v1.mkdir(parents=True)
            (v1 / "memory.limit_in_bytes").write_text("5000"); (v1 / "memory.usage_in_bytes").write_text("4000")
            proc.write_text("4:memory:/job\n")
            self.assertIn(1000, e.cgroup_headrooms(base, proc))
            (v1 / "memory.usage_in_bytes").unlink()
            with self.assertRaises(FileNotFoundError):
                e.cgroup_headrooms(base, proc)

    def test_other_python_blocks_and_parent_kernel_is_allowed(self):
        current = Mock(pid=1); current.parents.return_value = [Mock(pid=2)]
        parent = Mock(pid=2, info={"name": "python"})
        sibling = Mock(pid=3, info={"name": "python"})
        with patch("psutil.Process", return_value=current), patch("psutil.process_iter", return_value=[parent]):
            e.process_safety()
        with patch("psutil.Process", return_value=current), patch("psutil.process_iter", return_value=[sibling]):
            with self.assertRaisesRegex(e.Blocked, "PID 3"):
                e.process_safety()

    def test_exclusive_lock_no_stale_stealing_and_release_after_exception(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(e, "resource_gate"), patch.object(e, "process_safety"):
            path = Path(tmp) / ".cache/e5_portable_v2/inference.lock"
            with self.assertRaisesRegex(ValueError, "fixture"):
                with e.inference_session(tmp):
                    with self.assertRaises(e.Blocked):
                        with e.inference_session(tmp):
                            pass
                    raise ValueError("fixture")
            self.assertFalse(path.exists()); self.assertFalse(e._LOCK.locked())
            path.write_text('{"pid":999999,"owner":"fixture"}')
            with self.assertRaises(e.Blocked):
                with e.inference_session(tmp):
                    pass
            self.assertTrue(path.exists()); self.assertFalse(e._LOCK.locked())

    def test_cpu_torch_and_no_mixed_stack_are_mandatory(self):
        pins = dict(line.split("==") for line in (BUNDLE / "runtime.txt").read_text().splitlines() if line and not line.startswith("#"))
        pins["torch"] = "2.12.1+cpu"
        with patch.object(e.metadata, "version", side_effect=lambda n: pins[n]), patch.object(e.metadata, "distributions", return_value=[]):
            self.assertEqual(e.dependency_check(BUNDLE), pins)
        pins["torch"] = "2.12.1+cu126"
        with patch.object(e.metadata, "version", side_effect=lambda n: pins[n]), self.assertRaisesRegex(e.Blocked, "torch"):
            e.dependency_check(BUNDLE)
        pins["torch"] = "2.12.1+cpu"
        with patch.object(e.metadata, "version", side_effect=lambda n: pins[n]), \
             patch.object(e.metadata, "distributions", return_value=[SimpleNamespace(metadata={"Name": "nvidia-cublas-cu12"})]), \
             self.assertRaisesRegex(e.Blocked, "isolated"):
            e.dependency_check(BUNDLE)

    def test_runtime_imports_no_historical_or_windows_api(self):
        source = Path(e.__file__).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any(n.name in ("ctypes", "msvcrt") for n in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, ("embedding_profiles", "e5_memory_recovery", "e5_development_evaluation"))
            if isinstance(node, ast.Attribute):
                self.assertNotEqual(node.attr, "windll")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotEqual(node.func.attr, "cuda")


class EncodingTests(unittest.TestCase):
    def test_ram_drop_after_import_tokenizer_stops_before_weight_loading(self):
        import torch
        from transformers import AutoModel, AutoTokenizer
        encoder = e.Encoder("synthetic", {}, BUNDLE)
        self.assertTrue(e._LOCK.acquire(blocking=False))
        try:
            with patch.object(e, "dependency_check", return_value={}), patch.object(e, "process_safety"), \
                 patch.object(e, "verify_snapshot", return_value=Path("synthetic")), \
                 patch.object(e, "resource_gate", side_effect=[{}, e.Blocked("RAM dropped")]) as gate, \
                 patch.object(torch.version, "cuda", None), patch.object(torch, "get_num_interop_threads", return_value=1), \
                 patch.object(AutoTokenizer, "from_pretrained", return_value=Mock()), \
                 patch.object(AutoModel, "from_pretrained") as load:
                with self.assertRaisesRegex(e.Blocked, "RAM dropped"):
                    encoder.load()
                load.assert_not_called()
                self.assertEqual(gate.call_count, 2)
                self.assertTrue(all(call.kwargs["loading"] for call in gate.call_args_list))
        finally:
            encoder.close()
            e._LOCK.release()

    def test_forward_query_passage_mask_padding_l2_cpu_fp32(self):
        import numpy as np
        import torch
        encoder = e.Encoder("unused", {}, BUNDLE)
        hidden = torch.zeros((1, 3, 384)); hidden[0, 0, 0] = 1.; hidden[0, 1, :2] = torch.tensor([3., 4.]); hidden[0, 2] = 999.
        features = {"input_ids": torch.tensor([[1, 2, 0]]), "attention_mask": torch.tensor([[1, 1, 0]])}
        def tokenize(text, **kwargs):
            self.assertIn(text, ("query: PIC", "passage: PIC"))
            return features if kwargs.get("return_tensors") else {"input_ids": [1, 2, 0]}
        encoder.tokenizer = Mock(side_effect=tokenize)
        def model(**kwargs):
            self.assertFalse(torch.is_grad_enabled())
            self.assertTrue(all(v.device.type == "cpu" for v in kwargs.values()))
            return SimpleNamespace(last_hidden_state=hidden)
        encoder.model = model
        self.assertTrue(e._LOCK.acquire(blocking=False))
        try:
            with patch.object(e, "resource_gate", return_value={}), patch.object(e, "process_safety"):
                for kind in ("query", "passage"):
                    value, info = encoder.encode(" PIC ", kind)
                    self.assertEqual((value.shape, value.dtype), ((1, 384), np.dtype("float32")))
                    np.testing.assert_allclose(value[0, :2], [2**-.5] * 2, atol=1e-6)
                    self.assertFalse(info["truncated"])
                hidden[:] = 0
                with self.assertRaisesRegex(ValueError, "Invalid E5 vector"):
                    encoder.encode("PIC", "query")
        finally:
            e._LOCK.release()

    def test_no_load_without_lock_no_batch_input_and_bounded_corpus(self):
        with self.assertRaises(e.Blocked):
            e.Encoder("unused", {}, BUNDLE).load()
        for text, kind in ((["batch"], "query"), ("", "query"), ("text", "document")):
            with self.assertRaises(ValueError):
                e.input_text(text, kind)
        for value in ("0", "6", "371"):
            with self.assertRaises(argparse.ArgumentTypeError):
                cli.limit(value)

    def test_frozen_sample_input_checks_hash_and_order_before_inference(self):
        rows = cli.sample_rows(ROOT / e.read_json(BUNDLE / "corpus-binding.json")["path"], 5)
        self.assertEqual(len(rows), 5)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrupt.jsonl"; path.write_text('{"text":"fake"}')
            with self.assertRaisesRegex(ValueError, "SHA256"):
                cli.sample_rows(path, 1)

    def test_bounded_cli_integration_with_mock_model_one_and_five_chunks(self):
        import numpy as np
        import torch
        class FakeEncoder:
            def __init__(self, *args):
                self.samples = [{"synthetic_fixture": True}]
                self.model = Mock(parameters=Mock(return_value=[torch.zeros(1)]))
                self.calls = []
            def load(self):
                pass
            def encode(self, text, kind):
                self.calls.append(kind)
                value = np.zeros((1, 384), dtype=np.float32); value[0, 0] = 1.
                return value, {"original_tokens": 10, "retained_tokens": 10, "truncated": False}
            def close(self):
                pass
        for count in (1, 5):
            with tempfile.TemporaryDirectory() as tmp:
                args = SimpleNamespace(stage="chunks", snapshot=Path("synthetic"), output=Path(tmp), limit=count,
                    chunks_file=ROOT / e.read_json(BUNDLE / "corpus-binding.json")["path"])
                receipt = {"query_embeddings_computed": 0, "corpus_embeddings_computed": 0}
                encoder = FakeEncoder()
                with patch.object(e, "resource_gate", return_value={}), patch.object(e, "process_safety"), \
                     patch.object(e, "dependency_check", return_value={}), \
                     patch.object(e, "select_snapshot", return_value=Path("synthetic")), \
                     patch.object(e, "inference_session", return_value=nullcontext()), \
                     patch.object(e, "Encoder", return_value=encoder), \
                     patch.object(cli.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
                    cli.run(args, receipt)
                self.assertEqual(encoder.calls, ["query"] + ["passage"] * count)
                self.assertEqual(receipt["corpus_embeddings_computed"], count)
                self.assertEqual(receipt["passage_shape"], [count, 384])
                self.assertEqual([r["chunk_id"] for r in receipt["dense_ranking"]], receipt["sample_chunk_ids"])
                self.assertEqual(np.load(Path(tmp) / "passages.npy", allow_pickle=False).shape, (count, 384))

    def test_failed_dependency_or_snapshot_does_not_construct_encoder(self):
        args = SimpleNamespace(stage="short", snapshot=Path("invalid"))
        for stage in ("dependency_check", "select_snapshot"):
            with patch.object(e, "resource_gate", return_value={}), patch.object(e, "process_safety"), \
                 patch.object(e, "dependency_check", return_value={}), \
                 patch.object(cli.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")), \
                 patch.object(e, stage, side_effect=e.Blocked("fixture STOP")), patch.object(e, "Encoder") as encoder:
                with self.assertRaisesRegex(e.Blocked, "STOP"):
                    cli.run(args, {})
                encoder.assert_not_called()


if __name__ == "__main__":
    unittest.main()
