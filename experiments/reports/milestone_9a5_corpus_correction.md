# Milestone 9A.5 — AI-assisted corpus correction dan versioned candidate

Tanggal audit: 2026-10-09. Dibuat: 2026-10-09T01:33:12.687892+00:00.

**AI-CORRECTED CANDIDATE — NOT HUMAN VALIDATED.** Judul penelitian tidak berubah. Ini paket koreksi otomatis sesuai persetujuan pengguna, bukan keputusan peneliti, independent expert validation, corpus final, snapshot V2, atau hasil benchmark. Metodologi utama tetap memerlukan persetujuan pembimbing.

## Hasil dan batas klaim

Paket kandidat terpisah berisi **50 dokumen dengan ID/format asli**: 26 DOCX, 9 PDF, 10 XLSX, 5 TXT. **024 dan 027 berubah; 48 dokumen lainnya identik byte-for-byte dengan V1.** Total empat paragraf berubah: dua paragraf isi dan dua label versi. Tidak ada keputusan validasi manusia yang diisi.

Ledger mencatat **14 isu**: 1 CONFIRMED_INTERNAL_CONTRADICTION, 0 CLEAR_EDITORIAL_ERROR, 2 PLAUSIBILITY_CONCERN, 5 REQUIRES_EXTERNAL_DOMAIN_VERIFICATION, 6 NO_CHANGE_NEEDED. Tindakan: 2 diterapkan hanya pada kandidat, 6 dipertahankan, 6 unresolved tanpa patch. Tidak semua uncertainty menjadi perubahan. Confidence menilai keterlacakan teks, bukan probabilitas bahwa prosedur benar di lapangan.

**Technical package checks PASS; domain validation NOT PERFORMED; DOCX visual/layout QA NOT VERIFIED.** Tidak ditemukan kontradiksi baru yang jelas dalam perbandingan terarah ini; itu bukan jaminan seluruh corpus bebas masalah. Batas pembacaan dan keterbatasan rendering dijelaskan di bawah.

## Input, cakupan pembacaan dan audit review lama

Dibaca: laporan 9A.3 AI silver ground truth, 9A.4 corpus reconciliation dan qrels readiness; manifest JSON, FILE_INVENTORY.csv; workbook AI review terbaru; canonical/chunk/query provenance/qrels sebagai peta dampak. Manifest dan inventory digunakan untuk identitas/hash/audit, bukan sebagai retrievable corpus. Keputusan koreksi didasarkan pada teks sumber lengkap yang relevan, bukan ringkasan saja.

Semua 50 sumber diekstrak read-only langsung dari file asli untuk pemeriksaan teknis dan pencarian terarah waktu/closure/handover. Pembacaan isi penuh mencakup **34 dokumen**: 001, 003, 004, 006, 011, 014, 016, 017, 018, 019, 021, 023, 024, 025, 026, 027, 028, 029, 030, 031, 032, 033, 034, 035, 036, 037, 038, 040, 042, 043, 044, 047, 048, 050. Enam belas lainnya mendapat pemeriksaan inventory, format, identitas dan pencarian teks terarah; tidak diklaim telah mendapatkan exhaustive semantic review. Locator `bodyN` berarti posisi elemen/paragraf body sumber DOCX; TXT menggunakan nomor baris, PDF nomor halaman, XLSX nama sheet/baris/range. Locator V1 tidak otomatis menjadi locator canonical V2.

Workbook `data/validation/ai_corpus_review_v1.xlsx` terverifikasi **47 AI_APPROVE / 3 AI_REVISE / 0 AI_REJECT**. Ketiga AI_REVISE adalah 024, 027, 042 dan seluruhnya ditinjau. Workbook lama 30 conceptual approve / 20 revise tidak ditemukan pada aset workbook repository dan attachment/arsip yang diperiksa; rincian temuannya tidak dapat dibandingkan. Ketiadaan file bukan bukti tidak ada masalah. Hasil 47/3 tidak membatalkan temuan lama dan bukan human validation; workbook lama tidak direkonstruksi atau diisi berdasarkan angka.

## Dua koreksi yang diterapkan

### C01 — WO-DOC-024 dan acuan WO-DOC-042

CONFIRMED_INTERNAL_CONTRADICTION di sini berarti perbedaan tekstual acuan standby pada skenario EVT-02: 024 menyebut standby08.30, sedangkan 042 memisahkan registrasi08.30–08.45, standby akad/keluarga08.45–09.00, dan akad09.00. Apakah08.30 dahulu dimaksudkan personal readiness berbeda belum tertulis dan tetap unresolved. Kandidat mengacu secara eksplisit pada rundown simulasi042; ini pilihan editorial internal dengan dasar sumber, **bukan penetapan waktu final acara nyata**. Waktu awal makeup06.00 dan akad09.00 tetap dipertahankan. 042 tidak diedit.

