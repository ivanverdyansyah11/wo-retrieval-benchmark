# Milestone 8A — Retrieval foundation, TF-IDF dan BM25

**PASS untuk implementasi, indexing dan sanity check teknis lexical.** R1/R2 memakai 371 frozen chunks dari snapshot WO-CORPUS-V1-DRAFT-PILOT-001. Corpus tetap v1-draft / pending_practitioner_validation; seluruh 18 queries tetap draft_pending_expert_review. Tidak ada qrels atau metrik efektivitas.

## Scope dan file created/changed

Otorisasi pengguna Milestone 8A terbatas untuk R1/R2. Flag implementation_authorized=false pada protokol desain lama tidak diedit; tidak ada otorisasi implisit untuk R3/R4/evaluasi. Parameter protokol tetap byte-identical.

- Created: src/wo_retrieval/retrieval/{__init__,text,lexical,cli}.py.
- Created: tests/test_lexical_retrieval.py dan experiments/configs/lexical_environment.lock.txt.
- Created: experiments/indexes/R1/{documents.json,model.json,matrix.npz,manifest.json} dan experiments/indexes/R2/{documents.json,model.json,manifest.json}.
- Created: laporan ini dan experiments/reports/milestone_8a_lexical_audit.json, termasuk source locator lengkap hasil sanity.
- Changed: pyproject.toml (optional lexical extra, entry point wo-retrieve) dan README.md (arsitektur, CLI dan tests). Parser/chunker existing tidak berubah.

## Dependency dan environment

Windows, Intel Core i7-7700HQ, Python 3.12.14. CPU saja; OMP/OPENBLAS/MKL_NUM_THREADS=4. .venv-ml existing dengan PYTHONPATH=src. Tidak ada import torch, transformers atau FlagEmbedding dalam proses indexing/sanity.

| Package | Actual version |
|---|---|
| scikit-learn | 1.9.1 |
| rank-bm25 | 0.2.2 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| joblib | 1.6.0 |
| threadpoolctl | 3.7.0 |

Hanya rank-bm25==0.2.2 ditambahkan setelah dry-run menunjukkan satu package ini saja. Install PASS; pip check PASS: No broken requirements found. Official PyPI wheel SHA-256: 7bd4a95571adadfc271746fa146a4bcfd89c0cf731e49c3d1ad863290adbe8ae. PIP_CACHE_DIR=D:/ModelCache/pip, TMP/TEMP=D:/ModelCache/tmp, HF_HOME=D:/ModelCache/huggingface pada setiap subprocess pip. Tidak ada checkpoint download.

PyTorch 2.12.1+cu126, FlagEmbedding 1.4.2, Transformers 4.57.6 tetap. Seluruh 1.038 file existing .venv dan 26.674 file existing .venv-ml mempertahankan size/mtime_ns (pycache dikecualikan); file baru ML hanya rank_bm25 module/dist-info. Ini stat check environment, bukan rehash seluruh DLL/model. .venv ingestion tidak diubah.

