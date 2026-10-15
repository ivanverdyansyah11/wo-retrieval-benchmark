"""Standalone E5 CPU experiment v2. No historical encoder/recovery/BGE imports.

Imports are light; weights load only under a process/resource-gated context.
CPU-only torch is mandatory. Historical v1 index identities remain untouched.
"""
from contextlib import contextmanager
from hashlib import sha256
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import re
import threading
import unicodedata
from uuid import uuid4

MODEL = "intfloat/multilingual-e5-small"
REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
DIMENSION, MAX_LENGTH = 384, 256
_LOCK = threading.Lock()
_ACTIVE_ENCODER = None


class Blocked(RuntimeError):
    """Missing environment/resource prerequisite; never retried automatically."""


def cpu_environment():
    os.environ.update(CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2",
                      OPENBLAS_NUM_THREADS="2", TOKENIZERS_PARALLELISM="false")


def file_hash(path):
    h = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def binding(bundle):
    value = read_json(Path(bundle) / "snapshot.json")
    names = {"config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
             "model.safetensors", "sentencepiece.bpe.model"}
    if (value.get("model_id") != MODEL or value.get("revision") != REVISION
            or set(value.get("files", {})) != names
            or any(not re.fullmatch(r"[a-f0-9]{64}", h) for h in value["files"].values())):
        raise ValueError("Unsupported pinned snapshot binding")
    return value


def verify_snapshot(path, expected):
    path = Path(path).expanduser().absolute()
    if path.name != REVISION:
        raise ValueError("Snapshot basename must be the pinned revision")
    # HF snapshots legitimately use symlinks into the hub blobs directory.
    for name, wanted in expected["files"].items():
        if not (path / name).is_file():
            raise FileNotFoundError("Incomplete pinned snapshot: " + name)
        if file_hash(path / name) != wanted:
            raise ValueError("Snapshot SHA256 mismatch: " + name)
    config = read_json(path / "config.json")
    if config.get("hidden_size") != DIMENSION or config.get("max_position_embeddings") != 512:
        raise ValueError("E5 model dimension/position contract mismatch")
    return path


def cache_roots(root, env=None, home=None):
    env = os.environ if env is None else env
    home = Path.home() if home is None else Path(home)
    roots = []
    if env.get("HF_HUB_CACHE"):
        roots.append(Path(env["HF_HUB_CACHE"]).expanduser())
    if env.get("HF_HOME"):
        roots.append(Path(env["HF_HOME"]).expanduser() / "hub")
    cache_home = Path(env.get("XDG_CACHE_HOME", str(home / ".cache"))).expanduser()
    roots.extend([cache_home / "huggingface/hub", Path(root) / ".cache/huggingface/hub"])
    # Preserve discoverability of an old Windows installation without requiring it.
    if platform.system() == "Windows":
        roots.append(Path("D:/ModelCache/huggingface/hub"))
    return list(dict.fromkeys(p.absolute() for p in roots))


def select_snapshot(root, expected, explicit=None, diagnostics=None):
    diagnostics = [] if diagnostics is None else diagnostics
    if explicit is not None:
        return verify_snapshot(explicit, expected)  # Explicit corruption must fail, not silently fall back.
    suffix = Path("models--intfloat--multilingual-e5-small/snapshots") / REVISION
    for base in cache_roots(root):
        candidate = base / suffix
        if not candidate.exists():
            continue
        try:
            return verify_snapshot(candidate, expected)
        except (FileNotFoundError, ValueError, OSError) as error:
            diagnostics.append({"cache": str(base), "rejected": type(error).__name__})
    raise Blocked("No complete SHA256-verified pinned snapshot; use explicit download or --snapshot")


def download(root, expected):
    resource_gate(loading=True)
    from huggingface_hub import snapshot_download
    # Always use a writable workspace cache. Authentication/config are not exported.
    path = snapshot_download(MODEL, revision=REVISION, max_workers=1,
            cache_dir=str(Path(root) / ".cache/huggingface/hub"), allow_patterns=list(expected["files"]))
    return verify_snapshot(path, expected)


