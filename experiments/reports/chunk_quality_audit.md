# Additional read-only chunk quality audit

Audit memakai existing chunks dan canonical documents. Tidak menjalankan ingestion/chunker atau mengubah code/data.

## Hasil utama

- Chunks: 371; canonical documents: 50.
- Orphan/fragment candidates: 0.
- Near-duplicate candidates: 0.
- Coverage: 768/768 operational blocks; full nonwhitespace coverage: 768.
- Rekomendasi: LAYAK_DIBEKUKAN_UNTUK_PILOT_RETRIEVAL.

## Distribusi proxy token

Counter existing: approx_unicode_chars_div4_v1 = ceil(Unicode code points / 4), bukan tokenizer model final.

| Bucket | Jumlah | Persen | DOCX | PDF | TXT | XLSX |
|---|---:|---:|---:|---:|---:|---:|
| <75 | 0 | 0.00% | 0 | 0 | 0 | 0 |
| 75-99 | 25 | 6.74% | 5 | 1 | 19 | 0 |
| 100-149 | 177 | 47.71% | 99 | 56 | 22 | 0 |
| 150-249 | 109 | 29.38% | 76 | 21 | 1 | 11 |
| 250-349 | 12 | 3.23% | 7 | 1 | 0 | 4 |
| 350-449 | 31 | 8.36% | 0 | 0 | 0 | 31 |
| 450-500 | 17 | 4.58% | 0 | 0 | 0 | 17 |

Source type provenance pada seluruh bucket nonempty: researcher_composed_operational_draft. Format ditampilkan terpisah karena source_type tidak sama dengan format.

## Orphan / fragment candidates

Chunk pendek tidak otomatis buruk. Pemeriksaan memakai primary body dari locator canonical, bukan hanya prefix heading.

- empty text
- single label without a value in primary body
- primary body contains only explicit above/below cross-reference
- body <=8 words or chunk <75 proxy tokens AND both title and heading absent
- continuation marker at body start AND missing heading or midblock span
- list/numbered procedure lacks heading
- table row lacks canonical/header/sheet/row context or is split
- overlap table row not whole

Tidak ada chunk yang memenuhi rule kandidat. Ini pemeriksaan sintaktik/struktural, bukan pembuktian semantik.

## Near duplicates

Semua 68,635 pasangan diperiksa pada dua view: full text serta primary body tanpa prefix/overlap. Minimal 30 word tokens per view dan length ratio >=0.90. Flag jika word 5-gram Jaccard >=0.85 atau SequenceMatcher ratio >=0.95 (autojunk=False).

NFC + casefold + Unicode word tokens including hyphenated codes; no code/number masking, stemming, stopword removal, embeddings, or semantic inference.

Tidak ada pasangan mencapai ambang kandidat.

Pasangan terdekat berikut hanya diagnostik, **bukan flags**:

| View | Chunk A | Chunk B | Jaccard 5-gram |
|---|---|---|---:|
| full_text | WO-DOC-040-C004 | WO-DOC-040-C005 | 0.357143 |
| full_text | WO-DOC-040-C001 | WO-DOC-040-C002 | 0.298343 |
| full_text | WO-DOC-040-C002 | WO-DOC-040-C003 | 0.260664 |
| full_text | WO-DOC-040-C003 | WO-DOC-040-C004 | 0.260664 |
| full_text | WO-DOC-011-C006 | WO-DOC-038-C006 | 0.247126 |
| primary_body | WO-DOC-040-C004 | WO-DOC-040-C005 | 0.256410 |
| primary_body | WO-DOC-011-C006 | WO-DOC-038-C006 | 0.215569 |
| primary_body | WO-DOC-008-C006 | WO-DOC-026-C006 | 0.198795 |
| primary_body | WO-DOC-008-C006 | WO-DOC-048-C007 | 0.197740 |
| primary_body | WO-DOC-008-C006 | WO-DOC-011-C006 | 0.197531 |

Lexical similarity only; absence of candidates is not proof of semantic uniqueness.

