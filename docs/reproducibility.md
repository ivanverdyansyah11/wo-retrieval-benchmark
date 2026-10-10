# Reproduksibilitas development dan bukti penelitian

`scripts/verify_repository.py` memeriksa corpus V1/V2, frozen hash bindings, human history chain/completeness, retrieval existing dari cache, exact parity 72 ranking, dan exact JSON evaluasi. Tidak ada penulisan output penelitian atau model inference. README dan aturan Git tidak memengaruhi corpus/protokol.

## Artefak acuan

- Snapshot: `data/versions/v2_ai_corrected/validation/pilot_snapshot.json`; fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.
- Queries: `data/benchmark/development_queries_draft.jsonl`; metadata V1 historis dipertahankan, binding V2 melalui migrasi/qrels/annotation manifests.
- Ranking: `experiments/results/milestone_9a12_development_pilot/rankings.jsonl`, 72 runs; contoh Top-10 pada `top10.md`/`top10.csv`.
- Judgments: `experiments/human_judgments/development_v2/`; 654 current resolved records, 695 events termasuk revisi. History bukan current export.
- Official export: `experiments/human_judgments/development_v2/exports/researcher_reviewed_9a18_20261010/`.
- Evaluasi: `experiments/results/human_development_evaluation/milestone_9a18_20261010/`, JSON/CSV/Markdown/Word.

Hashes memeriksa integritas, bukan validitas domain/independensi penilai. Paths sumber impor asli merupakan provenance dan tidak berarti input historis tersedia dari clone.

## Evaluator dan Word

Baca output existing. Verification script menghitung dengan evaluator yang sama pada input/protokol existing hanya untuk exact comparison, tanpa benchmark baru atau output baru.

CLI berikut menerbitkan output baru; gunakan hanya ketika diperlukan secara eksplisit, pada salinan dengan folder target yang belum ada:

```powershell
.\.venv\Scripts\python.exe scripts/human_annotation.py evaluate --out experiments/results/human_development_evaluation/review_copy --word
```

Target wajib folder baru di bawah `human_development_evaluation`. Syarat: semua human records RESOLVED, scope development sama, semua Top-5/Top-10 dinilai, pooled IDCG positif. Word memerlukan python-docx. Audit ini menguji generator pada temporary file di luar working tree; tidak menerbitkan ulang hasil frozen.

Annotation server hanya bind localhost, bukan deployment multiuser. Menyimpan keputusan mengubah penelitian dan menambah revision history. Review dosen/praktisi perlu workspace/version penilaian terpisah. Backup impor, initial exports, AI assessments, alias mapping, dan disagreements dipertahankan.

## Publikasi

Kandidat menyertakan research evidence aktual; root `data.zip` dikecualikan sebagai transfer archive yang tidak dibutuhkan runtime dan tetap disimpan/hash-checked lokal. Query vectors/indeks V2 disertakan; weights, venv, cache, dan live server locks dikecualikan.

Folder utama belum memiliki Git/remote saat audit. Isolated candidate staging bukan actual clone dari commit/GitHub. Sebelum commit pertama, review daftar file, privasi, dan izin distribusi. Disarankan private repository dengan dosen sebagai collaborator; LICENSE publik tidak ditetapkan otomatis.
