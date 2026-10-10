# Milestone 9A.6 — V1–V2 corpus diff dan query/qrels impact

Status: **ai_corrected_pilot_not_human_validated**. Audit konten/mapping saja, bukan relevance judgment baru. Document IDs tetap dan source V1/candidate tidak diubah. Summary/build/snapshot rationale ada pada laporan milestone pendamping.

## Document comparison

V1=50 dokumen/371chunk; V2=50 dokumen/371chunk.48 source bytes dan normalized block records identik kecuali version/source binding metadata dataset. Dua sources024/027 memiliki masing-masing satu label versi dan satu paragraf isi yang berubah. Semua50 canonical JSON records berubah provenance/source path/corpus version/validation status; itu tidak berarti50 operational texts berubah.

`full_span_locators_unchanged=false` pada024/027 karena serialized_char_end mengikuti panjang teks baru. **Block grouping/partition tidak berubah** pada semua dokumen: grouping source blocks dan jumlah chunks tetap. Jadi2 dokumen memiliki perubahan span extent,0 dokumen mengalami perubahan grouping/split chunk. Tidak boleh menyebut seluruh boundaries identik tanpa membedakan ini.

| Document | V1 chunks | V2 chunks | Normalized block content unchanged | Full span locators unchanged | Block grouping unchanged | Serialization unchanged |
|---|---:|---:|---|---|---|---|
|WO-DOC-001|6|6|True|True|True|True|
|WO-DOC-002|6|6|True|True|True|True|
|WO-DOC-003|6|6|True|True|True|True|
|WO-DOC-004|5|5|True|True|True|True|
|WO-DOC-005|6|6|True|True|True|True|
|WO-DOC-006|5|5|True|True|True|True|
|WO-DOC-007|7|7|True|True|True|True|
|WO-DOC-008|6|6|True|True|True|True|
|WO-DOC-009|7|7|True|True|True|True|
|WO-DOC-010|8|8|True|True|True|True|
|WO-DOC-011|6|6|True|True|True|True|
|WO-DOC-012|7|7|True|True|True|True|
|WO-DOC-013|7|7|True|True|True|True|
|WO-DOC-014|6|6|True|True|True|True|
|WO-DOC-015|7|7|True|True|True|True|
|WO-DOC-016|6|6|True|True|True|True|
|WO-DOC-017|10|10|True|True|True|True|
|WO-DOC-018|9|9|True|True|True|True|
|WO-DOC-019|7|7|True|True|True|True|
|WO-DOC-020|6|6|True|True|True|True|
|WO-DOC-021|7|7|True|True|True|True|
|WO-DOC-022|6|6|True|True|True|True|
|WO-DOC-023|6|6|True|True|True|True|
|WO-DOC-024|6|6|False|False|True|False|
|WO-DOC-025|6|6|True|True|True|True|
|WO-DOC-026|6|6|True|True|True|True|
|WO-DOC-027|9|9|False|False|True|False|
|WO-DOC-028|8|8|True|True|True|True|
|WO-DOC-029|8|8|True|True|True|True|
|WO-DOC-030|7|7|True|True|True|True|
|WO-DOC-031|9|9|True|True|True|True|
|WO-DOC-032|9|9|True|True|True|True|
|WO-DOC-033|7|7|True|True|True|True|
|WO-DOC-034|6|6|True|True|True|True|
|WO-DOC-035|7|7|True|True|True|True|
|WO-DOC-036|7|7|True|True|True|True|
|WO-DOC-037|7|7|True|True|True|True|
|WO-DOC-038|6|6|True|True|True|True|
|WO-DOC-039|6|6|True|True|True|True|
|WO-DOC-040|7|7|True|True|True|True|
|WO-DOC-041|13|13|True|True|True|True|
|WO-DOC-042|8|8|True|True|True|True|
|WO-DOC-043|16|16|True|True|True|True|
|WO-DOC-044|16|16|True|True|True|True|
|WO-DOC-045|8|8|True|True|True|True|
|WO-DOC-046|6|6|True|True|True|True|
|WO-DOC-047|7|7|True|True|True|True|
|WO-DOC-048|7|7|True|True|True|True|
|WO-DOC-049|7|7|True|True|True|True|
|WO-DOC-050|10|10|True|True|True|True|

