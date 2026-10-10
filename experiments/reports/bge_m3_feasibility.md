# Milestone 5 — BGE-M3 feasibility

## Hasil terbaru — GPU inference smoke test PASS

Test: **2026-10-08T22:20:13.603761+08:00** sampai **2026-10-08T22:21:25.444923+08:00**. Pengguna secara eksplisit mengizinkan satu percobaan GPU dengan RAM sekitar 4 GiB, menggantikan gate sebelumnya 6 GiB untuk test ini. Tidak ada instalasi/download ulang atau retry. Satu proses model, checkpoint lokal, tanpa network (HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1).

| Pemeriksaan | Hasil aktual |
|---|---|
| GPU model loading | **PASS**, 47.076 s, termasuk konstruksi CPU dari checkpoint lokal dan transfer CUDA; import library di luar timer |
| Short inference, max_length cap 128 | **PASS**, tiga input, batch size 1 |
| Medium/long inference, max_length cap 640 | **PASS**, 145 dan 588 token termasuk special tokens; tanpa truncation |
| CPU FP32 fallback | **NOT RUN**, GPU berhasil; CPU model tidak dimuat |
| Embedding dimension / aggregate short shape | **1024 / (3, 1024)**; setiap forward (1, 1024) |
| Numerical validity | Seluruh output finite; tanpa NaN/Inf; norm sekitar 1 (0.99978–1.00011) |
| Repeat consistency | Input pertama pada warm-up dan timed inference: maximum absolute difference **0.0** |
| Error / OOM / retry | Tidak ada |
| Maksimum input neural yang diuji | **588 token**, bukan 640 token aktual; 640 adalah cap konfigurasi |

### Resource dan pemantauan

| Pengukuran | Nilai |
|---|---|
| RAM available sebelum import/loading | 4.227 GiB (4,538,499,072 bytes) |
| Windows memory load sebelum test | 73% |
| Windows commit headroom sebelum test | 10.367 GiB |
| GPU VRAM total / used / free sebelum test | 4096 / 0 / 4007 MiB |
| C: / D: free sebelum test | 14.527 / 845.943 GiB |
| Peak process working set (Windows OS high-water mark) | **4.136 GiB** (4,440,920,064 bytes) |
| Peak process RSS, sampled | 4.135 GiB |
| Minimum available system RAM, sampled | **0.999 GiB** (1,073,160,192 bytes) |
| Minimum Windows commit headroom, sampled | 5.290 GiB |
| Peak PyTorch GPU allocated / reserved | **1106.65 / 1132.00 MiB** |
| Maximum observed GPU device used memory, nvidia-smi | **1191 MiB** (device-wide; not process attribution) |
| GPU after cleanup while test process still alive | 79 MiB used; CUDA context remains until process exit |

RAM/commit sampled approximately every 200 ms; GPU device memory approximately every 2 seconds plus synchronous readings after loading/inference. Watchdog stops only its own test process if available RAM <768 MiB, commit headroom <1 GiB, or memory load >=97% persists >=2 seconds. This is a local safety policy, not an official model minimum. No guard fired. Sampled values may miss brief system peaks; Windows peak working set and PyTorch allocator high-water marks provide separate measurements. No GPU process-memory attribution available in this test. No claim that paging was absent: paging/page-fault rates were not measured. No applications were killed or files cleaned.

**RAM margin was narrow during loading:** available memory reached approximately 1.00 GiB. Passing this one test does not establish repeated-run stability when other applications consume more RAM.

### Environment dan inference path

Existing `.venv-ml`: Python 3.12.14; torch **2.12.1+cu126**, CUDA runtime **12.6**, FlagEmbedding **1.4.2**, Transformers **4.57.6**. GPU **NVIDIA GeForce GTX 1050**, capability 6.1; supported build architectures: sm_50, sm_60, sm_61, sm_70, sm_75, sm_80, sm_86, sm_90. No package, driver, CUDA Toolkit, or system configuration changes.

Model: **BAAI/bge-m3**, pinned revision **5617a9f61b028005a4858fdac845db406aefb181**.

Local checkpoint: `D:\ModelCache\huggingface\hub\models--BAAI--bge-m3\snapshots\5617a9f61b028005a4858fdac845db406aefb181`.

