# MILESTONE 9A.19 — SAFE REPOSITORY CLEANUP, DOCUMENTATION RESTRUCTURING & GITHUB READINESS

Tanggal audit: 10 Oktober 2026. Working tree aktual menjadi source of truth; isi root ZIP tidak diasumsikan sama. Audit selesai dalam scope non-destructive. Dokumentasi dan kandidat publikasi telah diperbaiki, tetapi **full regression/clean-clone readiness belum PASS**. Tidak ada commit, push, PR, deploy, tuning, perubahan judgments/protokol, atau GPU inference.

**SAFE TO COMMIT: BELUM direkomendasikan sebelum review blocker. SAFE TO PUSH: BELUM.** Folder utama belum menjadi Git repository; tests historis masih mengunci hash dokumentasi lama dan paths/environment asal. Jalur CPU development yang dibatasi pada artefak existing berhasil diverifikasi. Ini berbeda dari klaim seluruh repository/inference portable.

## 1. Kondisi awal dan inventory

Root tidak memiliki `.git`. `git status --short`, `git remote -v`, dan `git log -1 --oneline` mengembalikan fatal/exit 128. Tidak ada tracked files, remote, commits, atau history yang dapat diaudit. Statusnya bukan clean Git working tree. Tidak dilakukan Git init/reset/clean/amend pada folder utama.

Baseline mencatat 42.055 files, 5.040.773.414 bytes (4,695 GiB), termasuk virtual environments. Sebanyak 428 file di luar environment/generated metadata di-hash sebelum perubahan. Rincian per file, kategori, ukuran, hash, dan tindakan terdapat pada [cleanup_inventory.csv](../results/milestone_9a19_repository_readiness/cleanup_inventory.csv); [baseline hashes](../results/milestone_9a19_repository_readiness/baseline.json) dan [folder sizes](../results/milestone_9a19_repository_readiness/size_baseline.json) disertakan.

| Kategori inventory | Jumlah awal / kelompok | Keputusan |
|---|---:|---|
| ESSENTIAL | 38 | Source modules dipertahankan; tidak di-refactor |
| RESEARCH EVIDENCE | 288 | Corpus, chunks, indeks, judgments/history, ranking, results/manifests dilindungi |
| REPRODUCIBILITY | 36 | Scripts, tests, configs/locks, portable packages dipertahankan |
| DOCUMENTATION | 58 | Laporan lama dipertahankan; README diperbarui |
| GENERATED / TEMPORARY | 4 kelompok | Venv, bytecode, egg-info dikecualikan Git; tetap lokal |
| ARCHIVE / OPTIONAL | 2 | Root ZIP di-ignore; transfer encoding tetap tersedia |
| SENSITIVE / REVIEW REQUIRED | 6 | Private alias/old label comparison dan incoming import evidence tetap tersedia; review akses diperlukan |

Jumlah kategori ini merupakan file/kelompok baseline, bukan jumlah final setelah artefak audit baru. Privacy flags lintas kategori ditampilkan terpisah. Installed package contents diwakili kelompok environment; seluruhnya sudah dihitung ukuran, tidak dibagikan sebagai ribuan baris inventory Git. [cleanup_summary.json](../results/milestone_9a19_repository_readiness/cleanup_summary.json) mencatat tujuh kategori dan nol removal/move.

## 2. Kandidat cleanup dan alasan