### C02 — WO-DOC-027 versus WO-DOC-018/050

PLAUSIBILITY_CONCERN: frasa “serta area sudah diserahkan” pada kriteria closure027 ambigu. 018/050 secara konsisten mencatat closure21.10 dan handover22.30. Referen area027 belum terbukti final handover, sehingga tidak dinyatakan sebagai kontradiksi kronologis tanpa syarat. Kandidat memisahkan penutupan insiden dari serah terima area dalam skenario tersebut; **tidak mengubah21.10/22.30, tidak mengarang intermediate handover, dan tidak melabeli21.10 sebagai temporary recovery**. Handover area tidak direduksi menjadi administrasi saja. Contoh recheck15.30/izin buka15.40 berbeda dari closure; perbedaan ini bukan SOP perusahaan universal. 029/033/047 juga menunjukkan closure, outstanding dan penerimaan tanggung jawab harus dibaca menurut kasusnya.

Berikut before/after lengkap untuk seluruh paragraf yang berubah. Paragraf provenance asli (`body3`) dipertahankan. Label `Versi 2.0-ai-candidate` adalah label kandidat lokal, bukan bukti bahwa snapshot/corpus_version final sudah dibuat.

### C01 — exact before/after

Sumber/locator: WO-DOC-024 / body11; metadata body2.

**Before**

```text
body2: WO-DOC-024  |  Versi 1.0  |  Wedding Organizer X

body11: Layanan pasangan direncanakan mulai 06.00 WITA, disusul dressing dan pemeriksaan siap sebelum standby 08.30. Akad direncanakan 09.00. Jam ini merupakan asumsi rundown EVT-02 dan harus diperiksa bersama vendor sebelum dipakai nyata. Keluarga inti menerima slot yang disepakati tanpa mengambil waktu pasangan. PIC pengantin meminta perkiraan selesai pada titik kerja yang disetujui, bukan terus-menerus menyela.
```

**After — candidate only**

```text
body2: WO-DOC-024  |  Versi 2.0-ai-candidate  |  Wedding Organizer X

body11: Layanan pasangan direncanakan mulai 06.00 WITA, disusul dressing dan pemeriksaan siap sebelum standby akad dan keluarga 08.45 WITA, mengikuti rundown simulasi WO-DOC-042. Akad direncanakan 09.00. Jam ini merupakan asumsi rundown EVT-02 dan harus diperiksa bersama vendor sebelum dipakai nyata. Keluarga inti menerima slot yang disepakati tanpa mengambil waktu pasangan. PIC pengantin meminta perkiraan selesai pada titik kerja yang disetujui, bukan terus-menerus menyela.
```

### C02 — exact before/after

Sumber/locator: WO-DOC-027 / body26; metadata body2.

**Before**

```text
body2: WO-DOC-027  |  Versi 1.0  |  Wedding Organizer X

body26: Log mencatat pemicu, penilaian pengelola, estimasi vendor, persetujuan client yang relevan, keputusan EC, penerima pesan, waktu aktual, serta dampak. Insiden ditutup operasional setelah kegiatan dan akses tidak lagi terganggu serta area sudah diserahkan. Tindakan perbaikan proses dapat tetap terbuka untuk debrief. Catat apakah petunjuk arah, urutan pindah, dan komunikasi benar-benar bekerja, bukan hanya apakah ceremony akhirnya berlangsung.
```

**After — candidate only**

```text
body2: WO-DOC-027  |  Versi 2.0-ai-candidate  |  Wedding Organizer X

body26: Log mencatat pemicu, penilaian pengelola, estimasi vendor, persetujuan client yang relevan, keputusan EC, penerima pesan, waktu aktual, serta dampak. Insiden ditutup operasional setelah kegiatan dan akses tidak lagi terganggu. Dalam skenario sintetis EVT-01 pada WO-DOC-018 dan WO-DOC-050, penutupan insiden dan serah terima area dicatat sebagai tahap terpisah; penutupan insiden tidak menyatakan handover area sudah selesai. Tindakan perbaikan proses dapat tetap terbuka untuk debrief. Catat apakah petunjuk arah, urutan pindah, dan komunikasi benar-benar bekerja, bukan hanya apakah ceremony akhirnya berlangsung.
```

