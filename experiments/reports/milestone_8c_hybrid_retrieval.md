# Milestone 8C — Hybrid Retrieval BM25 + BGE-M3 Dense + RRF

**Implementasi dan index readiness PASS; GPU technical smoke NOT RUN: final controlled attempt Milestone8C.2 berhenti pada gate5GiB. Milestone 8C belum dinyatakan selesai end-to-end.**

Snapshot `WO-CORPUS-V1-DRAFT-PILOT-001`: 50 operational documents, 371 frozen chunks, `pending_practitioner_validation`. Development queries tetap `draft_pending_expert_review`. Tidak ada benchmark score atau klaim keunggulan Hybrid.

## 1. Scope dan minimal changes

Latest continuation **Milestone8C.2**, 9 Oktober2026 Asia/Singapore: satu percobaan baru disetujui hanya jika semua resource gate terpenuhi. Run memakai existing approved-low-memory flag dan approval note, tanpa code/threshold/config/index changes. Pada continuation ini hanya dua laporan Milestone8C diperbarui; changes di bawah adalah history implementation sebelumnya.

Pengguna memberi persetujuan eksplisit pada 9 Oktober 2026 (Asia/Singapore) untuk **satu controlled low-memory smoke** WO-DEV-001/007/013. Ini bukan perubahan permanen protokol dan tidak memakai ulang persetujuan satu-run8B. Historical default-gate attempt disimpan dalam audit JSON.

Updated existing files:

- `src/wo_retrieval/hybrid/cli.py`: `--approved-low-memory`, `--approval-note`, meneruskan bool ke existing gate; default6GiB/approved5GiB. Run evidence mencatat approval, actual gate dan effective safety policy. Approval note wajib bila flag dipakai; operator tetap harus mempunyai izin manusia nyata.
- `tests/test_hybrid_retrieval.py`: dua tes tambahan untuk real gate6vs5GiB, evidence, CLI propagation, required approval note, 2GiB stop dan no config mutation.
- `README.md`: dokumentasi penggunaan flag berizin dan safety policy.
- Dua report Milestone8C ini.

R2/R3 source dan seluruh indices tidak berubah. RRF/scoring/serializer/model/retrieval parameters tidak berubah. Safety policy hanya salinan in-memory: low-memory flag memakai stop_available_ram_mib=2048 dan stop_sustained_seconds=0, sehingga watchdog menghentikan own process pada sampel unsafe pertama. Existing commit/load limits tetap berlaku dan menjadi immediate juga. Checks sinkron sebelum/setelah tiap query memakai policy sama. TOML tetap identik.

## 2. RRF dan candidate policy

`RRF(d) = 1/(60 + dense_rank(d)) + 1/(60 + bm25_rank(d))` jika BM25 eligible; kontribusi BM25 nol bila absent. Rank mulai 1. Equal weights; tidak memakai magnitude raw score, score normalization atau weighted fusion.

- Dense: semua 371 finite scores termasuk cosine nol/negatif; tidak ada top-100 cutoff.
- BM25: seluruh score >0, bukan top-K final; nol/negatif dibuang sebelum eligible rank assignment. Tidak ada pseudo-rank/tail filling.
- Semua chunk eligible lewat Dense. Jika BM25 tidak menghasilkan kandidat, RRF mengikuti Dense ordering.
- Component rankings divalidasi (method, snapshot, mapping, rank, finite, uniqueness, ordering); full Dense universe wajib lengkap.
- Final sorting: score descending **tanpa pembulatan**, lalu chunk_id ascending Unicode codepoint. Top-K diterapkan setelah fusion. Dictionary/set iteration tidak menentukan ranking.

## 3. Interface, diagnostics dan CLI

`HybridRetriever.retrieve(query, top_k) -> list[RetrievalResult]`. Schema: method_id=R4, chunk_id, document_id, rank, score, snapshot_id. Empty/whitespace query returns []; invalid/noninteger/bool/zero/negative top_k ditolak. Query NFC/newline/outer-whitespace normalized sekali, teks yang sama dikirim ke R2 dan R3. Tidak ada query instruction/expansion.

