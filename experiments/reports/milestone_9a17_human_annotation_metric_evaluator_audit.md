# Milestone 9A.17 — Human Annotation & Metric Evaluator Ready

Tanggal laporan: 10 Oktober 2026. Peneliti dan primary human annotator: **Muhammad Ivan Verdyansyah**.

**Status: 9A.17 — HUMAN ANNOTATION & METRIC EVALUATOR READY.** Aplikasi lokal, input 654 pasangan, storage terpisah, evaluator, tests, dan generator laporan telah tersedia. **Development effectiveness results belum tersedia; main evaluation belum dijalankan.** Seluruh human records masih PENDING. Kesiapan calculator dibuktikan dengan tests sintetis, bukan dengan mengisi human judgments penelitian.

## 1. Audit sumber dan implementasi

Audit membaca source Python retrieval dan pipeline, laporan 9A.12–9A.15, dokumen supervisor 9A.16, snapshot V2, queries, qrels, ranking, union pool, manifests indeks, serialized text, dan cache query vectors. Pembacaan penuh dan SHA-256 dicatat pada `experiments/results/milestone_9a17_human_workflow_audit/source_audit.json`. Verifikasi tidak menjalankan retrieval pada corpus penelitian atau inference model.

| Komponen | Hasil verifikasi |
|---|---|
| Frozen snapshot | WO-CORPUS-V2-AI-CORRECTED-PILOT-001 |
| Fingerprint | `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6` |
| Sumber / chunks | 50 dokumen / 371 chunks |
| Development queries | 18; 6 lexical_oriented, 6 semantic_paraphrase, 6 mixed_natural |
| Implementasi | R1 TF-IDF, R2 BM25, R3 BGE-M3 Dense, R4 BM25 + Dense RRF |
| Saved ranking runs | 72 = 18 queries × 4 metode; 720 baris Top-10 |
| Union Top-20 pool | 654 unique query–chunk pairs |
| Existing silver dalam pool | 90; 564 lainnya unknown |
| Existing corpus-query silver qrels | 684: Grade 0 = 621, Grade 1 = 32, Grade 2 = 31 |
| Corpus-query pairs tanpa silver judgment | 5.994 dari 6.678; bukan Grade 0 |
| Hashes frozen input annotation | 194 artefak, cocok |
| Protected source integrity | 754 unique files cocok; 360 file baseline sebelum task dan 740 file ledger historis dengan overlap |

Pemeriksaan mencakup aggregate fingerprint/source hashes, status COMPLETE indeks R1–R3, serialized corpus parity R1/R2, query cache binding R3, query/chunk/document IDs, score finite, urutan score/ties, rank sequence, pasangan union pool terhadap blind ledger, serta seluruh silver qrel/text/snapshot bindings. Output terdahulu juga dicocokkan dengan checksums pada manifest masing-masing. Fingerprint/input hashes diverifikasi ulang ketika package human dibuka; perubahan sumber menyebabkan penolakan.

Query file historis tetap memuat metadata snapshot V1. Binding V2 yang digunakan saved pilot ditetapkan melalui migration artifacts/ledger dan manifest V2. Metadata historis tersebut tidak ditulis ulang. Dokumen supervisor 9A.16 dibaca dan hash-nya tetap identik, dengan 12 tabel; dokumen lama tidak disimpan ulang.

Audit consistency terdahulu tetap hanya bukti kesesuaian penilai AI pada pilot kecil, bukan validitas human/expert. Kedua AI assessor tidak sepenuhnya terisolasi. Paket baru tidak memakai grade AI sebagai human ground truth dan tidak memaksakan adjudikasi atas disagreement lama.

## 2. Protokol development yang dibekukan

Keputusan pengguna menetapkan peneliti sebagai human annotator. Label resmi tahap ini: **Researcher-annotated relevance judgments**. `expert_validated=false` dan `independently_validated=false`. Rancangan expert assessment pada TOML lama tetap merupakan rencana historis; keputusan saat ini dicatat melalui protokol human development baru, tanpa mengubah TOML atau qrels lama.

