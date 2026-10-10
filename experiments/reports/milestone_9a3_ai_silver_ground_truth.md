# Milestone 9A.3 — AI corpus review dan partial silver qrels

**AI-GENERATED PROVISIONAL / SILVER STANDARD — NOT HUMAN VALIDATED.**

Artifact creation (AI/system UTC): 2026-10-09T00:48:11.788814+00:00. Tidak ada penilai manusia pada milestone ini. Judul penelitian tetap: IMPLEMENTASI DAN EVALUASI HYBRID RETRIEVAL BERBASIS BM25 DAN DENSE VECTOR SEARCH PADA RETRIEVAL-AUGMENTED GENERATION (RAG) UNTUK KNOWLEDGE MANAGEMENT OPERASIONAL WEDDING ORGANIZER.

## Status dan batas hasil

Review isi source selesai **50/50 dokumen**, review AI query **18/18**. Silver qrels adalah **partial_checkpoint**, bukan dataset complete: **684/6.678 pasangan (10,2426%) judged**, **5.994 unjudged**. Ada **621 grade0,32 grade1,31 grade2**. Tidak ada skor retrieval dihitung.

Ini mengikuti izin terbaru pengguna untuk AI silver khusus development; larangan terdahulu atas qrels otomatis tidak digunakan untuk menolak izin baru ini. Protocol existing tetap tidak diubah. Izin menghasilkan silver tidak mengesahkan metodologi final/main evaluation. Corpus tetap pending_practitioner_validation,18 query tetap draft_pending_expert_review; AI recommendation tidak mengubah status tersebut. Milestone8C tetap end_to_end_pending.

## Metode review corpus

AI membaca isi seluruh50 source operasional:26 DOCX,9 PDF,10 XLSX,5 TXT. DOCX dibaca berurutan menurut body paragraf/tabel; PDF seluruh halaman; XLSX seluruh sheet/baris terisi beserta header dan Panduan; TXT seluruh baris. SHA-256 masing-masing sumber cocok dengan manifest. Manifest/inventory hanya navigasi dan audit, bukan bahan retrievable atau pengganti pembacaan. Workbook preliminary30/20 yang disebut sebelumnya tidak ditemukan sebagai aset input; angka itu tidak disalin.

Workbook baru memuat Corpus Review (50),12 Criteria (50×12 dimensi),Query Review (18). Kriteria: relevansi operasional,konsistensi prosedur,kejelasan peran,urutan waktu,koordinasi vendor,contingency,batas kewenangan/keselamatan,kelengkapan,hubungan lintas dokumen,ambiguitas,asumsi tidak didukung,terminologi. Evidence locator mengacu body/halaman/baris source, bukan klaim bahwa seluruh dokumen telah diuji di lapangan. Perbandingan lintas dokumen difokuskan pada keluarga topik, bukan exhaustive1.225 pasangan dokumen. Dokumen manusia/researcher existing tetap kosong dan tidak diisi oleh AI.

Rekomendasi: **47 AI_APPROVE,3 AI_REVISE,0 AI_REJECT,0 AI_UNCERTAIN**. AI_APPROVE berarti cukup koheren sebagai draft tekstual dalam lingkup isi, bukan praktik resmi, validasi ahli, kepatuhan atau jaminan keselamatan. Semua50 mempunyai uncertainty note: kapasitas/personel/durasi/fasilitas nyata belum dibuktikan. Tidak dibuat skor confidence numerik palsu.

## Temuan prioritas dan perbandingan sumber

**X01 — klarifikasi waktu standby EVT-02 (024 dan042: AI_REVISE).** WO-DOC-024 body11: “sebelum standby 08.30”. WO-DOC-042 Operasional row13 adalah Registrasi akad08.30–08.45; row14 Standby akad dan keluarga08.45–09.00. Ini ketidakselarasan label/jam yang perlu diselesaikan, bukan bukti acara tidak aman. Bisa jadi08.30 target siap personal dan08.45 standby floor, tetapi pembedaan itu belum tertulis. Usul: jelaskan kedua milestone atau pilih jadwal melalui keputusan versi; tidak mengubah sumber sekarang. Query004/013 tetap dijudgment berdasarkan prosedur, bukan mengesahkan salah satu jam.

