# Milestone 9A.9 — Incremental BGE-M3 Dense index V2 completion

Tanggal: 2026-10-09. **OFFLINE IMPLEMENTATION / AUDIT PASS; GPU RESOURCE GATE FAIL; R3 V2 INCOMPLETE.**

Snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.
Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.
Corpus status: **ai_corrected_pilot_not_human_validated**. Tidak ada validasi manusia atau hasil benchmark efektivitas.

## Hasil dan batas eksekusi

Tujuan melengkapi real R3 V2 **belum tercapai** karena resource gate awal gagal. Persetujuan pengguna attachment `aa0ea420-38db-448b-b370-fa762d0d8428` untuk satu controlled run dicatat dengan approved low-memory threshold5GiB. Hanya **satu pemeriksaan gate aktual**, nol percobaan model loading dan nol GPU inference. Tidak ada retry atau penurunan threshold. Bagian G mengizinkan penyelesaian kode/offline tests saat GPU tidak dapat dijalankan; pekerjaan berikutnya dibatasi pada itu.

| Tahap | Hasil |
|---|---|
|Initial resource gate|FAIL: available RAM4,242GiB < approved5GiB|
|Snapshot / R1–R2 V2 / source R3 V1 audit|PASS offline|
|369 reuse receipts verification|PASS|
|GPU model loading|NOT RUN|
|CUDA runtime/capability readiness recheck|NOT RUN setelah initial gate fail|
|024-C003 new embedding|NOT RUN|
|027-C009 new embedding|NOT RUN|
|Real V2 assembly/publication|NOT RUN; R3 V2 INCOMPLETE|
|Live query sanity|NOT RUN|
|Synthetic assembly/exact-search/atomic-publication tests|PASS|
|Final test suites|120 PASS|

Tidak ada `experiments/indexes/v2_ai_corrected/R3/` atau staging vector directory dibuat. Shape real final V2 **belum tersedia**; expected `(371,1024)` bukan hasil embedding baru. Original Dense source matrix `(371,1024)` diverifikasi tanpa weights loading.

## Resource preflight aktual

Probe menggunakan existing `resource()`, `gpu_resource()`, dan `gate()`; probe dilakukan setelah minimal CPU lexical imports, sebelum ML imports/tokenizer/weights. Cache/temp tetap D:. Disk/commit safety checks tidak diabaikan.

| Metrik | Actual |
|---|---:|
|Available RAM|4,242462GiB (4.555.309.056bytes)|
|System commit headroom|9,674713GiB|
|Memory load|73%|
|Probe process RSS|143,82MiB|
|Probe process peak working set|145,49MiB|
|C: free at preflight|13,026GiB|
|D: free at preflight|846,887GiB|
|GPU|NVIDIA GeForce GTX1050|
|NVIDIA driver|581.80|
|Reported total VRAM|4.096MiB|
|Reported used/free VRAM|0 / 4.007MiB|

Existing gate error: **Available RAM below 5 GiB model-loading gate; no model loaded**. Available VRAM dan commit memenuhi batas masing-masing, tetapi itu tidak menggantikan RAM gate.

Satu proses python lain tercatat pada probe, RSS3,45MiB; nama/RSS saja tidak membuktikan fungsi proses. Tidak ada klaim seluruh proses model telah diperiksa atau CUDA readiness aktual PASS. Initial GPU memory0MiB menunjukkan tidak ada pemakaian GPU terlapor saat probe, bukan bukti lengkap tidak adanya model CPU/background. Final inference-specific process scan/locks tidak dijalankan karena initial gate sudah gagal.

Probe akhir setelah offline tests: available RAM4,567009GiB, commit headroom9,619644GiB, memory load71%, C:13,022GiB dan D:846,881GiB. Ini observasi, **bukan gate kedua atau retry**. Perubahan RAM dipengaruhi OS/aplikasi lain; tidak diklaim sebagai penghematan kode.

**Actual embedding/loading time dan peak model RAM/GPU allocated/reserved: NOT MEASURED / NOT RUN.** Angka working set di atas hanya probe, bukan footprint BGE-M3. Tidak ada latency palsu.

