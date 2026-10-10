# Panduan review corpus oleh peneliti

Paket ini menyiapkan **researcher-based content review** atas 50 dokumen WO dan
review peneliti atas 18 query development. Perubahan metodologi, termasuk single-assessor
relevance judgment, **masih menunggu persetujuan dosen pembimbing** sebelum menjadi
dasar evaluasi utama. Judul penelitian tetap. Paket ini tidak menyatakan dokumen atau
query sudah disetujui, dan bukan independent expert validation.

Dokumen adalah draft operasional susunan peneliti dengan bantuan AI dan skenario
simulasi, bukan arsip autentik perusahaan WO. Review sendiri tidak mengubah asal-usul
tersebut atau membuktikan prosedur berlaku umum di industri.

## Urutan kerja

1. Buka **corpus_researcher_review.xlsx**, sheet **Independent Review**. Mulai dari
   lima dokumen pilot pada tabel di bawah. Baca dokumen lengkap sesuai Source path,
   relatif terhadap root project. Untuk XLSX, baca seluruh sheet dan konteks header.
2. Isi checklist tetap tanpa melihat rincian AI preliminary findings, keputusan AI,
   atau catatan rekonsiliasi. Reviewer role sudah `researcher`; isikan Researcher ID,
   tanggal dan durasi sebenarnya sendiri. Sel kuning masih kosong.
3. Setelah pilot, evaluasi kejelasan checklist. Jika definisinya perlu diubah, tetapkan
   versi checklist baru dan ulangi lima dokumen dengan definisi yang sama sebelum
   melanjutkan sisa dokumen. Catat versi checklist pada Researcher notes.
4. Catat hasil awal **seluruh 50 dokumen** sebelum membuka workbook AI yang memuat
   temuan seluruh corpus. Simpan hasil Stage 1 sebagai rekaman bertanggal yang tidak
   ditimpa; catat nama file, versi checklist dan SHA-256 untuk rujukan Stage 2.
   Jika belum dapat memutuskan, tulis alasan dan Needs clarification, bukan menebak.
5. Baru setelah rekaman awal tersimpan, buka temuan AI dan isi sheet **Reconciliation**.
   Jangan mengganti hasil Stage 1 dengan hasil akhir. Keputusan AI tidak disalin
   otomatis dan tidak wajib diikuti.

“Independen” di sini berarti penilaian awal dilakukan tanpa memakai rincian screening
AI. Peneliti tetap penyusun corpus dan satu-satunya reviewer; ini **bukan penilai
independen atau ahli domain eksternal**. Angka screening 30 conceptual approve,
20 revise, 0 reject sudah diketahui dari informasi awal. Catat paparan ini; jangan
mengklaim peneliti sepenuhnya blinded. Jika sudah melihat temuan per dokumen,
catat dokumen serta waktu paparannya dan batas independensi yang tersisa.

## Checklist tetap Stage 1 — researcher-content-checklist-v1

| Aspek | Yang diperiksa |
|---|---|
| Operational relevance | Ada kebutuhan kerja WO yang jelas dan isi membantu tugas tersebut. |
| Procedural plausibility | Urutan, prasyarat, kewenangan dan batas tugas masuk akal berdasarkan isi serta rujukan yang tersedia. Kewajaran bukan bukti akurasi ahli. |
| Internal consistency | Peran, angka, waktu, istilah, versi dan rujukan selaras di dalam dokumen dan dokumen terkait. |
| Completeness | Tujuan, pelaksana, kondisi awal, langkah, hasil, pengecualian dan eskalasi yang dibutuhkan tersedia. |
| Ambiguity | Ada instruksi, istilah, subjek atau skenario yang dapat ditafsirkan berbeda. Sebutkan lokasinya. |
| Unsupported claims or assumptions | Ada klaim kapasitas, waktu, keselamatan, kewenangan atau generalisasi yang tidak didukung; bedakan asumsi simulasi yang dinyatakan dari fakta terverifikasi. |

Empat aspek pertama: **Memadai / Perlu revisi / Tidak dapat menilai**.
Dua aspek terakhir: **Tidak ditemukan / Ditemukan / Tidak dapat menilai**.
“Tidak ditemukan” terbatas pada review yang dilakukan, bukan jaminan tidak ada masalah.
Tulis heading/halaman/sheet/baris, masalah, dasar pertimbangan dan koreksi dalam notes.
Jika tidak ada rujukan yang mendukung klaim penting, nyatakan keterbatasannya.

Keputusan peneliti:

- **Approve:** layak untuk lingkup corpus penelitian yang dinyatakan; tidak ada
  koreksi wajib yang belum diselesaikan menurut checklist. Bukan sertifikasi praktik WO.
- **Revise:** masalah dapat diperbaiki; tulis koreksi wajib dan kebutuhan pemeriksaan ulang.
- **Reject:** tidak layak dalam lingkup tersebut; jelaskan alasannya.

Review status adalah progres pencatatan lokal: In progress, Stage 1 complete atau
Needs clarification. Stage 1 complete tidak berarti corpus validated/frozen.
Semua pilihan, keputusan, tanggal dan status awal tetap kosong sampai Anda mengisinya.

## Pilot dan waktu review