Official `BGEM3FlagModel` loads FP16 weights; model explicitly moved to `cuda:0` and set to eval. Forward uses its official `EncoderOnlyEmbedderM3ModelForInference` under `torch.inference_mode()`, `return_dense=True`, `return_sparse=False`, `return_colbert_vecs=False`, batch size 1. The installed `encode_single_device()` wrapper contains automatic RuntimeError/OOM batch-size retries; this smoke test directly calls the same inference model to avoid retry. No library source was patched. Sparse/ColBERT heads are present in the official loaded model, but their outputs/computation paths are disabled.

Official reference: [BAAI BGE-M3 model card and FlagEmbedding usage](https://huggingface.co/BAAI/bge-m3).

### Inputs, timing dan truncation

Short Indonesian WO inputs:

1. Koordinator acara memastikan seluruh vendor hadir sebelum briefing terakhir.
2. PIC pengantin mendampingi pasangan dan melaporkan perubahan jadwal kepada Event Coordinator.
3. Tim logistik memeriksa perlengkapan dekorasi dan jalur evakuasi sebelum tamu datang.

One warm-up on short input 1, followed by one measured inference for each short input. The timed inference region includes CPU-to-GPU input transfer and synchronized GPU forward, excludes tokenizer, output conversion/validation, resource probes, and report I/O. Latencies are single observations, not statistical estimates or retrieval benchmark results. Warm-up is reported separately; different sequence lengths may still initialize additional kernels/workspaces.

| Input | Actual tokens incl. special | max_length cap | Inference seconds | Peak allocated MiB | Peak reserved MiB | GPU used MiB after forward |
|---|---|---|---|---|---|---|
| warmup_short_1 | 14 | 128 | 4.111906 | 1093.46 | 1110.00 | 1169 |
| short_1 | 14 | 128 | 0.037050 | 1093.46 | 1110.00 | 1169 |
| short_2 | 18 | 128 | 0.158532 | 1093.55 | 1110.00 | 1169 |
| short_3 | 16 | 128 | 0.033548 | 1093.51 | 1110.00 | 1169 |
| medium | 145 | 640 | 0.109328 | 1097.73 | 1112.00 | 1171 |
| longest | 588 | 640 | 0.355673 | 1106.65 | 1132.00 | 1191 |

Short measured total: **0.229130 s**, batch size 1, three sequential inputs. Warm-up **4.111906 s** is excluded from this total.

Actual tokenizer used with `add_special_tokens=True`, `truncation=False`, `padding=False`; assertions require token count <= cap before GPU allocation. Single-input lengths include XLM-R special tokens. No artificial padding to 128/640 and no token truncation occurred.

Frozen chunks were read only to tokenize/select samples; only two real chunk representations underwent neural inference:

- Medium: **WO-DOC-028-C001**, 145 tokens (median by audited scenario B length).
- Longest: **WO-DOC-042-C005**, 588 tokens.

Scenario B serialization uses actual LF newline characters, not literal backslash-n:

```text
Judul: {title}
Heading: {heading}
Konteks kategori: {category}

{text}
```

All fields come directly from existing chunks. This remains a diagnostic representation, not approval of a final benchmark input protocol. Prior tokenizer audit: 371 chunks; scenario A max544 and scenario B max588, zero overflow at640. This test validates full neural inference on the longest audited B input, not embedding the complete corpus.

### Recommendation dan limitations

**Local GPU feasible for this bounded dense-only smoke test:** use `cuda:0`, FP16, batch size **1**, candidate cap **640**, verify actual token length and forbid silent truncation. Retain resource monitoring and avoid concurrent model instances. Loading took approximately47 s and transient host RAM use was substantial; repeat resource checks before a future run. No increase in batch size, sparse/multi-vector enablement, or full-corpus run is authorized by this result.

Google Colab or another GPU environment is a reasonable alternative if the local loading RAM margin cannot be maintained, or if longer/repeated experiments are needed. This is a recommendation based on the measured local margin; no Colab runtime was provisioned/tested and no cloud performance/capacity is claimed. Keep the same pinned model revision, protocol, and corpus fingerprint if a later cloud experiment is approved.

CPU FP32 remains **NOT RUN**, not PASS. No need for fallback was observed on these GPU samples, and no CPU model was loaded simultaneously. CPU feasibility must be assessed separately if GPU later fails. No retrieval effectiveness, throughput benchmark, or full-corpus stability claim follows from these smoke latencies.

### Research integrity verification

After test: **84 protected files checked, 0 changed**, including all files under `data/source_corpus/`, canonical documents, frozen chunks, source implementation, pilot config, snapshot files and ML environment manifest. All four key artifact hashes match the frozen snapshot.

- Snapshot ID: **WO-CORPUS-V1-DRAFT-PILOT-001**; practitioner validation remains pending.
- Snapshot JSON SHA-256: **279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e**.
- Aggregate fingerprint: **7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40** (unchanged).
- No corpus/chunking change, corpus embedding/indexing, query/qrels creation, retrieval implementation/evaluation, commit, push, PR or deployment.

Execution evidence outside repository: `D:\ModelCache\tmp\bge_gpu_smoke.py`, `bge_gpu_smoke_result.json`, `.jsonl` event log, and `bge_inference_integrity_before.json` / `bge_inference_integrity_after.json`. No embedding vectors were persisted. Only this report was intentionally updated in the repository.

**STOP after GPU smoke test.** GPU loading/short/long samples PASS; CPU and full-corpus/retrieval tests NOT RUN.

---

## Historical results — superseded resource gate and preparation

The sections below retain earlier measurements. The latest authorized GPU result above supersedes their inference NOT RUN status; preparation/tokenizer findings remain historical evidence.

## Tahap 3 — Resource preflight: STOP

Pemeriksaan aktual: **2026-10-08T22:12:56.3570068+08:00**. RAM tersedia **4.1028 GiB (4,409,749,504 bytes)**, di bawah gate konservatif **6 GiB**. Model tidak dimuat; batas tidak diturunkan. Tidak ada instalasi/download ulang, penghentian aplikasi, atau pembersihan file/cache.

| Resource sebelum test | Hasil aktual |
|---|---|
| Available RAM | 4.1028 GiB; gate FAIL |
| C: free | 15,609,638,912 bytes (14.54 GiB) |
| D: free | 908,324,290,560 bytes (845.94 GiB) |
| GPU | NVIDIA GTX 1050, capability 6.1 |
| NVIDIA driver | 581.80 |
| GPU memory total / used / free | 4096 / 0 / 4007 MiB, menurut nvidia-smi |
| Python isolated environment | .venv-ml, Python 3.12.14 |
| Installed versions (package metadata) | torch 2.12.1+cu126; FlagEmbedding 1.4.2; transformers 4.57.6 |

| Tahap inference yang diminta | Status |
|---|---|
| GPU model loading | NOT RUN — RAM gate FAIL |
| GPU short inference dan warm-up | NOT RUN |
| GPU medium/long-input inference, max_length=640 | NOT RUN |
| CPU FP32 fallback | NOT RUN |
| Embedding shape/dimension dan finite-value verification | NOT RUN |
| Actual neural input token length / truncation verification | NOT RUN |
| Model loading/inference latency | Tidak diukur |
| Peak process RAM / GPU allocated/reserved memory saat inference | Tidak diukur |

Tidak ada error model/CUDA dari percobaan ini karena model belum dijalankan. VRAM di atas merupakan pembacaan idle preflight, bukan peak inference. CUDA PASS dan tokenizer PASS pada riwayat di bawah tidak membuktikan inference BGE-M3 PASS. Maksimum 588 token pada audit tokenizer sebelumnya juga bukan panjang input neural yang sudah berhasil diuji.

Konfigurasi rencana tetap **cuda:0, FP16, batch size 1, dense-only, sparse/ColBERT disabled, max_length=640**. Konfigurasi ini belum tervalidasi untuk model inference pada GTX 1050. CPU FP32 tetap fallback bersyarat setelah model GPU dilepas dan resource diperiksa. Pengguna perlu menutup aplikasi yang tidak diperlukan secara manual, lalu RAM diperiksa kembali; jangan load model sebelum tersedia minimal 6 GiB.

Snapshot JSON SHA-256 tetap **279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e**. Keempat key artifact cocok dengan snapshot; aggregate fingerprint tetap **7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40**. Tidak ada perubahan corpus, canonical documents, chunks, pilot config, snapshot, atau ingestion environment. Tidak ada embedding/indexing corpus atau implementasi retrieval.

**STOP pada resource gate. BGE-M3 belum dinyatakan siap untuk inference/retrieval.**

---

## Riwayat persiapan — hasil sebelum Tahap 3

Resource dan timestamp pada bagian berikut adalah hasil persiapan sebelumnya, bukan pembacaan preflight terbaru.

Updated: 2026-10-08T22:06:43.505180+08:00

**Persiapan PASS:** dependency dry-run, instalasi, pip check, import resmi FlagEmbedding, CUDA regression, download pinned model, dan tokenizer-only audit selesai. **Model loading/inference belum dilakukan**, sesuai instruksi STOP setelah persiapan. Milestone inference belum selesai.

## 1. Scope dan status

| Pemeriksaan | Hasil |
|---|---|
| Isolated environment | Existing .venv-ml, Python 3.12.14 di D: |
| Dependency dry-run / instalasi | PASS / PASS |
| ML pip check | PASS — No broken requirements found |
| Official BGEM3FlagModel import | PASS; public alias mengarah ke class M3Embedder; tidak dibuat instance |
| Torch / runtime | **2.12.1+cu126 / CUDA 12.6**, tidak di-upgrade/downgrade/reinstall |
| CUDA regression | **PASS**, FP32 dan FP16 operasi kecil |
| Model/tokenizer download dan hashes | **PASS** |
| Tokenizer 371 frozen chunks | **PASS**, tanpa truncation/padding |
| BGE-M3 GPU / CPU inference | **NOT RUN / NOT RUN** |
| Neural model loading / embedding shape / model latency | N/A |
| Model peak RAM / VRAM | N/A |

Tidak ada embeddings corpus, indexing, query/qrels, retrieval, benchmark performance, training atau aplikasi RAG/LLM dibuat.

## 2. Exact root cause dan constraint yang diperbaiki

Dry-run sebelumnya membekukan seluruh dependency existing, termasuk fsspec==2026.7.0, sambil memilih transformers==4.57.6 dan huggingface-hub==0.36.2. Kombinasi constraints ini menghalangi resolver:

- datasets 5.1.0 memerlukan huggingface-hub >=1.31.0,<3, bertentangan dengan hub 0.36.2 dan requirement Transformers 4.57.6 untuk hub <1.
- Versi datasets yang cocok dengan hub 0.36.2 membatasi versi fsspec lebih rendah; pembekuan fsspec 2026.7.0 mencegah pemilihan tersebut.
- Ini conflict dari constraints awal, bukan bukti incompatibility PyTorch/Pascal.

Pada percobaan sukses, pembekuan transitive fsspec dan pin NumPy/SciPy/scikit-learn lama dilepas. Constraint mutlak tetap **torch==2.12.1+cu126**. API stack inference dipilih secara eksplisit: FlagEmbedding 1.4.2, Transformers 4.57.6, SentenceTransformers 5.2.0, Hugging Face Hub 0.36.2, PEFT 0.18.1. Tujuannya mempertahankan stack Transformers 4.x yang konsisten; dependency numerik/transitive lain dipilih resolver.

Resolver memilih **datasets 5.0.1 dan fsspec 2026.6.0**. datasets 5.0.1 membatasi fsspec <=2026.6.0. Perubahan transitive existing yang diperlukan: **fsspec 2026.7.0 → 2026.6.0**, sesuai persetujuan perbaikan dependency.

Dry-run exit code 0; **53 package baru/berubah**, seluruhnya wheel. Daftar install plan diverifikasi secara programatik tidak mengandung package torch sebelum menjalankan instalasi. Versi resolved kemudian dipin dalam constraint temporary agar instalasi mengikuti rencana. Pip menyatakan torch already satisfied; tidak ada uninstall/install torch. Tidak memakai --no-deps, --force-reinstall, CUDA Toolkit global atau perubahan driver.

Sumber primary: [FlagEmbedding setup](https://github.com/FlagOpen/FlagEmbedding/blob/master/setup.py), [datasets 5.1.0 metadata](https://pypi.org/pypi/datasets/5.1.0/json), [datasets 5.0.1 metadata](https://pypi.org/pypi/datasets/5.0.1/json).

## 3. Installation dan reproducibility manifest

Library resmi **FlagEmbedding 1.4.2** berhasil dipasang dan diimport, sehingga tidak perlu beralih ke alternatif SentenceTransformers dense-only. SentenceTransformers tetap terpasang sebagai dependency FlagEmbedding. Ini tidak membuktikan sparse/multi-vector inference telah diuji.

Environment lock/manifest terpisah:

[ml_environment.lock.json](D:/Project/wo-retrieval-benchmark/experiments/configs/ml_environment.lock.json)

Manifest mencatat seluruh versi installed, resolved wheel URLs/SHA-256, provenance torch cu126, CUDA test, model revision/files/hashes, tokenizer summary dan resource state. Ini JSON manifest, bukan requirements file yang langsung dikonsumsi pip. Untuk reproduksi: pasang Python 3.12.14 dan torch dari official cu126 index lebih dahulu, lalu remaining exact versions dengan torch constraint yang sama.

Temporary resolver artifacts di D:\ModelCache\tmp:

- bge_stageA_constraints.txt — API stack dan immutable torch constraint.
- bge_stageA_plan.json — pip dry-run report.
- bge_stageA_resolved.txt — exact resolved constraints untuk instalasi.

Command inti, dengan environment variables berikut diset sebelum subprocess:

```powershell
.\.venv-ml\Scripts\python.exe -B -m pip install --dry-run --report D:\ModelCache\tmp\bge_stageA_plan.json -c D:\ModelCache\tmp\bge_stageA_constraints.txt --index-url https://pypi.org/simple --disable-pip-version-check 'FlagEmbedding==1.4.2'
.\.venv-ml\Scripts\python.exe -B -m pip install -c D:\ModelCache\tmp\bge_stageA_resolved.txt --only-binary=:all: --index-url https://pypi.org/simple --disable-pip-version-check 'FlagEmbedding==1.4.2'
.\.venv-ml\Scripts\python.exe -B -m pip check
```

| Session-local variable | Lokasi/nilai |
|---|---|
| HF_HOME | D:\ModelCache\huggingface |
| HF_HUB_CACHE | D:\ModelCache\huggingface\hub |
| TORCH_HOME | D:\ModelCache\torch |
| PIP_CACHE_DIR | D:\ModelCache\pip |
| TEMP dan TMP | D:\ModelCache\tmp |
| PYTHONDONTWRITEBYTECODE | 1 |
| HF_HUB_DISABLE_XET | 1, jalur HTTP resmi |
| HF_HUB_DOWNLOAD_TIMEOUT | 120 seconds |

Variabel tersebut diterapkan pada setiap subprocess instalasi/download/tokenizer/regression. Tidak mengubah environment variables global. Aktivasi .venv-ml saja tidak otomatis mengatur cache; set ulang pada proses berikutnya. Runtime Python dasar existing tetap runtime terkelola Codex; path interpreter/versi tercatat di manifest.

### Final installed package versions

| Package | Version |
|---|---|
| FlagEmbedding | 1.4.2 |
| Jinja2 | 3.1.6 |
| MarkupSafe | 3.0.3 |
| PyYAML | 6.0.3 |
| accelerate | 1.15.0 |
| aiohappyeyeballs | 2.7.1 |
| aiohttp | 3.14.4 |
| aiosignal | 1.4.0 |
| anyio | 4.15.1 |
| attrs | 26.1.0 |
| certifi | 2026.7.22 |
| charset-normalizer | 3.5.2 |
| cloudpickle | 3.1.2 |
| colorama | 0.4.6 |
| datasets | 5.0.1 |
| dill | 0.4.1 |
| filelock | 3.32.3 |
| frozenlist | 1.8.0 |
| fsspec | 2026.6.0 |
| h11 | 0.16.0 |
| httpcore | 1.0.9 |
| httpx | 0.28.1 |
| huggingface_hub | 0.36.2 |
| idna | 3.20 |
| ir_datasets | 0.6.3 |
| joblib | 1.6.0 |
| lxml | 6.1.3 |
| lz4 | 4.4.5 |
| mpmath | 1.3.0 |
| multidict | 6.9.1 |
| multiprocess | 0.70.19 |
| narwhals | 2.26.0 |
| networkx | 3.6.1 |
| numpy | 2.5.3 |
| packaging | 26.3 |
| pandas | 3.0.6 |
| peft | 0.18.1 |
| pip | 25.0.1 |
| propcache | 0.5.4 |
| protobuf | 7.36.2 |
| psutil | 7.2.2 |
| pyarrow | 25.0.1 |
| python-dateutil | 2.9.0.post0 |
| regex | 2026.9.29 |
| requests | 2.34.2 |
| safetensors | 0.8.0 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| sentence-transformers | 5.2.0 |
| sentencepiece | 0.2.2 |
| setuptools | 78.1.0 |
| six | 1.17.0 |
| sympy | 1.14.0 |
| threadpoolctl | 3.7.0 |
| tokenizers | 0.22.2 |
| torch | 2.12.1+cu126 |
| tqdm | 4.70.1 |
| transformers | 4.57.6 |
| typing_extensions | 4.16.0 |
| tzdata | 2026.5 |
| urllib3 | 2.8.0 |
| xxhash | 4.0.1 |
| yarl | 1.25.1 |

Kedua environment, ML dan ingestion, kembali lolos pip check pada pemeriksaan akhir.

## 4. PyTorch/CUDA regression aktual

GTX 1050, NVIDIA driver 581.80, capability (6,1). torch.cuda.is_available()=True.
Compiled architectures: sm_50, sm_60, sm_61, sm_70, sm_75, sm_80, sm_86, sm_90; **sm_61 tersedia**.

- CUDA arange(16): PASS, device cuda:0 dan nilai 0..15.
- FP32 2×3 @ 3×2: PASS; result [[58,64],[139,154]] tepat sama dengan expected, finite.
- FP32 256×256 ones @ ones: PASS; semua elemen 256, finite.
- FP16 matrix kecil: PASS; hasil expected yang sama, finite.
- CPU matrix kecil: PASS; ini bukan CPU model inference.

Peak allocator CUDA regression: **9.31 MiB allocated / 22.00 MiB reserved**.
Peak process working set regression: **680.46 MiB**, diukur dengan Windows GetProcessMemoryInfo.

Peak tersebut untuk import torch dan test tensor kecil, **bukan BGE-M3**. Torch allocator tidak mencakup seluruh driver/context/library overhead. CUDA process keluar setelah test; GPU tidak memegang model weights.

## 5. Official BGE-M3 download

- Model repository: **BAAI/bge-m3**.
- Exact verified available revision: **5617a9f61b028005a4858fdac845db406aefb181**.
- Source: Hugging Face resmi, menggunakan huggingface_hub.snapshot_download dengan revision eksplisit.
- Cache snapshot path: `D:\ModelCache\huggingface\hub\models--BAAI--bge-m3\snapshots\5617a9f61b028005a4858fdac845db406aefb181`.
- **Actual verified payload: 2,295,419,991 bytes = 2.295 GB desimal / 2.14 GiB, 12 files**.
- Checkpoint pytorch_model.bin: **2,271,145,830 bytes**.
- Verified checkpoint SHA-256: **b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38**.
- Download plus file verification elapsed: 1186.43 seconds; ini waktu persiapan, bukan model loading/inference atau benchmark retrieval.

Payload dihitung dari ukuran file aktual, bukan network wire bytes/HTTP overhead. File tokenizer/config kecil disiapkan terpisah saat checkpoint masih ditransfer, sehingga tokenizer audit dapat berjalan tanpa weights neural. Download memakai satu worker per proses; library cache locks menghindari penulisan file yang sama secara bersamaan.

Ukuran setiap file dibandingkan metadata pinned commit. SHA-256 seluruh file dihitung secara streaming; lima LFS files cocok dengan published SHA-256. Tujuh file kecil Git diverifikasi dengan Git blob SHA-1 terhadap commit metadata. **Semua 12 file cocok dengan upstream.** Full hashes tersedia di environment manifest.

| Required native model/tokenizer file | Bytes | Upstream hash |
|---|---:|---|
| 1_Pooling/config.json | 191 | PASS (Git blob SHA-1) |
| colbert_linear.pt | 2100674 | PASS (LFS SHA-256) |
| config.json | 687 | PASS (Git blob SHA-1) |
| config_sentence_transformers.json | 123 | PASS (Git blob SHA-1) |
| modules.json | 349 | PASS (Git blob SHA-1) |
| pytorch_model.bin | 2271145830 | PASS (LFS SHA-256) |
| sentence_bert_config.json | 54 | PASS (Git blob SHA-1) |
| sentencepiece.bpe.model | 5069051 | PASS (LFS SHA-256) |
| sparse_linear.pt | 3516 | PASS (LFS SHA-256) |
| special_tokens_map.json | 964 | PASS (Git blob SHA-1) |
| tokenizer.json | 17098108 | PASS (LFS SHA-256) |
| tokenizer_config.json | 444 | PASS (Git blob SHA-1) |

Checkpoint, tokenizer, model config, sentence-transformer modules/pooling dan official sparse/ColBERT head files lengkap untuk native checkpoint ini. ONNX/export variants tidak diunduh. Keberadaan head files bukan hasil uji sparse/multi-vector inference.

Windows tidak mendukung cache symlink pada konfigurasi saat ini; Hugging Face memberi warning cache degraded yang dapat menambah penggunaan storage. Tidak mengaktifkan Developer Mode, meminta admin, atau membersihkan cache pengguna. Ruang D: tetap mencukupi.

## 6. Tokenizer-only audit — 371 frozen chunks

Tokenizer **XLMRobertaTokenizerFast**, pinned revision yang sama, use_fast=True, local_files_only=True, trust_remote_code=False. Tidak membuat AutoModel/BGEM3FlagModel instance dan tidak membaca weights ke model neural.

Perhitungan: add_special_tokens=True, **2 special tokens per single input**, truncation=False, padding=False. Tokenizer model_max_length=8192; sentence_bert_config max_seq_length=8192; model config max_position_embeddings=8194 (bukan izin input 8194 tokens). P95 memakai nearest rank: sorted_values[ceil(0.95*N)-1].

Skenario A: chunk.text persis sebagaimana tersimpan, tanpa normalization atau prefix tambahan.

Skenario B, serialization deterministik di memory:

```text
Judul: {title}
Heading: {heading}
Konteks kategori: {category}

{text}
```

Context berasal dari field category existing; tidak menambahkan ringkasan/informasi buatan, manifest, inventory atau audit report. Title/heading/category memakai nilai string existing; newline LF seperti format di atas. **Skenario B diagnostik saja, belum final benchmark protocol.** chunks.jsonl tidak ditulis ulang.

| Statistik, termasuk special tokens | A: text saja | B: title + heading + kategori + text |
|---|---:|---:|
| N | 371 | 371 |
| Minimum | 55 | 90 |
| Median | 108 | 145 |
| Mean | 166.353100 | 204.283019 |
| P95 | 468 | 514 |
| Maximum | **544** | **588** |

Tambahan context: min 28, median 37, mean 37.929919, p95 50, max 57 tokens.
Chunk terpanjang pada kedua skenario: **WO-DOC-042-C005**.

### Truncation risk

Overflow didefinisikan token count **> max_length**. Tidak ada truncation aktual yang diterapkan dalam audit.

| max_length | A overflow | B overflow |
|---:|---:|---:|
| 512 | 1 | 19 |
| 640 | 0 | 0 |
| 1024 | 0 | 0 |
| 2048 | 0 | 0 |
| 8192 | 0 | 0 |

A pada cap 512: WO-DOC-042-C005.
B pada cap 512 (19 chunks):

- WO-DOC-006-C002
- WO-DOC-006-C003
- WO-DOC-006-C004
- WO-DOC-025-C002
- WO-DOC-025-C003
- WO-DOC-025-C004
- WO-DOC-026-C002
- WO-DOC-026-C003
- WO-DOC-026-C004
- WO-DOC-026-C005
- WO-DOC-034-C003
- WO-DOC-038-C004
- WO-DOC-040-C003
- WO-DOC-040-C004
- WO-DOC-042-C002
- WO-DOC-042-C003
- WO-DOC-042-C004
- WO-DOC-042-C005
- WO-DOC-042-C006

Audit berhasil tanpa model inference. Durasi tokenizer-only audit 1.975 seconds, bukan latency embedding/retrieval. Detail hitungan per chunk disimpan sebagai working audit data di D:\ModelCache\tmp\bge_tokenizer_audit_result.json; summary, serialization dan affected IDs dicatat permanen di laporan/manifest ini.

## 7. Resource gate dan rekomendasi

Latest resource reading: **2026-10-08T22:06:43.505180+08:00**.

| Resource | Aktual |
|---|---|
| Available RAM | 4912472064 bytes / **4.58 GiB** |
| C: free | **14.54 GiB** |
| D: free | **845.94 GiB** |
| GPU used/free/total | 0 / 4007 / 4096 MiB |
| Margin available RAM >=6 GiB | **NOT MET** |
| Model loading / inference | NOT RUN sesuai scope STOP setelah persiapan |

Rekomendasi calon smoke test berikutnya: cuda:0, FP16, batch size 1, dense-only, return_sparse=False, return_colbert_vecs=False, eval/inference mode dan attention konservatif. CPU FP32 batch 1 tetap fallback bila GPU gagal dan RAM cukup; **CPU model inference belum PASS**, hanya CPU tensor test yang telah PASS.

Berdasarkan tokenizer aktual, **candidate max_length=640** mencakup seluruh chunk pada A/B, termasuk special tokens. Cap 1024 juga nol overflow dan dapat dipilih jika protocol memerlukan headroom tambahan; default 512 tidak aman untuk seluruh snapshot. Cap ini belum diubah pada model/config dan belum dibekukan untuk benchmark. Gunakan dynamic padding, jangan mengasumsikan proxy token chars/4 setara dengan tokenizer BGE-M3. Perubahan serialization context harus diaudit ulang.

Sebelum percobaan model pertama, recheck available RAM dengan target konservatif >=6 GiB; CPU fallback membutuhkan headroom lebih besar (target konservatif >=8 GiB). Jangan mematikan proses/menghapus file pengguna otomatis. Sesudah resource dan izin inference tersedia, uji tiga teks Indonesia serta input terpanjang dengan batch 1, catat model load time terpisah dari inference dan actual peak memory. GTX 1050 4 GB dapat tetap OOM pada model, meskipun CUDA matmul dan tokenizer telah PASS. Tidak ada klaim bahwa GPU lebih cepat dari CPU.

## 8. Research integrity dan perubahan file

**Integrity PASS.** Seluruh **118 existing protected repository files** memiliki SHA-256, ukuran dan mtime identik terhadap baseline percobaan ini. Seluruh **1822 files ingestion .venv** memiliki aggregate hash atas path/content/size/mtime identik. Tidak ada perubahan source corpus, canonical documents, chunks, pilot config, pilot snapshot atau chunking implementation.

Snapshot **WO-CORPUS-V1-DRAFT-PILOT-001**, 371 frozen chunks, corpus v1-draft, status **pending_practitioner_validation**. Dataset tetap preliminary research snapshot; practitioner validation masih pending.

Snapshot JSON SHA-256 identik: `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e`.

Key artifact hashes kembali cocok:

| Artifact | SHA-256 |
|---|---|
| corpus_manifest.json | 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f |
| documents.jsonl | 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01 |
| chunks.jsonl | 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0 |
| pilot.toml | 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26 |

Repository changes hanya update laporan ini dan file baru experiments/configs/ml_environment.lock.json. Changes yang diizinkan di luar protected files: package .venv-ml, model/pip cache dan working temporary artifacts di D:\ModelCache. Tidak ada commit, push, PR atau deploy.

**STOP setelah persiapan.** Environment dan tokenizer siap; neural model loading/inference masih menunggu resource check dan instruksi berikutnya.
