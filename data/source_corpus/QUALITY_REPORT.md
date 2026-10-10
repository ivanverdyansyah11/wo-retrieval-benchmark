# Quality Report

Dataset: Wedding Organizer Operational Knowledge Corpus. Versi 1.0 Research Draft. Pemeriksaan 8 Oktober 2026. Semua dokumen source_type `researcher_composed_operational_draft` dan validation_status `pending_practitioner_validation`. Laporan ini mencatat pemeriksaan file dan telaah penyusun, bukan validasi praktisi atau hasil eksperimen retrieval.

## A Corpus statistics

- Dokumen utama: 50; file corpus dapat dibaca: 50/50.
- Format: DOCX 26, PDF 9, XLSX 10, TXT 5.
- Total kata aktual: 33,506; total karakter ekstraksi: 251,528.
- Rentang kata per file: 354-1021; median 647.
- Naratif: 40 file, rentang 354-1021 kata. 1 dokumen mencapai >=1.000 kata; mayoritas panduan fokus lebih singkat daripada sasaran menengah 1.000-1.800 kata dalam brief. Tidak ditambah filler. Layout aktual dan kekayaan topik tetap perlu dinilai praktisi.
- Spreadsheet: 10 file; 25-36 baris operasional per file, di luar sheet Panduan. WO-DOC-040 memiliki sheet Perubahan yang substantif.
- Render: 26 DOCX utama dan checklist berhasil diekspor Microsoft Word; bersama 9 PDF utama, 36 PDF kerja dirasterisasi menjadi 80 halaman PNG. Tidak ditemukan halaman kosong atau karakter melewati batas halaman 10 pt pada pemeriksaan koordinat. Preview seluruh sheet XLSX dibuat; inspeksi visual memakai contact sheet dan sampel ukuran penuh, tidak setiap sel pada setiap tingkat zoom.

Metode penghitungan sama dengan README: regex kata Unicode pada teks hasil pembukaan ulang; karakter termasuk newline dan pemisah. DOCX body dan tabel berurutan tanpa header/footer; PDF text layer tiap halaman termasuk footer yang terbaca; TXT UTF-8; XLSX nama sheet dan nilai sel tidak kosong per baris, delimiter ` | `. Nilai waktu dikonversi ISO dalam hitungan; cached duration formula diperiksa independen. Perbedaan representasi antarformat dapat memengaruhi jumlah kata; nilai ini bukan jumlah token model.

### Distribusi kategori

| Kategori | Dokumen |
|---|---:|
| A. Struktur Tim dan Job Description | 6 |
| B. Persiapan Sebelum Acara | 6 |
| C. Wedding Day Operation | 7 |
| D. Vendor Management | 7 |
| E. Contingency / Problem Handling | 8 |
| F. Venue Operation | 4 |
| G. Guest dan Family Handling | 3 |
| H. Rundown dan Timeline | 3 |
| I. Internal Communication / Escalation | 3 |
| J. Post-event / Evaluation | 3 |

### Distribusi genre

| Genre | Dokumen |
|---|---:|
| Annotated event timeline | 1 |
| Contingency procedure | 2 |
| Decision and escalation note | 1 |
| Detailed rundown | 1 |
| Dispatch schedule | 1 |
| Escalation reference card | 1 |
| Evaluation and meeting guide | 1 |
| Field operations log | 1 |
| Field operations manual | 1 |
| Field reference guide | 1 |
| Guest arrangement matrix | 1 |
| Hospitality guideline | 1 |
| Incident closure report | 1 |
| Incident decision matrix | 1 |
| Incident handling SOP | 1 |
| Incident response guide | 1 |
| Inspection checklist | 1 |
| Internal FAQ | 1 |
| Internal briefing note | 1 |
| Internal communication SOP | 1 |
| Internal operations guideline | 1 |
| Job description | 2 |
| Meeting and briefing guide | 1 |
| Operational checklist | 1 |
| Operational contingency | 1 |
| Operational cue guide | 1 |
| Operational guideline | 2 |
| Operational handbook | 1 |
| Operational procedure | 1 |
| Planning handbook | 1 |
| Post-event checklist | 1 |
| Responsibility matrix | 1 |
| Role guideline | 1 |
| SOP | 2 |
| Service coordination plan | 1 |
| Site assessment matrix | 1 |
| Technical contingency guide | 1 |
| Timed event rundown | 1 |
| Vendor briefing guide | 1 |
| Vendor coordination guide | 1 |
| Vendor guideline | 1 |
| Vendor operations guide | 1 |
| Vendor readiness matrix | 1 |
| Venue operations guide | 1 |
| Venue operations manual | 1 |
| Venue-specific guide | 1 |

