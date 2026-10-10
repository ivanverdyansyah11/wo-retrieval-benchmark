# Setup dan jalur CPU dari artefak existing

Target: Windows x64, Python 3.12.14. Jalankan instalasi README dari root repository, menggunakan interpreter `.venv\Scripts\python.exe` tanpa activation. `pip check` harus berhasil. Setup CPU memasang ingestion, lexical extras, dan psutil untuk import modul/test historis; tidak memasang Torch, FlagEmbedding, Transformers, atau weights BGE-M3.

`requirements.lock` membekukan ingestion; `experiments/configs/lexical_environment.lock.txt` membekukan enam dependency lexical; `docs/offline_constraints.txt` melengkapi transitive CPU dependencies yang teramati saat instalasi audit. ML environment lock merupakan provenance encoding historis, bukan dependency quick start CPU.

## Verifikasi tanpa cache eksternal

```powershell
.\.venv\Scripts\python.exe scripts/verify_repository.py
.\.venv\Scripts\python.exe scripts/verify_repository.py --query-id WO-DEV-001
.\.venv\Scripts\python.exe scripts/human_annotation.py status
```

Root default berasal dari lokasi script; `--root` dapat menunjuk salinan lengkap. Frozen source hashes divalidasi terlebih dahulu, kemudian script memakai serializer, loader lexical/matriks Dense, CachedEncoder, dan Hybrid existing. Encoding identity dibaca dari provenance frozen; weights, tokenizer, dan inference environment historis tidak diverifikasi ulang. Seluruh ranking dan JSON evaluasi dibandingkan exact tanpa menerbitkan hasil baru.

Artefak wajib mencakup data, configs, indeks R1/R2/R3 V2 dan 18 query vectors, source/scripts, annotation manifests/history/input, serta semua hasil yang dirujuk frozen source hashes. Laporan/artefak 9A.12–9A.15 merupakan dependency audit human. Semua tersedia pada kandidat publikasi ini; tidak ada unduhan artefak yang diasumsikan tersedia.

## Entry points dan keterbatasan historis

`wo-corpus`, `wo-retrieve`, `wo-dense` adalah installed entry points. Default pipeline/retrieval CLI historis masih V1. `wo-corpus audit` menulis laporan: gunakan verification script untuk read-only. Jangan menjalankan build/run/ingest/chunk pada snapshot frozen.

Loader `full_colab.load_components`, `versioned_dense.prepare_v2`, dan Dense/Hybrid CLI historis memerlukan V1 Dense cache, checkpoint hashes, dan official FlagEmbedding installation pada paths Windows eksternal. Driver 9A.12/9A.13 juga merujuk baseline di luar repository. Kode tersebut dipertahankan sebagai provenance dan tidak dijanjikan portable setelah clone. Jalur development CPU menggunakan `verify_repository.py`.

Encoding ulang bukan quick start. Notebook `experiments/portable/v2_bge_m3/` dan lock ML mendokumentasikan environment khusus. Query baru memerlukan encoding dengan kontrak yang sama dan hardware yang sesuai. Cache 18 queries tidak mendukung arbitrary queries. Audit ini tidak mengubah paths/protokol frozen atau menjanjikan inference di semua perangkat.

## Tests

```powershell
$env:PYTHONPATH = (Join-Path $PWD 'src')
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Perintah menjalankan seluruh tests. Exchange/import/kontrak Colab diuji dengan frozen V2 artifacts dan synthetic vector fixtures pada CPU. Satu test terpisah, `LocalEncodingEnvironmentTests.test_pinned_local_encoding_provenance`, SKIP jika metadata dependency encoding, historical cache/checkpoint, atau official implementation tidak tersedia. SKIP dicatat terpisah dari PASS. Jika prasyarat tersedia tetapi hash/versi tidak cocok, test gagal; error tidak diubah menjadi SKIP. Fixture encoder bukan inference nyata dan actual cloud execution tidak diklaim diuji ulang.

Environment asal memiliki dua venv terpisah. Environment CPU gabungan pada README dapat menjalankan seluruh offline suite; prasyarat encoding historis hanya untuk test environment-specific di atas. Historical whole-workspace receipts tetap utuh. Tests me-relokasi paths repository, memeriksa semua scientific data/results/configs dan source lama, serta membedakan dokumentasi, test implementation, generated metadata, dan external cache yang diuji terpisah. Linux/macOS belum diverifikasi; imported-history validation memakai semantik absolute Windows paths. Hasil audit terbaru ada pada [Milestone 9A.20](../experiments/reports/milestone_9a20_final_github_readiness.md).
