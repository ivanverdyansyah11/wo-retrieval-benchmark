"""Two-input Colab exchange contract; local import never imports neural runtimes.

This file is also bundled as runtime.py for the isolated Colab subprocess.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import io
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
import zipfile

import numpy as np

SCHEMA = "wo_colab_two_embeddings_v1"
IDS = ["WO-DOC-024-C003", "WO-DOC-027-C009"]
DEPENDENCIES = {"torch": "2.12.1+cu126", "FlagEmbedding": "1.4.2", "transformers": "4.57.6",
    "tokenizers": "0.22.2", "sentence-transformers": "5.2.0", "peft": "0.18.1", "datasets": "5.0.1",
    "accelerate": "1.15.0", "sentencepiece": "0.2.2", "protobuf": "7.36.2", "numpy": "2.5.3",
    "psutil": "7.2.2", "safetensors": "0.8.0", "huggingface-hub": "0.36.2", "fsspec": "2026.6.0", "ir-datasets": "0.6.3"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf8")


def digest(value):
    return sha256(canonical(value)).hexdigest()


def file_hash(path):
    result = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            result.update(block)
    return result.hexdigest()


def parse_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def read_zip(path, required, limit):
    with zipfile.ZipFile(path) as archive:
        items = archive.infolist()
        if len(items) != len(required) or {i.filename for i in items} != set(required):
            raise ValueError("Missing/duplicate/extra archive entry")
        if any(i.file_size > limit or i.flag_bits & 1 for i in items):
            raise ValueError("Oversized/encrypted exchange artifact")
        return {i.filename: archive.read(i) for i in items}


def write_zip(path, items):
    path = Path(path)
    if path.exists():
        raise FileExistsError("Exchange artifact exists; no overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in items.items():
            archive.writestr(name, data)


def validate_input(package):
    if package.get("schema") != SCHEMA or package.get("package_fingerprint") != digest({k: v for k, v in package.items() if k != "package_fingerprint"}):
        raise ValueError("Input package fingerprint/schema mismatch")
    if (package.get("snapshot_id") != "WO-CORPUS-V2-AI-CORRECTED-PILOT-001"
            or package.get("snapshot_fingerprint") != "78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6"
            or package.get("serialization_version") != "wo_operational_context_dedup_v1"):
        raise ValueError("Snapshot/serialization mismatch")
    cfg = package["inference"]
    expected = {"model_id": "BAAI/bge-m3", "model_revision": "5617a9f61b028005a4858fdac845db406aefb181",
        "device": "cuda:0", "precision": "float16", "batch_size": 1, "max_length": 640, "dimension": 1024,
        "return_dense": True, "return_sparse": False, "return_colbert_vecs": False,
        "pooling_method": "cls", "storage_dtype": "float32", "truncation": False,
        "normalization": "official L2; convert output to float32 and L2-normalize again before score/storage"}
    if cfg != expected or package["dependency_pins"] != DEPENDENCIES:
        raise ValueError("Model/inference/dependency contract mismatch")
    if [r["chunk_id"] for r in package["inputs"]] != IDS:
        raise ValueError("Missing/duplicate/wrong input chunk IDs")
    for row in package["inputs"]:
        text = row["serialized_text"]
        if (not isinstance(text, str) or not text or sha256(text.encode("utf8")).hexdigest() != row["input_sha256"]
                or row["document_id"] != row["chunk_id"].rsplit("-C", 1)[0]
                or type(row["actual_tokens"]) is not int or not 0 < row["actual_tokens"] <= 640):
            raise ValueError("Input hash/document/token mismatch")
        if any(row.get(k) != package[k] for k in ("snapshot_id", "snapshot_fingerprint", "serialization_version")):
            raise ValueError("Per-input snapshot/serializer binding mismatch")
    return package


def read_input(path):
    files = read_zip(path, {"inputs.json", "runtime.py"}, 2*1024**2)
    package = validate_input(parse_json(files["inputs.json"]))
    if sha256(files["runtime.py"]).hexdigest() != package["runtime_sha256"]:
        raise ValueError("Portable runtime checksum mismatch")
    return package


def validate_vector(vector):
    if (not isinstance(vector, np.ndarray) or vector.dtype != np.float32 or vector.shape != (1, 1024)
            or not np.isfinite(vector).all() or not np.allclose(np.linalg.norm(vector, axis=1), 1, rtol=0, atol=1e-5)):
        raise ValueError("Invalid vector dimension/dtype/finite/L2 values")
    return vector


def write_output(path, package, vectors, environment, timings):
    validate_input(package)
    if set(vectors) != set(IDS):
        raise ValueError("Missing/extra output vectors")
    artifacts, rows = {}, []
    for row in package["inputs"]:
        vector = validate_vector(vectors[row["chunk_id"]])
        stream = io.BytesIO()
        np.save(stream, vector, allow_pickle=False)
        name = row["chunk_id"] + ".npy"
        artifacts[name] = stream.getvalue()
        rows.append({k: row[k] for k in ("chunk_id", "document_id", "input_sha256", "actual_tokens")})
    manifest = {"schema": SCHEMA, "completion_status": "COMPLETE", "input_package_fingerprint": package["package_fingerprint"],
        "snapshot_id": package["snapshot_id"], "snapshot_fingerprint": package["snapshot_fingerprint"],
        "serialization_version": package["serialization_version"], "inference": package["inference"],
        "model_file_hashes": package["model_file_hashes"], "official_inference_file_hashes": package["official_inference_file_hashes"],
        "runtime_sha256": package["runtime_sha256"], "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": rows, "encoding_environment": environment, "timings": timings,
        "artifact_sha256": {k: sha256(v).hexdigest() for k, v in artifacts.items()},
        "numerical_bitwise_equivalence_with_local_gpu": "NOT TESTED"}
    manifest["manifest_fingerprint"] = digest(manifest)
    write_zip(path, {"manifest.json": canonical(manifest), **artifacts})
    return manifest


def read_output(path, package, allow_synthetic=False):
    validate_input(package)
    files = read_zip(path, {"manifest.json", *(i + ".npy" for i in IDS)}, 256*1024)
    manifest = parse_json(files["manifest.json"])
    if (manifest.get("schema") != SCHEMA or manifest.get("completion_status") != "COMPLETE"
            or manifest.get("manifest_fingerprint") != digest({k: v for k, v in manifest.items() if k != "manifest_fingerprint"})):
        raise ValueError("Incomplete/corrupted output manifest")
    for key in ("snapshot_id", "snapshot_fingerprint", "serialization_version", "inference", "model_file_hashes", "official_inference_file_hashes", "runtime_sha256"):
        if manifest.get(key) != package[key]:
            raise ValueError("Output contract mismatch: " + key)
    if manifest.get("input_package_fingerprint") != package["package_fingerprint"]:
        raise ValueError("Stale input package")
    expected_rows = [{k: r[k] for k in ("chunk_id", "document_id", "input_sha256", "actual_tokens")} for r in package["inputs"]]
    if manifest.get("rows") != expected_rows:
        raise ValueError("Missing/duplicate/incorrect output input mapping")
    env = manifest["encoding_environment"]
    if env.get("synthetic_fixture") is not False and not allow_synthetic:
        raise ValueError("Synthetic or unknown outputs cannot complete a real index")
    if (env.get("dependency_versions") != DEPENDENCIES or env.get("platform") != "Linux"
            or not env.get("gpu_name") or not env.get("cuda_runtime") or env.get("precision") != "float16"):
        raise ValueError("Missing/mismatched cloud environment provenance")
    date = datetime.fromisoformat(manifest["created_at_utc"])
    if date.utcoffset() is None or date.utcoffset().total_seconds() != 0:
        raise ValueError("Output timestamp must be UTC")
    names = {i + ".npy" for i in IDS}
    if set(manifest["artifact_sha256"]) != names:
        raise ValueError("Missing vector checksum")
    vectors = {}
    for name in names:
        if sha256(files[name]).hexdigest() != manifest["artifact_sha256"][name]:
            raise ValueError("Vector artifact checksum mismatch")
        vectors[name[:-4]] = validate_vector(np.load(io.BytesIO(files[name]), allow_pickle=False))
    return vectors, manifest


def export_inputs(root, output):
    from wo_retrieval.versioned_dense import prepare_v2
    context = prepare_v2(root)
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(str(context["local"] / "tokenizer.json"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    inputs = []
    for row in context["rows"]:
        if row["chunk_id"] not in IDS:
            continue
        length = len(tokenizer.encode(row["text"], add_special_tokens=True).ids)
        expected = next(m["token_length"] for m in context["mapping"] if m["chunk_id"] == row["chunk_id"])
        if length != expected:
            raise ValueError("Actual tokenizer differs from verified V2 mapping")
        inputs.append({"chunk_id": row["chunk_id"], "document_id": row["document_id"], "serialized_text": row["text"],
                       "input_sha256": row["text_sha256"], "actual_tokens": length,
                       "snapshot_id": context["identity"]["snapshot_id"], "snapshot_fingerprint": context["identity"]["snapshot_fingerprint"],
                       "serialization_version": context["identity"]["serializer_version"]})
    identity = context["identity"]
    cfg = {k: identity[k] for k in ("model_id", "model_revision", "device", "precision", "max_length", "dimension", "normalization", "storage_dtype", "batch_size")}
    cfg.update(return_dense=True, return_sparse=False, return_colbert_vecs=False, pooling_method="cls", truncation=False)
    runtime = Path(__file__).read_bytes()
    package = {"schema": SCHEMA, "snapshot_id": identity["snapshot_id"], "snapshot_fingerprint": identity["snapshot_fingerprint"],
        "serialization_version": identity["serializer_version"], "inference": cfg, "inputs": inputs,
        "dependency_pins": DEPENDENCIES, "model_file_hashes": identity["model_file_hashes"],
        "official_inference_file_hashes": identity["official_inference_file_hashes"], "runtime_sha256": sha256(runtime).hexdigest()}
    package["package_fingerprint"] = digest(package)
    validate_input(package)
    write_zip(output, {"inputs.json": canonical(package), "runtime.py": runtime})
    read_input(output)
    return package


def import_output(root, input_package, cloud_output):
    from wo_retrieval.versioned_dense import prepare_v2, publish, load_components
    context = prepare_v2(root)
    if (Path(root) / context["binding"]["r3_index"]).exists():
        raise FileExistsError("R3 V2 exists; never overwrite")
    package = read_input(input_package)
    vectors, manifest = read_output(cloud_output, package)
    for item in package["inputs"]:
        row = next(r for r in context["rows"] if r["chunk_id"] == item["chunk_id"])
        if (row["text"] != item["serialized_text"] or row["text_sha256"] != item["input_sha256"]
                or row["document_id"] != item["document_id"]):
            raise ValueError("Imported package differs from current exact V2 inputs")
    if (package["model_file_hashes"] != context["identity"]["model_file_hashes"]
            or package["official_inference_file_hashes"] != context["identity"]["official_inference_file_hashes"]
            or package["runtime_sha256"] != file_hash(Path(__file__))):
        raise ValueError("Model/API/runtime provenance differs from local contract")
    records = {}
    for item in package["inputs"]:
        records[item["chunk_id"]] = {**{k: package["inference"][k] for k in
            ("model_id", "model_revision", "precision", "device", "max_length", "normalization", "dimension")},
            "input_sha256": item["input_sha256"], "actual_tokens": item["actual_tokens"], "truncation": False,
            "vector": vectors[item["chunk_id"]], "encoding_environment": manifest["encoding_environment"],
            "exchange_manifest": manifest, "exchange_zip_sha256": file_hash(cloud_output),
            "portable_import_code_sha256": file_hash(Path(__file__)),
            "mixed_hardware": True, "local_dependency_identity_scope": "369 inherited source vectors / local scoring validators; see actual cloud environment for these two rows"}
    def reverify():
        fresh = prepare_v2(root)
        if fresh["identity"] != context["identity"]:
            raise ValueError("Source/snapshot changed before atomic publication")
        read_output(cloud_output, read_input(input_package))
    result = publish(context, records, reverify)
    load_components(root, "v2")
    return result


def run_colab(input_package, output):
    """Manual Colab invocation only; no local CLI dispatch reaches this implicitly."""
    if platform.system() != "Linux" or sys.version_info[:2] != (3, 12):
        raise RuntimeError("This cloud runner requires Linux/Python3.12; no alternative inference environment")
    package = read_input(input_package)
    if package["runtime_sha256"] != file_hash(Path(__file__)):
        raise ValueError("Uploaded runtime differs from input contract")
    from importlib.metadata import version, distributions
    for name, expected in DEPENDENCIES.items():
        if version(name) != expected:
            raise RuntimeError("Dependency version mismatch: " + name)
    import torch
    if not torch.cuda.is_available() or torch.version.cuda != "12.6":
        raise RuntimeError("Pinned CUDA12.6 GPU runtime unavailable; no CPU fallback")
    from huggingface_hub import HfApi, snapshot_download
    revision = package["inference"]["model_revision"]
    if HfApi().model_info(package["inference"]["model_id"], revision=revision).sha != revision:
        raise RuntimeError("Official repository revision mismatch")
    local = Path(snapshot_download(repo_id=package["inference"]["model_id"], revision=revision,
        allow_patterns=list(package["model_file_hashes"]), cache_dir="/content/wo_bge_m3/hf_cache"))
    if local.name != revision:
        raise RuntimeError("Checkpoint path is not the pinned revision")
    for name, expected in package["model_file_hashes"].items():
        if file_hash(local / name) != expected:
            raise RuntimeError("Official checkpoint/tokenizer checksum mismatch: " + name)
    import os
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    from transformers import AutoTokenizer
    from FlagEmbedding import BGEM3FlagModel
    import FlagEmbedding
    library_root = Path(FlagEmbedding.__file__).parent
    for name, expected in package["official_inference_file_hashes"].items():
        if file_hash(library_root / name) != expected:
            raise RuntimeError("Official inference implementation mismatch: " + name)
    tokenizer = AutoTokenizer.from_pretrained(str(local), use_fast=True, local_files_only=True, trust_remote_code=False)
    tokens = []
    for row in package["inputs"]:
        item = tokenizer(row["serialized_text"], add_special_tokens=True, truncation=False, padding=False)
        if len(item["input_ids"]) != row["actual_tokens"] or len(item["input_ids"]) > 640:
            raise RuntimeError("Actual tokenizer count mismatch/truncation risk")
        tokens.append(item)
    if Path(output).exists():
        raise FileExistsError("Output already exists; no automatic rerun")
    torch.set_num_threads(4)
    torch.cuda.reset_peak_memory_stats()
    started = perf_counter()
    model = BGEM3FlagModel(str(local), use_fp16=True, devices=["cuda:0"], batch_size=1,
        query_max_length=640, passage_max_length=640, normalize_embeddings=True, pooling_method="cls",
        return_dense=True, return_sparse=False, return_colbert_vecs=False, trust_remote_code=False)
    model.model.eval().to("cuda:0")
    torch.cuda.synchronize()
    loading = perf_counter() - started
    if next(model.model.parameters()).dtype != torch.float16:
        raise RuntimeError("Expected actual FP16 model weights")
    import psutil
    peak_rss, times, vectors = psutil.Process().memory_info().rss, {}, {}
    for row, item in zip(package["inputs"], tokens, strict=True):
        features = tokenizer.pad([item], padding=True, return_tensors="pt").to("cuda:0")
        torch.cuda.synchronize()
        before = perf_counter()
        with torch.inference_mode():
            out = model.model(features, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        torch.cuda.synchronize()
        times[row["chunk_id"]] = perf_counter() - before
        if set(out) != {"dense_vecs"}:
            raise RuntimeError("Unexpected sparse/ColBERT output")
        vector = out["dense_vecs"].float().cpu().numpy()
        if vector.shape != (1, 1024) or not np.isfinite(vector).all():
            raise RuntimeError("Invalid dense output")
        norms = np.linalg.norm(vector, axis=1, keepdims=True)
        if not np.isfinite(norms).all() or np.any(norms <= 0):
            raise RuntimeError("Invalid vector norm")
        vectors[row["chunk_id"]] = validate_vector(vector / norms)
        peak_rss = max(peak_rss, psutil.Process().memory_info().rss)
    environment = {"synthetic_fixture": False, "platform": "Linux", "python": platform.python_version(),
        "dependency_versions": {n: version(n) for n in DEPENDENCIES}, "full_environment_lock": sorted(d.metadata["Name"] + "==" + d.version for d in distributions()),
        "gpu_name": torch.cuda.get_device_name(0), "gpu_capability": list(torch.cuda.get_device_capability(0)),
        "cuda_runtime": torch.version.cuda, "precision": "float16", "peak_gpu_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_gpu_reserved_bytes": torch.cuda.max_memory_reserved(), "sampled_peak_rss_bytes": peak_rss,
        "ram_measurement_limit": "Boundary samples, not continuous process peak", "torch_architectures": torch.cuda.get_arch_list()}
    return write_output(output, package, vectors, environment, {"model_loading_seconds": loading, "embedding_seconds": times, "retrieval_benchmark": False})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("export", "import", "colab"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "export":
        result = export_inputs(args.root, args.output)
    elif args.command == "import":
        if args.input is None:
            parser.error("--input requires the original input package; --output is the returned Colab zip")
        result = import_output(args.root, args.input, args.output)
    else:
        if args.input is None:
            parser.error("--input required")
        result = run_colab(args.input, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
