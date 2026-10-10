# Pilot ingestion and chunk audit

Corpus v1-draft; pending_practitioner_validation. No retrieval experiment executed.

Token proxy: ceil(Unicode code points / 4), including labels and separators. This is not a model tokenizer.

Target 500 / overlap up to 75 pilot proxy tokens. Overlap only within split natural units; no cross-section overlap.

## Statistics

```json
{
  "canonical_documents": 50,
  "chunks_by_format": {
    "DOCX": 187,
    "PDF": 79,
    "TXT": 42,
    "XLSX": 63
  },
  "chunks_per_document": {
    "max": 16,
    "median": 7.0,
    "min": 5
  },
  "chunks_per_document_detail": {
    "WO-DOC-001": 6,
    "WO-DOC-002": 6,
    "WO-DOC-003": 6,
    "WO-DOC-004": 5,
    "WO-DOC-005": 6,
    "WO-DOC-006": 5,
    "WO-DOC-007": 7,
    "WO-DOC-008": 6,
    "WO-DOC-009": 7,
    "WO-DOC-010": 8,
    "WO-DOC-011": 6,
    "WO-DOC-012": 7,
    "WO-DOC-013": 7,
    "WO-DOC-014": 6,
    "WO-DOC-015": 7,
    "WO-DOC-016": 6,
    "WO-DOC-017": 10,
    "WO-DOC-018": 9,
    "WO-DOC-019": 7,
    "WO-DOC-020": 6,
    "WO-DOC-021": 7,
    "WO-DOC-022": 6,
    "WO-DOC-023": 6,
    "WO-DOC-024": 6,
    "WO-DOC-025": 6,
    "WO-DOC-026": 6,
    "WO-DOC-027": 9,
    "WO-DOC-028": 8,
    "WO-DOC-029": 8,
    "WO-DOC-030": 7,
    "WO-DOC-031": 9,
    "WO-DOC-032": 9,
    "WO-DOC-033": 7,
    "WO-DOC-034": 6,
    "WO-DOC-035": 7,
    "WO-DOC-036": 7,
    "WO-DOC-037": 7,
    "WO-DOC-038": 6,
    "WO-DOC-039": 6,
    "WO-DOC-040": 7,
    "WO-DOC-041": 13,
    "WO-DOC-042": 8,
    "WO-DOC-043": 16,
    "WO-DOC-044": 16,
    "WO-DOC-045": 8,
    "WO-DOC-046": 6,
    "WO-DOC-047": 7,
    "WO-DOC-048": 7,
    "WO-DOC-049": 7,
    "WO-DOC-050": 10
  },
  "config": {
    "overlap_tokens": 75,
    "target_tokens": 500,
    "token_count_method": "approx_unicode_chars_div4_v1"
  },
  "duplicate_hash_groups": {},
  "environment": {
    "config_sha256": "adc0efc00ecf09625b187035f189087da778657cb93614493ea70492fc95435f",
    "dependencies": {
      "et-xmlfile": "2.0.0",
      "lxml": "6.1.3",
      "openpyxl": "3.1.5",
      "pypdf": "6.10.0",
      "python-docx": "1.2.0",
      "typing_extensions": "4.16.0"
    },
    "pipeline_code_sha256": "e3362bc033fb85ca7bc0d5dcb30eb1af425d7a1418c6c8af8021e6a37ae22d74",
    "pipeline_version": "1",
    "python": "3.12.14"
  },
  "failed_documents": 0,
  "number_of_chunks_with_overlap": 42,
  "number_of_chunks_without_heading": 0,
  "number_of_duplicate_content_hashes": 0,
  "number_of_empty_chunks": 0,
  "number_of_parsing_warnings": 0,
  "p95_method": "nearest_rank",
  "pilot_not_final_tokenizer": true,
  "source_documents": 50,
  "successfully_parsed": 50,
  "token_count": {
    "max": 485,
    "mean": 190.49056603773585,
    "median": 132,
    "min": 77,
    "p95": 447
  },
  "token_count_method": "approx_unicode_chars_div4_v1",
  "total_chunks": 371
}
```

## Samples

### WO-DOC-001-C001 (DOCX)

Document: WO-DOC-001; heading: Cara menggunakan struktur lapangan; pilot tokens: 159

Locator:
```json
{
  "blocks": [
    {
      "block_id": "b0006",
      "body_position": 6,
      "heading": "Cara menggunakan struktur lapangan",
      "heading_path": [
        "Cara menggunakan struktur lapangan"
      ],
      "paragraph_position": 6,
      "serialized_char_end": 598,
      "serialized_char_start": 0
    }
  ]
}
```

