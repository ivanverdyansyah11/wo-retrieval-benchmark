# Milestone 9A.11 — Full Colab import and R3 V2 finalization

**MILESTONE 9A.11 — R3 V2 COMPLETE, R4 INTEGRATION SMOKE PASS.**

The previous path blocker is resolved. The source is the actual repository-local ZIP provided by the user; no attempt was made to use the previous ModelCache exchange path. Import and smoke used CPU-only existing modules. No BGE-M3/CUDA inference, installation, model download, Colab execution, algorithm or data change occurred locally.

## Source and preflight

- Source: `D:\Project\wo-retrieval-benchmark\colab_exchange\v2\bge_m3_v2_full_embeddings.zip`.
- ZIP size: 1,513,420 bytes.
- ZIP SHA-256: `4dab62100a425aa9ea705d9b74e738e100851ee0055b680c3add94381bac2671`.
- Target was absent before publication; no conflict or overwrite.
- CRC integrity PASS; exactly four allowlisted entries, no duplicate/missing/extra files.
- Manifest fingerprint, COMPLETE status and all three internal NPY SHA-256 checks PASS.
- Snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.
- Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.
- Model: `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`.
- CUDA FP16 provenance, batch 1, max_length 640, dense-only, CLS, dimension 1024, normalized float32 storage: PASS.
- Pinned checkpoint/tokenizer and official implementation hashes, runtime hashes, package fingerprint, actual environment lock, dependency deviation records and UTC manifest timestamp: PASS through unchanged existing importer.

Existing `prepare_v2` verified frozen V1/V2 identities, V2 R1/R2 index readiness, source R3 V1 checksums/mapping and the exact shared serializer. Existing V1 R1 loader also passed readback. All 371 canonical chunk IDs, document IDs, serialized text/hashes, ordering and token counts match current local V2 inputs. All 50 document IDs are represented. All 18 query IDs, exact original texts, effective shared-normalized texts/hashes and DRAFT status match local queries. Token mappings and truncation=false match the frozen input contract.

## Vector and query-cache compatibility

| Artifact | Shape | dtype | Finite/nonzero | Norm minimum | Norm maximum |
|---|---|---|---|---:|---:|
| corpus.npy | [371, 1024] | float32 | PASS | 0.9999998808 | 1.0000001192 |
| queries.npy | [18, 1024] | float32 | PASS | 0.9999999404 | 1.0000001192 |
| query_encoder_output.npy | [18, 1024] | float32 | PASS | 0.9997151494 | 1.0002712011 |

The two query stages are deliberately **not byte-identical**:

- Maximum absolute difference, official encoder output versus project-normalized query matrix: `6.63995742798e-05`.
- Local `unit(query_encoder_output.npy)` versus `queries.npy`: maximum absolute difference `0.0`; differing elements `0`; existing exact array-equality check PASS.

`query_encoder_output.npy` is the official normalized CLS FP16 output converted to float32, **before the additional project float32 L2 pass**. Its small norm deviation is checked against the existing official-FP16 tolerance (0.002). Normalized matrices use the existing absolute norm tolerance 1e-5. No tolerance or validator was modified. The importer preserves original encoder-output values in the unchanged shared query cache contract; DenseRetriever applies project L2 once. All 18 imported query artifacts were validated by existing `load_artifact` and used successfully without model loading.

## Atomic publication and runner integration

The unchanged `full_colab.import_output` validated the real exchange, staged all corpus/query artifacts, performed existing matrix/cache readback and immediate source/output revalidation, then atomically renamed the complete tree. It did not reuse any V1/local vector.

- Target: `experiments/indexes/v2_ai_corrected/R3`.
- Status: COMPLETE.
- Corpus matrix: `(371, 1024)`; new vectors 371; reused vectors 0.
- Query store: `R3/query_vectors/WO-DEV-001` through `WO-DEV-018`, all COMPLETE.
- Index manifest SHA-256: `9bc2f383bfd0a3ba485c79121c0df51e73930bbe581d7965a1c261adce4c5097`.
- Local import/publication time: 14.895929 s, including CPU validation/readback/source checks, **not inference time**.
- No leftover publication staging directory was needed after success.

The explicit full-cloud version-aware loader `full_colab.load_components` passed real readback and feeds the unchanged `query_vectors.offline.retrievers` adapter, DenseRetriever and HybridRetriever. The legacy incremental 369+2 loader was not repurposed or used for this full-cloud identity. This integration proves runner/scorer compatibility on the explicit full-cloud path, without claiming every legacy CLI now selects it automatically.

## Real cached-query integration smoke

