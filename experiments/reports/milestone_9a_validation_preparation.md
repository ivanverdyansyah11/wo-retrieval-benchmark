# Milestone 9A.1 — Practitioner validation package preparation

Tanggal persiapan: 9 Oktober 2026. **Paket siap untuk review manusia; belum ada
validasi praktisi.** Snapshot `WO-CORPUS-V1-DRAFT-PILOT-001`, corpus `v1-draft`,
50 dokumen, 371 chunks. Status corpus tetap `pending_practitioner_validation`;
18 query tetap `draft_pending_expert_review`. Milestone 8C tetap `end_to_end_pending`.

## Paket dan aset yang digunakan

Tepat tiga file baru dibuat:

1. `data/validation/corpus_expert_review.xlsx`
2. `data/validation/practitioner_validation_guide.md`
3. `experiments/reports/milestone_9a_validation_preparation.md`

Workbook `data/validation/development_query_review.xlsx` existing dipakai tanpa
perubahan atau duplikasi. Checklist source tidak disalin atau diisi. Tidak ada
source, query, prototype retrieval, protokol, indeks atau environment yang diubah.
Script, hasil ekstraksi, pemeriksaan dan preview sementara berada di luar repository,
`D:/ModelCache/tmp/wo-m9a1/`.

Inspeksi mencakup manifest JSON/CSV/XLSX, FILE_INVENTORY.csv, DOCUMENT_SUMMARIES.md,
QUALITY_REPORT.md, VALIDATION_CHECKLIST.docx, seluruh 50 file operasional, canonical
records, audit query 7A/7B, 18 provenance records dan workbook review query.
Semua dokumen dibuka read-only: DOCX paragraf/tabel, PDF text layer, TXT UTF-8 dan
XLSX seluruh sheet termasuk Panduan/Perubahan. Ini inspeksi teknis isi, bukan
pengganti penilaian praktisi atau pemeriksaan visual setiap halaman source.

Distribusi format sesuai manifest: DOCX26, PDF9, XLSX10, TXT5. Sepuluh kategori
A–J memiliki jumlah 6/6/7/7/8/4/3/3/3/3. Jumlah file aktual documents/ adalah 50.
Manifest JSON/CSV/XLSX konsisten untuk ID, judul, kategori, format, nama file,
ringkasan dan SHA-256 dokumen. Semua 50 source hashes sesuai manifest dan inventory.

**Catatan inventory existing:** 56 dari 57 entri cocok terhadap hash dan ukuran
file yang dirujuk. Entri dokumentasi `README.md` memakai lokasi/hash authoring lama:
README aktual berada di root repository, bukan data/source_corpus/, dan telah
berkembang bersama project. Hash inventory `4aec8d828d1477eb6ae784c37b2445906d6009dfb05e6b9a61b66fc3b1c916e4`
berbeda dari README root aktual
`6998155b89e4ff5b0a097bb8753d9e60cd06b8be5b7fd3fbb172910dd97a049d`.
README root identik dengan baseline awal task ini. Inventory diperlakukan sebagai
metadata historis, tidak diperbaiki dan tidak dimasukkan ke corpus retrievable.
Ketidaksesuaian dokumentasi ini tidak menunjukkan perubahan pada 50 dokumen frozen.

## Workbook corpus

Satu sheet **Review Corpus**, tabel **CorpusExpertReview** pada A1:P51:
50 baris dokumen unik, urut WO-DOC-001 sampai WO-DOC-050, ditambah satu header.

| Kolom | Isi |
|---|---|
| A–E | Document ID, judul, kategori, jenis file, ringkasan isi |
| F–I | Relevansi operasional, akurasi prosedur, kelengkapan, realistis untuk praktik WO |
| J | Keputusan Approve / Revise / Reject |
| K–L | Koreksi yang disarankan, catatan reviewer |
| M | Durasi review dalam detik |
| N–O | Reviewer ID, tanggal review sebenarnya |
| P | Lokasi file operasional relatif terhadap root repository |

**Seluruh 500 sel F2:O51 kosong**, termasuk keputusan, catatan, durasi, identitas
dan tanggal. Tidak ada placeholder “belum dinilai” dalam sel judgment, nilai nol,
skor, formula atau persetujuan otomatis. Status pending dijelaskan pada panduan,
bukan ditulis sebagai jawaban reviewer.