### Estimasi prospective chunks

Proxy perencanaan menggunakan `ceil(karakter/4)` untuk token ilustratif, total 62,903 token proxy. Per dokumen, jumlah perkiraan adalah `max(1, ceil((token_proxy - overlap)/(chunk_size - overlap)))`. Profil 400/40 menghasilkan sekitar 198 chunks; 350/50 sekitar 219; 300/60 sekitar 273. Rentang ilustratif 198-273; profil tengah berada di luar target 300-600. Rasio empat karakter per token tidak dikalibrasi tokenizer Bahasa Indonesia. Batas heading, unit checklist, dan pewarisan header tabel belum disimulasikan, sehingga angka akhir bisa berbeda. Tidak ada chunk final atau eksperimen yang dijalankan.

## B Quality checks

PASS berarti pemeriksaan yang dijelaskan lolos sesuai lingkupnya, bukan bukti kebenaran domain. FAIL berarti pemeriksaan gagal. NOT VERIFIED berarti belum diperiksa dengan bukti yang memadai.

| Check ID | Description | Result | Findings |
|---|---|---|---|
| QA-01 | Jumlah dokumen | PASS | Tepat 50 file di documents/, tanpa sidecar atau duplikat format. |
| QA-02 | ID unik | PASS | WO-DOC-001 sampai WO-DOC-050 tersedia. |
| QA-03 | Konsistensi tiga manifest | PASS | 50 record per format, ID dan hash cocok file akhir. Field XLSX dan CSV dibandingkan dengan JSON. |
| QA-04 | Distribusi kategori | PASS | A-J = 6, 6, 7, 7, 8, 4, 3, 3, 3, 3. |
| QA-05 | Keterbacaan format asli | PASS | Semua 50 file dibuka ulang; arsip OOXML lolos CRC. 26 DOCX dan checklist juga dirender dengan Microsoft Word. |
| QA-06 | Ekstraksi teks | PASS | DOCX body dan tabel, PDF text layer tiap halaman, TXT UTF-8, serta seluruh sheet XLSX berhasil diekstrak tanpa OCR. |
| QA-07 | Kelengkapan isi | PASS | Minimum 354 kata aktual; sheet operasional memiliki 25-36 baris bermakna. Kolom hasil checklist sengaja belum diisi, aktivitas dan kriterianya sudah lengkap. |
| QA-08 | Bahasa utama | PASS | Seluruh dokumen disusun dan ditelaah dalam Bahasa Indonesia; pemeriksaan otomatis kata fungsi mendukung, bukan detektor bahasa formal. Istilah operasional Inggris dipertahankan kontekstual. |
| QA-09 | Identitas dan konsistensi skenario | PASS | Kode event, venue, client, staf, dan vendor diperiksa terhadap kamus. Kronologi perpindahan 14.40, versi 14.45, ceremony 16.45 cocok pada dokumen 018, 027, 030, 047, 050. STAFF-11/12 dan varian internasional dijelaskan. Telaah domain tetap pending. |
| QA-10 | Relasi dokumen | PASS | Seluruh relasi mengarah ke ID tersedia dan dipilih sesuai isi, tanpa self-reference. |
| QA-11 | Duplikasi substansial | PASS | Tidak ada paragraf body identik >=30 kata lintas dokumen. Jaccard 5-gram tertinggi 0.018, WO-DOC-008 vs WO-DOC-038. Kemiripan semantik tidak diuji; boilerplate identitas tetap ada. |
| QA-12 | Privasi dan anonimisasi | PASS | Tidak ditemukan email atau pola nomor telepon Indonesia. Identitas memakai kode dan Wedding Organizer X; telaah penyusun tidak menemukan nama client atau perusahaan nyata. Deteksi regex tidak menjamin audit privasi menyeluruh. |
| QA-13 | Metadata dan hitungan aktual | PASS | 20 field wajib tersedia; array JSON valid; kata, karakter, dan hash dihitung ulang dari file akhir. |
| QA-14 | Packaging | PASS | ZIP dibuka ulang, CRC dan nama anggota cocok; hash seluruh isi dibandingkan dengan file final dan inventory. |
| QA-15 | Kesiapan ingestion struktural | PASS | Empat format dapat diekstrak; topik, genre, ID, relasi, dan unit tabel bervariasi. Kelayakan domain serta performa retrieval belum disimpulkan. |
| QA-DOMAIN | Validasi praktisi | NOT VERIFIED | Tidak ada reviewer, persetujuan ahli, atau pemeriksaan venue nyata. |
| QA-SEMANTIC | Duplikasi semantik | NOT VERIFIED | Uji paragraf identik dan 5-gram dijalankan; model embedding dan penilaian ahli kemiripan belum dijalankan. |
| QA-VISUAL | Tampilan file | PASS | Seluruh DOCX dan PDF dirender; contact sheet seluruh halaman dan preview setiap sheet ditinjau, dengan sampel ukuran penuh. Uji koordinat tidak menggantikan pemeriksaan seluruh sel. |
| QA-FORMULA | Durasi dan alokasi | PASS | 33 formula durasi rundown dibandingkan selisih waktu independen, cached result cocok. Seating 28 kelompok x 10 = 280. Tiga kelompok dispatch kendaraan x 15 = 45. |