| Kandidat | Ukuran baseline | Penggunaan / dampak | Tindakan |
|---|---:|---|---|
| `.venv/` | 29.292.118 bytes | Interpreter/dependencies lokal; dapat diinstal ulang. Menghapusnya mengganggu workflow lokal | Ignore; tidak dihapus |
| `.venv-ml/` | 4.952.539.301 bytes | Environment ML/provenance lama; beberapa tests memerlukannya | Tambah ignore; tetap lokal |
| `__pycache__/`, bytecode project | 110.742 bytes | Generated; bukan input retrieval | Ignore existing; tetap lokal |
| `src/wo_retrieval_benchmark.egg-info/` | Lihat inventory | Generated packaging metadata; beberapa integrity reports lama justru mengikat hashes file ini | Ignore existing; tetap lokal; empat file dipulihkan setelah install sementara |
| Root `data.zip` | 11.999.271 bytes | Transfer archive berisi working tree historis; pencarian source/scripts tidak menemukan runtime reference. Tidak diperlukan jalur CPU baru | Ignore path exact; retain/hash lokal |
| `colab_exchange/v2/bge_m3_v2_full_embeddings.zip` | 1.513.420 bytes | Exchange encoding/import historis; evidence reproducibility | Retain dan sertakan kandidat |
| `experiments/portable/` | 159.688 bytes | Notebook/input packages historis; full loader memerlukan full input ZIP | Retain; kedua notebook tidak memiliki outputs/execution counts |
| `experiments/results/` | 13.969.966 bytes | Hasil, receipts, hashes, rankings; audit human bergantung pada outputs 9A.12–9A.15 | Retain seluruh existing results |
| `experiments/reports/` | 1.020.438 bytes | Laporan/protokol historis | Retain; tidak mengedit laporan lama |
| `experiments/human_judgments/` | 5.248.466 bytes | Input, 695 history events, current records, official exports/provenance | Retain; jangan menghapus history |
| Backup impor `workspace_backup/` | 2.640.554 bytes | Recovery dan bukti state sebelum impor | Retain; tidak dipindah/dihapus |
| Root `pilot_second_assessments.jsonl` | 78.894 bytes | Assessment provenance; masih terikat audit second assessor | Retain; tidak dianggap temporary sembarangan |

Tidak ada broad ignore untuk `data/`, `experiments/`, JSONL, NPY/NPZ, ZIP, CSV, atau seluruh logs. Logs penelitian/manifests yang mengikatnya tetap tersedia. Tidak ada model weights Hugging Face yang dipilih untuk kandidat. Folder cache/model lokal yang dapat dibuat kemudian dibatasi root-only dalam ignore.

## 3. Perubahan konkret

File existing yang berubah hanya:

- `README.md`: 12 bagian berbahasa Indonesia, judul locked/identitas benar, kondisi V2 dan human development evaluation aktual, metrik actual output, batasan/prasyarat jelas.
- `.gitignore`: tambah `.venv-ml`, secrets/env, cache/IDE/OS/checkpoints, root local directories/download residue, root `data.zip`, exact annotation live lock paths. Tidak menyembunyikan research evidence actual.

File dokumentasi/verifikasi baru:

- `docs/setup.md`
- `docs/reproducibility.md`
- `docs/limitations.md`
- `docs/offline_constraints.txt`
- `scripts/verify_repository.py`
- Laporan ini.

Evidence audit baru berada hanya di `experiments/results/milestone_9a19_repository_readiness/`. [Final file manifest](../results/milestone_9a19_repository_readiness/final_manifest.json) mencatat **exact seluruh file baru/berubah** beserta hashes, termasuk logs, inventory, security/privacy summaries, test summaries, parity output, dan final publication candidate listing. Manifest mengecualikan hash dirinya untuk menghindari circular hash; report tidak diubah lagi sesudah manifest final.

**Removed: 0. Moved: 0.** Seluruh source/config/tests existing, data, embedding matrices, query vectors, rankings, qrels, grade assessments, judgments/history, dan laporan existing dipertahankan byte-for-byte.

Pip editable installation awal pada temporary environment sempat meregenerasi empat egg-info files di root source tree. File tersebut dikembalikan dari archive **hanya setelah bytes archive cocok dengan hashes historis**. Net perubahan metadata menjadi nol. Archive tidak dipakai untuk menyimpulkan working tree dataset sama; hanya sebagai sumber recovery empat generated files yang diverifikasi exact. [Receipt](../results/milestone_9a19_repository_readiness/restored_generated_metadata.json).

## 4. Git dan efek ignore

Karena root bukan Git repository, `git check-ignore` dan Git status tidak dapat memeriksa tracked/untracked primary. Temporary candidate dibuat pada `D:/ModelCache/tmp/wo-m9a19/publication_candidate`; Git init hanya pada folder baru terisolasi untuk menerapkan ignore rules. Tidak ada commit, staging index, remote, atau push. Seluruh chosen files pada kandidat berstatus untracked; keberadaan kandidat tidak membuat primary memiliki Git.

`git check-ignore --no-index --stdin` dijalankan pada kandidat. Dari 428 baseline non-generated files dan lima additions awal, satu file existing yang dikecualikan adalah root `data.zip`. Paths env/bytecode/secrets/model-cache/server-lock diuji dengan `check-ignore -v`. `git ls-files --others --exclude-standard` dibandingkan exact dengan daftar file yang disalin. Frozen annotation source hashes tetap tersedia; tidak ada research runtime asset yang di-ignore. [Initial candidate inventory/rules](../results/milestone_9a19_repository_readiness/candidate.json), [final candidate availability](../results/milestone_9a19_repository_readiness/final_candidate.json).