Ringkasan disalin persis dari content_summary manifest, dengan sumber dicatat dalam
laporan ini dan lokasi dokumen per baris. Ringkasan bukan hasil validasi. Pada 40
dokumen naratif, ringkasan juga cocok dengan paragraf sumber setelah normalisasi
whitespace. Pada 10 XLSX, ringkasan merupakan metadata ringkasan konteks tabel;
tidak diklaim sebagai kutipan satu baris. Tabel dan sheet sumber tetap harus dibaca.

Workbook memiliki filter, header dan dua kolom identitas frozen (C2), wrapping,
lebar kolom yang disesuaikan, dan area input kuning. F–I menyediakan pilihan
Sesuai / Perlu koreksi / Tidak sesuai / Tidak dapat menilai; J menyediakan tiga
keputusan; M mempunyai aturan bilangan bulat tidak negatif. Semua nilai awal tetap
kosong. Dropdown membantu input, bukan pemeriksaan kelengkapan atau pengesahan.
Tanggal memakai format yyyy-mm-dd hh:mm; belum ada nilai tanggal yang diisikan.
Tidak ada tabel keputusan tambahan, skor penilaian, grafik atau salinan dokumen.

## Review query existing

Workbook existing memiliki sheet Review, Panduan dan Evidence. Semua 18 teks query
cocok persis dengan draft JSONL; 198 sel judgment F2:P19 tetap kosong. Kolom
current_draft_status tetap `draft_pending_expert_review`. Empat puluh dua evidence
pointers diverifikasi kembali terhadap ID dokumen, canonical block, heading,
source locator dan keberadaan file. Evidence bukan qrels, grade atau seluruh himpunan
chunk relevan; tidak menetapkan relevansi chunk lain.

Enam perhatian editorial tersedia sebagai **catatan peneliti untuk reviewer** dalam
panduan baru, terpisah dari kolom keputusan existing:

| Query | Fokus diskusi, bukan keputusan |
|---|---|
| WO-DEV-003 | Kejelasan kode C03 dan konteks entrance resepsi |
| WO-DEV-006 | Makna checkout sebagai serah terima aset setelah acara |
| WO-DEV-013 | Perbedaan makeup selesai, standby dan siap prosesi |
| WO-DEV-014 | Batas kelompok pengguna shuttle serta istilah LO/chapel/dinner |
| WO-DEV-015 | Tata bahasa pembuka dan kursi tampak kosong vs alokasi tersedia |
| WO-DEV-016 | Kealamian frasa kepastian informasi makanan khusus |

Panduan menunjuk usulan wording existing pada development_query_review.md tanpa
menyalin seluruh paket atau mengubah pertanyaan. Praktisi dapat mempertahankan,
mengusulkan revisi atau menolak; keputusan belum diisi.

## Pilot validasi yang diusulkan

Pemilihan purposive untuk mencoba alur review: lima kategori dan empat format.
Ini bukan sampling untuk mengestimasi akurasi domain seluruh corpus dan tidak
dipilih berdasarkan hasil retrieval.

| Dokumen | Kategori / format | Alasan dan aspek yang dicoba |
|---|---|---|
| WO-DOC-001 — Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer | A / DOCX | Peran, delegasi dan konsistensi komando lintas fungsi |
| WO-DOC-008 — Checklist Final Preparation H-7 hingga H-1 | B / XLSX | Checklist terstruktur, tenggat simulasi, kriteria kesiapan dan sheet Panduan |
| WO-DOC-021 — Panduan Sinkronisasi Catering dan Banquet Service | D / PDF | Koordinasi vendor, batas tanggung jawab layanan dan prasyarat keputusan |
| WO-DOC-030 — Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara | E / TXT | Keputusan contingency, dampak perubahan dan hak eskalasi |
| WO-DOC-040 — Matriks Seating Allocation dan Penugasan Guest Escort | G / XLSX | Alokasi kelompok, escort dan hubungan sheet Operasional/Perubahan/Panduan |

