# Milestone 9A.18 Controlled Import dan Development Metrics

Tanggal: 10 Oktober 2026. Peneliti: **Muhammad Ivan Verdyansyah**.

**Status: MILESTONE 9A.18 — HUMAN JUDGMENTS IMPORTED, DEVELOPMENT METRICS COMPUTED.** Seluruh 654 pasangan selesai dalam storage resmi. Hasil di bawah merupakan **development pooled evaluation**, bukan hasil evaluasi utama skripsi.

## Preflight dan input

Implementasi CLI, validation/history dan evaluator dibaca sebelum perubahan. State lokal diverifikasi langsung: 66 events untuk 25 current resolved judgments, 629 PENDING, 0 UNRESOLVED. Seluruh 25 keputusan existing cocok persis dengan input pada status, grade, notes dan evidence; tidak ada konflik.

Server awalnya aktif di port 8765. Import tidak dilakukan pada kondisi tersebut. Peneliti kemudian menyatakan perubahan sudah disimpan dan server dimatikan; pemeriksaan ulang memastikan listener dan lock sudah tidak aktif sebelum dry-run dan write. Import memegang server lock dan write lock untuk mencegah app baru membuka workspace selama batch berjalan.

Input: `experiments/human_judgments/development_v2/incoming/wo_reviewed_judgments_654_IMPORT_INPUT.jsonl`.

Input audit: `wo_reviewed_judgments_654_IMPORT_AUDIT.json` pada folder yang sama.

| Pemeriksaan | Hasil |
|---|---|
| Input SHA-256 | `36a422efe1899e7bc0b3cb321edf3d4764bdcfbf0bd7bf27d0543db43afd5bca` |
| Audit SHA-256 | `fc4f2de03fe19c851d196008708f3f45c5f9fdda13274be5abcc5bbaf9eba17b` |
| Annotation input SHA-256 | `f67790436f726a064e234d6665c0c3a7fdbc93a725dc14fea9face2b40afe960` |
| Snapshot | WO-CORPUS-V2-AI-CORRECTED-PILOT-001 |
| Fingerprint | `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6` |
| Assessment IDs / canonical bindings | 654 unik, exact package match |
| Source grade distribution | 0: 429; 1: 152; 2: 73 |
| Notes / nonempty exact evidence | 654 / 225 |
| Queries dengan relevant pair | 18 dari 18 |
| Snapshot, frozen sources, saved rankings, indices | PASS pada existing audit/194 frozen hashes |

Source JSONL dan audit dibaca seluruhnya. Counts, schema, exact binding, grade type, status, evidence substring, checksums dan package identity diperiksa ulang; tidak hanya menerima angka dari audit. Checksums CSV dan JSONL asal yang disebut audit tidak dapat diverifikasi ulang karena kedua file asal tidak tersedia lokal. File import yang benar-benar dipakai dan auditnya tersedia serta terverifikasi. Isi judgments diterima sebagai review peneliti sesuai pernyataan pengguna; task ini tidak memberi grade baru atau melakukan expert validation.

## Safe importer dan hasil import

Importer menambahkan command terpisah `scripts/import_reviewed_judgments.py`, memakai validation, binding, history contract, event builder dan atomic writer yang sama dengan aplikasi. `load_history` tetap menerima native provenance lama dan sekarang menerima optional import source provenance yang divalidasi ketat. Protokol evaluasi tidak berubah.

Dry-run PASS sebelum apply. Dry-run mengikat input/source/audit/annotation manifest/history checksums, daftar missing/skipped/conflicts dan query coverage. Apply menolak plan yang stale, source yang berubah, active lock, atau conflict. Tidak ada import langsung external JSONL ke native history.

| Operasi | Imported | Skipped identical | Conflicts |
|---|---:|---:|---:|
| Import pertama | 629 | 25 | 0 |
| Rerun idempotence actual | 0 | 654 | 0 |

Backup seluruh workspace dilakukan sebelum publication, termasuk incoming, exports, input/manifests dan history. Runtime locks yang dimiliki operasi dikecualikan dari backup. Backup file hashes diverifikasi terhadap workspace. Lokasi: `experiments/results/milestone_9a18_controlled_import/import_20261010/workspace_backup/`, dengan `backup_manifest.json` dan `import_receipt.json` di parent folder.

Seluruh 66 existing events dipertahankan tanpa perubahan; 629 events baru ditambahkan, sehingga total menjadi **695**. Events baru memakai sequence/revision/hash chain sah, label **Researcher-annotated relevance judgments**, identitas peneliti, source path/SHA-256, audit path/SHA-256 dan waktu import UTC aktual. Original assessment timestamp tidak diketahui dan disimpan null, bukan direkayasa dari metadata eksternal. Native decisions lama tetap memiliki provenance awalnya.