Referensi API/formula: [sklearn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html), [rank-bm25 0.2.2 resmi](https://pypi.org/project/rank-bm25/0.2.2/), [source BM25 resmi](https://github.com/dorianbrown/rank_bm25/blob/master/rank_bm25.py). Versi actual dan formula diverifikasi dengan fixture matematis.

## Architecture dan serializer

text.py menyediakan serializer allowlist dan tokenizer bersama; lexical.py menyediakan structural Retriever Protocol, RetrievalResult, R1/R2, build/load/audit; cli.py menyediakan argparse CLI. RetrievalResult berisi method_id,chunk_id,document_id,rank,score,snapshot_id.

Policy wo_operational_context_dedup_v1: NFC, newline LF, strip luar saja. Seleksi heading→title→category; suppress jika seluruh nilai field ada di body/field terpilih memakai casefold, collapsed Unicode whitespace, dan batas (?<!\w)...(?!\w). Emisi title→heading→category dengan label protokol, LF dan blank line sebelum body. Semua normalized body dipertahankan, termasuk pengulangan internal.

Hanya title/heading/category/text menjadi retrievable input. Guide_context audit-only; tidak diinjeksikan. Panduan operasional yang sudah dalam body tetap utuh. Semua 63 XLSX mempertahankan Sheet/Header/Row context; 53 mempunyai guide metadata. File/locator disimpan sebagai metadata inspeksi terpisah; status, reviewer, provenance administratif dan evidence tidak diinjeksikan.

String hasil serializer dibandingkan langsung dengan implementasi audit sebelumnya: **371/371 identik**, tanpa menjalankan tokenizer neural. Fingerprint historis 2f4e59835ad4cf81e84f60a5177b6b721c821ddc23970b484de01dd23613ef37 juga memuat token count BGE-M3; tidak dihitung ulang. Hash lexical berikut mempunyai payload berbeda dan tidak disamakan dengan fingerprint neural.

| Check | Actual |
|---|---:|
| Chunk universe | 371 |
| DOCX / PDF / TXT / XLSX | 187 / 79 / 42 / 63 |
| Title / heading / category emitted | 318 / 63 / 371 |
| Empty / duplicate serialized / duplicate tokenized | 0 / 0 / 0 |
| Duplicate chunk IDs | 0 |
| Lexical tokens min / max / total | 58 / 310 / 43979 |

R1/R2 row order chunk_id ascending, input text dan token identik. Tokenizer: normalization, casefold, U+2019→apostrof ASCII, re.findall dengan (?u)\b\w+(?:[-'’]\w+)*\b. Angka/underscore/satu karakter/pengulangan query dipertahankan; tanpa stemming, stopwords, accent stripping atau expansion. Query tidak memakai prefix metadata.

Shared hashes, compact sorted-key UTF-8 JSON tanpa trailing newline:

- Universe (array chunk_id): 6bc63ce997da6e80df7b954a476dc46f959bf339986e8c28d389aa8f28f8d6c3.
- Serialized input (array chunk_id/text_sha256): dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c.
- Tokenized input (array chunk_id/tokens): b270da468f4510d0a7b11b7803bef5050bf2d8ea02b517c0b799e53d86dddecc.

## R1, R2 dan index

R1: sklearn TfidfVectorizer dengan custom tokenizer, token_pattern=None, lowercase=False, preprocessor=None, strip_accents=None. Unigram/raw TF/smoothed IDF/L2/float64; min_df=1,max_df=1.0, vocabulary unlimited. Parameter diambil dari TOML. Fit hanya corpus, tidak query. Exact cosine melalui dot query/corpus L2-normalized. Persistence: sparse CSR NPZ + JSON vocabulary/IDF, tanpa pickle.

R2: rank_bm25.BM25Okapi dengan k1=1.5,b=0.75,epsilon=0.25 dari TOML, pretokenized lists dan tokenizer=None. Raw IDF ln((N-df+0.5)/(df+0.5)); negative IDF diganti epsilon×mean raw IDF. Mean actual 4.120291771928227, safety >0 PASS; min effective IDF 0.1022395030520693; avgdl 118.54177897574124. Repeated query tokens dijumlah sesuai get_scores. Persistence state JSON, load ke class versi library yang terikat manifest.

Kedua metode hanya meranking score >0; zero/negative dibuang sebelum rank assignment. Nonfinite score menggagalkan run. Sorting score tak dibulatkan descending lalu chunk_id Unicode ascending. Rank 1-based, tanpa duplicate/parent collapse/padding. Query kosong/whitespace/punctuation-only/OOV→[]. Query non-string ditolak. top_k harus integer positif (bool/float/nonpositive ditolak); nilai besar mengembalikan kandidat tersedia saja.

Manifest: snapshot ID/hash/fingerprint, method, protocol/config/serialization hash, serializer/tokenizer version, dependency versions, lexical lock hash, code hashes, chunk count, timestamp UTC, statistics/warnings. Loader memverifikasi hash artifacts dan seluruh row/text/tokens/locator terhadap frozen corpus. Snapshot/input/config/kode/dependency berubah→reject reuse. Build staging lalu rename COMPLETE; gagal tidak menimpa index lama. Tidak ada cleanup otomatis. Default build ulang verified reuse; rebuild eksplisit memakai --index-name. Payload bytes deterministik pada environment sama; timestamp/duration metadata memang volatile.

## CLI dan tests

Full commands ada di README. Command module telah diuji; entry point wo-retrieve dideklarasikan untuk instalasi project berikutnya tanpa memaksa reinstall sekarang.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONUTF8 = '1'
$env:OMP_NUM_THREADS = '4'
$env:OPENBLAS_NUM_THREADS = '4'
$env:MKL_NUM_THREADS = '4'
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli build --method R1
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli build --method R2
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli retrieve --method R1 --query "koordinasi vendor akad" --top-k 5
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli retrieve --method R2 --query "koordinasi vendor akad" --top-k 5
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli inspect --method R2 --chunk-id WO-DOC-001-C001
.\.venv-ml\Scripts\python.exe -B -m wo_retrieval.retrieval.cli audit
```

| Suite | Environment | Actual result |
|---|---|---|
| Lexical unit/integration | .venv-ml | 14 PASS, 32.729 s |
| Protocol contract | .venv-ml | 5 PASS, 0.007 s |
| Existing ingestion/parser/chunker | .venv | 25 PASS, 4.968 s |

**Total 44 PASS** pada environment sesuai. Coverage: serialization empat format, Unicode/apostrof/terminologi WO; cosine/BM25 expected manual; negative-IDF floor dan unsafe mean gate; repeated/empty/OOV/invalid input/top_k; finite scores/ties/duplicate prevention; protected tamper/output path/stale-incomplete index rejection; full universe, load/rebuild byte identity; CLI success/error. Small-fixture ranking adalah expected matematis, bukan qrels.

Percobaan discovery semua tests di .venv-ml: lexical/protocol PASS, import test_pipeline gagal karena python-docx tidak ada dalam ML environment. Tidak menambah dependency ingestion untuk menutupi pemisahan environment; seluruh 25 tests ingestion kemudian PASS di .venv asal. Gunakan tiga command test terpisah dalam README.

Final pip check pada installed ML environment, dengan PYTHONPATH tidak diset: **PASS**. Project wo-retrieval-benchmark tidak di-install di .venv-ml; CLI mengakses source dengan PYTHONPATH=src. Bila pip check dijalankan dengan source path itu aktif, pip juga menemukan metadata egg-info project ingestion pada src dan melaporkan openpyxl/pypdf/python-docx tidak tersedia. Ini batas pemisahan environment, bukan konflik rank-bm25/sklearn atau perubahan package existing. Gunakan pip check tanpa PYTHONPATH untuk installed-package audit; jangan mengklaim seluruh dependency project ingestion terpasang di ML environment.

## Full 371-chunk technical indexing

| Method | Chunks | Vocabulary | Cold build s | Logical bytes | Allocated NTFS bytes | Verified load s |
|---|---:|---:|---:|---:|---:|---:|
| R1 | 371 | 2138 | 0.398336 | 1335420 | 1347584 | 0.177107 |
| R2 | 371 | 2138 | 0.199747 | 1450059 | 1458176 | 0.158007 |

Cold construction: satu kali perf_counter mengelilingi build baru, termasuk verifikasi protected artifacts, serialization/tokenization, fit, storage/manifest, integrity gate dan publish. Library import/startup Python dikecualikan. Bukan OS-cold-cache trial atau statistik latency benchmark. Load diukur terpisah termasuk hash/row checks. Ukuran termasuk manifest dan row metadata per index, tanpa shared BGE checkpoint. Allocated bytes dari Windows FileStandardInfo.AllocationSize.

R1 matrix 371×2138, 30.402 nonzero entries. Default rebuild verified reuse PASS pada kedua index; explicit fixture rebuild payload byte-identical. Tidak ada warning numerik atau empty/duplicate documents. Warnings penelitian tetap preliminary corpus dan DRAFT queries.

Resource sampled awal/akhir proses indexing+audit+sanity (**bukan peak RAM/VRAM**):

| Resource | Before GiB | After GiB |
|---|---:|---:|
| Available RAM | 5.562 | 5.544 |
| Commit headroom | 12.575 | 12.549 |
| C: free | 12.966 | 12.966 |
| D: free | 846.944 | 846.942 |

## Retrieval sanity top-5

Selection: query pertama menurut urutan file untuk setiap declared style, WO-DEV-001/007/013, dipilih tanpa melihat ranking. Label style bukan bukti keunggulan metode. Semua enam calls PASS: lima ID unik/valid, rank benar, score finite, file/locator cocok dengan frozen chunk. Score tabel dibulatkan hanya untuk display; JSON float penuh dan locator lengkap. Tidak ada judgment relevansi, performance comparison atau tuning.

### R1 — WO-DEV-001

Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-006-C002 | WO-DOC-006 | 0.31564487953 |
| 2 | WO-DOC-006-C001 | WO-DOC-006 | 0.306363369949 |
| 3 | WO-DOC-006-C004 | WO-DOC-006 | 0.300988802638 |
| 4 | WO-DOC-006-C003 | WO-DOC-006 | 0.296835152957 |
| 5 | WO-DOC-006-C005 | WO-DOC-006 | 0.146094413442 |

### R1 — WO-DEV-007

Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-001-C006 | WO-DOC-001 | 0.171718459444 |
| 2 | WO-DOC-013-C002 | WO-DOC-013 | 0.16469939938 |
| 3 | WO-DOC-013-C003 | WO-DOC-013 | 0.151764054061 |
| 4 | WO-DOC-050-C005 | WO-DOC-050 | 0.147737570109 |
| 5 | WO-DOC-029-C004 | WO-DOC-029 | 0.145775751712 |

### R1 — WO-DEV-013

Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-024-C003 | WO-DOC-024 | 0.28224327451 |
| 2 | WO-DOC-014-C004 | WO-DOC-014 | 0.226764776641 |
| 3 | WO-DOC-014-C002 | WO-DOC-014 | 0.210265993089 |
| 4 | WO-DOC-003-C004 | WO-DOC-003 | 0.20873849387 |
| 5 | WO-DOC-003-C002 | WO-DOC-003 | 0.207493014726 |

### R2 — WO-DEV-001

Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-006-C002 | WO-DOC-006 | 24.7992590709 |
| 2 | WO-DOC-006-C001 | WO-DOC-006 | 22.8739884592 |
| 3 | WO-DOC-006-C004 | WO-DOC-006 | 22.323543873 |
| 4 | WO-DOC-006-C003 | WO-DOC-006 | 22.1571280895 |
| 5 | WO-DOC-006-C005 | WO-DOC-006 | 16.7480519618 |

### R2 — WO-DEV-007

Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-001-C006 | WO-DOC-001 | 17.6580846025 |
| 2 | WO-DOC-023-C005 | WO-DOC-023 | 15.2709854085 |
| 3 | WO-DOC-028-C004 | WO-DOC-028 | 14.5288793827 |
| 4 | WO-DOC-050-C005 | WO-DOC-050 | 14.519157087 |
| 5 | WO-DOC-013-C003 | WO-DOC-013 | 13.9923480655 |

### R2 — WO-DEV-013

Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap?

| Rank | Chunk | Document | Score |
|---:|---|---|---:|
| 1 | WO-DOC-024-C003 | WO-DOC-024 | 22.0891665732 |
| 2 | WO-DOC-014-C002 | WO-DOC-014 | 19.1462969739 |
| 3 | WO-DOC-014-C004 | WO-DOC-014 | 18.8686590422 |
| 4 | WO-DOC-003-C002 | WO-DOC-003 | 18.5834589995 |
| 5 | WO-DOC-003-C004 | WO-DOC-003 | 18.2168069125 |

## Integrity, anomaly dan limitations

Baseline SHA-256: 113 existing repository files, environment/Git/pycache dikecualikan. Hanya README.md dan pyproject.toml berubah; seluruh existing file lainnya byte-identical, termasuk source corpus lengkap, canonical documents, chunks, pilot, snapshot, protocol Markdown/TOML, draft queries/provenance/review package dan laporan lama. Seluruh 50 source hashes pada snapshot juga diverifikasi langsung. Git repository tidak terdeteksi; Git status/diff tidak tersedia, baseline hashes menjadi evidence.

| Protected artifact | SHA-256 unchanged |
|---|---|
| data/source_corpus/corpus_manifest.json | 3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f |
| data/processed/documents.jsonl | 314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01 |
| data/chunks/chunks.jsonl | 2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0 |
| experiments/configs/pilot.toml | 958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26 |
| pilot_snapshot.json | 279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e |

Snapshot fingerprint unchanged: 7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40.

Tidak menjalankan neural tokenizer/model, GPU/CUDA, corpus embedding, Dense/Hybrid, query/qrels generation, automatic expert validation atau Recall/MRR/nDCG/MAP. Tidak commit/push/PR/deploy. Anomaly teknis: discovery suite lintas environment dan pip metadata source-path di atas; command disesuaikan dengan environment masing-masing tanpa perubahan metodologi/parameter. Tidak mengukur peak RAM/VRAM atau stress/concurrency; single-build timing di laptop ini tidak menjamin performa produksi. Tidak ada klaim relevansi ranking sanity.

## Rekomendasi Milestone 8B

Foundation R1/R2 siap ditinjau secara teknis. Setelah otorisasi terpisah, tambahkan pinned Dense memakai universe/serialized_inputs_hash yang sama, dengan resource gate dan cache/manifest checks. Jangan lanjut R3/R4 sekarang. Human validation corpus/query dan persetujuan qrels/evaluation protocol tetap dibutuhkan sebelum studi efektivitas. Parameter baseline tidak dituning dari sanity check.

**STOP setelah Milestone 8A.**
