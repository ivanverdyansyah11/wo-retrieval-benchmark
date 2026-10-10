# Milestone 9A.10B — Simple Google Colab full V2 Dense preparation

**PREPARED — NOT EXECUTED.** Notebook, input exchange, full importer, and offline technical tests are ready. Colab installation, GPU model loading/inference, real output generation, and real import are NOT RUN. **R3 V2 remains INCOMPLETE**; Milestone 8C live end-to-end verification remains pending. No effectiveness metrics or human-validation claims are made.

## Scope and architecture audit

Reviewed actual V2 chunks/snapshot, checksum-bound V2 builder and R1/R2 indexes, shared serializer, R3 encoder/cache/scorer, shared query artifact contract and offline adapter, version-aware V2 support, previous portable package, and reports 8B, 8D-B, 9A.8, 9A.9 and 9A.10. Read-only preparation verified current snapshot/index/model identities through existing `prepare_v2`.

The new workflow supersedes the two-vector plan for the user's next run. The old notebook, package, module and report remain byte-identical. Full output must regenerate **all 371 corpus vectors and all 18 query vectors in the same Colab environment/model session**, with **zero local vector reuse**. Original documents, extraction, chunking, queries, silver qrels, lexical methods, Dense exact scoring and RRF remain unchanged.

No conflicting input preprocessing was found. Corpus texts match the existing serializer and V2 lexical input mapping exactly. Query input remains the existing shared normalization: NFC, CRLF/CR to LF, outer strip, no prompt. Exact original text and effective input hashes are stored separately.

One important output-stage distinction is preserved: the existing shared query cache stores official encoder float32 output **before** project `unit_vectors`, whereas the requested final query matrix is project-normalized float32. The cloud ZIP therefore contains both `queries.npy` (normalized) and `query_encoder_output.npy` (official output before additional project L2). Import publishes the latter through the unchanged shared query artifact contract; existing DenseRetriever applies project L2 once. This avoids an extra normalization step or a misleading vector-stage claim. No query rewriting or new serialization policy is introduced.

## Files created

Only five additive repository files:

- `experiments/portable/v2_bge_m3/bge_m3_v2_full_colab.ipynb`
- `experiments/portable/v2_bge_m3/full_input_package.zip`
- `src/wo_retrieval/full_colab.py`
- `tests/test_full_colab.py`
- This report.

No existing file was changed. No packages were installed or downloaded on the laptop.

## Input package and integrity

Snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.

Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

Corpus status: `ai_corrected_pilot_not_human_validated`. All 18 queries retain `draft_pending_expert_review`; their original V1 metadata/text is not rewritten to pretend they were newly validated against V2.

Input ZIP: **127,558 bytes**, four entries: `inputs.json`, `runtime.py`, checksum-bound previous exchange helpers, and the exact existing shared text module. It contains 371 serialized corpus records, 18 exact original query texts, canonical IDs/order, hashes, actual token counts, model/configuration, snapshot binding, source artifact hashes and runtime hashes. It records the count of 42 provenance pointers but does **not** include their evidence text. No qrels, review notes, source documents, credentials, indices or model checkpoint are uploaded.

ZIP SHA-256: `634f861031fb002884f5637aebdd0ff2256dbfc1f831fcd155f3c9efcdf6f112`.

Canonical package fingerprint: `88a40a5ef5ce264ae282c67a90bb79525d34cd5c1eedb11f03fda01341fd554b`.

Corpus ID/text-hash mapping digest: `d184e8e43ecc94388c6aaebeedf9ad99c873687c834c5caf0f1cc15885ebf619`.

Query ID/text-hash mapping digest: `89bc58f09830430b8bb5e4dd2f5b3b8ec81207aec0ae5ca83fbfd7541c7b7f55`.