## Preflight integrity dan Dense reuse

Dibaca: V2 snapshot,9A.8 eligibility manifest/completion plan, V1 R3 manifest, retrieval protocol, shared serializer, original R3 builder/loader/model normalization, resource gate/watchdog, shared-query offline loader. Existing builder/ready path masih terikat V1; ini alasan additive version selection diperlukan.

`prepare_v2()` menjalankan checksum-bound9A.8 preparation/validation, memverifikasi kedua snapshot/source hashes,50V2 canonical documents,371chunks, R1/R2 V2 manifests/checksums, shared serialized input parity,18query checksum dan migrated silver artifact checksums. Qrels tetap684judged/5994unjudged; tidak dimuat sebagai retrievable input atau diperbarui.

V1 Dense diverifikasi melalui existing `load_components()`: pinned local model hashes, dependency/code/config fingerprints, row mapping/serialized input hashes, original tokenizer mapping fingerprint, vector checksums, dimension1024, float32 storage, finite values dan unit norms. Checkpoint files dibaca streaming untuk hash, bukan sebagai neural weights. Tidak mengimpor torch/Transformers/FlagEmbedding pada audit aktual ini.

Seluruh371reuse receipts dibanding ulang terhadap exact V1/V2 serialized input, row/document IDs, mapping order, source vector raw bytes SHA, source manifest checksum/fingerprint dan target Dense identity. **369 REUSABLE_VERIFIED; tepat2 REQUIRES_REEMBEDDING.** Same ID tidak digunakan sebagai bukti reuse.

| Changed chunk | V2 serialized SHA-256 | Tokens termasuk special tokens |
|---|---|---:|
|WO-DOC-024-C003|`4a3795989f57df285596b4a1b73eb6a70723a67e6cbe1a94f34046b906e00208`|218|
|WO-DOC-027-C009|`d1704c559dfa415f359f820e11c726fb20f3ccec84117a98b03d0567a7f75bbf`|169|

Token counts di milestone ini berasal dari checksum-bound9A.8/frozen V2 audit; tidak diklaim tokenizer/model forward baru. Implemented controlled encoder memeriksa lagi actual BGE tokenizer counts sebelum loading/encoding jika gate pada task berikutnya lolos. Max_length640 dan no truncation tetap.

Model tetap `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`, CUDAFP16,batch1,dense-only,1024dimensions; storagefloat32 dan existing official/project L2 normalization. Target identity fingerprint masih `8dba4c5660edd892285f0b3093732f11a5815e4ac39d06707900ff468f204254`; bukan fingerprint index COMPLETE yang belum ada.

## Version-aware implementation

Semua existing source modules terkunci pada snapshot V2, sehingga **tidak diedit**. Additive module `src/wo_retrieval/versioned_dense.py` dan explicit binding `experiments/configs/dense_v2_binding.json` menyediakan:

- `load_components(..., corpus_version="v1", v1_dense_index=...)`: defaultV1, delegate unchanged legacy validator. V1 cache masih dimuat aktual sebagai sumber reuse.
- `load_components(..., corpus_version="v2")`: explicit V2 binding, versioned R2 path, checksum-bound source audit, V2 identity/mapping dan COMPLETE index di `experiments/indexes/v2_ai_corrected/R3/`. Missing/incomplete/mismatched V2 ditolak; tidak fallbackV1.
- `complete_v2(...)`: one-shot incremental builder, note persetujuan wajib. Tidak ada resume/retry otomatis atau CPU fallback.

Binding mengikat snapshot ID/path/hash/fingerprint, unchanged parent protocol checksum,9A.8 script checksum, eligibility checksum, source R3 V1 dan separate R1/R2/R3 V2 paths. V2 identity dihitung ulang dari config/dataset yang diverifikasi, bukan dengan mengganti snapshot pada V1 manifest. Seluruh retrieval parameters/serialization/ranking tetap diwarisi tanpa perubahan. Existing `wo-dense`/R4/query-vector CLIs masih defaultV1 dan tidak diarahkan ulang.