## Modified chunks — exact content hashes

Added IDs:0. Removed IDs:0. Modified content/serialized IDs:2.369 exact-content candidates. Mapping ambigu:0, missing:0. Same IDs dipertahankan hanya karena deterministic chunker menghasilkan grouping sama; bukti mapping berasal dari document+source block locators dan exact text/hash comparison.

| Chunk ID | V1 content SHA-256 | V2 content SHA-256 | V1→V2 proxy tokens |
|---|---|---|---|
|WO-DOC-024-C003|`10f618c44b1e69881d1fc911bb966b031ff33ccd4662631de5d303183c78d073`|`ef0815f6eeb43bcdbc52ad0338a7735ca0108fd124f2c892b765147eb90f9e94`|198→213|
|WO-DOC-027-C009|`5beec4bd27ce0ce969bc1abd580d69839fe8910dc9a8f86fc70390b88295dec6`|`4dcceef3430106e0b8ae7c553a6ea669613ea834070ffb1794903f412a895078`|118→161|

Machine-readable mapping: `data/versions/v2_ai_corrected/reports/v1_v2_chunk_mapping.json` (371 rows, before/after content and serialized hashes plus full locators). Candidate selection requires matching document and ordered underlying block locators, then exact content and serializer equality. Jika beberapa candidates memenuhi dan tidak dapat dibedakan, mapping menjadi CHUNK_MAPPING_AMBIGUOUS; jika tidak ditemukan, MISSING_OR_INVALID. Offset endpoints tidak dipakai sebagai bukti isi sama. Unit fixtures menguji ID berbeda dengan konten sama, ID sama dengan konten berubah, context/title berubah, locator mismatch, dan ambiguous repeated candidate.

XLSX: seluruh10 dokumen/63chunk identik dalam text, sheet/header/row references dan guide_context. PDF/TXT tidak berubah dalam content/locators; DOCX selain024/027 juga sama. Shared serializer policy/hashes tidak diubah. Mapping exact-content bukan otorisasi reuse corpus embeddings; V2 snapshot/cache identity tetap baru dan seluruh V2 indices harus dibangun khusus bila diizinkan.

## Seluruh18 query dan42 evidence pointers

Query text tidak diubah. Semua pointers valid;41 block text exact-match,1 berubah (004→024 b0011). Tidak ada pointer hilang. Tidak ditemukan kehilangan information need inti yang jelas dari diff; status draft/pending tetap. Answerability belum disetujui manusia. Setiap query memiliki satu judged pair pada024-C003 dalam V1 sehingga seluruh18 memiliki setidaknya satu label yang memerlukan rejudgment, meskipun evidence pembentukan query biasanya tidak berubah.