## Ketersediaan konteks

- Title field present dan aligned: 371/371.
- Heading field present: 371/371.
- Title literal dalam text: 53; heading literal: 308.
- XLSX dengan Sheet/Section/Header dan row context valid: 63/63.
- Tidak ada title/heading yang ditambahkan ke text; metadata terpisah tetap valid dan perlu dipertahankan downstream.

## Coverage

retrievable=true; nonempty text; kind not title, heading, or table_header. Structural blocks are context, administrative blocks remain excluded.

Canonical blocks: 1353; operational body blocks: 768; administrative excluded: 235; structural context excluded dari body denominator: 350.

Missing blocks: 0; partial nonwhitespace coverage: 0; locator issues: 0. Pemeriksaan mengonfirmasi span source benar-benar ada pada chunk text, bukan sekadar ID reference. Header tabel diperiksa tersendiri sebagai context.

Coverage ini canonical-to-chunk; tidak mengklaim audit semantik atau ekstraksi ulang terhadap file asli. Detail per dokumen ada dalam JSON.

## Dua puluh chunks terpendek

Urutan: token_count ascending, lalu chunk_id. Text ditampilkan lengkap; tidak ada truncation.

### WO-DOC-041-C008

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Apakah seseorang sudah hadir
- token_count: 77
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0029-0029",
      "line_end": 29,
      "line_start": 29,
      "section": "Apakah seseorang sudah hadir",
      "serialized_char_end": 275,
      "serialized_char_start": 0
    }
  ],
  "line_end": 29,
  "line_start": 29
}
```

Text lengkap:
```text
Apakah seseorang sudah hadir

Informasi kedatangan tidak diberikan kepada siapa pun yang bertanya. Arahkan kebutuhan yang sah kepada PIC keluarga. Salinan daftar tidak difoto, diteruskan ke vendor, atau ditempel pada area terbuka. Gunakan kode kelompok dalam komunikasi internal yang dapat terdengar tamu.
```

### WO-DOC-041-C011

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Tamu melaporkan barang hilang
- token_count: 79
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0038-0038",
      "line_end": 38,
      "line_start": 38,
      "section": "Tamu melaporkan barang hilang",
      "serialized_char_end": 282,
      "serialized_char_start": 0
    }
  ],
  "line_end": 38,
  "line_start": 38
}
```

Text lengkap:
```text
Tamu melaporkan barang hilang

Catat ciri umum, lokasi terakhir, waktu, dan kode pelapor. Hubungkan dengan PIC yang menangani lost and found. Jangan membuka tas atau menyebarkan foto dokumen pribadi. Jika barang ditemukan, kepemilikan diverifikasi melalui ciri pembeda serta prosedur pengelola sebelum diserahkan.
```

### WO-DOC-041-C013

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Jawaban antarstaf berbeda
- token_count: 81
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0044-0044",
      "line_end": 44,
      "line_start": 44,
      "section": "Jawaban antarstaf berbeda",
      "serialized_char_end": 297,
      "serialized_char_start": 0
    }
  ],
  "line_end": 44,
  "line_start": 44
}
```

Text lengkap:
```text
Jawaban antarstaf berbeda

Hentikan penyebaran jawaban yang belum jelas, periksa versi dokumen, lalu minta STAFF-08 menyatukan informasi melalui PIC terkait. Setelah keputusan diterima, ulangi kepada staf meja dan escort. Catat pertanyaan serta koreksi untuk debrief agar FAQ berikutnya diperbarui berdasarkan temuan aktual.
```

### WO-DOC-041-C012

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Lokasi acara berubah karena kondisi cuaca
- token_count: 83
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0041-0041",
      "line_end": 41,
      "line_start": 41,
      "section": "Lokasi acara berubah karena kondisi cuaca",
      "serialized_char_end": 286,
      "serialized_char_start": 0
    }
  ],
  "line_end": 41,
  "line_start": 41
}
```