## Seluruh isu, keputusan dan uncertainty

Setiap kutipan ringkas di bawah adalah navigation aid; exact before/after dua perubahan terdapat di atas dan pada ledger. Alternatif untuk isu unresolved adalah usulan kondisional, **tidak ditambahkan ke sumber kandidat sebagai fakta**. NO_CHANGE_NEEDED berarti tidak ada patch yang dibenarkan oleh bukti yang diperiksa, bukan approve terhadap praktik WO nyata.

### C01 — WO-DOC-024

- Kelas/tindakan: `CONFIRMED_INTERNAL_CONTRADICTION` / `APPLIED_CANDIDATE_ONLY`.
- Locator: body11; metadata body2. Evidence silang: 024 body4,6,11,12;042 Operasional A13:I15, Panduan10;014 body8,14;035 body15.
- Alasan: Istilah standby akad pada EVT-02 mempunyai dua jam. Kandidat mengikuti referensi eksplisit rundown042 sebagai pilihan editorial skenario sintetis, bukan penetapan jadwal lapangan. Label versi kandidat diperbarui; provenance notice asli dipertahankan.
- Dampak operasional: Menghilangkan dua acuan waktu untuk label standby yang sama dalam kandidat.
- Dampak retrieval: 024-C003 berbeda; query004/013 dan batas konteks003 perlu audit mapping.
- Confidence: Tinggi: perbedaan teks dan nilai042. Sedang: pilihan acuan sintetis.
- Unresolved: Maksud historis08.30 personal-ready tidak diketahui. Durasi MUA/buffer nyata belum diverifikasi;08.45 bukan waktu final lapangan.

### C02 — WO-DOC-027

- Kelas/tindakan: `PLAUSIBILITY_CONCERN` / `APPLIED_CANDIDATE_ONLY`.
- Locator: body26; metadata body2. Evidence silang: 027 body24,26;018 lines23,25–32;050 page2 Penutupan operasional;019 body6,20;048 Operasional35/Panduan11.
- Alasan: Syarat area sudah diserahkan tidak jelas referennya. Klarifikasi mempertahankan closure sebagai tahap terpisah dari handover seperti contoh018/050, tanpa mengganti jam atau membuat tahap pemulihan baru. Label versi kandidat diperbarui; provenance notice asli dipertahankan.
- Dampak operasional: Mencegah penutupan log dianggap telah menyelesaikan serah terima area.
- Dampak retrieval: 027-C009 berubah; batas chunk dapat berubah. Existing tiga chunk027 judged bukan paragraf26.
- Confidence: Tinggi:018/050 membedakan tahap. Sedang: referen area pada027.
- Unresolved: Belum terbukti apakah area pada027 berarti final handover. Norma perusahaan/venue tidak divalidasi. Tidak menganggap21.10 pemulihan sementara.

### C03 — WO-DOC-042

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: Operasional rows12–15;Panduan10. Evidence silang: 042 A12:I15;024 body11.
- Teks existing/ringkasan nilai: Registrasi akad08.30–08.45; Standby akad dan keluarga08.45–09.00.
- Usulan: Tidak diubah.
- Alasan: Tiga milestone registrasi/standby/akad sudah berbeda eksplisit; digunakan sebagai referensi skenario pada024.
- Dampak operasional: Tidak memaksakan edit rundown yang sudah koheren.
- Dampak retrieval: 042-C002 tetap sama; snapshot baru tetap memerlukan binding baru.
- Confidence: Tinggi untuk isi sel.
- Unresolved: Tidak membuktikan semua durasi layanan nyata memadai. Status AI_REVISE lama tidak ditimpa.

### C04 — WO-DOC-018; WO-DOC-050

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: 018 line32;050 page2 Penutupan operasional. Evidence silang: 018 lines23,25–32;050 pages1–2.
- Teks existing/ringkasan nilai: INC-01 ditutup operasional21.10; handover area selesai22.30.
- Usulan: Tidak diubah.
- Alasan: Kedua sumber konsisten tentang closure dan handover. Tidak ada dasar menyebut21.10 penutupan sementara.
- Dampak operasional: Mempertahankan kronologi simulasi, bukan menambah kejadian.
- Dampak retrieval: Tidak mengubah answer-bearing chronology.
- Confidence: Tinggi untuk kronologi tertulis.
- Unresolved: 15.30 recheck,15.40 izin buka,21.10 closure,22.30 handover bukan tahapan universal atau bukti event nyata.

