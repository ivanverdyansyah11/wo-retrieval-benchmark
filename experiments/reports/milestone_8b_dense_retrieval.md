# Milestone 8B — BGE-M3 Dense Vector Retrieval

**PASS — Milestone 8B selesai secara teknis untuk pilot.** Canary20/20, full corpus371/371 dan tiga query sanity PASS pada satu controlled low-margin run. Shape371×1024, finite, normalized, tanpa missing/duplicate mapping atau truncation. R3 siap untuk review sebelum Milestone8C; R4/Hybrid belum diimplementasikan dan tidak diotorisasi.

Snapshot WO-CORPUS-V1-DRAFT-PILOT-001, corpus v1-draft, pending_practitioner_validation. Development queries tetap draft_pending_expert_review. Ini hasil indexing/sanity teknis, bukan benchmark efektivitas atau validasi praktisi.

## 1. Scope, authorization dan files

Pengguna memberikan persetujuan eksplisit melalui attachment4ec92dbb-f84d-41c8-95b6-08df9e3450f6 untuk satu controlled low-margin full-corpus run, dengan canary terlebih dahulu, tanpa retry/CPU fallback. Ini pengecualian satu run; benchmark protocol dan default resource gate **tidak berubah**.

- Updated: experiments/reports/milestone_8b_dense_retrieval.md dan milestone_8b_dense_audit.json.
- Updated: README.md satu kalimat status R3 agar selaras dengan hasil aktual; command/default gate tidak diubah.
- Semua source code, tests, pyproject, konfigurasi, R1/R2 indexes dan environment packages existing tetap identik.
- Driver orchestration satu run di luar repository, memakai komponen 8B existing:

D:\ModelCache\tmp\wo-m8b-controlled\run.py

Driver SHA-256: 070a58bb92a5be9a45786e17e55a929d3c9f4793b1860422fea22c2f535b8da3. Ia memilih canary, menjalankan existing BGEEncoder/embed_sequential/load_vectors/DenseRetriever dan mengumpulkan resource; tidak membuat ulang serializer/scoring/index architecture.

Run evidence:

D:\ModelCache\wo-retrieval-benchmark\runs\20261008T173150591129Z-controlled

Folder tersebut berisi run.json/events.jsonl/paging.jsonl. Working baseline/test logs di D:/ModelCache/tmp/wo-m8b-controlled. Artifact derived R3 berada pada D: cache; tidak menyalin checkpoint ke repository.

## 2. Environment dan architecture

Existing .venv-ml, Python3.12.14, Windows11Pro, i7-7700HQ, RAM16GB, GTX1050 4GB. CUDA availability actual True; runtime12.6; compute capability6.1 dan sm_61 tersedia. NVIDIA driver581.80. Tidak ada instalasi/download/reinstall/driver change. Akses package memakai session-local PYTHONPATH=src, tanpa editable install; ingestion .venv dipertahankan.

| Dependency | Actual version |
|---|---|
| FlagEmbedding | 1.4.2 |
| huggingface-hub | 0.36.2 |
| numpy | 2.5.3 |
| psutil | 7.2.2 |
| safetensors | 0.8.0 |
| sentencepiece | 0.2.2 |
| tokenizers | 0.22.2 |
| torch | 2.12.1+cu126 |
| transformers | 4.57.6 |

Pip check ML dan ingestion PASS. ML check tanpa PYTHONPATH agar source egg-info ingestion tidak ikut terbaca; pemisahan environment ini sudah dicatat pada8A. HF_HOME/HF_HUB_CACHE/TORCH_HOME/PIP_CACHE_DIR/TMP/TEMP di D:, offline flags aktif. Tidak ada network model download.

Foundation existing dipakai utuh: shared prepare/serializer/snapshot verification, RetrievalResult schema, BGEEncoder official dense-only forward, float32 L2 normalization, sequential checkpointing dan exact cosine DenseRetriever. Common result tetap method_id/chunk_id/document_id/rank/score/snapshot_id. No query instruction, rewriting, reranking, sparse atau ColBERT output.

## 3. Model dan shared input parity

BAAI/bge-m3 revision5617a9f61b028005a4858fdac845db406aefb181; local checkpoint D:/ModelCache/huggingface/hub/models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181. Semua12 local file hashes diverifikasi sebelum/sesudah. Checkpoint SHA-256 b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38.

