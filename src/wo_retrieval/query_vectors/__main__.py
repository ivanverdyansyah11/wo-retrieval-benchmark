"""Technical cache scoring and separately authorized, resource-gated encoding."""

import argparse
from dataclasses import asdict
from pathlib import Path
from time import perf_counter
import traceback

from wo_retrieval.dense.index import atomic_json
from wo_retrieval.retrieval.lexical import verify_snapshot
from wo_retrieval.retrieval.text import normalize
from .artifacts import contract, publish, text_hash
from .offline import load_components, retrievers


def encode(root, components, output, query_id, query, approved_low_memory=False, approval_note=None):
    # Only this explicit command may import ML runtimes; offline scoring cannot reach it.
    from wo_retrieval.dense.model import BGEEncoder, offline_environment
    from wo_retrieval.dense.resources import Monitor, gate, gpu_resource, resource, unsafe
    if not approval_note or not approval_note.strip():
        raise ValueError("Encoding requires a recorded explicit approval note")
    if not isinstance(query_id, str) or not query_id.strip() or not normalize(query):
        raise ValueError("Nonempty query ID and query required")
    output = Path(output).resolve()
    if not output.is_relative_to(Path("D:/ModelCache/wo-retrieval-benchmark/query_vectors").resolve()):
        raise ValueError("Query artifacts must remain in the approved D: query cache")
    if output.exists():
        raise FileExistsError("Existing query artifact; no overwrite/retry")
    _, _, manifest, config, local = components
    policy = {**config["hardware"], "stop_available_ram_mib": 2048, "stop_sustained_seconds": 0}
    evidence = {"completion_status": "INCOMPLETE", "approval_note": approval_note,
                "approved_low_memory": approved_low_memory, "loading_gate_gib": 5 if approved_low_memory else 6,
                "effective_resource_policy": policy, "query_id": query_id, "query_text_sha256": text_hash(query),
                "technical_only": True, "end_to_end_gpu_smoke_status": "end_to_end_pending"}
    evidence_path = output.with_name(output.name + ".run.json")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(evidence_path, evidence)
    encoder = None
    offline_environment()
    try:
        evidence["initial_resource"], evidence["initial_gpu"] = resource(), gpu_resource()
        gate(evidence["initial_resource"], evidence["initial_gpu"], policy, approved_low_memory)
        with Monitor(policy, output.with_name(output.name + ".resource")) as monitor:
            encoder = BGEEncoder(local, config)
            tokens = len(encoder.tokens(query)["input_ids"])
            # Import preparation must precede the last gate, as shown by the 8C.1 diagnostic.
            import torch
            from FlagEmbedding import BGEM3FlagModel
            evidence["before_weights"], evidence["before_weights_gpu"] = resource(), gpu_resource()
            gate(evidence["before_weights"], evidence["before_weights_gpu"], policy, approved_low_memory)
            atomic_json(evidence_path, evidence)
            encoder.load(Path(config["R3"]["cache"]["root"]) / "GPU_MODEL.lock")
            if unsafe(resource(), policy):
                raise RuntimeError("Unsafe resources after loading; STOP without encoding")
            started = perf_counter()
            vector = encoder.encode(normalize(query))
            encoding_seconds = perf_counter() - started
            if unsafe(resource(), policy):
                raise RuntimeError("Unsafe resources after encoding; do not publish")
            verify_snapshot(Path(root), config)
            encoding = {key: config["R3"][key] for key in ("device", "precision", "batch_size", "max_length")}
            encoding.update(actual_tokens_including_special=tokens, truncation=False,
                            query_encoding_seconds=encoding_seconds, model_metrics=encoder.metrics())
            publish(output, contract(manifest), query_id, query, vector, encoding)
            evidence.update(completion_status="COMPLETE", encoding=encoding)
        evidence["resource_summary"] = monitor.summary
    except BaseException:
        evidence["error"] = traceback.format_exc()
        raise
    finally:
        if encoder is not None:
            encoder.close()
        atomic_json(evidence_path, evidence)
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["score", "encode"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--corpus-index", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--query-id", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--method", choices=["R3", "R4"], default="R4")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--approved-low-memory", action="store_true")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    if args.command == "score" and (args.approved_low_memory or args.approval_note):
        parser.error("Memory approval flags apply only to the explicit encoder command")
    components = load_components(args.root, args.corpus_index)
    if args.command == "encode":
        result = encode(args.root, components, args.artifact, args.query_id, args.query,
                        args.approved_low_memory, args.approval_note)
    else:
        dense, hybrid = retrievers(components, args.artifact, args.query_id, args.query)
        started = perf_counter()
        if args.method == "R3":
            results, diagnostics = dense.retrieve(args.query, args.top_k), []
        else:
            results, diagnostics, _ = hybrid.retrieve_with_diagnostics(args.query, args.top_k)
        elapsed = perf_counter() - started
        result = {"method_id": args.method, "mode": "technical_offline_cached_query",
                  "query_id": args.query_id, "query_text_sha256": text_hash(args.query),
                  "results": [asdict(row) for row in results], "contributions": diagnostics,
                  "offline_scoring_seconds": elapsed, "live_end_to_end_latency": "NOT MEASURED",
                  "snapshot_fingerprint": components[3]["snapshot"]["aggregate_fingerprint"]}
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