### C05 — WO-DOC-006

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: Operasional row12;Panduan11–12. Evidence silang: 001 body9,11;004 body6,12;006 Panduan11–12;028 body6,13,18.
- Teks existing/ringkasan nilai: Menilai fasilitas listrik | EC | PIC venue | petugas kompeten; PIC vendor | floor | Petugas berwenang menilai teknis; WO hanya mengoordinasikan
- Usulan: Tidak diubah.
- Alasan: A/R harus dibaca bersama batas kewenangan dan Panduan; bukan izin EC melakukan sertifikasi listrik.
- Dampak operasional: Batas peran sudah disebut eksplisit.
- Dampak retrieval: Pembacaan row tanpa context berisiko; shared context wajib dipertahankan pada ekstraksi berikutnya.
- Confidence: Tinggi untuk koherensi tekstual.
- Unresolved: Tidak menyertifikasi kompetensi personel atau legalitas pembagian peran nyata.

### C06 — WO-DOC-028; WO-DOC-011; WO-DOC-034

- Kelas/tindakan: `REQUIRES_EXTERNAL_DOMAIN_VERIFICATION` / `UNRESOLVED_NO_PATCH`.
- Locator: 028 body6,8,13,18,23;011 Operasional15–18;034 Operasional11/Panduan12. Evidence silang: 028 body6–23;011 Panduan13–14;034 Panduan12–14.
- Teks existing/ringkasan nilai: Pemeriksaan instalasi, isolasi sumber daya, penyambungan backup, dan penilaian kelayakan hanya dilakukan petugas berkompeten yang berwenang.
- Usulan: Alternatif untuk penggunaan nyata: catat petugas, fasilitas dan prosedur lokal yang sudah dikonfirmasi; tidak ditambahkan sebagai fakta.
- Alasan: Tidak ada data lokasi/operator nyata untuk menilai kemampuan backup atau kelayakan instalasi.
- Dampak operasional: Kecukupan respons teknis belum dibuktikan.
- Dampak retrieval: Tidak menambah angka daya/ambang keselamatan atau jawaban teknis palsu.
- Confidence: Tinggi bahwa verifikasi eksternal belum tersedia.
- Unresolved: Tidak melakukan audit keselamatan/sertifikasi fasilitas.

### C07 — WO-DOC-027; WO-DOC-036; WO-DOC-038; WO-DOC-050

- Kelas/tindakan: `REQUIRES_EXTERNAL_DOMAIN_VERIFICATION` / `UNRESOLVED_NO_PATCH`.
- Locator: 027 body6,8,24;036 page2 Rain plan;038 Operasional20;050 page2. Evidence silang: 018 lines17–23;027 body8,22,24;036 pages1–2;050 page2.
- Teks existing/ringkasan nilai: Pilihan tertutup belum siap jika hanya ruangnya tersedia tetapi layanan dan akses belum ditelaah.
- Usulan: Pertahankan asumsi dan status belum diverifikasi.
- Alasan: Perpindahan14.40 sampai recheck15.30 merupakan contoh, bukan estimasi pekerjaan nyata. Layout/tenaga/durasi belum diukur.
- Dampak operasional: Tidak mengesahkan kapasitas alternatif atau kecukupan waktu pindah.
- Dampak retrieval: Hindari retrieval memperlakukan contoh sebagai SOP universal.
- Confidence: Tinggi untuk sifat simulasi; kelayakan nyata tidak diketahui.
- Unresolved: Personel, layout, jarak, cuaca dan fasilitas aktual belum tersedia.

### C08 — WO-DOC-021; WO-DOC-026; WO-DOC-035

- Kelas/tindakan: `REQUIRES_EXTERNAL_DOMAIN_VERIFICATION` / `UNRESOLVED_NO_PATCH`.
- Locator: 021 pages1–2;026 Operasional10–14/Panduan10;035 body6,17. Evidence silang: 021 Menetapkan dasar layanan;026 Panduan10;035 body6,17.
- Teks existing/ringkasan nilai: Kelebihan tamu tidak otomatis berarti stok dapat diperbanyak saat itu juga.
- Usulan: Pertahankan wording kondisional; jangan membuat kapasitas/stok/waktu aman baru.
- Alasan: 280 padaEVT02 dan120 padaEVT01 bukan konflik headcount karena event berbeda. Kesiapan layanan tetap dari provider.
- Dampak operasional: Kapasitas banquet/keamanan pangan nyata belum diverifikasi.
- Dampak retrieval: Membedakan event dan kebutuhan layanan; tidak mengarang support pada qrels.
- Confidence: Tinggi untuk konteks event.
- Unresolved: Tidak menilai keamanan pangan atau kapasitas venue sebenarnya.