CUDA cuda:0, FP16 inference, batch1, max_length640 termasuk special tokens, dimension1024. Official CLS/L2, eval+torch.inference_mode; direct official forward menghindari encode-wrapper OOM retry. Output di-cast float32 dan L2-normalized lagi sebelum storage/scoring. Model **dimuat satu kali**; canary, seluruh corpus dan queries memakai instance yang sama. Post-run metadata audit tidak memuat weights.

R1/R2/R3 memakai371 chunk ID dan serialized text identik. Title/heading/category dedup mengikuti wo_operational_context_dedup_v1. Seluruh operational body/XLSX Sheet/Header/Row context dipertahankan, guide_context audit-only. Administrative provenance/status/reviewer/evidence tidak diinjeksikan. Title318,heading63,category371 emitted; empty/duplicate serialized documents0.

- Universe hash: 6bc63ce997da6e80df7b954a476dc46f959bf339986e8c28d389aa8f28f8d6c3.
- Serialized inputs hash: dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c.
- Serialization+actual token-count fingerprint tetap: 2f4e59835ad4cf81e84f60a5177b6b721c821ddc23970b484de01dd23613ef37.

## 4. Actual tokenizer audit

XLMRobertaTokenizerFast lokal, add_special_tokens=True,truncation=False,padding=False. Semua input dicek sebelum forward; token count cap640 berlaku sama untuk corpus/query. Tidak ada re-chunking atau silent truncation.

| Statistic | Actual |
|---|---:|
| chunks | 371 |
| min | 83 |
| median | 136 |
| mean | 194.33962264150944 |
| p95_nearest_rank | 497 |
| max | 573 |
| max_length | 640 |
| truncation_count | 0 |

## 5. Preflight dan safety

RAM awal 6.120GiB; tepat sebelum weights loading 5.363GiB. Persetujuan low-margin dicatat; existing gate --approved-low-memory>=5GiB terpenuhi. Tidak menurunkan/mengedit default6GiB pada protocol atau source code.

| Resource | Initial | Before weights |
|---|---:|---:|
| Available RAM GiB | 6.120 | 5.363 |
| Commit headroom GiB | 12.365 | 11.327 |
| Memory load percent | 61 | 66 |
| C: free GiB | 12.967 | 12.967 |
| D: free GiB | 846.936 | 846.936 |
| GPU used / free MiB | 0 / 4007 | 0 / 4007 |

Satu GPU model process, lock existing, tanpa parallel inference worker. Watchdog run-local dibuat lebih konservatif: available RAM<1024MiB,commit headroom<1GiB atau memory load>=97% bertahan1s menghentikan hanya proses sendiri. Health check synchronous sebelum canary/queries dan transisi stage menghentikan jika available<1.25GiB. Konfigurasi permanen tidak berubah. Existing checkpoint every valid row dipakai, lebih sering dari contoh every25 yang diminta.

Windows PDH mengukur Memory/Page Reads/sec dan Pages Input/sec setiap kira-kira1s. Heuristic stop tambahan: available<1.5GiB bersamaan Page Reads/sec>1000 dan Pages Input/sec>10000, sustained2s. System counters mencakup file-backed hard faults, sehingga tidak dipakai sendirian sebagai bukti pagefile swapping. Tidak ada safety-stop/OOM/driver error/automatic retry. Tidak ada aplikasi lain dimatikan atau cache pengguna dihapus.

## 6. Canary actual — 20/20 PASS

Selection prospektif deterministik: untuk tiap format DOCX/PDF/TXT/XLSX, sort(actual token length,chunk_id); ambil posisi round(q*(N-1)) untuk q=0,.25,.5,.75,1. Lima per format, total20 unique. Selection mencakup global min83 dan max573 serta kuartil/median per format. Tidak berdasarkan hasil retrieval.

