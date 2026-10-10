# Milestone 9A.12 — Offline retrieval development pilot & qrels coverage audit

**MILESTONE 9A.12 — DEVELOPMENT PILOT COMPLETE, QRELS COVERAGE AUDITED**

**NOT FINAL EVALUATION.** Seluruh judgments adalah AI silver provisional; UNJUDGED berarti belum diketahui, bukan nonrelevant. Tidak ada metrik efektivitas, inference, indexing, fitting, tuning, atau judgment baru.

## 1. Approval gate dan konfigurasi

Laporan Milestone 9A.11 dibaca lengkap. R3 V2 COMPLETE dan R4 integrasi cached PASS; tidak ada blocker untuk scoring offline. Live GPU end-to-end lokal tetap belum dibuktikan dan tidak dijalankan dalam milestone ini.

Snapshot: `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`. Fingerprint: `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

Preflight loaders existing memverifikasi snapshot V1/V2, artefak sumber, serialization, index manifest/checksums, model identity, pinned revision, dan 18 query artifacts. R1/R2/R3 memiliki tepat 371 chunk IDs dengan urutan dan shared serialized text/hash identik; 50 document IDs. Konteks XLSX tetap berasal dari serializer existing. Evidence/qrels tidak ditambahkan ke retrieval input.

Protocol TOML existing tetap berlabel PROPOSED dan terikat V1. Binding V2 menggunakan overlay in-memory existing `prepare_v2_indexes.bind_v2`, tanpa menulis ulang protokol. Otorisasi pilot berasal dari instruksi pengguna Milestone 9A.12; tidak mengotorisasi evaluasi utama.

| Metode | Konfigurasi existing |
|---|---|
| R1 | TF-IDF unigram; smoothed IDF; L2; exact cosine |
| R2 | BM25Okapi k1=1.5, b=0.75, epsilon=0.25 |
| R3 | Exact cosine terhadap 371 vectors full Colab V2, 18 query cache validated |
| R4 | RRF k=60, weights 1/1; full Dense 371; BM25 strict positive candidates |

BGE-M3 identity: `BAAI/bge-m3`, revision `5617a9f61b028005a4858fdac845db406aefb181`, dimension 1024, max_length 640, encoding provenance CUDA FP16 batch 1 dense-only. Tidak memuat weights atau mengimpor Torch. Original query texts dipertahankan; normalization NFC/line endings/strip existing diterapkan identik. Tidak ada prompt tambahan.

Ranking diurutkan score descending unrounded, kemudian chunk_id ascending Unicode. R1/R2 menyimpan seluruh kandidat berskor positif (270–371 per query; total 6.411 masing-masing), tanpa zero-tail padding; R3/R4 masing-masing 371 per query (total 6.678 masing-masing). Metadata, finite scores, unique IDs, canonical document mapping, determinisme repeat dan kesamaan Dense R4/R3 PASS. RRF diverifikasi independen dari full component ranks dengan kontribusi 1/(60+rank), absent BM25=0.

## 2. Eksekusi 18 query

| Query | Style | Topik | R1/R2/R3/R4 | Judged relevant dalam pool |
|---|---|---|---|---|
| WO-DEV-001 | lexical_oriented | A. Struktur Tim dan Job Description | PASS | True |
| WO-DEV-002 | lexical_oriented | B. Persiapan Sebelum Acara | PASS | True |
| WO-DEV-003 | lexical_oriented | C. Wedding Day Operation | PASS | True |
| WO-DEV-004 | lexical_oriented | D. Vendor Management | PASS | True |
| WO-DEV-005 | lexical_oriented | E. Contingency / Problem Handling | PASS | True |
| WO-DEV-006 | lexical_oriented | J. Post-event / Evaluation | PASS | True |
| WO-DEV-007 | semantic_paraphrase | A. Struktur Tim dan Job Description | PASS | True |
| WO-DEV-008 | semantic_paraphrase | B. Persiapan Sebelum Acara | PASS | True |
| WO-DEV-009 | semantic_paraphrase | E. Contingency / Problem Handling | PASS | True |
| WO-DEV-010 | semantic_paraphrase | F. Venue Operation | PASS | True |
| WO-DEV-011 | semantic_paraphrase | G. Guest dan Family Handling | PASS | True |
| WO-DEV-012 | semantic_paraphrase | J. Post-event / Evaluation | PASS | True |
| WO-DEV-013 | mixed_natural | C. Wedding Day Operation | PASS | True |
| WO-DEV-014 | mixed_natural | D. Vendor Management | PASS | True |
| WO-DEV-015 | mixed_natural | E. Contingency / Problem Handling | PASS | True |
| WO-DEV-016 | mixed_natural | G. Guest dan Family Handling | PASS | True |
| WO-DEV-017 | mixed_natural | H. Rundown dan Timeline | PASS | True |
| WO-DEV-018 | mixed_natural | I. Internal Communication / Escalation | PASS | True |

72 per-query/method rankings, 720 top-10 rows dan 360 per-query top-k coverage rows disimpan. Tabel top-10 lengkap keempat metode untuk seluruh 18 query tersedia di [top10.md](../results/milestone_9a12_development_pilot/top10.md); scores unrounded disimpan dalam JSONL/CSV. Label lexical/paraphrase/mixed adalah gaya query, bukan bukti keunggulan retriever.

## 3. Definisi dan hasil coverage

684/6.678 pasangan sudah dinilai (10,24%): grade 0=621, grade 1=32, grade 2=31; 5.994 belum dinilai (89,76%). Relevant threshold grade >=1 hanya berlaku pada pasangan judged. Seluruh 18 query memiliki judged relevant dalam pool, tetapi kelengkapan relevant set seluruh corpus tidak diketahui.

Coverage = judged/returned top-k; UNJUDGED% = unjudged/returned top-k. Grade 0 termasuk judged. Missing result slots dilaporkan terpisah, tidak menjadi grade 0 atau UNJUDGED. Empty window memiliki coverage undefined (CSV kosong), bukan 0; macro mengecualikan empty window dan jumlahnya dilaporkan. `judged_pct_requested` pada tabel per-query memakai requested k dan dapat berbeda pada short rankings. Semua windows pilot ini memenuhi requested k, sehingga denominators overall 18×k dan macro coverage sama dengan micro.

| Metode | k | Grade 0 | Grade 1 | Grade 2 | Judged / returned | UNJUDGED | UNJUDGED % |
|---|---:|---:|---:|---:|---:|---:|---:|
| R1 | 1 | 0 | 1 | 5 | 6/18 | 12 | 66.67 |
| R1 | 3 | 1 | 4 | 11 | 16/54 | 38 | 70.37 |
| R1 | 5 | 2 | 5 | 13 | 20/90 | 70 | 77.78 |
| R1 | 10 | 12 | 8 | 19 | 39/180 | 141 | 78.33 |
| R1 | 20 | 26 | 10 | 22 | 58/360 | 302 | 83.89 |
| R2 | 1 | 0 | 0 | 6 | 6/18 | 12 | 66.67 |
| R2 | 3 | 2 | 2 | 11 | 15/54 | 39 | 72.22 |
| R2 | 5 | 3 | 5 | 13 | 21/90 | 69 | 76.67 |
| R2 | 10 | 8 | 5 | 18 | 31/180 | 149 | 82.78 |
| R2 | 20 | 25 | 9 | 24 | 58/360 | 302 | 83.89 |
| R3 | 1 | 0 | 1 | 8 | 9/18 | 9 | 50.00 |
| R3 | 3 | 2 | 3 | 14 | 19/54 | 35 | 64.81 |
| R3 | 5 | 4 | 5 | 21 | 30/90 | 60 | 66.67 |
| R3 | 10 | 10 | 8 | 26 | 44/180 | 136 | 75.56 |
| R3 | 20 | 22 | 11 | 27 | 60/360 | 300 | 83.33 |
| R4 | 1 | 0 | 1 | 9 | 10/18 | 8 | 44.44 |
| R4 | 3 | 1 | 4 | 16 | 21/54 | 33 | 61.11 |
| R4 | 5 | 3 | 7 | 20 | 30/90 | 60 | 66.67 |
| R4 | 10 | 8 | 8 | 25 | 41/180 | 139 | 77.22 |
| R4 | 20 | 19 | 11 | 29 | 59/360 | 301 | 83.61 |

### Coverage top-10 menurut style

| Style | Metode | Judged / 60 | UNJUDGED / 60 | Judged % |
|---|---|---:|---:|---:|
| lexical_oriented | R1 | 14 | 46 | 23.33 |
| lexical_oriented | R2 | 12 | 48 | 20.00 |
| lexical_oriented | R3 | 14 | 46 | 23.33 |
| lexical_oriented | R4 | 14 | 46 | 23.33 |
| mixed_natural | R1 | 15 | 45 | 25.00 |
| mixed_natural | R2 | 10 | 50 | 16.67 |
| mixed_natural | R3 | 17 | 43 | 28.33 |
| mixed_natural | R4 | 16 | 44 | 26.67 |
| semantic_paraphrase | R1 | 10 | 50 | 16.67 |
| semantic_paraphrase | R2 | 9 | 51 | 15.00 |
| semantic_paraphrase | R3 | 13 | 47 | 21.67 |
| semantic_paraphrase | R4 | 11 | 49 | 18.33 |

### Coverage top-10 menurut topik

| Topik | Metode | Query count | Judged / returned | UNJUDGED % |
|---|---|---:|---:|---:|
| A. Struktur Tim dan Job Description | R1 | 2 | 3/20 | 85.00 |
| A. Struktur Tim dan Job Description | R2 | 2 | 4/20 | 80.00 |
| A. Struktur Tim dan Job Description | R3 | 2 | 3/20 | 85.00 |
| A. Struktur Tim dan Job Description | R4 | 2 | 4/20 | 80.00 |
| B. Persiapan Sebelum Acara | R1 | 2 | 5/20 | 75.00 |
| B. Persiapan Sebelum Acara | R2 | 2 | 2/20 | 90.00 |
| B. Persiapan Sebelum Acara | R3 | 2 | 4/20 | 80.00 |
| B. Persiapan Sebelum Acara | R4 | 2 | 3/20 | 85.00 |
| C. Wedding Day Operation | R1 | 2 | 7/20 | 65.00 |
| C. Wedding Day Operation | R2 | 2 | 6/20 | 70.00 |
| C. Wedding Day Operation | R3 | 2 | 7/20 | 65.00 |
| C. Wedding Day Operation | R4 | 2 | 6/20 | 70.00 |
| D. Vendor Management | R1 | 2 | 4/20 | 80.00 |
| D. Vendor Management | R2 | 2 | 2/20 | 90.00 |
| D. Vendor Management | R3 | 2 | 4/20 | 80.00 |
| D. Vendor Management | R4 | 2 | 4/20 | 80.00 |
| E. Contingency / Problem Handling | R1 | 3 | 4/30 | 86.67 |
| E. Contingency / Problem Handling | R2 | 3 | 4/30 | 86.67 |
| E. Contingency / Problem Handling | R3 | 3 | 8/30 | 73.33 |
| E. Contingency / Problem Handling | R4 | 3 | 8/30 | 73.33 |
| F. Venue Operation | R1 | 1 | 1/10 | 90.00 |
| F. Venue Operation | R2 | 1 | 1/10 | 90.00 |
| F. Venue Operation | R3 | 1 | 3/10 | 70.00 |
| F. Venue Operation | R4 | 1 | 2/10 | 80.00 |
| G. Guest dan Family Handling | R1 | 2 | 5/20 | 75.00 |
| G. Guest dan Family Handling | R2 | 2 | 4/20 | 80.00 |
| G. Guest dan Family Handling | R3 | 2 | 5/20 | 75.00 |
| G. Guest dan Family Handling | R4 | 2 | 6/20 | 70.00 |
| H. Rundown dan Timeline | R1 | 1 | 4/10 | 60.00 |
| H. Rundown dan Timeline | R2 | 1 | 3/10 | 70.00 |
| H. Rundown dan Timeline | R3 | 1 | 4/10 | 60.00 |
| H. Rundown dan Timeline | R4 | 1 | 2/10 | 80.00 |
| I. Internal Communication / Escalation | R1 | 1 | 1/10 | 90.00 |
| I. Internal Communication / Escalation | R2 | 1 | 1/10 | 90.00 |
| I. Internal Communication / Escalation | R3 | 1 | 1/10 | 90.00 |
| I. Internal Communication / Escalation | R4 | 1 | 2/10 | 80.00 |
| J. Post-event / Evaluation | R1 | 2 | 5/20 | 75.00 |
| J. Post-event / Evaluation | R2 | 2 | 4/20 | 80.00 |
| J. Post-event / Evaluation | R3 | 2 | 5/20 | 75.00 |
| J. Post-event / Evaluation | R4 | 2 | 4/20 | 80.00 |

Per-query counts dan semua style/topik untuk k=1/3/5/10/20 tersedia di coverage.csv dan coverage_summary.csv. `complete_returned_window` hanya menunjukkan judgments tersedia dalam returned window, bukan relevant-set completeness atau human validity.

Pool asal bersifat purposive content pool dari pembacaan sumber, bukan retrieval ranks, random sample atau exhaustive judgment. V2 mempertahankan pool tersebut dengan migration/rejudgment. Coverage top-10 R1 21,67%, R2 17,22%, R3 24,44%, R4 22,78% menunjukkan differential exposure terhadap pool kecil. Ini risiko bias interpretasi incomplete judgments, bukan bukti pool dibuat menguntungkan suatu metode atau bukti ranking effectiveness.

## 4. Qualitative diagnostics — bukan judgments baru

Berikut observations dari ranks nyata dan kutipan raw frozen chunk. Silver grade adalah label existing, tidak divalidasi ulang. Tidak menganggap chunk lain nonrelevant.

### WO-DEV-001 / WO-DOC-006-C002

Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim?

Lexical: matriks A/R muncul rank 1 pada keempat metode; header dan guide context spreadsheet terpelihara.

Ranks R1/R2/R3/R4: {'R1': 1, 'R2': 1, 'R3': 1, 'R4': 1}. Existing silver grade: 2.

Kutipan raw chunk (excerpt):

> Sheet: Operasional
> Section: Matriks Pembagian Tanggung Jawab Tim Wedding Day
> Header: Tugas | A | R | C | I | Keluaran dan batas kewenangan
> 
> Bagian: Konteks 2
> Keterangan: A adalah pengesah operasional untuk satu tugas; R pelaksana utama, C dimintai masukan, I penerima informasi.
> 
> Row: 12
> Tugas: Menilai fasilitas listrik
> A: EC
> R: PIC venue
> C: petugas kompeten; PIC vendor
> I: floor
> Keluaran dan batas kewenangan: Petugas berwenang menilai teknis; WO hanya mengoordinasikan
> 
> Row: 13
> Tugas: Menyiapkan ruang pengantin
> A: WC
> R: PIC pengantin
> C: PIC venue

### WO-DEV-007 / WO-DOC-001-C006

Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru?

Paraphrase: atasan memberi arahan bertentangan dan heading perintah bertentangan muncul rank 1 semua metode; tidak semua paraphrase harus bergantung pada Dense.

Ranks R1/R2/R3/R4: {'R1': 1, 'R2': 1, 'R3': 1, 'R4': 1}. Existing silver grade: 2.

Kutipan raw chunk (excerpt):

> Ketika perintah bertentangan
> 
> Kru menyebut dua instruksi yang berbeda dan menahan bagian yang belum aman atau belum jelas. PIC menyatukan informasi kepada EC; WC mengonfirmasi apakah ada permintaan baru dari client. EC menerbitkan satu instruksi pengganti dengan waktu berlaku dan menarik versi lama. Perselisihan tidak diselesaikan melalui adu pesan di depan tamu. Sesudah acara, perbedaan informasi dicatat untuk debrief, termasuk siapa menerima versi mana dan akibat operasionalnya. Struktur dianggap berfungsi jika setiap tugas kritis memiliki pe

### WO-DEV-013 / WO-DOC-014-C002

Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?

Mixed: checklist perpindahan dan jam standby dipromosikan R4 dari Dense rank 3 ke Hybrid rank 1, dengan BM25 rank 2.

Ranks R1/R2/R3/R4: {'R1': 3, 'R2': 2, 'R3': 3, 'R4': 1}. Existing silver grade: 1.

Kutipan raw chunk (excerpt):

> Memeriksa rencana sebelum layanan dimulai
> 
> PIC pengantin mencocokkan urutan makeup dan pakaian dengan jam standby pada rundown. Hitung perpindahan dari ruang persiapan menuju titik tunggu, waktu dokumentasi, dan waktu pasangan benar-benar perlu tenang sebelum prosesi. Jangan menjadwalkan foto panjang tepat pada saat pasangan harus bergerak. PIC vendor menyampaikan slot VEN-DOC-01; PIC keluarga memastikan orang yang diperlukan tersedia tanpa memenuhi ruang persiapan.
> 
> Periksa ruang telah diizinkan, pintu akses diketahui, barang kebutuhan tersedi

### WO-DEV-013 / WO-DOC-024-C006

Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?

Dense rank 1 bergeser ke Hybrid rank 10; isi touch-up/checkout memperlihatkan topik pengantin yang luas. Relevance terhadap kesiapan sebelum prosesi memerlukan human review.

Ranks R1/R2/R3/R4: {'R1': 36, 'R2': 37, 'R3': 1, 'R4': 10}. Existing silver grade: UNJUDGED.

Kutipan raw chunk (excerpt):

> Touch-up dan akhir layanan
> 
> Tentukan siapa standby untuk touch-up, lokasi, dan sampai tahap mana layanan tersedia. Jangan mengasumsikan vendor tetap di lokasi sepanjang resepsi bila tidak termasuk lingkup. PIC vendor memastikan client melalui WC mengetahui batas tersebut. Sebelum checkout, PIC pengantin memeriksa barang personal, perlengkapan vendor, dan permintaan yang masih terbuka. Catat perubahan waktu, layanan tambahan yang disetujui, serta hambatan untuk evaluasi berikutnya.

### WO-DEV-006 / WO-DOC-019-C004

Saat checkout, apa yang perlu dicocokkan pada daftar aset WO sebelum barang diserahterimakan?

Vocabulary mismatch candidate: query checkout/daftar aset berhubungan dengan heading mengembalikan barang dan aset; R3/R4 rank 1, R2 rank 3. Ini observasi padanan wording, bukan klaim kemampuan semantik umum.

Ranks R1/R2/R3/R4: {'R1': 2, 'R2': 3, 'R3': 1, 'R4': 1}. Existing silver grade: 2.

Kutipan raw chunk (excerpt):

> Mengembalikan barang dan aset
> 
> Setiap aset dicocokkan dengan daftar pinjam: kode, jumlah, kondisi awal yang diketahui, pemegang terakhir, dan penerima. Barang pribadi client dikembalikan melalui PIC pengantin atau WC kepada penerima yang disetujui. Barang vendor tidak dipindahkan ke kendaraan pemasok lain tanpa bukti serah terima. Bila jumlah tidak cocok, pisahkan masalah dari arus checkout dan tetapkan petugas pencarian. Jangan menandatangani semua barang lengkap jika belum dihitung.
> 
> Lost and found dicatat dengan ciri umum dan lokasi temuan. 

### WO-DEV-014 / WO-DOC-022-C004

Setelah foto di chapel, beberapa tamu akan naik shuttle ke lokasi dinner. Bagaimana LO memastikan tidak ada kelompok yang tertinggal?

Top-ranked UNJUDGED: foto kelompok/chapel menjadi rank 1 R1/R2/R4, sementara Dense memprioritaskan buffer keberangkatan. Pertanyaan memuat dua tahap operasional, sehingga thematic overlap belum memastikan kebutuhan shuttle terjawab.

Ranks R1/R2/R3/R4: {'R1': 1, 'R2': 1, 'R3': 3, 'R4': 1}. Existing silver grade: UNJUDGED.

Kutipan raw chunk (excerpt):

> Foto kelompok yang terkendali
> 
> PIC keluarga memanggil kelompok sesuai kode dan urutan prioritas. Dokumentasi mengarahkan posisi foto setelah floor memastikan titik dapat dipakai. Kelompok berikutnya menunggu di area yang diizinkan, bukan memenuhi pintu chapel. Permintaan foto tambahan diterima PIC keluarga dan dibawa WC jika memengaruhi waktu transisi. Jangan memotong ritual atau meminta pengulangan tanpa konfirmasi pemimpin prosesi dan client.
> 
> Untuk tamu internasional, LO membantu instruksi singkat mengenai posisi dan tujuan berikutnya. Instr

### WO-DEV-014 / WO-DOC-041-C010

Setelah foto di chapel, beberapa tamu akan naik shuttle ke lokasi dinner. Bagaimana LO memastikan tidak ada kelompok yang tertinggal?

Corpus ambiguity candidate: FAQ transport dinner berisi pencatatan jumlah naik/tiba, sedangkan rundown buffer keberangkatan berisi kendaraan dan penerima. Informasi tersebar pada beberapa bentuk dokumen; kebutuhan jawaban dan overlap wajib direview manusia.

Ranks R1/R2/R3/R4: {'R1': 2, 'R2': 9, 'R3': 13, 'R4': 7}. Existing silver grade: UNJUDGED.

Kutipan raw chunk (excerpt):

> Transport dinner EVT-03 belum datang
> 
> Hubungi LO STAFF-10 untuk posisi kendaraan dan perkiraan yang dikonfirmasi penyedia. Kelompok menunggu di titik yang diizinkan PIC venue. Jangan meminta driver melanggar pembatasan akses atau menjanjikan waktu tiba tanpa sumber. LO mencatat jumlah naik serta tiba dan menyerahkan kelompok kepada penerima dinner.

### Top-10 overlap

| Pair | Mean intersection /10 | Mean Jaccard |
|---|---:|---:|
| R1/R2 | 8.00 | 0.6755 |
| R1/R3 | 3.67 | 0.2431 |
| R1/R4 | 5.89 | 0.4320 |
| R2/R3 | 3.33 | 0.2185 |
| R2/R4 | 5.83 | 0.4271 |
| R3/R4 | 6.67 | 0.5179 |

Overlap dihitung atas sets IDs per-query; Jaccard intersection/union, kemudian macro mean 18 query. Overlap mengukur agreement, bukan relevance. File diagnostic_examples.jsonl menyimpan 77 contoh top candidates dan promotion/demotion dengan ranks, source locator, kutipan raw dan unchanged silver labels.

## 5. Effectiveness analysis

**NOT COMPUTED.** Top-10 UNJUDGED 75,56–82,78% dan top-20 83,33–83,89% membuat even judged-only/condensed estimates terlalu rentan terhadap pool availability untuk interpretasi yang dimaksud. Tidak menghitung Recall/MRR/nDCG, tidak mengubah UNJUDGED menjadi 0, dan tidak menyatakan metode terbaik, improvement final atau significance. Tidak melakukan tuning berdasarkan observations ini.

## 6. Timing dan reproducibility

Actual host: Intel Core i7-7700HQ @2.80GHz, 4 cores/8 threads; Windows 11 build 22631; Python 3.12.14. RAM total 15.89 GiB, available saat runner 6.05 GiB. Tidak mengukur peak RAM/VRAM karena ini CPU cached scoring; tidak ada GPU/model process.

Dependencies: numpy=2.5.3, scipy=1.18.1, scikit-learn=1.9.1, rank-bm25=0.2.2, psutil=7.2.2.

Per-query satu warm-up full eligible ranking, lalu tiga calls timed perf_counter per R1/R2/R3 dan RRF. Pengujian HybridRetriever existing di luar timing mengonfirmasi hasil fuse langsung identik. Query cache/index loading, encoding, artefak/report I/O dan independent math checks tidak masuk waktu component. R3 termasuk CachedEncoder validation yang dilaksanakan retrieve existing; ini bukan pure matrix-kernel microbenchmark. RRF menerima component ranks yang sudah dihitung. Tidak mengklaim reconstruction timing sebagai live end-to-end atau membandingkan Colab encoding dengan lexical lokal.

| Component | Samples | Min ms | Median ms | Max ms |
|---|---:|---:|---:|---:|
| R1 | 54 | 1.3078 | 1.6048 | 2.8118 |
| R2 | 54 | 1.3122 | 1.9544 | 3.3596 |
| R3 | 54 | 0.6778 | 0.8153 | 1.6752 |
| RRF | 54 | 1.2111 | 1.4009 | 2.1162 |

216 samples disimpan di timing.csv. Timing hanya technical observations, dipengaruhi scheduling/CPU caches/filesystem; tidak diurutkan sebagai fastest method claim. Run manifest merekam timestamps, effective configuration, environment, driver hash dan input/output checksums. Ranking floats JSONL unrounded. Query encoding telah terjadi di Colab sebelumnya, tidak dihitung atau dipalsukan sebagai inference lokal.

## 7. Tests dan integritas

PASS: 116 retrieval/offline tests pada `.venv-ml` + 29 ingestion/versioned pipeline tests pada `.venv`, total 145 distinct tests. Termasuk 8 targeted pilot tests (coverage grade 0 vs UNJUDGED, empty/short windows, micro vs macro, invalid/non-finite/duplicate/incomplete ranking, independent RRF math, published output checksums, same-query parity, V2 binding dan baseline integrity). Existing protocol consistency/version isolation/cache validation regression tests PASS. Seluruh TOML experiments parse PASS. Torch tidak diimpor oleh retrieval/offline suite.

Initial combined discovery dalam `.venv-ml` menjalankan 113 tests dan menghasilkan dua import errors untuk ingestion modules karena python-docx tidak dipasang di ML environment. Tidak menginstal package; ingestion tests dijalankan pada environment existing yang tepat dan PASS. Final tests/logs dipersist dalam run_manifest.json. CLI rejection messages serta mocked STOPPED evidence pada logs adalah expected negative-path fixture tests, bukan live model/GPU execution.

703 existing files dibandingkan bytewise SHA-256 dengan baseline sebelum pekerjaan: PASS. Termasuk source V1/V2, canonical/chunks, snapshots/fingerprints, protocol/pilot configs, 18 queries, AI qrels, existing R1/R2/R3 V1/V2 indices, model/cache-related evidence serta source code lama. protected_integrity.json menyimpan seluruh before hashes; targeted published-artifact tests juga menghitung ulang after hashes. No overwrite existing protected files.

## 8. Files created

- `scripts/run_development_pilot.py`: additive driver yang memakai loaders/scorers existing, tidak mengubah retrieval implementations.
- `tests/test_development_pilot.py`: coverage/invalid ranking/RRF synthetic tests dan published-artifact integration checks.
- `experiments/reports/milestone_9a12_offline_retrieval_development_pilot.md`: laporan ini.
- `experiments/results/milestone_9a12_development_pilot/`: run_manifest.json, rankings.jsonl, coverage.csv, coverage_summary.csv, top10.csv, top10.md, timing.csv, overlap.csv, diagnostic_examples.jsonl, protected_integrity.json.

Tidak ada file existing diubah. Runner menolak target output yang telah terisi. Diagnostic run menggunakan `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`, Python `-B`, UTF-8, TMP/TEMP di D:, `.venv-ml`. Baseline audit tersimpan read-only untuk runner di `D:/ModelCache/tmp/wo-m9a12/baseline.json`; before hashes juga dipersist pada protected_integrity.json. Untuk mereproduksi scoring, gunakan loader/scorer yang sama dan fresh output terpisah setelah approval; jangan overwrite hasil run ini.

## 9. Risks dan recommended next milestone

Silver qrels cukup untuk menemukan blind spots coverage dan merancang manual development diagnostics, belum cukup untuk klaim effectiveness atau final dataset validation. Corpus sintetis/AI-corrected dan query AI-assisted belum menjadi independent expert-validated; corpus/qrels/query status tidak dinaikkan. Researcher single-assessor bias dan selection bias tetap harus didokumentasikan; perubahan metodologi utama memerlukan persetujuan pembimbing.

Usulan milestone berikutnya: development judgment pooling preparation, dengan approval terpisah. Gabungkan union top-20 keempat retriever per-query, deduplicate pair, balance seluruh 18 queries dan tiga styles; audit strata di luar pool (topik/document/format) plus sample acak dengan seed dan inclusion rules ditetapkan sebelum assessment. Union top-20 pada output nyata ini berjumlah 654 pasangan unik (90 existing AI silver; 564 UNJUDGED). Jika targetnya human-reviewed pool, semua 654 pasangan tetap memerlukan keputusan manusia, bukan hanya 564 pasangan kosong. Angka ini menghitung jumlah pasangan, bukan estimasi jam kerja. Pool top-20 tidak menjamin exhaustive relevance; tetap laporkan unjudged dan recall denominator limitations.

Pertahankan 684 silver labels existing. Tambahkan judgments baru melalui ledger terpisah/versioned, provenance AI vs researcher/human vs domain expert eksplisit. Existing AI labels jangan otomatis diangkat sebagai keputusan manusia. Penilai melihat query dan chunk/context yang dibutuhkan, tetapi method/rank/score disembunyikan untuk mengurangi bias; catat grade 0/1/2, alasan, waktu aktual, assessor identity nyata dan adjudication/reconciliation history bila tersedia. Penilaian manusia yang berbeda disimpan sebagai penilaian terpisah, bukan overwrite label AI. Pilot dahulu workload aktual sebelum menyetujui pool lebih besar.

Protocol pooling, treatment incomplete qrels dan primary metrics dibekukan setelah persetujuan pembimbing; final/main queries tetap terpisah dan tidak dibuat sekarang. Jangan tuning final test berdasarkan development coverage. Jika corpus berubah, snapshot/index/query evidence/qrels harus dimigrasi dengan versioning baru. Tidak menjalankan rekomendasi tersebut pada task ini.

**STOP: development pilot selesai; NOT FINAL EVALUATION.**