Text lengkap:
```text
Lokasi acara berubah karena kondisi cuaca

Tunggu instruksi EC yang menyebut tujuan dan waktu berlaku. Ganti penunjuk arah dan tempatkan escort di simpang. PIC venue memastikan tujuan boleh dipakai; PIC vendor memeriksa kesiapan layanan. Informasikan tindakan praktis kepada tamu tanpa prediksi cuaca atau jaminan yang belum ada.
```

### WO-DOC-044-C015

- document_id: WO-DOC-044
- format: PDF
- title: Timeline Koordinasi International Wedding dan Outdoor Reception
- heading: 20.30 sampai 21.00 perpisahan 30 menit
- token_count: 85
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "p003-b007",
      "heading": "20.30 sampai 21.00 perpisahan 30 menit",
      "page_block": 7,
      "page_end": 3,
      "page_start": 3,
      "serialized_char_end": 297,
      "serialized_char_start": 0
    }
  ],
  "page_end": 3,
  "page_start": 3
}
```

Text lengkap:
```text
20.30 sampai 21.00 perpisahan 30 menit

PIC keluarga memeriksa kepulangan, LO mengonfirmasi kendaraan bila digunakan, dan PIC pengantin mengembalikan barang. MC menutup pukul 21.00 atas cue EC. Guest desk tetap memiliki penerima untuk tamu yang memerlukan bantuan. Vendor belum boleh melintasi jalur tamu dengan alat sampai zona dilepas.
```

### WO-DOC-041-C006

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Tamu membutuhkan bantuan bergerak
- token_count: 86
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0023-0023",
      "line_end": 23,
      "line_start": 23,
      "section": "Tamu membutuhkan bantuan bergerak",
      "serialized_char_end": 306,
      "serialized_char_start": 0
    }
  ],
  "line_end": 23,
  "line_start": 23
}
```

Text lengkap:
```text
Tamu membutuhkan bantuan bergerak

Tanyakan jenis bantuan yang diinginkan, lalu hubungi escort dan PIC venue untuk jalur yang tersedia. Minta izin sebelum menyentuh orang atau alat bantu. Jangan mengangkat tamu atau menggunakan jalur yang belum diperiksa. Kebutuhan pertolongan kesehatan diarahkan kepada petugas berwenang melalui PIC venue.
```

### WO-DOC-041-C009

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Tamu datang saat ceremony berjalan
- token_count: 86
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0032-0032",
      "line_end": 32,
      "line_start": 32,
      "section": "Tamu datang saat ceremony berjalan",
      "serialized_char_end": 305,
      "serialized_char_start": 0
    }
  ],
  "line_end": 32,
  "line_start": 32
}
```

Text lengkap:
```text
Tamu datang saat ceremony berjalan

Floor menentukan titik tunggu serta jeda masuk yang sesuai dengan arahan pemimpin prosesi. Escort menjaga pintu tetap dapat digunakan dan tidak memotong prosesi. Jangan mempersilakan masuk hanya karena kursi terlihat kosong. Guest desk tetap mencatat kedatangan dan memberi waktu pembaruan yang realistis.
```

### WO-DOC-041-C001

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: FAQ kerja guest desk
- token_count: 87
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0008-0008",
      "line_end": 8,
      "line_start": 8,
      "section": "FAQ kerja guest desk",
      "serialized_char_end": 326,
      "serialized_char_start": 0
    }
  ],
  "line_end": 8,
  "line_start": 8
}
```

Text lengkap:
```text
FAQ kerja guest desk

FAQ ini dipakai STAFF-08 dan escort pada EVT-02 di VENUE-02 untuk sekitar 280 tamu, serta EVT-03 di VENUE-03 untuk sekitar 45 tamu. Jawaban harus disesuaikan dengan versi daftar dan fasilitas yang telah dikonfirmasi. Bila informasi belum tersedia, sampaikan sedang dikonfirmasi dan beri penerima tindak lanjut; jangan menebak.
```