Text preview:
```text
Cara menggunakan struktur lapangan

Wedding Organizer X membagi pekerjaan menurut kendali acara, pendampingan orang, koordinasi pemasok, dan penguasaan fasilitas. Struktur ini dipakai untuk menetapkan siapa yang menyelesaikan pekerjaan dan siapa yang mengesahkan perubahan. Satu orang boleh memegang lebih dari satu peran pada acara kecil, tetapi penugasannya harus tertulis. Merangkap PIC pengantin dan pengendali seluruh vendor tidak dianjurkan ketika kedua pekerjaan berlangsung bersamaan. Daftar penugasan diterbitkan Event Coordinator sebelum briefing terakhir; kru membaca peran, pengganti, area kerja, dan jalur laporan mereka.
```

### WO-DOC-014-C001 (DOCX)

Document: WO-DOC-014; heading: Lingkup pendampingan; pilot tokens: 111

Locator:
```json
{
  "blocks": [
    {
      "block_id": "b0006",
      "body_position": 6,
      "heading": "Lingkup pendampingan",
      "heading_path": [
        "Lingkup pendampingan"
      ],
      "paragraph_position": 6,
      "serialized_char_end": 422,
      "serialized_char_start": 0
    }
  ]
}
```

Text preview:
```text
Lingkup pendampingan

Prosedur ini digunakan untuk persiapan pasangan dan keluarga inti pada EVT-02 di hotel ballroom VENUE-02 dengan sekitar 280 tamu. PIC pengantin STAFF-03 berkoordinasi dengan WC dan VEN-MUA-01. PIC keluarga STAFF-04 mengatur kelompok pendamping. Tujuannya menjaga waktu siap yang realistis, kenyamanan, privasi, serta perpindahan menuju akad. Urutan ritual hanya mengikuti konfirmasi pemimpin prosesi dan client melalui WC.
```

### WO-DOC-028-C001 (DOCX)

Document: WO-DOC-028; heading: Tujuan dan batas tindakan; pilot tokens: 131

Locator:
```json
{
  "blocks": [
    {
      "block_id": "b0006",
      "body_position": 6,
      "heading": "Tujuan dan batas tindakan",
      "heading_path": [
        "Tujuan dan batas tindakan"
      ],
      "paragraph_position": 6,
      "serialized_char_end": 494,
      "serialized_char_start": 0
    }
  ]
}
```

Text preview:
```text
Tujuan dan batas tindakan

Panduan ini mengatur koordinasi ketika pasokan listrik atau layanan yang bergantung padanya terganggu. Berlaku untuk garden EVT-01 dan ballroom EVT-02 sesuai fasilitas masing-masing. WO mengoordinasikan penghentian kegiatan, perlindungan arus orang, komunikasi, serta keputusan acara. Pemeriksaan instalasi, isolasi sumber daya, penyambungan backup, dan penilaian kelayakan hanya dilakukan petugas berkompeten yang berwenang. Dokumen ini tidak memberi prosedur perbaikan listrik untuk kru umum.
```

### WO-DOC-005-C001 (PDF)

Document: WO-DOC-005; heading: Pegangan cepat kru pendukung; pilot tokens: 135

Locator:
```json
{
  "blocks": [
    {
      "block_id": "p001-b007",
      "heading": "Pegangan cepat kru pendukung",
      "page_block": 7,
      "page_end": 1,
      "page_start": 1,
      "serialized_char_end": 510,
      "serialized_char_start": 0
    }
  ],
  "page_end": 1,
  "page_start": 1
}
```

Text preview:
```text
Pegangan cepat kru pendukung

Panduan ini digunakan runner, LO, dan guest desk saat EVT-03 di VENUE-03 dengan 45 tamu. Ketiganya bekerja dekat tamu, tetapi menerima tugas dari PIC yang berbeda. Runner menerima penugasan logistik dari PIC terkait melalui pengendali tugas. LO transport bekerja dengan PIC keluarga dan penyedia kendaraan. Guest desk melapor kepada STAFF-08. Jika dua orang memberikan tugas bersamaan, kru menyampaikan pekerjaan yang sedang berjalan dan meminta prioritas; jangan meninggalkan penugasan pertama tanpa handover.
```

### WO-DOC-021-C001 (PDF)

Document: WO-DOC-021; heading: Titik temu WO dan banquet; pilot tokens: 114

