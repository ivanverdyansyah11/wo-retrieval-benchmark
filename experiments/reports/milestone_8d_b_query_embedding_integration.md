# Milestone 8D-B — Shared query embedding and offline retrieval integration

Date: 2026-10-09 Asia/Singapore. Status: **PASS for offline technical integration**.
Milestone 8C remains **`end_to_end_pending`**. Live query encoding and live R4 GPU
end-to-end inference are **NOT TESTED** here. Corpus and development queries remain
pending practitioner/expert validation; no effectiveness results or qrels were produced.

## Architecture and scope

Separate process A encodes one explicitly identified query with the existing local
`BGEEncoder`. Process B validates that artifact and scores existing corpus vectors
without importing a neural runtime or creating a tokenizer. Both R3 and the Dense
component of R4 share the **same DenseRetriever instance**, rows, corpus matrix and
CachedEncoder. R4 continues calling its existing BM25 retriever and `fuse` implementation.

Existing R1/R2/R3/R4 source files, protocols, parameters, serialization, indices and
environment were not edited. New code lives outside directories hashed by the existing
corpus index identities, preserving their validity. No new retrieval algorithm was added.
R3 still applies float32 L2 normalization and exhaustive cosine scoring; R4 still uses
k=60, all 371 Dense candidates, every positive BM25 candidate, no pseudo-rank, and
unrounded score descending then chunk ID ascending tie-breaking.

Files created:

- `src/wo_retrieval/query_vectors/__init__.py`
- `src/wo_retrieval/query_vectors/artifacts.py`
- `src/wo_retrieval/query_vectors/offline.py`
- `src/wo_retrieval/query_vectors/__main__.py`
- `tests/test_query_vectors.py`
- This report.

## Query artifact contract

Each directory contains `manifest.json` and `vector.npy` for **one** query.
The manifest records:

| Field | Meaning |
|---|---|
| `completion_status` | INCOMPLETE during staging; COMPLETE before validated atomic publication |
| `query_id` | Exact nonempty caller-supplied ID |
| `query_text_sha256` | SHA-256 of exact original UTF-8 query, including outer whitespace |
| `effective_input_sha256` | SHA-256 after existing shared normalization |
| `created_at_utc` | Timezone-aware UTC ISO timestamp |
| `contract.schema_version` | `wo_query_vector_v1` |
| `contract.corpus_index_manifest_sha256_canonical` | Canonical JSON digest of verified complete corpus manifest |
| `contract.dense_identity` | Full verified existing Dense identity, including model ID/revision, snapshot fingerprint, tokenizer/model file hashes, dependencies, environment lock, configuration and serializer/code hashes |
| `contract.query_input_contract` | Existing NFC, line-ending normalization, outer strip; no prompt or extra query metadata |
| `contract.dimension`, `dtype`, `shape` | 1024, float32, [1,1024] |
| `contract.vector_stage` | Exact BGEEncoder.encode output before project unit_vectors |
| `contract.normalization` | Official normalized CLS; existing project float32 L2 applied once inside DenseRetriever |
| `encoding` | CUDA device, FP16 provenance, batch1, max_length640, actual token length including special tokens, truncation=false; future encoding time and model metrics |
| `artifact_sha256.vector.npy` | Checksum of stored NPY bytes |

Model remains `BAAI/bge-m3`, revision
`5617a9f61b028005a4858fdac845db406aefb181`.
Raw float32 encoder output is deliberately preserved: saving a newly normalized vector
and normalizing it again during retrieval could introduce additional rounding.

Load verifies the exact original query hash and ID before constructing the adapter.
The adapter subsequently accepts only the same normalized effective input. BM25 and
Dense both receive the existing shared normalized query, with no rewriting, evidence,
answer hints or additional retriever-specific metadata.

Wrong query/hash, model/revision/config, snapshot, index identity, serializer contract,
encoding provenance, dimension, dtype, missing/invalid JSON, bad checksum, nonfinite
values, zero/overflowing norms, incomplete status and truncation are rejected. NPY uses
allow_pickle=false; file-size limits precede loading. Loaded vectors are read-only.
Publication uses a unique staging directory and never overwrites an existing artifact.
Failed runs do not automatically regenerate or retry. Timestamp is provenance, not an
arbitrary expiry period: staleness is determined by the bound identities and exact input.
Checksums establish integrity, not independent proof that a claimed producer ran BGE-M3;
actual artifacts must come from the controlled encoder with retained run evidence.