**X02 — definisi penutupan insiden vs handover area (027: AI_REVISE).** WO-DOC-027 body26: “Insiden ditutup operasional setelah kegiatan dan akses tidak lagi terganggu serta area sudah diserahkan.” WO-DOC-018 line32 dan050 page2 menutup INC-01 pukul21.10 tetapi handover area22.30. Kronologi018/050 saling konsisten; syarat umum027 tidak selaras jika “area sudah diserahkan” berarti handover final. Usul: pisahkan pemulihan gangguan dari penyerahan area, atau nyatakan penutupan21.10 sementara. Tidak menebak praktik perusahaan sebagai jawaban.

Pemeriksaan yang konsisten: peran001/006/045/046/047; cue resepsi017/023/030/042 (17.20 standby,17.30 entrance,17.40 sambutan,buffer17.55–18.00,dinner18.00); transport025/043 (buffer16.25–16.40,naik16.35,dispatch16.40,tiba17.00); aset019/033/048; privacy016/041. Kode G/SEAT berlaku lokal pada event, bukan identitas tamu global. STAFF-11/12 pada040 pendukung guest desk, tidak bertentangan dengan daftar fungsi inti001. Garden versi1.0 dan rain1.1 dibedakan eksplisit pada044; jangan menilai perubahan versi sebagai kontradiksi. Kecukupan dua escort,45 penumpang,20 menit perjalanan, atau waktu pindah garden tidak dapat dibuktikan hanya dari simulasi.

## Review query

Exact text18 query dipertahankan. Enam query003,006,013,014,015,016 mendapat proposed revision pada tab Query Review; belum diterapkan. Catatan:003 perlu konteks C03/EVT-02;006 checkout kru/aset WO;013 readiness personal berbeda dari izin cue;014 hanya kelompok pengguna shuttle;015 kalimat awal fragmen dan kursi tampak kosong;016 jangan menganggap kebutuhan makanan selalu alergi/medis. Distribusi gaya tetap6 lexical_oriented,6 semantic_paraphrase,6 mixed_natural. Gaya bukan bukti keunggulan metode. Semua need mempunyai dukungan source yang ditemukan, tetapi answerability AI bukan human approval dan bukan bukti seluruh chunk relevan sudah ditemukan.

| Query | Dukungan isi yang ditemukan (bukan qrels otomatis) | Catatan skenario |
|---|---|---|
| WO-DEV-001 | 006 Operasional row16; Panduan row11 | RACI perlu pengantar bagi staf baru. |
| WO-DEV-002 | 009 body14; body19 | H-1 adalah recheck; bukan memaksa izin baru. |
| WO-DEV-003 | 017 page1 C02/C03;023 body12;042 rows27–28 | C03 spesifik EVT-02; jangan menganggap kode universal. |
| WO-DEV-004 | 024 body8–12;014 body8 | Jam standby sumber024/042 belum selaras; jangan memilih jam secara otomatis. |
| WO-DEV-005 | 031 page2 Mikrofon gagal/Pemulihan;023 body17 | Peran WO koordinasi, bukan perbaikan perangkat sendiri. |
| WO-DEV-006 | 019 body13;048 Operasional row22 | Perjelas checkout kru/aset WO, bukan tamu hotel atau hanya vendor. |
| WO-DEV-007 | 001 body20;045 body16 | Atasan berarti pemberi instruksi operasional; otorisasi tetap diperiksa. |
| WO-DEV-008 | 008 Operasional row33;Panduan row12;007 body22 | Jangan mencampur belum diperiksa dan benar-benar selesai. |
| WO-DEV-009 | 027 body8,13–16,22;018 lines14–26 | Pilihan tertutup harus dikonfirmasi; bukan pasti tersedia. |
| WO-DEV-010 | 037 page1 Akses orang dan barang;038 rows28–31 | Tidak meminta angka kapasitas, pasang, atau izin yang tak tersedia. |
| WO-DEV-011 | 041 line29;016 body15 | Siapa penanya tidak diketahui; jawaban source memang membatasi dan mengarahkan kebutuhan sah. |
| WO-DEV-012 | 049 body18–20;050 page2 ACT01–05 | Bukan permintaan membuat hasil evaluasi atau skor kepuasan. |
| WO-DEV-013 | 014 body14–15;024 body12;003 body9 | Siap pribadi, siap pindah dan izin cue jangan disatukan; tipe prosesi dapat diperjelas. |
| WO-DEV-014 | 043 body22–24;025 rows18–27;005 page1 | Beberapa tamu tidak berarti seluruh45 wajib naik; rekonsiliasi yang memakai layanan. |
| WO-DEV-015 | 032 body8–15;040 Perubahan rows7–8;041 line14 | Kalimat awal fragmen; kosong secara visual bukan tersedia. |
| WO-DEV-016 | 041 line26;005 page2;021 page1 | Makanan khusus tidak otomatis alergi/medis; sumber jawaban provider, jangan asumsikan jenis kebutuhan. |
| WO-DEV-017 | 030 lines11–17;017 page1 C04/page2 C05;042 rows29–31 | Bukan izin memotong ritual atau menganggap banquet siap dari jam saja. |
| WO-DEV-018 | 047 body8–11;001 body17;045 body22 | Pengganti belum hadir perlu cakupan sementara, bukan dianggap menerima pesan. |