Locator:
```json
{
  "blocks": [
    {
      "block_id": "p001-b007",
      "heading": "Titik temu WO dan banquet",
      "page_block": 7,
      "page_end": 1,
      "page_start": 1,
      "serialized_char_end": 429,
      "serialized_char_start": 0
    }
  ],
  "page_end": 1,
  "page_start": 1
}
```

Text preview:
```text
Titik temu WO dan banquet

Pada EVT-02, sekitar 280 tamu mengikuti akad dan resepsi di ballroom VENUE-02. Banquet hotel dan penyedia catering yang benar-benar digunakan bertanggung jawab atas penyiapan serta layanan makanan sesuai lingkup mereka. WO mengendalikan arus acara dan pertukaran informasi. PIC vendor STAFF-05 menjadi jalur koordinasi layanan, PIC venue STAFF-06 menghubungkan kebutuhan fasilitas hotel, dan EC mengesahkan perubahan waktu utama.
```

### WO-DOC-037-C001 (PDF)

Document: WO-DOC-037; heading: Konteks dan asumsi lokasi; pilot tokens: 114

Locator:
```json
{
  "blocks": [
    {
      "block_id": "p001-b007",
      "heading": "Konteks dan asumsi lokasi",
      "page_block": 7,
      "page_end": 1,
      "page_start": 1,
      "serialized_char_end": 426,
      "serialized_char_start": 0
    }
  ],
  "page_end": 1,
  "page_start": 1
}
```

Text preview:
```text
Konteks dan asumsi lokasi

EVT-04 adalah beach wedding untuk sekitar 80 tamu di VENUE-04. Penggunaan area diasumsikan telah memperoleh persetujuan pengelola lokasi; dokumen ini tidak menjadi bukti izin, prediksi pasang surut, atau jaminan keamanan pantai. PIC venue memverifikasi ketentuan lokasi dan berkoordinasi dengan pihak berwenang bila diperlukan. EC mengendalikan keputusan operasional, WC mengurus persetujuan client terkait biaya atau lingkup.
```

### WO-DOC-012-C001 (TXT)

Document: WO-DOC-012; heading: Briefing simulasi H-1 pukul 17.00 WITA; pilot tokens: 105

Locator:
```json
{
  "blocks": [
    {
      "block_id": "l0008-0008",
      "line_end": 8,
      "line_start": 8,
      "section": "Briefing simulasi H-1 pukul 17.00 WITA",
      "serialized_char_end": 380,
      "serialized_char_start": 0
    }
  ],
  "line_end": 8,
  "line_start": 8
}
```

Text preview:
```text
Briefing simulasi H-1 pukul 17.00 WITA

Event EVT-01, CLIENT-01, VENUE-01 garden villa, sekitar 120 tamu. Ceremony sore dan resepsi malam menggunakan rundown versi 1.0. Catatan ini adalah briefing terisi untuk simulasi; seluruh status di bawah merupakan asumsi latihan. STAFF-01 memimpin kendali acara dan STAFF-02 memegang komunikasi client. Jangan memakai catatan ini sebagai bukti kesiapan fasilitas pada acara nyata.
```

### WO-DOC-018-C001 (TXT)

Document: WO-DOC-018; heading: Catatan lapangan simulasi EVT-01; pilot tokens: 96

Locator:
```json
{
  "blocks": [
    {
      "block_id": "l0008-0008",
      "line_end": 8,
      "line_start": 8,
      "section": "Catatan lapangan simulasi EVT-01",
      "serialized_char_end": 348,
      "serialized_char_start": 0
    }
  ],
  "line_end": 8,
  "line_start": 8
}
```

Text preview:
```text
Catatan lapangan simulasi EVT-01

Event: EVT-01. Client: CLIENT-01. Venue: VENUE-01 garden villa. Jumlah rencana: sekitar 120 tamu. Waktu: WITA. Catatan ini merupakan kasus simulasi perpindahan dari garden ke area tertutup, bukan arsip kejadian perusahaan. Log disusun STAFF-07 dan diserahkan kepada STAFF-01 untuk pengendalian. Rundown awal versi 1.0 mengikuti briefing WO-DOC-012.
```

### WO-DOC-030-C001 (TXT)

Document: WO-DOC-030; heading: Kartu keputusan untuk keterlambatan; pilot tokens: 96

Locator:
```json
{
  "blocks": [
    {
      "block_id": "l0008-0008",
      "line_end": 8,
      "line_start": 8,
      "section": "Kartu keputusan untuk keterlambatan",
      "serialized_char_end": 347,
      "serialized_char_start": 0
    }
  ],
  "line_end": 8,
  "line_start": 8
}
```