Renderer standar render_docx.py dicoba dan gagal karena LibreOffice tidak tersedia. Pemulihan memakai Microsoft Word yang terpasang, ExportAsFixedFormat, kemudian Poppler untuk PNG. File kerja render, log, dan skrip tidak dimasukkan ke paket. Formula durasi dihitung artifact-tool dan diverifikasi ulang dengan pembaca XLSX; uji pengubahan input dalam aplikasi Excel belum dijalankan, sehingga kemampuan recalculation native Excel tidak diklaim telah diuji.

## C Topical coverage

Corpus mencakup pembagian mandat EC/WC, pendampingan pengantin dan keluarga, vendor versus venue, runner dan LO, planning H-30 sampai H-1, technical meeting, final confirmation, assembly, floor, guest reception, MC dan banquet cue, dekor, dokumentasi, makeup, entertainment, transport, serta readiness. Contingency mencakup hujan, listrik, vendor terlambat, keterlambatan rundown, gangguan audio, tamu tambahan, barang hilang, serta prioritas insiden. Venue dibedakan menjadi ballroom, garden villa, chapel-dinner, dan pantai. Penutupan mencakup breakdown, aset, handover, debrief, dan laporan INC-01 simulasi.

## D Cross document consistency

Telaah penyusun membandingkan sembilan area berikut dengan dokumen acuan serta kamus kode. Ini bukan review independen praktisi.

| Area | Pemeriksaan dan hasil |
|---|---|
| Struktur peran | 001-006: STAFF-01 EC, STAFF-02 WC, PIC khusus berbeda; perangkapan harus tertulis. |
| Decision authority | 001, 002, 006, 027-034, 045-047: EC perubahan rundown, client biaya/lingkup melalui WC, petugas berwenang kelayakan teknis. |
| Komunikasi dan eskalasi | 012, 017, 045-047: standby bukan jalan; pengakuan penerima wajib; tidak menjawab bukan persetujuan. |
| Vendor arrival dan readiness | 004, 009, 020-026, 029: tiba tidak sama dengan keluaran siap; bukti dan syarat dicatat. |
| Venue access | 011, 035-038: akses dan batas lokal dikonfirmasi pengelola; WO tidak memperbaiki listrik. |
| Guest handling | 016, 032, 039-041: verifikasi berkode, seating diperiksa, tambahan tidak otomatis memakai kursi kosong. |
| Rundown | 017 dan 042 cocok untuk resepsi EVT-02; 025 dan 043 cocok untuk perpindahan EVT-03; 044 memakai varian bahasa EVT-01. |
| Contingency | 018, 027, 030, 047, 050: keputusan 14.40, versi 14.45, registrasi 15.45, ceremony 16.45 pada simulasi hujan; rencana utama 044 dibedakan eksplisit. |
| Post event handover | 019, 048-050: penutupan publik 21.00 EVT-01 berbeda dari handover area 22.30; tindakan proses dapat tetap terbuka. |

