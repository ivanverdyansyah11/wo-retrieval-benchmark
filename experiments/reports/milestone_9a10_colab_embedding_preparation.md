# Milestone 9A.10 — Portable Google Colab embedding preparation

Status: **PREPARATION / OFFLINE VALIDATION PASS**. Colab execution, real GPU inference, real output import, and numerical cross-GPU equivalence are **NOT RUN / NOT TESTED**. R3 V2 remains **INCOMPLETE**. No retrieval effectiveness evaluation was performed.

## Scope and files

This package prepares only the two changed V2 corpus vectors. It reuses the existing shared serializer and Milestone 9A.9 index publication/readback functions. It does not change retrieval parameters, source documents, queries, qrels, frozen snapshots, or existing indices.

Five additive files:

- `src/wo_retrieval/portable_embeddings.py`: input export, cloud runtime, strict output validation, and local import CLI.
- `tests/test_portable_embeddings.py`: offline fixtures and boundary validation.
- `experiments/portable/v2_bge_m3/input_package.zip`: two exact serialized inputs plus the checksum-bound portable runtime.
- `experiments/portable/v2_bge_m3/bge_m3_v2_colab.ipynb`: unexecuted Colab notebook.
- This report.

## Verified input package

Snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.

Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

Serializer: `wo_operational_context_dedup_v1`. Inputs were obtained from actual V2 chunks using the existing shared serializer, not directly from DOCX. No additional instruction or context was injected.

| Chunk ID | Document ID | Actual tokens, including special tokens | Serialized text SHA-256 |
|---|---|---:|---|
| WO-DOC-024-C003 | WO-DOC-024 | 218 | `4a3795989f57df285596b4a1b73eb6a70723a67e6cbe1a94f34046b906e00208` |
| WO-DOC-027-C009 | WO-DOC-027 | 169 | `d1704c559dfa415f359f820e11c726fb20f3ccec84117a98b03d0567a7f75bbf` |

Token counts were independently obtained from the existing pinned tokenizer and checked against V2 mapping records. Neither input needs truncation at 640 tokens.

ZIP size: **8,924 bytes**. Exactly `inputs.json` and `runtime.py`.

ZIP SHA-256: `4aaf7b5f122087789a4ec76467a40a6be5f31f57813cc4cfc4db1d4029adf183`.

Canonical input package fingerprint: `50e54d5d26979ef000a3b41e57c39fef91a91ea8a286488d865da7b5b450477a`.

The package also carries hashes for 12 required model/tokenizer files and three official FlagEmbedding implementation files. The notebook binds the uploaded ZIP to its SHA-256; the runtime is checksum-bound to the input manifest.

## Inference and dependency contract