Text preview:
```text
Kartu keputusan untuk keterlambatan

EC STAFF-01 memutuskan perubahan rundown utama. PIC melaporkan posisi kegiatan, prasyarat yang gagal, perkiraan siap, dan dampak. WC STAFF-02 memeriksa persetujuan client bila biaya atau lingkup berubah. Floor tidak memotong urutan utama sendiri, MC tidak mengumumkan jam baru sebelum instruksi, dan runner tidak menyetujui perubahan atas nama EC.
```

### WO-DOC-006-C001 (XLSX)

Document: WO-DOC-006; heading: Matriks Pembagian Tanggung Jawab Tim Wedding Day / Operasional; pilot tokens: 391

Locator:
```json
{
  "blocks": [
    {
      "block_id": "s1-r0006",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 6,
      "row_start": 6,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 172,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0007",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 7,
      "row_start": 7,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 178,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0008",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 8,
      "row_start": 8,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 195,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0009",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 9,
      "row_start": 9,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 176,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0010",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 10,
      "row_start": 10,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 177,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0011",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 11,
      "row_start": 11,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 183,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0012",
      "column_end": "F",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 12,
      "row_start": 12,
      "section": "Matriks Pembagian Tanggung Jawab Tim Wedding Day",
      "serialized_char_end": 191,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    }
  ],
  "header_row": 5,
  "row_end": 12,
  "row_start": 6,
  "sheet": "Operasional",
  "table": "Operasional:table-1"
}
```

Text preview:
```text
Sheet: Operasional
Section: Matriks Pembagian Tanggung Jawab Tim Wedding Day
Header: Tugas | A | R | C | I | Keluaran dan batas kewenangan

Bagian: Konteks 2
Keterangan: A adalah pengesah operasional untuk satu tugas; R pelaksana utama, C dimintai masukan, I penerima informasi.

Row: 6
Tugas: Menetapkan lingkup layanan
A: WC
R: WC
C: EC; client
I: PIC vendor
Keluaran dan batas kewenangan: Client menyetujui lingkup dan biaya; WC mencatat persetujuan

Row: 7
Tugas: Menyusun rundown utama
A: EC
R: floor
C: WC; PIC vendor; PIC venue
I: seluruh PIC
Keluaran dan batas kewenangan: Versi aktif disahkan EC setelah prasyarat diperiksa

Row: 8
Tugas: Mengonfirmasi urutan ritual
A: WC
R: WC
C: pemimpin prosesi; client
I: floor; PIC keluarga
Keluaran dan batas kewenangan: Arahan ritual berasal dari pihak berwenang, bukan asumsi WO

Row: 9
Tugas: Membagi personel dan pengganti
A: EC
R: EC
C: WC; seluruh PIC
I: runner; LO
Keluaran dan batas kewenangan: Setiap fungsi kritis mempunyai penerima serta pengganti

Row: 10
Tugas: Memeriksa akses loading
A: EC
R: PIC venue
C: pengelola; PIC vendor
I: runner
Keluaran dan batas kewenangan: Pengelola mengizinkan akses; EC mengatur urutan kerja

Row: 11
Tugas: Merekonsiliasi lingkup dekor
A: EC
R: PIC vendor
C: WC; PIC venue
I: floor
Keluaran dan batas kewenangan: Selisih tampilan dibawa WC kepada client bila mengubah lingkup

Row: 12
Tugas: Menilai fasi
```

### WO-DOC-025-C001 (XLSX)

Document: WO-DOC-025; heading: Matriks Penugasan Transport, Driver, Shuttle, dan Logistik / Operasional; pilot tokens: 412

Locator:
```json
{
  "blocks": [
    {
      "block_id": "s1-r0006",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 6,
      "row_start": 6,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 235,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0007",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 7,
      "row_start": 7,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 247,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0008",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 8,
      "row_start": 8,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 264,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0009",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 9,
      "row_start": 9,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 246,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0010",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 10,
      "row_start": 10,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 216,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0011",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 11,
      "row_start": 11,
      "section": "Matriks Penugasan Transport, Driver, Shuttle, dan Logistik",
      "serialized_char_end": 223,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    }
  ],
  "header_row": 5,
  "row_end": 11,
  "row_start": 6,
  "sheet": "Operasional",
  "table": "Operasional:table-1"
}
```

