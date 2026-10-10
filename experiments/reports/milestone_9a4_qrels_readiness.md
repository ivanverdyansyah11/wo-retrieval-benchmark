# Milestone 9A.4 — Silver qrels readiness audit

Tanggal: 2026-10-09. **AI-GENERATED PROVISIONAL / SILVER STANDARD — NOT HUMAN VALIDATED.** Bukan expert validation, human ground truth, atau gold standard. Semua grade yang dibahas adalah label existing; tidak ada penilaian baru, perubahan grade, atau persetujuan peneliti otomatis. Penggunaan metodologi AI silver/researcher-based evaluation masih perlu persetujuan pembimbing.

## Kesimpulan dan metode audit

**PASS struktural/provenance; PARTIAL untuk cakupan dan kepastian semantik; belum siap sebagai complete ground truth.** Hash, ID, locator dan kutipan cocok, tetapi bukti administratif tidak membuktikan ketepatan semantic assessment seluruh 684 pasangan. Audit ini tidak menjalankan retrieval atau evaluasi efektivitas. Cakupan hanya 18 development queries, bukan main/test benchmark.

Input: JSONL dan manifest silver qrels, 18 draft queries beserta provenance, 371 frozen chunks, canonical blocks, sumber terkait, workbook dan laporan 9A.3. Helper serializer 9A.3 dalam temporary directory dibaca statis, tidak dieksekusi atau diimpor. Hitungan, matriks keputusan, hash, dan referensi dihitung silang dengan audit ringan tanpa model/inference.

## Coverage independen

Universe 18×371=**6678** pasangan. Judged **684**=38 chunk×18 query (**10,2426%**); missing **5994**=333×18 (**89,7574%**). Grade 0/1/2=**621/32/31**; positives 63, bukan 63 unique chunks. Tidak ada duplikasi pasangan. Seluruh ID, hash exact query/chunk, source file, locator/block, snapshot, batch dan matriks cocok. Tabel dihitung ulang dari JSONL.

| Query | Judged | Unjudged | Grade0 | Grade1 | Grade2 | Positives | Kategori positives |
|---|---:|---:|---:|---:|---:|---:|---|
| WO-DEV-001 | 38 | 333 | 36 | 1 | 1 | 2 | A |
| WO-DEV-002 | 38 | 333 | 36 | 1 | 1 | 2 | B |
| WO-DEV-003 | 38 | 333 | 31 | 5 | 2 | 7 | A, C, D, E |
| WO-DEV-004 | 38 | 333 | 35 | 1 | 2 | 3 | C, D |
| WO-DEV-005 | 38 | 333 | 36 | 0 | 2 | 2 | E |
| WO-DEV-006 | 38 | 333 | 35 | 1 | 2 | 3 | B, C, J |
| WO-DEV-007 | 38 | 333 | 35 | 2 | 1 | 3 | A, E, G |
| WO-DEV-008 | 38 | 333 | 34 | 3 | 1 | 4 | A, B, I |
| WO-DEV-009 | 38 | 333 | 31 | 4 | 3 | 7 | A, B, E |
| WO-DEV-010 | 38 | 333 | 36 | 1 | 1 | 2 | E, F |
| WO-DEV-011 | 38 | 333 | 34 | 2 | 2 | 4 | A, B, C, G |
| WO-DEV-012 | 38 | 333 | 35 | 1 | 2 | 3 | G, J |
| WO-DEV-013 | 38 | 333 | 33 | 3 | 2 | 5 | A, C, D |
| WO-DEV-014 | 38 | 333 | 35 | 2 | 1 | 3 | A, H |
| WO-DEV-015 | 38 | 333 | 34 | 2 | 2 | 4 | C, E, G |
| WO-DEV-016 | 38 | 333 | 37 | 0 | 1 | 1 | G |
| WO-DEV-017 | 38 | 333 | 34 | 2 | 2 | 4 | A, B, E |
| WO-DEV-018 | 38 | 333 | 34 | 1 | 3 | 4 | A, C, I |

Seluruh query memiliki coverage 10,24%; kesamaan persentase tidak membuat pool representatif. Query003/009 mempunyai positives terbanyak (7), query 016 hanya 1. Angka ini bukan prevalensi seluruh corpus. Manifest menunjuk WO-DOC-005 page2, 021 page1, 026 Operasional row13 sebagai follow-up016; itu petunjuk untuk membaca isi, belum relevance label pada chunk.

**Missing pair berarti unjudged, bukan grade0.** Grade0 berarti pasangan diperiksa dan tidak menyediakan support substantif untuk information need. Jangan mengekspor missing sebagai nol atau menganggap 621 nol mencakup seluruh nonrelevant corpus.

## Kandidat, keragaman dan bias

| Kategori source | Dokumen dalam pool/total | Chunk dalam pool/total | Judged pairs |
|---|---:|---:|---:|
| A. Struktur Tim dan Job Description | 2/6 | 5/34 | 90 |
| B. Persiapan Sebelum Acara | 2/6 | 4/41 | 72 |
| C. Wedding Day Operation | 4/7 | 6/52 | 108 |
| D. Vendor Management | 1/7 | 2/43 | 36 |
| E. Contingency / Problem Handling | 4/8 | 9/63 | 162 |
| F. Venue Operation | 1/4 | 1/27 | 18 |
| G. Guest dan Family Handling | 1/3 | 4/26 | 72 |
| H. Rundown dan Timeline | 1/3 | 2/40 | 36 |
| I. Internal Communication / Escalation | 1/3 | 2/21 | 36 |
| J. Post-event / Evaluation | 2/3 | 3/24 | 54 |