| Chunk ID | Format | Actual tokens | Inference pipeline seconds | Result |
|---|---|---:|---:|---|
| WO-DOC-023-C006 | DOCX | 99 | 3.379610 | PASS |
| WO-DOC-045-C008 | DOCX | 122 | 0.067313 | PASS |
| WO-DOC-002-C006 | DOCX | 136 | 0.089583 | PASS |
| WO-DOC-028-C006 | DOCX | 201 | 0.118319 | PASS |
| WO-DOC-001-C002 | DOCX | 281 | 0.145420 | PASS |
| WO-DOC-044-C015 | PDF | 95 | 0.070894 | PASS |
| WO-DOC-021-C007 | PDF | 116 | 0.073485 | PASS |
| WO-DOC-017-C002 | PDF | 124 | 0.066461 | PASS |
| WO-DOC-021-C002 | PDF | 171 | 0.091329 | PASS |
| WO-DOC-050-C009 | PDF | 241 | 0.121591 | PASS |
| WO-DOC-041-C008 | TXT | 83 | 0.069082 | PASS |
| WO-DOC-041-C005 | TXT | 98 | 0.067100 | PASS |
| WO-DOC-041-C003 | TXT | 110 | 0.068027 | PASS |
| WO-DOC-012-C003 | TXT | 121 | 0.066135 | PASS |
| WO-DOC-012-C002 | TXT | 202 | 0.121654 | PASS |
| WO-DOC-008-C006 | XLSX | 209 | 0.128248 | PASS |
| WO-DOC-040-C006 | XLSX | 405 | 0.209625 | PASS |
| WO-DOC-048-C002 | XLSX | 467 | 0.266399 | PASS |
| WO-DOC-026-C002 | XLSX | 498 | 0.268754 | PASS |
| WO-DOC-042-C005 | XLSX | 573 | 0.281096 | PASS |

Seluruh canary shape(1,1024), finite, no NaN/Inf, L2 norms valid, tanpa truncation. Canary total 5.923868s termasuk first-forward/kernel warm-up, validasi/resource probes/diagnostic writes. Tidak ada separate artificial warm-up atau pengukuran throughput.

Canary vectors tidak di-seed ke checkpoint arbitrary positions. Setelah canary PASS, full corpus diproses ulang dalam urutan frozen chunk_id ascending untuk menjaga existing contiguous recovery mechanism. Total forward aktual:20 canary+371 corpus+3 queries=394; index final tetap371 unique rows. Tidak ada model reload.

## 7. Full corpus result

| Check | Actual |
|---|---|
| Full indexing | PASS / COMPLETE |
| Embedded / missing / duplicate chunk IDs | 371 / 0 / 0 |
| Vector shape / dtype | (371,1024) / float32 |
| All finite / NaN / Inf | True / 0 / 0 |
| L2 norm min / max | 0.9999998808 / 1.0000001192 |
| Actual maximum input / truncation count | 573 / 0 |
| CPU fallback | NOT RUN |

Existing embed_sequential mempersist setiap valid row sebagai atomic NPY+checksum dan progress INCOMPLETE. Final staging hanya dipublish COMPLETE setelah full mapping/hash/shape/finite/norm dan snapshot gate PASS. Full cache kemudian di-load kembali dan checksums/mapping divalidasi. .incomplete checkpoint log tetap dipertahankan untuk audit/recovery; ia tidak dipakai retrieval. Tidak ada resume pada run ini (resumed rows0).

## 8. Timing actual, bukan performance benchmark

| Stage | Seconds | Scope |
|---|---:|---|
| Model loading | 4.474977 | CPU checkpoint construction + CUDA transfer/synchronize; excludes FlagEmbedding import |
| Canary20 | 5.923868 | includes first-forward warm-up and diagnostics |
| Corpus embedding pipeline cumulative | 41.027154 | per-row tokenization/padding/H2D/forward/sync/float32/L2; not kernel-only |
| Full index construction | 46.238161 | 371 embeddings + per-row checkpoints + finalization + verified reload |
| Driver total wall | 81.247241 | preflight/hash/tokenizer/model loading/canary/index/queries/cleanup |

Driver wall excludes Python startup/initial foundation imports before timer, separate post-run CLI audit/tests/reporting. Full-index stage excludes earlier full-corpus tokenizer audit/serialization preparation; do not call this46.238s an end-to-end cold indexing benchmark. Model loading is a single observed value after local checkpoint SHA verification warmed filesystem cache; not cold-disk latency or evidence of improvement versus historical smoke. No statistical latency/throughput comparison or method superiority claim.

## 9. Measured resource peaks