| Query | Exact draft text | Potential answerability/provenance impact |
|---|---|---|
|WO-DEV-001|Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim?|RACI/registrasi: evidence tidak berubah; tidak ada kebutuhan rewrite query yang terdeteksi.|
|WO-DEV-002|Pada H-1, apa yang harus diperiksa dalam final confirmation ketika kebutuhan loading vendor berbeda dari izin venue?|Final confirmation/loading: evidence tidak berubah; otorisasi venue tetap kondisional.|
|WO-DEV-003|Apa saja prasyarat cue C03 entrance sebelum floor memberi aba-aba jalan?|Prasyarat C03: evidence asli017 tidak berubah. Label analogi existing pada024-C003 tetap memerlukan rejudgment.|
|WO-DEV-004|Apa yang harus dikonfirmasi kepada makeup artist agar jadwal makeup tidak berbenturan dengan standby akad?|Jadwal MUA/standby: pointer024 b0011 berubah. Acuan08.45 eksplisit pada skenario; kebutuhan informasi tetap, support perlu review ulang.|
|WO-DEV-005|Jika mikrofon gagal saat sambutan, bagaimana alur penanganan dan pemeriksaan sebelum audio dipakai lagi?|Gangguan mikrofon: evidence tidak berubah; tidak mengesahkan prosedur teknis nyata (C06 tetap unresolved).|
|WO-DEV-006|Saat checkout, apa yang perlu dicocokkan pada daftar aset WO sebelum barang diserahterimakan?|Checkout aset: evidence tidak berubah; fase checkout tetap berbeda dari pemeriksaan persiapan.|
|WO-DEV-007|Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru?|Instruksi bertentangan: evidence tidak berubah; alur komando tetap.|
|WO-DEV-008|Seminggu menjelang acara, bagaimana mencatat pekerjaan yang belum tuntas agar tetap ditindaklanjuti sampai hari pelaksanaan?|Tracking pekerjaan: evidence tidak berubah; beda fase preparation/handover tetap perlu dibaca.|
|WO-DEV-009|Hujan turun menjelang tamu masuk ke taman. Apa yang perlu dipastikan sebelum kegiatan dialihkan ke ruang tertutup?|Rain activation: tiga pointer027 b0013/b0016/b0022 tidak berubah; sumber berubah versi. Closure b0026 bukan bukti pengganti readiness.|
|WO-DEV-010|Saat meninjau lokasi di tepi pantai, apa yang perlu diperiksa agar tamu dan perlengkapan bisa mencapai area acara?|Akses pantai: evidence tidak berubah; C12 berarti akses/izin aktual belum divalidasi.|
|WO-DEV-011|Ada orang yang menanyakan apakah seorang tamu sudah datang. Informasi apa yang boleh disampaikan petugas penerima tamu?|Disclosure kehadiran tamu: evidence tidak berubah; tidak menambah data personal.|
|WO-DEV-012|Bagaimana mengubah hasil pembahasan setelah acara menjadi perbaikan yang bisa dipantau sampai selesai?|Debrief/follow-up: evidence tidak berubah; tidak otomatis menyatakan review praktisi selesai.|
|WO-DEV-013|Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?|Kesiapan pasangan: pointer024 b0012 tetap, tetapi containing chunk024-C003 berubah karena b0011. Review konteks standby, bukan ganti pertanyaan.|
|WO-DEV-014|Setelah foto di chapel, beberapa tamu akan naik shuttle ke lokasi dinner. Bagaimana LO memastikan tidak ada kelompok yang tertinggal?|Shuttle/LO: evidence tidak berubah; C09 tentang kapasitas/rute nyata tetap unresolved.|
|WO-DEV-015|Tamu yang datang melebihi daftar dan ada kursi kosong di ballroom. Apa yang perlu diperiksa sebelum menambah atau mengubah seating?|Seating: evidence tidak berubah; kursi kosong tidak otomatis tersedia atau membuktikan kapasitas venue.|
|WO-DEV-016|Seorang tamu meminta makanan khusus. Bagaimana guest desk menindaklanjuti permintaan itu dan apa batas informasi yang boleh dijanjikan?|Permintaan makanan khusus: evidence tidak berubah; asumsi layanan/capacity C08 tetap unresolved.|
|WO-DEV-017|Sambutan melewati durasi rencana, sementara dinner belum dimulai. Apa yang perlu dipertimbangkan untuk menyesuaikan rundown?|Penyesuaian rundown: evidence tidak berubah; context versi1.0 versus rain1.1 tetap dipertahankan.|
|WO-DEV-018|PIC pengganti akan mengambil alih di tengah acara. Apa isi handover dan bagaimana memastikan pekerjaan benar-benar sudah diterima?|Handover antar-PIC: evidence tidak berubah; closure insiden tidak boleh dianggap handover area selesai.|

Machine-readable: `query_provenance_impact.json` menyimpan seluruh42 pointer dengan old/new block hashes, locator/heading validity, containing chunk mapping dan source hash status. Tiga query mempunyai pointers ke changed source docs:004,009,013. V1 source paths/snapshot references existing tidak diedit. Rebinding seluruh18 ke V2 memerlukan versi query/provenance baru pada task berikutnya, bukan sekadar mengganti snapshot string sekarang.

## Silver qrels impact, tanpa transfer grades

Seluruh684 pairs diuji binding query ID/exact text hash, chunk ID/document, chunk text hash, source file/locator dan V1 snapshot. Hasil klasifikasi:

| Classification | Count |
|---|---:|
|EXACT_CONTENT_MATCH_CANDIDATE|666|
|CHANGED_CONTENT_REQUIRES_REJUDGMENT|18|
|CHUNK_MAPPING_AMBIGUOUS|0|
|MISSING_OR_INVALID|0|