Overlap yang dibatasi:003 cue lintas fungsi vs013 readiness pasangan;004 konfirmasi MUA sebelum acara vs013 hari acara;008 outstanding persiapan vs012 action debrief;005 mikrofon gagal vs017 durasi sambutan;006 aset vs018 kendali PIC. Tidak menghapus query hanya karena topik beririsan.

## Metode silver judgment dan checkpoint

Unit adalah pasangan exact query text dan exact frozen chunk.text; label bukan parent-document relevance. Title/heading/locator dipakai mengenali konteks, tidak digunakan untuk memasukkan jawaban yang hanya ada di chunk lain. Grade2 = informasi langsung dan substantif untuk kebutuhan, tidak wajib seluruh jawaban lengkap dalam satu chunk; grade1 = aspek yang berguna tetapi terbatas/generik lintas skenario; grade0 = isi diperiksa dan tidak memberi dukungan substantif untuk need spesifik. Kesamaan domain/keyword tidak cukup. Contoh006-C002/001 mendapat2 karena baris A EC/R guest desk benar-benar ada,006-C005/001 mendapat1 karena hanya definisi A/R.

AI membaca34 chunk awal seluruhnya dalam3 batch, menilai masing-masing terhadap18 query dengan matriks keputusan eksplisit. Scope dipilih purposively berdasarkan informasi operasional yang ditemukan saat membaca source; ini bukan sample acak, pooling dari ranking retriever, atau bukti lengkap. Second-pass menambahkan4 chunk016-C004,032-C002,032-C003,048-C003 dan memeriksa masing-masing terhadap seluruh18 query. Hasil akhir38 chunk dari19 dokumen. Batas konteks setelah review50source dan penulisan evidence membuat exhaustive6.678 penilaian tidak diselesaikan pada run ini; fallback parsial dipakai sesuai izin pengguna. Tidak ada grade yang dihasilkan dari keyword classifier, BM25/Dense similarity, method ID, atau ranking.

JSONL hanya menyimpan684 **assessed pairs**. **Absence berarti unjudged, bukan0.** Manifest menyimpan daftar exact judged38 dan unjudged333 chunk IDs, coverage per query, hash input, matriks keputusan, batch evidence dan self-audit. Tidak ada uncertain pair dipaksakan jadi0; assessed ambiguous cases diberi grade terbatas dengan uncertainty note, sedangkan333 chunk/query yang belum dinilai tetap unknown. Checkpoint ini resumable dengan key(query_id,chunk_id), input hashes dan snapshot fingerprint; lanjutkan hanya pasangan yang belum ada setelah memverifikasi semua hash tetap sama, atau simpan perubahan grade dalam log version baru. Original query/evidence tetap tidak diubah.