| Source artifact | SHA-256 |
|---|---|
| V2 chunks.jsonl | `0cfad810122cde84be55b1fedb330c98aafbe30e14ea0168699212382dd4c5ba` |
| V2 pilot_snapshot.json | `6658fee4737c0d2fa725ee31cb647ec638de350fc2ccfe669999847ac2331b07` |
| Original development_queries_draft.jsonl | `27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95` |
| Original development_query_provenance.jsonl | `a880b60972e64c559e7dbe61e6b446a6d258914182e35c22e5c2520f62d05d59` |
| retrieval_protocol_v1.toml | `dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300` |
| dense_v2_binding.json | `5155ce8f7a5773b6372be74f5c08ef91f09a14241ab78293803e41d2c7f1232a` |

The existing snapshot anchors all protected document/chunk/code/configuration hashes. R1/R2 V2 readiness and the old Dense index were verified read-only; source vectors are not used to build the cloud output.

### Tokenization

These are actual pinned-tokenizer counts obtained locally without neural model loading; special tokens included. The notebook repeats the audit before loading weights and must reproduce every record's count.

| Input | Count | Min | Median | Mean | P95 nearest-rank | Max | Over 640 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Corpus | 371 | 83 | 137 | 194.518 | 497 | 573 | 0 |
| Queries | 18 | 18 | 24 | 24.222 | 30 | 30 | 0 |

Truncation is disabled; any mismatch or input above 640 stops execution. XLSX operational/header/row context remains exactly as serialized by the existing pipeline.

## Native Colab dependency strategy

The notebook uses Colab's Python 3.12 runtime and pip directly. There is no additional virtual environment, `EnvBuilder`, `ensurepip`, apt/Python replacement or working-directory dependency. `/content/wo_bge_m3_full` uses `exist_ok=True`.

Cell 1 inspects Python, installed Torch/dependencies, CUDA, GPU and free VRAM before installation. It stops on Python 3.13 or missing GPU. Cell 2 retains native CUDA Torch rather than forcing Windows/local `2.12.1+cu126`; native Torch and NumPy are protected by exact installed-version constraints during dependency resolution. This is the authorized cloud environment approach, not a model/precision/algorithm change.

Core official API pins:

| Package | Version |
|---|---|
| FlagEmbedding | 1.4.2 |
| transformers | 4.57.6 |
| tokenizers | 0.22.2 |
| sentence-transformers | 5.2.0 |
| peft | 0.18.1 |

Only missing/different core pins are requested; their required transitive dependencies are resolved by pip. The plan is dry-run first; any attempted Torch replacement stops installation. There is no global blanket upgrade/uninstall, `--no-deps`, or force reinstall. A failed resolver/import/`pip check`/CUDA numerical smoke is an environment FAIL, not a reason to ignore conflicts. Native Torch compatibility is established by actual import, FP32/FP16 CUDA smoke and later model inference, not assumed from its version string.

If installation occurs, the cell records a setup checkpoint and explicitly stops for **Runtime > Restart session**, followed by rerunning Cell 1–2. It does not continue with stale imported packages. After matching pins, successful imports, `pip check` and CUDA numeric checks, it prints **ENVIRONMENT PASS**. Cloud runtime availability and package resolution remain untested here.

