# Milestone 9A.8 — V2 lexical index rebuild dan Dense reuse audit

Tanggal: 2026-10-09. **Technical preparation PASS; R3 V2 INCOMPLETE; R4 V2 NOT READY.**

Active development snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.
Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.
Status: **ai_corrected_pilot_not_human_validated**. Dataset sintetis disusun peneliti dan dikoreksi AI; bukan corpus final atau bukti validasi manusia.

## Scope dan preflight

Dibaca: snapshot V1/V2, V1–V2 mapping, laporan 9A.6/9A.7, retrieval protocol Markdown/TOML, shared serializer/tokenizer, lexical fit/build/load, Dense normalization/cache validator, Hybrid dan shared query-vector loaders. Tidak ada perubahan metodologi atau parameter.

Kedua snapshot diperiksa melalui seluruh explicit artifact hashes, aggregate fingerprint dan seluruh 50 source document hashes masing-masing. V2 canonical document universe 50, chunk universe 371, source IDs dan mapping valid. Original 18 query file checksum serta manifest/checksums provenance/qrels V2 PASS. Dataset tetap 684 AI silver judged dan 5.994 unjudged; tidak dibuat judgment atau query baru.

Baseline sebelum perubahan mencakup **635 existing files** dalam `data/`, `experiments/`, `src/`, `tests/`, `scripts/`, root README/pyproject/requirements.lock/.gitignore, serta project cache `D:/ModelCache/wo-retrieval-benchmark`. `__pycache__`, environment trees dan root `data.zip` tidak termasuk baseline; tidak digunakan/diubah. Tidak ada Git repository; pemeriksaan memakai filesystem dan SHA-256.

Semua source modules existing tercakup hash snapshot V2, sehingga tidak diedit. Penambahan dibatasi script persiapan terpisah, satu file tests, derived versioned artifacts, dan laporan ini. Tidak ada instalasi/download.

## Serialization comparison

Shared `wo_operational_context_dedup_v1` dipanggil langsung. Semua 371 serialized texts cocok persis dengan frozen V2 `reports/serialized_inputs.jsonl`. Input dibandingkan terhadap V1 lexical rows, Dense row mapping, dan frozen V1–V2 mapping, bukan hanya kesamaan chunk ID.

| Pemeriksaan | Hasil |
|---|---:|
|Same chunk ID universe dan chunk_id ascending order|371/371|
|Exact serialized texts/hashes identik|369|
|Changed serialized inputs|2|
|Empty lexical inputs|0|
|Duplicate serialized inputs|0|
|Title / heading / category emitted|318 / 63 / 371|
|XLSX chunks / nonempty guide context|63 / 53|
|Jumlah lexical tokens|44.009|

Changed inputs hanya `WO-DOC-024-C003` dan `WO-DOC-027-C009`. Title/heading/category dedup dan body preservation tetap. XLSX Sheet/Header/Row dan operational guidance yang sudah di body dipertahankan; metadata guide_context tetap audit-only. Tidak ada query evidence, qrels, validation ledger atau metadata administratif yang diinjeksikan ke retrievable text. New tests membuktikan metadata tambahan tidak mengubah serializer output; existing tests memeriksa marker XLSX dan dedup lintas format.

Universe hash: `6bc63ce997da6e80df7b954a476dc46f959bf339986e8c28d389aa8f28f8d6c3`.
V1 serialized inputs hash: `dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c`.
V2 serialized inputs hash: `58a95f3183f10398ea1e8f6c9de7b40056d23f7291dfe6570652811bef3faf1c`.
V2 tokenized inputs hash: `34e93e42f26d39ddd89220395dead1cd7c9fa55c681a86846626f318c1360b44`.

## R1 dan R2 V2 indexing

Output baru: `experiments/indexes/v2_ai_corrected/R1/` dan `R2/`. V1 directories tidak ditimpa. Fitter, vectorizer, tokenizer dan ranking functions existing digunakan kembali tanpa monkeypatch atau penggantian algoritma.

| Index | Status | Chunks | Build sebelum validation/publish | Total build + validation + publish | Actual bytes termasuk manifest |
|---|---|---:|---:|---:|---:|
|R1 TF-IDF|COMPLETE, readback PASS|371|0,188764 s|0,335632 s|1.349.687|
|R2 BM25Okapi|COMPLETE, readback PASS|371|0,091487 s|0,228307 s|1.464.567|

Durasi adalah single-run technical indexing observations, bukan retrieval latency atau effectiveness benchmark. Timer build dimulai setelah shared input preparation. Total preparation timer termasuk audit/hash/tokenizer, tetapi tidak startup/import, tercatat 21,254805 s.

