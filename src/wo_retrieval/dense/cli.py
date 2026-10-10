"""R3 local-only token audit, build, retrieval and metadata inspection."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback

from wo_retrieval.retrieval.lexical import read_protocol, verify_snapshot
from wo_retrieval.retrieval.text import normalize
from .index import (
    DenseRetriever, atomic_json, cache_identity, cache_paths, embed_sequential,
    inspect_inputs, load_vectors, token_audit,
)
from .model import BGEEncoder, model_files, offline_environment
from .resources import Monitor, gate, gpu_resource, resource, unsafe


def run(root: Path, command: str, query: str | None = None, top_k: int = 5,
        chunk_id: str | None = None, resume: bool = False, approved_low_memory: bool = False):
    root = root.resolve()
    offline_environment()
    config = read_protocol(root)
    if type(top_k) is not int or top_k <= 0:
        raise ValueError("top_k must be a positive integer")
    if command == "retrieve" and not normalize(query):
        return []
    encoder = None
    started = perf_counter()
    report = {"method_id": "R3", "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "command": command, "loading": "NOT RUN", "indexing": "NOT RUN", "smoke": "NOT RUN",
              "preflight": resource(), "gpu_preflight": gpu_resource(), "approved_low_memory": approved_low_memory,
              "cpu_fallback": "NOT RUN; separate approval required", "effectiveness_evaluation": "NOT RUN"}
    # Separate run evidence from COMPLETE cache; diagnostics never mutate vectors.
    run_dir = Path(config["R3"]["cache"]["root"]) / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir.mkdir(parents=True)
    report_path = run_dir / "run.json"
    monitor = Monitor(config["hardware"], run_dir)
    try:
        with monitor:
            rows, statistics = inspect_inputs(root, config)
            local_path, hashes = model_files(root, config)
            encoder = BGEEncoder(local_path, config)
            mapping, counts = token_audit(rows, encoder)
            report.update({"serialization_statistics": statistics, "tokenizer_audit": counts,
                           "local_model_path": str(local_path), "model_hashes_verified": len(hashes)})
            identity = cache_identity(root, config, statistics, hashes, mapping)
            directory, partial = cache_paths(config, identity)
            report.update({"cache_identity": identity, "cache_path": str(directory), "partial_cache_path": str(partial)})
            atomic_json(report_path, report)
            if command == "tokenize":
                report["tokenizer_rows"] = mapping
                report["status"] = "TOKENIZER_PASS_MODEL_NOT_LOADED"
                return report
            if command in ("audit", "inspect"):
                vectors, manifest = load_vectors(directory, identity, mapping)
                report.update({"status": "PASS", "index": manifest})
                if command == "inspect":
                    found = next((row for row in rows if row["chunk_id"] == chunk_id), None)
                    if found is None:
                        raise ValueError("Unknown frozen chunk ID")
                    return found
                return report
            if directory.exists():
                vectors, manifest = load_vectors(directory, identity, mapping)
                report["indexing"] = "REUSED_VERIFIED_COMPLETE"
                if resume:
                    raise ValueError("Index already complete; resume is unnecessary")
                if command == "build":
                    report.update({"status": "PASS", "index": manifest})
                    return report
            elif command == "retrieve":
                raise ValueError("No COMPLETE dense index; build first")
            if query is not None:
                encoder.tokens(query)
            # Gate after tokenizer/imports, immediately before neural checkpoint loading.
            report["pre_model_loading"] = resource()
            report["gpu_pre_model_loading"] = gpu_resource()
            gate(report["pre_model_loading"], report["gpu_pre_model_loading"], config["hardware"], approved_low_memory)
            if not directory.exists():
                from .index import checkpoint_rows
                checkpoint_rows(partial, identity, mapping, resume)
            report["loading"] = "RUNNING"
            atomic_json(report_path, report)
            encoder.load(Path(config["R3"]["cache"]["root"]) / "gpu-inference.lock")
            report["loading"] = "PASS"
            report["resources_after_loading"] = resource()
            if unsafe(report["resources_after_loading"], config["hardware"]):
                raise RuntimeError("Critical memory immediately after loading; no inference")
            report["model_metrics_after_loading"] = encoder.metrics()
            atomic_json(report_path, report)
            if not directory.exists():
                report["indexing"] = "RUNNING"
                atomic_json(report_path, report)
                manifest = embed_sequential(rows, mapping, identity, encoder, directory, partial,
                                            resume=True, verify_before_publish=lambda: verify_snapshot(root, config))
                vectors, manifest = load_vectors(directory, identity, mapping)
                report["indexing"] = "PASS"
            report["index"] = manifest
            report["index_build_seconds_excluding_model_loading"] = perf_counter() - started - encoder.loading_seconds
            report["model_metrics_after_indexing"] = encoder.metrics()
            retriever = DenseRetriever(rows, vectors, encoder, config["snapshot"]["id"])
            if command == "smoke":
                queries = [json.loads(line) for line in (root / "data/benchmark/development_queries_draft.jsonl").read_text(encoding="utf-8").splitlines()]
                selected = [next(query for query in queries if query["style"] == style) for style in config["queries"]["styles"]]
                report["sanity_selection"] = "first query in existing file order per style; no ranking-based selection"
                report["smoke_results"] = []
                for item in selected:
                    before = perf_counter()
                    results = retriever.retrieve(item["text"], 5)
                    if len(results) != 5:
                        raise RuntimeError("Expected five sanity results")
                    result_rows = []
                    for result in results:
                        source = next(row for row in rows if row["chunk_id"] == result.chunk_id)
                        if source["document_id"] != result.document_id:
                            raise ValueError("Retrieval source mapping mismatch")
                        result_rows.append({**asdict(result), "source_file": source["source_file"], "source_locator": source["source_locator"]})
                    report["smoke_results"].append({"query_id": item["query_id"], "text": item["text"],
                                                    "query_status": item["validation_status"], "seconds": perf_counter() - before,
                                                    "actual_tokens": len(encoder.tokens(item["text"])["input_ids"]), "results": result_rows})
                report["smoke"] = "PASS"
            elif command == "retrieve":
                report["results"] = [asdict(result) for result in retriever.retrieve(query, top_k)]
            report["model_metrics_final"] = encoder.metrics()
            report["status"] = "PASS"
            verify_snapshot(root, config)
            return report.get("results", report)
    except BaseException as error:
        report["status"] = "FAIL"
        report["error"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
        for key in ("loading", "indexing", "smoke"):
            if report[key] == "RUNNING":
                report[key] = "FAIL"
        raise
    finally:
        if encoder is not None:
            encoder.close()
        report["resource_monitor"] = monitor.summary
        report["resource_after_cleanup"] = resource()
        report["total_wall_seconds_including_model_loading"] = perf_counter() - started
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        atomic_json(report_path, report)
        print(json.dumps({"event": "run_evidence", "path": str(report_path), "status": report.get("status", "INCOMPLETE")}), file=sys.stderr, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("tokenize", "build", "smoke", "retrieve", "audit", "inspect"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chunk-id")
    parser.add_argument("--resume", action="store_true", help="Only after explicit approval and resource repair; never automatic")
    parser.add_argument("--approved-low-memory", action="store_true", help="Use only with recorded human approval; gate becomes 5 GiB rather than 6 GiB")
    args = parser.parse_args()
    if args.command == "retrieve" and args.query is None:
        parser.error("--query is required")
    if args.command == "inspect" and not args.chunk_id:
        parser.error("--chunk-id is required")
    if args.resume and args.command not in ("build", "smoke"):
        parser.error("--resume requires build or smoke")
    try:
        result = run(args.root, args.command, args.query, args.top_k, args.chunk_id, args.resume, args.approved_low_memory)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as error:
        parser.exit(1, f"Dense retrieval stopped: {error}\n")


if __name__ == "__main__":
    main()