def cgroup_headrooms(base=Path("/sys/fs/cgroup"), proc=Path("/proc/self/cgroup")):
    """Conservatively check visible v1/v2 limits, including visible ancestors."""
    base = Path(base)
    paths = [(base, "memory.max", "memory.current")]
    if proc.is_file():
        for line in proc.read_text().splitlines():
            _, controllers, relative = line.split(":", 2)
            if ".." in Path(relative).parts:
                raise Blocked("Cannot safely resolve cgroup path")
            if controllers == "":
                paths.append((base / relative.lstrip("/"), "memory.max", "memory.current"))
            elif "memory" in controllers.split(","):
                paths.extend([(base / "memory", "memory.limit_in_bytes", "memory.usage_in_bytes"),
                              (base / "memory" / relative.lstrip("/"), "memory.limit_in_bytes", "memory.usage_in_bytes")])
    values, visited = [], set()
    for location, limit_name, usage_name in paths:
        while location.is_relative_to(base):
            key = (location, limit_name)
            if key not in visited and (location / limit_name).is_file():
                visited.add(key)
                limit = (location / limit_name).read_text().strip()
                if limit != "max":
                    # Unreadable/missing usage for a visible finite limit fails closed.
                    values.append(max(0, int(limit) - int((location / usage_name).read_text().strip())))
            if location == base:
                break
            location = location.parent
    return values


def memory_sample():
    import psutil
    vm = psutil.virtual_memory()
    sample = {"available_ram_bytes": vm.available, "memory_percent": vm.percent,
              "rss_bytes": psutil.Process().memory_info().rss,
              "commit_headroom_bytes": None,
              "commit_policy": "Portable physical/container gates; Windows commit API is not used"}
    if platform.system() == "Linux":
        ceilings = cgroup_headrooms()
        sample["visible_cgroup_headrooms_bytes"] = ceilings
        if ceilings:
            sample["available_ram_bytes"] = min(vm.available, *ceilings)
        info, mode = Path("/proc/meminfo"), Path("/proc/sys/vm/overcommit_memory")
        if info.is_file() and mode.is_file() and mode.read_text().strip() == "2":
            fields = {line.split(":")[0]: int(line.split()[1]) * 1024 for line in info.read_text().splitlines()
                      if line.startswith(("CommitLimit:", "Committed_AS:"))}
            sample["commit_headroom_bytes"] = fields["CommitLimit"] - fields["Committed_AS"]
            sample["commit_policy"] = "Linux strict overcommit: CommitLimit minus Committed_AS"
    return sample


def resource_gate(loading=False):
    sample = memory_sample()
    minimum = 3 if loading else 1.5
    if (sample["available_ram_bytes"] < minimum * 1024**3 or sample["memory_percent"] >= 90
            or sample["commit_headroom_bytes"] is not None and sample["commit_headroom_bytes"] < 2 * 1024**3):
        raise Blocked("STOP: unsafe RAM/container/strict-commit headroom; no automatic retry")
    return sample


def process_safety():
    import psutil
    current = psutil.Process()
    family = {current.pid, *(p.pid for p in current.parents())}
    try:
        for proc in psutil.process_iter(["name"]):
            if proc.pid not in family and "python" in (proc.info["name"] or "").casefold():
                raise Blocked("Other Python workload exists; inspect PID " + str(proc.pid))
    except (psutil.AccessDenied, psutil.NoSuchProcess) as error:
        raise Blocked("Cannot verify process safety; inspect workloads") from error


@contextmanager
def inference_session(root):
    """Exclusive portable lock; stale lock is never stolen/deleted automatically."""
    if not _LOCK.acquire(blocking=False):
        raise Blocked("E5 model already active in this process")
    path, owned, token = Path(root) / ".cache/e5_portable_v2/inference.lock", False, uuid4().hex
    try:
        resource_gate(loading=True)
        process_safety()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf8") as stream:
                json.dump({"pid": os.getpid(), "owner": token}, stream)
            owned = True
        except FileExistsError as error:
            raise Blocked("Existing E5 v2 lock; inspect owner before removing a stale lock") from error
        yield
    finally:
        try:
            if _ACTIVE_ENCODER is not None:
                _ACTIVE_ENCODER.close()
            if owned and path.is_file() and read_json(path).get("owner") == token:
                path.unlink()
        finally:
            _LOCK.release()


