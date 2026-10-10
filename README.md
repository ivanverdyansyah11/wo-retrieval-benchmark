# IMPLEMENTASI DAN EVALUASI HYBRID RETRIEVAL BERBASIS BM25 DAN DENSE VECTOR SEARCH PADA RETRIEVAL-AUGMENTED GENERATION (RAG) UNTUK KNOWLEDGE MANAGEMENT OPERASIONAL WEDDING ORGANIZER

Muhammad Ivan Verdyansyah · Program Studi Informatika · Universitas Primakara

## 1. Tentang Penelitian

Penelitian ini membandingkan pencarian informasi untuk menemukan pengetahuan operasional Wedding Organizer (WO), seperti pembagian tugas, koordinasi vendor, rundown, dan penanganan gangguan. Fokusnya adalah **retrieval**, yaitu pemeringkatan potongan dokumen sesuai kebutuhan informasi; implementasi belum mencakup chatbot atau evaluasi jawaban generatif RAG.

Empat metode memakai corpus, chunks, queries, dan protokol yang sama. Hasil yang tersedia merupakan **uji coba development**, bukan evaluasi akhir skripsi.

## 2. Dataset

- 50 dokumen WO sintetis: 26 DOCX, 9 PDF, 10 XLSX, dan 5 TXT.
- 371 canonical chunks pada snapshot V2 `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`.
- 18 development queries: masing-masing 6 `lexical_oriented`, `semantic_paraphrase`, dan `mixed_natural`.
- 654 pasangan dalam union Top-20 pool dinilai peneliti: 429 Grade 0, 152 Grade 1, 73 Grade 2; seluruhnya RESOLVED.

Corpus merupakan simulasi, bukan arsip autentik perusahaan. V1 tetap dibekukan; V2 berstatus `ai_corrected_pilot_not_human_validated`. Penilaian relevansi peneliti tidak menjadikan substansi corpus tervalidasi praktisi. AI silver qrels historis terpisah dari human judgments. Validasi praktisi dan penilai independen masih pending.

## 3. Metode Retrieval

| ID | Metode | Implementasi |
|---|---|---|
| R1 | TF-IDF | scikit-learn; lexical cosine |
| R2 | BM25 | rank-bm25; parameter protokol frozen |
| R3 | BGE-M3 Dense | 1.024 dimensi; exhaustive cosine NumPy CPU |
| R4 | Hybrid BM25 + Dense | Reciprocal Rank Fusion, k=60, bobot sama |

RRF menggabungkan seluruh ranking Dense dengan kandidat BM25 berskor positif. Tie diurutkan menurut `chunk_id`. Encoding BGE-M3 sudah dilakukan; pembacaan indeks dan query vectors existing dapat berjalan tanpa GPU atau model weights.

## 4. Arsitektur Singkat

```text
Dokumen → ekstraksi teks/tabel → preprocessing → canonical chunks → indexing
Development query → retrieval R1–R4 → ranking → union Top-20 pool
Pool → relevance judgments peneliti → pooled development evaluation
```

Snapshot, manifests, hashes, query vectors, ranking, dan history dipertahankan sebagai bukti reproduksibilitas. Kebijakan pipeline/retrieval terdapat pada `experiments/configs/` dan laporan historis.

## 5. Teknologi

Python 3.12; python-docx, pypdf, openpyxl untuk dokumen; scikit-learn, rank-bm25, NumPy, SciPy untuk retrieval; BGE-M3 untuk encoding historis. Penyimpanan memakai JSON/JSONL, CSV, NPY/NPZ, dan manifests SHA-256. Tests memakai `unittest`; annotation memakai server HTTP lokal; laporan Word memakai python-docx.

Versi ingestion: `requirements.lock`; lexical: `experiments/configs/lexical_environment.lock.txt`; provenance encoding: `experiments/configs/ml_environment.lock.json`. Lihat [setup](docs/setup.md).

## 6. Struktur Repository

```text
data/                       Corpus V1/V2, chunks, benchmark, snapshot
src/wo_retrieval/            Pipeline, retrieval, judgments, evaluator
scripts/                    Workflow dan verifikasi read-only
tests/                      Offline unit/integration tests
experiments/configs/        Protokol dan environment locks
experiments/indexes/        Indeks dan query vectors
experiments/human_judgments/ Input, history, provenance, exports
experiments/results/        Ranking dan evaluasi development
experiments/reports/        Laporan audit/milestone historis
experiments/portable/       Notebook dan input packages Colab
colab_exchange/             Transfer encoding historis
docs/                       Setup, reproduksibilitas, batasan
```

## 7. Instalasi

Target yang diperiksa: Windows x64, Python 3.12. URL clone mengikuti repository yang nanti diberikan peneliti; audit ini belum membuat repository GitHub.

