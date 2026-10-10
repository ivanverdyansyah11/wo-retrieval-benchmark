# Environment feasibility audit

Tanggal audit: 2026-10-08, Asia/Singapore. Snapshot: **WO-CORPUS-V1-DRAFT-PILOT-001**. Audit lokal read-only; satu-satunya output baru adalah laporan ini. Angka kapasitas model di bawah adalah perhitungan/perencanaan, bukan hasil benchmark atau pengukuran inference.

## Keputusan

**TF-IDF, BM25, dan pencarian exact atas 371 dense vectors layak pada CPU. BGE-M3 layak masuk tahap uji kelayakan CPU dan GPU, dengan GPU sebagai opsi bersyarat. Environment belum siap untuk langsung menjalankan model.** Project belum memiliki PyTorch/dependency retrieval; RAM bebas saat audit rendah dan cache default berisiko memenuhi C:.

Usulan awal: environment retrieval terpisah berbasis Python 3.12.14; BGE-M3 GPU FP16 batch 1 setelah pengujian kompatibilitas dan memory, dengan CPU FP32 batch 1 sebagai fallback. Jangan mengasumsikan GTX 1050 lebih cepat; tentukan device untuk run utama dari pengujian nyata sebelum membekukan konfigurasi retrieval.

## Hardware dan software aktual

| Komponen | Hasil deteksi |
|---|---|
| OS | Microsoft Windows 11 Pro, 64-bit, 10.0.22631, build 22631 |
| CPU | Intel Core i7-7700HQ @ 2.80 GHz; 4 physical cores, 8 logical processors |
| RAM terpasang | 17,059,098,624 bytes, sekitar 15.89 GiB, nominal 16 GB |
| RAM bebas | 3,605,264 KiB, sekitar 3.44 GiB pada saat pemeriksaan; berubah mengikuti proses lain |
| GPU CUDA | NVIDIA GeForce GTX 1050; 4096 MiB VRAM; compute capability **6.1** |
| VRAM saat audit | Used 0 MiB, free 4007 MiB menurut nvidia-smi; sebagian memori dicadangkan driver |
| iGPU | Intel HD Graphics 630; tidak dipakai untuk baseline CUDA. AdapterRAM WMI bukan ukuran dedicated CUDA VRAM |
| NVIDIA driver | 581.80; WMI 32.0.15.8180; mode WDDM |
| nvidia-smi | Tersedia di `C:\WINDOWS\system32\nvidia-smi.exe`; menampilkan CUDA Version 13.0 |
| Project interpreter | `D:\Project\wo-retrieval-benchmark\.venv\Scripts\python.exe`, Python **3.12.14** |
| Python pada PATH | `C:\laragon\bin\python\python-3.10\python.exe`, Python **3.10.6** |
| PyTorch dalam project .venv | **Tidak terpasang**; CUDA availability melalui PyTorch project belum dapat diuji |
| PyTorch Laragon | **2.9.1+cpu**, `torch.version.cuda=None`, `torch.cuda.is_available()=False`, compiled CUDA architectures `[]` |
| Python launcher | `py -0p` mencantumkan Python 3.13, tetapi executable yang dirujuk tidak ditemukan ketika dijalankan; bukan interpreter project |
| CUDA toolkit compiler | `nvcc` tidak ditemukan pada PATH; tidak membuktikan toolkit tidak ada di lokasi lain |

Driver API `nvcuda.dll` juga diperiksa tanpa membuat context/model: `cuInit(0)=0`, `cuDriverGetVersion=13000`, `cuDeviceGetCount=1`. Driver mengenali satu GPU CUDA. Ini belum membuktikan kernel dari wheel PyTorch yang diusulkan bisa dijalankan.

Metode pemeriksaan: CIM (`Win32_OperatingSystem`, `Win32_Processor`, `Win32_ComputerSystem`, `Win32_VideoController`, `Win32_LogicalDisk`), nvidia-smi, resolusi interpreter, metadata package, `pip check`, driver API, dan hash file. Tidak dilakukan stress test. Telemetri suhu/daya nvidia-smi yang tidak masuk akal diabaikan.

## Kompatibilitas CUDA dan PyTorch