The [official pinned model revision](https://huggingface.co/BAAI/bge-m3/tree/5617a9f61b028005a4858fdac845db406aefb181) is `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`. Configuration remains CUDA `cuda:0`, FP16, batch size 1, max_length 640, CLS pooling, dimension 1024, dense output only. Sparse and ColBERT output are disabled. Truncation is prohibited. Official L2-normalized output is converted to float32 and L2-normalized again using the existing project operation before storage/scoring.

The notebook requires Linux Python 3.12 and creates an isolated venv under `/content/wo_bge_m3`. Hugging Face, pip, and temporary paths remain under that cloud directory. It uses the [official PyTorch CUDA 12.6 index](https://pytorch.org/get-started/previous-versions/), protects the torch version with a constraint, dry-runs dependencies, rejects a torch replacement, installs, and runs `pip check` before model loading. No install/download was executed on the laptop in this milestone.

Pinned dependencies, matching the inspected existing ML environment:

| Package | Version |
|---|---|
| torch | 2.12.1+cu126 |
| FlagEmbedding | 1.4.2 |
| transformers | 4.57.6 |
| tokenizers | 0.22.2 |
| sentence-transformers | 5.2.0 |
| peft | 0.18.1 |
| datasets | 5.0.1 |
| accelerate | 1.15.0 |
| sentencepiece | 0.2.2 |
| protobuf | 7.36.2 |
| numpy | 2.5.3 |
| psutil | 7.2.2 |
| safetensors | 0.8.0 |
| huggingface-hub | 0.36.2 |
| fsspec | 2026.6.0 |
| ir-datasets | 0.6.3 |

Actual Linux dependency resolution and GPU compatibility remain untested until the user executes the notebook. Other transitive dependencies are resolver-selected; the complete actual environment lock is recorded in the returned manifest. Pin mismatch or resolution failure stops execution, without selecting an alternative model/build.

The exact installed FlagEmbedding 1.4.2 source/API was inspected locally. The runtime verifies the model repository commit, downloads only required files with pinned `snapshot_download`, checks every file hash, then passes the verified local checkpoint directory to `BGEM3FlagModel`. It does not assume a constructor `revision` argument. [Hugging Face documents revision and file selection for snapshot downloads](https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download).

Inference uses the official model forward path with explicit dense-only flags. It avoids the wrapper's automatic batch-size fallback: one input per call, no automatic retry or alternative model. Model loading time and each embedding time are recorded separately, not presented as retrieval benchmark latency. GPU allocated/reserved peaks are measured; process RSS is sampled at boundaries and explicitly is not a continuously measured RAM peak.

## Exchange and import validation

The cloud output ZIP contains `manifest.json` and exactly two named float32 NPY vectors. COMPLETE is written only after both vectors pass validation. The manifest records snapshot/serializer/inference identity, exact input mappings, tokenizer and checkpoint hashes, runtime/code hashes, environment lock, device/capability, precision, UTC creation time, loading/inference times, memory observations, vector checksums, and its own deterministic fingerprint.

The CPU-only local importer:

1. Revalidates current V1/V2 snapshots, indices, reuse eligibility, serialized inputs, tokenizer/model identity, runtime identity, and returned manifest/checksums.
2. Rejects wrong IDs, text hashes, model/revision/config, snapshot, dependency identity, missing/duplicate records, incomplete or corrupted artifacts, extra ZIP entries, non-finite vectors, zero/non-unit norms, wrong dimensions/dtype, and synthetic artifacts at the production boundary. ZIP contents are bounded and read without filesystem extraction; NPY loading disables pickle.
3. Reuses the existing verified 369 V1 vectors byte-for-byte, inserts the two verified cloud vectors in canonical V2 order, and delegates `(371, 1024)` assembly, checksum/readback, and atomic completion to the existing V2 publisher. Existing V1 remains untouched; an existing R3 V2 target is not overwritten.

The resulting exact-cosine index retains existing scoring semantics. The local dependency identity inherited by the existing index format describes the 369 inherited vectors and local validators, not the cloud execution. Each of the two new vector records explicitly carries actual cloud environment, runtime/checkpoint/input/output hashes and exchange provenance; mixed hardware is marked. Model, revision, text, normalization and format must match, but small floating-point differences can occur across GPUs/libraries. **Bitwise equivalence is NOT TESTED and is not claimed.**

## Offline verification

**129 distinct tests PASS**: 100 ML/retrieval tests in 37.188 s and 29 ingestion/versioned pipeline tests in 10.544 s. The 100 include nine new portable test methods with multiple rejection cases; the targeted nine also passed separately.

Coverage includes valid synthetic import; snapshot, revision, input hash, tokenizer/config/dependency and precision mismatches; corrupted/incomplete/missing/duplicate/extra archive entries; dimension/dtype/NaN/Inf/zero/non-unit vectors; and synthetic artifact rejection by production validation. Synthetic integration uses the actual 371-ID/text mapping but synthetic vectors, exercising real import/publication/readback in temporary directories. It verifies all 369 reused rows remain byte-identical, the two new rows occupy their correct positions, V1 stays unchanged, and mixed provenance is retained. These are offline fixtures, not actual model outputs.

Notebook validation: JSON structure, cell IDs, and AST parsing of all five code cells PASS. All execution counts are null and outputs empty. No Colab execution or full `nbformat.validate` was performed.

Baseline integrity verification: all **652 existing tracked-by-audit files** retain their original SHA-256, including protected V1/V2 research files, query/qrels assets, source code/configuration, existing indices and run evidence. This is a filesystem hash baseline, not a Git claim; this checkout has no Git repository. V2 snapshot SHA-256 remains `6658fee4737c0d2fa725ee31cb647ec638de350fc2ccfe669999847ac2331b07`; fingerprint remains the value above. R1/R2 V2 remain COMPLETE and the real R3 V2 directory has not been published.

## Manual execution instructions

1. Open `experiments/portable/v2_bge_m3/bge_m3_v2_colab.ipynb` in Google Colab. Select a GPU runtime. The first cell checks Python 3.12 and GPU availability; stop if requirements fail.
2. Run cells sequentially. Upload **only** `experiments/portable/v2_bge_m3/input_package.zip` when prompted. Do not upload source documents, queries, qrels or corpus vectors. The ZIP contains the two researcher-composed operational inputs needed for this task.
3. Allow the notebook to install its isolated cloud dependencies and download the official pinned checkpoint on Colab. Any failed check stops the run. Do not change pins, input text, precision, length or model to bypass an error.
4. After both embeddings and manifest validation succeed, download **`colab_embeddings.zip`**. Save it locally as `D:/ModelCache/wo-retrieval-benchmark/colab_exchange/v2/colab_embeddings.zip`. Preserve the original input ZIP and notebook.
5. Return the output path and notebook execution evidence to Codex for review. A COMPLETE cloud exchange means two outputs exist; it does not yet mean the local R3 V2 index is complete.
6. For the later authorized local import, run from repository root:

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
.venv-ml/Scripts/python.exe -B -m wo_retrieval.portable_embeddings import --input experiments/portable/v2_bge_m3/input_package.zip --output D:/ModelCache/wo-retrieval-benchmark/colab_exchange/v2/colab_embeddings.zip
```

For this CLI, `--output` denotes the **returned Colab ZIP being imported**, not a destination index path. The existing version binding fixes the destination to `experiments/indexes/v2_ai_corrected/R3`. Import does not require BGE-M3 loading or GPU inference. Only a successful real import plus index readback can promote R3 V2 to COMPLETE. Do not start retrieval effectiveness evaluation as part of this step.

## Remaining limits and stop point

The package is ready for manual Colab execution and review. Actual cloud installation, model loading, inference, download of results, real import, and cross-device numerical equivalence remain untested. Cloud runtime availability, dependency wheels and GPU capacity can still block execution; failures must be reported without silently changing the contract. Local memory thresholds and safety controls remain unchanged. No local GPU test, benchmark, corpus re-embedding, real index completion, installation, model download, commit, push, PR or deploy occurred. STOP after preparation.