| Measurement | Actual |
|---|---:|
| Process peak Windows working set, OS high-water | 4,725,547,008 bytes / 4.401GiB |
| Process peak RSS, sampled | 4,026,515,456 bytes / 3.750GiB |
| Minimum available system RAM, sampled | 2,754,572,288 bytes / 2.565GiB |
| Minimum commit headroom, sampled | 7.971GiB |
| Peak torch GPU allocated | 1106.36MiB |
| Peak torch GPU reserved | 1136.00MiB |
| Sampled max GPU device used | 1195MiB |
| Max system Page Reads/sec | 669.664 |
| Max system Pages Input/sec | 2667.943 |

RAM monitor 342 samples, nominal0.2s; nvidia-smi nominal2s. PDH 77 samples, nominal1s. Synchronous probe overhead can lengthen intervals. OS working-set high-water exceeds sampled RSS because short peaks can be missed. GPU device-wide usage includes context/driver overhead and is not process-attributed memory. All peaks include model loading/canary/full corpus/queries, not isolated per-stage comparisons.

No heavy-paging stop signal was observed; these counters do not prove absence of paging. After cleanup while process alive, CUDA context may remain; independent nvidia-smi after process exit observed0MiB used/4007MiB free. No repeated driver error or system instability was observed during this bounded run.

## 10. Exact search index / metadata / storage

Complete cache:

D:\ModelCache\wo-retrieval-benchmark\R3\7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f

| File | Logical bytes | Allocated bytes | SHA-256 |
|---|---:|---:|---|
| manifest.json | 4433 | 8192 | bc96099725d17dca4e45c0b10ec3204fd56bb91f5f7349843f6a61275f1a5e1b |
| rows.json | 62686 | 65536 | a2841c513395e16c053427fdad8a3d3fa2438bcd041a7c1461ad4a167ffaee16 |
| vectors.npy | 1519744 | 1523712 | 6774becce519fcaa822807ddf20b334197a8a0c41f30c3d7de8f29fe3baeb5e5 |

Final exact-search index total **1,586,863 logical bytes / 1,597,440 allocated NTFS bytes**. NPY payload1,519,616 bytes plus header; index size includes mapping/manifest, excludes shared checkpoint, diagnostics and recovery artifacts. Separate retained incomplete/checkpoint folder logical size 1,673,623bytes. Allocated bytes measured with Windows FileStandardInfo.AllocationSize.

Identity/fingerprint is directory key7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f. Manifest records snapshot/hash, frozen chunk hash, model revision/file hashes, serializer/input hashes, precision/dimension/cap/device/batch, normalization, exact NumPy backend, dependency/implementation hashes and row-mapping hash. Each vector links chunk/document/retrieval-text hash/token length via rows.json and snapshot via manifest.

Read-only production CLI audit PASS after process exit: checksums, identity, every row/text/token mapping, shape/finite/norm/snapshot verified; no neural weights loaded. Corrupt/incomplete/mismatched index rejection remains covered by unit fixtures. No ANN/vector database/FAISS dependency added. Exact float32 normalized inner product includes all371 finite candidates, with unrounded score-descending/chunk_id-ascending ties, rank1-based.

## 11. Retrieval sanity actual

Prospectively selected first existing development query per style:001/007/013, identical selection rule to8A. All remain DRAFT. Same loaded encoder, no paraphrase/instruction/expansion/reranking/query cache. Each returned five unique valid IDs, finite scores, correct ranks and common schema; source file/locator matched frozen rows. Full float scores and locators in audit JSON. Table scores rounded only for display. No relevance labeling or evaluation metrics.

### WO-DEV-001

Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim?

Actual tokens 23; observed single-call pipeline 0.033960s, not benchmark latency.

| Rank | Chunk | Document | Cosine score |
|---:|---|---|---:|
| 1 | WO-DOC-006-C002 | WO-DOC-006 | 0.579380273819 |
| 2 | WO-DOC-006-C001 | WO-DOC-006 | 0.572127938271 |
| 3 | WO-DOC-006-C003 | WO-DOC-006 | 0.563765645027 |
| 4 | WO-DOC-006-C004 | WO-DOC-006 | 0.559484601021 |
| 5 | WO-DOC-034-C005 | WO-DOC-034 | 0.537702918053 |

### WO-DEV-007

Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru?

