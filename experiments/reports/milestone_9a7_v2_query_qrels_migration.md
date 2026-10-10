# Milestone 9A.7 — V2 query binding dan AI silver qrels migration

**AI SILVER PROVISIONAL — V2 DEVELOPMENT PILOT — NOT HUMAN VALIDATED.**

Tanggal:2026-10-09. V2 diadopsi pengguna sebagai development pilot saja. Migration/recording timestamp:2026-10-09T03:48:12.512200+00:00. Judul penelitian tidak berubah. Tidak ada human/expert/independent validation atau effectiveness evaluation pada milestone ini.

## Kesimpulan

**Preflight, binding, eligibility checks, readback dan integrity PASS.**18 query memiliki provenance V2 baru dengan42 active evidence pointers yang valid.666 existing pairs memenuhi syarat carry-forward dan dilabeli `CARRIED_FORWARD_AI_SILVER`.18 pairs pada024-C003 dinilai ulang secara semantik:15 grade0,2 grade1,1 grade2. Seluruh18 grade numerik tetap dibanding V1, tetapi rationale/evidence/provenance diperbarui; ini bukan auto-copy old grade.0 pasangan di luar pool ditambahkan.

Hasil tetap **684 judged +5994 unjudged =6678 pasangan**, coverage10,2426%. Grade0/1/2=621/32/31; positives63. Keenam isu corpus unresolved tetap mengikuti snapshot V2. Corpus, chunks, snapshots,18 original query texts, original provenance/qrels dan retrieval protocol tidak diubah.

## Preflight dan input

Dibaca dan diverifikasi: dua snapshot manifests; V2 canonical documents/chunks; source manifests/hashes; V1–V2 mapping dan diff;18 queries dengan information needs/scenario; seluruh684 qrels V1 serta manifest/audit readiness9A.4; benchmark protocol dan shared serialization config. Semua42 pointer text dibaca terhadap exact query untuk memeriksa domain/kebutuhan informasi; pointer tetap navigation aid, bukan qrel otomatis.

Actual counts cocok expected:50 documents,371 chunks,369 unchanged chunks,2 modified (`WO-DOC-024-C003`,`WO-DOC-027-C009`),18 queries,684 V1 judged,5994 unjudged. Mapping dicek silang dari document IDs, block/source locators, raw content hash dan exact shared serialized text hashes; tidak mengandalkan ID sama. Tidak ada ambiguity atau missing/invalid binding yang menghalangi migrasi.

V1 snapshot: `WO-CORPUS-V1-DRAFT-PILOT-001`; fingerprint `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`.

V2 snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`; fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`. Semua hashes pada explicit snapshot payloads dan50 source files V1/V2 diperiksa ulang. Snapshot V2 tidak ditulis ulang.

## Query provenance V2

File baru menyimpan exact original query text/hash, query dataset path/hash, V2 snapshot/fingerprint/corpus status, V2 canonical/source path, block locator/heading/hash, source document hash, dan containing chunk content/serialized hashes. Source formats serta XLSX header/row context tetap.42/42 locator, heading dan block pointers valid;41 block texts unchanged,1 changed. Tidak ditemukan pointer dengan kebutuhan informasi yang tidak didukung pada pembacaan ini; itu bukan human query validation.

Query dataset file dan `query_dataset_version=development-v1-draft` tetap sebagai **identitas teks asal**. Binding overlay baru memakai `provenance_version=development-v2-pilot-binding-v1` dan active snapshot V2. File query original memang masih memuat metadata V1; tidak diubah atau diduplikasi. Konsumen berikutnya harus membaca explicit V2 binding, bukan diam-diam menganggap original query metadata sudah dimigrasi. Query validation status tetap `draft_pending_expert_review` sebagai existing draft status, bukan bukti review praktisi pernah dilakukan.