The final manifest records actual Python/platform, CUDA runtime, GPU name/capability, Torch and dependency versions, complete installed environment lock, and differences against local reference versions (including absent local-reference packages). Exact cloud reproduction can use that actual lock after review; the portable protocol does not claim all preinstalled transitive versions are already known. [Colab explains runtime-version and preinstalled-library changes](https://research.google.com/colaboratory/runtime-version-faq.html).

## Pinned model and inference

Model `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`; CUDA FP16, batch 1, max_length 640, CLS, dense-only, dimension 1024, float32 storage. Sparse/ColBERT/reranking/fine-tuning/CPU fallback and automatic retry are absent.

The runtime verifies the official repository commit through Hugging Face and downloads the exact snapshot revision into the Colab cache. All 12 required checkpoint/tokenizer files are checked against existing local hashes. The exact three installed official FlagEmbedding inference/model files are also verified against local 1.4.2 implementation hashes. Loading uses the verified local snapshot path, not an assumed FlagEmbedding `revision` constructor argument. The pinned repository is available at the [official revision tree](https://huggingface.co/BAAI/bge-m3/tree/5617a9f61b028005a4858fdac845db406aefb181).

One model is loaded and reused for a dimension/finite smoke input, 371 sequential corpus forwards and 18 sequential query forwards. Direct official model forward uses the same existing dense-only flags and input normalization; no wrapper batch-size retry. Actual FP16 weights are verified. The cloud output records separate model loading, corpus encoding and query encoding times plus peak allocated/reserved GPU memory. Exact Dense scoring, BM25 scoring and RRF timings are **NOT MEASURED** here. Cache-hit scoring must never be called live end-to-end latency.

## Checkpoints and reruns

Per-vector NPY files and atomically updated progress JSON live in `corpus_partial/` and `queries_partial/`, marked INCOMPLETE. Resume is **explicit** through `RESUME=True`, bound to exact package fingerprint, full input mapping, revision, environment and runtime session ID. Each completed row is rechecked for checksum, shape, finite values, official-normalization tolerance, ID/input and order before reuse. A previously finished corpus checkpoint can be reused while the not-yet-started query checkpoint is created in the same session.

The notebook never treats file existence as validity. A COMPLETE output ZIP stops rerun; archive/move it explicitly before starting another run. Corrupted/stale/session-mismatched partials stop rather than triggering automatic retries.

Checkpoint scope is the **surviving same Colab VM/kernel session**: a browser disconnect can be resumed if that session remains alive. Deleting/replacing the VM loses `/content`; a kernel restart changes the session identity and existing inference partials are rejected. No cross-session vector mixing or durable Drive checkpoint is claimed. If the VM/session is lost, report the interruption and start a new full run in a fresh work state; never combine the old local 369 vectors with cloud results.

## Output and local import

Cloud output: `bge_m3_v2_full_embeddings.zip`, with:

- `corpus.npy`: normalized float32 `(371,1024)`.
- `queries.npy`: normalized float32 `(18,1024)`.
- `query_encoder_output.npy`: official float32 query output before project L2, for unchanged query-cache compatibility.
- `manifest.json`: COMPLETE only after all validations; canonical corpus/query mappings, input hashes, tokenizer counts, model/configuration/runtime hashes, checksums, UTC creation, actual environment, precision/device, session, timings and provenance.

The importer rejects partial/synthetic/corrupt artifacts, wrong revision/config/snapshot, stale exact texts, duplicate/missing/order mappings, wrong shapes/dtypes, NaN/Inf, zero/non-normalized vectors and checksum failures. Archive entries are bounded/allowlisted and read without path extraction; NPY uses `allow_pickle=False`. It rechecks source/input/output identities immediately before publication.

The previous V2 publisher is designed for 369+2 reuse, so it cannot serve this full rebuild unchanged. The additive full publisher uses the **existing R3 format, matrix validator, atomic JSON/NPY writers and `load_vectors` readback**, and the existing shared query artifact `publish`/`contract`/`load_artifact`. No alternative scoring/index algorithm is introduced, and no additional L2 pass is applied to already-normalized corpus output during import.

All 371 cloud rows and 18 shared query artifacts are staged together; only after complete readback and source revalidation is the whole index tree atomically renamed to `experiments/indexes/v2_ai_corrected/R3`. Query store: `R3/query_vectors/WO-DEV-xxx/`. Failure leaves unpublished INCOMPLETE staging. Existing R3 V2 conflicts are refused, never overwritten. V1 and R1/R2 stay untouched.

Actual cloud dependency/environment identity replaces local encoding identity in this full artifact; frozen protocol fingerprints still identify the unchanged research/input policy. The new `full_colab.load_components` is the explicit loader for full-cloud V2. The legacy `versioned_dense` loader remains the separate incremental 369+2 contract and is not silently repurposed. Existing offline `query_vectors.offline.retrievers` accepts the full loader's components, reusing DenseRetriever and HybridRetriever unchanged. Synthetic tests verify R3 and R4's Dense component use identical rankings and BM25 receives the same query.

All corpus/query vectors share cloud provenance; **local vector reuse = 0**. Numerical bitwise equivalence against GTX 1050 is NOT TESTED. Differences across native Torch/NumPy/GPU versions can affect floating-point rounding; this does not establish an effectiveness improvement.

## Tests and protected artifacts

**137 distinct tests PASS**: final 108 ML/retrieval/portable tests in 58.095 s plus 29 ingestion/versioned-pipeline tests in 12.347 s. The final regression runner confirmed `torch_imported=false`. Eight new test methods, with rejection subcases, are included in the final 108-test run against the final package/runtime.

Tests cover notebook JSON/AST and nine unexecuted code cells; 371/18 counts and exact serializer/source parity; ZIP corruption/extra/duplicate/missing entries; model/snapshot/hash/mapping/config/partial rejection; dtype/dimension/NaN/Inf/zero/norm validation; explicit checkpoint resume with no re-encoding of verified rows; stale session/model/order and corrupt checkpoint rejection; synthetic full import, zero local reuse, query raw-stage preservation, shared R3/R4 ranking/contribution compatibility, conflict refusal, atomic failure isolation, and existing lexical/Dense/Hybrid/protocol regressions. Synthetic vectors are explicitly test-only, not real GPU evidence. No effectiveness scores were computed.

**657 existing baseline files are SHA-256 unchanged**, including V1/V2 source/canonical/chunk/snapshot assets, original queries, silver qrels, protocol/model environment configuration, all existing indices, previous portable notebook/package/code and run evidence. Frozen V2 fingerprint is unchanged. R1/R2 V2 remain COMPLETE; real R3 V2 is absent/unpublished. This is a filesystem hash audit, not a Git status claim; this checkout has no Git repository.

## Instruksi pengguna

1. Upload/buka **`bge_m3_v2_full_colab.ipynb`** di Google Colab.
2. Pilih runtime **Python 3.12** dan **T4 GPU**. Jika opsi tidak tersedia atau kuota sesi habis, kelola sesi melalui UI Colab; notebook tidak mengubah Python sistem atau menutup sesi lain.
3. Jalankan Cell 1–2. Jika diminta, **Runtime > Restart session**, lalu ulangi Cell 1–2 sampai **ENVIRONMENT PASS**.
4. Jalankan Cell 3 dan upload **`full_input_package.zip`** saja.
5. Jalankan Cell 4–8 berurutan: audit token, load satu model, corpus, query, validasi. Jangan ubah konfigurasi atau melakukan retry otomatis setelah error/OOM.
6. Jalankan Cell 9 untuk download **`bge_m3_v2_full_embeddings.zip`**.
7. Simpan output di `D:/ModelCache/wo-retrieval-benchmark/colab_exchange/v2/bge_m3_v2_full_embeddings.zip`. Simpan notebook execution log dan checksum yang dicetak.
8. Kirim path output dan hasil execution untuk review. Jangan menganggap local R3 V2 sudah COMPLETE hanya karena ZIP cloud berhasil di-download.
9. Setelah import lokal disetujui, dari repository root:

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
.venv-ml/Scripts/python.exe -B -m wo_retrieval.full_colab import --input experiments/portable/v2_bge_m3/full_input_package.zip --output D:/ModelCache/wo-retrieval-benchmark/colab_exchange/v2/bge_m3_v2_full_embeddings.zip
.venv-ml/Scripts/python.exe -B -m wo_retrieval.full_colab inspect
```

`--output` pada import adalah ZIP hasil Colab yang dibaca, bukan path destination index. `inspect` menggunakan loader full-cloud dan tidak memuat model. Setelah real import/readback PASS barulah R3 V2 dapat disebut COMPLETE. Jangan lanjut benchmark atau tuning tanpa instruksi terpisah.

STOP setelah preparation. Tidak ada eksekusi Colab, local GPU/model inference, actual import, instalasi/download laptop, benchmark, query/qrels generation, commit, push, PR atau deploy.