Text preview:
```text
Sheet: Operasional
Section: Matriks Penugasan Transport, Driver, Shuttle, dan Logistik
Header: Waktu WITA | Unit atau tugas | Muatan atau kelompok | Jumlah orang | PIC | Prasyarat | Penerima dan fallback

Row: 6
Waktu WITA: H-7
Unit atau tugas: Verifikasi rute
Muatan atau kelompok: chapel ke dinner
Jumlah orang: 0
PIC: PIC venue
Prasyarat: Pengelola mengonfirmasi akses
Penerima dan fallback: LO menerima batas; revisi durasi bila berbeda

Row: 7
Waktu WITA: H-7
Unit atau tugas: Verifikasi kapasitas
Muatan atau kelompok: TRN-01 sampai TRN-03
Jumlah orang: 0
PIC: PIC vendor
Prasyarat: Penyedia memeriksa kendaraan
Penerima dan fallback: EC menerima kemampuan aktual, bukan asumsi tabel

Row: 8
Waktu WITA: H-3
Unit atau tugas: Konfirmasi bantuan akses
Muatan atau kelompok: kelompok berkebutuhan bantuan
Jumlah orang: 0
PIC: PIC keluarga
Prasyarat: Tanyakan bantuan yang diinginkan
Penerima dan fallback: LO dan penyedia memilih dukungan terkonfirmasi

Row: 9
Waktu WITA: H-1
Unit atau tugas: Konfirmasi driver
Muatan atau kelompok: DRIVER-01 sampai DRIVER-03
Jumlah orang: 0
PIC: PIC vendor
Prasyarat: Penyedia menunjuk penanggung jawab
Penerima dan fallback: LO menerima kanal transport konseptual

Row: 10
Waktu WITA: 12:30:00
Unit atau tugas: Briefing dispatch
Muatan atau kelompok: STAFF-10
Jumlah orang: 1
PIC: EC
Prasyarat: Rundown dan daftar berlaku
Penerima dan fallback: LO mengulang ti
```

### WO-DOC-040-C001 (XLSX)

Document: WO-DOC-040; heading: Matriks Seating Allocation dan Penugasan Guest Escort / Operasional; pilot tokens: 384

Locator:
```json
{
  "blocks": [
    {
      "block_id": "s1-r0006",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 6,
      "row_start": 6,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 223,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0007",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 7,
      "row_start": 7,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 223,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0008",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 8,
      "row_start": 8,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 223,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0009",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 9,
      "row_start": 9,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 223,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0010",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 10,
      "row_start": 10,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 224,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0011",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 11,
      "row_start": 11,
      "section": "Matriks Seating Allocation dan Penugasan Guest Escort",
      "serialized_char_end": 224,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    }
  ],
  "header_row": 5,
  "row_end": 11,
  "row_start": 6,
  "sheet": "Operasional",
  "table": "Operasional:table-1"
}
```

Text preview:
```text
Sheet: Operasional
Section: Matriks Seating Allocation dan Penugasan Guest Escort
Header: Kelompok | Alokasi | Jumlah orang | Sektor | Escort | Titik serah terima | Kontrol perubahan

Row: 6
Kelompok: G-01
Alokasi: SEAT-01
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-11
Titik serah terima: Guest desk ke floor sektor A
Kontrol perubahan: PIC keluarga konfirmasi prioritas, tidak tukar tanpa verifikasi

Row: 7
Kelompok: G-02
Alokasi: SEAT-02
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-12
Titik serah terima: Guest desk ke floor sektor A
Kontrol perubahan: PIC keluarga konfirmasi prioritas, tidak tukar tanpa verifikasi

Row: 8
Kelompok: G-03
Alokasi: SEAT-03
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-11
Titik serah terima: Guest desk ke floor sektor A
Kontrol perubahan: PIC keluarga konfirmasi prioritas, tidak tukar tanpa verifikasi

Row: 9
Kelompok: G-04
Alokasi: SEAT-04
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-12
Titik serah terima: Guest desk ke floor sektor A
Kontrol perubahan: PIC keluarga konfirmasi prioritas, tidak tukar tanpa verifikasi

Row: 10
Kelompok: G-05
Alokasi: SEAT-05
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-11
Titik serah terima: Guest desk ke floor sektor A
Kontrol perubahan: PIC keluarga konfirmasi prioritas, tidak tukar tanpa verifikasi

Row: 11
Kelompok: G-06
Alokasi: SEAT-06
Jumlah orang: 10
Sektor: A keluarga
Escort: STAFF-
```

### WO-DOC-042-C001 (XLSX)

Document: WO-DOC-042; heading: Rundown Operasional Akad dan Resepsi Hotel Ballroom / Operasional; pilot tokens: 367

