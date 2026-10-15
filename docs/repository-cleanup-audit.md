# Audit cleanup repository — 15 Oktober 2026

Keputusan: **SAFE TO PUSH untuk allowlist 13 file yang ditentukan di bawah**,
sesudah review pengguna. Seluruh pending working tree belum dinyatakan aman untuk
dipublikasikan. Tidak ada staging, commit, push, PR, merge atau deployment.

Cleanup dilakukan dengan aturan ignore yang terarah. **Tidak ada file yang
dihapus**, tidak ada `git rm --cached`, dan tidak ada baseline/checksum penelitian
yang ditulis ulang. Branch aktif dipisahkan menjadi
`codex/e5-repository-cleanup`; HEAD dan referensi `main` tetap pada commit semula.

## Sebelum dan sesudah

Inventaris menggunakan `git status --porcelain=v1 --untracked-files=all -z`,
`git ls-files -z`, `git check-ignore`, dan walk filesystem tanpa mengikuti
junction/symlink ke luar workspace. Staged adalah hitungan tersendiri; tidak
ditambahkan lagi ke jumlah total status karena dapat beririsan dengan modified.

| Ukuran | Sebelum | Sesudah, termasuk laporan baru ini |
|---|---:|---:|
| Entri Git status | **19.012** | **719** |
| Tracked modified | 2 | 2 |
| Tracked deleted | 0 | 0 |
| Staged | 0 | 0 |
| Untracked nonignored | 19.010 | 717 |
| File tracked keseluruhan | 489 | 489 |

Dua tracked modified adalah `.gitignore` dan README yang sudah berubah sebelum
cleanup. README tidak disentuh pekerjaan ini dan tidak dipilih untuk commit.
Total sesudah sebelum laporan ditambahkan adalah 718; laporan baru menambah satu
untracked. **18.294 path lama kini ignored**, tanpa penghapusan. Penurunan bersih
status adalah 18.293 entri karena ada tambahan laporan ini.

Penyebab utama angka puluhan ribu adalah **empat directory junction
`_support/node_modules`**, masing-masing menampilkan 4.465 path Git. Keempatnya
mengarah ke satu runtime dependency bersama di luar repository. Itu **17.860
entri virtual yang berulang**, bukan 17.860 perubahan source penelitian.
Junction dan targetnya tidak dihapus atau diubah.

| Kelompok yang baru diabaikan | Path Git lama |
|---|---:|
| Dependency Node melalui empat junction | 17.860 |
| Cache embedding E5 historis lokal, tetap disimpan | 384 |
| Receipt portabilitas lokal v1/v2 | 3 |
| Workspace review aktif dan prototype integration privat | 39 |
| Preview PNG dan inspection NDJSON workbook | 7 |
| Duplikat arsip transfer `src.zip`, tetap disimpan | 1 |
| **Total** | **18.294** |

Angka cache/dependency berbeda dari angka artefak penelitian: 384 cache E5 tetap
dianggap artefak riset yang perlu dipreservasi. Ignore hanya mengecualikannya dari
seleksi publikasi otomatis, bukan menyatakan isinya boleh dibuang.

## Klasifikasi A–G

Klasifikasi berikut mencakup **19.499 path unik** dalam gabungan 489 tracked dan
19.010 untracked awal. Flag protected dan sensitive-review dicatat terpisah;
misalnya source dapat berkategori A sekaligus terlindungi inventaris hash.

| Kategori | Jumlah | Perlakuan |
|---|---:|---|
| A — source dan dependency/configuration | 143 | Source, scripts, konfigurasi eksperimen dan lock tetap tersedia. |
| B — tests dan fixtures | 49 | Dipertahankan; tidak ada ignore folder tests. |
| C — dokumentasi akademik/teknis | 140 | README, docs, laporan dan dokumen bimbingan tetap disimpan; bukan seluruhnya otomatis dipublikasikan. |
| D — corpus/qrels/indices/evidence/artefak riset | 1.267 | Tidak dihapus atau ditulis ulang; sebagian cache lokal dikecualikan dari publikasi otomatis. |
| E — dependency/cache/generated | 17.860 | Empat junction Node pada daftar Git awal; venv/cache yang sudah ignored dihitung pada inventaris fisik terpisah. |
| F — workspace lokal sensitif | 39 | Review manusia/prototype lokal dikecualikan dari publikasi; isinya dipertahankan. |
| G — redundant terverifikasi | 1 | `src.zip`: 138/138 entry cocok byte dengan file yang masih ada. Tetap disimpan; tidak perlu dihapus untuk merapikan Git. |