Scope hanya 18 existing **development** queries dan seluruh 654 pasangan union Top-20. Termasuk 90 pasangan bersilver, semuanya mulai tanpa grade. Fixed shuffle seed **17042**, assigned identifiers `HUMAN-DEV-0001` hingga `HUMAN-DEV-0654`, exact source/text hashes, dan urutan tersimpan menghasilkan resume reproducible.

UI tidak mengirim metode asal, retrieval score/rank, query style, AI grades, atau expected metrics. Source locator, document/chunk ID, judul, heading, query, dan serialized chunk lengkap tetap tersedia. Ini mengurangi petunjuk retrieval saat menilai, tetapi tidak membuktikan kebutaan penuh: peneliti mungkin pernah melihat artefak lama. Manifest mencatat keterbatasan exposure/independence tersebut.

Rubric: Grade 0 tidak memberi dukungan berguna; Grade 1 memberi dukungan substantif sebagian; Grade 2 langsung memenuhi kebutuhan utama. UNRESOLVED berarti belum dapat diputuskan, dengan grade null. PENDING berarti belum dinilai, juga null. Kecocokan kata/topik saja tidak otomatis relevan. Evidence opsional harus merupakan substring persis chunk; catatan opsional dianjurkan untuk kasus ambigu. Penilaian didasarkan pada isi pasangan, tanpa memindahkan jawaban dari dokumen lain.

## 3. Aplikasi, persistence, dan provenance

Jalankan dari PowerShell:

```powershell
Set-Location 'D:\Project\wo-retrieval-benchmark'
.\.venv\Scripts\python.exe -B scripts/human_annotation.py serve
```

Buka `http://127.0.0.1:8765`. Aplikasi memakai Python standard library dan browser, tanpa dependency baru, database, cloud, PyTorch, atau GPU. Navigasi Sebelumnya/Berikutnya, posisi, PENDING/UNRESOLVED, progress, optional notes/evidence, autosave, tombol simpan, dan JSONL download tersedia dalam bahasa Indonesia. Tunggu **Tersimpan** sebelum menutup. Ctrl+C menghentikan server; perintah yang sama melanjutkan ke PENDING pertama.

Workspace terpisah: `experiments/human_judgments/development_v2/`. Input/manifest immutable; history menyimpan timestamp UTC aktual, researcher identity, revision/sequence, snapshot/input/protocol binding, dan hash chain. Revisi lama dipertahankan. Atomic replacement setelah fsync mencegah file terpotong; write/server locks dan expected revision mencegah konflik proses/tab. Hash chain mendeteksi kerusakan atau editing inkonsisten, bukan tanda tangan digital independen. Backup seluruh workspace setelah server berhenti tetap diperlukan.

Server hanya bind 127.0.0.1, memeriksa Host/Origin dan session token pada POST, membatasi request/schema, dan tidak menyediakan endpoint arbitrary files/raw manifest. Browser menampilkan source melalui textContent, bukan HTML sumber. Provenance dan source binding tidak dapat diganti dari save request. Identitas penilai adalah deklarasi protokol lokal, bukan autentikasi atau pembuktian siapa yang mengoperasikan browser; perangkat/workspace perlu dijaga oleh peneliti.

Initial export tersedia pada `exports/initial_pending_20261010/`: JSONL 654 PENDING, TSV kosong, manifest checksums. TSV hanya memuat RESOLVED, sehingga absent rows tidak berarti nonrelevant. Evaluator membaca validated human history, bukan TSV parsial atau AI qrels. Ekspor baru dan report baru menolak overwrite.

## 4. Definisi evaluator dan completion gate