Locator:
```json
{
  "blocks": [
    {
      "block_id": "s1-r0006",
      "column_end": "I",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 6,
      "row_start": 6,
      "section": "Rundown Operasional Akad dan Resepsi Hotel Ballroom",
      "serialized_char_end": 241,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0007",
      "column_end": "I",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 7,
      "row_start": 7,
      "section": "Rundown Operasional Akad dan Resepsi Hotel Ballroom",
      "serialized_char_end": 249,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0008",
      "column_end": "I",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 8,
      "row_start": 8,
      "section": "Rundown Operasional Akad dan Resepsi Hotel Ballroom",
      "serialized_char_end": 251,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0009",
      "column_end": "I",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 9,
      "row_start": 9,
      "section": "Rundown Operasional Akad dan Resepsi Hotel Ballroom",
      "serialized_char_end": 257,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0010",
      "column_end": "I",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 10,
      "row_start": 10,
      "section": "Rundown Operasional Akad dan Resepsi Hotel Ballroom",
      "serialized_char_end": 258,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    }
  ],
  "header_row": 5,
  "row_end": 10,
  "row_start": 6,
  "sheet": "Operasional",
  "table": "Operasional:table-1"
}
```

Text preview:
```text
Sheet: Operasional
Section: Rundown Operasional Akad dan Resepsi Hotel Ballroom
Header: Mulai | Selesai | Durasi menit | Aktivitas | PIC | Vendor terkait | Cue | Dependensi | Fallback atau komunikasi

Row: 6
Mulai: 05:30:00
Selesai: 06:00:00
Durasi menit: 30
Aktivitas: Crew inti dan akses ruang
PIC: EC
Vendor terkait: VEN-MUA-01
Cue: Cek akses
Dependensi: Pengelola melepas ruang
Fallback atau komunikasi: PIC venue konfirmasi bila tertahan

Row: 7
Mulai: 06:00:00
Selesai: 07:30:00
Durasi menit: 90
Aktivitas: Makeup pasangan
PIC: PIC pengantin
Vendor terkait: VEN-MUA-01
Cue: Mulai layanan
Dependensi: Lingkup serta urutan diakui
Fallback atau komunikasi: WC meminta prioritas bila berubah

Row: 8
Mulai: 06:00:00
Selesai: 07:00:00
Durasi menit: 60
Aktivitas: Setup akhir ballroom
PIC: PIC vendor
Vendor terkait: VEN-DEC-01; VEN-AV-01
Cue: Area kerja
Dependensi: Akses loading disetujui
Fallback atau komunikasi: EC menentukan keluaran kritis

Row: 9
Mulai: 07:00:00
Selesai: 07:30:00
Durasi menit: 30
Aktivitas: Uji perangkat oleh teknisi
PIC: PIC vendor
Vendor terkait: VEN-AV-01
Cue: Sound check
Dependensi: Posisi dan fasilitas dinilai
Fallback atau komunikasi: Tahan cue jika perangkat belum siap

Row: 10
Mulai: 07:30:00
Selesai: 08:00:00
Durasi menit: 30
Aktivitas: Dressing serta benda prosesi
PIC: PIC pengantin
Vendor terkait: VEN-MUA-01
Cue: Cek siap
Dependensi: Makeup selesai, barang
```

### WO-DOC-048-C001 (XLSX)

Document: WO-DOC-048; heading: Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset / Operasional; pilot tokens: 382

Locator:
```json
{
  "blocks": [
    {
      "block_id": "s1-r0006",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 6,
      "row_start": 6,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 212,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0007",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 7,
      "row_start": 7,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 219,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0008",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 8,
      "row_start": 8,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 235,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0009",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 9,
      "row_start": 9,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 211,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0010",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 10,
      "row_start": 10,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 221,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    },
    {
      "block_id": "s1-r0011",
      "column_end": "G",
      "column_start": "A",
      "header_row": 5,
      "merged_ranges": [],
      "row_end": 11,
      "row_start": 11,
      "section": "Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset",
      "serialized_char_end": 210,
      "serialized_char_start": 0,
      "sheet": "Operasional",
      "table": "Operasional:table-1"
    }
  ],
  "header_row": 5,
  "row_end": 11,
  "row_start": 6,
  "sheet": "Operasional",
  "table": "Operasional:table-1"
}
```

