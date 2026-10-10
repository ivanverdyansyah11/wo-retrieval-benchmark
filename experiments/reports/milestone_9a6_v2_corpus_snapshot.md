# Milestone 9A.6 — Versioned V2 corpus ingestion, chunking dan pilot snapshot

Tanggal: 2026-10-09. Status: **ai_corrected_pilot_not_human_validated**. Judul skripsi tidak berubah. Pilot sintetis yang dikoreksi AI, bukan final research dataset, human validation, expert validation, complete qrels atau hasil benchmark.

## Hasil utama

**Technical validation PASS.** 50/50 kandidat berhasil di-ingest; nol kegagalan dan nol parsing warnings. V2 menghasilkan **371 chunk aktual**, tanpa memaksa jumlahnya sama dengan V1. Distribusi: DOCX187, PDF79, TXT42, XLSX63. Dokumen sumber tetap DOCX26/PDF9/TXT5/XLSX10.

Dua dokumen memiliki perubahan hasil ekstraksi dan operational text:024 dan027. Sebanyak48 source files tetap byte-identical dengan V1. Document IDs001–050 tetap;371 chunk IDs kebetulan tetap sama, tetapi **024-C003 dan027-C009 memiliki content/serialization hash baru**. Tidak boleh memakai embedding V1 untuk content berubah atau menganggap indeks V1 kompatibel hanya karena ID sama.

Coverage **768/768 operational blocks**; empty0, duplicate content hashes0, missing documents0, invalid locator/span0, orphan candidates0 menurut heuristik deterministik terbatas. Title/heading mapping valid; proxy-token maximum tetap485. Ini audit teknis, bukan exhaustive semantic/domain review. Visual DOCX QA: **NOT TESTED**, karena renderer LibreOffice tidak tersedia pada runtime/PATH yang diperiksa; parsing XML bukan layout validation.

## Preflight dan enam isu unresolved

Laporan9A.5 dan seluruh14 correction ledger records dibaca. Verifikasi SHA-25650 kandidat terhadap ledger PASS; tepat024/027 berubah dan48 sama. Dua DOCX corrected dapat dibaca existing parser. Semua IDs, manifest metadata, file suffix dan inventory konsisten. Snapshot/fingerprint V1 diverifikasi sebelum build dan sesudahnya.

Tidak ditemukan blocker kritis untuk **pilot penelitian sintetis dengan disclosure**. Keenam isu berikut tetap unresolved dan dicatat pada snapshot; tidak diberi status resolved/approved dan tidak diperbaiki melalui asumsi baru. Mereka membatasi interpretasi isi serta penggunaan sebagai panduan operasional nyata.

| Isu | Lingkup | Keputusan untuk pilot |
|---|---|---|
|C06|Otorisasi teknis, listrik dan backup|Nonblocking teknis untuk text pilot; tidak ada sertifikasi keselamatan/fasilitas/personel nyata.|
|C07|Rain plan, kapasitas alternatif, waktu perpindahan|Nonblocking dengan skenario berlabel; layout, tenaga, jarak dan durasi nyata belum diverifikasi.|
|C08|Catering/banquet capacity|Nonblocking; headcount event berbeda bukan konflik. Kecukupan layanan/keamanan pangan tidak divalidasi.|
|C09|Shuttle, kapasitas kendaraan, route/LO|Nonblocking;3×15=45 hanya aritmetika skenario. Tidak mengesahkan kapasitas/durasi/driver nyata.|
|C10|Kecukupan dua escort|Nonblocking plausibility concern;28×10=280 bukan bukti staffing optimal. Tidak menambah staf secara spekulatif.|
|C12|Beach access/permission|Nonblocking sebagai teks asumsi;80 tamu bukan bukti kapasitas, izin, pasang surut atau keamanan pantai.|

Ini penilaian AI atas readiness teknis pilot, bukan independen domain assessment. Persetujuan pembimbing tetap diperlukan untuk metodologi evaluasi utama. Konten asli notice “belum divalidasi praktisi” tetap dipertahankan/terekstrak sebagai metadata; status dataset baru tidak mengklaim human validation.