All 18 development queries were scored on CPU using their real Colab-produced cache. For each query, full R3 ranking and R4 ranking contain 371 unique valid IDs with correct consecutive ranks and snapshot metadata. Source mapping validates document IDs; RRF also checks component metadata. Scores are finite and rankings obey score-descending, chunk-ID-ascending tie-breaking.

Each R3 and R4 ranking was repeated and compared exactly. R4's Dense component matched the standalone R3 full ranking. Dense ordering/scores were checked against a separate normalized matrix-vector computation. RRF contribution and total scores were recomputed separately as `1/(60 + dense_rank)` plus `1/(60 + positive_bm25_rank)` when eligible; absent/nonpositive BM25 candidates contribute zero. Full Dense depth 371, k=60, positive-score eligibility and tie-breaking are unchanged.

| Query | R3/R4 | BM25 positive candidates | R3 top-1 chunk | R4 top-1 chunk | Determinism / RRF check |
|---|---|---:|---|---|---|
| WO-DEV-001 | PASS | 371 | WO-DOC-006-C002 | WO-DOC-006-C002 | PASS |
| WO-DEV-002 | PASS | 363 | WO-DOC-035-C002 | WO-DOC-009-C001 | PASS |
| WO-DEV-003 | PASS | 270 | WO-DOC-017-C004 | WO-DOC-017-C004 | PASS |
| WO-DEV-004 | PASS | 354 | WO-DOC-024-C004 | WO-DOC-024-C004 | PASS |
| WO-DEV-005 | PASS | 371 | WO-DOC-031-C005 | WO-DOC-031-C005 | PASS |
| WO-DEV-006 | PASS | 352 | WO-DOC-019-C004 | WO-DOC-019-C004 | PASS |
| WO-DEV-007 | PASS | 331 | WO-DOC-001-C006 | WO-DOC-001-C006 | PASS |
| WO-DEV-008 | PASS | 349 | WO-DOC-012-C007 | WO-DOC-012-C007 | PASS |
| WO-DEV-009 | PASS | 356 | WO-DOC-050-C003 | WO-DOC-036-C001 | PASS |
| WO-DEV-010 | PASS | 371 | WO-DOC-037-C003 | WO-DOC-037-C003 | PASS |
| WO-DEV-011 | PASS | 366 | WO-DOC-016-C003 | WO-DOC-041-C008 | PASS |
| WO-DEV-012 | PASS | 353 | WO-DOC-050-C009 | WO-DOC-049-C006 | PASS |
| WO-DEV-013 | PASS | 365 | WO-DOC-024-C006 | WO-DOC-014-C002 | PASS |
| WO-DEV-014 | PASS | 370 | WO-DOC-043-C009 | WO-DOC-022-C004 | PASS |
| WO-DEV-015 | PASS | 371 | WO-DOC-032-C003 | WO-DOC-032-C001 | PASS |
| WO-DEV-016 | PASS | 371 | WO-DOC-041-C007 | WO-DOC-005-C004 | PASS |
| WO-DEV-017 | PASS | 356 | WO-DOC-043-C013 | WO-DOC-030-C004 | PASS |
| WO-DEV-018 | PASS | 371 | WO-DOC-003-C006 | WO-DOC-003-C006 | PASS |

Top-1 results are technical ranking observations, not relevance judgments, answer keys or evidence of method effectiveness.

### Sample top-5 RRF contributions


WO-DEV-001:

| Chunk | BM25 rank | Dense rank | BM25 contribution | Dense contribution | RRF total |
|---|---:|---:|---:|---:|---:|
| WO-DOC-006-C002 | 1 | 1 | 0.016393442623 | 0.016393442623 | 0.032786885246 |
| WO-DOC-006-C001 | 2 | 2 | 0.016129032258 | 0.016129032258 | 0.032258064516 |
| WO-DOC-006-C003 | 4 | 3 | 0.015625000000 | 0.015873015873 | 0.031498015873 |
| WO-DOC-006-C004 | 3 | 4 | 0.015873015873 | 0.015625000000 | 0.031498015873 |
| WO-DOC-006-C005 | 5 | 8 | 0.015384615385 | 0.014705882353 | 0.030090497738 |

WO-DEV-007:

| Chunk | BM25 rank | Dense rank | BM25 contribution | Dense contribution | RRF total |
|---|---:|---:|---:|---:|---:|
| WO-DOC-001-C006 | 1 | 1 | 0.016393442623 | 0.016393442623 | 0.032786885246 |
| WO-DOC-028-C004 | 3 | 7 | 0.015873015873 | 0.014925373134 | 0.030798389007 |
| WO-DOC-031-C004 | 7 | 9 | 0.014925373134 | 0.014492753623 | 0.029418126758 |
| WO-DOC-005-C006 | 13 | 4 | 0.013698630137 | 0.015625000000 | 0.029323630137 |
| WO-DOC-005-C001 | 16 | 3 | 0.013157894737 | 0.015873015873 | 0.029030910610 |