| Query khusus | V2 evidence dan context update |
|---|---|
|004|024 b0008→024-C002 unchanged; b0011→024-C003 changed. Old standby08.30 diganti explicit standby akad/keluarga08.45 mengacu rundown simulasi042. Old/new full block text, hashes dan full containing chunk context tersimpan pada binding history. Tidak menetapkan waktu nyata.|
|009|027 b0013→C004, b0016→C005, b0022→C007 tetap secara teks/locator. Source hash/path dan snapshot diperbarui karena body26 di bagian lain berubah; tidak menganggap clarification closure sebagai evidence baru rain activation.|
|013|014 b0014/b0015→014-C004 unchanged;024 b0012→024-C003 text unchanged tetapi containing chunk berubah akibat b0011. Old/new full context dan hash dicatat; pertanyaan/kriteria tidak diubah.|

Semua18 bindings mempunyai historical parent path/hash dan revision event baru. Active evidence fields seluruhnya V2; V1 paths/text/snapshot hanya tersisa pada fields yang eksplisit historical (`parent_binding`, `binding_changes`, revision history). Evidence tidak dimasukkan ke field query text atau retrievable corpus.

##666 carry-forward eligibility checks

Seluruh666 pairs diuji ulang: query ID/exact text/hash; chunk/document ID; snapshot V1 asal; unique locator/block mapping; raw text/content hash; exact serialized content/hash V1/V2; grade integer0/1/2; source file/locator; positive excerpt exact substring pada old/new chunk. Semua PASS.606 inherited negatives dan60 inherited positives dibawa; positive evidence60/60 cocok.

Grade, reason, evidence excerpt dan original `assessed_at` pada carried rows dipertahankan. Ditambahkan V2 source/snapshot/content binding, migration timestamp, parent record checksum dan eligibility receipt. `second_pass_status=NOT_REASSESSED_IN_9A7`; original status disimpan sebagai inherited.666 rows **bukan penilaian independen baru** dan tidak dinyatakan semantically revalidated. Record-time migration dibedakan dari original assessment time.

Manifest memuat666 carried receipts (serta18 changed receipts); change log memuat seluruh684 migration events, bukan hanya changes grade. Tidak ada stale serialized hash yang dipakai untuk changed chunk. Tidak ada carried row yang berasal dari027-C009: chunk itu tetap unjudged bagi seluruh18 query.

##18 semantic rejudgments pada024-C003

Assessor AI membaca setiap exact query beserta information need/scenario, full V2 chunk, lalu membandingkan full V1 chunk. Script hanya menyimpan18 keputusan eksplisit dan menjalankan checks; grade tidak dihitung dari keyword, similarity, kategori query, grade lama, atau retrieval score. Same-AI self-check bukan independent second rater. Exact backend model version dan durasi review tidak dapat diverifikasi sehingga tidak dikarang.

Rubric existing:0=inspected/no substantive useful support untuk specific need;1=useful partial support;2=direct substantive support, tidak harus semua aspek jawaban. Relevance dibatasi isi chunk; source/provenance query bukan izin memasukkan jawaban dari chunk lain.

V2 chunk berisi urutan MUA/dressing, standby akad/keluarga08.45 berbasis042, akad09.00, koordinasi perkiraan selesai, readiness pakaian/benda prosesi/pendamping/rute, WC/floor dan batas perubahan foto. Perubahan hanya62 karakter pada kalimat acuan standby; paragraf kriteria kesiapan berikutnya tetap. Full old/new chunk tersimpan untuk setiap rejudgment event pada change log.

