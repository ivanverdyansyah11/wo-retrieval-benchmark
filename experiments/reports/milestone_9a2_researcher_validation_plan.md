# Milestone 9A.2 — Researcher-based corpus validation preparation

Tanggal: 9 Oktober 2026. **Paket persiapan selesai; perubahan metodologi evaluasi utama
PENDING SUPERVISOR APPROVAL.** Judul penelitian tidak berubah. Tidak ada review,
keputusan corpus/query, relevance judgment atau persetujuan pembimbing yang dibuat
atas nama peneliti.

## Konteks dan batas perubahan

Snapshot acuan tetap `WO-CORPUS-V1-DRAFT-PILOT-001`: 50 researcher-composed operational
WO documents, 371 frozen chunks dan 18 draft development queries. Source merupakan
draft peneliti dengan bantuan AI dan skenario simulasi, bukan arsip autentik perusahaan.
Review peneliti tidak mengubah provenance ini menjadi data operasional lapangan.

Keputusan pengguna untuk menyiapkan researcher-based corpus review dan later
single-assessor relevance judgment dicatat sebagai arah metodologi yang diusulkan.
Paket ini menggantikan tujuan penggunaan paket praktisi untuk rencana review mendatang,
tetapi tidak menghapus atau menulis ulang paket/hasil historis 9A.1.

Protokol Markdown/TOML existing belum diubah. TOML masih menyebut primary assessor
WO domain expert, independent secondary reviewer, serta status expert_reviewed dan
pending_practitioner_validation. Ketentuan itu **belum dipenuhi dan tidak boleh dianggap
diam-diam telah diubah menjadi researcher review**. Setelah pembimbing menyetujui,
revisi protokol/skema status dan pencatatan kualifikasi harus dilakukan secara eksplisit
pada pekerjaan berikutnya sebelum evaluasi utama. R1–R4 dan parameter retrieval tetap.
Status dalam frozen snapshot adalah metadata historis yang dipertahankan, bukan klaim
bahwa validasi praktisi akan atau telah dilakukan.

## A. AI preliminary screening

Pengguna melaporkan 30 conceptual approve, 20 revise, 0 reject. Ini **bukan hasil review
peneliti, praktisi atau expert**, bukan ground truth, dan bukan persetujuan 30 dokumen.
Workbook AI preliminary belum ditemukan dalam daftar workbook repository; isi per
dokumen, cakupan dan hitungan tersebut belum dapat diverifikasi. Tidak dilakukan
screening AI baru atau pembuatan findings pengganti.

Ketika artifact disediakan, dokumentasikan nama/versi, checksum, tanggal dan asal
screening bila benar-benar tersedia; jangan mengarang provenance yang tidak ada.
Periksa ID mapping serta kecocokan source version/hash yang discreening. Temuan pada
versi berbeda ditandai belum cocok, bukan diterapkan ke source frozen. Detailed findings
baru dibuka setelah hasil awal seluruh 50 dokumen tersimpan. Informasi agregat yang sudah
diketahui serta paparan AI sebelumnya tetap diungkap sebagai keterbatasan blinding.

## B. Independent-first researcher content review

“Independent” dibatasi pada **review awal tanpa menggunakan rincian temuan AI**,
bukan independensi peneliti dari kepengarangan corpus, bukan external assessor dan
bukan independent expert validation. Reviewer role adalah `researcher`.

Checklist tetap `researcher-content-checklist-v1` memiliki enam dimensi:

1. Operational relevance: hubungan isi dengan kebutuhan tugas WO.
2. Procedural plausibility: kewajaran urutan, prasyarat dan batas kewenangan berdasarkan
   isi serta rujukan yang tersedia; tidak disamakan dengan expert-certified accuracy.
3. Internal consistency: keselarasan peran, istilah, angka, waktu dan rujukan lintas dokumen.
4. Completeness: kecukupan tujuan, pelaksana, langkah, hasil, pengecualian dan eskalasi.
5. Ambiguity: instruksi atau skenario yang memungkinkan penafsiran berbeda.
6. Unsupported claims or assumptions: klaim tanpa dukungan, atau asumsi simulasi yang
   disajikan seolah fakta nyata. Batas ketidakmampuan peneliti menilai harus dicatat.

Empat dimensi pertama memakai Memadai / Perlu revisi / Tidak dapat menilai; dua terakhir
Tidak ditemukan / Ditemukan / Tidak dapat menilai. Ini pilihan input manual, bukan skor
numerik atau cut-off otomatis untuk keputusan. Alasannya ditulis dengan heading,
halaman, sheet/baris dan rujukan yang benar-benar tersedia.