| Metrik / kebijakan | Kontrak sebelum human labels |
|---|---|
| Precision@5 / @10 | Relevant jika grade ≥1; jumlah relevant pada returned window dibagi requested k |
| MRR@10 | Reciprocal rank relevant pertama, grade ≥1; 0 jika tidak ada hit dalam 10 |
| nDCG@5 / @10 (pooled) | Gain 2^grade−1; discount log2(rank+1); IDCG dari seluruh human-resolved pool query yang sama, sort grade menurun |
| Missing / UNRESOLVED | Tetap unknown/null; tidak diimputasi menjadi 0 |
| Completion | Seluruh 654 pasangan harus RESOLVED dan setiap returned Top-5/10 item memiliki valid human judgment |
| Missing returned slots | Zero hit/gain untuk posisi yang memang tidak dikembalikan; tanpa membuat dummy qrels |
| Ties | Saved score descending, chunk ID ascending; perubahan urutan ditolak |
| Aggregation | Macro atas 18 fixed query IDs yang sama untuk semua metode; per query dan 3 styles terpisah |
| Zero pooled IDCG | Seluruh evaluation diblokir; review answerability/protocol terpisah, jangan memaksa grade |
| Recall@10 | Tidak dihitung; corpus-wide relevant denominator belum diketahui |
| Method comparison | 6 paired contrasts, mean delta/win/tie/loss; tidak merupakan uji signifikansi |

Gate sengaja lebih ketat daripada hanya kelengkapan Top-10: seluruh pool harus selesai agar pooled IDCG dapat ditentukan konsisten. Tidak ada selective incomplete-query dropping atau judged-only denominator. Pool tanpa relevansi untuk sebuah query tidak membuktikan corpus-wide no-answer; grade tidak boleh disesuaikan untuk membuka gate. Konfirmasi no-answer atau perluasan assessment memerlukan desain versi baru yang disepakati.

Keluaran evaluator: JSON; macro/per_query/by_style/window_coverage/method_comparisons CSV; summary Markdown dan checksum manifest. Word editable dengan tabel macro/style/per-query dan lima metrik hanya dapat dibuat ketika status **VALID_COMPLETED_DEVELOPMENT_POOLED**. Word menggunakan A4, Calibri, tabel bergaris tipis, label development/provenance/completeness, dan tidak menulis kesimpulan metode terbaik.

Pada milestone ini, `readiness_before_annotations` hanya membuktikan gate **BLOCKED_INCOMPLETE_ASSESSMENTS**: 654 missing, 0 resolved, 0 UNRESOLVED; seluruh metric cells null/NOT COMPUTED dan evaluated_queries=0. Tidak ada angka effectiveness penelitian atau Word hasil penelitian yang dibuat. Exit code 2 adalah penghentian gate yang disengaja.

Setelah seluruh judgments benar-benar selesai, perintah yang disediakan untuk **development**, belum dijalankan pada completed research data:

```powershell
.\.venv\Scripts\python.exe -B scripts/human_annotation.py evaluate --out experiments/results/human_development_evaluation/run_01 --word
```

## 5. Tests dan quality control

**189 unique tests PASS, 0 failure/error pada final runs**: 28 tests baru human workflow/evaluator; 132 regresi offline existing; 29 tests existing pipeline/versioned pipeline. Suite 57 merupakan gabungan 29 existing dan 28 baru, bukan tambahan 57 unique tests. Setelah perubahan format Word terakhir, 28 tests baru dijalankan ulang dan tetap PASS.

Coverage: matematis Precision, MRR, graded nDCG; zero ideal; invalid/bool/null grades; duplicate pair/run/candidate; rank ties; missing/unresolved/short windows; deterministic evaluation; per-style/macros/paired contrasts; AI provenance/main scope rejection; HTTP Host/Origin/token/schema; hidden-label payload allowlist; fixed shuffle; persistence/revisions/stale tab; atomic failure preserving old bytes; history/input/snapshot tampering; family/exact-normalized overlap dan semantic review requirement untuk future split.

Contoh verifikasi matematis sintetis: Precision `[0,1,2,0,0]` pada k=5 = 2/5; tiga hasil `[0,1,2]` pada k=10 = 2/10; RR `[0,0,1,2]` = 1/3; nDCG memakai `(1/log2(3)+3/log2(4))/(3+1/log2(3))`. Angka tersebut hanya expected values fixture, bukan hasil metode penelitian.

Browser QA pada temporary synthetic workspace membuktikan simpan grade/catatan, navigation, UNRESOLVED, dan reload/resume. Human storage penelitian tidak diisi dalam QA. Word fixture berlabel SYNTHETIC TEST / NOT RESEARCH dirender melalui Microsoft Word native XPS/WPF; ketiga halaman diperiksa visual, termasuk tabel dan per-query text. Fixture berada di temporary directory, bukan deliverable hasil penelitian.