Actual tokens 22; observed single-call pipeline 0.032315s, not benchmark latency.

| Rank | Chunk | Document | Cosine score |
|---:|---|---|---:|
| 1 | WO-DOC-001-C006 | WO-DOC-001 | 0.567663431168 |
| 2 | WO-DOC-046-C003 | WO-DOC-046 | 0.5367847085 |
| 3 | WO-DOC-005-C001 | WO-DOC-005 | 0.498578906059 |
| 4 | WO-DOC-005-C006 | WO-DOC-005 | 0.498212665319 |
| 5 | WO-DOC-034-C001 | WO-DOC-034 | 0.477972120047 |

### WO-DEV-013

Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?

Actual tokens 30; observed single-call pipeline 0.034744s, not benchmark latency.

| Rank | Chunk | Document | Cosine score |
|---:|---|---|---:|
| 1 | WO-DOC-024-C006 | WO-DOC-024 | 0.665811479092 |
| 2 | WO-DOC-024-C003 | WO-DOC-024 | 0.652037858963 |
| 3 | WO-DOC-014-C004 | WO-DOC-014 | 0.643602907658 |
| 4 | WO-DOC-014-C002 | WO-DOC-014 | 0.640089511871 |
| 5 | WO-DOC-014-C003 | WO-DOC-014 | 0.63969707489 |

## 12. Tests dan integrity

Accepted implementation suite sebelumnya:60 unique tests PASS (R3 16,lexical14,ingestion25,protocol5); source/tests tidak berubah pada continuation ini. Post-run actual rerun:16 R3 PASS(1.053s),5 protocol PASS(0.007s). Real checks baru:canary20,full371,3 query sanity,read-only complete index CLI audit dan protected/environment/model verification PASS. Tidak mengklaim60 tests diulang seluruhnya pada continuation ini.

Baseline136 existing repository files: hanya dua report dan satu kalimat README berubah. Seluruh existing source code/tests/pyproject, source corpus57 files/50 documents, canonical documents, frozen chunks, pilot, snapshot/protocol, draft queries/provenance/reviewer workbook, R1/R2 index/code byte-identical. Environment .venv1,038 dan .venv-ml26,682 files mempertahankan path/size/mtime_ns tanpa file baru (pycache excluded); bukan full byte rehash semua environment DLL. Seluruh12 local model/tokenizer files kembali cocok SHA-256. Pip check kedua environment PASS.

| Protected artifact | SHA-256 unchanged |
|---|---|
| data/chunks/chunks.jsonl | 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0 |
| data/processed/documents.jsonl | 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01 |
| data/source_corpus/corpus_manifest.json | 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f |
| experiments/configs/pilot.toml | 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26 |
| pilot_snapshot.json | 279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e |

Snapshot aggregate fingerprint: 7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40.

Git repository tidak tersedia; baseline SHA-256 dipakai untuk audit. Tidak ada commit/push/PR/deploy, query/qrels/main generation, benchmark score atau perubahan frozen corpus.

## 13. Error, limitation dan next milestone

No CUDA error/OOM/retry/CPU fallback. Satu tokenizer advisory: fast tokenizer lebih efisien memakai combined call daripada separate encode+pad. Existing two-step path dipertahankan untuk explicit no-truncation validation; tidak tuning/mengubah inference code demi timing.

Historical previous attempt berhenti sebelum weights loading pada5.321GiB/default6GiB; itu NOT RUN, bukan CUDA/model failure. Hasil controlled run yang disetujui ini menggantikannya. Historical gate summary disimpan dalam audit JSON.

R3 complete untuk pilot pada environment yang dideklarasikan, bukan jaminan repeated-run/concurrent stability atau portability bitwise lintas device/library. CPU model FP32, sparse/ColBERT, performance benchmark dan effectiveness evaluation tetap NOT RUN. Low-margin authorization hanya untuk satu run ini; default resource gate tetap berlaku pada run berikutnya.

Milestone8C dapat dipersiapkan untuk review pengguna, dengan R1/R2/R3 snapshot/serialization yang sama. R4/Hybrid/RRF **jangan diimplementasikan sebelum review/otorisasi terpisah**. Corpus/query masih pending practitioner review; tidak ada ground-truth atau retrieval-superiority claim.

**STOP setelah R3 selesai.**