### C09 — WO-DOC-025; WO-DOC-043

- Kelas/tindakan: `REQUIRES_EXTERNAL_DOMAIN_VERIFICATION` / `UNRESOLVED_NO_PATCH`.
- Locator: 025 Operasional19–26/Panduan12–14;043 body22,24. Evidence silang: 025 rows19–26;043 body21–24;038 Operasional26.
- Teks existing/ringkasan nilai: Tiga kendaraan konseptual TRN-01 sampai TRN-03 masing-masing kapasitas layanan simulasi15 orang wajib diverifikasi penyedia sebelum digunakan nyata.
- Usulan: Pertahankan asumsi; alternatif nyata harus mengikuti kapasitas/rute terkonfirmasi, tanpa angka baru.
- Alasan: 3×15=45 koheren secara aritmetika, tetapi bukan bukti kapasitas atau kecukupan satu LO. Naik16.35 berbeda dari dispatch16.40 dan arrival17.00.
- Dampak operasional: Kelayakan shuttle, bantuan akses, dan durasi20menit belum terbukti.
- Dampak retrieval: Perbedaan boarding/dispatch tidak boleh diperbaiki sebagai konflik jam semu.
- Confidence: Tinggi untuk angka tertulis; kelayakan nyata tidak diketahui.
- Unresolved: Kendaraan, driver, jarak dan actual headcount belum diverifikasi.

### C10 — WO-DOC-040

- Kelas/tindakan: `PLAUSIBILITY_CONCERN` / `UNRESOLVED_NO_PATCH`.
- Locator: Operasional rows6–33;Panduan11–14. Evidence silang: 040 Panduan11–14;001 body8;032 body6,10.
- Teks existing/ringkasan nilai: Dua escort pendukung STAFF-11 dan STAFF-12 diperkenalkan khusus matriks ini dan berada di bawah STAFF-08, tanpa hak mengubah rundown.
- Usulan: Pertahankan sebagai simulasi; kebutuhan staf tambahan baru ditentukan berdasarkan kondisi yang tersedia.
- Alasan: 28kelompok×10=280 konsisten, tetapi kecukupan dua escort tidak dapat dipastikan dari matriks. Tidak ada dasar menambah jumlah staf.
- Dampak operasional: Kapasitas pelayanan dan kepadatan belum diukur.
- Dampak retrieval: Tidak memberi retriever angka staffing optimal palsu.
- Confidence: Tinggi untuk hitungan; staffing belum terverifikasi.
- Unresolved: Laju kedatangan, jarak dan kebutuhan bantuan tidak tersedia.

### C11 — WO-DOC-016; WO-DOC-032

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: 016 body14–15;032 body6,10,14–15,17. Evidence silang: 032 body6,10,14–15;016 body14–15;040 Perubahan7–8.
- Teks existing/ringkasan nilai: Kapasitas, layout yang diizinkan, dan jalur yang wajib tetap tersedia harus dikonfirmasi pengelola untuk acara nyata.
- Usulan: Tidak diubah.
- Alasan: Kursi tampak kosong dibedakan dari tersedia; biaya client tidak mengesampingkan batas fasilitas.
- Dampak operasional: Kewenangan seating dan privasi sudah eksplisit secara tekstual.
- Dampak retrieval: Preservasi context fase/otorisasi; tidak mengubah query015.
- Confidence: Tinggi untuk koherensi teks.
- Unresolved: Tidak memvalidasi kapasitas atau kebijakan privasi organisasi nyata.

### C12 — WO-DOC-037; WO-DOC-038

- Kelas/tindakan: `REQUIRES_EXTERNAL_DOMAIN_VERIFICATION` / `UNRESOLVED_NO_PATCH`.
- Locator: 037 pages1–2;038 Operasional28–31/Panduan14. Evidence silang: 037 Konteks/Verifikasi/Pemeriksaan kondisi;038 rows28–31.
- Teks existing/ringkasan nilai: Penggunaan area diasumsikan telah memperoleh persetujuan pengelola lokasi; dokumen ini tidak menjadi bukti izin, prediksi pasang surut, atau jaminan keamanan pantai.
- Usulan: Pertahankan status asumsi; tidak menambahkan aturan venue, jam aman, pasang, angin, atau jalur alternatif yang belum ada.
- Alasan: Sumber sudah membatasi klaim. Tidak tersedia data venue/tanggal untuk membuktikan izin atau kelayakan.
- Dampak operasional: Penggunaan pantai dan akses aktual unresolved.
- Dampak retrieval: Menjaga retrieval tidak mengubah rencana80tamu menjadi kapasitas atau izin resmi.
- Confidence: Tinggi untuk disclosure; domain belum diverifikasi.
- Unresolved: Tidak ada verifikasi eksternal atas izin, akses, fasilitas atau kondisi perairan.