Pool mencakup **19/50 dokumen**, 38/371 chunk. Format: DOCX22, TXT6, PDF5, XLSX5 chunk. Evidence XLSX mempertahankan header, baris dan context yang memang tersimpan pada chunk. Semua 10 kategori hadir, tetapi F hanya 1/27 chunk dan H 2/40; kehadiran kategori bukan coverage semantik lengkap.

Batch existing: B01=12 chunk/216 pasangan; B02=12/216; B03=10/180; B04_SECOND_PASS_EXPANSION=4/72. B04 menambah 016-C004, 032-C002/C003, 048-C003. Semua memiliki matriks 18 grade eksplisit. Manifest menyebut **purposive content pool** dari pembacaan sumber dan kebutuhan query, bukan random sample, exhaustive assessment, atau top-k retriever. Memasangkan seluruh 18 query dengan setiap chunk terpilih menghasilkan banyak nol, tetapi tidak menghapus bias pemilihan chunk.

Risiko: fokus pada bagian yang tampak menjawab query; anchoring pada dokumen/provenance pembentukan query; keterwakilan tidak merata; dan relevansi yang terlewat pada 333 chunk tersisa. Penyusunan corpus, query, review dan judgment oleh AI menambah bias bersama. Label style lexical/semantic/mixed tidak membuktikan difficulty setara atau metode tertentu unggul.

**Retrieval-method leakage:** manifest menyatakan tidak memakai rank/score. Serializer yang diperiksa hanya mematerialisasi keputusan eksplisit, tanpa pemanggilan retrieval atau aturan keyword untuk inferensi grade. Pada qrels tidak ditemukan field score/rank/method yang diperiksa atau bukti corpus vector dipakai sebagai query vector. Jadi tidak ditemukan leakage langsung dari output R1–R4 pada jejak tersedia. Ketiadaan field bukan bukti bahwa seluruh pengaruh historis mustahil; query yang dibangun dari corpus tetap berisiko circularity. Jangan memasukkan qrels/evidence ke retrievable text atau memakai development silver labels untuk tuning final test.

## Traceability semantic assessment 684 pasangan

Manifest menyediakan 38 matriks berisi 18 grade, fokus isi chunk, urutan query, hash dan batch. JSONL menyimpan exact query/hash, chunk hash, locator, reason dan excerpt positif, serta provenance AI. Static inspection helper 9A.3 `qrels.py` menunjukkan grade dan reasons eksplisit, bukan grade yang dihitung dari kategori, judul, keyword atau similarity. Matriks cocok dengan label tersimpan. Jejak ini mendukung proses content-oriented AI assessment yang kemudian diserialisasi, bukan classifier keyword dalam script.

Namun matriks hardcoded dan `pair_examined=true` **tidak membuktikan secara independen** bahwa setiap pasangan dipertimbangkan dengan benar. Sebanyak 621 grade0 memakai pola reason berupa ringkasan fokus chunk ditambah specific information need; itu bukan argumentasi individual lengkap. Manifest memberi second-pass reason spesifik untuk 18 nol (satu per query); **603 nol lainnya tidak memiliki detail second pass serupa**. Field `same_ai_self_checked` tidak boleh diartikan semua nol telah dinilai oleh penilai kedua. Semua 31 grade2 dan 32 grade1 dicatat diperiksa ulang oleh AI yang sama; ini bukan inter-rater reliability.

Manifest mencatat dua perubahan 0→1: query 011/008-C005 dan query 003/024-C003, dengan alasan konsistensi partial support. Alasan perubahan dapat dilacak, tetapi checkpoint temporary bukan log immutable lengkap semua tahapan. Exact model/backend version assessment belum dapat diverifikasi; timestamp serialisasi seragam bukan bukti waktu penilaian setiap pasangan. **Semantic assessment seluruh 684 tidak dapat disertifikasi independen dari artefak yang ada.** Pembentukan kandidat/label dapat ditelusuri sebagian, sedangkan keandalan seluruh negatif tetap perlu pemeriksaan isi. Audit ini tidak membuat log yang hilang atau mengubah status lama.

## Grade consistency dan seluruh positive evidence

Rubric existing: **0** inspected/no substantive useful support; **1** useful partial support; **2** direct substantive support, tidak harus menjawab semua aspek. Alasan, excerpt dan konteks full chunk seluruh 63 positive pairs diperiksa. **63/63 exact excerpts ditemukan pada chunk**, dengan source locator/block valid. Tidak ada kutipan positif yang fabricated/missing. Exact match tidak dengan sendirinya membuktikan grade benar.

Temuan berikut adalah candidate calibration, bukan keputusan grade baru:

| Pasangan existing | Temuan | Tindak lanjut yang diusulkan |
|---|---|---|
| 009 /001-C003, grade1 | Excerpt hanya “pemindahan lokasi”; full chunk memuat EC/venue, tetapi dua kata tidak mendukung seluruh reason secara mandiri. | Gunakan exact quote lebih panjang saat perubahan evidence diizinkan; jangan menyamakan substring match dengan semantic sufficiency. |
| 003 /014-C004,024-C003,027-C007, grade1 | Readiness akad/ceremony/hujan dipakai sebagai partial support untuk C03 entrance resepsi; analogi dinyatakan pada reason. | Kalibrasi apakah prasyarat dapat diterapkan pada exact scenario. Kesamaan topik saja tidak cukup. |
| 006 /008-C005, grade1 | Pemeriksaan aset H-2 dibanding checkout akhir. | Bedakan atribut yang dapat digunakan ulang dari prosedur pada fase berbeda. |
| 008 /001-C005,047-C002, grade1 | Handover lapangan dibanding tracking persiapan minggu terakhir. | Perjelas batas useful partial support dan analogi terlalu umum. |
| 008 /008-C006, grade2 | Panduan checklist minggu terakhir memberi fakta, pemilik, waktu tindak lanjut, bukan seluruh workflow. | Pertahankan definisi grade2=direct substantive support saat kalibrasi; tidak harus complete answer. |
| 011 /006-C002,008-C005, grade1 | Control akses daftar tidak sama dengan aturan menjawab pertanyaan kehadiran. | Nilai manfaat parsial secara eksplisit; jangan dianggap setara disclosure policy pada041-C008/016-C004. |
| 007 /041-C013, grade1 | Penyatuan jawaban staf dibanding konflik instruksi atasan. | Evaluasi transferability, bukan kemiripan kata “berbeda”. |
| 001 /006-C005, grade1 | Definisi A/R tanpa penugasan registrasi. | Support konseptual terbatas, bukan jawaban langsung seperti006-C002. |
| 005 /031-C005,C009, grade2;018 /047-C002,C003, grade2 | Masing-masing memberi bagian langsung: respons/retest, atau paket/readback. | Konsisten dengan rubric existing meski bukan jawaban lengkap; dokumentasikan prinsip direct subpart sebelum ekspansi. |

Contoh support kuat yang dapat dilacak:003/017-C003,C004 (prasyarat/izinC03),014/043-C010 (jumlah naik/tiba),016/041-C007 (batas janji makanan/jalur provider). Ini tetap AI assessment, bukan human validation. Temuan excerpt singkat dan batas grading membuat klaim “seluruh 63 grade pasti benar” tidak defensible. Seluruh existing evidence ditampilkan pada lampiran tanpa perubahan label.

## Corpus reconciliation dan rekomendasi versi

Laporan pendamping `milestone_9a4_corpus_reconciliation.md` memuat kutipan sumber dan proposal minimal. Ringkasan: standby08.30 pada024 dan08.45 pada042 berbeda untuk EVT02; pembeda personal readiness/floor belum tertulis. Pada027 syarat “serta area sudah diserahkan” berpotensi mensyaratkan final handover sebelum closure, sedangkan018/050 konsisten closure21.10 dan handover22.30. Referen area pada027 masih unresolved. Jangan mengarang handover antara atau menyebut21.10 sebagai temporary recovery yang tidak tertulis.

Review terbaru47approve/3revise terverifikasi. Workbook lama30/20 tidak ditemukan pada repository/attachments/arsip yang diperiksa; rubric, threshold, scope atau AI instability hanya kemungkinan penyebab, bukan kesimpulan. Hasil baru tidak membatalkan findings lama otomatis. Ketiga AI_REVISE024/027/042 ditinjau;042 mungkin cukup menjadi referensi tanpa edit jika024 diselaraskan.

**OpsiA:** frozen pilot tetap layak untuk development teknis sementara dengan disclosure, belum corpus final. **OpsiB lebih disarankan sebelum ekspansi besar:** peneliti menyetujui makna koreksi, kemudian buat corpus version baru. Envelope tiga dokumen=23chunk/414 pasangan potensial, termasuk90 pasangan existing untuk audit mapping; bukan90 grade otomatis salah. Direct edit024-C003 memiliki18 judged, sedangkan027-C009 dan042-C002 belum judged. Versi baru membutuhkan re-extraction/re-chunking, snapshot/fingerprint baru, pemeriksaan query evidence/qrels mapping dan rebuild corpus indices; jangan overwrite pilot atau membawa grade/cache lintas versi berdasarkan ID saja.

## Completion plan yang diusulkan, belum dijalankan

1. **Gate keputusan:** peneliti memilih versi corpus dan meninjau rubric/batas evidence; pembimbing menyetujui penggunaan AI silver untuk metodologi utama. Tetapkan manifest input (snapshot/hash chunk,18 exact queries, rubric version dan context yang boleh digunakan). Jika corpus berubah, hitung ulang universe;5994 berlaku untuk frozen v1 saat ini.
2. Untuk v1, urutkan333 chunk unknown secara deterministik berdasarkan Document ID/chunk index. Usulan **3 chunk×18 query=54 pasangan per batch,111 batch**. Chunk panjang boleh1–2 per batch; jumlah batch menyesuaikan. Ini rencana, bukan assessment yang sudah terjadi. Tidak ada estimasi jam fiktif; durasi aktual dicatat saat pelaksanaan.
3. Baca full chunk beserta title/heading/context yang tersimpan, lalu setiap exact query dan information need. Sumber boleh membantu interpretasi, tetapi jawaban dari luar chunk tidak menjadi support chunk. Grade harus berasal dari isi; kategori/keyword bukan shortcut. Catat quote positif dan reason spesifik, termasuk manfaat parsial, batas fase dan informasi yang tidak disediakan. Jika belum dapat diputuskan, simpan assessed_uncertain terpisah tanpa resolved grade; jangan paksa nol.
4. Setelah persetujuan, simpan hasil per batch pada artefak baru tanpa menimpa qrels v1. Rekam IDs, input/output SHA, prompt/rubric version, model/backend jika tersedia, timestamps/durasi aktual, AI provenance dan append-only decision change log. Jangan mengarang metadata yang tidak diketahui. Batch complete memerlukan pemeriksaan isi dan referensi, bukan hanya jumlah baris.
5. Validasi: unique pairs, ID/hash/locator, type grade, exact evidence, full 18 coverage atau daftar sisa eksplisit, resume union tanpa duplikat, counts per query/kategori/format. Script hanya serialisasi/validasi. Status disjoint harus memenuhi judged+unjudged+assessed_uncertain=universe; positives dan nol hanya bagian resolved judged.
6. Periksa ulang seluruh positives dan boundary cases. Rancang negative second-pass sampling deterministik lintas query/kategori, ditambah hard negatives, dengan jumlah/seed/IDs disepakati sebelumnya. Bukti isi621 nol existing perlu diperkuat melampaui18 samples. Same-AI self-check bukan independent agreement; keputusan yang dipakai peneliti harus benar-benar ditinjau, tanpa klaim external expert.
7. Complete coverage berarti seluruh 6678 pasangan pada versi input yang sama telah resolved; itu tetap AI silver, bukan gold standard. Milestone ini **tidak menambah satu pun label**.

