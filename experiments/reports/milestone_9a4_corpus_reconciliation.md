# Milestone 9A.4 — Corpus reconciliation

Tanggal audit: 2026-10-09. Status: **AI-GENERATED PROVISIONAL / SILVER STANDARD — NOT HUMAN VALIDATED.** Review ini tidak merupakan validasi expert independen atau keputusan peneliti. Corpus tetap `pending_practitioner_validation`, query tetap `draft_pending_expert_review`; status legacy pada artefak tidak diubah. Metodologi researcher-based/single-assessor masih membutuhkan persetujuan pembimbing sebelum menjadi metodologi evaluasi utama.

## Kesimpulan dan cakupan pembacaan

Ditemukan ketidakselarasan tekstual waktu standby EVT-02 dan ketidakselarasan kriteria penutupan insiden. Ada kemungkinan perbedaan konteks, tetapi konteks pembeda itu belum dinyatakan cukup jelas pada sumber. Rekomendasi: pertahankan frozen pilot untuk development teknis sementara; selesaikan keputusan koreksi dan buat versi baru sebelum memperluas silver qrels secara substansial. Tidak ada koreksi diterapkan dalam milestone ini.

Kelima sumber dibaca lengkap: WO-DOC-018 TXT seluruh 32 baris, WO-DOC-024 DOCX seluruh 21 body paragraphs, WO-DOC-027 DOCX seluruh 27 body paragraphs, WO-DOC-042 XLSX seluruh sel berisi pada Operasional dan Panduan, WO-DOC-050 PDF kedua halaman. DOCX locator `body_position` dihitung satu-based termasuk judul/heading; TXT locator adalah baris fisik satu-based; XLSX locator sheet/row/cell, PDF halaman satu-based. Semua tiga AI_REVISE (024,027,042) diperiksa. Manifest/inventory/review aids digunakan sebagai bukti audit, tidak sebagai corpus retrievable.

## C01 — Waktu standby akad EVT-02

Evidence asli:

- **024**, `WO-DOC-024.docx`, body_position 11, heading “Urutan simulasi pagi EVT-02”, canonical `b0011`, chunk `WO-DOC-024-C003`: “Layanan pasangan direncanakan mulai 06.00 WITA, disusul dressing dan pemeriksaan siap sebelum standby 08.30. Akad direncanakan 09.00.” Paragraf yang sama menyatakan jam merupakan asumsi rundown dan harus diperiksa bersama vendor sebelum dipakai nyata.
- **042**, `WO-DOC-042.xlsx`, sheet **Operasional**, header A5:I5 “Mulai | Selesai | Durasi menit | Aktivitas | PIC | Vendor terkait | Cue | Dependensi | Fallback atau komunikasi”; **A13:B13** 08:30–08:45, **D13** “Registrasi akad”, **G13** “Buka tamu”. **A14:B14** 08:45–09:00, **D14** “Standby akad dan keluarga”, **E14** “floor”, **G14** “Standby prosesi”, **H14** “Pemimpin prosesi, pasangan, keluarga siap”. A15=09:00, D15=“Akad sesuai konfirmasi”. Canonical `s1-r0014`, chunk `WO-DOC-042-C002`.
- 042 **Panduan row10** menyebut EVT-02/CLIENT-02/VENUE-02, sekitar 280 tamu, WITA. 024 body4 juga merujuk EVT-02 serta 042. Jadi ini bukan dua event atau zona waktu yang berbeda.

**Confirmed:** sumber memberi waktu berbeda untuk istilah standby akad pada event yang sama: 08.30 vs 08.45. Registrasi 08.30 pada 042 tidak otomatis menjelaskan mengapa 024 menyebutnya standby. **Unresolved:** mungkin 08.30 dimaksudkan siap personal dan 08.45 standby floor; kedua sumber belum menetapkan pembedaan tersebut. Jangan menganggap interpretasi ini fakta atau mengklaim jadwal sebenarnya pasti salah. Jam simulasi bukan bukti kejadian nyata.