### WO-DOC-041-C007

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Tamu meminta makanan tertentu
- token_count: 87
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0026-0026",
      "line_end": 26,
      "line_start": 26,
      "section": "Tamu meminta makanan tertentu",
      "serialized_char_end": 316,
      "serialized_char_start": 0
    }
  ],
  "line_end": 26,
  "line_start": 26
}
```

Text lengkap:
```text
Tamu meminta makanan tertentu

Sampaikan kode kebutuhan kepada PIC vendor agar catering atau banquet mengonfirmasi. Jangan menjamin bebas bahan tertentu dari nama menu saja. Jika penyedia belum memberi jawaban, sampaikan keterbatasan informasi dan hubungkan tamu dengan personel layanan. Hindari menyebarkan informasi kesehatan melalui radio umum.
```

### WO-DOC-041-C005

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Tamu menanyakan toilet atau ruang ibadah
- token_count: 88
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0020-0020",
      "line_end": 20,
      "line_start": 20,
      "section": "Tamu menanyakan toilet atau ruang ibadah",
      "serialized_char_end": 307,
      "serialized_char_start": 0
    }
  ],
  "line_end": 20,
  "line_start": 20
}
```

Text lengkap:
```text
Tamu menanyakan toilet atau ruang ibadah

Berikan arah hanya ke fasilitas yang dikonfirmasi PIC venue. Jika belum diketahui, panggil penghubung venue dan jangan mengarahkan tamu ke pintu acak. Tawarkan escort apabila diperlukan. Tidak semua venue memiliki fasilitas yang sama; jangan membawa jawaban ballroom ke chapel atau garden tanpa pemeriksaan.
```

### WO-DOC-041-C010

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Transport dinner EVT-03 belum datang
- token_count: 88
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0035-0035",
      "line_end": 35,
      "line_start": 35,
      "section": "Transport dinner EVT-03 belum datang",
      "serialized_char_end": 312,
      "serialized_char_start": 0
    }
  ],
  "line_end": 35,
  "line_start": 35
}
```

Text lengkap:
```text
Transport dinner EVT-03 belum datang

Hubungi LO STAFF-10 untuk posisi kendaraan dan perkiraan yang dikonfirmasi penyedia. Kelompok menunggu di titik yang diizinkan PIC venue. Jangan meminta driver melanggar pembatasan akses atau menjanjikan waktu tiba tanpa sumber. LO mencatat jumlah naik serta tiba dan menyerahkan kelompok kepada penerima dinner.
```

### WO-DOC-041-C002

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Kode undangan tidak ada pada daftar
- token_count: 89
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0011-0011",
      "line_end": 11,
      "line_start": 11,
      "section": "Kode undangan tidak ada pada daftar",
      "serialized_char_end": 316,
      "serialized_char_start": 0
    }
  ],
  "line_end": 11,
  "line_start": 11
}
```

Text lengkap:
```text
Kode undangan tidak ada pada daftar

Arahkan tamu ke sisi meja, catat kode kelompok serta jumlah orang, dan minta PIC keluarga memverifikasi. Layanan reguler tetap berjalan. Jangan mengatakan tamu tidak diundang di depan antrean. WC membantu konfirmasi bila hubungan undangan belum jelas. Kursi baru diberikan setelah alokasi dan kondisi area diperiksa.
```

### WO-DOC-041-C004

- document_id: WO-DOC-041
- format: TXT
- title: FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu
- heading: Kursi yang dituju sudah ditempati
- token_count: 89
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0017-0017",
      "line_end": 17,
      "line_start": 17,
      "section": "Kursi yang dituju sudah ditempati",
      "serialized_char_end": 321,
      "serialized_char_start": 0
    }
  ],
  "line_end": 17,
  "line_start": 17
}
```

Text lengkap:
```text
Kursi yang dituju sudah ditempati