| Strategi | Beban dan manfaat | Risiko dan batas |
|---|---|---|
| Exhaustive bertahap | 5994 assessment tambahan pada frozen v1;333 chunk×18, dibagi batch kecil. Mengatasi missing-pair coverage bila selesai. | Tetap bias/error AI; revisi corpus dapat memerlukan penilaian ulang. Waktu aktual belum diukur. |
| Pooling transparan | Lebih sedikit assessment dengan daftar kandidat, aturan inclusion dan coverage yang jelas. | Kandidat terlewat tetap unknown. Bias bergantung pool/metode; denominator Recall dan IDCG nDCG tidak lengkap. Retriever yang menemukan unjudged relevant dapat dirugikan. |

Untuk371 chunk/18 query, exhaustive bertahap lebih disarankan setelah keputusan versi. Jika pooling dipilih kemudian, perlu policy approval: union komponen dengan kontribusi setara, depth ditetapkan sebelum evaluasi, penilai tidak melihat method/rank, serta audit random/stratified di luar pool dengan seed tercatat. Pool purposive38chunk saat ini bukan fair retriever pool. Tidak membuat pool retrieval sekarang. Tidak menjalankan Recall/MRR/nDCG atau mengubah unknown menjadi nol.

## Status akhir dan rekomendasi milestone berikutnya

- **PASS:** struktur/hash/reference, coverage counts, trace matriks/batch, exact63 positive quotes, snapshot/source/index bytes unchanged.
- **PARTIAL / UNRESOLVED:** coverage 10,24%; representativitas pool; batas grade/quote singkat; bukti semantik individual seluruh 684; konteks konflik source; perbandingan workbook AI lama.
- **PENDING peneliti/pembimbing:** makna koreksi, versi corpus, kalibrasi rubric dan izin melanjutkan AI judgment serta penggunaannya untuk evaluasi utama. Tidak ada human/expert validation yang otomatis selesai.
- **NOT RUN:** judgment baru/relabeling, retrieval/metrics/tuning, model/GPU/embedding. Status Milestone8C `end_to_end_pending` tidak berubah oleh audit ini.

Next milestone yang direkomendasikan: keputusan corpus version dan kalibrasi evidence/grade berdasarkan findings ini. Tunggu review pengguna sebelum revisi source atau ekspansi qrels. STOP setelah dua laporan; tidak membuat main queries, final ground truth atau benchmark scores.

## Lampiran — seluruh 63 positive evidence existing

Tabel menyalin grade, exact excerpt dan reason existing untuk audit, bukan judgment baru. Full source path dan objek locator lengkap tersedia di JSONL. Kutipan cocok dengan chunk; catatan kalibrasi di atas tetap berlaku walaupun reason existing terdengar tegas.

