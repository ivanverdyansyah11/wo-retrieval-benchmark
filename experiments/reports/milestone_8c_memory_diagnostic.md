# Milestone 8C.1 — Memory Diagnostic & Minimal Optimization

**Diagnostic PASS; no weights loading, GPU inference atau retrieval smoke. Tidak ada perubahan production code karena tidak ditemukan penghematan besar yang aman dan terbukti pada jalur persiapan.**

Diagnostic dilaporkan 2026-10-09T06:34:46.997224+08:00 (Asia/Singapore). Snapshot `WO-CORPUS-V1-DRAFT-PILOT-001`, corpus pending practitioner validation; development queries tetap DRAFT.

## 1. Confirmed findings

Confirmed: `BGEEncoder.__init__` memanggil `from transformers import AutoTokenizer` dan local tokenizer initialization sebelum gate. Dalam environment ini Transformers mengimpor PyTorch CPU/CUDA runtime libraries meskipun weights belum dimuat. Import library bukan BGE-M3 model loading atau CUDA tensor/inference test. FlagEmbedding masih belum diimpor pada final readiness checkpoint.

Import Torch terukur menambah 446.13 MiB RSS. Whole Transformers import menambah 528.10 MiB, **termasuk** Torch; jangan dijumlahkan sebagai dua komponen independen. Resolusi AutoTokenizer + inisialisasi tokenizer setelah import Transformers menambah 256.20 MiB lagi. Langkah ini termasuk lazy class/dependency imports dan native tokenizer allocations; tidak semuanya dapat diatribusikan hanya ke vocabulary.

Antara CLI imported dan readiness selesai, RSS bertambah **801.62 MiB**, available system RAM turun **0.924 GiB**. Footprint RSS ini konsisten dengan historical controlled run: process RSS143.13→944.26MiB, meskipun available system RAM saat itu5.13→4.41GiB. Normal import/tokenizer initialization merupakan penyebab besar yang teramati; tidak ada bukti corpus weights dimuat sebelum gate.

## 2. Measurement method dan limitations

Satu fresh `.venv-ml` subprocess menjalankan actual `hybrid.cli.run(root,"audit")` melalui event-driven wrappers pada existing configuration/R2/model hash/tokenizer/R3 functions. Wrappers mengembalikan original results; tidak melewati loader, checksum, snapshot, config/model/code identity atau token checks. BGEEncoder.load dan encode diganti assertion-only dalam subprocess diagnostic supaya percobaan loading/forward menggagalkan audit. Tidak ada patch file source/dependency di disk.

Startup sample diambil setelah minimal stdlib/psutil/resource imports, bukan pada instruksi pertama interpreter. Actual audit watchdog existing tetap berjalan pada interval existing; tidak ada polling loop tambahan untuk profiling. Stage samples diambil hanya pada batas operasi/import. No tracemalloc overhead, package install, repeated experiment atau neural model. Import hook hanya mengukur first top-level torch/transformers/tokenizers imports; nested work termasuk pada parent duration/delta.

RSS/Windows working set mencakup resident private **dan shared** pages. System available RAM juga dipengaruhi OS, file cache/reclaim, driver, proses lain dan paging. RSS delta bukan conservation accounting terhadap available RAM. Satu stage bahkan menunjukkan available RAM naik saat RSS bertambah. Tidak ada per-process system-wide memory trace atau private-byte accounting; kontribusi proses lain, OS cache dan shared pages **tidak dapat dipastikan secara numerik** dari sampel ini. Tidak menyebut seluruh penurunan available RAM sebagai milik Python.

Checkpoint yang diberi label before-weights equivalent adalah akhir readiness pada jalur audit; weights tidak dipanggil, bukan measurement setelah gate smoke. Audit tidak memproses tiga query, dan tidak mengimpor FlagEmbedding melalui encoder.load; tambahan import/model-wrapper costs setelah gate belum diukur. No inference readiness guarantee dari audit ini.

## 3. Memory per initialization stage