| Query | Grade V1→V2 | Keputusan dan alasan semantik V2 |
|---|---:|---|
|WO-DEV-001|0→0|Chunk menyebut PIC pengantin, WC dan floor dalam persiapan akad, tetapi tidak menetapkan A/R atau pembagian tugas daftar registrasi. Penyebutan peran saja tidak mendukung penugasan RACI registrasi.|
|WO-DEV-002|0→0|Pemeriksaan jam layanan MUA bersama vendor tidak memberi pemeriksaan izin loading, rekonsiliasi akses venue atau keputusan saat permintaan vendor berbeda dari izin. Konteks persiapan akad tidak menjawab final confirmation akses.|
|WO-DEV-003|1→1|Kriteria pakaian, benda prosesi, pendamping, rute, kesiapan area dan pemimpin prosesi memberi support parsial untuk menahan pelepasan entrance sebelum pasangan/area siap. Namun chunk membahas akad EVT-02, bukan cue C03 resepsi, dan tidak memuat cue chain, kesiapan MC/AV atau otorisasi C03. Transfer kriteria kesiapan dinilai useful partial, bukan jawaban langsung seluruh skenario.|
|WO-DEV-004|1→1|Rencana mulai06.00, standby akad/keluarga08.45 yang mengacu rundown042, pemeriksaan jam bersama vendor, serta permintaan perkiraan selesai memberi acuan penyelarasan jadwal MUA. Namun fokusnya urutan pagi dan kesiapan hari acara; data lingkup, daftar orang dan durasi layanan yang perlu dikonfirmasi sebelum hari acara tidak dijabarkan. Support parsial ini dinilai ulang dari V2; klarifikasi waktu tidak otomatis menaikkan grade.|
|WO-DEV-005|0→0|Chunk membahas makeup, dressing, foto dan kesiapan pasangan. Tidak tersedia isolasi gangguan mikrofon, teknisi, pengalihan audio atau retest sebelum audio dipakai lagi; menunggu area siap bukan prosedur pemulihan audio.|
|WO-DEV-006|0→0|Benda prosesi disebut sebagai prasyarat kesiapan pasangan, bukan aset WO untuk checkout. Tidak ada pencocokan daftar aset, kondisi/jumlah, penerima atau bukti serah terima barang saat penutupan.|
|WO-DEV-007|0→0|Jalur PIC pengantin ke WC dan pembahasan prioritas foto dengan client/EC tidak menjelaskan tindakan kru menerima dua arahan atasan yang bertentangan. Tidak ada penahanan instruksi, readback konflik atau penyatuan perintah.|
|WO-DEV-008|0→0|Permintaan perkiraan selesai pada titik kerja MUA berlaku pada urutan pagi, bukan register pekerjaan minggu terakhir. Chunk tidak menyediakan pencatatan outstanding, pemilik, tenggat atau kesinambungan follow-up sampai hari acara.|
|WO-DEV-009|0→0|Floor menunggu kesiapan area/pemimpin prosesi untuk akad pada lokasi rencana. Chunk tidak membahas hujan, penilaian garden versus alternatif tertutup, kesiapan vendor setelah pindah atau kewenangan aktivasi rain plan. Syarat area siap yang umum tidak cukup menjadi support substantif pengalihan lokasi.|
|WO-DEV-010|0→0|Rute pasangan perlu terkonfirmasi, tetapi tidak ada survei akses pantai, jalur kendaraan/perlengkapan, pembatasan pengelola atau pemeriksaan kondisi lokasi. Konfirmasi rute pengantin pada akad bukan pemeriksaan beach access.|
|WO-DEV-011|0→0|Slot keluarga inti dan laporan PIC pengantin tidak memuat aturan pengungkapan kehadiran tamu, verifikasi pihak penanya atau batas informasi guest desk. Tidak ada dukungan untuk keputusan disclosure.|
|WO-DEV-012|0→0|Urutan layanan MUA dan prioritas dokumentasi foto bukan evaluasi pasca-acara. Tidak ada penyusunan action item, pemilik, tenggat, verifikasi hasil atau pemantauan perbaikan setelah debrief.|
|WO-DEV-013|2→2|Chunk langsung menyatakan makeup saja belum cukup: pakaian, benda prosesi, pendamping dan rute harus terkonfirmasi; PIC pengantin melapor ke WC dan floor menunggu kesiapan area/pemimpin prosesi. Ini support langsung untuk kriteria menyatakan pasangan siap. Teks tidak menyatakan makeup selesai berarti sudah tiba standby; acuan waktu tetap simulasi, bukan jaminan kesiapan.|
|WO-DEV-014|0→0|Foto pasangan dan rute menuju prosesi tidak menjelaskan LO atau rekonsiliasi kelompok shuttle chapel-ke-dinner. Tidak ada daftar naik/tiba, hitungan kelompok atau penerima di tujuan.|
|WO-DEV-015|0→0|Slot keluarga inti berkaitan urutan layanan makeup, bukan alokasi kursi ballroom. Tidak ada rekonsiliasi daftar tamu, pemeriksaan kursi reserved, kapasitas venue atau dampak layanan sebelum menambah seating.|
|WO-DEV-016|0→0|Tidak ada permintaan makanan khusus, penyedia catering, konfirmasi ketersediaan atau batas janji guest desk. Permintaan perkiraan selesai MUA tidak dapat digunakan sebagai jawaban terhadap kebutuhan makanan tamu.|
|WO-DEV-017|0→0|Batas menggeser akad karena sesi foto adalah konteks pagi yang berbeda dari sambutan dan dinner. Tidak ada kesiapan catering, buffer sambutan, urutan dinner atau pertimbangan penyesuaian rundown pada fase resepsi; kesamaan kata jadwal tidak menjadi support substantif.|
|WO-DEV-018|0→0|Laporan kesiapan PIC pengantin ke WC tidak menyediakan paket handover pengganti, outstanding, penerimaan tanggung jawab atau acknowledgment. Kehadiran jalur laporan tidak sama dengan proses memastikan serah terima antar-PIC diterima.|