| Urutan | Dokumen | Fokus percobaan checklist |
|---|---|---|
| 1 | WO-DOC-001 — Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer | Peran, delegasi dan konsistensi komando; kategori A, DOCX. |
| 2 | WO-DOC-008 — Checklist Final Preparation H-7 hingga H-1 | Prasyarat, tenggat dan kriteria kesiapan; kategori B, XLSX. |
| 3 | WO-DOC-021 — Panduan Sinkronisasi Catering dan Banquet Service | Batas layanan dan kewenangan vendor; kategori D, PDF. |
| 4 | WO-DOC-030 — Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara | Pilihan tindakan serta dampak perubahan; kategori E, TXT. |
| 5 | WO-DOC-040 — Matriks Seating Allocation dan Penugasan Guest Escort | Alokasi, escort dan konsistensi antar-sheet; kategori G, XLSX. |

Mulai stopwatch saat membaca satu dokumen, berhenti setelah penilaian dan komentar
selesai; keluarkan jeda istirahat. Isi detik aktif pada Review duration. Waktu Stage 2
dicatat terpisah pada Reconciliation duration. Jangan menebak durasi yang tidak tercatat.
Setelah pilot, lanjutkan ID lain secara berurutan tanpa mengulang item yang sudah dicatat,
kecuali checklist berubah. Lima dokumen ini bukan sampel untuk mengklaim seluruh corpus
valid; semua 50 tetap memerlukan pencatatan review dan penyelesaian keputusan.

## Stage 2 — rekonsiliasi dengan screening AI

Workbook AI belum ditemukan di project saat paket ini disiapkan. Gunakan artifact
yang Anda sediakan kemudian; catat nama file, tanggal/versi dan SHA-256. Jumlah
30/20/0 adalah informasi preliminary dari pengguna, belum diverifikasi terhadap file,
dan tidak menentukan dokumen mana yang boleh di-Approve.

Per dokumen, isi rujukan rekaman Stage 1 dan salin **keputusan awal Anda sendiri** ke
Stage 1 recorded decision sebagai nilai tetap. Jika keputusan awal belum ada,
biarkan kolom itu kosong dan jelaskan alasannya dalam notes. Kemudian:

1. Catat lokasi dan ringkasan temuan AI, lalu periksa ulang bagian source yang terkait.
2. Tuliskan apakah temuan didukung, tidak didukung atau belum dapat dipastikan,
   beserta dasar kesimpulannya. Jangan menerima klaim AI hanya karena terdengar meyakinkan.
3. Isi Reconciled researcher decision, Decision changed? dan alasan. Perubahan dari
   keputusan kosong ke keputusan baru juga dicatat sebagai perubahan. Bila keputusan
   tetap tetapi koreksi berubah, catat perubahan koreksi dan alasannya.
4. Pertahankan hasil awal, hasil akhir dan masalah yang masih terbuka. Reconciled berarti
   pembandingan telah dicatat, bukan persetujuan pembimbing atau pengesahan seluruh corpus.

Rekonsiliasi ini dilakukan oleh peneliti yang sama, bukan adjudication dua assessor.
Tanpa artifact AI, biarkan Stage 2 kosong/tertunda; Stage 1 tetap bisa disiapkan/dijalankan.

## Review 18 query development

Gunakan **development_query_review.xlsx existing**, tanpa membuat salinan dataset
baru atau mengubah query_text. Reviewer berperan sebagai peneliti, meskipun panduan
lama menyebut praktisi. Untuk penilaian awal, gunakan sheet Review dan source asli;
tunda membuka Evidence serta usulan AI/editorial sampai catatan awal tersimpan.
Nilai kejelasan, satu information need, answerability, asumsi, jargon, naturalitas
dan kemungkinan redundansi. Label lexical/semantic/mixed bukan prediksi metode unggul.

Enam catatan editorial 003, 006, 013, 014, 015, 016 tetap bahan diskusi, bukan keputusan.
Sesudah review awal, bandingkan Evidence/catatan existing dan catat perubahan serta
alasannya pada reviewer_notes/suggested_rewording, tanpa menimpa catatan awal.
Gunakan reviewer_id peneliti sebenarnya dan catat role researcher dalam reviewer_notes.
Kolom validation_status dan current_draft_status tidak diubah menjadi expert_reviewed
atau frozen melalui paket ini. Revisi teks/status dataset memerlukan persetujuan dan
pembaruan skema/protokol tersendiri; semua 18 query sekarang tetap draft.

## Setelah review dan persetujuan metodologi

Jangan mengedit source pilot. Approve tetap melekat pada versi/hash yang direview.
Revise memerlukan koreksi dan review ulang; Reject dikeluarkan atau dikerjakan ulang
dengan keputusan terdokumentasi. Jika source berubah, peneliti menyiapkan corpus versi
baru di lokasi berbeda, menjalankan ulang extraction/chunking, memeriksa ID mapping,
query evidence dan qrels bila kelak ada, lalu membuat snapshot/fingerprint serta indeks
retrieval baru. Source, 371 chunks dan snapshot pilot lama tetap dipertahankan.

Single-assessor relevance judgment dilakukan **nanti**, terpisah dari review corpus
dan query, hanya sesudah metodologi disetujui dan corpus final ditetapkan. Peneliti
menilai pasangan query–chunk secara manual dengan rubric yang disetujui; AI tidak
menghasilkan qrels. Approve suatu dokumen atau pointer Evidence tidak otomatis memberi
grade relevansi. Tidak ada klaim inter-assessor agreement dari satu penilai.

Jangan memasukkan data pribadi klien sebenarnya. Pakai kode simulasi dan alasan
berdasarkan isi. Review peneliti tetap rentan confirmation bias, anchoring AI dan bias
corpus sintetis; catatan transparan membantu audit tetapi tidak menggantikan penilai
independen atau validitas eksternal.