Validator9A.8 dipakai melalui import checksum-bound script untuk menghindari duplikasi model persistence/serializer. Ini coupling lokal yang disengaja; perubahan script atau binding di masa depan menyebabkan checksum rejection, bukan silent acceptance. Shared `prepare` tetap memeriksa V1 canonical ID set tambahan; input teks V2 hanya dari verified V2 chunks.

R3 COMPLETE manifest nanti tetap memakai structure existing `manifest.json`/`rows.json`/`vectors.npy`, dengan tambahan binding/completion code hashes dan incremental provenance. Loader existing `load_vectors` tetap memeriksa exact identity/row mapping, finite normalized float32 matrix dan checksums. Hash kode baru divalidasi melalui metadata baru, tidak mengubah hash existing Dense/lexical modules atau V1 indices.

## Incremental builder dan safety — implementasi, belum live-tested

1. Initial gate sebelum preparation: default6GiB atau explicitly approved5GiB, same disk/commit/GPU limits.
2. Existing monitor dipakai dengan watchdog2GiB/zero sustained grace, sesuai controlled-run safety. Memverifikasi seluruh reused vectors dan source identities sebelum model initialization.
3. Local tokenizer memeriksa dua input saja; ML imports dan CUDA/Pascal readiness diperiksa **sebelum final gate immediately before weights**. Required RAM tidak dihitung dari initial sample saja.
4. Known model-capable command process scan dan kedua managed locks (`gpu-inference.lock` dan `GPU_MODEL.lock`) mencegah overlap dengan legacy/new managed inference. GPU busy gate tetap. Unmanaged process detection terbatas; bila ada keraguan, stop/manual inspection. Tidak mematikan proses pengguna.
5. Satu model load, dua encode calls, CUDAFP16batch1,max_length640,dense-only. Unsafe memory/OOM/instability stop tanpa retry.
6. Dua output baru di-normalize dengan existing `unit_vectors`, finite/dimension/norm diperiksa, dan disimpan terpisah bersama exact input SHA, actual tokens, model revision, precision/device, duration dan file checksum pada new run evidence directory. Tidak ada full-corpus/query encoding otomatis.
7.369originalfloat32rows disalin byte-for-byte; tidak direnormalisasi. Assembly mengikuti canonical chunk_id ascending, menolak missing/extra/duplicate/stale mapping, input/model/token/config mismatches dan invalid vectors.
8. New final matrix diperiksa penuh, unpublished staging/readback dengan existing `load_vectors`, reverify source/snapshot/resources, lalu atomic directory rename. Failure sebelum publication mempertahankan staging INCOMPLETE dan tidak menghasilkan target COMPLETE.

Tidak ada real staging, dua output vector atau final matrix dibuat pada milestone ini. Synthetic tests memverifikasi orchestration/assembly/publication dengan fixture vectors dan temp directories; mereka bukan keberhasilan real model inference.

## Sanity dan CLI

Current real V2 target missing dan ditolak validator; live retrieval **NOT RUN**. Exact search sanity diuji hanya dengan normalized **synthetic basis vector**, bukan development/query embedding, dan bukan corpus vector yang disamarkan sebagai query. Tests memeriksa topK, finite scores, ties dan snapshot binding. Implemented completion path memiliki offline scoring probe setelah successful publication; tidak memuat model kedua atau menghasilkan query embedding. Live query sanity tetap perlu task/resource review kemudian.

Contoh pemakaian setelah review, **tidak dijalankan sebagai retry sekarang**:

```powershell
# Dari root: PYTHONPATH=src, UTF-8, cache/temp D:, offline HF.
# V1 inspection tanpa weights:
.venv-ml/Scripts/python.exe -B -m wo_retrieval.versioned_dense inspect --corpus-version v1 --v1-dense-index D:/ModelCache/wo-retrieval-benchmark/R3/7867c587b38f59de19ca9f278a29e9f22a5cdbe25f08a4d1289d4d629528b50f

# V2 inspection menolak current incomplete/missing index:
.venv-ml/Scripts/python.exe -B -m wo_retrieval.versioned_dense inspect --corpus-version v2

# Hanya setelah persetujuan baru dan resource memadai:
.venv-ml/Scripts/python.exe -B -m wo_retrieval.versioned_dense complete --corpus-version v2 --approved-low-memory --approval-note "Persetujuan pengguna untuk satu controlled incremental run"
```

