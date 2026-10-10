# Panduan review praktisi Wedding Organizer

Paket ini meminta masukan praktisi atas **50 dokumen operasional dan 18 pertanyaan
development**. Dokumen disusun peneliti dengan bantuan AI, memakai skenario simulasi;
bukan arsip autentik perusahaan atau prosedur yang sudah disahkan. Status corpus
`pending_practitioner_validation`, pertanyaan `draft_pending_expert_review`.
Snapshot acuan: `WO-CORPUS-V1-DRAFT-PILOT-001`.

## Mulai dari sini

1. Buka `corpus_expert_review.xlsx` pada folder yang sama dengan panduan ini.
   Gunakan sheet **Review Corpus**; satu baris untuk satu dokumen. Sel kuning adalah
   tempat mengisi penilaian. Kolom A–E dan P adalah informasi acuan, jangan diubah.
2. Buka dokumen asli sesuai kolom **Lokasi dokumen sumber**, relatif terhadap root
   project. Contoh: `data/source_corpus/documents/WO-DOC-001.docx`.
   Baca isi lengkap, bukan hanya ringkasan. Untuk XLSX, periksa seluruh sheet,
   termasuk Panduan dan Perubahan bila ada, beserta header dan konteks baris.
3. Untuk pertanyaan, gunakan **development_query_review.xlsx existing** di folder
   ini. Isi sheet **Review**; sheet **Panduan** menjelaskan kolom dan **Evidence**
   membantu mencari bagian dokumen. Jangan mengedit query_text atau informasi acuan.
4. Gunakan kode reviewer yang disepakati bersama peneliti, lalu isi tanggal dan waktu
   review sebenarnya. Peran/pengalaman reviewer dapat dicatat pada salinan checklist
   existing atau catatan reviewer. Jangan isi identitas atau tanggal sebelum review.
5. Simpan hasil review dengan nama yang dapat dibedakan dari template kosong.
   Jangan menimpa dokumen pada `data/source_corpus/`, query JSONL atau snapshot.

## Yang diperiksa pada dokumen

| Kolom | Pertanyaan untuk reviewer |
|---|---|
| Relevansi operasional | Apakah isi membantu kebutuhan kerja staf WO? |
| Akurasi prosedur | Apakah urutan, pembagian peran dan hak keputusan sesuai praktik? |
| Kelengkapan | Adakah prasyarat, pengecualian atau informasi penting yang belum ada? |
| Realistis untuk praktik WO | Apakah skenario, waktu, sumber daya dan istilah masuk akal? |

Pilih **Sesuai / Perlu koreksi / Tidak sesuai / Tidak dapat menilai** pada empat
aspek tersebut. Jelaskan batas pengetahuan atau perbedaan praktik venue bila perlu.
Gunakan juga aspek pada `data/source_corpus/VALIDATION_CHECKLIST.docx`: job description,
timeline, komunikasi/eskalasi, vendor, venue, contingency, kejelasan dan konsistensi
antar-dokumen. Checklist tersebut tetap sebagai acuan; jangan mengisi file source asli.

**Keputusan dokumen:**

- **Approve:** layak dalam lingkup yang diperiksa, tanpa revisi substantif yang masih
  wajib dilakukan. Setara makna dengan “Akurat” pada checklist existing.
- **Revise:** dapat digunakan setelah koreksi yang ditulis jelas dan diperiksa ulang.
  Ini belum persetujuan akhir.
- **Reject:** tidak layak untuk lingkup tersebut; jelaskan alasan dan masalah utamanya.

Jika belum bisa memutuskan, biarkan keputusan kosong dan tulis kebutuhan klarifikasi.
Kolom kosong berarti belum ada penilaian, bukan persetujuan atau nilai nol. Satu
Approve tidak mengesahkan dokumen lain atau seluruh corpus.

## Pertanyaan development dan catatan editorial

Nilai apakah bahasa staf terasa alami, skenario jelas, satu kebutuhan informasi dapat
dipahami, istilah sesuai, dan jawaban memang tersedia dalam dokumen. Gunakan pilihan
keputusan existing **accept / revise / reject / needs_discussion**, serta kolom yes/no
dan catatan sesuai Panduan workbook. Label lexical/semantic/mixed tidak menunjukkan
metode retrieval yang seharusnya unggul.