Peneliti mengisi Approve / Revise / Reject sendiri. Approve berarti layak dalam lingkup
penelitian menurut checklist, tidak berarti prosedur benar secara universal. Revise
memerlukan koreksi wajib dan review ulang. Reject memerlukan alasan. Jika belum dapat
menentukan keputusan, catat Needs clarification dan alasannya; jangan memaksa approval.

Catat durasi aktif dan tanggal sebenarnya. Semua Stage 1 records harus tersimpan sebelum
akses detailed AI workbook; arsipkan hasil awal dengan versi checklist dan checksum.
Pengarsipan hasil manual nanti diperlukan untuk jejak perubahan, tidak dibuat sekarang.

## C. Researcher decision reconciliation

Stage 2 memakai sheet terpisah. Catat rujukan rekaman awal yang tidak ditimpa, keputusan
awal peneliti sebagai nilai tetap, referensi/checksum AI artifact, finding locator,
temuan AI dan verifikasi ulang terhadap source. AI finding dapat diterima, ditolak atau
dibiarkan belum terselesaikan berdasarkan alasan dokumenter, bukan karena keputusan AI.

Simpan keputusan rekonsiliasi, indikator perubahan, alasan dan koreksi yang diperlukan.
Alasan wajib dicatat bila keputusan berubah; perubahan koreksi walaupun keputusan tetap
juga dicatat. Keputusan awal yang kosong tidak diisi retrospektif seolah telah diputuskan.
Tidak ada formula yang menghubungkan keputusan awal ke keputusan akhir atau menyalin
hasil AI. Ini reconciliation oleh orang yang sama, **bukan adjudication antar-assessor**.
Tanpa AI artifact, Stage 2 masih tertunda; hal itu tidak menghalangi persiapan Stage 1.

## Workbook peneliti

Workbook baru diturunkan dari metadata `corpus_expert_review.xlsx` existing dan dicocokkan
dengan manifest. Template expert dan query existing tidak ditimpa. Dua sheet memiliki
fungsi berbeda, masing-masing 50 baris unik, bukan dua kumpulan keputusan baru.

| Sheet | Struktur |
|---|---|
| Independent Review, A1:R51 | A–D: ID/title/category/source path; E–J: enam dimensi checklist; K: researcher decision; L: required corrections; M: notes; N: duration seconds; O: review date; P: review status; Q: reviewer role; R: researcher ID |
| Reconciliation, A1:Q51 | A: ID; B–C: rekaman dan keputusan awal; D–F: artifact/checksum AI, locator, finding; G: source verification; H–K: keputusan akhir, berubah/tidak, alasan, koreksi; L–O: notes, durasi, tanggal, status; P–Q: role dan researcher ID |

**Stage 1: 600 sel assessment E2:P51 dan 50 sel researcher ID kosong.**
**Stage 2: seluruh 750 sel input B2:O51/Q2:Q51 kosong**, termasuk hasil AI dan keputusan
awal/akhir. Hanya metadata ID/title/category/path dan role konstan `researcher` yang
terisi. Tidak ada reviewer identity, tanggal, durasi, temuan, status atau judgment palsu.

Status workbook hanya progres kerja lokal: In progress / Stage 1 complete /
Needs clarification pada Stage 1; In progress / Reconciled / Needs clarification pada
Stage 2. Semua awalnya kosong. Status tersebut bukan enum dataset baru, bukan expert_reviewed,
validated atau frozen; tidak mengubah source manifest/query JSONL.

Kedua sheet memiliki tabel/filter, freeze headers/identitas, wrapping, kolom input kuning,
dropdown dan format detik/tanggal. Tidak ada formula, hasil AI atau statistik screening
pada Independent Review. Panduan terpisah menjelaskan urutan, checklist dan batas klaim.

## Pilot review

Urutan Stage 1 awal, sesuai daftar pengguna:

| Urutan | Dokumen | Kategori/format dan tujuan pilot |
|---|---|---|
| 1 | WO-DOC-001 — Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer | A / DOCX; pembagian peran dan jalur komando |
| 2 | WO-DOC-008 — Checklist Final Preparation H-7 hingga H-1 | B / XLSX; prasyarat, tenggat dan kriteria kesiapan |
| 3 | WO-DOC-021 — Panduan Sinkronisasi Catering dan Banquet Service | D / PDF; batas tanggung jawab layanan vendor |
| 4 | WO-DOC-030 — Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara | E / TXT; pilihan tindakan dan dampak perubahan |
| 5 | WO-DOC-040 — Matriks Seating Allocation dan Penugasan Guest Escort | G / XLSX; konsistensi alokasi dan sheet perubahan |

Lima kategori dan empat format dipilih untuk mencoba keterpakaian checklist, bukan
sampling statistik untuk menyatakan seluruh corpus layak. Stopwatch per item mengukur
waktu membaca sampai komentar/keputusan selesai, tidak termasuk jeda. Stage 2 dicatat
terpisah. Tidak ada durasi atau hasil pilot yang dibuat sekarang.

