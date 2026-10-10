import json


def markdown_report(report, samples, boilerplate):
    lines = ["# Pilot ingestion and chunk audit", "",
             "Corpus v1-draft; pending_practitioner_validation. No retrieval experiment executed.", "",
             "Token proxy: ceil(Unicode code points / 4), including labels and separators. This is not a model tokenizer.", "",
             "Target 500 / overlap up to 75 pilot proxy tokens. Overlap only within split natural units; no cross-section overlap.", "",
             "## Statistics", "", "```json", json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2), "```", "",
             "## Samples", ""]
    for sample in samples:
        lines.extend([f"### {sample['chunk_id']} ({sample['format']})", "",
                      f"Document: {sample['document_id']}; heading: {sample['heading']}; pilot tokens: {sample['token_count']}", "",
                      "Locator:", "```json", json.dumps(sample["source_locator"], ensure_ascii=False, sort_keys=True, indent=2), "```", "",
                      "Text preview:", "```text", sample["text_preview"], "```", ""])
    lines.extend(["## Boilerplate", "", boilerplate["policy"], "", "```json",
                  json.dumps(boilerplate, ensure_ascii=False, sort_keys=True, indent=2), "```", "",
                  "## Review before retrieval", "",
                  "- Review PDF typography and TXT stanza heading heuristics against the original files.",
                  "- Review XLSX row boundaries, cached formulas, RACI definitions and inherited guide_context.",
                  "- Review retained operational organization names, document references and rundown versions; do not delete these globally.",
                  "- Review small natural sections and large table splits; pilot counts do not imply optimal retrieval settings.",
                  "- Practitioner validation remains pending; freeze extraction/chunk policy before query/qrels work.", ""])
    return "\n".join(lines)