## Pipeline dan reproduksibilitas

Parser DOCX/PDF/TXT/XLSX, cleaning, structure-aware chunker dan shared serializer tidak diubah. Satu file existing diubah: `src/wo_retrieval/pipeline.py`, untuk menerima explicit version V2, membatasi source/manifest/inventory/output ke jalur V2, memeriksa sumber kandidat selama ingestion, dan menempatkan config/integrity sidecars pada folder versi. Defaults V1 tetap. CLI existing tidak diubah.

Config baru `experiments/configs/pilot_v2.toml` berbeda hanya dalam identitas versi/jalur input-output. Parameter chunking sama persis dengan frozen `pilot.toml`: target500, overlap maksimal75, `approx_unicode_chars_div4_v1`. Source manifest baru mencatat parent hashes/dataset version, candidate hashes/status dan ledger reference; tidak menyentuh manifest V1. Inventory V2 hanya50 operational documents; `documents/<filename>` adalah key inventory yang diaudit terhadap configured candidate source directory, bukan file salinan baru di dataset output.

Source files tetap berada di `data/corpus_candidates/v2_ai_corrected/documents/`; tidak dibuat salinan corpus ketiga. Seluruh data turunan ada di `data/versions/v2_ai_corrected/`: source_manifest, inventory, processed/documents, chunks/chunks, reports, validation. Manifest/inventory/ledger/report tidak menjadi retrievable content.