```powershell
$repositoryUrl = Read-Host 'URL repository GitHub dari peneliti'
git clone $repositoryUrl wo-retrieval-benchmark
Set-Location wo-retrieval-benchmark
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -c docs/offline_constraints.txt -r experiments/configs/lexical_environment.lock.txt -e ".[lexical]" psutil==7.2.2
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import sys,docx,pypdf,openpyxl,numpy,scipy,sklearn,rank_bm25; print(sys.version)"
```

Instalasi memerlukan internet atau wheel cache yang sesuai. Model weights tidak disertakan dan tidak dibutuhkan oleh verifikasi berikut. Encoding ulang mempunyai persyaratan hardware, environment, dan cache khusus; lihat [setup](docs/setup.md).

## 8. Cara Menjalankan

```powershell
# Audit corpus, history, seluruh ranking, dan exact hasil evaluasi existing.
.\.venv\Scripts\python.exe scripts/verify_repository.py
# Top-10 empat metode untuk satu existing development query.
.\.venv\Scripts\python.exe scripts/verify_repository.py --query-id WO-DEV-001
# Kelengkapan penilaian, tanpa mengubah keputusan.
.\.venv\Scripts\python.exe scripts/human_annotation.py status
```

Verification script membaca artefak dan melakukan retrieval CPU dari cache; tidak membangun indeks, menulis ranking, atau membuat embedding. Hanya existing development queries didukung cache ini.

Hasil existing: [ringkasan](experiments/results/human_development_evaluation/milestone_9a18_20261010/summary.md), [JSON](experiments/results/human_development_evaluation/milestone_9a18_20261010/evaluation.json), [CSV macro](experiments/results/human_development_evaluation/milestone_9a18_20261010/macro.csv), [Word](experiments/results/human_development_evaluation/milestone_9a18_20261010/development_metrics_report.docx).

Annotation: `.\.venv\Scripts\python.exe scripts/human_annotation.py serve --port 8765`, lalu buka `http://127.0.0.1:8765`; simpan dan hentikan dengan Ctrl+C. **Menyimpan keputusan menambah revisi history**; untuk latihan gunakan salinan terpisah. Jangan menjalankan `prepare` pada workspace existing. Evaluator dan output baru dijelaskan di [reproduksibilitas](docs/reproducibility.md).

## 9. Hasil Uji Coba Development

Macro-average 18 queries, dari output tervalidasi existing:

| Metode | P@5 | P@10 | MRR@10 | nDCG@5 pooled | nDCG@10 pooled |
|---|---:|---:|---:|---:|---:|
| R1 TF-IDF | 0.633333 | 0.494444 | 0.722222 | 0.486942 | 0.517324 |
| R2 BM25 | 0.622222 | 0.500000 | 0.784722 | 0.497634 | 0.524130 |
| R3 BGE-M3 Dense | 0.744444 | 0.577778 | 0.972222 | 0.646561 | 0.663459 |
| R4 Hybrid RRF | 0.711111 | 0.588889 | 0.944444 | 0.627933 | 0.646549 |

BGE-M3 Dense tertinggi pada empat dari lima metrik; Hybrid tertinggi pada Precision@10. Temuan ini deskriptif pada development set. Hybrid tidak selalu unggul; signifikansi statistik dan generalisasi belum diuji.

Relevansi biner: Grade ≥1. nDCG: gain `2^grade−1`, discount `log2(rank+1)`, ideal ranking dari seluruh assessed union Top-20 pool per query. Recall tidak dihitung karena jumlah seluruh chunk relevan dalam corpus tidak diketahui.

## 10. Batasan Penelitian

Corpus sintetis, 18 development queries, judgments satu peneliti, dan pooled nDCG. Di luar pool tetap unknown. Belum expert-validated atau independently validated. Kedua penilai AI pada pilot consistency audit tidak sepenuhnya terisolasi; agreement tidak menggantikan validasi manusia/praktisi. Lihat [batasan](docs/limitations.md).

## 11. Status Penelitian

Implementasi R1–R4, saved development retrieval, annotation workflow, dan pooled development evaluation selesai. **Evaluasi utama skripsi belum selesai.** Evaluation queries independen, split development/evaluation, review praktisi, dan protokol utama perlu disepakati bersama pembimbing sebelum dijalankan.

Disarankan GitHub **private** dengan dosen sebagai collaborator. Inventory historis ada di [audit 9A.19](experiments/reports/milestone_9a19_repository_cleanup_github_readiness.md); hasil regression dan readiness terbaru ada di [audit 9A.20](experiments/reports/milestone_9a20_final_github_readiness.md). Tidak ada Git init, commit, atau push pada milestone ini.

## 12. Peneliti

Muhammad Ivan Verdyansyah · Informatika — Universitas Primakara