`retrieve_with_diagnostics` mengembalikan common results, breakdown terpisah, dan component rankings yang sudah dihitung; tidak memanggil Dense kedua kali untuk diagnostics. CLI output query memisahkan results/diagnostics/component_top5. CLI memakai pola argparse existing tanpa dependency/install/entry-point refresh.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OMP_NUM_THREADS = '4'
$env:OPENBLAS_NUM_THREADS = '4'
$env:MKL_NUM_THREADS = '4'
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.hybrid.cli audit
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.hybrid.cli retrieve --query "Bagaimana koordinasi vendor sebelum acara?" --top-k 5
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.hybrid.cli smoke
# Hanya sesudah explicit human approval; bukan izin untuk retry otomatis:
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.hybrid.cli smoke --approved-low-memory --approval-note "referensi izin manusia untuk satu run"
.\.venv-ml\Scripts\python.exe -B -m unittest discover -s tests -p test_hybrid_retrieval.py -v
```

`audit` memverifikasi local checkpoint dan tokenizer tanpa neural weights. Tidak ada build/re-index command. GPU commands memuat satu model, CUDA FP16 batch1 cap640, tanpa truncation, retry atau CPU fallback. Default gate existing tetap 6 GiB sebelum weights loading. Flag berizin memakai existing5GiB gate dengan immediate stop below2GiB, tanpa menonaktifkan critical safety checks. Error dan resource evidence disimpan di D: runs folder; corrupt/stale/incomplete index ditolak, tidak diperbaiki otomatis.

## 4. Verified index reuse dan reproducibility

R2 dimuat melalui existing lexical.load: completion, snapshot, config/code/dependency identity, artifact checksums, serialized row equality dan BM25 state diverifikasi. R3 dimuat melalui existing model_files/token_audit/cache_identity/load_vectors: pinned checkpoint/tokenizer hashes, model revision/config/environment/code fingerprints, COMPLETE status, vector/row hashes, mapping, shape, finite dan norm diverifikasi. Tidak ada corpus forward atau embedding/index write.

Cross-index checks: snapshot ID/SHA/fingerprint, protocol SHA, serializer version/policy hash, universe hash, serialized-input hash dan chunk/document/text-hash row mapping. Exact Dense index tetap 371×1024 float32 normalized; BM25 parameter existing tetap k1=1.5,b=0.75,epsilon=0.25.

| Identity | Value |
|---|---|
| snapshot_fingerprint | `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40` |
| bm25_index_fingerprint | `6311e3dde68c96f4f84a1601a894946af5abe655d5656d1ed93ceffbf2874120` |
| dense_index_fingerprint | `465cf54c7fa3aadaccbb3090279762bd27f24817360c749ede4315f1f34abc72` |
| serialized_inputs_hash | `dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c` |
| universe_hash | `6bc63ce997da6e80df7b954a476dc46f959bf339986e8c28d389aa8f28f8d6c3` |
| protocol_sha256 | `dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300` |
| model_revision | `5617a9f61b028005a4858fdac845db406aefb181` |
| R4 identity fingerprint | `8b156b009525821d78516e765a788fb1064a33790a3bca088b07e740a475fb31` |

Index fingerprints di atas adalah SHA-256 canonical sorted-key compact JSON complete manifest, termasuk artifact hashes. R4 identity juga mencatat parameter/policy/tie handling, dependency versions dan code/config hashes. UTC timestamp berada di luar stable identity fingerprint. Tidak perlu R4 embedding atau fusion index baru; lightweight metadata tercatat pada run/audit JSON.

Dependencies actual:

| Package | Version |
|---|---|
| FlagEmbedding | 1.4.2 |
| huggingface-hub | 0.36.2 |
| joblib | 1.6.0 |
| numpy | 2.5.3 |
| psutil | 7.2.2 |
| rank-bm25 | 0.2.2 |
| safetensors | 0.8.0 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| sentencepiece | 0.2.2 |
| threadpoolctl | 3.7.0 |
| tokenizers | 0.22.2 |
| torch | 2.12.1+cu126 |
| transformers | 4.57.6 |

## 5. Validation dan mathematical example

**21 unique tests PASS pada8C.2**: R416 dan protocol5. Previous51 relevant regression tests (R416,lexical14,Dense16,protocol5) PASS pada8C.1; lexical/Dense tidak diulang pada8C.2 karena source/index/config tetap byte-identical. Ini bukan klaim51 tes dijalankan ulang pada8C.2. Historical validation berikut berasal dari continuation sebelumnya: R4 juga PASS16 sebelum attempt. Full74-suite sebelumnya termasuk25 ingestion/chunking masih historical;25 pipeline tests tidak diulang karena implementasinya tidak berubah. Tests memakai `.venv-ml`; tidak ada package install/upgrade. Mathematical tests tidak memerlukan GPU/model weights. Regresi cache menggunakan synthetic tiny fixtures di temporary directories, bukan frozen corpus re-embedding/indexing. Test log: `D:/ModelCache/tmp/wo-m8c-low/post_tests.log`.

Coverage: one-based formula, differing rankings, both/Dense-only membership, BM25 zero/negative, Dense zero/negative cosine, ties, input row permutation, full371 candidates, no duplicates, same query, universe/fingerprint/mapping mismatch, top-K, empty/invalid input, incomplete/corrupt loader error propagation, CLI validation dan resource stop before loading/no retry. Existing regression tests mencakup corrupt/incomplete artifact checksum rejection dan no source mutation. Actual readiness melalui real loaders PASS.

Contoh **synthetic fixture**, bukan retrieval output development queries atau qrels:

| Chunk | BM25 eligible rank | Dense rank | BM25 contribution | Dense contribution | Total RRF | Final rank |
|---|---:|---:|---:|---:|---:|---:|
| A | 2 | 1 | 0.016129032258064516 | 0.016393442622950821 | 0.03252247488101534 | 1 |
| B | 1 | 3 | 0.016393442622950821 | 0.015873015873015872 | 0.032266458495966696 | 2 |
| C | absent | 2 | 0 | 0.016129032258064516 | 0.016129032258064516 | 3 |

Tes juga menukar BM25 ranks B1/A2 dengan Dense A1/B2 untuk equal-score tie; chunk A mendahului B. Identical component rankings menghasilkan identical RRF scores/ranks; tidak mengklaim bitwise reproducibility neural inference lintas GPU/library atau repeated GPU runs.

## 6. Milestone 8C.2 — Final controlled attempt

**Satu attempt baru di bawah persetujuan8C.2; exit1 pada gate sebelum loading. Tidak ada attempt kedua/retry.** Historical attempt sebelumnya tersimpan di audit JSON.

Run evidence: `D:\ModelCache\wo-retrieval-benchmark\runs\20261008T223835960781Z-R4\run.json`.

Actual R2/R3 readiness PASS: COMPLETE metadata, pinned model revision5617a9f61b028005a4858fdac845db406aefb181, snapshot SHA/fingerprint, serialized-input/universe/model/tokenizer/code/config/dependency identities cocok. Existing model config CUDA FP16,batch1,max_length640 tetap dipakai. RRFk60/full Dense371/BM25positive policy tidak berubah. Tidak ada re-embedding atau re-indexing.

Before-run process inventory tidak menemukan python/pythonw process lain atau NVIDIA compute process. Existing managed GPU lock tetap tersedia; acquisition tidak dicapai karena gate gagal sebelum encoder.load.

| Observation/status | Actual |
|---|---|
| Available RAM before startup, lightweight probe | 5.271 GiB |
| Available RAM at CLI run preflight | 5.131 GiB |
| Available RAM after preparation, before loading | **4.357 GiB** (4678381568 bytes) |
| Approved/default loading gate | 5 / 6 GiB, unchanged |
| Low-memory watchdog | immediate stop below2GiB; existing commit/load guards retained |
| Commit headroom before loading | 12.678 GiB |
| Memory load before loading | 72% |
| Free C: / D: before loading | 12.909 / 846.928 GiB |
| VRAM free / used before loading | 4007 / 0 MiB |
| Peak process working set, preparation only | 0.979 GiB |
| Peak sampled RSS, preparation only | 0.963 GiB |
| Minimum sampled available RAM | 4.351 GiB |
| Monitor samples | 66 |
| Sampled peak GPU device memory used | 0 MiB |
| Actual GPU model loading | **NOT RUN**, prevented by gate |
| GPU inference / RRF contribution checks on actual queries | NOT RUN / NOT RUN |
| Loading time / query latency / PyTorch peak allocated-reserved | NOT MEASURED; no model/query execution |
| Retry / CPU fallback / corpus embedding-indexing | NOT RUN |

Exact stop: `Available RAM below 5 GiB model-loading gate; no model loaded`. Ini bukan model/CUDA inference failure. Initial OS RAM bukan substitusi final after-preparation gate. Semua measurements berasal dari actual run; tidak dibuat top5 atau latency sintetis untuk mengganti hasil yang belum ada.

| Query ID | Smoke | Top-5 and contribution breakdown |
|---|---|---|
| WO-DEV-001 | NOT RUN | NOT AVAILABLE |
| WO-DEV-007 | NOT RUN | NOT AVAILABLE |
| WO-DEV-013 | NOT RUN | NOT AVAILABLE |

Post-attempt independent probe: RAM available5.235GiB (proses inference sudah exit), GPUused0/free4007MiB. Ini bukan readiness untuk attempt baru. Tidak ada weights loading, CUDA allocation, inference, driver/config changes, forced process termination atau retry.

RRF formula/ties/eligibility/full-coverage tests tetap PASS dengan synthetic fixtures. Real-query contribution recomputation/metadata checks belum dieksekusi; tidak menggunakan hasil8B sebagai substitusi. Raw full traceback, approval note, effective policy dan resource monitor tersimpan di audit JSON.

## 7. Integrity verification

Latest8C.2 baseline mencakup 139 existing files. Pada8C.2 hanya dua laporan Milestone8C berubah; seluruh source/tests/config/README dan laporan lain identik; seluruh50 source documents, canonical documents, chunks, pilot, snapshot JSON/MD, protocol Markdown/TOML, R1/R2/R3 source dan indices, queries/provenance/review workbook serta environment lock/config tetap identik. R3 complete manifest/rows/vectors juga identik dengan baseline sebelum attempt dan accepted8B hashes. Git tidak tersedia; SHA-256 baseline digunakan. Existing protected source mutation =0.

| Artifact | SHA-256 |
|---|---|
| `data/source_corpus/corpus_manifest.json` | `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f` |
| `data/processed/documents.jsonl` | `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01` |
| `data/chunks/chunks.jsonl` | `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0` |
| `experiments/configs/pilot.toml` | `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26` |
| `data/validation/pilot_snapshot.json` | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` |
| R3 `manifest.json` | `bc96099725d17dca4e45c0b10ec3204fd56bb91f5f7349843f6a61275f1a5e1b` |
| R3 `rows.json` | `a2841c513395e16c053427fdad8a3d3fa2438bcd041a7c1461ad4a167ffaee16` |
| R3 `vectors.npy` | `6774becce519fcaa822807ddf20b334197a8a0c41f30c3d7de8f29fe3baeb5e5` |