| Stage | Process RSS MiB | Available RAM GiB | Commit headroom GiB |
|---|---:|---:|---:|
| Startup: resource probe only | 17.53 | 5.143 | 14.106 |
| R4 CLI imports finished | 143.41 | 5.020 | 13.840 |
| Configuration loaded | 143.43 | 5.020 | 13.840 |
| R2 verified index loaded | 154.80 | 5.001 | 13.801 |
| Local checkpoint hashes verified | 154.82 | 5.031 | 13.836 |
| Before first Torch import | 159.52 | 5.020 | 13.828 |
| After first Torch import | 605.65 | 4.586 | 13.153 |
| After Transformers import (includes Torch) | 682.92 | 4.309 | 12.908 |
| BGEEncoder initialized: tokenizer only | 939.11 | 4.113 | 12.691 |
| 371-tokenizer audit finished | 942.87 | 4.113 | 12.690 |
| R3 identity verified | 943.19 | 4.112 | 12.689 |
| R3 verified vectors loaded | 945.04 | 4.103 | 12.688 |
| Readiness complete / before-weights equivalent | 945.04 | 4.096 | 12.688 |
| Diagnostic gc.collect probe | 944.05 | 4.094 | 12.689 |
| Audit returned; retriever/tokenizer released | 694.21 | 4.335 | 12.937 |

Readiness process peak working set: 1002.26MiB. R2 load increment: 11.25MiB. R3 vector load increment: 1.84MiB. Exact vector payload: 1,519,616bytes (371×1024×4; about1.45MiB). GPU sampled peak device usage from audit monitor: 0MiB. No PyTorch GPU peak stats collected; no GPU allocations requested.

## 4. Inspection: retained objects dan duplicates

- CLI eager `dense.index` imports lexical foundation, NumPy/SciPy/sklearn sebelum initial run resource sample. Startup17.53→CLI143.41MiB menunjukkan biaya ini sudah ada sebelum historical preflight143MiB, sehingga bukan seluruh penyebab penurunan historical5.13→4.41GiB.
- `ready` loads R2 once melalui existing verified loader. R2 loader membaca protocol dan reconstructs canonical serialized input untuk mengecek index; configuration juga dibaca oleh CLI dan ready. Repeated tiny configuration reads bukan dominant cost.
- `rows = bm25.rows`; DenseRetriever memakai list yang sama. `rows_shared_object=True` dan `encoder_shared_object=True` diverifikasi. Tidak ada duplicate retained corpus list atau duplicate encoder pada readiness.
- R3 load_vectors loads vectors once. Validation sementara mencakup checksum reads, row-mapping JSON equality, finite/norm arrays; matrix hanya1.45MiB. R2 persisted documents JSON sekitar1,033,399bytes dan BM25 model JSON412,506bytes; Python object expansion tetap terukur hanya sekitar11MiB pada tahap R2 load.
- `model_files` streams checkpoint in1MiB blocks, memverifikasi12 local files termasuk2GB checkpoint tanpa deserialisasi weights. Filesystem caching dapat memengaruhi system memory namun retained Python checkpoint object besar tidak dibuat; RSS sebelum/sesudah hash hanya berbeda sekitar0.01MiB.
- Tokenizer, BM25 state, corpus rows, vector matrix, metadata dan config memang masih direferensikan saat readiness mengembalikan retriever. Tokenizer diperlukan untuk actual query tokenization/forward; bukan abandoned temporary object.
- One explicit diagnostic-only gc.collect collected63 objects, RSS turun 0.99MiB. Tidak ada alasan menambahkan gc.collect pada production path untuk mengejar gate.
- Setelah audit returns, local retriever/encoder/tokenizer keluar scope dan RSS turun sekitar250MiB. Penghematan tersebut tidak tersedia untuk inference dengan encoder yang sama: menghapus tokenizer lalu memuat ulang hanya memindahkan biaya.
- No pre-gate BGEM3FlagModel initialization: hanya AutoTokenizer; `encoder.model=None`, lock=None. FlagEmbedding import dan BGEM3FlagModel construction terjadi dalam load setelah gate. Potential additional tokenizer/model-wrapper memory pada weights-loading path belum diukur karena dilarang dalam task ini.

## 5. Minimal optimization decision

**Tidak ada production optimization diterapkan.** Mengubah eager imports menjadi lazy dapat memperkecil startup RSS, tetapi modul yang sama tetap diperlukan untuk readiness/inference sehingga belum membuktikan pengurangan final gate footprint. Menunda tokenizer atau memasang gate sebelum import demi angka available RAM yang lebih tinggi akan menggeser biaya, bukan menyelesaikannya. Tidak menghapus tokenizer/model hash/token audit checks atau menonaktifkan Torch untuk memaksa gate PASS.

