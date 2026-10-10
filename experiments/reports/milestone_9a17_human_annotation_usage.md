# Panduan human relevance annotation — Milestone 9A.17

Penilai: **Muhammad Ivan Verdyansyah**, sebagai peneliti. Label hasil: **Researcher-annotated relevance judgments**. Penilaian ini belum expert-validated atau independently validated.

## 1. Jalankan aplikasi

Buka PowerShell, kemudian:

```powershell
Set-Location 'D:\Project\wo-retrieval-benchmark'
.\.venv\Scripts\python.exe -B scripts/human_annotation.py serve
```

Buka **http://127.0.0.1:8765** pada browser. Biarkan terminal berjalan selama penilaian. Jika port dipakai aplikasi lain, gunakan `serve --port 8766`, kemudian buka alamat port yang dicetak terminal. Aplikasi hanya menerima koneksi loopback komputer ini. Tidak memerlukan instalasi dependency baru, GPU, layanan cloud, database, atau `.venv-ml`.

Workspace sudah dibuat. **Jangan jalankan `prepare` untuk melanjutkan pekerjaan**: perintah tersebut khusus membuat workspace baru dan menolak overwrite. Aplikasi tidak otomatis memilih grade.

## 2. Nilai 654 pasangan

Tersedia **654 pasangan query–chunk unik** dari union Top-20 empat metode pada 18 development queries. Semua pasangan harus dinilai, termasuk 90 pasangan yang pernah memiliki label AI. Urutan disimpan berdasarkan shuffle seed **17042** dan tidak berubah ketika aplikasi dibuka kembali.

1. Baca query dan seluruh isi chunk. Judul, heading, document/chunk ID, dan source locator tersedia untuk membantu memahami sumber. Teks ditampilkan lengkap dengan serializer existing yang dipakai retrieval.
2. Tentukan apakah substansi chunk membantu kebutuhan informasi query, termasuk tahap/kondisi yang disebut query. Kecocokan istilah atau topik saja tidak otomatis cukup. Nilai setiap chunk secara individual; jangan memindahkan jawaban dari sumber lain ke chunk ini.
3. Pilih **Grade 0** jika chunk tidak memberi dukungan berguna; **Grade 1** jika memberi dukungan substantif sebagian; **Grade 2** jika langsung menjawab kebutuhan utama. Pilih **UNRESOLVED** bila keputusan belum dapat dipertanggungjawabkan. Belum dinilai dan UNRESOLVED tetap null, tidak menjadi Grade 0.
4. Catatan/alasan bersifat opsional. Evidence, bila diisi, harus berupa kutipan **persis** dari chunk; jangan menambahkan tanda kutip atau elipsis yang tidak terdapat pada teks sumber. Untuk kasus ambigu, catatan sangat dianjurkan.
5. Tunggu status **Tersimpan**. Gunakan Sebelumnya/Berikutnya, Buka posisi, Belum dinilai, atau Tinjau UNRESOLVED. Perubahan grade maupun catatan tersimpan otomatis; tombol Simpan sekarang tersedia. Navigasi menunggu penyimpanan berhasil.

Aplikasi menyembunyikan metode asal, score, rank retrieval, silver judgments, dan penilaian AI sebelumnya. Angka **Posisi** adalah posisi dalam urutan penilaian yang diacak, bukan ranking retrieval. Grade yang terlihat ketika kembali ke sebuah pasangan adalah keputusan manusia Anda sendiri. Peneliti mungkin sudah mengenal ranking/label dari pekerjaan sebelumnya; aplikasi ini tidak membuktikan isolasi atau kebutaan penuh.

## 3. Simpan dan lanjutkan

Storage berada pada:

`experiments/human_judgments/development_v2/`

File `annotation_input.jsonl` dan `annotation_manifest.json` adalah input immutable. File `human_judgment_history.jsonl` menyimpan semua revisi keputusan dengan timestamp UTC, identitas peneliti, snapshot/input binding, nomor revisi, dan hash chain. `storage_manifest.json` mengikat storage ke input dan protokol. Menyunting keputusan tidak menghapus revisi lama. Penyimpanan memakai file replacement atomik setelah flush/fsync.

Tutup aplikasi hanya setelah Tersimpan, lalu tekan **Ctrl+C** di terminal. Untuk melanjutkan, jalankan perintah `serve` yang sama. Grade dan catatan tetap tersedia; aplikasi membuka pasangan PENDING pertama dalam urutan tetap. UNRESOLVED tetap tersimpan dan dapat ditinjau melalui tombol tersendiri.

Jangan membuka beberapa tab untuk menilai pasangan yang sama secara bersamaan: revisi tab lama akan ditolak. Jika ada error simpan, tetap di halaman itu, periksa kutipan evidence/status error, lalu simpan kembali sebelum menutup tab. Menutup tab saat masih ada perubahan akan memunculkan peringatan browser. Jika history rusak atau checksum input berubah, aplikasi berhenti; jangan memperbaiki dengan mengisi grade 0.

Backup **seluruh folder workspace** setelah menutup server. Pada crash proses, `.server.lock` atau `.write.lock` dapat tertinggal. File tersebut berisi PID. Pastikan proses dengan PID itu sudah tidak berjalan, buat backup workspace, lalu hapus **hanya lock file yang tertinggal**, bukan input/history. Jangan menghapus lock dari server yang masih berjalan.

Periksa progres tanpa menghitung metrik:

```powershell
.\.venv\Scripts\python.exe -B scripts/human_annotation.py status
```

## 4. Ekspor human judgments

Tautan Unduh human judgments JSONL di browser mengekspor semua 654 current records, termasuk PENDING dan UNRESOLVED. Untuk ekspor lengkap dengan manifest dan TREC TSV:

```powershell
.\.venv\Scripts\python.exe -B scripts/human_annotation.py export --out experiments/human_judgments/development_v2/exports/checkpoint_01
```

Gunakan nama folder baru pada setiap checkpoint. Folder existing ditolak. Ekspor berisi `human_judgments.jsonl`, `human_resolved_qrels.tsv`, dan `export_manifest.json`. TSV hanya memuat RESOLVED; tidak adanya pasangan di TSV berarti unknown, bukan nonrelevant. Evaluator membaca validated history, **bukan TSV parsial atau AI qrels**. Ekspor awal `initial_pending_20261010` tersedia sebagai contoh format, dengan 654 PENDING dan TSV kosong; itu bukan ground truth selesai.

## 5. Kapan boleh menghitung metrik development

Protokol development telah ditetapkan sebelum melihat human labels:

- Precision@5/10 dan MRR@10: binary relevance **grade ≥1**; denominasi Precision tetap requested k.
- nDCG@5/10: gain **2^grade−1**, discount **log2(rank+1)**. IDCG memakai grades seluruh union Top-20 pool **untuk query yang sama**, disusun menurun. Namanya **nDCG (pooled)**; bukan ideal ranking seluruh corpus.
- Semua 654 pasangan harus **RESOLVED**, dan setiap returned Top-5/10 chunk harus mempunyai human judgment yang sah. Tidak ada incomplete-query dropping, judged-only denominator, zero imputation, atau evaluasi subset yang dipilih berdasarkan hasil.
- Macro-average menggunakan 18 query IDs tetap yang sama bagi semua metode; hasil per query dan tiga query styles disimpan terpisah. Posisi hasil yang memang tidak dikembalikan memberi zero hit/gain, tanpa menciptakan dummy qrels. Saved score ties mempertahankan chunk-ID ascending.
- Pool yang tidak memiliki satu pun relevant chunk pada sebuah query menyebabkan evaluation gate tertutup. **Jangan mengubah grade untuk memenuhi gate.** Tinjau answerability, perluas assessment melalui versi/protokol baru jika disepakati, atau tetapkan desain untuk confirmed no-answer queries melalui review terpisah. Pool kosong relevan tidak membuktikan corpus tidak mempunyai jawaban.
- Recall@10 tidak diimplementasikan untuk scope ini karena total relevant set corpus belum diketahui. Tidak ada klaim signifikansi atau metode terbaik.

Setelah seluruh gate terpenuhi:

```powershell
.\.venv\Scripts\python.exe -B scripts/human_annotation.py evaluate --out experiments/results/human_development_evaluation/run_01 --word
```

Evaluator membaca ranking 9A.12 tersimpan; tidak menjalankan retrieval/inference. Output JSON/CSV memuat macro, per-query, style, coverage, dan descriptive differences antarmetode. `development_metrics_report.docx` hanya dibuat jika semua gate lulus; dokumen editable memuat angka yang benar-benar dihitung dan label Development pooled evaluation. Data manusia, ranking, input, protokol, dan output diikat dengan hashes.

Jika judgments belum lengkap, `evaluate` tanpa `--word` hanya membuat laporan **BLOCKED** dengan metric cells null/NOT COMPUTED, lalu mengembalikan exit code **2**. Itu penghentian metodologis yang disengaja. Dengan `--word`, keadaan incomplete ditolak tanpa membuat Word. Folder output existing selalu ditolak. Saat milestone ini selesai, **belum ada metrik efektivitas penelitian yang dihitung**.

## 6. Evaluasi utama masih memerlukan rancangan baru

18 queries ini tetap development, tidak otomatis menjadi hasil final skripsi. **75 evaluation queries masih rencana; belum dibuat atau disetujui.** Siapkan kebutuhan informasi baru, family IDs/provenance, pemisahan intent dari development, pemeriksaan exact/normalized overlap, dan review semantik manusia untuk memastikan nama family baru tidak menyamarkan parafrasa kebutuhan lama. Jangan memilih parameter dari hasil main set.

Sebelum main evaluation: sepakati dengan pembimbing penggunaan corpus sintetis, jumlah/style/topic queries, answerability, pilihan pool/exhaustive scope, kebijakan no-answer/UNRESOLVED/UNJUDGED, metrik utama, serta prosedur freeze. Buat package, ranking, human storage, dan qrels versi main yang terpisah setelah persetujuan. CLI sekarang sengaja hanya menerima package development.

Peneliti adalah primary annotator sesuai keputusan Anda. Review praktisi WO atau second human assessor dapat ditambahkan sebagai tahap **terpisah**, dengan judgments independen, subset yang dipilih sebelum labels, exposure disclosure, dan adjudication yang mempertahankan kedua keputusan. Review tersebut belum terjadi. Penilaian seluruh corpus per query atau exhaustive subset yang disepakati diperlukan sebelum membahas corpus-wide Recall.

## 7. Tests

```powershell
$env:PYTHONPATH=(Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_human_annotation.py -v
```

Semua grade pada fixture tests bersifat sintetis. Tests memakai temporary folders dan tidak mengisi storage penelitian. Tidak perlu menjalankan tests untuk melanjutkan annotation sehari-hari.