Setiap positive63 memiliki alasan spesifik, exact excerpt yang cocok dengan substring chunk, source locator/block refs, document mapping, query/chunk text hashes, AI provenance dan ai_silver_provisional. Negative621 mempunyai pair_examined=true,reason code NO_SUPPORT_FOR_SPECIFIC_INFORMATION_NEED dan fokus isi chunk dibanding need query; bukan default negative seluruh corpus.

| Query | Judged | Unjudged | Grade0 | Grade1 | Grade2 |
|---|---:|---:|---:|---:|---:|
| WO-DEV-001 | 38 | 333 | 36 | 1 | 1 |
| WO-DEV-002 | 38 | 333 | 36 | 1 | 1 |
| WO-DEV-003 | 38 | 333 | 31 | 5 | 2 |
| WO-DEV-004 | 38 | 333 | 35 | 1 | 2 |
| WO-DEV-005 | 38 | 333 | 36 | 0 | 2 |
| WO-DEV-006 | 38 | 333 | 35 | 1 | 2 |
| WO-DEV-007 | 38 | 333 | 35 | 2 | 1 |
| WO-DEV-008 | 38 | 333 | 34 | 3 | 1 |
| WO-DEV-009 | 38 | 333 | 31 | 4 | 3 |
| WO-DEV-010 | 38 | 333 | 36 | 1 | 1 |
| WO-DEV-011 | 38 | 333 | 34 | 2 | 2 |
| WO-DEV-012 | 38 | 333 | 35 | 1 | 2 |
| WO-DEV-013 | 38 | 333 | 33 | 3 | 2 |
| WO-DEV-014 | 38 | 333 | 35 | 2 | 1 |
| WO-DEV-015 | 38 | 333 | 34 | 2 | 2 |
| WO-DEV-016 | 38 | 333 | 37 | 0 | 1 |
| WO-DEV-017 | 38 | 333 | 34 | 2 | 2 |
| WO-DEV-018 | 38 | 333 | 34 | 1 | 3 |

Setiap query:38/371=10,2426% coverage. Relevant count dalam pool tidak mengestimasi jumlah relevan corpus; tidak ada klaim query tanpa relevant chunk. Semua18 memiliki positive dalam pool; jumlah positive tidak digunakan untuk balancing label. Sisa333 per query masih dapat mengandung relevansi penting. Query016 baru mempunyai1 positive dalam pool, sedangkan source005 page2,021 page1 dan026 Operasional row13 juga membahas permintaan makanan khusus. Chunk terkait yang belum dinilai tetap unjudged dan menjadi prioritas continuation, bukan otomatis positive atau negative. Rentang positive pool1–7 bukan estimasi prevalensi atau alasan menambah/mengurangi grade agar jumlah seimbang.

## Second-pass quality audit

Seluruh31 grade2 dan32 grade1 diperiksa ulang terhadap kebutuhan dan excerpt; ini AI yang sama, **bukan inter-rater agreement**. Boundary retained:001-C005/009 grade1 (ringkasan rain plan belum semua verifikasi);043-C009/014 grade1 (sebelum boarding, belum hitung naik/tiba);024-C003/004 grade1 (urutan/ETA, bukan daftar konfirmasi lengkap; X01 terbuka). Cross-document privacy,readiness,aset,handover,transport dibandingkan.

Dua perubahan setelah checkpoint pertama:008-C005/011 **0→1** karena akses daftar terbatas membantu sebagian kebutuhan privacy dan harus konsisten dengan006-C002;024-C003/003 **0→1** karena prasyarat umum pasangan/area/pihak prosesi konsisten dengan014-C004, tetapi tidak seluruh C03. Audit memperluas4 chunk (72 pasangan); positive baru di016/032/048 tidak dianggap berarti chunk lain nonrelevant. Sampel18 grade0 (satu/query) ditelaah ulang dengan alasan spesifik di manifest; contoh030-C004/005 hanya delay sambutan, bukan mikrofon;049-C007/008 action pascaacara berbeda dari outstanding H-7. No changes based on retrieval metrics.