Walk filesystem awal menemukan 51.763 file lokal, empat junction, dan tidak ada
error baca metadata. `.git` tidak ditelusuri sebagai data workspace dan target
junction eksternal tidak dihitung ulang. Venv ML sekitar 4,95 GB logical bytes,
cache workspace sekitar 747 MB, dan experiments sekitar 3,43 GB. Nilai itu
logical file sizes, bukan ukuran disk fisik atau rekomendasi menghapus cache.
Tree lengkap, klasifikasi per path, dan metadata disimpan lokal di
`.cache/repository_cleanup_20261015/`.

## Perubahan .gitignore

Aturan lama dipertahankan, termasuk perubahan pengguna yang sudah ada sebelumnya.
Tambahan dibatasi berdasarkan struktur yang benar-benar ditemukan:

- `node_modules/` untuk dependency JavaScript, termasuk directory junction.
- `.venv-*/` untuk venv khusus dengan prefix yang jelas.
- Path spesifik cache lokal E5 v1, inference lock, dan output portabilitas v1/v2.
- Tiga workspace review aktif di `experiments/main_evaluation/` dan satu workspace
  prototype E5 lokal, tanpa mengabaikan seluruh main_evaluation atau experiments.
- `/src.zip` yang sudah diverifikasi redundant, tanpa menghapus arsip.
- Preview PNG dan inspection NDJSON hanya untuk workbook di folder outputs yang
  ditemukan. **XLSX yang dirujuk dokumentasi dan verification receipt tetap ada**.

Aturan yang sudah ada mencakup bytecode, venv utama, pytest/mypy/ruff/coverage,
notebook checkpoints, cache/download model, temp/download parsial, `.env` dan
file IDE. Tidak ditambahkan global-ignore weights atau JSON/NPY: file model yang
ditemukan berada pada cache khusus yang sudah ignored; indeks ilmiah dan fixtures
harus tetap dapat direview. Log/evidence penelitian tidak disembunyikan secara
massal hanya karena berekstensi `.log` atau `.json`.

Tidak ada ignore seluruh `src/`, `scripts/`, `tests/`, `docs/`, `experiments/`,
atau `data/`. Tidak ada global-ignore `*.json`, `*.md`, `*.pdf`, `*.npy`,
`*.toml`, atau `*.lock`. `requirements.lock` serta seluruh lock/config dependency
E5 tetap dapat dipilih untuk publikasi. Ignore tidak mengeluarkan file tracked
dari index maupun sejarah Git.

## Preservasi dan file yang dihapus

| Pemeriksaan | Hasil |
|---|---|
| Inventaris awal 1.082 file terhadap baseline lama | PASS: 1.082 identik sebelum cleanup. |
| Perbandingan sesudah cleanup | **1.081 byte-identical; satu perubahan `.gitignore` yang diotorisasi pengguna.** |
| Kesetaraan byte ketat seluruh 1.082 sesudah perubahan | Tidak terpenuhi, hanya karena `.gitignore`; tidak dinyatakan 1.082/1.082 identik. |
| Perubahan penelitian/source/config lain dalam inventaris | PASS: 0 unexpected changes dan 0 missing. |
| Original 11 file allowlist E5 v2 | PASS: seluruh hash lama tetap cocok. |
| Set tracked dan commit historis | PASS: 489 path tracked tetap sama; HEAD dan main tidak berubah. |
| File yang dihapus | **0**. |

Pemeriksaan keberadaan ulang juga menemukan **51.763/51.763 file fisik awal
tetap tersedia** dan target keempat junction tetap sama. Pemeriksaan ini menguji
keberadaan, sedangkan kesetaraan byte penelitian dibuktikan oleh inventaris hash.

`.gitignore` memang termasuk inventaris 1.082 file. Izin eksplisit pengguna untuk
memperbaikinya diperlakukan sebagai pengecualian khusus konfigurasi Git. Baseline
penelitian tidak diganti untuk menyamarkan perbedaan ini. Salinan `.gitignore`
sebelum cleanup disimpan di `.cache/repository_cleanup_20261015/gitignore_before.txt`.

