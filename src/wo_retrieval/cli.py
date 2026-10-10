import argparse
from pathlib import Path

from .pipeline import (audit, build_chunks, ingest, json_text, load_config,
                       read_documents, safe_write, verify_canonical,
                       write_chunks, write_ingestion)


def main():
    parser = argparse.ArgumentParser(description="Read-only source audit, ingestion and pilot chunking")
    parser.add_argument("command", choices=["audit", "ingest", "chunk", "run"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/pilot.toml"))
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        config = load_config(root, root / args.config)
        if args.command == "audit":
            _, report = audit(root, config)
            safe_write(root, root / config["reports_dir"] / "source_audit.json", json_text(report))
            print(json_text({k: v for k, v in report.items() if k != "source_snapshot"}))
            return 1 if report["errors"] else 0
        if args.command in {"ingest", "run"}:
            documents, report, source_audit = ingest(root, config)
            write_ingestion(root, config, documents, report, source_audit)
            print(json_text(report))
        if args.command in {"chunk", "run"}:
            if args.command == "chunk":
                documents = read_documents(root / config["documents_output"])
            verify_canonical(root, config, documents)
            chunks, report = build_chunks(documents, config)
            write_chunks(root, config, documents, chunks, report)
            print(json_text(report))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