`git diff --check` primary tidak tersedia (exit 129, bukan PASS). Alternatif actual adalah `git diff --no-index --check` untuk README/.gitignore terhadap baseline; exit 1 karena terdapat perubahan, tanpa whitespace diagnostic. File baru diperiksa terhadap empty file serta pemeriksaan trailing whitespace; tidak ada whitespace issue. Review seluruh perubahan dilakukan terhadap baseline hashes/file list, bukan klaim staged Git diff.

## 5. Baseline dan regression tests

Baseline sebelum edit:

```powershell
$env:PYTHONPATH = (Join-Path $PWD 'src')
$env:PYTHONIOENCODING = 'utf-8'
.venv\Scripts\python.exe D:\ModelCache\tmp\wo-m9a19\tests.py baseline base
.venv-ml\Scripts\python.exe D:\ModelCache\tmp\wo-m9a19\tests.py baseline ml
```

Harness menggunakan unittest loader dan membagi semua existing modules karena dua environment asal berbeda. [Baseline base](../results/milestone_9a19_repository_readiness/baseline_base.json): 64 tests, exit 0; [baseline ML](../results/milestone_9a19_repository_readiness/baseline_ml.json): 132 tests, exit 0. Total **196 PASS**, 0 failure/error/skipped; Torch tidak diimpor. Log fixture “embedded” tidak merupakan GPU encoding nyata.

Sesudah perubahan, command yang sama dijalankan dengan phase `post`. Kelompok base tetap **64 PASS**, exit 0. Kelompok ML **132 dijalankan, 0 failures, 3 errors**, exit 1. Setelah generated metadata dipulihkan, ML suite dijalankan lagi (`post_restored ml`) dan tiga errors tetap ada, kini **hanya README/.gitignore hashes**:

1. `test_development_pilot.PublishedPilotTests.test_outputs_and_version_isolation`.
2. `test_judgment_pool.PublishedPoolTests.test_previous_outputs_and_protected_artifacts`.
3. `test_pilot_assessment_audit.PublishedAuditTests.test_actual_preflight_and_flags`.

Ini **regression dari perubahan dokumentasi/ignore yang diminta**, bukan kegagalan baseline. Historical integrity fixtures memeriksa snapshot seluruh working tree lama termasuk dokumentasi mutable/egg-info dan absolute original paths. Tidak dilakukan whitelist palsu, patch tests, atau perubahan protected historical manifests. Full post-suite bukan PASS. Evidence: [post base](../results/milestone_9a19_repository_readiness/post_base.json), [post restored ML](../results/milestone_9a19_repository_readiness/post_restored_ml.json), [detail errors](../results/milestone_9a19_repository_readiness/post_restored_ml.log).

Menyelesaikan regression secara permanen memerlukan keputusan scope terpisah untuk memisahkan historical snapshot evidence dari current mutable documentation dalam integrity checks/tests. Tidak dilakukan pada milestone ini karena perubahan source/tests/protected evidence dibatasi.

## 6. Integritas penelitian dan pemeriksaan operasional

[Protected integrity](../results/milestone_9a19_repository_readiness/protected_integrity.json): **426/426 baseline non-generated protected files exact**, 0 missing/changed; dua pengecualian authorized ialah README/.gitignore. Root archive termasuk baseline protected lokal walau tidak dipublikasikan. Existing source, scripts, tests, configs/locks, seluruh reports/results, V1/V2, assessments, history, exports, dan indeks termasuk pemeriksaan.

[Working verification](../results/milestone_9a19_repository_readiness/working_verification.json) dan [candidate verification](../results/milestone_9a19_repository_readiness/candidate_verification.json) benar-benar dieksekusi:

- Corpus audits V1/V2: masing-masing 50 documents, format 26/9/10/5, 0 errors. V1 mengeluarkan notice README packaging hash historis berbeda; ini memang ditangani auditor existing, immutable corpus tetap valid.
- Frozen V1/V2 snapshots, V2 source hashes, 371 chunks, 18 query bindings dan AI silver qrels diverifikasi oleh validator existing.
- Annotation package: 194 frozen source hashes, history chain/provenance valid, 695 events, 654 current records; seluruh RESOLVED, missing/unresolved 0; grade 429/152/73.
- R1/R2 verified loaders memakai indeks existing; R3 matrix/query vector contract hashes dan row mapping diperiksa; R4 memakai implementation/protocol existing.
- Seluruh **72 full ranking** dibandingkan exact pada ID, rank, document, score tanpa rounding, method, snapshot. Top-10 empat metode untuk `WO-DEV-001` tersedia pada output verification. Tidak ada ranking ditulis ulang.
- Evaluator existing dihitung di memori dengan data/protokol yang sama; **seluruh result object cocok exact** dengan saved `evaluation.json`, bukan baseline angka hardcoded.
- Torch tidak diimpor; tidak ada BGEEncoder/model initialization, tokenizer loading, model download, atau GPU inference pada jalur verification.
- Semua 62 existing/new Python source files berhasil AST parse. Import checks pada fresh CPU environment berhasil.
- Verification script mempunyai negative self-check: perubahan score retrieval di memori ditolak, query ID baru ditolak, model loading diberi guard yang akan gagal jika dipanggil. [Self-check](../results/milestone_9a19_repository_readiness/verification_selfcheck.json).

Word generator existing dijalankan pada temporary file di luar repository menggunakan actual saved result; DOCX terbaca, 22 tables, formatted macro cells exact. Output Word frozen tidak diubah. Audit ini tidak melakukan rendering visual ulang dokumen temporary; validasi layout historis bukan diklaim sebagai pemeriksaan baru.

## 7. Clean candidate setup dan keterbatasan

Kandidat disusun berdasarkan **files yang lolos ignore**, bukan memakai working tree lama beserta venv. Fresh `.venv` dibuat di kandidat. Perintah instalasi README benar-benar dijalankan dari root kandidat dengan constraints ingestion/lexical/CPU dan editable package; exit 0. Instalasi pertama pada isolated CPU env memakai network download dari package index; instalasi kandidat berikutnya memakai cached wheels dan editable build. Network/build dependencies benar-benar diakses; bukan hanya analisis requirements.

`pip check`, imports ingestion/lexical, human `status`, dan verification/Top-10 masing-masing exit 0. CPU environment tidak memiliki Torch/FlagEmbedding, dan verification berjalan tanpa historical ML installation/cache. Source entry points/config paths tersedia. [Checks/commands](../results/milestone_9a19_repository_readiness/candidate_checks.json).

All-test discovery kandidat dijalankan: **188 tests executed, 0 failures, 4 errors**, exit 1. Satu `setUpClass(FullColabTests)` error berasal dari metadata Torch yang tidak tersedia pada CPU-only setup; delapan tests kelas tersebut tidak dijalankan. Tiga errors lain berasal dari old absolute-path/historical whole-tree integrity checks. Beberapa tests historis masih membaca primary/external cache, sehingga keberhasilannya di kandidat **bukan bukti isolasi semua tests**. New verification path tidak bergantung pada checks/cache tersebut.

**Status:** portable cached-development path PASS pada isolated publication candidate; whole-suite clean-clone readiness FAIL/conditional. Ini bukan actual `git clone` dari commit/remote karena primary tidak memiliki Git/remote. `git clone` URL nyata belum dapat diuji. Linux/macOS, inference ulang, dan reviewer perangkat lain belum diverifikasi. Tidak dipasang environment GPU atau weights untuk menyembunyikan batasan ini.

Percobaan awal candidate copy berhenti pada assertion ignore karena stdin Git Windows memerlukan LF tanpa text-mode CRLF conversion. Diperbaiki hanya pada temporary harness. Pip berikutnya sempat gagal karena candidate belum lengkap; setelah exact copy berhasil, perintah README diulang dan exit 0. Tidak ada failure percobaan yang dinyatakan PASS.

## 8. Hasil development yang tetap sama

| Method | P@5 | P@10 | MRR@10 | nDCG@5 pooled | nDCG@10 pooled |
|---|---:|---:|---:|---:|---:|
| TF-IDF | 0.633333 | 0.494444 | 0.722222 | 0.486942 | 0.517324 |
| BM25 | 0.622222 | 0.500000 | 0.784722 | 0.497634 | 0.524130 |
| BGE-M3 Dense | 0.744444 | 0.577778 | 0.972222 | 0.646561 | 0.663459 |
| Hybrid RRF | 0.711111 | 0.588889 | 0.944444 | 0.627933 | 0.646549 |