Regresi ML existing memakai dependencies `.venv-ml` yang sudah ada dengan encoder/GPU mocks; tidak mengimpor torch atau menjalankan model/GPU inference. Harness awal mengalami environment/PYTHONPATH/Windows encoding mismatch; final runner memakai environment yang tepat dan UTF-8, tanpa mengubah kode original. Aplikasi human/tests baru berjalan pada `.venv` biasa. Evidence: `test_results.json`, `offline_regression.log`, `base_and_human_tests.log`.

## 6. Main evaluation: rekomendasi, belum eksekusi

**75 evaluation queries masih proposal; tidak dibuat atau difinalisasi.** Sepakati bersama pembimbing jumlah, topic/style distribution, answerability, corpus sintetis versus sumber autentik, scope pooling/exhaustive, penanganan no-answer/UNRESOLVED/UNJUDGED, metrik utama, dan metode analisis statistik sebelum melihat main results. Development metrics tidak otomatis menjadi hasil final skripsi.

Kebutuhan informasi main harus baru, bukan parafrasa 18 development queries. Dokumentasikan information-need families dan provenance; lakukan pemeriksaan IDs/normalized query text/family overlap serta review semantik manusia terhadap intent. Validator menolak overlap eksplisit dan mewajibkan semantic review confirmation; validator tidak dapat membuktikan bahwa family ID baru tidak menyamarkan intent lama. Belum ada main query atau konfirmasi review yang dibuat oleh task ini.

Freeze query set/protokol sebelum ranking dan judgments main; gunakan package/storage terpisah. Hindari pemilihan parameter dari main labels. Peneliti tetap primary annotator; bila praktisi WO atau second human assessor tersedia, simpan independent judgments, exposure disclosure, agreement dan adjudication sebagai tahap validasi tersendiri, mempertahankan keputusan awal. Pilih subset validasi sebelum melihat labels dan dokumentasikan disagreement/no-answer. Corpus-wide Recall memerlukan relevant denominator dari assessment scope yang memadai, misalnya exhaustive corpus assessment per query atau exhaustive subset desain yang dinyatakan.

## 7. Files created dan perubahan

Seluruh perubahan bersifat additive; tidak ada source retrieval existing yang diubah.

- `src/wo_retrieval/human_judgments.py`: frozen package, validation, shuffle, revision history dan completeness.
- `src/wo_retrieval/human_metrics.py`: pure metric functions, strict evaluator, JSON/CSV/MD/Word generator.
- `src/wo_retrieval/human_annotation.html`: UI lokal Indonesia, full texts, autosave/navigation/resume.
- `scripts/human_annotation.py`: prepare/serve/status/export/evaluate CLI.
- `tests/test_human_annotation.py`: 28 tests baru dan synthetic fixtures.
- `experiments/human_judgments/development_v2/`: input/annotation/storage manifests, empty history, initial pending export.
- `experiments/results/human_development_evaluation/readiness_before_annotations/`: BLOCKED/null readiness evidence.
- `experiments/results/milestone_9a17_human_workflow_audit/`: source audit, protected integrity, tests/logs dan output manifest.
- `experiments/reports/milestone_9a17_human_annotation_usage.md`: panduan operasi/grading/resume/export/gates.
- Laporan ini.

Untuk dosen: **implementasi R1–R4 dan saved pilot retrieval tersedia; consistency assessment AI telah diaudit pada milestone sebelumnya; calculator human evaluation kini siap dan diuji; development effectiveness menunggu 654 human judgments; main effectiveness menunggu approved independent queries dan completed judgments.** Belum ada expert/independent validation, final effectiveness, signifikansi statistik, atau klaim metode terbaik.

Tidak dilakukan GPU inference, Colab, retraining, tuning, re-chunking, new query generation, perubahan corpus/qrels/rankings/indices/embeddings, commit, push, atau deploy. Workflow berhenti pada kesiapan annotation dan evaluator.