### C13 — WO-DOC-030; WO-DOC-044

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: 030 lines17,20;044 page2 decision window/page3 dinner. Evidence silang: 030 lines11–20;044 pages2–3;017 pages1–2;042 rows29–31.
- Teks existing/ringkasan nilai: Timeline utama di sini tetap versi1.0; kedua jadwal tidak boleh digunakan bersamaan.
- Usulan: Tidak diubah.
- Alasan: Rencana garden15.30/16.30/18.00 dan versi hujan15.45/16.45/18.15 sudah dibedakan; buffer sambutan bukan izin memotong ritual.
- Dampak operasional: Tidak menghapus varian kronologi yang sah.
- Dampak retrieval: Version context wajib dipertahankan; perbedaan versi bukan otomatis contradiction.
- Confidence: Tinggi untuk perbedaan versi tertulis.
- Unresolved: Durasi/buffer nyata tetap tidak divalidasi.

### C14 — WO-DOC-019; WO-DOC-048

- Kelas/tindakan: `NO_CHANGE_NEEDED` / `RETAIN_BYTES`.
- Locator: 019 body6,20;048 Operasional35/Panduan11–12. Evidence silang: 019 body6,20;048 row35/Panduan11–12;018 line32.
- Teks existing/ringkasan nilai: Handover area22.30 rencana; seluruh item Belum diperiksa.
- Usulan: Tidak diubah.
- Alasan: Serah terima venue dan penutupan publik merupakan tahap berbeda; checklist kosong bukan bukti pelaksanaan kasus nyata.
- Dampak operasional: Menjaga outstanding dan penerimaan area tetap terpisah.
- Dampak retrieval: Tidak memperlakukan status checklist sebagai evidence selesai aktual.
- Confidence: Tinggi untuk status dan kronologi.
- Unresolved: Tidak menyatakan semua aset sudah diperiksa nyata.

## Folder kandidat dan ledger

`data/corpus_candidates/v2_ai_corrected/documents/` berisi tepat 50 file sumber; tidak disertai manifest baru yang dapat disalahartikan sebagai frozen snapshot. Original source path tetap `data/source_corpus/documents/`. 48 file disalin tanpa perubahan bytes; hanya `word/document.xml` pada dua DOCX yang memiliki empat text replacements tercatat. ZIP members lainnya identik; setelah mengembalikan empat teks dalam perbandingan in-memory, XML identik dengan V1. Styles, relationships, tabel, urutan body dan jumlah paragraf tidak diubah. Ini pemeriksaan struktur/format, bukan bukti pagination tetap sama.

Ledger memiliki sheet **Corrections** (14 baris isu) dengan ID, dokumen, kelas, tindakan, locator, before/after atau proposal, alasan, evidence, dampak operasional/retrieval, confidence, unresolved assumptions, status. Sheet **Files** (50 baris) memuat ID, judul, format, change status, source/candidate path, original/candidate SHA-256, correction IDs, review scope, status. Hash lengkap per dokumen tersedia di sana. Tidak ada reviewer identity atau judgment manusia palsu. Status paket berlaku juga untuk48 salinan yang tetap memuat metadata versi1.0/status pending lama; menulis ulang label semua salinan justru melanggar syarat byte-identical.

## Change impact analysis — belum dijalankan