Enam catatan berikut adalah **bahan diskusi peneliti, bukan keputusan reviewer**.
Teks asli semua pertanyaan tetap dipertahankan.

| Query | Hal yang perlu dikonfirmasi bersama praktisi |
|---|---|
| WO-DEV-003 | Apakah kode C03 dapat dipahami tanpa membuka cue sheet? Perlukah fase entrance resepsi diperjelas? |
| WO-DEV-006 | Apakah “checkout” cukup jelas sebagai serah terima aset WO setelah acara? |
| WO-DEV-013 | Apakah “pasangan siap” jelas membedakan selesai makeup, posisi standby dan kesiapan prosesi? |
| WO-DEV-014 | Pastikan skenario hanya membahas tamu pengguna shuttle; konfirmasi istilah LO, chapel dan dinner. |
| WO-DEV-015 | Tinjau kalimat pembuka; kursi yang tampak kosong belum tentu tersedia untuk dialokasikan. |
| WO-DEV-016 | Tinjau kealamian “informasi yang boleh dijanjikan” dan kejelasan kebutuhan makanan khusus. |

Usulan wording lengkap ada di
`experiments/reports/development_query_review.md`, bagian **Proposed wording — not
applied**. Tuliskan pilihan atau usulan sendiri pada suggested_rewording dan alasannya
di reviewer_notes. Usulan tidak otomatis mengganti query atau membekukan dataset.

## Komentar dan waktu review

Tulis **heading/halaman/sheet/baris → masalah → alasan → koreksi yang disarankan**.
Sebutkan dokumen terkait bila perubahan berdampak pada pembagian peran atau timeline
lain. Catat variasi praktik secara umum; jangan memasukkan nama, kontak, alamat,
daftar tamu, kondisi pribadi atau dokumen klien sebenarnya. Pakai kode simulasi.

Gunakan stopwatch per dokumen/pertanyaan: mulai saat membaca item, berhenti setelah
penilaian dan komentar selesai. Jeda istirahat dikeluarkan. Isi detik aktif pada
**Durasi review (detik)** atau **review_duration_seconds**. Waktu diskusi bersama
dapat ditulis terpisah dalam catatan; jangan menebak waktu yang tidak dicatat.

## Pilot awal dan kelanjutan

Mulai dengan lima dokumen berikut untuk mencoba alur dan mencatat waktu nyata:

| Dokumen | Kategori / format | Alasan dipilih |
|---|---|---|
| WO-DOC-001 — Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer | A / DOCX | Memeriksa peran, delegasi dan jalur komando. |
| WO-DOC-008 — Checklist Final Preparation H-7 hingga H-1 | B / XLSX | Mencoba pemeriksaan checklist, tenggat dan kriteria kesiapan. |
| WO-DOC-021 — Panduan Sinkronisasi Catering dan Banquet Service | D / PDF | Memeriksa batas tanggung jawab dan koordinasi layanan vendor. |
| WO-DOC-030 — Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara | E / TXT | Menilai pilihan saat terlambat, dampak dan kewenangan keputusan. |
| WO-DOC-040 — Matriks Seating Allocation dan Penugasan Guest Escort | G / XLSX | Memeriksa alokasi tamu, escort dan pencatatan perubahan lintas sheet. |

Pilihan ini mencakup lima kategori dan empat format, bukan sampel statistik seluruh
praktik WO. Setelah pilot, diskusikan kejelasan kolom dan waktu aktual dengan peneliti,
lalu atur sesi lanjutan. **Seluruh 50 dokumen tetap memerlukan keputusan terdokumentasi**;
item Revise harus ditindaklanjuti dan direview ulang sebelum corpus final ditetapkan.
Dokumen Reject tidak dimasukkan ke corpus final tanpa perbaikan dan review baru;
peneliti mendokumentasikan keputusan serta perubahan cakupan dataset.

Validasi dokumen menilai kelayakan pengetahuan operasional. Validasi query menilai
kualitas pertanyaan dan kebutuhan informasinya. **Relevance judgment** adalah proses
terpisah untuk menilai pasangan query–chunk, bukan tugas paket ini. Evidence bukan
qrels atau daftar seluruh chunk relevan; jangan memberi grade 0/1/2 sekarang.
Perubahan yang disetujui akan ditangani peneliti melalui versi baru; snapshot pilot
dan 371 chunks frozen tidak diubah melalui workbook ini.