Default command version adalahV1; `complete` wajib explicitV2. No method parameters berubah. New versioned component tuple dapat dipakai shared R3 scoring setelah COMPLETE; R4 activation/shared query artifact binding bukan bagian milestone ini dan tidak dilakukan.

## Tests dan integrity

| Final checks | Hasil |
|---|---|
|Retrieval/Dense/Hybrid/query-vector/protocol/V2index/versionedDense suites|91PASS,43,160s|
|Existing ingestion/versioned pipeline suites di `.venv`|29PASS,12,742s|
|Total distinct tests|120PASS|
|New versioned Dense tests|19PASS|
|AST / TOML / protocol consistency|PASS|
|Actual offline source/V2 lexical/reuse audit|PASS tanpa ML import|
|Missing V2 index rejected, no fallback|PASS actual validator + explicit-selection fixtures|
|Existing protected-file SHA integrity|647/647 unchanged|

Tests mencakup default/explicit version selection, V1/V2 isolation, hash/model revision/precision/config mismatch, invalid vectors, duplicate/missing mapping/new records, preserved source bytes, truncation/token mismatch, atomic publication/readback/nooverwrite, failed final verification leaving INCOMPLETE, exact search/ties/snapshot, default6vsapproved5 gate, missing approval rejection, initial gate preventing preparation/encoder dan final post-import gate preventing weights/encode.

Initial new final-gate test memakai mocked Monitor.summary yang belum JSON-serializable; satu test fixture error diperbaiki dengan dict summary. Final19targeted dan91combined suites PASS. Tidak ada real inference/retry dalam test; Torch/FlagEmbedding pada final-gate fixture adalah mocks. Kegagalan awal tidak dihitung sebagai PASS.

Baseline647existing files mencakup source/canonical/chunks/snapshots V1/V2, protocols/configs, original query/qrels/provenance,9A.8indices/audit/plan/code/tests/report serta original cache indices/runs. Semua hash tetap identik; environment trees/root data.zip tidak di-hash menyeluruh dan tidak diubah. Tidak ada Git repository; verifikasi memakai SHA-256/filesystem. `.venv` dan `.venv-ml` dipertahankan; tidak ada instalasi/download.

## Files created dan next step

Hanya5file baru, nol existing file diubah:

- `experiments/configs/dense_v2_binding.json`
- `src/wo_retrieval/versioned_dense.py`
- `tests/test_versioned_dense.py`
- `experiments/reports/milestone_9a9_v2_dense_completion.json`
- `experiments/reports/milestone_9a9_v2_dense_completion.md`

Actual resource/offline/checksum evidence ada pada audit JSON. Temporary baseline/test logs berada di `D:/ModelCache/tmp/wo-m9a9`, bukan corpus/index. R1/R2 V2 artifacts dan existing completion plan tidak diubah; R3 V2 tetap incomplete. Corpus fingerprint tetap, query/qrels unchanged; semua human/expert validation limitations berlaku.

Rekomendasi: pengguna menyediakan RAM yang cukup dan meninjau hasil ini sebelum memberikan persetujuan baru untuk satu incremental GPU attempt. Lakukan last gate setelah imports/tokenizer, bukan hanya initialRAM. Jika successful, verifikasi real two-vector outputs,371×1024merge,atomic readback kemudian tinjau readiness. Jangan melanjutkan R4/effectiveness benchmark sekarang.

**STOP setelah laporan9A.9.** Tidak ada GPU inference, model/query/full-corpus embeddings baru, R4 benchmark, Recall/MRR/nDCG,75mainqueries, qrels generation, commit/push/PR/deploy.