Minta escort menjaga tamu tetap nyaman sementara floor memeriksa versi seating serta kelompok penghuni. Jangan memindahkan orang secara paksa atau menukar kursi keluarga berdasarkan dugaan. Perubahan dicatat dengan kelompok asal, tujuan, jumlah, alasan, serta pengesah. Guest desk dan escort menerima pembaruan yang sama.
```

### WO-DOC-046-C004

- document_id: WO-DOC-046
- format: TXT
- title: Panduan Singkat Jalur Eskalasi dan Hak Pengambilan Keputusan
- heading: Bila penerima tidak menjawab
- token_count: 89
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0017-0017",
      "line_end": 17,
      "line_start": 17,
      "section": "Bila penerima tidak menjawab",
      "serialized_char_end": 323,
      "serialized_char_start": 0
    }
  ],
  "line_end": 17,
  "line_start": 17
}
```

Text lengkap:
```text
Bila penerima tidak menjawab

Gunakan jalur cadangan yang disepakati saat briefing. Sampaikan event, lokasi, fakta, dampak, serta keputusan yang dibutuhkan. Penerima membaca ulang waktu dan tujuan. Tidak ada jawaban bukan persetujuan. Floor menahan cue yang belum memenuhi prasyarat; runner membawa pesan tetapi tidak mengambil alih kewenangan pengesah.
```

### WO-DOC-043-C012

- document_id: WO-DOC-043
- format: DOCX
- title: Rundown Pemberkatan, Perpindahan Venue, dan Intimate Dinner
- heading: 17.30 sampai 18.00 entrance dan sambutan 30 menit
- token_count: 93
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "b0028",
      "body_position": 28,
      "heading": "17.30 sampai 18.00 entrance dan sambutan 30 menit",
      "heading_path": [
        "17.30 sampai 18.00 entrance dan sambutan 30 menit"
      ],
      "paragraph_position": 28,
      "serialized_char_end": 319,
      "serialized_char_start": 0
    }
  ]
}
```

Text lengkap:
```text
17.30 sampai 18.00 entrance dan sambutan 30 menit

EC mengesahkan cue setelah floor menerima kesiapan. MC, AV, dan dokumentasi mengakui nomor cue yang sama. PIC keluarga menyiapkan pembicara tanpa menutup jalur layanan. Jika sambutan memanjang, EC memeriksa dampaknya kepada catering dan waktu venue. WC mengurus prioritas client bila sesi tambahan perlu disederhanakan.
```

### WO-DOC-046-C006

- document_id: WO-DOC-046
- format: TXT
- title: Panduan Singkat Jalur Eskalasi dan Hak Pengambilan Keputusan
- heading: Jejak keputusan minimum
- token_count: 93
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0023-0023",
      "line_end": 23,
      "line_start": 23,
      "section": "Jejak keputusan minimum",
      "serialized_char_end": 345,
      "serialized_char_start": 0
    }
  ],
  "line_end": 23,
  "line_start": 23
}
```

Text lengkap:
```text
Jejak keputusan minimum

Tuliskan waktu, pemicu, keputusan, pengesah, penerima, instruksi pengganti, dan status tindak lanjut. Sebut versi rundown apabila berubah. Handover kepada pengganti harus mendapat pengakuan. Masalah selesai secara lapangan dapat tetap memiliki tindakan perbaikan terbuka setelah acara; pemilik tindak lanjut tidak boleh hilang saat kru checkout.
```

### WO-DOC-018-C001

- document_id: WO-DOC-018
- format: TXT
- title: Catatan Handover dan Perubahan Situasi pada Wedding Day
- heading: Catatan lapangan simulasi EVT-01
- token_count: 96
- orphan_candidate: false

Source locator:
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

Text lengkap:
```text
Catatan lapangan simulasi EVT-01

Event: EVT-01. Client: CLIENT-01. Venue: VENUE-01 garden villa. Jumlah rencana: sekitar 120 tamu. Waktu: WITA. Catatan ini merupakan kasus simulasi perpindahan dari garden ke area tertutup, bukan arsip kejadian perusahaan. Log disusun STAFF-07 dan diserahkan kepada STAFF-01 untuk pengendalian. Rundown awal versi 1.0 mengikuti briefing WO-DOC-012.
```

