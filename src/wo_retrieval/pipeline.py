import csv
import hashlib
import json
import math
import platform
import statistics
import tomllib
from collections import Counter
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from .ingestion import PARSERS, parse
from .preprocessing.chunking import chunk_document
from .preprocessing.cleaning import clean
from .schemas import Block, Document


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def jsonl_text(values) -> str:
    return "".join(json.dumps(asdict(v), ensure_ascii=False, sort_keys=True) + "\n" for v in values)


def snapshot(source: Path) -> dict:
    return {p.relative_to(source).as_posix(): sha256(p) for p in sorted(source.rglob("*")) if p.is_file()}


def load_config(root: Path, config_path: Path) -> dict:
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if config["pipeline_version"] != "1" or config["corpus_version"] not in {"v1-draft", "v2-ai-corrected"}:
        raise ValueError("Unsupported pipeline/corpus version")
    protected = (root / "data/source_corpus").resolve()
    v2 = config["corpus_version"] == "v2-ai-corrected"
    source = root / ("data/corpus_candidates/v2_ai_corrected/documents" if v2 else "data/source_corpus/documents")
    if (root / config["source_documents"]).resolve() != source.resolve():
        raise ValueError("Retrievable source does not match the corpus version")
    if v2:
        base = "data/versions/v2_ai_corrected"
        expected = {"manifest": f"{base}/source_manifest.json", "inventory": f"{base}/FILE_INVENTORY.csv",
                    "documents_output": f"{base}/processed/documents.jsonl",
                    "chunks_output": f"{base}/chunks/chunks.jsonl", "reports_dir": f"{base}/reports",
                    "source_integrity_output": f"{base}/validation/source_integrity.json"}
        if any(config.get(key) != value for key, value in expected.items()):
            raise ValueError("V2 metadata and outputs must use the separate versioned dataset paths")
    for key in ["documents_output", "chunks_output", "reports_dir"]:
        output = (root / config[key]).resolve()
        if output == protected or protected in output.parents:
            raise ValueError(f"Output inside immutable source corpus is forbidden: {key}")
        if root.resolve() not in output.parents:
            raise ValueError(f"Output must stay inside project: {key}")
    return config


def audit(root: Path, config: dict) -> tuple[list[dict], dict]:
    source = root / config["source_documents"]
    manifest = json.loads((root / config["manifest"]).read_text(encoding="utf-8-sig"))
    files = sorted(p for p in source.rglob("*") if p.is_file())
    errors, notices = [], []
    ids = [m["document_id"] for m in manifest]
    names = [m["filename"] for m in manifest]
    if len(files) != config["expected_documents"]:
        errors.append(f"Expected {config['expected_documents']} documents, found {len(files)}")
    if len(set(ids)) != len(ids) or len(set(names)) != len(names):
        errors.append("Duplicate manifest ID/filename")
    if len(manifest) != len(files) or set(names) != {p.name for p in files}:
        errors.append("Manifest and actual document set differ")
    required = {"document_id", "title", "category", "document_type", "source_type", "dataset_version", "validation_status", "file_sha256", "format"}
    by_name = {m["filename"]: m for m in manifest}
    for p in files:
        if p.is_symlink() or p.resolve().parent != source.resolve():
            errors.append(f"Nested/symlink source is not permitted: {p.name}")
        if p.suffix.lower() not in PARSERS:
            errors.append(f"Unsupported format: {p.name}")
        if not p.stat().st_size:
            errors.append(f"Empty file: {p.name}")
        m = by_name.get(p.name, {})
        if required - m.keys():
            errors.append(f"Required manifest fields missing: {p.name}")
        if m.get("file_sha256") != sha256(p):
            errors.append(f"Manifest SHA-256 mismatch: {p.name}")
        if m.get("format", "").lower() != p.suffix[1:].lower():
            errors.append(f"Manifest format mismatch: {p.name}")
        if m.get("document_id") != p.stem:
            errors.append(f"Manifest ID/filename mismatch: {p.name}")
        status = "ai_corrected_pilot_not_human_validated" if config["corpus_version"] == "v2-ai-corrected" else "pending_practitioner_validation"
        if m.get("validation_status") != status:
            errors.append(f"Unexpected validation status: {p.name}")
    inventory_path = root / config["inventory"]
    with inventory_path.open(encoding="utf-8-sig", newline="") as stream:
        inventory = list(csv.DictReader(stream))
    inventory_docs = []
    inventory_mismatches = []
    for row in inventory:
        relative = Path(row["relative_path"])
        path = inventory_path.parent / relative
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"Invalid inventory path: {relative}")
            continue
        if row["file_role"] == "corpus_document":
            inventory_docs.append(row["filename"])
            if config["corpus_version"] == "v2-ai-corrected":
                if relative.as_posix() != f"documents/{row['filename']}":
                    errors.append(f"Invalid V2 inventory document path: {relative}")
                    continue
                path = source / row["filename"]
        if not path.exists() and relative.as_posix() == "README.md":
            path = root / "README.md"
            notices.append("Inventory README.md is located at repository root; original packaging path differs")
            if path.exists() and sha256(path) != row["sha256"]:
                notices.append("Root README.md differs from original packaging hash after project documentation was appended; immutable corpus unaffected")
            continue
        if not path.is_file() or sha256(path) != row["sha256"] or path.stat().st_size != int(row["file_size_bytes"]):
            inventory_mismatches.append(row["relative_path"])
    if len(inventory_docs) != len(set(inventory_docs)) or set(inventory_docs) != set(names):
        errors.append("Inventory corpus_document set differs from manifest")
    if inventory_mismatches:
        errors.append(f"Inventory integrity mismatch: {inventory_mismatches}")
    report = {"source_documents": len(files), "manifest_records": len(manifest),
              "inventory_records": len(inventory), "formats": dict(sorted(Counter(p.suffix[1:].upper() for p in files).items())),
              "errors": errors, "notices": notices, "source_snapshot": snapshot(source.parent)}
    return manifest, report