| Komponen | Dampak dan tindakan pada versi baru |
|---|---|
| Extraction | Format dan document ID tetap; ekstraksi V2 harus memakai folder kandidat setelah diputuskan. Source hash024/027 berubah. Tidak ada full ingestion sekarang. |
| Cleaning | Label versi2.0-ai-candidate masih cocok dengan existing identity/version exclusion. Provenance notice asli dipertahankan dan tetap cocok dengan exact provenance exclusion. Rule check read-only PASS untuk body2/3 kedua dokumen. Tidak ada perubahan cleaning implementation. |
| Chunking | Isi body11/26 lebih panjang; text hash dan kemungkinan boundaries/overlap berubah. Label371 hanya berlaku V1. Jumlah chunk/token V2 belum dihitung; perlu structural coverage/truncation audit baru. |
| Document/chunk IDs | Pertahankan document IDs sebagai identitas logis; jangan berasumsi chunk IDs sama berarti content sama. Periksa ID/block/locator mapping dengan version+hash, termasuk unchanged documents yang masuk snapshot baru. |
| Retrieval serialization | Shared serializer dan parameternya tidak diubah. Semua retriever harus membaca hasil V2 yang sama. Cross-reference042/018/050 adalah konteks operasional sumber, bukan query evidence/qrels. Jangan memasukkan ledger atau status administratif ke retrieval. |
| Query provenance | Exact18 query tetap. Query004 menunjuk024 b0011 yang berubah; query013 menunjuk024 b0012 dalam chunk yang sama; query009 menunjuk027 b0013/b0016/b0022 yang tidak diedit tetapi perlu rebinding versi. Audit ulang seluruh42 pointers pada hasil V2; evidence bukan judgment. |
| 684 existing silver judgments | Tetap terikat V1 dan tidak diubah/disalin otomatis ke V2. Enam puluh tiga positives dan621 negatives tidak disahkan ulang oleh milestone ini. Missing5994 tetap unjudged V1. |
| R1/R2/R3 indices | Indeks existing valid hanya terhadap input/hash V1. Corpus version baru memerlukan rebuild TF-IDF/BM25 dan corpus Dense embeddings/index dengan model/serializer yang tetap, setelah persetujuan dan resource gate. Tidak reuse atas dasar ID saja. |
| R4 fusion | Algoritma, RRF k60, full Dense dan BM25 positive-score policy tetap. Gunakan komponen R2/R3 yang terikat snapshot baru; tidak perlu index Hybrid terpisah. Query-vector provenance/cache harus cocok dengan contract dan corpus-scoring inputs. |
| Snapshot/benchmark | Setelah kandidat disetujui untuk pipeline: extraction/cleaning/chunking baru, mapping/coverage audit, snapshot+fingerprint baru dan index rebuild sebelum benchmark V2. V1 tetap immutable. M8C end_to_end_pending tidak berubah; tidak ada klaim live GPU/effectiveness PASS. |

**Envelope dampak V1 terukur:**024 memiliki6chunk dan027 memiliki9chunk, total15chunk/270 pasangan potensial dengan18 query. Existing judgments pada kedua dokumen berjumlah90:02436 (grade0/1/2=32/2/2),02754 (49/2/3). Ini scope pemeriksaan mapping, **bukan90 grade otomatis salah**. Direct body11 berada pada024-C003 dengan18 judged pairs (15/2/1); body26 berada pada027-C009 yang belum judged. 042 tidak berubah (8chunk V1); tidak perlu dihitung sebagai edited document. Ingestion V2 dapat mengubah envelope tersebut, jadi angka270/90 tidak digunakan sebagai jumlah final V2.

Tambahan label AI ke body3 sempat dipertimbangkan pada working candidate, tetapi dibatalkan sebelum finalisasi: regex provenance existing memakai exact full match. Final candidate mempertahankan body3 asli, menyimpan status lengkap di paket/ledger/laporan dan hanya memperbarui label versi pada body2. Tidak ada temporary variant yang disimpan sebagai deliverable. Ini mencegah administrative text menjadi retrievable tanpa perlu mengubah pipeline.

## Automated quality checks dan integrity

| Check | Hasil | Batas |
|---|---|---|
|50 sources/candidates, unique IDs001–050, filenames/format parity, no missing|PASS|DOCX26/PDF9/XLSX10/TXT5; manifest/inventory cocok|
|Source hash vs manifest dan inventory|PASS|50/50 file asli sesuai SHA-256 metadata|
|Format parsing|PASS|DOCX ZIP/XML+paragraphs; XLSX ZIP+workbook read; PDF reader; TXT UTF-8 nonempty|
|Change scope/ledger|PASS|2 changed,48 byte-identical; tepat4 paragraph replacements tercatat; no non-text XML changes|
|Target internal assertions|PASS|024 sekarang mengacu standby08.45 rundown042; 027 tidak lagi menyatakan closure berarti handover selesai;018/042/050 byte-identical|
|New operational claims|PASS pada diff terarah|Waktu/rundown dan closure/handover bersumber eksplisit; tidak ada angka kapasitas, safety threshold atau SOP eksternal baru|
|Cleaning administrative-rule self-check|PASS|Hanya fungsi normalize/exclusion pure diuji; bukan full ingestion|
|Ledger readback|PASS|2 sheets,14 issue rows,50 file rows; seluruh nilai dibandingkan exact dengan ledger input; tidak ada formulas/error tokens|
|Workbook visual sampling|PASS|Render Corrections IDs/before-after dan Files IDs/titles diperiksa; bukan native Excel full-workbook print QA|
|Candidate DOCX visual rendering|NOT VERIFIED|Bundled runtime tidak menyediakan LibreOffice soffice; satu render attempt gagal FileNotFoundError. Tidak menginstal software. Pagination/overflow dua DOCX belum dapat disertifikasi|
|V1 snapshot/artifacts/indices unchanged|PASS|548 pre-existing files dibandingkan ulang byte SHA-256 dengan baseline awal termasuk cache indices/runs|
|Domain/independent human validation|NOT PERFORMED|Tidak menyertifikasi safety, capacity, permission atau praktik perusahaan nyata|

