# Readiness E5 alternatif v2 — 15 Oktober 2026

Dokumen ini memperbarui status E5 untuk review branch eksperimen. Atas pilihan
pengguna, **seluruh 1.082 file dalam inventaris audit awal dipertahankan identik**.
README dan panduan lama tidak disunting; pernyataan lama bahwa full-corpus E5
belum tersedia sudah tidak mencerminkan cache yang diverifikasi pada 15 Oktober.
Pemeriksaan rinci inventaris menunjukkan README dilindungi, sedangkan panduan
`docs/embedding_cpu_profiles.md` di luar inventaris tersebut; keduanya tetap utuh.

## Keadaan penelitian yang harus dibedakan

| Jalur | Keadaan terverifikasi |
|---|---|
| BGE-M3 historis | Dipertahankan: revision `5617a9f61b028005a4858fdac845db406aefb181`, 640 token, batch 1, 1024 dimensi, CLS, CUDA FP16 lalu storage float32/L2. Bukan default v2 dan tidak diubah. |
| E5 v1 alternatif | Revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`, 256 token, batch 1, CPU FP32, 384 dimensi, prefix query/passage, mean pooling dengan attention mask, L2. Cache lengkap **(371,384)** sudah tersimpan. |
| Development E5 lama | Hasil **18 query** tersedia di namespace recovery_v2. Audit memeriksa checksum 11 artifact hasil dan mengulang scoring dari vektor tersimpan: **54/54 ranking** BM25/Dense_E5/Hybrid_E5 cocok tepat. Ini verifikasi cache, bukan 18 inference baru. |
| Smoke aktual audit pertama | Tepat satu query pendek benar-benar di-encode pada Windows: **(1,384), CPU FP32, finite, norm 1.0**. Tidak ada inference passage/corpus baru pada pekerjaan readiness ini. |
| Truncation | Tokenizer ulang cocok dengan receipt lama: **55/371 chunk (14,8248%)**, 10.992 token dibuang (15,0765% total); 18 query lama tidak terpotong. Dampak kualitas kausal belum diuji. E5 256 tidak dinyatakan setara kualitasnya dengan BGE 640. Posisi maksimum E5 adalah 512; angka overflow pada 640 hanya diagnostik. |
| E5 portable v2 | Encoder dan CLI baru terpisah dari encoder/recovery historis. Source dan unit/mock Windows telah diuji; snapshot aktual diperiksa. Inference v2 dalam CPU-only environment baru belum dijalankan. |
| Linux/Kaggle | Native Linux clean install, notebook Kaggle, dan smoke model v2 di target **NOT TESTED**. WSL terdaftar tetapi start **BLOCKED** oleh disk yang dirujuk tidak ditemukan. Penyebab kegagalan Kaggle pengguna tetap belum diketahui. |
| Pipeline penelitian end-to-end | Full-corpus v2, evaluasi utama dan pipeline RAG end-to-end **NOT TESTED** dalam pekerjaan ini. Tidak ada klaim hasil utama baru. |

## Perbaikan yang tersedia

| Temuan awal | Perbaikan dan file baru | Status |
|---|---|---|
| Recovery membutuhkan API Windows | `src/wo_retrieval/e5_portable_v2.py` dan `scripts/e5_portable_v2.py` berdiri sendiri. Tidak mengimpor historical encoder, recovery, dense/BGE atau ctypes. Recovery Windows lama tetap utuh dan khusus Windows. | PASS static/import/unit Windows; native Linux NOT TESTED |
| Partial cache menutupi snapshot lengkap | V2 mencoba semua kandidat, melewati kandidat parsial/korup dan mencatat alasan penolakan. Snapshot eksplisit yang salah langsung ditolak. | PASS regression tests |
| Cache custom tidak dihormati | HF_HUB_CACHE, HF_HOME, XDG_CACHE_HOME, default home, workspace; lokasi D: lama hanya kandidat tambahan pada Windows. | PASS tests; actual workspace snapshot PASS |
| Snapshot/revision/provenance | Keenam file wajib sesuai SHA256, nama direktori revision benar, config 384 dan 512 posisi. Verifikasi sebelum load; load offline, safetensors, trust_remote_code=False. | PASS actual snapshot inspection + rejection tests |
| Dependency E5 bercampur BGE/CUDA | Bundle v2 hanya E5; torch **2.12.1+cpu** wajib. Stack nvidia/FlagEmbedding/datasets/ir-datasets/sentence-transformers/peft ditolak. Tidak perlu lexical/scipy/sklearn. `pyproject.toml` historis tidak diubah; instalasi E5 melalui bundle mandiri. | PASS gate tests; local legacy ML environment BLOCKED sesuai desain |
| Reproducibility dependency Linux | Resolusi wheel cp312 Linux x86_64 benar-benar dilakukan dari Windows, 27 artifact diberi hash pada `linux-wheels.lock.txt`. Model/library utama tetap dipin; tidak ada fallback versi. | PASS cross-resolution; clean install Linux NOT TESTED |
| RAM/process safety | Gate RAM 3 GiB load/1,5 GiB forward, host memory load <90%, visible cgroup v1/v2 dan ancestor limits. Linux strict commit gate >=2 GiB saat strict mode berlaku. Python di luar keluarga launcher ditolak. Lock eksklusif dan hanya satu managed encoder; tidak mencuri lock stale atau retry otomatis. | PASS unit/mock; inspect resource aktual Windows PASS |
| Log overwrite/Windows replace error | V2 membuat direktori output baru dan receipt dengan exclusive create. Tidak mengganti diagnostic log lama dan tidak melanjutkan checkpoint recovery Windows. | PASS desain/integration tests; sejarah error lama dipertahankan |
| Dokumentasi tidak sinkron | Status terkini dan pembatasan ditulis di dokumen baru ini sesuai keputusan preservasi pengguna; panduan Kaggle baru tersedia. | PASS dengan README lama tetap historis/stale |

API commit-memory Windows tidak dipakai atau dipalsukan oleh v2. Karena itu
v2 **tidak mengklaim** mengukur ambang commit-headroom Windows milik runner lama.
Gate portable memakai physical/container RAM dan pressure; Linux strict commit
ditambahkan ketika dapat diukur. Sampling berada pada batas operasi, bukan peak
kontinu atau bukti terhadap lonjakan OOM. Kernel induk dianggap keluarga launcher;
sibling Python tetap memblokir. Semua ini dijelaskan pada recipe target.

Konfigurasi ilmiah E5 tidak diubah. V2 merupakan implementasi terpisah, sehingga
tidak boleh menulis ulang identitas/cache/checkpoint v1 agar menerima runtime baru.
Tidak disediakan opsi full-corpus pada smoke v2. Pemulihan full-corpus lintas
platform kelak memerlukan desain checkpoint/identity/namespace baru dan otorisasi
terpisah; belum diperlukan untuk meninjau source eksperimen ini.

## Validasi aktual

| Pemeriksaan | Status | Bukti |
|---|---|---|
| Compile src/scripts/tests | PASS | 155 file, 0 error; fresh import v2 melalui interpreter core tidak memuat torch, transformers, encoder/recovery historis atau ctypes. |
| Unit/regression/integration aman | PASS | 162 tests, 0 failure/error/skip. Mencakup 17 tes baru untuk v2, termasuk alur query + 1/5 passage dengan model mock dan STOP bila RAM turun setelah import/tokenizer. Ini tidak menghasilkan hasil penelitian/Kaggle. |
| Dependency lokal | PASS terbatas | Pip check dua venv lama exit 0; tidak ada instalasi/upgrade environment lokal. Venv lama tetap tidak memenuhi syarat CPU-only v2. |
| Contract dan replay artifacts | PASS | Corpus/index/qrels/baseline/snapshot tervalidasi ulang, truncation parity penuh dan 54/54 ranking identik; tanpa embedding/metrik baru. |
| Snapshot/resource v2 aktual Windows | PASS inspeksi | Receipt `windows_inspect_20261015`: snapshot verified, tanpa forward; `cpu_environment_ready=false` karena torch lokal `+cu126`. Inspect PASS bukan inference/preflight PASS. |
| Preflight v2 pada venv ML lokal | BLOCKED | Receipt `windows_preflight_20261015` menolak torch `+cu126`; 0 query/corpus embeddings. Tidak menurunkan syarat `+cpu` untuk memaksakan PASS. |
| Linux wheel resolution | PASS | Pip dry-run/cross-platform, 27 artifact dari PyPI/CPU PyTorch. Semua memiliki SHA256, tidak ada wheel Windows atau package nvidia. Cross-resolution masih memakai marker host Windows; colorama pure-Python ikut terpilih dan diberi hash. |
| Clean install Linux | BLOCKED / NOT TESTED | WSL gagal start dengan `ERROR_PATH_NOT_FOUND`; tidak ada interpreter Linux yang berhasil dijalankan. Tidak menginstal/memperbaiki WSL. |
| Kaggle Notebook/model v2 | NOT TESTED | Tidak tersedia sesi Kaggle aktual. Recipe dan lock disiapkan, bukan notebook output fiktif. |
| Inference lokal baru/full corpus | NOT TESTED | Tidak dijalankan. Embedding aktual satu query berasal dari audit pertama, disebut sebagai bukti lama. |

Bukti lokal baru berada di `experiments/reports/e5_readiness_v2_20261015/`:
`compile.json`, `tests.json/.log`, `contracts.json`, `cached_retrieval.json`,
`dependencies.json`, `linux_resolution_status.json`, `linux_wheel_resolution.json`,
`preservation.json`, dan `publication_review.json`. Laporan/bukti lama tidak
ditimpa. Raw pip metadata dan diagnostics lokal tidak termasuk daftar source
publikasi karena dapat memuat metadata/path environment yang tidak diperlukan.

## Smoke Kaggle yang masih diperlukan

Ikuti [panduan notebook v2](../experiments/portable/e5_cpu_smoke_v2/README.md).
Urutannya: sesi CPU baru → Python 3.12 venv baru → dry-run lock hash → instalasi
lock dan pip check → download/verified offline snapshot → preflight → satu query
pendek → satu chunk → lima chunk. Jalankan bertahap, baca receipt sebelum lanjut.
Data sample terikat SHA256 frozen serialized inputs; file data harus disediakan
secara terpisah oleh peneliti. Hentikan jika dependency/hash/RAM/process/lock gate
menolak. Tidak ada flag untuk menurunkan pin, melewati gate atau full corpus.

Masih dibutuhkan dari Kaggle aktual: metadata Python/OS, output instalasi dan pip
check, actual freeze, receipt model/query/passages CPU FP32, resource samples,
serta traceback lengkap jika gagal. Kegagalan pengguna sebelumnya tidak dapat
diatribusikan ke satu faktor tanpa bukti tersebut.

## Review Git dan keputusan branch

Publikasi eksperimen dibatasi pada **allowlist source/tests/config/docs v2** di
`experiments/reports/e5_readiness_v2_20261015/publication_allowlist.json` beserta
hash dan ukuran tiap file. Tidak ada git add, commit, push, PR atau deployment.
Jumlah file dan hasil scan final dicatat pada `publication_review.json`.

Daftar itu mengecualikan `.env`, credentials, weights, cache, seluruh data,
checkpoint, indeks, vectors, raw reports, arsip transfer, dokumen bimbingan,
assessor/reviewer history dan artefak aplikasi/prototype lain. Tidak aman memilih
seluruh working tree: ribuan file untracked di luar scope sudah ada sebelumnya.
File tracked historis yang mungkin memuat provenance/data dicatat untuk review;
tidak dihapus atau ditulis ulang. Scan regex text bersifat heuristik, bukan audit
seluruh sejarah Git atau bukti hak redistribusi dataset privat.

Scan akhir pada 11 file allowlist: 0 pola secret terdeteksi, 0 path terlarang,
0 file staged. Pemeriksaan heuristik text file tracked juga tidak mendeteksi
pola secret yang dicari. Provenance/qrels yang sudah tracked tetap merupakan
scope review tersendiri, dan tidak dipilih sebagai perubahan publikasi v2.

Probe ignore awal pada helper audit mendapat false negative karena input text
Windows menambahkan CR pada nama path. Aturan `.gitignore` diverifikasi langsung
dan probe diulang dengan pemisah NUL: `.env`, `.env.local`, cache HF/model dan
model_cache diabaikan. Helper diperbaiki; `.gitignore` tidak diubah.

**Keputusan untuk branch eksperimen: SAFE TO PUSH hanya allowlist v2 yang telah
direview.** Kelulusan source ini mendukung publikasi eksperimen dengan batas
pengujian yang dijelaskan. Status Linux/Kaggle dan pipeline end-to-end tetap
NOT TESTED; tidak ada klaim produksi atau hasil benchmark baru. Seluruh working
tree di luar allowlist belum mendapat keputusan aman untuk dipublikasikan.

Keputusan ini disiapkan untuk review pengguna. Tidak ada tindakan Git publikasi
yang dilakukan oleh agen.