Machine-readable: `silver_qrels_impact.json`,684 audit rows tanpa grades V2. Candidate reuse tetap membutuhkan verifikasi/adopsi nyata; tidak ada label otomatis dipindahkan.18 changed pairs adalah semua18 query×024-C003; bukan18 grade otomatis salah.027-C009 berubah tetapi unjudged pada V1.90 existing pairs terkait dokumen024/027 secara keseluruhan tetap perlu version-binding check;72 di antaranya exact-content candidates. Frozen V1 tetap684 judged/5994 unjudged, sementara V2 belum menerima judgment apa pun: universe6678 dan accepted qrels0. Jangan menyebut5994 sebagai jumlah unjudged V2 setelah migrasi otomatis yang tidak terjadi.

## Integrity dan perubahan code

V1 fingerprint unchanged: `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`.
V1 snapshot SHA unchanged: `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e`.
V2 fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

Allowed pipeline code hash before: `a52505db2be380b7199d2510a556ff2bef3745332c1e9267eba0447efadf770d`; after: `8e3776d198a65d0be1564fe47327fc44336412d1d227d72de219dd002dd4a4d0`.
Baseline600 file: satu existing pipeline file berubah sesuai izin versioned support;599 lainnya unchanged. Candidate50/V1 docs/chunks/config/snapshot/query/qrels/cache indices semuanya unchanged. Parser/cleaning/chunker/serializer dan R1–R4 code unchanged. Script/checks tidak menjalankan retrieval atau neural inference.

Tests:29 pipeline/version/mapping +5 protocol=34 PASS. V1 in-memory regeneration cocok byte-exact frozen docs/chunks. V2 two-pass deterministic rebuild hashes cocok published JSONL; final build cocok previous working build untuk kedua core JSONL. Snapshot timestamp excluded dari deterministic core comparison. Visual DOCX NOT TESTED; domain/human validation NOT PERFORMED.

## Daftar file baru

- `data/versions/v2_ai_corrected/FILE_INVENTORY.csv`
- `data/versions/v2_ai_corrected/chunks/chunk_config.json`
- `data/versions/v2_ai_corrected/chunks/chunks.jsonl`
- `data/versions/v2_ai_corrected/processed/documents.jsonl`
- `data/versions/v2_ai_corrected/processed/ingestion_config.json`
- `data/versions/v2_ai_corrected/reports/boilerplate_audit.json`
- `data/versions/v2_ai_corrected/reports/chunk_audit.md`
- `data/versions/v2_ai_corrected/reports/chunk_report.json`
- `data/versions/v2_ai_corrected/reports/ingestion_report.json`
- `data/versions/v2_ai_corrected/reports/outstanding_issues.json`
- `data/versions/v2_ai_corrected/reports/quality_audit.json`
- `data/versions/v2_ai_corrected/reports/query_provenance_impact.json`
- `data/versions/v2_ai_corrected/reports/sample_chunks.json`
- `data/versions/v2_ai_corrected/reports/serialization_audit.json`
- `data/versions/v2_ai_corrected/reports/serialized_inputs.jsonl`
- `data/versions/v2_ai_corrected/reports/silver_qrels_impact.json`
- `data/versions/v2_ai_corrected/reports/source_audit.json`
- `data/versions/v2_ai_corrected/reports/tokenizer_audit.json`
- `data/versions/v2_ai_corrected/reports/tokenizer_lengths.json`
- `data/versions/v2_ai_corrected/reports/v1_v2_chunk_mapping.json`
- `data/versions/v2_ai_corrected/reports/v1_v2_diff.json`
- `data/versions/v2_ai_corrected/source_manifest.json`
- `data/versions/v2_ai_corrected/validation/pilot_snapshot.json`
- `data/versions/v2_ai_corrected/validation/source_integrity.json`
- `experiments/configs/pilot_v2.toml`
- `experiments/reports/milestone_9a6_v1_v2_diff.md`
- `experiments/reports/milestone_9a6_v2_corpus_snapshot.md`
- `scripts/build_v2_pilot.py`
- `tests/test_versioned_pipeline.py`

Tidak ada README/protocol/V1 artifact/query/qrels/candidate/index yang diubah. Tidak ada snapshot/index/qrels publication di luar paket V2 yang diminta. STOP sebelum index rebuild atau ground truth continuation.