Sesudah pilot, tetapkan checklist yang digunakan untuk sisa 45 dokumen. Jika definisi
berubah, catat versi dan periksa ulang lima item agar konsisten. Selesaikan pencatatan
awal semua 50 sebelum membuka temuan AI seluruh corpus untuk mencegah leakage ke
review dokumen yang belum dinilai. Semua dokumen memerlukan keputusan/penyelesaian
terdokumentasi sebelum corpus final ditetapkan.

## D. Corpus revision and versioning

| Keadaan | Kebijakan yang direncanakan |
|---|---|
| Approve tanpa perubahan | Keputusan melekat pada document ID, source hash, versi corpus dan checklist yang direview; bukan persetujuan versi lain. |
| Revise | Catat koreksi wajib, bagian terdampak, alasan, penanggung jawab dan hasil review ulang. Belum dianggap approved. |
| Reject | Dokumentasikan penolakan; keluarkan dari calon corpus final atau kerjakan ulang dan review kembali. Jangan silently menghapus dari snapshot lama. |
| Source berubah | Gunakan lokasi/versi corpus baru yang terpisah dan changelog; jangan overwrite original frozen pilot. Nama/lokasi versi baru ditentukan pada task implementasi yang disetujui. |

Setelah perubahan diizinkan dan dilakukan, urutan wajib adalah:

1. Simpan source versi baru dengan provenance, checksum dan hubungan ke versi sebelumnya.
2. Jalankan ulang extraction/canonicalization/chunking melalui pipeline yang berlaku;
   jangan mengedit documents.jsonl/chunks.jsonl lama secara manual.
3. Periksa ulang parsing, coverage dan chunk quality; document ID dapat mempertahankan
   lineage bila sesuai, tetapi block/chunk ID atau locator dapat berubah. Buat mapping
   old-to-new dan daftar removed/changed/new; jangan mengasumsikan ID tetap stabil.
4. Audit ulang seluruh query evidence dan answerability; review ulang query yang
   terdampak. Qrels belum dibuat. Jika kelak ada, ikat ke snapshot asal dan jangan
   menyalin grades otomatis ke chunks baru; rejudge pasangan terdampak.
5. Buat snapshot dan fingerprint baru setelah cakupan final serta keputusan review
   terdokumentasi. Status review baru harus dibedakan dari expert validation dan
   diselaraskan dengan skema/protokol yang disetujui.
6. Rebuild indeks corpus R1/R2/R3 terhadap snapshot baru dan verifikasi mapping/serializer;
   R4 menggunakan komponen R2/R3 final yang cocok. Jangan memakai indeks pilot stale
   atau mencampur hasil antar-snapshot sebelum benchmark.

Tidak satu pun perubahan source, pipeline, snapshot, evidence atau indeks tersebut
dijalankan pada milestone persiapan ini.

## Query review: tetap 18 draft

Gunakan development_query_review.xlsx existing. Peneliti mengisi penilaian manual dengan
role researcher yang dicatat pada reviewer_notes; reviewer_id tidak diisi oleh sistem.
Stage awal menilai satu information need, naturalitas, answerability, skenario, jargon,
asumsi dan redundansi menggunakan pertanyaan asli dan dokumen lengkap. Simpan catatan
awal sebelum membaca Evidence/pointer AI dan usulan editorial existing.

Kemudian bandingkan dengan evidence/catatan, termasuk 003,006,013,014,015,016. Usulan
rewording serta alasan ditulis tanpa mengganti query_text atau JSONL. Pertahankan
catatan awal dan rekonsiliasi dalam notes; reviewer dapat menyimpan hasil awal
bertanggal untuk jejak perubahan. Jangan menyebut hasil reviewer peneliti sebagai
expert_reviewed hanya karena istilah itu tersedia dalam skema lama. Kolom status
judgment sekarang tetap kosong dan current_draft_status tetap draft_pending_expert_review.

## E. Later single-assessor relevance judgments

**PROPOSED, belum dijalankan.** Setelah persetujuan pembimbing, pembaruan protokol dan
corpus/query yang sesuai telah ditetapkan, peneliti menjadi satu assessor manual untuk
pasangan query–chunk. Corpus review dan query review tidak menghasilkan qrels.
AI screening, keputusan Approve dan evidence pointer tidak dikonversi menjadi grade.

Pertahankan pembedaan judged nonrelevant dan unjudged: yang belum dinilai tetap unknown,
bukan grade0. Rubric graded0/1/2, threshold relevan, pool/census, audit coverage,
penanganan incomplete qrels dan timing judgment harus ditetapkan/disetujui melalui
revisi protokol sebelum evaluasi; paket ini tidak memilih kebijakan baru berdasarkan
hasil retrieval. Parameter R1–R4 tidak diubah.

