# Frozen preliminary pilot corpus snapshot

Snapshot ID: **WO-CORPUS-V1-DRAFT-PILOT-001**

Created: 2026-10-08T17:18:28+08:00 (Asia/Singapore).

Corpus version: `v1-draft`. Validation status: `pending_practitioner_validation`. Manual chunk review accepted by the user before snapshot creation.

**Practitioner validation is still pending. This snapshot is for preliminary retrieval benchmarking, not the final validated thesis dataset.**

## Accepted snapshot

| Item | Value |
|---|---|
| Source documents | 50 |
| Canonical documents | 50 |
| Chunks | 371 |
| Source formats | DOCX 26; PDF 9; TXT 5; XLSX 10 |
| Chunk formats | DOCX 187; PDF 79; TXT 42; XLSX 63 |
| Chunking | Structure-aware with recursive fallback |
| Target proxy tokens | 500 |
| Maximum overlap proxy tokens | 75 |
| Token method | approx_unicode_chars_div4_v1 |
| Orphan candidates | 0 |
| Near-duplicate candidates | 0 |
| Operational block coverage | 768/768, including full nonwhitespace span coverage |
| Source mutation | None |

Retrievable source is restricted to `data/source_corpus/documents/`. Manifest and audit documentation are metadata/evidence only.

## Artifact hashes

SHA-256 over existing file bytes:

- `data/chunks/chunks.jsonl`
  `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0`
- `data/processed/documents.jsonl`
  `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01`
- `data/source_corpus/corpus_manifest.json`
  `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f`
- `experiments/configs/pilot.toml`
  `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26`

## Aggregate fingerprint

`7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`

Algorithm: SHA-256 over the UTF-8 encoding of the artifact hash mapping, JSON keys sorted, compact comma/colon separators, no trailing newline. Exactly the four artifacts above are included. Creation timestamp and snapshot files are excluded. The exact canonical payload is also saved in the JSON manifest.

## Configuration

```json
{
  "effective_config": {
    "overlap_tokens": 75,
    "target_tokens": 500,
    "token_count_method": "approx_unicode_chars_div4_v1"
  },
  "maximum_overlap_proxy_tokens": 75,
  "overlap_policy": "Only within oversized natural units; no cross-section overlap; structured table/list overlap retains whole pieces.",
  "strategy": "structure-aware chunking with recursive fallback",
  "target_proxy_tokens": 500
}
```

Token proxy is `ceil(Unicode code points / 4)`, including labels and newlines. It is not an embedding-model tokenizer.

## Quality summary

```json
{
  "chunks_with_overlap": 42,
  "chunks_without_heading": 0,
  "coverage_status": "PASS",
  "covered_operational_blocks": 768,
  "duplicate_content_hashes": 0,
  "empty_chunks": 0,
  "fully_covered_nonwhitespace_operational_blocks": 768,
  "locator_issues": 0,
  "missing_blocks": 0,
  "near_duplicate_candidates": 0,
  "operational_blocks": 768,
  "orphan_candidates": 0,
  "partial_blocks": 0,
  "quality_audit_scope": "Deterministic structural and lexical checks; not semantic uniqueness or practitioner validation.",
  "source_mutation": false,
  "token_count_statistics": {
    "max": 485,
    "mean": 190.33423180592993,
    "median": 132,
    "min": 77,
    "p95": 447
  }
}
```

Evidence report hashes and all 50 source-document hashes are recorded in the JSON manifest. Existing quality audit hashes were checked against the current canonical, chunk and pilot-config bytes. Source document hashes match the corpus manifest, and all source files match the prior source integrity record.

## Research scope

- Practitioner validation is still pending. Manual chunk review does not validate operational domain knowledge.
- This snapshot is for preliminary retrieval benchmarking, not the final validated thesis dataset.
- The source documents are researcher-composed operational drafts. No source corpus or derived artifact was copied, rewritten or repaired.
- Frozen means a research reference to the recorded bytes and configuration; no filesystem permissions or existing file attributes were changed.
- No queries, qrels, retrieval, BM25, embeddings, FAISS, RRF, evaluation or LLM implementation was performed.

## Preservation verification

All 115 existing protected project files, including 57 source corpus files, retained the same filename set, SHA-256, byte size and modification time. Environment cache `.venv` and Git metadata `.git` are outside this research-artifact verification scope.

Only `data/validation/pilot_snapshot.json` and `data/validation/pilot_snapshot.md` were created. No corpus copies, regeneration, code/config changes, existing audit report changes, commit, push, PR or deploy.