Hal yang memerlukan perhatian: kapasitas kendaraan dispatch, kecukupan personel escort, durasi pemindahan saat hujan, waktu ceremony, kemampuan layanan catering, dan fasilitas alternatif belum diuji pada lokasi nyata. Angka 120, 280, 45, 80 adalah basis skenario tetap, bukan kapasitas resmi venue. Seluruh penilaian checklist awal tetap belum diperiksa; laporan INC-01 adalah kasus simulasi dan tidak mengesahkan checklist sebagai pekerjaan nyata selesai.

## E Retrieval readiness

File dapat diproses tanpa OCR. Relasi lintas dokumen membedakan persiapan, penanganan gangguan, dan evaluasi dengan topik yang beririsan. Genre terdiri atas handbook, job description, guideline, SOP, matriks, checklist, briefing, field log, FAQ, cue guide, rundown, timeline, dan laporan. Ini menyediakan variasi bentuk, bukan bukti kualitas retrieval.

Chunking berikutnya perlu mempertahankan heading, peran, kondisi pengecualian, dan batas kewenangan. Tabel harus diserialisasi dengan nama sheet, header, kode baris, dan konteks; angka jam tanpa aktivitas kehilangan makna. Rumus waktu perlu dibaca sebagai nilai durasi yang telah diperiksa. Boilerplate identitas dan provenance dapat dipindah menjadi metadata melalui kebijakan ingestion yang konsisten untuk seluruh metode. Jangan mengulang seluruh sheet Panduan pada setiap baris sehingga mendominasi skor leksikal. Log dan laporan simulasi memiliki overlap kronologi yang sah, tetapi fokus serta kedalaman berbeda.

## F Remaining limitations

- Seluruh domain knowledge masih pending practitioner validation; belum menjadi kebijakan perusahaan.
- Naratif ringkas mendominasi; sebagian berada di bawah sasaran 1.000-1.800 kata dokumen menengah. Praktisi dapat meminta rincian tambahan yang relevan tanpa filler.
- Rasterisasi dan contact sheet tidak menjamin setiap sel serta fitur native Word/Excel diuji pada semua mesin.
- Deteksi privasi dan duplikasi menggunakan heuristik, dengan keterbatasan yang dijelaskan; audit semantik menyeluruh belum dilakukan.
- Aturan venue, kondisi pantai, kapasitas, fasilitas, ritual, dan kebutuhan layanan memerlukan konfirmasi pihak terkait.
- Jumlah token serta chunk final belum diketahui. Profil estimasi hanya ilustrasi.
- Tidak tersedia query benchmark, label relevansi final, hasil retrieval, atau klaim metode terbaik.

## G Final deliverable status

Semua 50 dokumen utama telah dibuat dalam format blueprint dan dibuka ulang. Delapan file pendukung tersedia: tiga manifest, README, DOCUMENT_SUMMARIES, VALIDATION_CHECKLIST, QUALITY_REPORT, dan FILE_INVENTORY. ZIP berisi 58 file final di bawah wo_corpus/ dan lolos pembukaan ulang serta verifikasi integritas. Inventory memiliki 57 record karena mengecualikan dirinya dan ZIP luar untuk menghindari hash sirkular. Status penyelesaian pembuatan file: Completed. Status validasi praktisi: Pending.