### Positive evidence dan batas interpretasi

**WO-DEV-003 — grade1**

> Waktu siap dinilai setelah makeup, pakaian, benda prosesi, pendamping, dan rute terkonfirmasi. PIC pengantin melapor kepada WC; floor menunggu kesiapan area serta pemimpin prosesi.

**WO-DEV-004 — grade1**

> Layanan pasangan direncanakan mulai 06.00 WITA, disusul dressing dan pemeriksaan siap sebelum standby akad dan keluarga 08.45 WITA, mengikuti rundown simulasi WO-DOC-042. Akad direncanakan 09.00. Jam ini merupakan asumsi rundown EVT-02 dan harus diperiksa bersama vendor sebelum dipakai nyata. Keluarga inti menerima slot yang disepakati tanpa mengambil waktu pasangan. PIC pengantin meminta perkiraan selesai pada titik kerja yang disetujui, bukan terus-menerus menyela.

**WO-DEV-013 — grade2**

> Waktu siap dinilai setelah makeup, pakaian, benda prosesi, pendamping, dan rute terkonfirmasi. PIC pengantin melapor kepada WC; floor menunggu kesiapan area serta pemimpin prosesi.

003 tetap1 karena kriteria kesiapan pasangan/floor dapat membantu sebagian cue entrance, tetapi akad EVT-02 bukan C03 resepsi. Ini boundary transferability yang subjektif; tidak semua analogi fase diberi partial relevance.004 tetap1 karena acuan jadwal/perkiraan selesai membantu tetapi chunk tidak merinci data konfirmasi layanan sebelum hari acara; klarifikasi08.45 tidak otomatis menaikkan grade.013 tetap2 karena readiness criteria langsung substantif untuk query, tanpa menganggap makeup selesai berarti sudah tiba standby. Sumber lain pada provenance tidak dipakai untuk melengkapi grade chunk ini.

**Grade changes0, unchanged after fresh semantic rejudgment18.** Alasan seluruh18 diganti dengan hasil assessment baru; excerpt003/013 diperluas dan004 kini mengutip full paragraph V2. Tidak ada fabricated disagreement atau grade change untuk menunjukkan progres. Semua18 dapat diberi keputusan eksplisit; uncertain0. Jika verifikasi manusia nanti berbeda, buat qrels version/change log baru, jangan overwrite hasil ini.

## Coverage dan positive evidence audit

| Query | Judged | Unjudged | Carried | Rejudged | Grade0 | Grade1 | Grade2 |
|---|---:|---:|---:|---:|---:|---:|---:|
|WO-DEV-001|38|333|37|1|36|1|1|
|WO-DEV-002|38|333|37|1|36|1|1|
|WO-DEV-003|38|333|37|1|31|5|2|
|WO-DEV-004|38|333|37|1|35|1|2|
|WO-DEV-005|38|333|37|1|36|0|2|
|WO-DEV-006|38|333|37|1|35|1|2|
|WO-DEV-007|38|333|37|1|35|2|1|
|WO-DEV-008|38|333|37|1|34|3|1|
|WO-DEV-009|38|333|37|1|31|4|3|
|WO-DEV-010|38|333|37|1|36|1|1|
|WO-DEV-011|38|333|37|1|34|2|2|
|WO-DEV-012|38|333|37|1|35|1|2|
|WO-DEV-013|38|333|37|1|33|3|2|
|WO-DEV-014|38|333|37|1|35|2|1|
|WO-DEV-015|38|333|37|1|34|2|2|
|WO-DEV-016|38|333|37|1|37|0|1|
|WO-DEV-017|38|333|37|1|34|2|2|
|WO-DEV-018|38|333|37|1|34|1|3|