Mengubah shared lexical/dense modules juga akan mengubah code-bound existing index identity. Task melarang index format/fingerprint changes; tidak ada perubahan tersebut. Genuine optimization yang aman perlu evidence baru di scope terpisah, bukan refactor spekulatif. Retrieval/RRF k60/full Dense371/BM25 positive-only/model revision/serialization dan thresholds6GiB/5GiB/2GiB tetap identik.

## 6. Files dan evidence

Created repository report: `experiments/reports/milestone_8c_memory_diagnostic.md`. Existing source/tests/configs/README/reports tidak diubah. Instrumentation script dan machine-readable evidence disimpan di luar repository pada approved D: temporary area:

- `D:/ModelCache/tmp/wo-m8c-memory/diagnostic.py`
- `D:/ModelCache/tmp/wo-m8c-memory/result.json` dan `stages.json`
- `D:/ModelCache/tmp/wo-m8c-memory/stdout.log` dan `stderr.log`
- `D:/ModelCache/tmp/wo-m8c-memory/tests.json` dan `tests.log`
- `D:/ModelCache/tmp/wo-m8c-memory/final_resource_and_integrity.json`
- Existing CLI audit run evidence: `D:\ModelCache\wo-retrieval-benchmark\runs\20261008T223151699899Z-R4\run.json`
- Diagnostic script SHA-256: `9cbdda5ae51e544203124e4994440904964d52e501284b2e3be586dac9ce74cf`

## 7. Tests dan integrity

**51 targeted/regression tests PASS**: R4 16, R1/R2 lexical14, R3 Dense16, protocol5. TOML parsing dan Markdown/TOML consistency PASS melalui existing protocol tests. No new unit test karena tidak ada production code change; diagnostic assertions menjaga no-load/no-forward,371rows, shared object references dan readiness status. Synthetic tiny regression caches di temporary directories bukan frozen corpus embedding atau production re-indexing.25 pipeline tests tidak diulang; parser/chunker tidak berubah.

**Integrity PASS:** seluruh138 baseline existing repo files byte-identical, termasuk50 source documents, canonical documents, chunks, pilot.toml, snapshot JSON/MD, protocol, queries/provenance/workbook, source/tests, model-environment locks dan R1/R2 index artifacts. R3 manifest/rows/vectors SHA identik dengan baseline sebelum diagnostic; actual loader juga memverifikasi complete status, snapshot, serialization, model/checkpoint/tokenizer/code/dependency identity, row mapping, shape/finite/norm. No Git tersedia; baseline SHA-256 dipakai.

| Identity | Value |
|---|---|
| Snapshot fingerprint | `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40` |
| R2 manifest fingerprint | `6311e3dde68c96f4f84a1601a894946af5abe655d5656d1ed93ceffbf2874120` |
| R3 manifest fingerprint | `465cf54c7fa3aadaccbb3090279762bd27f24817360c749ede4315f1f34abc72` |
| Serialized input hash | `dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c` |

## 8. Remaining resources dan next smoke readiness

Post-diagnostic/regression fresh lightweight resource probe at2026-10-08T22:34:46.997224+00:00 UTC: available RAM **5.040GiB**, commit headroom13.606GiB; C: free12.911GiB, D: free846.928GiB. Ini sesudah diagnostic process exits; bukan RAM setelah framework/tokenizer dalam future inference process.

**Belum siap mengklaim GPU smoke dapat dimulai:** final equivalent checkpoint dalam diagnostic hanya4.096GiB (<approved5GiB). Sistem perlu menyediakan lebih banyak headroom sebelum run berikutnya; biaya persiapan yang teramati sekitar0.8GiB RSS setelah CLI imports memberi planning context, bukan threshold baru atau guaranteed prediction. Pengguna dapat menutup aplikasi secara manual, lalu menyetujui preflight/smoke baru. Actual6/5GiB loading gates dan2GiB watchdog tetap menjadi penentu; tidak ada izin inference pada task ini.

Milestone8C.1 diagnostic selesai; Milestone8C GPU smoke masih pending dan8D tidak dimulai. No install/download, full model loading, GPU/CPU inference, corpus re-embedding/indexing, retries, qrels, effectiveness metrics, commit/push/PR/deploy. **STOP.**