| Query | Chunk | Grade existing | Locator | Exact excerpt | Reason existing |
|---|---|---:|---|---|---|
| WO-DEV-001 | WO-DOC-006-C002 | 2 | Operasional rows13–19 | Tugas: Mengelola daftar registrasi<br>A: EC<br>R: guest desk | Menetapkan tepat pengesah EC dan pelaksana guest desk, disertai definisi A/R yang dibawa dalam chunk. |
| WO-DEV-001 | WO-DOC-006-C005 | 1 | Panduan rows9–15 | A adalah pengesah operasional untuk satu tugas; R pelaksana utama | Menjelaskan makna A dan R, tetapi tidak menunjuk pemegang A/R tugas daftar registrasi. |
| WO-DEV-002 | WO-DOC-009-C004 | 2 | body 14,15 | Jika dekor meminta akses lebih awal daripada izin venue, PIC vendor mencatat selisih | Langsung mengatur pencatatan selisih, opsi pengelola, keputusan EC, persetujuan client, dan larangan di luar izin. |
| WO-DEV-002 | WO-DOC-009-C006 | 1 | body 19 | Pada H-1, PIC vendor mengonfirmasi perubahan terakhir | Mendukung pemeriksaan versi/perubahan konfirmasi akhir, tetapi tidak menyelesaikan selisih izin loading. |
| WO-DEV-003 | WO-DOC-001-C003 | 1 | body 11,12 | STAFF-07 boleh menahan entrance sampai jalur bersih | Menjelaskan batas floor menahan entrance dan kebutuhan izin EC; belum merinci seluruh prasyarat C03. |
| WO-DEV-003 | WO-DOC-006-C002 | 1 | Operasional rows13–19 | Standby diakui sebelum jalan; floor tidak memutuskan urutan sendiri | Memberi prasyarat acknowledgment dan kewenangan entrance; belum rincian orang/perangkat C03. |
| WO-DEV-003 | WO-DOC-014-C004 | 1 | body 14,15 | Floor menggabungkan status dengan kesiapan area dan pemimpin prosesi. EC memberi izin cue utama. | Kriteria lintas fungsi sebelum cue membantu entrance; konteks akad, belum cue C03 resepsi spesifik. |
| WO-DEV-003 | WO-DOC-017-C003 | 2 | {"block_id":"p001-b011","heading":"C02 standby entrance pukul 17.20","page_block":11,"page_end":1,"page_start":1,"serialized_char_end":428,"serialized_char_start":0} | WC mengonfirmasi pasangan siap, PIC keluarga menempatkan keluarga inti, dokumentasi mengambil posisi, dan AV mengonfirmasi track benar. | Langsung merinci orang/perangkat dan acknowledgment sebelum entrance, serta MC menunggu instruksi jalan. |
| WO-DEV-003 | WO-DOC-017-C004 | 2 | {"block_id":"p001-b013","heading":"C03 entrance pukul 17.30","page_block":13,"page_end":1,"page_start":1,"serialized_char_end":444,"serialized_char_start":0} | Sesudah EC mengesahkan, floor memberikan jalan kepada MC dan AV dengan nomor cue yang sama. | Langsung mengatur otorisasi C03, instruksi pendamping, perlindungan jalur banquet dan tahan jika musik gagal. |
| WO-DEV-003 | WO-DOC-024-C003 | 1 | body 11,12 | floor menunggu kesiapan area serta pemimpin prosesi. | Prasyarat umum kesiapan pasangan/area/pihak prosesi mendukung sebagian kebutuhan cue, setara 014-C004; bukan seluruh C03 resepsi. |
| WO-DEV-003 | WO-DOC-027-C007 | 1 | body 22 | EC menerima laporan gabungan sebelum memberi izin registrasi atau cue ceremony. | Menjelaskan readiness gabungan sebelum cue dalam konteks pindah ceremony, belum C03 resepsi. |
| WO-DEV-004 | WO-DOC-014-C002 | 2 | body 8,9 | PIC pengantin mencocokkan urutan makeup dan pakaian dengan jam standby pada rundown. | Langsung mengaitkan layanan dengan standby, slot foto dan durasi perpindahan agar tidak berbenturan. |
| WO-DEV-004 | WO-DOC-024-C002 | 2 | body 8,9 | urutan penerima layanan berkode, perkiraan durasi masing-masing, jumlah personel, kebutuhan ruang, jam akses | Langsung memberi data konfirmasi penyedia untuk menyusun jadwal tanpa tambahan keluarga menggeser pasangan. |
| WO-DEV-004 | WO-DOC-024-C003 | 1 | body 11,12 | PIC pengantin meminta perkiraan selesai pada titik kerja yang disetujui | Memberi estimasi dan penyelarasan makeup/dressing/foto dengan standby; bukan daftar konfirmasi lingkup. Jam standby lintas dokumen perlu klarifikasi X01. |
| WO-DEV-005 | WO-DOC-031-C005 | 2 | {"block_id":"p002-b003","heading":"Mikrofon gagal saat sambutan","page_block":3,"page_end":2,"page_start":2,"serialized_char_end":437,"serialized_char_start":0} | Bila mikrofon cadangan siap, teknisi mengatur pergantian lalu floor mengonfirmasi pembicara dapat melanjutkan. | Langsung memberi rantai penanganan gangguan saat sambutan dan pemeriksaan kesiapan alternatif sebelum lanjut; uji formal di C009. |
| WO-DEV-005 | WO-DOC-031-C009 | 2 | {"block_id":"p002-b011","heading":"Pemulihan dan penutupan insiden","page_block":11,"page_end":2,"page_start":2,"serialized_char_end":520,"serialized_char_start":0} | Setelah teknisi menyatakan perangkat siap, lakukan uji yang disetujui | Langsung menjawab pemeriksaan sebelum audio kembali dipakai, penerima standby, izin EC dan log hasil uji. |
| WO-DEV-006 | WO-DOC-008-C005 | 1 | Operasional rows30–35 | Kriteria pemeriksaan: Jumlah, kondisi, penerima tercatat | Pemeriksaan aset memberi sebagian atribut rekonsiliasi; dilakukan H-2, belum kode dan checkout akhir. |
| WO-DEV-006 | WO-DOC-019-C004 | 2 | body 13,14 | kode, jumlah, kondisi awal yang diketahui, pemegang terakhir, dan penerima. | Langsung menyebut atribut daftar aset sebelum serah terima dan larangan menandatangani lengkap sebelum hitung. |
| WO-DEV-006 | WO-DOC-048-C003 | 2 | Operasional rows18–23 | Kriteria selesai: Kode, jumlah, kondisi, penerima diketahui | Lintas dokumen: baris cocokkan aset WO memberi tepat atribut pemeriksaan dan penerima EC; radio dicocokkan pemegang. |
| WO-DEV-007 | WO-DOC-001-C006 | 2 | body 20 | Kru menyebut dua instruksi yang berbeda dan menahan bagian yang belum aman atau belum jelas. | Langsung menjawab tindakan kru, jalur PIC/EC, satu instruksi pengganti, dan penarikan versi lama. |
| WO-DEV-007 | WO-DOC-030-C004 | 1 | {"block_id":"l0017-0017","line_end":17,"line_start":17,"section":"Contoh EVT-02","serialized_char_end":410,"serialized_char_start":0} | MC menerima satu instruksi terakhir, bukan dua pesan dari keluarga dan vendor. | Contoh pengendalian arahan ganda melalui EC; belum langkah kru menyebut konflik dan menahan tugas. |
| WO-DEV-007 | WO-DOC-041-C013 | 1 | {"block_id":"l0044-0044","line_end":44,"line_start":44,"section":"Jawaban antarstaf berbeda","serialized_char_end":297,"serialized_char_start":0} | Hentikan penyebaran jawaban yang belum jelas, periksa versi dokumen | Mekanisme menyatukan informasi melalui PIC berguna secara analogi; konteks jawaban guest desk bukan dua atasan memberi tugas. |
| WO-DEV-008 | WO-DOC-001-C005 | 1 | body 17,18 | tugas belum tuntas, risiko, serta tindakan berikutnya | Menyediakan kesinambungan outstanding melalui penerima; belum format tenggat tracking minggu terakhir. |
| WO-DEV-008 | WO-DOC-008-C005 | 1 | Operasional rows30–35 | Kriteria pemeriksaan: Semua isu memiliki pemilik berikutnya | Menjaga outstanding H-1 dengan pemilik berikutnya dan larangan menutup karena tanggal; belum format fakta/tenggat lengkap. |
| WO-DEV-008 | WO-DOC-008-C006 | 2 | Panduan rows9–14 | temuan mencatat fakta, pemilik, dan waktu tindak lanjut. | Langsung memberi isi catatan pekerjaan terbuka dan membedakan belum diperiksa dari hasil selesai dalam checklist minggu terakhir. |
| WO-DEV-008 | WO-DOC-047-C002 | 1 | body 8 | Untuk setiap outstanding, sebut tindakan berikutnya, penanggung jawab, tenggat, dan kapan perlu eskalasi. | Format kesinambungan tugas terbuka dapat membantu persiapan, walau konteks dokumen handover lapangan bukan H-7. |
| WO-DEV-009 | WO-DOC-001-C003 | 1 | body 11,12 | pemindahan lokasi | Menetapkan EC sebagai pengambil keputusan lokasi dan venue sebagai penilai kelayakan; tidak merinci kesiapan alternatif. |
| WO-DEV-009 | WO-DOC-001-C005 | 1 | body 17,18 | PIC venue mengecek kelayakan, PIC vendor menghitung kesiapan pindah | Menyebut pemeriksaan venue/vendor dan dampak client untuk hujan, tetapi belum daftar fasilitas dan uji ulang. |
| WO-DEV-009 | WO-DOC-008-C005 | 1 | Operasional rows30–35 | Pengelola memberi pembatasan aktual | Pemeriksaan kondisi terbaru dan rencana alternatif relevan sebelum hujan ditangani; belum prosedur aktivasi lokasi. |
| WO-DEV-009 | WO-DOC-008-C006 | 1 | Panduan rows9–14 | pengelola serta petugas kompeten menilai fasilitas. | Menjelaskan kewenangan penilaian fasilitas dan keputusan EC; tanpa daftar kesiapan pemindahan. |
| WO-DEV-009 | WO-DOC-027-C002 | 2 | body 8,9 | Pilihan tertutup belum siap jika hanya ruangnya tersedia tetapi layanan dan akses belum ditelaah. | Langsung merinci kesiapan alternatif, waktu pindah/uji/registrasi/orang dan kewenangan pengelola sebelum aktivasi. |
| WO-DEV-009 | WO-DOC-027-C004 | 2 | body 13,14 | kelayakan lokasi dari pengelola, waktu kesiapan vendor, kesiapan orang melalui WC, dan dampak arus tamu dari floor. | Langsung memberi masukan yang harus dipastikan dan larangan mengirim tamu ke alternatif belum dilepas. |
| WO-DEV-009 | WO-DOC-027-C007 | 2 | body 22 | PIC vendor meminta teknisi menguji perangkat di posisi baru dan memeriksa kesiapan layanan pemasok. | Langsung memberi verifikasi lokasi baru, perangkat, seating, keluarga dan pasangan sebelum izin EC. |
| WO-DEV-010 | WO-DOC-027-C002 | 1 | body 8,9 | akses, kondisi permukaan, fasilitas, jalur tamu, storage | Memberi sebagian aspek survei akses dan konfirmasi pantai, belum rincian kendaraan dan urutan loading. |
| WO-DEV-010 | WO-DOC-037-C003 | 2 | {"block_id":"p001-b012","heading":"Akses orang dan barang","page_block":12,"page_end":1,"page_start":1,"serialized_char_end":432,"serialized_char_start":0}; {"block_id":"p001-b013","heading":"Akses orang dan barang","page_block":13,"page_end":1,"page_start":1,"serialized_char_end":392,"serialized_char_start":0} | Survei memeriksa perjalanan dari drop-off ke area acara, permukaan jalur, bagian yang sempit | Langsung mengatur akses orang dan barang, izin kendaraan, pemisahan sirkulasi, serta penerima storage. |
| WO-DEV-011 | WO-DOC-006-C002 | 1 | Operasional rows13–19 | Daftar berkode, versi sama dengan seating, akses data terbatas | Membatasi akses daftar registrasi; belum aturan menjawab pertanyaan kehadiran pihak luar. |
| WO-DEV-011 | WO-DOC-008-C005 | 1 | Operasional rows30–35 | Daftar berkode terbatas aksesnya | Membantu batas akses informasi daftar tamu, sebanding dengan RACI006; belum aturan jawaban kehadiran untuk penanya. |
| WO-DEV-011 | WO-DOC-016-C004 | 2 | body 14,15 | bukan dijawab kepada siapa pun yang bertanya. | Lintas dokumen: kebutuhan kehadiran yang sah melalui PIC keluarga; larangan daftar untuk vendor, sesuai FAQ041. |
| WO-DEV-011 | WO-DOC-041-C008 | 2 | {"block_id":"l0029-0029","line_end":29,"line_start":29,"section":"Apakah seseorang sudah hadir","serialized_char_end":275,"serialized_char_start":0} | Informasi kedatangan tidak diberikan kepada siapa pun yang bertanya. Arahkan kebutuhan yang sah kepada PIC keluarga. | Jawaban langsung terhadap pertanyaan pihak luar tentang kehadiran, bukan sekadar aturan akses file. |
| WO-DEV-012 | WO-DOC-041-C013 | 1 | {"block_id":"l0044-0044","line_end":44,"line_start":44,"section":"Jawaban antarstaf berbeda","serialized_char_end":297,"serialized_char_start":0} | Catat pertanyaan serta koreksi untuk debrief agar FAQ berikutnya diperbarui | Contoh tindakan perbaikan FAQ dari temuan; belum pemilik/tenggat/kriteria selesai dan monitoring lengkap. |
| WO-DEV-012 | WO-DOC-049-C006 | 2 | body 18 | pemilik, tenggat relatif, kriteria selesai, dan dokumen yang terdampak. | Langsung memberi format tindakan perbaikan yang dapat dipantau serta contoh bukti latihan arah. |
| WO-DEV-012 | WO-DOC-049-C007 | 2 | body 20 | Pada event berikutnya, periksa apakah tindakan benar-benar diterapkan dan apakah menimbulkan masalah baru. | Langsung menjelaskan monitoring sampai penerapan, pengakuan pemilik dan outstanding tetap terbuka. |
| WO-DEV-013 | WO-DOC-006-C002 | 1 | Operasional rows13–19 | Pemberi dan penerima barang dicatat; tidak dititipkan informal | Membantu memastikan benda prosesi pada penerima dan keluarga standby; belum keseluruhan kriteria pasangan siap. |
| WO-DEV-013 | WO-DOC-014-C002 | 1 | body 8,9 | Hitung perpindahan dari ruang persiapan menuju titik tunggu | Membantu mengecek rute/waktu perpindahan serta benda, tetapi bagian ini persiapan rencana, belum pernyataan readiness akhir. |
| WO-DEV-013 | WO-DOC-014-C004 | 2 | body 14,15 | Siap berarti pakaian selesai, benda prosesi berada pada penerima, pendamping tersedia, rute boleh dilewati | Langsung menjabarkan readiness melebihi makeup dan kewajiban handover/posisi standby sebelum pemanggilan. |
| WO-DEV-013 | WO-DOC-017-C003 | 1 | {"block_id":"p001-b011","heading":"C02 standby entrance pukul 17.20","page_block":11,"page_end":1,"page_start":1,"serialized_char_end":428,"serialized_char_start":0} | MC belum memanggil pasangan sampai instruksi jalan. | Menjelaskan siap bukan langsung memanggil dan status melalui WC, tetapi tidak memerinci pakaian/barang/rute. |
| WO-DEV-013 | WO-DOC-024-C003 | 2 | body 11,12 | Waktu siap dinilai setelah makeup, pakaian, benda prosesi, pendamping, dan rute terkonfirmasi. | Langsung memberi kriteria siap dan jalur laporan WC/floor; gunakan kriteria tanpa menganggap jam standby sudah konsisten. |
| WO-DEV-014 | WO-DOC-001-C005 | 1 | body 17,18 | LO memastikan 45 tamu berpindah dari chapel ke dinner sesuai daftar kelompok. | Daftar kelompok memberi kontrol perpindahan chapel, tanpa mekanisme hitung naik/tiba. |
| WO-DEV-014 | WO-DOC-043-C009 | 1 | body 22 | PIC keluarga menyerahkan jumlah kelompok. | Memberi handover jumlah dan kesiapan kendaraan/penerima agar kelompok tidak ditinggal; belum hitung saat naik dan tiba. |
| WO-DEV-014 | WO-DOC-043-C010 | 2 | body 24 | LO mencatat jumlah naik dan tiba per kelompok. | Langsung memberi kontrol kelompok lengkap, perubahan perjalanan sendiri, penerima dinner dan respons keterlambatan. |
| WO-DEV-015 | WO-DOC-016-C004 | 1 | body 14,15 | setelah pengelola serta banquet memberi kondisi aktual. | Memberi pemeriksaan kondisi, PIC keluarga dan EC sebelum solusi seating; belum alasan kursi tampak kosong. |
| WO-DEV-015 | WO-DOC-032-C002 | 1 | body 8 | Bedakan undangan, kelompok, dan orang | Mencegah hitung ganda dan mewajibkan verifikasi PIC keluarga; belum penilaian kursi kosong dan kemampuan banquet. |
| WO-DEV-015 | WO-DOC-032-C003 | 2 | body 10 | pemiliknya belum tiba, berpindah sementara, atau memang tidak digunakan. | Kasus persis kursi kosong, lalu pemeriksaan banquet dan pengelola sebelum penambahan/keputusan. |
| WO-DEV-015 | WO-DOC-041-C003 | 2 | {"block_id":"l0014-0014","line_end":14,"line_start":14,"section":"Satu kelompok datang lebih banyak dari rencana","serialized_char_end":390,"serialized_char_start":0} | floor memeriksa seating, PIC vendor menanyakan layanan banquet, dan PIC venue meminta pengelola menilai kapasitas. | Langsung merinci pemeriksaan tambahan tamu sebelum menjanjikan kursi/makanan dan otorisasi EC/client. |
| WO-DEV-016 | WO-DOC-041-C007 | 2 | {"block_id":"l0026-0026","line_end":26,"line_start":26,"section":"Tamu meminta makanan tertentu","serialized_char_end":316,"serialized_char_start":0} | Jangan menjamin bebas bahan tertentu dari nama menu saja. | Langsung memberi jalur guest desk ke PIC vendor/catering, batas janji, jawaban belum tersedia, dan privasi. |
| WO-DEV-017 | WO-DOC-001-C003 | 1 | body 11,12 | Perubahan biaya atau lingkup layanan memerlukan persetujuan client melalui WC. | Menyediakan hak keputusan perubahan waktu/lingkup, tetapi bukan pemeriksaan banquet atau buffer sambutan. |
| WO-DEV-017 | WO-DOC-009-C004 | 1 | body 14,15 | EC menyesuaikan cue setelah banquet atau catering menyatakan konsekuensi. | Memberi pemeriksaan konsekuensi banquet sebelum perubahan waktu; bukan kasus sambutan dan buffer spesifik. |
| WO-DEV-017 | WO-DOC-030-C002 | 2 | {"block_id":"l0011-0011","line_end":11,"line_start":11,"section":"Sebelum memilih tindakan","serialized_char_end":416,"serialized_char_start":0} | Identifikasi batas venue, kesiapan banquet, posisi pengantin, kebutuhan keluarga | Langsung memberi faktor pemeriksaan sebelum menyesuaikan rundown saat kegiatan berlangsung lebih lama. |
| WO-DEV-017 | WO-DOC-030-C004 | 2 | {"block_id":"l0017-0017","line_end":17,"line_start":17,"section":"Contoh EVT-02","serialized_char_end":410,"serialized_char_start":0} | EC dapat memakai buffer 17.55 sampai 18.00 jika kegiatan segera selesai dan banquet siap. | Kasus persis sambutan melewati rencana, status banquet, buffer terbatas dan waktu baru melalui EC/WC. |
| WO-DEV-018 | WO-DOC-001-C005 | 2 | body 17,18 | Penerima harus menyatakan menerima dan mengulangi titik kritis. | Langsung menyebut isi status/bukti/tugas/risiko dan pengakuan pengganti sebelum pemberi meninggalkan area. |
| WO-DEV-018 | WO-DOC-014-C004 | 1 | body 14,15 | PIC pengantin menyerahkan status kepada floor di titik standby, menyebut kebutuhan yang masih harus dijaga. | Contoh isi handover satu fungsi, tetapi belum acknowledgment dan paket lengkap pengganti PIC. |
| WO-DEV-018 | WO-DOC-047-C002 | 2 | body 8 | event, waktu, area, versi rundown dan layout, status pekerjaan | Langsung merinci isi paket, keputusan terakhir, orang/aset, risiko dan outstanding untuk penerima baru. |
| WO-DEV-018 | WO-DOC-047-C003 | 2 | body 10,11 | Penerima mengulang keputusan terakhir, cue berikutnya, serta satu risiko utama. | Langsung memberi verifikasi penerimaan, pencatatan waktu, aturan pengganti belum hadir, serta log handover mendesak. |