### WO-DOC-018-C003

- document_id: WO-DOC-018
- format: TXT
- title: Catatan Handover dan Perubahan Situasi pada Wedding Day
- heading: 14.30 pemeriksaan area
- token_count: 96
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0014-0014",
      "line_end": 14,
      "line_start": 14,
      "section": "14.30 pemeriksaan area",
      "serialized_char_end": 360,
      "serialized_char_start": 0
    }
  ],
  "line_end": 14,
  "line_start": 14
}
```

Text lengkap:
```text
14.30 pemeriksaan area

STAFF-06 melaporkan hujan dan permukaan garden basah; pengelola diminta memeriksa jalur serta fasilitas. STAFF-07 menahan pelepasan garden untuk tamu. STAFF-05 meminta perkiraan pemindahan dekor esensial, AV, dan layanan catering. STAFF-02 memeriksa preferensi client serta dampak terhadap ceremony. Status insiden INC-01 dibuka; kegiatan publik belum dimulai.
```

### WO-DOC-018-C007

- document_id: WO-DOC-018
- format: TXT
- title: Catatan Handover dan Perubahan Situasi pada Wedding Day
- heading: 15.40 izin buka dan 15.45 registrasi
- token_count: 96
- orphan_candidate: false

Source locator:
```json
{
  "blocks": [
    {
      "block_id": "l0026-0026",
      "line_end": 26,
      "line_start": 26,
      "section": "15.40 izin buka dan 15.45 registrasi",
      "serialized_char_end": 343,
      "serialized_char_start": 0
    }
  ],
  "line_end": 26,
  "line_start": 26
}
```

Text lengkap:
```text
15.40 izin buka dan 15.45 registrasi

STAFF-01 menerima laporan gabungan dan mengizinkan registrasi dibuka pukul 15.45. STAFF-08 mengakui dan mengarahkan tamu ke area tertutup. MC menerima kalimat pengantar perubahan lokasi melalui floor. Informasi kepada tamu menjelaskan lokasi serta bantuan akses, tanpa menyatakan prediksi cuaca atau jaminan keselamatan yang tidak dimiliki WO.
```

### WO-DOC-030-C001

- document_id: WO-DOC-030
- format: TXT
- title: Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara
- heading: Kartu keputusan untuk keterlambatan
- token_count: 96
- orphan_candidate: false

Source locator:
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

Text lengkap:
```text
Kartu keputusan untuk keterlambatan

EC STAFF-01 memutuskan perubahan rundown utama. PIC melaporkan posisi kegiatan, prasyarat yang gagal, perkiraan siap, dan dampak. WC STAFF-02 memeriksa persetujuan client bila biaya atau lingkup berubah. Floor tidak memotong urutan utama sendiri, MC tidak mengumumkan jam baru sebelum instruksi, dan runner tidak menyetujui perubahan atas nama EC.
```

## Rekomendasi

LAYAK_DIBEKUKAN_UNTUK_PILOT_RETRIEVAL

Freeze existing bytes and config for preliminary pilot retrieval; this is a chunk quality gate, not model optimality, domain validation, or retrieval performance evidence.

- Read the 20 shortest samples in full before approving the freeze.
- Retain title/heading and table guide_context in downstream consumers; some document titles are metadata only.
- Practitioner validation remains pending; token counts are pilot character proxies.
- Rerun token counting only in a future version after the embedding model is fixed; preserve this pilot snapshot.

## Immutability dan validasi audit

112 existing project files diperiksa hash, size, mtime_ns dan set nama; termasuk 57 file source corpus. Semua tetap sama. Hanya dua report audit ini ditulis.

Integrity checks: stored content hashes dan proxy token counts cocok; hasil analisis deterministik pada dua evaluasi in-memory; bucket mencakup seluruh chunks; tidak ada package/model yang diinstall.

Tidak ada commit, push, PR, deploy, atau implementasi retrieval.