## Offline corpus verification

The offline loader uses existing R2 readiness validation, compares every Dense row's
chunk/document/serialized-text hash against those rows, checks the saved token audit
fingerprint, hashes local checkpoint/tokenizer files, reconstructs the existing Dense
cache identity, verifies its exact directory, and calls the existing complete-vector loader.
It never builds, repairs or modifies an index. R1 was independently loaded for validation.

Actual checks PASS: **371 identical unique corpus rows; matrix [371,1024], float32**.
Model/tokenizer verification reads checkpoint bytes as a streaming hash; it does not
load neural weights into an ML runtime. This adds disk I/O to readiness, excluded from
offline scoring latency. Corpus vector payload is 1,519,616 bytes (about 1.45 MiB).
One query vector payload is 4,096 bytes plus NPY header and JSON manifest.

No verified actual query embedding cache was available from 8D-A. This milestone
created no development query embeddings. Tests use explicitly synthetic query IDs,
vectors and fixture model identities; corpus vectors were never substituted for queries.

## CLI usage

Commands below are usage examples, **not live encoding runs executed in this milestone**.
No package installation or console-script registration is required.

```powershell
$env:PYTHONPATH = "$PWD/src"
$index = 'D:/ModelCache/wo-retrieval-benchmark/R3/7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f'
$artifact = 'D:/ModelCache/wo-retrieval-benchmark/query_vectors/approved-query-artifact'

# Future encoder invocation: requires separate authorization and a real exact query.
.venv-ml/Scripts/python.exe -B -m wo_retrieval.query_vectors encode `
  --corpus-index $index --artifact $artifact --query-id '<approved-ID>' `
  --query '<exact approved query text>' --approval-note '<explicit authorization reference>'

# After an actual COMPLETE artifact exists, reuse it for both methods.
.venv-ml/Scripts/python.exe -B -m wo_retrieval.query_vectors score `
  --corpus-index $index --artifact $artifact --query-id '<same-ID>' `
  --query '<same exact query text>' --method R3 --top-k 5
.venv-ml/Scripts/python.exe -B -m wo_retrieval.query_vectors score `
  --corpus-index $index --artifact $artifact --query-id '<same-ID>' `
  --query '<same exact query text>' --method R4 --top-k 5
```

Future encoding defaults to the existing **6 GiB** loading gate. An explicitly approved
low-memory run may additionally supply `--approved-low-memory`, using the existing
**5 GiB** gate and recorded approval note. The new encoder uses the previously required
**2 GiB immediate watchdog**, existing commit/load/disk/VRAM guards, and the shared GPU
lock. It imports ML dependencies and prepares the tokenizer before the final gate;
weights loading occurs only after that gate passes. Single GPU process, CUDA FP16,
batch1, dense only, cap640 with no truncation; no CPU fallback or retry.
Cache/temp remain on D: through existing offline_environment; encoder outputs are
restricted to the D: query cache. Success/failure and resource/approval evidence are
written separately as `<artifact>.run.json`; a watchdog failure leaves the run incomplete.
These gates were tested with mocks, not real GPU loading. Existing resource thresholds
and experimental TOML were not modified.

## Timing interpretation

| Component | Definition and status |
|---|---|
| Query encoding | Shared normalization/tokenization, device transfer, synchronized model forward and host output; future encoder timer, not measured here |
| Dense scoring | Existing float32 query L2, exhaustive similarity and deterministic ranking; offline phase, no model forward |
| BM25 scoring | Existing query lexical processing, scores, positive eligibility and ranking |
| RRF fusion | Existing component validation, reciprocal-rank contributions and ordering |
| Offline scoring timer | R3 Dense path or R4 BM25+Dense+fusion including normal method overhead; excludes startup, readiness, artifact loading and neural encoding |
| Reconstructed total | Future encoding time plus nonoverlapping scoring/fusion phases and documented orchestration/transfer overhead; an estimate, not measured live end-to-end latency |