Tabel disalin dari actual validated JSON; parity memeriksa seluruh precision data/provenance, bukan enam digit tabel. Dense tertinggi empat dari lima metrik; Hybrid tertinggi P@10. Ini development dengan satu peneliti, bukan efektivitas final/signifikansi. Synthetic corpus, pooled IDCG, development split, assessor independensi, dan main evaluation pending dijelaskan di README dan docs/limitations.md.

## 9. Secret, privacy, binary, dan lisensi

[Security summary](../results/milestone_9a19_repository_readiness/security.json): 2.672 text members diperiksa dari files/ZIP/Office XML/PDF text/metadata/notebooks, termasuk archive lokal yang di-ignore. Pola private keys, GitHub/HF/OpenAI/AWS keys, credential assignments, dan credential URLs tidak menghasilkan secret candidates. Tidak ada `.env` actual dipilih untuk kandidat. Ini automated pattern/content audit, bukan jaminan tidak ada arbitrary secret atau audit keseluruhan dependencies/virtualenv yang tidak dipublikasikan. Git history tidak bisa diperiksa karena tidak tersedia.

136 text members memuat paths perangkat asal; 112 broad contact candidates ternyata termasuk numeric/hash false positives. Pemeriksaan parser atas **100 source documents V1/V2** menemukan 0 email/phone candidates; author metadata yang teramati adalah organisasi sintetis/draft peneliti/peneliti/openpyxl. [Source privacy details](../results/milestone_9a19_repository_readiness/privacy_details.json). Kedua notebook memiliki 0 outputs dan 0 execution counts. Source corpus tidak disanitasi atau diubah.

Review sebelum public tetap diperlukan untuk nama peneliti, notes, timestamps/history, import paths, binary author/last-modifier metadata, private assessor alias mapping/old labels, dan dokumen/laporan historis. “Private” pada alias mapping adalah research blinding provenance, bukan bukti secret/token; tetap tidak layak diabaikan saat memutuskan audience. Jangan menghapus bukti frozen untuk sanitasi tanpa versioning/approval.

Tidak ada LICENSE repository terdeteksi. Tidak memilih lisensi publik otomatis dan tidak menyimpulkan izin redistribusi model/dependencies dari keberhasilan pip. Model weights tidak didistribusikan; apabila kelak ditambahkan, review license/revision/syarat distribusinya terpisah. Rekomendasi awal: **GitHub private, dosen sebagai collaborator**; keputusan public dan lisensi perlu peneliti/pembimbing.

Ukuran kandidat sebelum evidence 9A.19: **432 files, 46.828.163 bytes (44,659 MiB)**. Final inventory dengan report/evidence tersedia pada final_candidate.json. File terbesar adalah saved rankings, **7.362.402 bytes (7,021 MiB)**. Seluruh candidate files jauh di bawah 50 MiB. GitHub memberi warning di atas 50 MiB dan memblokir file di atas 100 MiB menurut [dokumentasi GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). `.venv-ml` sekitar 4,6 GiB tidak boleh masuk publikasi; ignore dibuktikan pada kandidat, bukan diasumsikan tracked removal. Tidak ada disk space dibebaskan karena cleanup tidak menghapus data/environment.

## 10. Remaining blockers dan keputusan review

1. Primary belum memiliki Git repository/remote/commit. Inisialisasi pertama dan pemilihan remote dilakukan setelah review, bukan milestone ini.
2. Tiga post-regression errors mengikat mutable README/.gitignore pada historical manifests. Penyelesaian membutuhkan scope baru untuk integrity checks/tests; protected reports tidak boleh ditulis ulang agar PASS.
3. Full Colab integration test setup memerlukan historical ML environment/cache/implementation hashes; full inference dan whole-suite clean clone belum portable. Jalur CPU cached development sudah diuji secara terpisah.
4. Keputusan audience, privacy/provenance, dan license/redistribution belum disetujui untuk public. Backup/alias/history tidak dihapus.
5. Actual remote clone/push, platform lain, dan perangkat dosen belum diuji. Research main evaluation/domain/expert/independent validation tetap pending.

**Target audit:** MILESTONE 9A.19 — REPOSITORY CLEANUP COMPLETE, GITHUB READINESS AUDITED, dengan blockers terdokumentasi. “Cleanup complete” berarti cleanup aman berupa aturan publikasi dan dokumentasi selesai; bukan semua tests PASS atau izin push. **SAFE TO COMMIT/PUSH: BELUM** sampai review blocker dan scope lanjut disepakati. Pekerjaan dihentikan sesudah audit, cleanup aman, laporan, dan verifikasi ini.