R4 CLI SHA-256 berubah karena dukungan flag:

- Before: `77bde3787faf0a8f89157960fabe470e9b6eaa44c66640d0b1fc6662486cc1d2`
- After: `c6eb1761f160ee9363a00ce72ad5bc5e3370c86a7bed70f5db274acf9b23ccb4`

Run identity mencatat hash after; stable R4 identity fingerprint berubah, sedangkan component index identities tetap sama.

## 8. Limitations dan kesiapan Milestone 8D

Implementasi, mathematical tests, regression dan actual index readiness PASS. **Milestone8C belum selesai end-to-end; Milestone8D belum siap dimulai.** Controlled attempt yang diizinkan telah berhenti pada final5GiB gate; jangan mengulang otomatis atau menurunkan gate lagi.

Persetujuan satu attempt8C.2 sudah digunakan dan berhenti pada gate. Tidak ada percobaan kedua. Minimal continuation setelah review pengguna membutuhkan resource tersedia minimal5GiB **setelah** readiness/import/tokenizer, bukan hanya sebelum memulai Python, beserta persetujuan satu-run baru setelah pengguna meninjau hasil. Tutup aplikasi secara manual bila diperlukan; tidak perlu install/download/model replacement/corpus re-embedding/indexing.

Tidak ada GPU inference/top5 aktual, Recall/MRR/nDCG, tuning, qrels/main queries, sparse/ColBERT, RAG/LLM, commit/push/PR/deploy. Corpus/query masih pending practitioner validation. **STOP setelah pelaporan ini; jangan memulai Milestone8D.**