The CLI currently measures total offline scoring, not separately instrumented BM25,
Dense and fusion durations. Do not infer those components from subtraction. Model load,
warm-up, artifact write/read and readiness must be recorded separately. Cache-hit timing
cannot replace the protocol's live query latency: existing timed benchmark query caching
remains disabled. A formal cached-query latency experiment would require separate
methodological approval; no protocol change was made for this technical integration.

## Tests and evidence

**66 relevant tests PASS**:

| Suite | Count |
|---|---:|
| New query artifact/offline integration/encoder safety | 15 |
| Existing R4 Hybrid | 16 |
| Existing R1/R2 lexical | 14 |
| Existing R3 Dense | 16 |
| Existing protocol consistency | 5 |

New tests cover byte-preserving round-trip, immutable loaded vectors, no overwrite,
query/ID/config/revision/snapshot/serializer mismatch, malformed/corrupted/incomplete
artifacts, invalid vectors, token/truncation provenance, normalized input parity,
R3/R4 score CLI, full371 shared Dense ranking and tail eligibility, exact ranking/score
equality against the existing encoder-shaped synthetic path, independent rational RRF
oracle, and mocked default/approved final resource gate failures preventing loading.

Validation used an import guard rejecting real Torch, Transformers and FlagEmbedding
imports and forbidding actual BGEEncoder initialization/loading/encoding. Safety tests
substitute explicit mocks. Existing build/checkpoint tests operate only on temporary
synthetic fixtures, not actual corpus re-indexing or embedding. Initial lexical subprocess
regression encountered Windows output encoding mismatch; with process-local
PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 the unchanged suite passed.

Evidence: `D:/ModelCache/tmp/wo-m8d-b/validation.json`, `tests.log`,
`targeted_final.log`, `baseline.json` and validation scripts. No Git repository is present,
so change verification uses independent byte hashes rather than Git diff.

Resource observations (different processes; not a live model feasibility claim): full
validation process initially had about 5.96 GiB available RAM and peak working set
about 169.44 MiB after index checks. Final targeted process observed 6,370,660,352 bytes
(about 5.93 GiB) available RAM, 14,179,454,976 bytes commit headroom, 62% memory load,
RSS153,968,640 bytes and peak working set158,343,168 bytes. Disk free was
C:13,864,722,432 bytes and D:909,381,369,856 bytes. These observations do not approve
future GPU loading; resources must be rechecked after ML/tokenizer preparation.

## Research integrity

All **529 pre-existing baseline files** were unchanged, including source corpus,
canonical/chunk files, snapshot, both protocols, existing reports, environment lock,
18 queries, qrels status and R1/R2/R3 index/cache files. Snapshot verification PASS.

```text
snapshot ID: WO-CORPUS-V1-DRAFT-PILOT-001
fingerprint: 7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40
corpus_manifest.json: 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f
documents.jsonl: 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01
chunks.jsonl: 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0
pilot.toml: 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26
pilot_snapshot.json: 279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e
retrieval_protocol_v1.toml: dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300
R3 complete manifest canonical fingerprint: 465cf54c7fa3aadaccbb3090279762bd27f24817360c749ede4315f1f34abc72
```

## Remaining validation

**PASS:** offline contracts, synthetic shared ranking/fusion integration, regression
tests, actual corpus index readiness and protected byte integrity.
**NOT TESTED:** actual query artifact production, GPU encoder/model loading, live
R3/R4 equivalence using real query vectors, live end-to-end timing and GPU memory.
**PENDING:** practitioner corpus/query validation and supervisor decisions already in
the existing protocol; no qrels or effectiveness claims.

Next work requires new explicit authorization for a single resource-gated real query
encoding run. After successful production, verify the same COMPLETE artifact against
both offline methods, then separately perform the approved live end-to-end check.
Separate processes reduce retained ML memory during fusion but do not remove the query
encoder's model-loading RAM/VRAM requirement. Milestone 8C is not closed by this audit.
No further milestone, installation, download, commit, push, PR or deployment was run.