Protected baseline: 548 file; 387 berada pada cache project eksternal `D:/ModelCache/wo-retrieval-benchmark`. Cakupan juga meliputi source corpus lengkap, canonical/chunks, snapshot, pilot/retrieval protocol,18 query/provenance, silver qrels, laporan/workbook existing, source code/tests dan README. `.venv`/`.venv-ml` tidak diubah atau dijalankan; hash seluruh environment tidak dihitung. `.git` tidak tersedia sehingga tidak ada Git diff; change-scope didasarkan pada baseline filesystem/hash dan daftar file baru.

### Hash kunci V1, dihitung ulang

| Artifact | SHA-256 |
|---|---|
| `data/chunks/chunks.jsonl` | `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0` |
| `data/processed/documents.jsonl` | `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01` |
| `data/source_corpus/corpus_manifest.json` | `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f` |
| `experiments/configs/pilot.toml` | `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26` |
| `data/validation/pilot_snapshot.json` | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` |
| `data/benchmark/development_queries_draft.jsonl` | `27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95` |
| `data/benchmark/development_query_provenance.jsonl` | `a880b60972e64c559e7dbe61e6b446a6d258914182e35c22e5c2520f62d05d59` |
| `data/benchmark/development_qrels_ai_silver_v1.jsonl` | `786922e8285a7ec9d311ca84e1b2371068a4ec0ffd7aa31d6e31438d060927ed` |
| `data/benchmark/development_qrels_ai_silver_manifest.json` | `804d9af9dc6d4770f660944211f65c9cd3e9c133ad1d75240fd4ce3e7b6a04ac` |

Snapshot ID: `WO-CORPUS-V1-DRAFT-PILOT-001`. Aggregate fingerprint dihitung ulang dari canonical sorted JSON empat artifact hashes: `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`. Sama dengan V1; tidak dibuat fingerprint/snapshot V2.

### Hash dua kandidat yang berubah

| Document | Original SHA-256 | Candidate SHA-256 |
|---|---|---|
|WO-DOC-024|`1663be764ba81ab9b4f932d306b4708ff8173b5d6850472f08faaef338564ec2`|`1b2ebed2b6a6e91b3e928dfbecd07336e89beab4fe52c4f0887c91152be97fc6`|
|WO-DOC-027|`07ee97c0f177bb3acc2f17c05103796373dac44a31609c214c6c70ffa03f1776`|`02de2cef6e3e27f36cd934c1c9e587316ac03b4ac694ba6f936f1860be107a0d`|

## Deliverables dan kelanjutan yang diusulkan

Dibuat tepat52 file baru:50 file pada `data/corpus_candidates/v2_ai_corrected/documents/`, `data/validation/ai_corpus_correction_ledger.xlsx`, dan laporan ini. Tidak ada existing repository file diubah. Helper/preview hanya berada pada temporary directory di luar repository; tidak ada manifest tambahan, qrels baru, query baru, snapshot V2 atau indeks baru.

**Usulan 9A.6, belum dimulai:** audit otomatis pra-ingestion terhadap kandidat, finalisasi keputusan version/paket serta pencatatan scope unresolved; pemeriksaan visual dua DOCX saat renderer tersedia; lalu, hanya dalam task yang disetujui, jalankan pipeline V2 terpisah, audit mapping/coverage/tokenization dan buat snapshot/index baru. Jangan mengklaim automated self-review telah menyelesaikan domain validation. Jika peneliti nanti mengadopsi kandidat, catat keputusan nyata dan keterbatasan AI/synthetic/researcher bias; penggunaan sebagai metodologi evaluasi utama tetap pending persetujuan pembimbing.

Tidak ada GPU/BGE-M3, retrieval/indexing/effectiveness evaluation, full re-ingestion, query judgment, instalasi, download, commit, push, PR atau deploy. **STOP setelah correction package dan audit; V1 tetap menjadi satu-satunya frozen pilot pada pekerjaan ini.**
