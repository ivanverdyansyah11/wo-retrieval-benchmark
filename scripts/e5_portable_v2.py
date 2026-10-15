"""E5 CPU v2: no historical runtime imports; bounded smoke, separate receipts."""
import argparse
from datetime import datetime, timezone
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from wo_retrieval import e5_portable_v2 as e

BUNDLE = ROOT / "experiments/portable/e5_cpu_smoke_v2"
OUTPUT = ROOT / "experiments/embedding_portability/v2"


def limit(value):
    count = int(value)
    if not 1 <= count <= 5:
        raise argparse.ArgumentTypeError("Only 1 to 5 chunks allowed")
    return count


def sample_rows(path, count):
    if type(count) is not int or not 1 <= count <= 5:
        raise ValueError("Only 1 to 5 sample chunks allowed")
    bound = e.read_json(BUNDLE / "corpus-binding.json")
    if e.file_hash(path) != bound["sha256"]:
        raise ValueError("Frozen serialized input SHA256 mismatch")
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf8").splitlines()]
    ids = [r["chunk_id"] for r in rows]
    if len(rows) != bound["rows"] or ids != sorted(set(ids)) or any(not r["text"].strip() for r in rows):
        raise ValueError("Frozen serialized input mapping mismatch")
    return rows[:count]


def run(args, receipt):
    e.cpu_environment()
    receipt["resource"] = e.resource_gate(loading=True)
    e.process_safety()
    expected = e.binding(BUNDLE)
    receipt["snapshot_binding"] = expected
    rejected = []
    receipt["rejected_caches"] = rejected
    # Inspect can validate resources/snapshot on a legacy machine without claiming
    # CPU-only dependencies are available. Inference stages always require them.
    if args.stage == "inspect":
        path = e.select_snapshot(ROOT, expected, args.snapshot, rejected)
        receipt["snapshot_verified"] = True
        try:
            receipt["dependencies"] = e.dependency_check(BUNDLE)
            receipt["cpu_environment_ready"] = True
        except e.Blocked as error:
            receipt["cpu_environment_ready"] = False
            receipt["cpu_environment_blocker"] = str(error)
        receipt["inference_tested"] = False
        return
    receipt["dependencies"] = e.dependency_check(BUNDLE)
    check = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    receipt["pip_check"] = {"exit_code": check.returncode, "stdout": check.stdout, "stderr": check.stderr}
    if check.returncode:
        raise e.Blocked("pip check failed")
    path = e.download(ROOT, expected) if args.stage == "download" else e.select_snapshot(ROOT, expected, args.snapshot, rejected)
    receipt["snapshot_verified"] = True
    receipt["full_environment_lock"] = sorted(d.metadata["Name"] + "==" + d.version for d in metadata.distributions())
    receipt["inference_code_sha256"] = e.file_hash(Path(e.__file__))
    if args.stage in ("download", "preflight"):
        return
    rows = sample_rows(args.chunks_file, args.limit) if args.stage == "chunks" else []
    # Scope/sample mapping is recorded BEFORE any forward, including on a STOP.
    receipt["sample_chunk_ids"] = [r["chunk_id"] for r in rows]
    receipt["scope"] = "E5 v2 smoke; never a full corpus/evaluator index"
    encoder = None
    try:
        with e.inference_session(ROOT):
            encoder = e.Encoder(path, expected, BUNDLE)
            encoder.load()
            import numpy as np
            vector, info = encoder.encode("Siapa PIC vendor?", "query")
            receipt["query_embeddings_computed"] += 1
            np.save(args.output / "query.npy", vector, allow_pickle=False)
            receipt["query"] = {"shape": list(vector.shape), "dtype": str(vector.dtype),
                                "norm": float(np.linalg.norm(vector[0])), "token_info": info}
            passages = []
            for row in rows:
                value, info = encoder.encode(row["text"], "passage")
                passages.append(value)
                receipt["corpus_embeddings_computed"] += 1
                receipt.setdefault("passages", []).append({"chunk_id": row["chunk_id"], **info})
            if passages:
                values = np.concatenate(passages)
                np.save(args.output / "passages.npy", values, allow_pickle=False)
                scores = values @ vector[0]
                order = sorted(range(len(rows)), key=lambda i: (-float(scores[i]), rows[i]["chunk_id"]))
                receipt["dense_ranking"] = [{"chunk_id": rows[i]["chunk_id"], "score": float(scores[i])} for i in order]
                receipt["passage_shape"] = list(values.shape)
            receipt["devices"] = sorted({p.device.type for p in encoder.model.parameters()})
            receipt["dtypes"] = sorted({str(p.dtype) for p in encoder.model.parameters()})
    finally:
        if encoder is not None:
            receipt["memory_samples"] = encoder.samples
            encoder.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("inspect", "download", "preflight", "short", "chunks"))
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--limit", type=limit, default=1)
    parser.add_argument("--chunks-file", type=Path, default=ROOT / e.read_json(BUNDLE / "corpus-binding.json")["path"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output == OUTPUT or not args.output.is_relative_to(OUTPUT):
        parser.error("Use a new child directory of " + str(OUTPUT))
    args.output.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": "wo_e5_portable_smoke_v2", "stage": args.stage, "status": "BLOCKED",
        "utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(), "python": sys.version,
        "synthetic_fixture": False, "query_embeddings_computed": 0, "corpus_embeddings_computed": 0,
        "model_id": e.MODEL, "revision": e.REVISION, "max_length": e.MAX_LENGTH, "batch_size": 1,
        "dimension": e.DIMENSION, "pooling": "attention_mask_mean", "normalization": "L2",
        "precision": "float32", "device": "cpu", "namespace": "embedding_portability/v2"}
    try:
        run(args, receipt)
        receipt["status"] = "PASS"
    except Exception as error:
        receipt.update(error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
        if not isinstance(error, (e.Blocked, ImportError, FileNotFoundError)):
            receipt["status"] = "FAIL"
    finally:
        receipt["artifact_sha256"] = {p.name: e.file_hash(p) for p in args.output.glob("*.npy")}
        # Exclusive write; a receipt from an earlier run is never replaced.
        with (args.output / "receipt.json").open("x", encoding="utf8") as stream:
            json.dump(receipt, stream, indent=2, allow_nan=False)
            stream.write("\n")
    print(json.dumps({k: receipt[k] for k in ("status", "stage", "query_embeddings_computed", "corpus_embeddings_computed")}))
    raise SystemExit(receipt["status"] != "PASS")


if __name__ == "__main__":
    main()