## Validasi dan integritas

Workbook diekspor dengan artifact-tool, dihitung ulang, dirender untuk pemeriksaan visual, dibaca ulang dengan openpyxl. Tidak ada formula/error token ditemukan. JSONL dibaca ulang; manifest divalidasi setelah ditulis. Input TOML parse PASS tanpa modifikasi. Validasi struktur tidak membuktikan kebenaran semantic label.

- source_hashes: PASS
- original_query_texts: PASS
- workbook_readback: PASS
- workbook_formula_error_scan: PASS (0 matches)
- workbook_visual_preview: PASS (Corpus Review and Query Review previews visually inspected)
- query_and_chunk_ids: PASS
- document_mapping: PASS
- duplicate_pairs: PASS (0)
- grade_domain: PASS (0/1/2 only for judged pairs)
- positive_evidence_exact_substring: PASS (63/63)
- positive_specific_reason_and_locator: PASS (63/63)
- negative_reason_codes: PASS (621/621)
- unknown_not_encoded_as_zero: PASS (5994 pairs absent, explicitly unjudged)
- pair_accounting: PASS (684 + 5994 = 6678)
- coverage_all_queries: PASS (18/18)
- snapshot_metadata: PASS
- human_validation_claims: PASS (AI only, 0 human raters)
- toml_parse: PASS (pilot and retrieval protocol)
- protected_existing_bytes: PASS (541/541)

Snapshot ID **WO-CORPUS-V1-DRAFT-PILOT-001**. Fingerprint yang dihitung ulang **7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40**. SHA snapshot **279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e**. Seluruh **541 existing files** baseline sama byte-for-byte, termasuk source,canonical,chunks,pilot/snapshot,indices,R4code,18query/provenance dan workbook manusia. Sumber50 juga cocok dengan hash source manifest. Hanya empat deliverable baru dibuat; helper/checkpoint/render berada di luar repository. Environment ingestion/ML tidak diaktifkan. Tidak ada commit/push/PR/deploy.

## Bias, kelayakan, dan langkah berikutnya

Corpus dan query disusun dari sumber sintetis yang sama; circularity, shared AI wording/style, confirmation bias, context/selection bias, leniency pada generic partial relevance dan bias self-check dapat terjadi. AI tidak memiliki pengalaman lapangan dan bisa melewatkan implikasi atau menganggap prosedur tertulis masuk akal padahal tak praktis. Same-AI second pass bukan reliability estimate. Exact model backend/version tidak direkam runtime secara terverifikasi sehingga identitas assessment hanya Codex AI assistant pada sesi ini; reproducibility label lebih lemah daripada hash reproducibility. Tidak ada calibration dengan manusia, external expert, atau statistik agreement.

**Belum siap sebagai complete provisional development effectiveness benchmark.** Paket siap ditinjau pengguna sebagai checkpoint silver parsial dan untuk pemeriksaan teknis format di tahap yang nanti diizinkan. Jangan menggunakan absennya judgment sebagai0 atau menyebut Recall terhadap seluruh relevansi. Incomplete qrels juga dapat membias nDCG/MRR jika unjudged diperlakukan nonrelevant; kebijakan evaluasi perlu diputuskan eksplisit setelah review, sebelum menghitung metrik. Jangan tuning terhadap label AI parsial ini atau menggunakannya sebagai final academic ground truth/main test.

Langkah berikutnya setelah review pengguna: lanjutkan semantically assessed pairs yang belum dinilai dengan inputhash sama, review isuX01/X02 dan proposed wording tanpa menimpa frozen source/query, serta minta persetujuan pembimbing atas posisi silver development dalam metodologi. Jika source/query nanti berubah, buat versi/snapshot baru dan periksa mapping/index/qrels, bukan mengedit frozen pilot. **STOP: tidak ada retrieval evaluation,model/GPU inference,query embedding,download/install atau main-query generation pada milestone ini.**