Text preview:
```text
Sheet: Operasional
Section: Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset
Header: Urutan | Pekerjaan | PIC | Kriteria selesai | Penerima atau eskalasi | Status | Waktu aktual dan temuan

Row: 6
Urutan: 1
Pekerjaan: Konfirmasi cue tutup
PIC: floor
Kriteria selesai: EC memberi izin setelah kesiapan pulang
Penerima atau eskalasi: MC menerima C penutup
Status: Belum diperiksa
Waktu aktual dan temuan:

Row: 7
Urutan: 2
Pekerjaan: Periksa tamu masih di area
PIC: guest desk
Kriteria selesai: Kelompok tersisa mempunyai pendamping
Penerima atau eskalasi: PIC keluarga dan EC
Status: Belum diperiksa
Waktu aktual dan temuan:

Row: 8
Urutan: 3
Pekerjaan: Konfirmasi transport pulang
PIC: LO
Kriteria selesai: Kendaraan serta tujuan terkonfirmasi bila digunakan
Penerima atau eskalasi: PIC keluarga menerima status
Status: Belum diperiksa
Waktu aktual dan temuan:

Row: 9
Urutan: 4
Pekerjaan: Periksa foto akhir
PIC: PIC vendor
Kriteria selesai: WC dan dokumentasi mengakui selesai
Penerima atau eskalasi: EC sebelum lepas zona
Status: Belum diperiksa
Waktu aktual dan temuan:

Row: 10
Urutan: 5
Pekerjaan: Kembalikan barang pengantin
PIC: PIC pengantin
Kriteria selesai: Penerima disetujui dan tercatat
Penerima atau eskalasi: WC bila belum diterima
Status: Belum diperiksa
Waktu aktual dan temuan:

Row: 11
Urutan: 6
Pekerjaan: Serahkan keluarga tersisa
PIC: PIC keluarga
Kriteria sel
```

## Boilerplate

Full-block exact administrative matches only. Operational mentions, event context in prose, negations, document relations in operational prose and rundown versions remain.