Staged events divalidasi sebelum publication. Seluruh batch diterbitkan melalui satu atomic file replacement. Exception setelah publication memulihkan byte history sebelum import dan memverifikasi rollback. Backup tersedia untuk pemulihan manual setelah crash keras. Jangan menyalin backup history di atas revisi baru tanpa audit conflict; hentikan server dan backup state terbaru terlebih dahulu. Crash setelah atomic publication tetapi sebelum receipt tetap dapat diaudit melalui event provenance; rerun memeriksa identical decisions dan tidak menggandakan events.

## Post-import verification dan official export

- Current records: **654**; RESOLVED: **654**; PENDING: **0**; UNRESOLVED: **0**.
- Grade 0: **429**; Grade 1: **152**; Grade 2: **73**.
- Seluruh incoming decisions cocok dengan latest native decisions, termasuk notes/evidence.
- History hash chain, sequence/revisions dan seluruh binding/provenance: PASS.
- Seluruh 18 query memiliki relevant pool member; seluruh returned Top-5/10 windows lengkap.
- Official export: `experiments/human_judgments/development_v2/exports/researcher_reviewed_9a18_20261010/` berisi human JSONL, resolved TREC TSV dan checksum manifest. Tidak mengubah AI qrels.
- Actual rerun import: SKIPPED_IDENTICAL, history tetap 695 events.

Post-import evidence: `import_20261010/post_import_verification.json` dan `quality_control.json` pada folder audit milestone.

## Hasil aktual development evaluation

Run: `experiments/results/human_development_evaluation/milestone_9a18_20261010/`.

Evaluator existing dijalankan pada saved rankings dan validated human history, tanpa retrieval baru atau inference. Status **VALID_COMPLETED_DEVELOPMENT_POOLED**. Macro-average memakai 18 fixed queries yang sama untuk semua metode. Per-query output mencakup 72 method-query rows, category output 12 rows, coverage 144 windows, dan 30 descriptive method-metric contrasts.

| Method | Precision@5 | Precision@10 | MRR@10 | nDCG@5 pooled | nDCG@10 pooled |
|---|---:|---:|---:|---:|---:|
| R1 TF-IDF | 0.633333 | 0.494444 | 0.722222 | 0.486942 | 0.517324 |
| R2 BM25 | 0.622222 | 0.500000 | 0.784722 | 0.497634 | 0.524130 |
| R3 BGE-M3 Dense | 0.744444 | 0.577778 | 0.972222 | 0.646561 | 0.663459 |
| R4 Hybrid RRF | 0.711111 | 0.588889 | 0.944444 | 0.627933 | 0.646549 |

Angka dibulatkan enam desimal untuk tabel audit; JSON/CSV mempertahankan numeric precision. Precision/MRR menggunakan binary threshold grade ≥1. nDCG memakai gain 2^grade−1, discount log2(rank+1) dan ideal denominator dari semua human-resolved union Top-20 pool members untuk query yang sama. Formula/protokol tidak diubah untuk import ini; semua 654 labels dipertahankan persis.

Per category, masing-masing enam queries:

| Category | Method | P@5 | P@10 | MRR@10 | nDCG@5 pooled | nDCG@10 pooled |
|---|---|---:|---:|---:|---:|---:|
| Lexical | R1 | 0.900000 | 0.616667 | 0.916667 | 0.705442 | 0.730916 |
| Lexical | R2 | 0.900000 | 0.650000 | 0.916667 | 0.711055 | 0.724211 |
| Lexical | R3 | 0.900000 | 0.650000 | 1.000000 | 0.790658 | 0.809568 |
| Lexical | R4 | 0.866667 | 0.650000 | 1.000000 | 0.799068 | 0.790716 |
| Paraphrase | R1 | 0.300000 | 0.283333 | 0.555556 | 0.256478 | 0.297709 |
| Paraphrase | R2 | 0.266667 | 0.283333 | 0.694444 | 0.272174 | 0.327499 |
| Paraphrase | R3 | 0.566667 | 0.483333 | 1.000000 | 0.554975 | 0.568619 |
| Paraphrase | R4 | 0.433333 | 0.416667 | 0.916667 | 0.434365 | 0.474077 |
| Mixed | R1 | 0.700000 | 0.583333 | 0.694444 | 0.498905 | 0.523348 |
| Mixed | R2 | 0.700000 | 0.566667 | 0.743056 | 0.509674 | 0.520679 |
| Mixed | R3 | 0.766667 | 0.600000 | 0.916667 | 0.594049 | 0.612190 |
| Mixed | R4 | 0.833333 | 0.700000 | 0.916667 | 0.650365 | 0.674852 |

Pada scope development ini, R3 mempunyai macro-average tertinggi pada P@5, MRR@10 dan nDCG@5/10 pooled. R4 tertinggi pada P@10, serta beberapa metrik category mixed. Perbedaan tersebut deskriptif. Tidak ada pengujian signifikansi statistik, klaim metode terbaik secara umum, atau hasil main evaluation.

## Word dan quality control

Word editable: `experiments/results/human_development_evaluation/milestone_9a18_20261010/development_metrics_report.docx`.