Setiap query mempunyai38 judged (37 carried+1 rejudged) dan333 unjudged. Total684+5994=6678. Query–chunk set sama persis dengan pool V1; tidak ada expansion. Manifest mencatat333 unjudged chunk IDs per query.027-C009 yang berubah tetap di luar pool. Missing pairs tidak diisi grade0;621 grade0 hanya pasangan yang memiliki judgment existing/rejudged eksplisit.

Seluruh63 positive pairs memiliki exact evidence pada chunk V2, source file/locator/content hash valid:60 inherited dan3 rejudged. Exact substring/ref match membuktikan keberadaan evidence, **bukan membuktikan seluruh grade benar**. Positives63 adalah pasangan, bukan63 unique chunks. Seluruh negative reasons inherited tetap memiliki keterbatasan review9A.4;621 negatives tidak mendapatkan independent reassessment pada milestone ini.

## Validation checks

PASS: unique684 pairs;18 valid query IDs/unchanged text hashes;371 valid corpus IDs;50 document/source mapping; correct V2 snapshot/fingerprint; all grade types/range; positive evidence exact match; active42 provenance bindings; historical fields disjoint; old/new grade logs; JSONL/manifest readback; input/output hashes; all-query coverage; unknown accounting; AI-only status.

**8 negative mutation self-checks PASS**: duplicate pair, invalid grade3, wrong query hash, wrong snapshot, invalid locator, fabricated evidence, pair moved outside pool, false human-validation claim semuanya ditolak validator pada in-memory copies. Checks ini tidak menulis corrupted files atau membuat judgments. Independent readback pass juga membandingkan seluruh666 retained grades/reasons/evidence/timestamps dengan V1 dan18 new decisions dengan explicit decision records. Tidak menjalankan ingestion, retrieval, GPU atau benchmark tests; tidak ada production code diubah.

Readback awal menemukan masalah Python integer keys pada grade distribution versus JSON string keys; representasi manifest dinormalisasi menjadi string keys dan seluruh checks diulang PASS. Intermediate draft files disimpan hanya di temporary diagnostic directory di luar repository. Bug ini tidak mengubah keputusan semantik atau protected files.

## Status silver ground truth dan limitations

**PARTIAL MIGRATION COMPLETE — NOT COMPLETE GROUND TRUTH.** Corpus V2 disetujui sebagai development pilot, bukan corpus final. Qrels ini AI silver provisional dan18 queries tetap draft.10,2426% universe judged;89,7574% unknown. Tidak memenuhi exhaustive ground truth atau main benchmark validation gates.

Benchmark protocol existing masih memuat workflow human/qualified assessor, independent subset/adjudication, main query validation dan supervisor approval. Instruksi pengguna mengizinkan **development-only AI migration**; itu tidak mengubah protocol atau memenuhi main evaluation requirements secara otomatis. Jangan memakai hasil ini untuk klaim final Recall/MRR/nDCG, tuning test set atau expert validation.

Risiko: inherited assessment errors pada666 rows; subjective partial-relevance boundaries; synthetic corpus/query circularity; purposive candidate-pool bias; relevant evidence pada333 unknown chunks per query mungkin terlewat; same-AI self-check bukan inter-rater reliability; enam corpus issues unresolved; backend/duration provenance terbatas. Koreksi internal standby/closure tidak membuktikan skenario WO nyata akurat.

## Integrity dan artifact identity

**629/629 existing files unchanged SHA-256** terhadap baseline sebelum task. Cakupan: seluruh source/candidate V1/V2, canonical docs/chunks, snapshots/config/protocol, original18 queries/provenance, V1 qrels/manifest, existing reports/workbooks/code/tests/scripts, README/pyproject/.gitignore dan cache project R1/R2/R3 indices/runs. `.venv` digunakan tanpa instalasi; environment tree tidak di-hash menyeluruh. Tidak ada Git repository tersedia; audit memakai filesystem/hashes.