def environment(root: Path, config: dict) -> dict:
    code_files = sorted((root / "src/wo_retrieval").rglob("*.py"))
    code_hash = hashlib.sha256("".join(f"{p.relative_to(root).as_posix()}:{sha256(p)}\n" for p in code_files).encode()).hexdigest()
    return {"python": platform.python_version(), "dependencies": {name: version(name) for name in ["python-docx", "pypdf", "openpyxl", "et-xmlfile", "lxml", "typing_extensions"]},
            "pipeline_version": config["pipeline_version"], "config_sha256": hashlib.sha256(json_text(config).encode()).hexdigest(),
            "pipeline_code_sha256": code_hash}


def ingest(root: Path, config: dict):
    manifest, audit_report = audit(root, config)
    if audit_report["errors"]:
        raise ValueError("Source audit failed: " + "; ".join(audit_report["errors"]))
    documents, failures, warnings = [], [], []
    for record in sorted(manifest, key=lambda m: m["document_id"]):
        path = root / config["source_documents"] / record["filename"]
        try:
            result = parse(path)
            warnings.extend({"document_id": record["document_id"], "message": w} for w in result.warnings)
            document = clean(Document(
                record["document_id"], record["title"], record["category"], record["document_type"],
                path.relative_to(root).as_posix(), record["source_type"], record["dataset_version"],
                config["corpus_version"], record["validation_status"],
                {**record, **result.metadata, "parser_format": path.suffix[1:].upper(), "parsing_warnings": result.warnings}, result.content_blocks,
            ))
            if not any(b.retrievable and b.kind not in {"title", "heading", "table_header"} and b.text for b in document.content_blocks):
                raise ValueError("No operational content after cleaning")
            documents.append(document)
        except Exception as exc:
            failures.append({"document_id": record["document_id"], "source_file": path.relative_to(root).as_posix(),
                             "error_type": type(exc).__name__, "message": str(exc)})
    after = snapshot((root / config["source_documents"]).parent)
    if after != audit_report["source_snapshot"]:
        raise RuntimeError("Source corpus changed during ingestion; refusing output publication")
    report = {"source_documents": audit_report["source_documents"], "successfully_parsed": len(documents),
              "failed_documents": len(failures), "canonical_documents": len(documents),
              "failures": failures, "parsing_warnings": warnings, "number_of_parsing_warnings": len(warnings),
              "formats": audit_report["formats"], "audit_notices": audit_report["notices"],
              "source_unchanged": True, "environment": environment(root, config),
              "canonical_blocks": sum(len(d.content_blocks) for d in documents),
              "excluded_administrative_blocks": sum(len(d.metadata["administrative_blocks"]) for d in documents),
              "formula_cells_read_from_cache": sum(d.metadata.get("formula_cells", 0) for d in documents)}
    report["xlsx_sheets"] = [
        {"document_id": d.document_id, "sheet": sheet,
         "table_headers": [b.source_locator["header_row"] for b in d.content_blocks
                           if b.kind == "table_header" and b.source_locator.get("sheet") == sheet],
         "structured_rows": sum(b.kind == "table_row" and b.source_locator.get("sheet") == sheet for b in d.content_blocks),
         "retrievable_rows": sum(b.kind == "table_row" and b.retrievable and b.source_locator.get("sheet") == sheet for b in d.content_blocks)}
        for d in documents if d.metadata["format"] == "XLSX"
        for sheet in dict.fromkeys(b.source_locator["sheet"] for b in d.content_blocks)
    ]
    return documents, report, audit_report