Dokumen menjelaskan scope, penilai, empat metode dan metrik dalam bahasa yang dapat dibaca dosen; memuat macro, categories, semua query beserta teksnya, kelengkapan dan interpretasi proporsional. Tidak memuat kode, logs atau path internal. Tabel Word dibulatkan empat desimal; full precision tetap tersedia di output pendamping. Terdapat 22 tabel native editable. Dokumen dibuat dari actual evaluation JSON, bukan dummy fixtures. Seluruh 440 numeric cells cocok dengan JSON setelah pembulatan. Sembilan halaman diperiksa melalui native Word PDF/A dan Poppler, termasuk zoom tabel; tidak ada angka/tabel terpotong pada dokumen final.

QC numerik memeriksa ulang semua 72 runs menggunakan perhitungan terpisah, lalu empat macros dan 12 category rows; semuanya cocok dengan tolerance 1e-12. Ini adalah pemeriksaan aritmetika, bukan menjalankan evaluation baru/tuning. Source bindings dan old-history prefix dipastikan tetap sah.

Regression: **64 unique tests PASS, 0 failures/errors/skips**: 28 existing human workflow/evaluator, 7 importer tests baru, dan 29 existing pipeline/versioned pipeline. Final human suite 35 tests dijalankan ulang setelah penyesuaian Word dan tetap PASS. Fixtures tetap sintetis dan tidak mengisi ulang research storage. Tests mencakup dry-run readonly, missing/identical handling, status/grade/notes/evidence conflicts, active lock, stale plan, checksum/schema/duplicates/bindings/evidence, atomic publication failure, postpublication rollback, preservation, idempotence, dan import provenance tanpa waktu penilaian palsu. Tidak ada torch import/inference/GPU.

Protected integrity: **779 current protected files** cocok dengan pre-task/historical hashes. Canonical corpus V2, embeddings, indexes, saved rankings, queries, AI qrels, annotation input/manifests dan protocol tetap utuh. Ledger 9A.17 juga menyebut archive `data.zip`, tetapi file tersebut tidak tersedia pada workspace saat pemeriksaan milestone ini; archive itu tidak dipakai sebagai input atau dibuat/dihapus oleh task ini. Karena itu tidak diklaim sebagai verified-current archive. Perubahan existing yang memang diperlukan hanya human history, event/provenance handling di `human_judgments.py`, serta presentasi Word di `human_metrics.py`; perhitungan metrik tetap sama.

## Penggunaan importer

CLI menolak output existing. Untuk input baru, lakukan dry-run ke folder baru terlebih dahulu:

```powershell
.\.venv\Scripts\python.exe -B scripts/import_reviewed_judgments.py dry-run --source experiments/human_judgments/development_v2/incoming/wo_reviewed_judgments_654_IMPORT_INPUT.jsonl --audit experiments/human_judgments/development_v2/incoming/wo_reviewed_judgments_654_IMPORT_AUDIT.json --out experiments/results/milestone_9a18_controlled_import/new_dry_run
```

Jika PASS, `apply` menggunakan source/audit yang sama, `--plan` menunjuk `dry_run.json`, dan `--out` menunjuk folder receipt/backup baru. Untuk data yang sudah diimpor identik, apply menghasilkan SKIPPED_IDENTICAL tanpa menambahkan event. Conflict report wajib diselesaikan peneliti; tidak ada pilihan force/overwrite otomatis.

Files baru: `src/wo_retrieval/human_import.py`, `scripts/import_reviewed_judgments.py`, `tests/test_human_import.py`, laporan ini, audit/import/backup evidence, official export, development result files dan Word. Existing file changes terbatas seperti dijelaskan di atas. Laporan dan manifests milestone terdahulu dipertahankan sebagai catatan historis, bukan ditulis ulang untuk menyamarkan perubahan baru.

## Batas interpretasi dan langkah berikutnya

Penilaian dicatat sebagai **Researcher-annotated relevance judgments**, belum expert-validated atau independently validated. Peneliti dapat pernah melihat ranking/AI labels sebelumnya; independensi dan kebutaan penuh tidak diklaim. Penilaian satu peneliti, corpus sintetis dan 18 development queries membatasi generalisasi. Pool belum exhaustive seluruh corpus: item di luar pool tetap unknown, pooled IDCG tidak setara exhaustive corpus IDCG. **Corpus-wide Recall tidak dihitung.**

Langkah berikutnya: sepakati protokol main dan rencana 75 independent evaluation queries bersama pembimbing; pisahkan information-need families, bukan hanya parafrasa development queries; lakukan semantic split review, freeze queries/protokol/parameter sebelum melihat main labels; simpan main package/judgments terpisah. Review praktisi WO atau second human assessor dapat menambah tahap validasi independen beserta agreement/adjudication yang mempertahankan decisions awal.

Tidak menjalankan GPU inference, tuning, perubahan corpus/queries/ranking/AI qrels/protocol, new query generation, commit, push atau deploy. Main evaluation belum dijalankan. Task berhenti setelah controlled import, development evaluation dan pelaporan.