R1 tetap unigram, smoothed IDF, float64, L2 dan exact cosine; seluruh parameter lain mengikuti frozen TOML. Readback independen menghitung DF, smoothed IDF `ln((1+371)/(1+df))+1`, term-frequency weights dan L2 normalization untuk membandingkan seluruh matrix.

R2 tetap BM25Okapi `k1=1.5`, `b=0.75`, `epsilon=0.25`. Readback independen membandingkan setiap doc-frequency map, document length, average IDF dan epsilon floor terhadap raw IDF. Ranking positive-score eligibility, unrounded scores dan chunk_id tie-break tetap pada shared LexicalRetriever. Synthetic mathematical/edge-case regression tests PASS.

R1 index fingerprint: `cd1523005bc01d2fdb2b6543b262f727a5c163cf5aca6fc451c34b62ed75843e`.
R2 index fingerprint: `c1409c731d3dc3aa9e6eafcd04c12bd605edceb8c66ba4e1a19847f583eee114`.
Fingerprint masing-masing = digest manifest tanpa field `index_fingerprint`; manifest mengikat V2 snapshot, corpus hashes, unchanged protocol/config/serializer/code/dependencies dan derived artifact checksums. Snapshot fingerprint tidak diganti oleh index fingerprint.

## Version binding dan penggunaan script

`scripts/prepare_v2_indexes.py` memakai in-memory snapshot overlay: manifest/hash/fingerprint/path/status V2. Seluruh bagian config selain snapshot tetap identik dengan frozen protocol. Ia memvalidasi V2 canonical documents secara eksplisit. Shared `prepare()` masih melakukan pemeriksaan tambahan terhadap V1 canonical ID set; isi V1 canonical document tidak pernah dipakai sebagai input index V2. Input text berasal hanya dari V2 chunks.

Existing `wo-retrieve`, R3/R4 ready dan shared offline loaders **tetap default V1**. Indeks V2 dapat diverifikasi/dimuat oleh `verify_index()` dalam script baru, tetapi tidak otomatis dipilih CLI existing. Loader lama menolak stale/mismatched binding; tidak ada fallback diam-diam atau aktivasi V2 global. Ini memisahkan pembuatan indeks yang diotorisasi dari perubahan pipeline berikutnya.