Pilot tidak mengubah status kelima dokumen. Praktisi mencatat waktu aktif nyata per
item; setelah itu peneliti dan praktisi meninjau kejelasan kolom dan kebutuhan sesi
lanjutan. Tidak ada estimasi durasi atau workload yang diklaim terukur sekarang.
Seluruh 50 dokumen tetap membutuhkan keputusan terdokumentasi. Revise membutuhkan
koreksi dan review ulang; Reject tidak dapat masuk corpus final tanpa penyelesaian
dan keputusan baru. Perubahan corpus nanti memerlukan versi/snapshot baru, bukan
penimpaan pilot frozen. Pilot lima dokumen tidak membekukan ground truth 75 query.

## Panduan dan pekerjaan manual

Panduan berbahasa Indonesia menjelaskan tujuan, sifat draft peneliti dengan bantuan
AI, cara membuka source/workbook, kriteria penilaian, pemetaan Approve/Revise/Reject
ke checklist existing, komentar berbasis lokasi, pencatatan detik aktif tanpa jeda,
serta larangan data pribadi klien nyata. Validasi dokumen, validasi query dan relevance
judgment dibedakan dengan jelas. Tidak ada permintaan grade relevansi 0/1/2.

Peneliti bersama praktisi masih perlu:

1. Menyepakati kode reviewer serta mendokumentasikan pengalaman/peran yang relevan.
2. Membaca panduan, membuka source asli dan mencoba lima dokumen pilot sambil
   mencatat durasi aktual serta masalah alur pengisian.
3. Mengisi keputusan, alasan dan koreksi sendiri; menyimpan hasil yang dapat ditelusuri
   tanpa menimpa source atau template kosong. Menilai seluruh 18 query termasuk enam
   catatan editorial, dengan revisi wording tetap sebagai usulan sampai disetujui.
4. Menjadwalkan sisa review, menyelesaikan koreksi dan review ulang sebelum corpus
   final ditetapkan. Tidak menganggap reviewer telah menyetujui apa pun dari paket ini.

## Pemeriksaan hasil dan integritas

**PASS:** XLSX berhasil diekspor dengan Artifact Tool, dibuka kembali read-only dengan
openpyxl dan diperiksa jumlah/keunikan ID, kesamaan metadata terhadap manifest,
lokasi source, 500 sel reviewer kosong, tabel/filter/freeze panes, pilihan dropdown,
aturan durasi, serta ketiadaan formula. Artifact error scan menemukan 0 formula
errors. Preview area metadata awal, kolom input dan baris terakhir diperiksa secara
visual: header/ringkasan terbaca, input kosong dan tidak ada konten terpotong pada
area yang diperiksa. Microsoft Excel native belum dibuka; perilaku UI dropdown dan
pengisian tanggal perlu dicoba saat pilot. Percobaan opsi API allowBlank yang tidak
didukung runtime tidak diterapkan pada workbook final; tidak ada judgment yang diisi.

**PASS:** seluruh **535 file baseline** identik, termasuk protected source, canonical,
chunks, snapshot, query/provenance, workbook query, protokol, kode retrieval, dan
R1/R2/R3 corpus indices/cache. Tidak ada perubahan file existing. SHA-256 empat
artifact snapshot dan aggregate fingerprint dihitung ulang secara independen.

```text
snapshot_id: WO-CORPUS-V1-DRAFT-PILOT-001
aggregate fingerprint: 7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40
corpus_manifest.json: 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f
documents.jsonl: 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01
chunks.jsonl: 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0
pilot.toml: 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26
pilot_snapshot.json: 279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e
development_queries_draft.jsonl: 27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95
development_query_provenance.jsonl: a880b60972e64c559e7dbe61e6b446a6d258914182e35c22e5c2520f62d05d59
development_query_review.xlsx: d13db552e11c28299e47ef7360ef2263e95ee0fff3f67ebbbe0072c66000a9a6
```

Evidence teknis berada pada D:/ModelCache/tmp/wo-m9a1/validation.json dan baseline.json.
Tidak ada GPU/model loading, embedding, retrieval/indexing, benchmark, qrels, instalasi,
download, commit, push, PR atau deploy. Pekerjaan berhenti pada persiapan paket.