Frozen corpus, annotations, human history, qrels, ground truth, indeks, model
snapshot, checkpoint, artefak benchmark, arsip backup, dokumen akademik dan semua
file yang belum diketahui fungsinya tetap dipertahankan. Dokumen kuesioner yang
dirujuk `docs/rag_user_evaluation.md` tidak dihapus atau diabaikan sebagai workbook.

Review docs sebelum laporan ini: 22 file, tidak ditemukan pasangan dengan hash
isi identik. Panduan E5 lama dan v2 menjelaskan tahap berbeda; rekomendasinya
adalah menambah navigasi/version notice kelak dengan izin terpisah, bukan
menghapus dokumen. Tidak ada penghapusan/merge docs pada cleanup ini.

## Validasi dan keamanan publikasi

| Pemeriksaan aktual | Status dan cakupan |
|---|---|
| Compile Python | PASS: 155 file src/scripts/tests, 0 error. |
| Regresi relevan | PASS: 162 tests, 0 failure/error/skip. Unit/mock dan validasi artefak; tidak ada model inference baru. |
| Fresh import E5 v2 | PASS: tidak memuat torch/transformers, encoder/recovery historis, atau ctypes pada import. |
| Git status/ls-files sebelum dan sesudah | PASS: tidak ada tracked deleted, staging, atau perubahan set tracked. |
| Ignore rule checks | PASS: 54 checks menggunakan `git check-ignore --no-index -z --stdin`, termasuk expected-ignored dan expected-visible untuk source, evidence, fixtures, `.env.example` dan lock. Framing NUL mencegah CRLF Windows dianggap bagian nama path. |
| Credential/privacy review | PASS terbatas: 1.058 file text first-party tracked dan untracked awal dipindai, 0 pola secret terdeteksi, 0 kandidat filename credentials. Nilai secret tidak dicetak. Directory dependency eksternal, bytes model dan binary besar tidak diperlakukan sebagai source publik; bukan audit PII/history lengkap. |
| Original 11 file E5 | Hash dibandingkan dan pola ignore diperiksa ulang; tidak tertimpa atau tersembunyi. |
| Linux/Kaggle dan full-corpus inference | NOT TESTED pada cleanup; tidak ada klaim keberhasilan baru. |

Scan token dan filename tidak membuktikan seluruh data bebas identitas atau
bahwa lisensi/izin redistribusi dataset sudah dipenuhi. File tracked historis
yang memuat provenance atau qrels tidak dihapus dari Git secara otomatis.
Dokumen bimbingan, assessor history, arsip backup dan workspace lokal di luar
allowlist tetap memerlukan review terpisah sebelum publikasi.

## File yang aman dipilih untuk commit

Daftar final adalah **11 path persis** dari
`experiments/reports/e5_readiness_v2_20261015/publication_allowlist.json`, ditambah:

1. `.gitignore` dengan perubahan cleanup ini.
2. `docs/repository-cleanup-audit.md`.

Total **13 file**: runtime/runner/tests v2, dokumen readiness v2, tujuh file
bundle dependency/snapshot/panduan E5, aturan ignore dan laporan cleanup.
Allowlist baru dengan ukuran/hash tersedia lokal di
`.cache/repository_cleanup_20261015/publication_allowlist.json`.
README yang sudah modified dan ratusan artefak untracked lainnya tidak termasuk
izin publikasi otomatis.

**SAFE TO PUSH terbatas pada 13 file allowlist setelah review pengguna.** Source
Control yang tersisa tetap memperlihatkan dokumen/source/artefak penelitian yang
perlu dipilih secara sadar. Seluruh working tree belum diberi keputusan aman
untuk commit massal. Jangan memakai stage-all untuk menggantikan review daftar.

Bukti lokal: `cleanup_summary.json`, `git_status_before.json`,
`git_status_after.json`, `inventory_summary.json`, `filesystem_inventory.json`,
`git_classification.json`, `integrity_before.json`, `integrity_after.json`,
`source_archive_review.json`, `documentation_review.json`, `tests.json/.log`,
`compile.json`, `ignore_checks.json`, `security_scan.json` dan allowlist baru di
`.cache/repository_cleanup_20261015/`. Folder audit mentah ini ignored agar detail
lokal tidak ikut publikasi. Agen tidak melakukan tindakan publikasi Git.