Build dan audit dapat direproduksi pada checkout identik dengan folder output V2 yang belum ada:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:TMP='D:/ModelCache/tmp'
$env:TEMP='D:/ModelCache/tmp'
.venv/Scripts/python.exe -B scripts/build_v2_pilot.py --tokenizer-python .venv-ml/Scripts/python.exe
```

Builder menolak overwrite output V2 existing. Jangan hapus snapshot untuk rerun; gunakan workspace/disposable copy terpisah bila perlu mengulang. Setelah metadata tersedia, CLI existing mendukung config V2, tetapi jangan menjalankan kembali `run` pada frozen output tanpa keputusan versioning baru. Tidak ada algorithm/tokenizer/model parameter yang dipilih dari skor retrieval.

Deterministic rebuild check: extraction/cleaning/chunking V2 dijalankan dua kali in-memory dan menghasilkan JSONL dokumen/chunk identik byte. Hasil core JSONL juga sama pada build final berikutnya setelah hardening audit schema; snapshot creation timestamp memang tidak diharapkan identik antar-run. V1 rebuilt in-memory dengan pipeline baru cocok byte-exact terhadap documents.jsonl dan chunks.jsonl frozen, tanpa publikasi ulang.

Satu build awal berhenti sebelum snapshot karena helper audit salah memakai `query_text` pada query draft yang schema-nya memakai `text`. Bug helper diperbaiki; artefak intermediate disimpan hanya pada temporary diagnostic directory di luar repository. Build final lulus. Tidak ada V1/candidate/query/qrels yang berubah dan tidak ada model loading/retry GPU.

## Serialization dan tokenizer audit

Existing shared `wo_operational_context_dedup_v1` tetap: title/heading/category ditambahkan hanya jika belum terkandung sesuai dedup policy; chunk.text dipertahankan. `metadata.guide_context` tetap audit-only; tidak diinjeksi. Semua63 XLSX chunks memiliki text, row/header/sheet locators dan structured guide_context yang identik dengan V1. Source path/status/version metadata berubah pada canonical V2, tetapi excluded dari retrievable serializer. Tidak ada query evidence, qrels atau ledger masuk serialized inputs.

Tokenizer aktual BGE-M3 dipakai offline melalui installed `tokenizers.Tokenizer.from_file` atas tokenizer.json dari pinned local checkpoint. No truncation/no padding, BOS0 dan EOS2 disertakan; hash file cocok lock. Tidak mengimpor torch/transformers atau memuat neural weights. Ini audit panjang input, bukan embedding/inference test.

Model: `BAAI/bge-m3`; revision `5617a9f61b028005a4858fdac845db406aefb181`; tokenizer SHA-256 `21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08`.

| Input | Min | Median | Mean | P95 nearest-rank | Max | >640 |
|---|---:|---:|---:|---:|---:|---:|
|chunk.text saja|55|108|166.530997|468|544|0|
|Shared retrieval serialization|83|137|194.517520|497|573|0|

Max_length640 tetap mencukupi untuk seluruh serialized V2 inputs yang diuji, dengan67 token margin pada input terpanjang. Tidak dilakukan truncation atau re-chunking. Risiko perubahan serialization/model/tokenizer di masa depan harus diaudit kembali. Tidak ada klaim GPU readiness, latency atau retrieval effectiveness baru.

## Query provenance dan silver qrels impact

Seluruh18 exact development queries tetap. Semua42 source evidence pointers diperiksa terhadap canonical V1 dan V2: IDs, title, source filename/format, block, locator dan heading cocok. Satu pointer memiliki teks berubah: query004→024 b0011. Query013→024 b0012 tetap tetapi containing chunk024-C003 berubah. Query009→027 b0013/b0016/b0022 tetap secara teks, tetapi source file/version binding berubah. Semua pointer harus direbind ke jalur/snapshot V2 pada task yang disetujui; existing provenance tetap menunjuk V1.

Pembacaan18 pertanyaan bersama diff tidak menemukan evidence pointer hilang atau penghapusan informasi inti yang jelas. Ini bukan validasi final answerability. Perubahan waktu standby dan klarifikasi closure harus dikalibrasi terhadap kebutuhan informasi; kebutuhan lain tetap dibatasi asumsi corpus sintetis. Tabel seluruh query dan mapping ada di laporan diff serta JSON impact.

| Existing judgment classification | Count | Arti |
|---|---:|---|
|EXACT_CONTENT_MATCH_CANDIDATE|666|Text, content hash, serialized text dan unique source-block mapping cocok; hanya kandidat reutilisasi setelah verifikasi.|
|CHANGED_CONTENT_REQUIRES_REJUDGMENT|18|Seluruh18 query paired dengan024-C003 yang berubah; tidak berarti semua grades lama salah.|
|CHUNK_MAPPING_AMBIGUOUS|0|Tidak ditemukan mapping ambigu pada684 existing pairs.|
|MISSING_OR_INVALID|0|Existing query/hash/chunk/source/locator/snapshot binding valid.|

027-C009 berubah tetapi tidak berada pada684 judged pairs. Audit JSON menyimpan classification dan candidate mapping, **tanpa membuat relevance grades/qrels V2**. Grades V1 tidak diubah. Universe V2=18×371=**6678 pasangan**; accepted V2 judgments=0, sehingga seluruh6678 belum mempunyai qrels V2 yang diterima. Angka684 judged/5994 unjudged tetap hanya status V1. Jangan mengubah666 candidates menjadi accepted judgments secara otomatis.

## Snapshot V2

ID: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.

Aggregate fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

Manifest: `data/versions/v2_ai_corrected/validation/pilot_snapshot.json`. Fingerprint=SHA-256 UTF-8 compact sorted-key JSON dari seluruh artifact_sha256 entries, tanpa trailing newline. Scope mencakup source manifest/inventory, derived dataset/audits, configs, ledger/report9A5, builder dan source-code hashes. Manifest sumber mengikat seluruh50 source hashes yang juga disimpan eksplisit pada snapshot. Snapshot JSON itu sendiri dan dua laporan milestone yang ditulis sesudah build tidak masuk fingerprint; timestamp tidak menjadi payload fingerprint.

Parent: `WO-CORPUS-V1-DRAFT-PILOT-001`, fingerprint `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`. V2 punya identitas/hash sendiri; corpus_version `v2-ai-corrected` dan validation_status `ai_corrected_pilot_not_human_validated`. Outstanding IDs C06/C07/C08/C09/C10/C12 tercatat. Bukan dataset final atau expert-validated corpus.

| Key V2 artifact | SHA-256 |
|---|---|
|`data/versions/v2_ai_corrected/source_manifest.json`|`67c0ff87c12f91e3ada35e4df07141254a85d3893cc38bf77f388a8833893517`|
|`data/versions/v2_ai_corrected/processed/documents.jsonl`|`fc7a31906d48c1de72f867147b91b8f5fb293e04d1cc27c699b923ed5ea202db`|
|`data/versions/v2_ai_corrected/chunks/chunks.jsonl`|`0cfad810122cde84be55b1fedb330c98aafbe30e14ea0168699212382dd4c5ba`|
|`data/versions/v2_ai_corrected/validation/pilot_snapshot.json`|`6658fee4737c0d2fa725ee31cb647ec638de350fc2ccfe669999847ac2331b07`|

## Tests, integrity dan batas eksekusi

**34 tests PASS:**25 existing parser/cleaning/chunking/ingestion tests +4 new versioned pipeline/mapping tests +5 existing protocol tests. New tests membuktikan output V2 tidak menyentuh V1 sentinels/candidate, path/status/inventory traversal invalid ditolak, deterministic rebuild, serta mapping tidak mengandalkan ID. Dua invocation awal dengan wildcard test yang keliru menemukan0 test; tidak dihitung sebagai PASS.

TOML parse/Markdown protocol consistency PASS dari existing protocol tests. Parameters frozen identik dan retrieval protocol tidak diubah. Protocol dan existing retriever/index loaders **masih terikat V1**; mereka belum diotorisasi/dikonfigurasi untuk V2. Tidak menjalankan retriever tests yang membangun indeks fixture karena perubahan ini hanya ingestion/versioning; tidak ada R1–R4 live run.

Baseline awal berisi600 file existing. **599/599 file selain satu pipeline file yang diizinkan tetap identik SHA-256**. Ini mencakup source V1, seluruh50 candidate source files, documents/chunks/pilot/snapshot V1,18 queries/provenance, silver qrels/workbooks/reports existing dan cache project indices/runs. Pipeline code hash before/after tercatat pada laporan diff. V1 aggregate fingerprint dan snapshot JSON SHA tidak berubah. `.venv`/`.venv-ml` digunakan tanpa instalasi/perubahan package; environment tree tidak di-hash menyeluruh. `.git` tidak tersedia; scope diverifikasi memakai baseline filesystem/hashes.

DOCX visual QA **NOT TESTED**; tidak ada renderer tersedia yang dipakai. Domain/independent human validation **NOT PERFORMED**. Orphan check terbatas pada pola fragment deterministik; technical PASS tidak membuktikan seluruh prosedur benar/aman di lapangan.

## Files created/changed dan next milestone

Changed existing: `src/wo_retrieval/pipeline.py` saja. Created code/config/tests: `scripts/build_v2_pilot.py`, `experiments/configs/pilot_v2.toml`, `tests/test_versioned_pipeline.py`. Created dataset:24 files dalam `data/versions/v2_ai_corrected/`. Created reports: laporan ini dan `experiments/reports/milestone_9a6_v1_v2_diff.md`. Total29 file baru; daftar lengkap ada pada laporan diff. README, protocol, frozen artifacts dan source candidate tidak diubah.

**Rekomendasi berikutnya, belum dijalankan:** review/adopsi pilot V2 dan metodologi/disclosure bersama pembimbing; putuskan task khusus version-binding query/provenance dan pemeriksaan ulang label yang terdampak. Baru setelah persetujuan terpisah lakukan V2-bound index rebuild dan pemeriksaan retrieval teknis. Jangan gunakan indeks/query cache/qrels V1 berdasarkan ID saja. Human/expert validation tidak dianggap selesai oleh audit ini.

**STOP setelah9A.6.** Tidak ada R1/R2/R3 re-indexing, BGE-M3/GPU inference, corpus embedding, R4 rewrite, qrels baru,75 main queries, Recall/MRR/nDCG, benchmark effectiveness, instalasi/download, commit/push/PR/deploy.