V2 snapshot tetap mengikat explicit original artifact set. Penambahan folder `benchmark/` adalah extension dataset, bukan perubahan corpus snapshot; snapshot JSON/fingerprint tidak diregenerasi. Benchmark extension memiliki manifest/hash/fingerprint sendiri, tanpa mengklaim mengubah arti fingerprint corpus.

| Artifact | SHA-256 |
|---|---|
|`data/validation/pilot_snapshot.json`|`279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e`|
|`data/versions/v2_ai_corrected/validation/pilot_snapshot.json`|`6658fee4737c0d2fa725ee31cb647ec638de350fc2ccfe669999847ac2331b07`|
|`data/chunks/chunks.jsonl`|`2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0`|
|`data/versions/v2_ai_corrected/chunks/chunks.jsonl`|`0cfad810122cde84be55b1fedb330c98aafbe30e14ea0168699212382dd4c5ba`|
|`data/benchmark/development_queries_draft.jsonl`|`27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95`|
|`data/benchmark/development_qrels_ai_silver_v1.jsonl`|`786922e8285a7ec9d311ca84e1b2371068a4ec0ffd7aa31d6e31438d060927ed`|
|`data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl`|`0b5fb1a281b451bdc5ab585ef04a007aea6a961628a816338302ea6bf28777d2`|
|`data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2_manifest.json`|`3e01c056225111b68c0c30fd76073630740a9e3c42d88206f2e84e6b35ea00a9`|
|`data/versions/v2_ai_corrected/benchmark/development_qrels_v1_v2_change_log.jsonl`|`5b67a4bfe285169d7b04f7ff8a6168f00fdf39315fb024467f33e291a31d095d`|
|`data/versions/v2_ai_corrected/benchmark/development_query_provenance_v2.jsonl`|`957d7b81b9ab6c86a085c040c0b5f86d2afc0f86f8046c375456023ab1c4ef22`|

Migration artifact fingerprint: `5fff8235ad385082ac1f7c8f5b99818a19fc69e29fcff001b778dfda301c1f82`. Payload=SHA-256 UTF-8 compact sorted-key JSON mapping inputs,outputs,snapshot_fingerprint seperti manifest. Manifest self-hash dan laporan Markdown ini dikecualikan untuk menghindari siklus. Snapshot fingerprint V2 tetap `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

## Deliverables dan rekomendasi berikutnya

Dibuat tepat5 file baru, tanpa mengubah file existing:

- `data/versions/v2_ai_corrected/benchmark/development_query_provenance_v2.jsonl` —18 bindings/42 active refs; original query text tetap.
- `data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl` —684 provisional AI rows dengan carry/rejudgment provenance terpisah.
- `data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2_manifest.json` —input/output hashes, eligibility receipts, coverage, statuses dan limitations.
- `data/versions/v2_ai_corrected/benchmark/development_qrels_v1_v2_change_log.jsonl` —684 migration events termasuk18 full semantic rejudgment records;0 numeric grade changes.
- `experiments/reports/milestone_9a7_v2_query_qrels_migration.md` —laporan ini.

**Recommended next task, belum dijalankan:** review paket9A.7, lalu persetujuan terpisah untuk versioned V2 index binding/rebuild R1/R2/R3. New indices harus memakai V2 snapshot/371 shared serialized inputs dan paths/cache identity terpisah; original V1 indices dipertahankan. Konsumen query/qrels perlu explicit V2 provenance overlay dan hashes manifest baru; jangan menganggap original query metadata atau inherited grades sudah human validated. R4 memakai komponen V2 setelah readiness checks; tidak perlu menulis ulang fusion. BGE-M3/resource gates dan end-to-end verification tetap pekerjaan terpisah, bukan dianggap PASS dari migration ini.

**STOP setelah9A.7.** Tidak ada index rebuild, BGE-M3/GPU/query embeddings, retrieval effectiveness/Recall/MRR/nDCG,75 final queries, protocol edits, instalasi/download, commit/push/PR/deploy.