def dependency_check(bundle):
    import sys
    if sys.version_info[:2] != (3, 12):
        raise Blocked("Python 3.12 is required")
    pins = dict(line.split("==", 1) for line in (Path(bundle) / "runtime.txt").read_text().splitlines()
                if line.strip() and not line.startswith("#"))
    pins["torch"] = "2.12.1+cpu"
    actual = {}
    for name, wanted in pins.items():
        try:
            actual[name] = metadata.version(name)
        except metadata.PackageNotFoundError as error:
            raise Blocked("Missing E5 CPU dependency: " + name) from error
        if actual[name] != wanted:
            raise Blocked("E5 CPU dependency mismatch: " + name + "; expected " + wanted)
    # No BGE/CUDA package is required or imported; mixed installed stacks fail closed.
    installed = {d.metadata["Name"].casefold().replace("_", "-") for d in metadata.distributions()}
    if any(n.startswith("nvidia-") or n in {"flagembedding", "datasets", "ir-datasets", "sentence-transformers", "peft"} for n in installed):
        raise Blocked("Use the isolated E5 CPU environment; BGE/CUDA/dataset stack detected")
    return actual


def input_text(text, kind):
    if kind not in ("query", "passage") or not isinstance(text, str):
        raise ValueError("One query/passage string is required")
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n")).strip()
    if not text:
        raise ValueError("Empty embedding input")
    return kind + ": " + text


class Encoder:
    def __init__(self, snapshot, expected, bundle):
        self.snapshot, self.expected, self.bundle = snapshot, expected, bundle
        self.model = self.tokenizer = None
        self.samples = []

    def load(self):
        global _ACTIVE_ENCODER
        if not _LOCK.locked() or self.model is not None or _ACTIVE_ENCODER is not None:
            raise Blocked("Fresh inference_session required for model loading")
        cpu_environment()
        dependency_check(self.bundle)
        process_safety()
        self.samples.append(resource_gate(loading=True))
        path = verify_snapshot(self.snapshot, self.expected)
        import torch
        from transformers import AutoModel, AutoTokenizer
        if torch.version.cuda is not None:
            raise Blocked("CPU-only torch build required; no CUDA runtime permitted")
        torch.set_num_threads(2)
        if torch.get_num_interop_threads() != 1:
            torch.set_num_interop_threads(1)
        torch.use_deterministic_algorithms(True)
        self.tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True,
                                                     trust_remote_code=False, use_fast=True)
        self.tokenizer.truncation_side = "right"
        # Imports/tokenizer can consume substantial memory; recheck before weights.
        process_safety()
        self.samples.append(resource_gate(loading=True))
        _ACTIVE_ENCODER = self
        self.model = AutoModel.from_pretrained(str(path), local_files_only=True, trust_remote_code=False,
                dtype=torch.float32, device_map=None, attn_implementation="eager", use_safetensors=True)
        self.model.to(device="cpu", dtype=torch.float32).eval()
        if self.model.config.hidden_size != DIMENSION or any(
                p.device.type != "cpu" or p.dtype != torch.float32 for p in self.model.parameters()):
            raise ValueError("Model must be 384-dimensional CPU FP32")
        self.samples.append(resource_gate())

    def encode(self, text, kind):
        if not _LOCK.locked() or self.model is None:
            raise Blocked("Loaded model inside inference_session required")
        process_safety()
        self.samples.append(resource_gate())
        import torch
        value = input_text(text, kind)
        full = self.tokenizer(value, truncation=False, add_special_tokens=True)["input_ids"]
        features = self.tokenizer(value, truncation=True, max_length=MAX_LENGTH, padding=True, return_tensors="pt")
        features = {k: v.to("cpu") for k, v in features.items()}
        with torch.inference_mode():
            mask = features["attention_mask"]
            counts = mask.sum(dim=1)[..., None]
            if (counts <= 0).any():
                raise ValueError("Empty attention mask")
            hidden = self.model(**features).last_hidden_state
            pooled = hidden.masked_fill(~mask[..., None].bool(), 0.).sum(dim=1) / counts
            values = torch.nn.functional.normalize(pooled, p=2, dim=1).float().cpu().numpy()
        import numpy as np
        if (values.shape != (1, DIMENSION) or values.dtype != np.float32 or not np.isfinite(values).all()
                or not np.allclose(np.linalg.norm(values, axis=1), 1., atol=1e-5, rtol=0)):
            raise ValueError("Invalid E5 vector dimension/dtype/finiteness/norm")
        ids = features["input_ids"][0].tolist()
        self.samples.append(resource_gate())
        return values, {"original_tokens": len(full), "retained_tokens": len(ids),
                        "truncated": len(full) > MAX_LENGTH,
                        "effective_token_sha256": sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()}

    def close(self):
        global _ACTIVE_ENCODER
        import gc
        self.model = self.tokenizer = None
        if _ACTIVE_ENCODER is self:
            _ACTIVE_ENCODER = None
        gc.collect()
