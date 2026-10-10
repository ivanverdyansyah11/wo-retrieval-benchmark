"""Local-only official BGE-M3 forward, without automatic wrapper retries."""

import gc
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
from time import perf_counter

import numpy as np

from wo_retrieval.retrieval.text import normalize


def offline_environment() -> None:
    for name, value in {"HF_HOME": "D:/ModelCache/huggingface", "HF_HUB_CACHE": "D:/ModelCache/huggingface/hub",
                        "TORCH_HOME": "D:/ModelCache/torch", "PIP_CACHE_DIR": "D:/ModelCache/pip",
                        "TMP": "D:/ModelCache/tmp", "TEMP": "D:/ModelCache/tmp",
                        "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1",
                        "OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4"}.items():
        os.environ[name] = value


def model_files(root: Path, config: dict) -> tuple[Path, dict]:
    lock = json.loads((root / "experiments/configs/ml_environment.lock.json").read_text(encoding="utf-8"))["model"]
    cfg = config["R3"]
    if lock["repo_id"] != cfg["model_id"] or lock["revision"] != cfg["revision"]:
        raise ValueError("Model revision differs from approved local checkpoint")
    path = Path(lock["snapshot_path"]).resolve()
    if path.name != cfg["revision"] or not path.is_relative_to(Path("D:/ModelCache/huggingface/hub").resolve()):
        raise ValueError("Model must use the pinned D: cache snapshot")
    hashes = {}
    for item in lock["files"]:
        artifact = (path / item["file"]).resolve()
        if not artifact.is_relative_to(path):
            raise ValueError("Model artifact escapes snapshot")
        hasher = sha256()
        with artifact.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(block)
        if artifact.stat().st_size != item["bytes"] or hasher.hexdigest() != item["sha256"]:
            raise ValueError(f"Local model artifact mismatch: {item['file']}")
        hashes[item["file"]] = hasher.hexdigest()
    return path, hashes


def validate_config(config: dict) -> None:
    cfg = config["R3"]
    expected = {"model_id": "BAAI/bge-m3", "revision": "5617a9f61b028005a4858fdac845db406aefb181",
                "torch_version": "2.12.1+cu126", "library_version": "1.4.2", "transformers_version": "4.57.6",
                "device": "cuda:0", "precision": "float16", "batch_size": 1, "processes": 1,
                "max_length": 640, "dimension": 1024, "return_dense": True, "return_sparse": False,
                "return_colbert_vecs": False, "ann_index": False, "automatic_oom_retry": False}
    if any(cfg.get(key) != value for key, value in expected.items()):
        raise ValueError("Unsupported R3 configuration; no automatic model/precision fallback")
    for package, key in (("torch", "torch_version"), ("FlagEmbedding", "library_version"), ("transformers", "transformers_version")):
        if version(package) != cfg[key]:
            raise ValueError(f"Pinned dependency mismatch: {package}")


def unit_vectors(values, dimension: int = 1024) -> np.ndarray:
    vectors = np.asarray(values, dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[1] != dimension or not np.isfinite(vectors).all():
        raise ValueError("Invalid dense embedding shape/nonfinite values")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if not np.isfinite(norms).all() or np.any(norms <= 0):
        raise ValueError("Zero/invalid dense vector norm")
    return vectors / norms


class BGEEncoder:
    def __init__(self, path: Path, config: dict):
        offline_environment()
        validate_config(config)
        from transformers import AutoTokenizer
        self.config, self.path = config, path
        self.tokenizer = AutoTokenizer.from_pretrained(str(path), use_fast=True, local_files_only=True, trust_remote_code=False)
        self.model = None
        self.loading_seconds = None
        self.lock = None

    def tokens(self, text: str) -> dict:
        tokens = self.tokenizer(normalize(text), add_special_tokens=True, truncation=False, padding=False)
        if len(tokens["input_ids"]) > self.config["R3"]["max_length"]:
            raise ValueError(f"Input exceeds 640-token cap: {len(tokens['input_ids'])}; truncation forbidden")
        return tokens

    def load(self, lock_path: Path) -> None:
        import msvcrt
        import torch
        from FlagEmbedding import BGEM3FlagModel
        if self.model is not None:
            raise RuntimeError("Model is already loaded")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = lock_path.open("a+b")
        self.lock.seek(0)
        try:
            msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            self.lock.close()
            self.lock = None
            raise RuntimeError("Another managed BGE-M3 inference process holds the GPU lock") from None
        if torch.__version__ != self.config["R3"]["torch_version"] or not torch.cuda.is_available():
            raise RuntimeError("Pinned CUDA runtime unavailable; no CPU fallback")
        if torch.cuda.get_device_capability(0) != (6, 1) or "sm_61" not in torch.cuda.get_arch_list():
            raise RuntimeError("GPU architecture differs from validated Pascal environment")
        torch.set_num_threads(self.config["hardware"]["threads"])
        torch.cuda.reset_peak_memory_stats()
        started = perf_counter()
        self.model = BGEM3FlagModel(str(self.path), use_fp16=True, devices=["cuda:0"], batch_size=1,
                                  query_max_length=640, passage_max_length=640, normalize_embeddings=True,
                                  pooling_method="cls", return_dense=True, return_sparse=False, return_colbert_vecs=False,
                                  trust_remote_code=False, cache_dir=os.environ["HF_HUB_CACHE"])
        self.model.model.eval().to("cuda:0")
        torch.cuda.synchronize()
        self.loading_seconds = perf_counter() - started
        if str(next(self.model.model.parameters()).dtype) != "torch.float16":
            raise RuntimeError("Expected GPU FP16 weights")

    def encode(self, text: str) -> np.ndarray:
        import torch
        if self.model is None:
            raise RuntimeError("Explicit resource-gated model loading is required")
        tokens = self.tokens(text)
        inputs = self.tokenizer.pad([tokens], padding=True, return_tensors="pt").to("cuda:0")
        torch.cuda.synchronize()
        with torch.inference_mode():
            output = self.model.model(inputs, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        torch.cuda.synchronize()
        if set(output) != {"dense_vecs"}:
            raise ValueError("Unexpected sparse/multi-vector output")
        return output["dense_vecs"].float().cpu().numpy()

    def metrics(self) -> dict:
        import torch
        return {"model_loading_seconds": self.loading_seconds, "peak_gpu_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_gpu_reserved_bytes": torch.cuda.max_memory_reserved(), "cuda_runtime": torch.version.cuda,
                "gpu_name": torch.cuda.get_device_name(0), "gpu_capability": list(torch.cuda.get_device_capability(0))}

    def close(self) -> None:
        import msvcrt
        import torch
        self.model = None
        gc.collect()
        if torch.cuda.is_initialized():
            torch.cuda.empty_cache()
        if self.lock is not None:
            self.lock.seek(0)
            msvcrt.locking(self.lock.fileno(), msvcrt.LK_UNLCK, 1)
            self.lock.close()
            self.lock = None
