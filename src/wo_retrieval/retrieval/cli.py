"""Build, retrieve, inspect and audit lexical indexes without corpus writes."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from .lexical import audit, build, load


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "retrieve", "inspect", "audit"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--method", choices=("R1", "R2"))
    parser.add_argument("--index-name", help="Optional new directory name under experiments/indexes")
    parser.add_argument("--query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chunk-id")
    args = parser.parse_args()
    if args.command != "audit" and not args.method:
        parser.error("--method is required")
    if args.command == "retrieve" and args.query is None:
        parser.error("--query is required")
    if args.command == "inspect" and not args.chunk_id:
        parser.error("--chunk-id is required")
    if args.command == "audit" and args.index_name:
        parser.error("audit compares default R1 and R2 indexes")
    try:
        if args.command == "build":
            result = build(args.root, args.method, args.index_name)
        elif args.command == "audit":
            result = audit(args.root)
        else:
            retriever = load(args.root, args.method, args.index_name)
            if args.command == "retrieve":
                result = [asdict(item) for item in retriever.retrieve(args.query, args.top_k)]
            else:
                result = next((row for row in retriever.rows if row["chunk_id"] == args.chunk_id), None)
                if result is None:
                    raise ValueError("Unknown frozen chunk ID")
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"Retrieval failed: {exc}\n")


if __name__ == "__main__":
    main()