GTX 1050 merupakan GPU Pascal, compute capability 6.1; hasil perangkat cocok dengan [daftar GPU legacy NVIDIA](https://developer.nvidia.com/cuda/gpus/legacy). Angka CUDA 13.0 di nvidia-smi menunjukkan versi CUDA maksimum yang didukung driver, bukan runtime PyTorch terpasang atau bukti dukungan arsitektur GPU oleh suatu wheel. Lihat [dokumentasi nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html).

**Kandidat GPU: PyTorch 2.12.1, build CUDA 12.6 (`cu126`), Windows x64, CPython 3.12.** Dokumentasi PyTorch menyediakan jalur Windows/Linux ini; kebijakan packaging mempertahankan CUDA 12.6 untuk Maxwell/Pascal/Volta. Hindari pemilihan build CUDA 13 hanya karena driver menampilkan 13.0, serta build cu128/cu129 yang telah menghapus dukungan Pascal. Sumber: [rilis/wheel PyTorch](https://pytorch.org/get-started/previous-versions/), [kebijakan CUDA 2.12](https://dev-discuss.pytorch.org/t/introducing-cuda-13-2-and-deprecating-cuda-12-8-release-2-12/3337), [penghapusan Pascal pada cu128/cu129](https://dev-discuss.pytorch.org/t/cuda-toolkit-version-and-architecture-support-update-maxwell-and-pascal-architecture-support-removed-in-cuda-12-8-and-12-9-builds/3128).

Index resmi telah diperiksa, tanpa mengunduh wheel:

- Wheel: `torch-2.12.1+cu126-cp312-cp312-win_amd64.whl`.
- Index: <https://download.pytorch.org/whl/cu126/torch/>.
- SHA-256 yang dipublikasikan: `71ee0eca3bde3a4067dfbc28c705b914d0773edd29ac4a634ad5e7a07f336aa1`.

Driver 581.80 mendukung runtime CUDA 12.x melalui backward compatibility. Instalasi toolkit/compiler CUDA terpisah tidak diperlukan untuk rencana memakai wheel prebuilt tanpa custom CUDA extension. Lihat [NVIDIA compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html).

**Batas bukti:** tabel arsitektur terperinci pada pengumuman packaging berlaku untuk Linux x86_64. Keberadaan wheel Windows dan kebijakan legacy menjadikannya kandidat beralasan, tetapi audit ini tidak memeriksa binary Windows atau menjalankan kernel build tersebut. Setelah instalasi diizinkan, wajib cek versi/build, `is_available`, device capability, `get_arch_list`, lalu operasi CUDA kecil dan inference BGE-M3. Arsitektur biner yang kompatibel dalam keluarga sm_6x dapat relevan; jangan mensyaratkan string literal `sm_61` saja. Jika gagal, gunakan build CPU terpisah; jangan membangun PyTorch dari source sebagai langkah pertama.

## Dependency existing dan proposed environment

Project mensyaratkan Python `>=3.12,<3.13`. Direct dependencies ingestion: python-docx 1.2.0, pypdf 6.10.0, openpyxl 3.1.5. Lock juga mencatat lxml 6.1.3, et-xmlfile 2.0.0, typing_extensions 4.16.0. Project .venv memiliki pip 25.0.1 dan editable project 0.1.0. `pip check`: **No broken requirements found**. Metadata editable dapat tampil lebih dari sekali; tidak diperbaiki dalam audit.

Belum terpasang dalam project: torch, numpy, scipy, scikit-learn, rank-bm25, bm25s, transformers, sentence-transformers, FlagEmbedding, faiss. PyTorch global Laragon tidak dipakai sebagai dependency project dan tidak menunjukkan dukungan CUDA.

Usulkan `.venv-retrieval` baru di D: dengan interpreter Python 3.12.14 yang dipilih secara eksplisit. Base interpreter project saat ini berada di `C:\Users\ivanv\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`; ini runtime terkelola Codex, sehingga catat lokasinya dan pertimbangkan instalasi standalone 3.12.14 untuk reproduksi jangka panjang. Jangan mengandalkan bare `python`, stale launcher `py`, atau menyalin site-packages Laragon. Existing .venv, pyproject dan requirements.lock tetap utuh.

| Kebutuhan | Proposed pin | Alasan |
|---|---|---|
| Array/dot product | numpy 1.26.4 | Wheel CPython 3.12 Windows tersedia; cukup untuk exact dense search |
| Sparse matrix | scipy 1.16.3 | Mendukung Python 3.12 dan rentang NumPy di atas |
| TF-IDF | scikit-learn 1.7.2 | TF-IDF sparse dan cosine tanpa dependency index tambahan |
| BM25 | rank-bm25 0.2.2 | Implementasi kecil, parameter dapat dicatat eksplisit |
| Dense runtime GPU | torch 2.12.1+cu126 | Kandidat legacy Pascal; install dari index cu126 resmi |
| Dense runtime CPU | torch 2.12.1+cpu | Alternatif environment CPU; jangan gabungkan dua build torch dalam satu env |
| Model/tokenizer | transformers 4.57.6 | Mendukung XLM-R/BGE; pin agar perilaku tidak berubah mengikuti latest |
| Dense pooling/normalization | sentence-transformers 5.2.0 | Memakai pipeline dense yang dipublikasikan model |
| R5/R6 optional | FlagEmbedding 1.4.2 | Wrapper sparse/ColBERT; tunda sampai core dense stabil |

Metadata versi, Python requirement, dan wheel dasar diperiksa melalui sumber publisher PyPI. **Ini proposed direct pins, bukan lock yang telah berhasil di-resolve atau diuji bersama.** Transitive dependencies seperti huggingface-hub, tokenizers, safetensors, filelock, requests, tqdm, joblib dan threadpoolctl masih perlu di-resolve, kemudian dipin beserta hash wheel setelah otorisasi. Contoh sumber metadata: [NumPy](https://pypi.org/pypi/numpy/1.26.4/json), [SciPy](https://pypi.org/pypi/scipy/1.16.3/json), [scikit-learn](https://pypi.org/pypi/scikit-learn/1.7.2/json), [Transformers](https://pypi.org/pypi/transformers/4.57.6/json), [SentenceTransformers](https://pypi.org/pypi/sentence-transformers/5.2.0/json).

FlagEmbedding menambah dependency datasets, accelerate, peft, ir-datasets, sentencepiece/protobuf dan lainnya; audit resolusi optional ini secara terpisah. Jangan mengambil extras training, DeepSpeed atau flash-attn. torchvision, torchaudio, FAISS, database vector dan embedding model tambahan tidak dibutuhkan untuk core 371 chunks. RRF tidak membutuhkan package tersendiri. Sumber: [FlagEmbedding setup](https://github.com/FlagOpen/FlagEmbedding/blob/master/setup.py), [rank_bm25](https://github.com/dorianbrown/rank_bm25).

## RAM, VRAM dan storage feasibility

BGE-M3 mendukung dense 1024 dimensi, sparse dan multi-vector, dengan batas model 8192 tokens. Model sekitar 568 juta parameter. Sumber: [model card BAAI](https://huggingface.co/BAAI/bge-m3), [dokumentasi BGE](https://bge-model.com/tutorial/1_Embedding/1.2.1.html).

Revision yang diperiksa untuk rencana reproducibility: `5617a9f61b028005a4858fdac845db406aefb181`. Metadata [Hugging Face API](https://huggingface.co/api/models/BAAI/bge-m3?blobs=true) melaporkan `pytorch_model.bin` 2,271,145,830 bytes (sekitar 2.12 GiB), SHA-256 `b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38`. Tokenizer JSON sekitar 16.3 MiB dan sentencepiece sekitar 4.83 MiB. Tidak ditemukan `model.safetensors` pada daftar file revision ini; jangan mengasumsikan format safetensors tersedia. Hanya metadata/config kecil yang dibaca; weights/tokenizer besar tidak diunduh.

| Objek | Estimasi kapasitas, bukan measured peak |
|---|---|
| Parameter model FP32 | Sekitar 2.12 GiB; loading/state dict/runtime dapat menambah salinan |
| Parameter model FP16 | Sekitar 1.06 GiB; belum termasuk activations, attention, workspace, allocator dan CUDA context |
| Dense matrix 371 × 1024 FP32 | 1,519,616 bytes, **1.45 MiB** |
| Multi-vector, asumsi maksimum 1024 vectors/chunk × 1024 dimensi FP32 | Sekitar **1.45 GiB**; ilustrasi budget, bukan ukuran aktual tokenizer/output |
| Multi-vector FP16 dengan asumsi sama | Sekitar 0.72 GiB; precision/ranking perlu diverifikasi |

16 GB RAM total cukup beralasan untuk pilot inference serial, tetapi **3.44 GiB bebas saat audit tidak memberi headroom aman** untuk loading FP32 dan staging. Sebelum smoke test, tutup proses yang tidak diperlukan; usulkan minimal 6 GiB RAM tersedia untuk percobaan GPU dan 8 GiB untuk CPU sebagai margin operasional konservatif, bukan batas teknis yang telah diukur. Hindari memegang dua model atau salinan penuh embeddings multi-vector sekaligus. Pagefile bukan pengganti RAM untuk benchmark latency.

4 GB VRAM memberi peluang untuk FP16 batch 1 pada sequence konservatif, tetapi tidak menjamin inference muat. GPU Pascal consumer tidak memiliki Tensor Cores; FP16 dipilih untuk menghemat memory, bukan janji percepatan. Hindari BF16 dan optimized attention yang mensyaratkan GPU baru; mulai dari eager attention. Lihat [Pascal tuning guide](https://docs.nvidia.com/cuda/pascal-tuning-guide/index.html).

| Drive | Total | Free saat audit | Penilaian |
|---|---:|---:|---|
| C: | 127,049,658,368 bytes | 2,868,445,184 bytes, **2.67 GiB** | Tidak aman untuk default cache model + wheel + temporary extraction |
| D: | 1,000,203,087,872 bytes | 917,185,835,008 bytes, **854.19 GiB** | Memadai untuk environment, model dan indeks pilot |

HF_HOME, HF_HUB_CACHE, TRANSFORMERS_CACHE, TORCH_HOME dan PIP_CACHE_DIR belum diset. TEMP/TMP berada di `C:\Users\ivanv\AppData\Local\Temp`. Untuk eksekusi berikutnya, usulkan session-local HF_HOME=`D:\ModelCache\huggingface`, TORCH_HOME=`D:\ModelCache\torch`, PIP_CACHE_DIR=`D:\ModelCache\pip`, TEMP/TMP=`D:\ModelCache\tmp`; jika HF_HUB_CACHE dipakai, arahkan konsisten ke D:. Semua ini **belum dibuat atau diubah**.

Sediakan budget awal 20–30 GiB di D: untuk weights, expanded environment, wheel cache dan temporary files; ini allowance perencanaan, bukan hasil pengukuran instalasi. Hindari mengunduh seluruh variasi ONNX/export model. Pada Windows, cache tanpa symlink dapat menggandakan file; verifikasi pemakaian storage nyata setelah download yang diotorisasi.

## Strategi device, batch, precision dan fallback

| Parameter | Percobaan GPU | CPU fallback/reference |
|---|---|---|
| Device | cuda:0, GTX 1050, hanya setelah smoke test berhasil | cpu |
| Model dtype | FP16 | FP32 |
| Batch dokumen/query | 1 / 1 | 1 / 1 |
| Thread/worker | CPU preprocessing 4 threads, interop 1, data workers 0 | 4 threads, interop 1, data workers 0 |
| Attention | Eager; tanpa FlashAttention, torch.compile, custom kernels | Eager |
| Execution | eval + inference_mode; tanpa gradient | Sama |
| Output dense | L2 normalized; simpan FP32 dengan chunk_id dan model revision | Sama |
| Ranking dense | Exact dot product CPU atas seluruh 371 vectors | Sama |

Usulkan `max_length=1024` sebagai **candidate**, bukan izin truncation. Pilot 500 proxy tokens memakai `approx_unicode_chars_div4_v1`, bukan tokenizer BGE; maksimum aktual proxy 485 tidak membuktikan panjang tokenizer <=1024. Setelah tokenizer boleh diunduh, hitung semua 371 panjang input, termasuk special tokens, tanpa mengubah text. Bila ada yang melebihi cap, laporkan chunk_id dan pilih cap bersama sebelum benchmark; model mendukung sampai 8192, tetapi memory 4 GB mungkin tidak mencukupi. Jangan diam-diam memotong text, mengurangi cap, atau membuat chunks baru untuk mengatasi OOM.

Uji smoke dengan chunk bertoken paling panjang, bukan hanya chunk pertama. Mulai ketika VRAM bebas sekitar >=3 GiB dan RAM memenuhi margin di atas. Batch 2 boleh diuji terpisah setelah batch 1 lolos; konfigurasi final harus ditetapkan sebelum pengukuran. Jika OOM/unsupported kernel/nonfinite output: hentikan proses GPU agar model benar-benar dilepas, mulai ulang proses CPU FP32 dengan input/cap yang sama. `empty_cache()` tidak membebaskan tensor yang masih direferensikan.

Catat fallback sebagai run/device/precision berbeda; jangan mencampur CPU dan GPU secara diam-diam dalam satu run. Jika CPU juga kekurangan RAM, hentikan dan bebaskan memory atau jalankan environment identik di mesin lebih besar. Jangan mengganti model/quantization/token cap dalam run yang sama. Tidak memakai CPU FP16, BF16, quantization, offload atau iGPU pada baseline ini.

## Proposed R1–R6 configuration

Semua konfigurasi berikut hanya usulan dalam laporan; tidak ada kode/config retrieval dibuat. Input retrievable hanya 371 `text` dari chunks.jsonl frozen. Title, heading dan locator tetap metadata; jangan otomatis menambahkan ke input hanya untuk sebagian metode. Jangan mengindeks manifest, ringkasan corpus atau audit report.

| Run | Metode | Konfigurasi usulan | Alasan |
|---|---|---|---|
| R1 | TF-IDF | CPU; unigram; min_df=1; max_df=1.0; smooth_idf=True; sublinear_tf=True; L2 norm; float32; cosine exact | Baseline lexical ringan dan transparan |
| R2 | BM25 | CPU; BM25Okapi; k1=1.5; b=0.75; epsilon=0.25; full corpus | Baseline lexical frequency/length; pin implementasi termasuk perlakuan negative IDF |
| R3 | BGE-M3 Dense | Revision di atas; CLS pooling + L2; candidate cap 1024 setelah token gate; batch 1; GPU FP16 bersyarat atau CPU FP32 run terpisah; exact CPU dot product | Memakai published dense pipeline; 371 vectors tidak memerlukan ANN |
| R4 | BM25 + BGE-M3 Dense + RRF | Ranking R2 dan R3; masing-masing top 50; bobot 1:1; k=60; ranks mulai 1; score=sum(1/(60+rank)); missing candidate contribution=0 | Fusion sederhana tanpa score calibration/model tambahan |
| R5 optional | BGE-M3 Sparse | FlagEmbedding; hanya sparse output yang dibutuhkan; learned lexical weights; exact sparse dot product CPU; batch/cap sama | Menguji sparse BGE sebagai metode tersendiri, bukan BM25 |
| R6 optional | Dense → BGE-M3 ColBERT reranking | Candidate R3 top 50; late interaction sum of query-token MaxSim; scoring CPU streaming per candidate; batch 1 | Membatasi RAM/biaya; **candidate-limited reranker**, bukan full-corpus multi-vector retrieval |

R6 harus dilabeli sebagai reranking pipeline, dengan candidate recall menjadi batas hasil. Jika diperlukan full-corpus ColBERT sebagai perbandingan penelitian, tetapkan varian terpisah yang menskor seluruh 371 chunks secara streaming; jangan menyamakan kedua hasil.

R1/R2 memakai tokenizer lexical bersama: Unicode NFC, lowercase, regex `\b\w+(?:[-’']\w+)*\b`, tanpa stopword removal/stemming; pertahankan angka, underscore dan kode ber-hyphen. Ini usulan analyzer eksplisit, belum diimplementasikan; jangan bergantung pada default sklearn yang dapat memecah kode. BGE memakai tokenizer resminya tanpa lexical lowercasing tambahan dan tanpa instruction prefix. R3 menggunakan modul CLS pooling dan Normalize pada model yang dipublikasikan, bukan mean pooling arbitrer. Sumber: [TF-IDF API](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html), [BGE model configuration](https://huggingface.co/BAAI/bge-m3/tree/5617a9f61b028005a4858fdac845db406aefb181), [SentenceTransformers API](https://sbert.net/docs/package_reference/sentence_transformer/model.html).

Common controls: stable ties `chunk_id` ascending, deduplicate by chunk_id, proposed final top-k 5/10/20, seed 42, query batch 1. Seed tidak menjamin bit-identical hasil lintas device; catat precision/library/driver dan determinism settings. Future queries/qrels harus sama untuk semua run. Pengukuran nantinya memisahkan model load, corpus encoding/index build, query encoding, search/fusion dan total query latency; GPU timing perlu synchronization. Laporkan warmup, repeats, RAM process peak dan VRAM peak. Tidak ada query, qrels, retrieval score, latency atau throughput yang dibuat dalam audit ini.

## Persiapan sebelum implementasi

1. Pertahankan snapshot dan hash; setujui proposed run definitions, text rendering, RRF/candidate depth dan optional R5/R6 sebelum menulis retrieval.
2. Siapkan headroom RAM dan lokasi cache/temp di D:. Jangan install ke existing ingestion .venv. Pilih interpreter 3.12 secara eksplisit.
3. Setelah instalasi diotorisasi, buat isolated env; resolve direct pins di atas, rekam seluruh transitive versions, source index dan hashes; jalankan pip check. Buat lock retrieval terpisah, tanpa mengubah ingestion lock.
4. Gate GPU: cek PyTorch build CUDA 12.6, capability/architecture, kernel kecil dan output finite. Jika tidak kompatibel, gunakan CPU build; jangan mencoba CUDA 13 pada Pascal.
5. Setelah download diotorisasi, pin model revision, verifikasi hash weights, hitung actual token length seluruh chunks dan tetapkan sequence cap tanpa truncation tersembunyi.
6. Smoke inference chunk terpanjang pada GPU FP16 dan CPU FP32 jika tersedia; ukur peak RAM/VRAM dan waktu nyata. Tetapkan satu device/precision per run setelah melihat hasil; CPU/GPU boleh dilaporkan sebagai varian terpisah.
7. Implementasi baru boleh dimulai setelah environment dan konfigurasi tersebut siap. R5/R6 dapat ditunda; core R1–R4 cukup untuk preliminary retrieval benchmarking.

## Snapshot integrity dan batas audit

Snapshot berisi 50 source documents, 50 canonical documents, 371 chunks, corpus_version v1-draft, status pending_practitioner_validation. Existing quality audit mencatat orphan candidates 0, near-duplicate candidates 0 dan coverage 768/768; ini evidence existing, bukan audit kualitas semantik baru. Practitioner validation tetap pending dan snapshot hanya untuk preliminary retrieval benchmarking, bukan final validated thesis dataset.

Aggregate fingerprint: `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`.

| Artifact | SHA-256 yang diverifikasi |
|---|---|
| data/source_corpus/corpus_manifest.json | 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f |
| data/processed/documents.jsonl | 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01 |
| data/chunks/chunks.jsonl | 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0 |
| experiments/configs/pilot.toml | 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26 |

Protected baseline: 117 existing repository files di luar .venv/.git, termasuk source corpus, parser/chunker, canonical/chunks, configuration, snapshot dan existing reports. Verifikasi sesudah penulisan membandingkan SHA-256, ukuran dan mtime terhadap baseline sebelum audit; hanya laporan ini boleh menjadi file baru. Inventory package juga diperiksa ulang tanpa install/upgrade.

**Hasil verifikasi: PASS.** Seluruh 117 file existing memiliki SHA-256, ukuran dan mtime yang identik; tidak ada file missing atau file baru lain selain laporan ini. Package inventory tetap sama dan pip check kembali lolos.

Tidak dilakukan download weights, instalasi/upgrade, implementasi retrieval, perubahan file protected, commit, push, PR atau deploy. Runtime PyTorch cu126 Windows, load BGE-M3, actual tokenizer lengths, peak inference memory dan performa belum diuji. Risiko utama: RAM bebas rendah, C: hampir penuh, serta dukungan kernel dan OOM pada GPU Pascal 4 GB yang harus dibuktikan melalui smoke test.