Jalankan dari repository menggunakan `.venv-ml`, `PYTHONPATH=src`, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1`, mode HF offline; cache/temp tetap D:.

```powershell
# Build sudah selesai; command tanpa --verify-only menolak overwrite.
.venv-ml/Scripts/python.exe -B scripts/prepare_v2_indexes.py --v1-dense-index D:/ModelCache/wo-retrieval-benchmark/R3/7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f --verify-only
```

`--verify-only` menghitung ulang input/reuse eligibility dan memvalidasi kedua lexical indexes tanpa menulis file atau memuat neural runtime. Audit artifact sendiri juga telah diperiksa melalui independent readback, termasuk audit fingerprint, seluruh receipts dan plan checksum.

## Dense reuse eligibility

Existing COMPLETE V1 index:
`D:/ModelCache/wo-retrieval-benchmark/R3/7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f`.

Existing `load_components()` memverifikasi V1 snapshot, R2 parity, model file hashes, dependency versions, inference implementation hashes, tokenizer mapping fingerprint, Dense cache identity/directory fingerprint dan vectors/rows checksums. Semua dilakukan tanpa neural initialization. Model checkpoint dibaca streaming untuk hash, bukan di-load sebagai weights.

Model `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`; inference provenance CUDA FP16, batch1; storage float32, dimension1024, max_length640. Normalization tetap official L2 lalu project float32 L2. Seluruh371×1024 vectors finite, unit norm within existing atol1e-5; mapping unique, ordered, matched exact V1 serialized hashes. Model/tokenizer/normalization/precision/storage/dependency/config contracts cocok dengan rencana V2.

Actual local `tokenizers.Tokenizer.from_file` memeriksa panjang input lama/baru dengan special tokens, truncation/padding disabled. File tokenizer.json checksum cocok pinned checkpoint. Old lengths cocok Dense mapping dan V2 lengths cocok frozen tokenizer audit. Ini tokenizer-only, bukan BGE-M3 inference. Max V2 serialized input573, overflow640=0.

| Eligibility | Jumlah | Tindakan |
|---|---:|---|
|REUSABLE_VERIFIED|369|Boleh copy byte-for-byte setelah re-verification pada task completion berikutnya.|
|REQUIRES_REEMBEDDING|2|Jangan memakai vektor lama untuk changed input.|

| Chunk | Row index zero-based | V1 tokens | V2 tokens | Penyebab |
|---|---:|---:|---:|---|
|WO-DOC-024-C003|154|200|218|Exact serialized input berubah.|
|WO-DOC-027-C009|178|121|169|Exact serialized input berubah.|

Eligibility manifest menyimpan seluruh371 receipts: chunk/document IDs, old/new input hashes, row indices, token lengths, raw float32 vector SHA, eligibility/reason, source index/manifest/checksums serta target identity/mapping. Seluruh receipts diperiksa ulang terhadap original vectors dan serialized text. Tidak ada vector baru, staged matrix, zero-row placeholder atau COMPLETE R3 V2 dibuat.

## V2 Dense completion plan — belum dijalankan

Plan artifact `dense_completion_plan.json` berstatus **INCOMPLETE**, artifact_type **PLAN_ONLY_NO_VECTORS**, `r3_v2_ready=false`. Eligibility audit sendiri AUDIT_COMPLETE, bukan embedding index.

1. Reverify snapshots, source vector checksum, input/mapping dan eligibility sebelum copy.
2. Setelah persetujuan terpisah, encode hanya dua changed serialized inputs memakai pinned BGE-M3, CUDA FP16 batch1, max_length640, tanpa truncation. Resource gates default6GiB/approved5GiB dan watchdog2GiB tidak berubah.
3. Copy369 verified float32 vectors bit-for-bit; jangan renormalisasi salinan yang sudah valid. Gunakan existing `unit_vectors` untuk dua output baru sesuai pipeline.
4. Merge sesuai canonical V2 chunk_id ascending mapping; validasi371×1024 float32 finite, unit norms, duplicate/missing IDs=0 dan copied-byte parity.
5. Buat rows/vectors/manifest baru dengan V2 identity dan artifact checksums, readback lalu atomic publish. Loader wajib menolak incomplete state.

Planned target identity fingerprint:
`8dba4c5660edd892285f0b3093732f11a5815e4ac39d06707900ff468f204254`.
Planned COMPLETE directory: `D:/ModelCache/wo-retrieval-benchmark/R3/8dba4c5660edd892285f0b3093732f11a5815e4ac39d06707900ff468f204254`.
Directory COMPLETE maupun `.incomplete` **belum dibuat**. Ini identity hasil derivasi kode/environment saat ini, bukan checksum index yang sudah selesai. Jika kode/config/dependency berubah pada task berikutnya, hitung ulang identity/path; jangan memaksakan planned fingerprint.

## R4 integration readiness

**Algorithm compatibility PASS dari inspection dan synthetic regression; V2 runtime selection/completion PENDING.** Existing HybridRetriever menerima snapshot-bound component instances dan memeriksa snapshot/hash/protocol/serialization/universe parity. RRF tetap60, full Dense371 dan seluruh strictly positive BM25 candidates; zero/negative dikeluarkan tanpa pseudo-rank. Tidak ada R4 index baru diperlukan.

Perubahan minimum yang perlu didokumentasikan/diotorisasi pada integration task berikutnya, belum diimplementasikan:

- Explicit V2 binding serta pemilihan versioned R2 index, sementara default V1 tetap.
- Validasi token mapping terhadap audit V2; `serialization.audit.fingerprint` di frozen protocol masih historical V1. Jangan menyalin hash V1 untuk V2 atau mengubah lexical/model policy hanya agar loader lolos.
- Admit hanya COMPLETE V2 Dense cache dengan freshly computed identity pada offline loader, bukan melonggarkan integrity checks.
- Shared query contract mengikat full Dense identity dan canonical manifest checksum. Query vectors V1 tidak otomatis diterima untuk V2; perlu explicit artifact rebinding/revalidation atau encoding task sesuai persetujuan. Tidak ada query embedding dibuat sekarang.

Tidak ada keputusan scoring/candidate/metodologis baru diterapkan. R3/R4 V2 end-to-end **NOT TESTED**. Milestone8C tetap `end_to_end_pending`.

## Resource dan environment

Digunakan existing `.venv-ml`: NumPy2.5.3, SciPy1.18.1, scikit-learn1.9.1, rank-bm25 0.2.2, tokenizers0.22.2. Pinned torch2.12.1+cu126/FlagEmbedding1.4.2/Transformers4.57.6 hanya diverifikasi package metadata; tidak di-import pada preparation maupun independent readback. `.venv` ingestion digunakan terpisah untuk parser regressions. Tidak ada install, upgrade, download atau perubahan environment.

Preflight available RAM4.019GiB, available virtual memory10.218GiB. Observasi akhir RAM4.408GiB dan available virtual memory10.344GiB melalui Win32_OperatingSystem; metrik virtual-memory ini bukan pengukuran commit headroom khusus. Disk akhir C:13.03GiB, D:846.89GiB. RAM sistem dipengaruhi aplikasi lain; tidak diklaim sebagai penghematan hasil kode. Peak process RAM/VRAM **NOT MEASURED**, GPU tidak digunakan. Payload final Dense tetap1.519.616bytes untuk371×1024 float32, tetapi model loading berikutnya tetap memerlukan resource gate tersendiri.

## Tests dan integrity

| Pemeriksaan akhir | Hasil |
|---|---|
|Retrieval, Dense synthetic, Hybrid synthetic, query-vector synthetic, protocol dan6new V2 tests|72 PASS (43,632s)|
|Existing ingestion dan versioned pipeline tests dalam `.venv`|29 PASS (13,273s)|
|Total distinct final tests|101 PASS|
|TOML parse/Markdown consistency|PASS melalui5existing protocol tests|
|Independent TF-IDF full matrix/IDF formula readback|PASS|
|Independent BM25 frequency/length/IDF floor readback|PASS|
|Dense source checksum, all371reuse receipts dan plan audit binding|PASS|
|Snapshot/source/index and existing-file integrity|PASS,635/635 unchanged|

New tests: unchanged config parameters/snapshot overlay; exact369/2serialization; excluded metadata isolation; R1/R2 roundtrip equivalence; V1 identity rejected by V2 loader; corrupt file rejected; overwrite blocked and V1 sentinel unchanged; exact-input/contract/mapping reuse requirements; invalid dimension/dtype/nonfinite/zero/nonunit vectors rejected. Tests menggunakan fixtures/temp output dan synthetic query strings, tidak menjalankan development queries atau effectiveness evaluation.

Initial broad discovery dalam `.venv-ml` gagal mengimpor dua ingestion test modules karena python-docx hanya tersedia di `.venv`; suite kemudian dipisah sesuai environment. Existing CLI audit test juga gagal membaca CP1252 curly apostrophe sebagai UTF-8, terkonfirmasi UnicodeDecodeError reader thread; final suite dijalankan dengan process-only PYTHONUTF8=1/PYTHONIOENCODING=utf-8 dan PASS. Tidak ada dependency/code fix untuk kegagalan environment itu. Satu initial independent-readback helper keliru memperlakukan documents.json array sebagai JSONL; helper sementara diperbaiki dan full readback PASS. Kegagalan awal tidak dihitung sebagai PASS.

Final SHA-256 terhadap635baseline files sama seluruhnya: source/canonical/chunks V1/V2, snapshots/fingerprints, original queries/provenance/qrels, migrated silver qrels, protocol/pilot configs, old reports/code/tests serta indices/runs R1/R2/R3 V1 tidak berubah. Frozen snapshot memiliki historical fields seperti `indices.v2_rebuilt=false` pada creation time; tidak ditulis ulang. Kesiapan artifact baru dicatat hanya pada manifest/report baru ini.

## Files created dan langkah berikutnya

Tidak ada existing file diubah. **12 new repository files**:

- `scripts/prepare_v2_indexes.py`
- `tests/test_v2_index_preparation.py`
- `experiments/indexes/v2_ai_corrected/R1/documents.json`, `model.json`, `matrix.npz`, `manifest.json`
- `experiments/indexes/v2_ai_corrected/R2/documents.json`, `model.json`, `manifest.json`
- `experiments/indexes/v2_ai_corrected/dense_reuse_eligibility.json`
- `experiments/indexes/v2_ai_corrected/dense_completion_plan.json`
- `experiments/reports/milestone_9a8_v2_index_preparation.md`

Temporary baseline/readback helpers dan stdout/stderr evidence ada di `D:/ModelCache/tmp/wo-m9a8`, di luar repository/frozen dataset. Environment trees tidak di-hash menyeluruh; tidak ada package mutation yang dijalankan.

Rekomendasi setelah review: task terpisah untuk resource-gated dua changed embeddings, merge/readback/publish V2 Dense, lalu minimal version-aware R3/R4/query-contract integration dengan regression tests. Reuse eligibility tetap harus diverifikasi lagi saat eksekusi; technical PASS tidak memvalidasi kebenaran domain atau silver qrels. Keenam unresolved corpus issues dan human-validation limitations tetap berlaku.

**STOP setelah9A.8.** Tidak ada BGE-M3/GPU inference, corpus/query embedding generation, retrieval effectiveness benchmark, Recall/MRR/nDCG, main queries, qrels generation, commit/push/PR/deploy.