## Verifikasi integritas dan batas audit

PASS: SHA-256 seluruh **545 file existing** dalam baseline awal dan pemeriksaan akhir identik. Cakupan: file pada `data/`, `experiments/`, `src/`, `tests/` (kecuali `__pycache__`), README/pyproject, dan artefak indeks/run pada `D:/ModelCache/wo-retrieval-benchmark`. Verifikasi juga mencocokkan 50 hash source dan empat hash artefak terhadap snapshot, bukan hanya membandingkan sebelum/sesudah. Dua laporan milestone ini adalah satu-satunya tambahan dalam cakupan repository tersebut.

Snapshot: `WO-CORPUS-V1-DRAFT-PILOT-001`; fingerprint dihitung kembali dari empat hash dengan serialisasi canonical snapshot:

`7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`

| Artefak existing | SHA-256 terverifikasi |
|---|---|
| `data/source_corpus/corpus_manifest.json` | `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f` |
| `data/processed/documents.jsonl` | `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01` |
| `data/chunks/chunks.jsonl` | `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0` |
| `experiments/configs/pilot.toml` | `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26` |
| `data/validation/pilot_snapshot.json` | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` |
| `data/benchmark/development_queries_draft.jsonl` | `27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95` |
| `data/benchmark/development_qrels_ai_silver_v1.jsonl` | `786922e8285a7ec9d311ca84e1b2371068a4ec0ffd7aa31d6e31438d060927ed` |
| `data/benchmark/development_qrels_ai_silver_manifest.json` | `804d9af9dc6d4770f660944211f65c9cd3e9c133ad1d75240fd4ce3e7b6a04ac` |
| `data/validation/ai_corpus_review_v1.xlsx` | `98000ffd0e0aee6b6a624f25d6dfe0f962a512015eb5408e65f651fd64b7919b` |

TOML existing parse PASS, tanpa perubahan parameter. JSON/JSONL parse, keunikan pasangan, referensi ID/block, hash teks, matriks keputusan, batch counts, serta sumber kutipan positif PASS. Pemeriksaan ini bukan uji efektivitas retrieval atau sertifikasi ketepatan semua grade. Tidak ada direktori `.git` pada repository ini; bukti integritas menggunakan hash, bukan Git diff. Tidak ada model loading, embedding, retrieval, benchmark, instalasi, download, perubahan source/query/qrels/protokol/kode/indeks, commit, push, PR, atau deploy.