def read_documents(path: Path) -> list[Document]:
    documents = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        value["content_blocks"] = [Block(**b) for b in value["content_blocks"]]
        documents.append(Document(**value))
    return documents


def verify_canonical(root: Path, config: dict, documents: list[Document]) -> None:
    manifest, source_audit = audit(root, config)
    if source_audit["errors"]:
        raise ValueError("Source audit failed: " + "; ".join(source_audit["errors"]))
    expected = {m["document_id"]: m for m in manifest}
    if len(documents) != len(expected) or {d.document_id for d in documents} != set(expected):
        raise ValueError("Canonical document set differs from audited source")
    for d in documents:
        m = expected[d.document_id]
        if (d.source_file != f"{config['source_documents']}/{m['filename']}"
                or d.metadata["file_sha256"] != m["file_sha256"]
                or d.corpus_version != config["corpus_version"]
                or d.validation_status != m["validation_status"]):
            raise ValueError(f"Stale/misaligned canonical document: {d.document_id}")


def build_chunks(documents: list[Document], config: dict):
    chunks = [c for d in documents for c in chunk_document(d, config["chunking"])]
    counts = Counter(c.document_id for c in chunks)
    per_doc = [counts[d.document_id] for d in documents]
    tokens = sorted(c.token_count for c in chunks)
    hashes = Counter(c.content_hash for c in chunks)
    report = {
        "source_documents": len(documents), "canonical_documents": len(documents), "total_chunks": len(chunks),
        "successfully_parsed": len(documents), "failed_documents": 0,
        "number_of_parsing_warnings": sum(len(d.metadata.get("parsing_warnings", [])) for d in documents),
        "chunks_per_document": {"min": min(per_doc, default=0), "median": statistics.median(per_doc) if per_doc else 0, "max": max(per_doc, default=0)},
        "token_count": {"min": min(tokens, default=0), "median": statistics.median(tokens) if tokens else 0,
                        "mean": statistics.mean(tokens) if tokens else 0,
                        "p95": tokens[math.ceil(.95 * len(tokens)) - 1] if tokens else 0,
                        "max": max(tokens, default=0)},
        "p95_method": "nearest_rank", "token_count_method": config["chunking"]["token_count_method"],
        "chunks_by_format": dict(sorted(Counter(c.metadata["format"] for c in chunks).items())),
        "number_of_chunks_with_overlap": sum(c.metadata["overlap_tokens"] > 0 for c in chunks),
        "number_of_chunks_without_heading": sum(not c.heading for c in chunks),
        "number_of_empty_chunks": sum(not c.text.strip() for c in chunks),
        "number_of_duplicate_content_hashes": sum(n - 1 for n in hashes.values() if n > 1),
        "duplicate_hash_groups": {h: [c.chunk_id for c in chunks if c.content_hash == h] for h, n in hashes.items() if n > 1},
        "chunks_per_document_detail": dict(sorted(counts.items())),
        "config": config["chunking"], "pilot_not_final_tokenizer": True,
    }
    return chunks, report