Dampak operasional potensial: PIC pengantin/floor/vendor bisa memakai titik kesiapan yang berbeda 15 menit. Dampak retrieval: dua chunk dapat menjawab waktu standby secara berbeda; hal ini berbeda dari error algoritma. Query development 004/013 terutama meminta proses konfirmasi/readiness, sehingga ketidakselarasan waktu tidak otomatis membuat seluruh support pada chunk tidak relevan.

**Proposal minimal, bersyarat:** apabila peneliti menetapkan rundown 042 sebagai referensi EVT-02, ubah hanya “standby 08.30” menjadi “standby 08.45” pada 024 body11 dalam versi corpus baru. Akad 09.00 tidak diubah. Periksa kembali konsistensi buffer/kesiapan dengan dokumen terkait; audit ini tidak membuktikan kelayakan layanan vendor nyata. Jika 08.30 memang dimaksudkan sebagai readiness personal, peneliti perlu menyetujui redaksi yang secara eksplisit membedakannya dari standby prosesi 08.45. Jangan menambah definisi tersebut tanpa keputusan penulis.

**Status 042:** telah ditinjau penuh sebagai dokumen ketiga AI_REVISE. Baris 12–15 membedakan standby registrasi, registrasi, standby prosesi, dan akad. Tidak ditemukan kebutuhan perubahan intrinsik pada baris tersebut setelah membandingkan sumber. 042 dapat menjadi referensi rekonsiliasi tanpa ikut diedit apabila 024 diselaraskan. Temuan ini tidak mengubah label AI_REVISE existing menjadi AI_APPROVE.

## C02 — Penutupan insiden dan handover area

Evidence asli:

- **027**, `WO-DOC-027.docx`, body_position **26**, heading “Dokumentasi dan penutupan”, canonical `b0026`, chunk `WO-DOC-027-C009`: “Insiden ditutup operasional setelah kegiatan dan akses tidak lagi terganggu serta area sudah diserahkan.” Dilanjutkan: “Tindakan perbaikan proses dapat tetap terbuka untuk debrief.”
- **018**, `WO-DOC-018.txt`, **line32**, bagian penutupan/handover: “INC-01 ditutup secara operasional pukul 21.10 setelah kegiatan publik selesai dan tidak ada hambatan tersisa dari perpindahan.” Pada baris yang sama: “Handover area selesai 22.30 dalam simulasi” dan “tindak lanjut proses tetap terbuka untuk debrief meskipun insiden operasional ditutup.”
- **050**, `WO-DOC-050.pdf`, **page2**, heading “Penutupan operasional dan handover”: “INC-01 ditutup operasional 21.10 setelah kegiatan publik selesai dan hambatan pemindahan tidak lagi terbuka dalam simulasi.” Kemudian: “PIC vendor menangani checkout, PIC venue memeriksa area dengan pengelola, dan handover area selesai 22.30.” Sumber menegaskan penutupan insiden tidak menyatakan semua evaluasi selesai atau semua aset nyata diperiksa.

**Confirmed:** 018 dan 050 konsisten satu sama lain: penutupan operasional 21.10 dan handover area 22.30 adalah dua tahap berbeda, dengan evaluasi tetap terbuka. Kriteria 027 menambahkan syarat “serta area sudah diserahkan” yang tidak dijelaskan cakupannya. Jika istilah itu berarti final handover area, contoh 018/050 belum memenuhi kriteria 027 saat ditutup 21.10: ada ketidakselarasan normatif terhadap kronologi, bukan dua kronologi yang saling berbeda.

**Unresolved:** 027 juga mencakup EVT-01/EVT-04 dan dapat saja merujuk serah terima area operasional yang lebih awal. Sumber tidak menyebut penerima, waktu, atau definisi tahap itu. Karena itu interpretasi alternatif masih hipotesis; jangan menyatakan telah terbukti tidak ada konflik, atau mengarang handover antara untuk menutup celah.