WO-DEV-013:

| Chunk | BM25 rank | Dense rank | BM25 contribution | Dense contribution | RRF total |
|---|---:|---:|---:|---:|---:|
| WO-DOC-014-C002 | 2 | 3 | 0.016129032258 | 0.015873015873 | 0.032002048131 |
| WO-DOC-014-C004 | 3 | 2 | 0.015873015873 | 0.016129032258 | 0.032002048131 |
| WO-DOC-024-C003 | 1 | 5 | 0.016393442623 | 0.015384615385 | 0.031778058008 |
| WO-DOC-003-C004 | 5 | 7 | 0.015384615385 | 0.014925373134 | 0.030309988519 |
| WO-DOC-024-C001 | 9 | 10 | 0.014492753623 | 0.014285714286 | 0.028778467909 |

## Environment and timing provenance

Actual values recorded in the cloud manifest: Python 3.12.13, GPU Tesla T4, capability [7, 5], Torch 2.11.0+cu128, CUDA runtime 12.8, NumPy 2.0.2, FlagEmbedding 1.4.2, Transformers 4.57.6. Full actual dependency lock and differences from local reference are preserved in the index manifest and query artifact provenance.

Colab-recorded timings, **not remeasured locally**:

- Model loading: 5.935571 s.
- Corpus encoding: 14.696692 s.
- Query encoding: 0.293055 s.
- Recorded peak GPU allocated/reserved: 1.082142 / 1.109375 GiB.

Local cached scoring observations are first timed full-ranking calls per query, followed by untimed determinism repeats. They exclude cache setup/load, model loading and query encoding, and are not a controlled retrieval latency benchmark:

| Local technical measurement | Min seconds | Median seconds | Max seconds |
|---|---:|---:|---:|
| Dense full-ranking scoring | 0.000772 | 0.000836 | 0.001222 |
| BM25 + Dense + RRF combined | 0.004051 | 0.004585 | 0.035716 |

BM25 and RRF were not timed separately. No local inference latency, live end-to-end latency, or cross-device reconstructed total is claimed. Import and smoke runners confirmed `torch_imported=false`.

## Regression and research integrity

**137 tests PASS**: 108 retrieval/Dense/Hybrid/query-contract/portable/protocol/versioned tests (47.586 s), plus 29 ingestion/versioned-pipeline tests (10.539 s). Regression runner also confirmed no Torch import. Synthetic test fixtures remain test-only; real smoke above uses actual cloud vectors.

Before report replacement, all **664 existing baseline files were SHA-256 unchanged** after import/smoke. The only authorized existing-file edit is this report, replacing its prior path-blocked status. Protected V1/V2 snapshots, source/canonical/chunk assets, original queries/provenance, silver qrels, protocol/environment configuration, all source code/tests, R1/R2 V1/V2 indices, V1 R3 and the supplied ZIP remain unchanged. Existing readiness/checksum validators also passed; integrity is not inferred only from file count.

Files created in the repository: **39 derived R3 V2 files**, consisting of `vectors.npy`, `rows.json`, `manifest.json`, and `vector.npy`/`manifest.json` under each of these 18 query folders:

- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-001/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-002/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-003/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-004/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-005/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-006/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-007/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-008/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-009/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-010/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-011/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-012/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-013/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-014/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-015/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-016/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-017/`
- `experiments/indexes/v2_ai_corrected/R3/query_vectors/WO-DEV-018/`

File changed: `experiments/reports/milestone_9a11_full_colab_import_r3v2.md` only. No source code, dependency, configuration, corpus, query or qrels change. Temporary run/test evidence is under `D:/ModelCache/tmp/wo-m9a11`; it is not a benchmark dataset.

## Remaining risks and next step

No import blocker remains. Corpus remains `ai_corrected_pilot_not_human_validated`; development queries remain DRAFT and silver qrels remain provisional, not expert/human-validated ground truth. No Recall, MRR or nDCG was calculated; no best-method conclusion or tuning occurred. Numerical bitwise equivalence with older GTX 1050 embeddings is not claimed.

This is real cached-vector R3/R4 integration, not local live GPU query encoding or local end-to-end inference completion. All full V2 corpus/query vectors share cloud session/environment provenance; there is no 369-local/2-cloud mixture.

Recommended next milestone: review this import and cached technical smoke, then explicitly approve a V2 offline evaluation protocol/run using the same verified corpus/query caches. Ground-truth approval and provisional-silver reporting must be resolved before final thesis effectiveness claims. Do not automatically start evaluation or generate main queries.

STOP: no commit, push, PR, deploy, inference rerun, or final benchmark was performed.