def boilerplate_report(documents, chunks):
    import re

    patterns = {
        "organization_name": r"Wedding Organizer X", "document_code": r"WO-DOC-\d{3}",
        "pending_validation": r"pending[_ ]practitioner[_ ]validation|belum divalidasi praktisi",
        "draft_notice": r"draft (?:operasional )?susunan peneliti|draft simulasi",
        "version": r"\bversi\s+\d+(?:\.\d+)*",
    }
    findings = {}
    for name, pattern in patterns.items():
        hits = [c.chunk_id for c in chunks if re.search(pattern, c.text, re.I)]
        findings[name] = {"chunks_with_pattern": len(hits), "chunk_ids": hits,
                          "occurrences": sum(len(re.findall(pattern, c.text, re.I)) for c in chunks)}
    removed = [b for d in documents for b in d.content_blocks if not b.retrievable]
    examples = []
    for rule in sorted({b.exclusion_rule for b in removed}):
        b = next(b for b in removed if b.exclusion_rule == rule)
        examples.append({"rule": rule, "before": b.raw_text, "after_retrievable_text": "",
                         "retained_as": "canonical block plus administrative_blocks metadata", "source_locator": b.source_locator})
    retained = [c for c in chunks if "Wedding Organizer X" in c.text][:2]
    return {"rule_counts": dict(sorted(Counter(b.exclusion_rule for b in removed).items())),
            "patterns": findings, "examples": examples,
            "retained_operational_examples": [{"chunk_id": c.chunk_id, "text": c.text[:1000]} for c in retained],
            "policy": "Full-block exact administrative matches only. Operational mentions, event context in prose, negations, document relations in operational prose and rundown versions remain."}


def sample_chunks(chunks):
    selected = []
    for fmt, number in [("DOCX", 3), ("PDF", 3), ("TXT", 3), ("XLSX", 5)]:
        candidates = [c for c in chunks if c.metadata["format"] == fmt]
        docs = sorted({c.document_id for c in candidates})
        # Spread samples across the corpus, including the rundown and seating sheets.
        preferred = ["WO-DOC-006", "WO-DOC-025", "WO-DOC-040", "WO-DOC-042", "WO-DOC-048"] if fmt == "XLSX" else docs[::max(1, len(docs)//number)][:number]
        for doc in preferred[:number]:
            c = next(c for c in candidates if c.document_id == doc)
            selected.append({"format": fmt, "chunk_id": c.chunk_id, "document_id": doc, "heading": c.heading,
                             "source_locator": c.source_locator, "token_count": c.token_count, "text_preview": c.text[:1400]})
    return selected


def safe_write(root: Path, path: Path, text: str) -> None:
    path = path.resolve()
    protected = (root / "data/source_corpus").resolve()
    if protected == path or protected in path.parents or root.resolve() not in path.parents:
        raise ValueError(f"Refusing unsafe output path: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.is_symlink():
        raise ValueError("Refusing symlink output temporary file")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def write_ingestion(root: Path, config: dict, documents, report, source_audit):
    reports = root / config["reports_dir"]
    safe_write(root, reports / "source_audit.json", json_text(source_audit))
    safe_write(root, reports / "ingestion_report.json", json_text(report))
    if report["failed_documents"]:
        raise ValueError("Ingestion failed; see ingestion_report.json. No partial canonical output published")
    safe_write(root, root / config["documents_output"], jsonl_text(documents))
    safe_write(root, (root / config["documents_output"]).parent / "ingestion_config.json", json_text(config))
    safe_write(root, root / config.get("source_integrity_output", "data/validation/source_integrity.json"), json_text({
        "source_unchanged": True, "checked_files": len(source_audit["source_snapshot"]),
        "sha256": source_audit["source_snapshot"],
    }))


def write_chunks(root: Path, config: dict, documents, chunks, report):
    from .reporting import markdown_report

    reports = root / config["reports_dir"]
    audit_report = boilerplate_report(documents, chunks)
    samples = sample_chunks(chunks)
    report["environment"] = environment(root, config)
    safe_write(root, root / config["chunks_output"], jsonl_text(chunks))
    safe_write(root, (root / config["chunks_output"]).parent / "chunk_config.json", json_text(config))
    safe_write(root, reports / "chunk_report.json", json_text(report))
    safe_write(root, reports / "boilerplate_audit.json", json_text(audit_report))
    safe_write(root, reports / "sample_chunks.json", json_text(samples))
    safe_write(root, reports / "chunk_audit.md", markdown_report(report, samples, audit_report))