Dampak operasional potensial: kondisi penutupan log dan tanggung jawab serah terima dapat tertukar; penutupan insiden bisa disalahartikan menutup checkout/handover. Dampak retrieval: pertanyaan tentang kriteria penutupan akan menemukan definisi yang lebih ketat daripada contoh. Query009 menanyakan readiness alternatif, bukan waktu penutupan; tiga chunk 027 yang sudah judged tidak memuat paragraf26, sehingga tidak otomatis harus diganti gradenya.

**Proposal minimal, bersyarat:** jika peneliti mempertahankan pembedaan tahap pada 018/050, usulkan pengganti satu kalimat 027 body26: “Insiden ditutup operasional setelah kegiatan publik selesai dan hambatan kegiatan serta akses tidak lagi terbuka. Serah terima area dan outstanding tetap dicatat serta diselesaikan melalui handover terpisah.” Ini memperjelas batas penutupan tanpa menghapus kewajiban handover atau menambah aturan venue. Tetap perlu persetujuan penulis, bukan SOP resmi yang ditetapkan AI.

Jangan otomatis mengganti 21.10 menjadi 22.30 pada 018/050. Jangan menyebut 21.10 sebagai “pemulihan sementara” seolah tertulis pada sumber: keduanya secara eksplisit menyebut ditutup operasional. Opsi redaksi itu muncul pada AI review sebelumnya, tetapi tidak didukung sebagai fakta sumber. Jika peneliti justru menghendaki final handover sebagai prasyarat penutupan, kronologi harus direkonsiliasi berdasarkan keputusan penulis; waktu penutupan baru tidak boleh dibuat oleh audit ini.

## Rekonsiliasi review AI 30/20 dan 47/3

Workbook terbaru `data/validation/ai_corpus_review_v1.xlsx` terverifikasi 50 document decisions: **47 AI_APPROVE, 3 AI_REVISE, 0 AI_REJECT**; yang revise adalah 024,027,042. Ini keputusan AI konseptual/provisional, bukan 47 dokumen tervalidasi manusia. Audit ini tidak menilai ulang 47 dokumen lain atau mengesahkan semuanya.

Workbook AI lama dengan 30 conceptual approve/20 revise **tidak ditemukan dalam cakupan pencarian**: XLSX repository di luar environment, XLSX pada direktori attachments, dan nama anggota arsip `data.zip`. Workbook expert/researcher kosong tidak merupakan pengganti hasil AI lama. Angka 30/20 hanya tersedia dari konteks pengguna; rubric, source hashes, document-level findings, versi dan tanggal review lama belum dapat dibandingkan. Ini bukan klaim file tersebut tidak ada di seluruh komputer.

Selisih agregat adalah +17 approve/−17 revise, tetapi belum dapat dipetakan menjadi 17 dokumen tertentu yang berubah keputusan. Kemungkinan penjelasan: rubrik berbeda; ambang approve/revise lebih menekankan kelayakan konseptual daripada kesiapan SOP; cakupan pembacaan berbeda; atau ketidakstabilan judgment AI. Semuanya hipotesis, bukan root cause terkonfirmasi. Hasil terbaru tidak otomatis menggugurkan temuan lama. Jika workbook lama disediakan, cocokkan Document ID, hash source, rubrik dan setiap finding; pertahankan temuan yang belum terselesaikan beserta alasan rekonsiliasi. Jangan mencari kesamaan angka dengan memaksa keputusan.

## Kesiapan corpus dan impact analysis

| Opsi | Rekomendasi dan batas |
|---|---|
| A — pertahankan frozen pilot | Layak sementara untuk development teknis pada snapshot existing dengan disclosure konflik dan status AI; belum corpus final atau ground truth final. Milestone ini tidak menjalankan eksperimen. |
| B — corrected corpus baru | Lebih disarankan sebelum memperluas ribuan judgment, setelah peneliti menyetujui makna standby dan kriteria closure. Mengurangi pekerjaan penilaian ulang. Tidak diimplementasikan sekarang. |