Catat assessor identity/role/latar belakang sebenarnya, rationale, source locator,
tanggal, rubric/qrels version dan snapshot. Bila memungkinkan, sembunyikan method label,
score dan hasil perbandingan saat memberi judgment; jangan tuning pada final test.
Kalibrasi rubric memakai development, bukan hasil test. Penilaian ulang subset oleh
orang yang sama setelah jeda dapat diusulkan untuk konsistensi intra-assessor dengan
subset/jeda ditetapkan lebih dulu; ini bukan inter-assessor agreement atau pengganti
external validation. Tidak ada qrels, calibration judgments atau agreement scores sekarang.

## Bias, keterbatasan dan persetujuan yang diperlukan

- Researcher/confirmation bias: penyusun menilai materi sendiri; checklist, catatan
  awal tetap dan alasan perubahan membantu audit tetapi tidak menghilangkan konflik ini.
- Anchoring AI: hasil awal seluruh corpus dicatat sebelum findings rinci dibuka;
  paparan agregat/per-dokumen yang sudah terjadi tetap harus dilaporkan.
- Synthetic corpus bias: istilah/skenario/query dapat mencerminkan gaya penyusun,
  bukan distribusi kebutuhan pengguna WO nyata. Jangan menggeneralisasikan validitas
  industri atau efektivitas lapangan dari corpus sintetis.
- Single-assessor limitation: tidak ada penilai independen untuk memeriksa keputusan;
  tidak dapat mengklaim external expert validation, inter-assessor reliability atau
  independent adjudication. Review ulang diri sendiri tidak mengatasi seluruh bias ini.

Persetujuan pembimbing masih diperlukan untuk penggunaan researcher review sebagai
metodologi utama, single-assessor judgment beserta cakupan/rubric/bias disclosure,
status/schema dataset baru dan perubahan protokol yang masih menyebut expert/secondary
assessor. Judul penelitian tetap; paket ini tidak mengubah naskah judul atau protokol aktif.

## Hasil pemeriksaan dan integritas

**PASS teknis:** workbook diekspor dengan Artifact Tool dan dibuka ulang read-only dengan
openpyxl. Dua sheet masing-masing 50 ID unik cocok manifest/metadata workbook existing;
semua judgment, status, identity, tanggal, waktu dan AI findings kosong. Role100sel
adalah researcher. Filter, pane C2/B2, dropdown, format detik/tanggal, jumlah kolom dan
ketiadaan formula diperiksa. Preview area metadata/input kedua sheet diperiksa visual;
error scan menemukan 0 formula errors. Microsoft Excel native belum dibuka, sehingga
uji input/dropdown UI sebenarnya tetap bagian pilot manual.

**PASS integritas:** semua **538 file baseline** tetap identik, termasuk 50 source,
canonical documents, 371 chunks, snapshot, 18 query/provenance, seluruh paket 9A.1,
protokol, kode serta indeks/cache R1/R2/R3. Semua 50 source hashes juga cocok manifest;
empat artifact hashes snapshot dan aggregate fingerprint dihitung ulang independen.
Workbook query masih mempunyai 198 sel judgment kosong dan teks sama dengan JSONL.

```text
snapshot_id: WO-CORPUS-V1-DRAFT-PILOT-001
aggregate fingerprint: 7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40
corpus_manifest.json: 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f
documents.jsonl: 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01
chunks.jsonl: 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0
pilot.toml: 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26
pilot_snapshot.json: 279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e
development_queries_draft.jsonl: 27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95
corpus_expert_review.xlsx: ec77820e45e4a03f97d2d8262f72800b15be1c56b511ec75992a03d22044b15e
development_query_review.xlsx: d13db552e11c28299e47ef7360ef2263e95ee0fff3f67ebbbe0072c66000a9a6
retrieval_protocol_v1.toml: dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300
```

Tepat tiga file deliverable baru: corpus_researcher_review.xlsx,
researcher_review_guide.md dan laporan ini. Evidence/script/preview sementara berada
di D:/ModelCache/tmp/wo-m9a2/, bukan file tambahan repository.

Selanjutnya secara manual: ajukan perubahan metodologi kepada pembimbing, lakukan
pilot Stage 1 dengan checklist dan stopwatch, catat hasil awal semua dokumen, lalu
sediakan/periksa AI workbook untuk rekonsiliasi. Review query tetap manual; revisi
corpus/protokol dan single-assessor qrels merupakan pekerjaan terpisah setelah izin.
Tidak ada source mutation, judgment otomatis, qrels, GPU inference, retrieval benchmark,
perubahan R1–R4, instalasi/download, commit, push, PR atau deployment. Milestone berhenti
pada paket persiapan; 8C tetap end_to_end_pending.