```json
{
  "examples": [
    {
      "after_retrievable_text": "",
      "before": "Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "document_title_to_metadata",
      "source_locator": {
        "body_position": 1,
        "heading": null,
        "heading_path": [],
        "paragraph_position": 1
      }
    },
    {
      "after_retrievable_text": "",
      "before": "Konteks: EVT-01, EVT-02, EVT-03, EVT-04. Dokumen terkait: WO-DOC-002, WO-DOC-003, WO-DOC-004, WO-DOC-006, WO-DOC-045, WO-DOC-046.",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "event_relation_banner_to_metadata",
      "source_locator": {
        "body_position": 4,
        "heading": null,
        "heading_path": [],
        "paragraph_position": 4
      }
    },
    {
      "after_retrievable_text": "",
      "before": "Wedding Organizer X | WO-DOC-005 1",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "exact_pdf_running_footer_to_metadata",
      "source_locator": {
        "heading": null,
        "page_block": 1,
        "page_end": 1,
        "page_start": 1
      }
    },
    {
      "after_retrievable_text": "",
      "before": "Draft operasional susunan peneliti. Status: belum divalidasi praktisi. Skenario dan catatan pelaksanaan bersifat simulasi.",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "exact_provenance_notice_to_metadata",
      "source_locator": {
        "body_position": 3,
        "heading": null,
        "heading_path": [],
        "paragraph_position": 3
      }
    },
    {
      "after_retrievable_text": "",
      "before": "Bagian: Identitas\nKeterangan: WO-DOC-006 | Wedding Organizer X | Versi 1.0",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "guide_administrative_row_to_metadata",
      "source_locator": {
        "column_end": "B",
        "column_start": "A",
        "header_row": 5,
        "merged_ranges": [],
        "row_end": 6,
        "row_start": 6,
        "section": "Panduan",
        "sheet": "Panduan",
        "table": "Panduan:table-1"
      }
    },
    {
      "after_retrievable_text": "",
      "before": "WO-DOC-001  |  Versi 1.0  |  Wedding Organizer X",
      "retained_as": "canonical block plus administrative_blocks metadata",
      "rule": "identity_version_status_to_metadata",
      "source_locator": {
        "body_position": 2,
        "heading": null,
        "heading_path": [],
        "paragraph_position": 2
      }
    }
  ],
  "patterns": {
    "document_code": {
      "chunk_ids": [
        "WO-DOC-008-C004",
        "WO-DOC-009-C004",
        "WO-DOC-013-C007",
        "WO-DOC-017-C010",
        "WO-DOC-018-C001",
        "WO-DOC-018-C009",
        "WO-DOC-024-C003",
        "WO-DOC-027-C008",
        "WO-DOC-027-C009",
        "WO-DOC-030-C005",
        "WO-DOC-036-C006",
        "WO-DOC-044-C007",
        "WO-DOC-048-C007",
        "WO-DOC-050-C001"
      ],
      "chunks_with_pattern": 14,
      "occurrences": 15
    },
    "draft_notice": {
      "chunk_ids": [],
      "chunks_with_pattern": 0,
      "occurrences": 0
    },
    "organization_name": {
      "chunk_ids": [
        "WO-DOC-001-C001",
        "WO-DOC-006-C005",
        "WO-DOC-034-C006",
        "WO-DOC-050-C001"
      ],
      "chunks_with_pattern": 4,
      "occurrences": 4
    },
    "pending_validation": {
      "chunk_ids": [],
      "chunks_with_pattern": 0,
      "occurrences": 0
    },
    "version": {
      "chunk_ids": [
        "WO-DOC-005-C005",
        "WO-DOC-008-C005",
        "WO-DOC-012-C001",
        "WO-DOC-012-C007",
        "WO-DOC-018-C001",
        "WO-DOC-018-C002",
        "WO-DOC-018-C005",
        "WO-DOC-018-C008",
        "WO-DOC-027-C008",
        "WO-DOC-030-C005",
        "WO-DOC-044-C007",
        "WO-DOC-047-C004",
        "WO-DOC-049-C005",
        "WO-DOC-050-C002",
        "WO-DOC-050-C004",
        "WO-DOC-050-C006",
        "WO-DOC-050-C009"
      ],
      "chunks_with_pattern": 17,
      "occurrences": 20
    }
  },
  "policy": "Full-block exact administrative matches only. Operational mentions, event context in prose, negations, document relations in operational prose and rundown versions remain.",
  "retained_operational_examples": [
    {
      "chunk_id": "WO-DOC-001-C001",
      "text": "Cara menggunakan struktur lapangan\n\nWedding Organizer X membagi pekerjaan menurut kendali acara, pendampingan orang, koordinasi pemasok, dan penguasaan fasilitas. Struktur ini dipakai untuk menetapkan siapa yang menyelesaikan pekerjaan dan siapa yang mengesahkan perubahan. Satu orang boleh memegang lebih dari satu peran pada acara kecil, tetapi penugasannya harus tertulis. Merangkap PIC pengantin dan pengendali seluruh vendor tidak dianjurkan ketika kedua pekerjaan berlangsung bersamaan. Daftar penugasan diterbitkan Event Coordinator sebelum briefing terakhir; kru membaca peran, pengganti, area kerja, dan jalur laporan mereka."
    },
    {
      "chunk_id": "WO-DOC-006-C005",
      "text": "Sheet: Panduan\nSection: Panduan\nHeader: Bagian | Keterangan\n\nRow: 9\nBagian: Cara pakai\nKeterangan: Kegiatan berstatus rencana atau belum diperiksa. Isi temuan setelah pemeriksaan; jangan menandai selesai tanpa bukti.\n\nRow: 10\nBagian: Konteks 1\nKeterangan: Matriks penugasan Wedding Organizer X.\n\nRow: 11\nBagian: Konteks 2\nKeterangan: A adalah pengesah operasional untuk satu tugas; R pelaksana utama, C dimintai masukan, I penerima informasi.\n\nRow: 12\nBagian: Konteks 3\nKeterangan: Persetujuan client atas biaya atau lingkup serta kelayakan fasilitas oleh petugas berwenang dicatat pada kolom batas, tidak digantikan oleh A.\n\nRow: 13\nBagian: Konteks 4\nKeterangan: STAFF-01 EC; STAFF-02 WC; STAFF-03 PIC pengantin; STAFF-04 PIC keluarga; STAFF-05 PIC vendor; STAFF-06 PIC venue; STAFF-07 floor; STAFF-08 guest desk; STAFF-09 runner; STAFF-10 LO.\n\nRow: 14\nBagian: Konteks 5\nKeterangan: Pada event kecil perangkapan harus tertulis dan beban kerja diperiksa EC.\n\nRow: 15\nBagian: Konteks 6\nKeterangan: Sem"
    }
  ],
  "rule_counts": {
    "document_title_to_metadata": 40,
    "event_relation_banner_to_metadata": 45,
    "exact_pdf_running_footer_to_metadata": 19,
    "exact_provenance_notice_to_metadata": 40,
    "guide_administrative_row_to_metadata": 30,
    "identity_version_status_to_metadata": 61
  }
}
```

## Review before retrieval

- Review PDF typography and TXT stanza heading heuristics against the original files.
- Review XLSX row boundaries, cached formulas, RACI definitions and inherited guide_context.
- Review retained operational organization names, document references and rundown versions; do not delete these globally.
- Review small natural sections and large table splits; pilot counts do not imply optimal retrieval settings.
- Practitioner validation remains pending; freeze extraction/chunk policy before query/qrels work.