Impact envelope konservatif tiga dokumen yang direkonsiliasi:

| Dokumen | Chunk existing | Chunk yang sudah judged | Pasangan existing | Grade0/1/2 existing |
|---|---:|---:|---:|---|
| 024 | 6 | 2 | 36 | 32/2/2 |
| 027 | 9 | 3 | 54 | 49/2/3 |
| 042 | 8 | 0 | 0 | 0/0/0 |

Total envelope 23 chunk/414 pasangan potensial terhadap18 query; **90 pasangan existing** pada lima chunk perlu pemeriksaan mapping bila versi source berubah, bukan otomatis salah semua. Proposal utama mengubah 024 dan027 saja, sedangkan042 menjadi referensi; envelope dokumen yang benar-benar diedit saat itu15 chunk/270 pasangan potensial. Perubahan langsung saat ini menunjuk **024-C003** (18 judged, grade1 pada003/004 dan grade2 pada013) serta **027-C009** (belum judged). Re-extraction/re-chunking dapat mengubah batas/ID/context lebih luas; jangan menyimpulkan hanya dua chunk berubah sebelum pipeline dijalankan. Dokumen sumber018/050 tetap menjadi evidence referensi jika tidak direvisi.

Setelah persetujuan terpisah: buat namespace corpus version baru (nama dan snapshot ID baru ditetapkan peneliti), simpan original frozen pilot utuh; simpan correction log old/new text, source locator dan alasan. Jalankan pipeline extraction/chunking existing pada source versi baru dengan konfigurasi terdokumentasi; buat manifest, canonical/chunks dan snapshot/fingerprint baru tanpa overwrite snapshot lama. Verifikasi format/count/block coverage dan ID mapping berbasis isi/hash/context, bukan kesamaan ID saja. Tinjau ulang provenance18 query dan answerability; jangan mengubah pertanyaannya otomatis. Qrels baru harus terikat snapshot baru: reassess pasangan berubah dan audit kemungkinan transfer pasangan identik; jangan menyalin grade hanya karena Document ID sama. Rebuild R1/R2/R3 corpus indices dan validasi integrasiR4 terhadap versi baru; cached corpus/query artifacts tidak diasumsikan kompatibel.

## Silver qrels, risiko, dan langkah berikutnya

Coverage dan tabel18 query, evidence63 positives, selection bias dan completion plan tersedia dalam laporan pendamping `milestone_9a4_qrels_readiness.md`. Ringkasan: **684/6678 (10,24%)** judged, **5994 (89,76%)** unjudged; distribusi0/1/2=621/32/31. Pool purposive38 chunk dari19 dokumen meliputi10 kategori, bukan coverage seluruh corpus. Semua query memiliki38 judged/333 unknown; unknown tidak menjadi grade0.

Risiko utama: corpus sintetis dan query yang disusun dari corpus, bias AI yang sama dalam penyusunan/review/judgment, ambang partial-support lintas konteks, serta tidak adanya penilai independen. Hash dan exactquotes memberi traceability, bukan external validity. Setelah keputusan versi, usulkan exhaustive remaining333 chunk×18 query dalam111 batch kecil berisi3 chunk/54 pasangan; simpan penilaian isi, alasan spesifik, uncertainty dan checkpoints immutable. Pooling lebih ringan tetapi tetap incomplete dan berisiko mengabaikan relevansi di luar pool. Tidak ada perluasan label pada milestone ini.

**Next milestone yang direkomendasikan:** review peneliti atas dua correction proposals, penetapan versi corpus dan kalibrasi rubric evidence/grade; persetujuan pembimbing untuk penggunaan AI silver/researcher-based evaluation. Setelah pengguna mengizinkan, baru revisi/versioning atau lanjut judgment. Tidak ada klaim human/expert validation atau gold standard. STOP setelah kedua laporan audit ini.

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
