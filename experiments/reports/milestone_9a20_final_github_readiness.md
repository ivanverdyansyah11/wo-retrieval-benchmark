# MILESTONE 9A.20 — FINAL REGRESSION FIX & FIRST COMMIT READINESS

Tanggal: 10 Oktober 2026. Keputusan: **SAFE TO INITIAL COMMIT**, untuk repository **private** yang ditujukan kepada pembimbing, berdasarkan publication manifest dan jalur CPU yang diverifikasi. Ini readiness teknis; bukan izin public release, validasi ahli, atau klaim final evaluation. Tidak ada Git init, commit, repository creation, push, atau GPU inference pada milestone ini.

Rencana yang dicatat, belum dieksekusi: branch `main`; first commit message `feat: initial implementation of WO retrieval benchmark`.

## 1. Root cause dan resolusi regression

Baseline historis 9A.19 sebelum cleanup adalah 196 PASS; sesudahnya tiga errors pada working tree dan empat pada kandidat. Angka ini berasal dari evidence 9A.19 yang dibaca; tidak diklaim sebagai baseline tests baru sebelum edit 9A.20.

| Error sebelumnya | Root cause | Perbaikan sekarang |
|---|---|---|
| `PublishedPilotTests.test_outputs_and_version_isolation` | Memeriksa 703 historical whole-workspace hashes, termasuk README/ignore lama, egg-info, test implementation, serta external cache dengan absolute original paths | Research-scope verifier memetakan scientific/source paths ke root saat ini dan membandingkan hashes original; mutable/generated/environment records diklasifikasikan eksplisit |
| `PublishedPoolTests.test_previous_outputs_and_protected_artifacts` | Asumsi yang sama pada 716 historical records | Verifier yang sama; assertions previous outputs, qrels, completeness, dan accounting tetap berjalan |
| `PublishedAuditTests.test_actual_preflight_and_flags` | Default historical preflight memeriksa 728 whole-workspace hashes dengan original absolute paths | Historical receipt tetap utuh; test memverifikasi scope lebih dahulu, lalu memberikan relocated research hashes melalui temporary persisted input untuk menjalankan actual preflight dengan source/assessment/provenance assertions yang sama |
| `FullColabTests.setUpClass` pada clean CPU candidate | `prepare_v2` meminta local encoding environment, Torch metadata, V1 Dense cache/checkpoint dan official FlagEmbedding files; fixture exchange tests sebenarnya tidak melakukan cloud inference | Delapan existing exchange/import/contract tests memakai frozen V2 artifacts pada CPU; actual local encoding provenance dipisahkan menjadi satu environment-specific test |

Perubahan README/.gitignore pada 9A.19 adalah perubahan dokumentasi valid. Tidak ditemukan mutation scientific artifacts atau regression algoritma retrieval. Coupling checks historis pada seluruh workspace adalah kesalahan scope/portability; Colab class setup adalah kesalahan dependency environment untuk CPU fixtures.

`tests/repository_integrity.py` hanya merupakan test helper. Seluruh `data/`, `experiments/`, historical `colab_exchange/`, production source/scripts, pyproject, dan locks yang ada pada historical receipts tetap diperiksa dengan **hash original**. Unknown external roots, traversal, missing/mutated protected data/source, atau empty research scope ditolak. Tidak ada pemberian expected hash baru untuk data yang berubah. Generated egg-info, root README/.gitignore, maintained test implementation, dan external encoding cache dibedakan dari frozen scientific artifacts. Tests dijalankan; external encoding prerequisites divalidasi terpisah bila tersedia.

| Receipt lama | Historical records | Research/source hashes diverifikasi | Diklasifikasikan di luar portable research scope |
|---|---:|---:|---:|
| 9A.12 | 703 | 297 | 406 |
| 9A.13 | 716 | 309 | 407 |
| 9A.14 | 728 | 320 | 408 |

Masing-masing mencakup 387 external runtime/cache entries dan 6 generated packaging entries, ditambah 11/12/13 historical test files serta dua mutable root files. Jumlah verified+classified harus sama dengan jumlah original; tidak ada entry yang hilang diam-diam. [Scope accounting](../results/milestone_9a20_final_readiness/historical_scope.json).

Assertions scientific outputs, snapshot identity, scores/RRF, pool, text/hash binding, AI flags, grade distributions, blinding, dan provenance dipertahankan. Empat negative tests baru membuktikan missing/mutated data/config/results/source tetap ditolak serta relocation dan category accounting bekerja. Existing preflight/driver source tidak diubah: historical rerun commands yang terkunci pada original workspace tetap historical, bukan quick-start portable. Current read-only verification memakai jalur CPU yang terdokumentasi.

## 2. Isolasi dan temuan tambahan yang diselesaikan

Kandidat dibuat di temporary folder baru **tanpa `.git`** dan tanpa venv/cache lama. Untuk menguji ignore rules, hanya Git repository temporary yang sudah ada dari 9A.19 dipakai sebagai oracle; `.gitignore` di oracle harus identik dengan primary. Tidak dilakukan Git init di lokasi mana pun pada 9A.20.

Full suite dan verification pada kandidat dijalankan dengan guard Python file I/O yang menolak akses ke primary `D:/Project/wo-retrieval-benchmark`, external WO cache, dan Hugging Face model cache. Pada percobaan pertama, guard menemukan satu fixture pada `EncoderSafetyTests` yang menulis synthetic `.run.json` ke approved external cache. Ini dependency filesystem dalam test, bukan scientific mutation atau real inference. Fixture tersebut dipindahkan ke temporary directory dengan approved-path mapping hanya dalam fixture; initial/final resource gate assertions tetap berjalan. Evidence INCOMPLETE/final-gate error juga diperiksa. Test baru menguji **real production cache boundary**, tanpa mapping, dan membuktikan unapproved path ditolak sebelum model initialization.

Percobaan awal optional local-provenance test juga menemukan pembacaan `snapshot_path` pada tingkat JSON yang salah. Ini diperbaiki menjadi `lock['model']['snapshot_path']` sesuai schema actual; final test pada environment ML asal lulus. [Intermediate trace](../results/milestone_9a20_final_readiness/local_encoding_tests.log), [final trace](../results/milestone_9a20_final_readiness/local_encoding_final.log). Kegagalan intermediate tidak diklaim PASS atau dijadikan SKIP.

Pada final isolated suite, guard mencatat **0 external access attempts**. Tidak ada Torch import dalam CPU suite/verification. Child CLI tests memakai candidate paths dan fixture roots; guard bukan OS sandbox menyeluruh atau bukti inference cloud telah dijalankan.

## 3. Exact perubahan

Existing files berubah:

1. `tests/test_development_pilot.py`
2. `tests/test_judgment_pool.py`
3. `tests/test_pilot_assessment_audit.py`
4. `tests/test_full_colab.py`
5. `tests/test_query_vectors.py`
6. `docs/setup.md`
7. `README.md`

File baru:

- `tests/repository_integrity.py`
- `tests/test_repository_integrity.py`
- Laporan ini.
- Audit evidence di `experiments/results/milestone_9a20_final_readiness/`; exact paths dan hashes ada pada [publication manifest](../results/milestone_9a20_final_readiness/git_publication_manifest.json).

Tidak ada file removed/moved. `.gitignore` 9A.19 tetap sama setelah effects-nya diverifikasi ulang. Tidak ada perubahan production source/scripts, algorithms, tokenizer/chunking, BM25/RRF/configs, corpus, query text, qrels, human assessments/history/exports, vectors, rankings, metrics, atau existing reports/manifests. README tidak dikembalikan ke status lama; hanya referensi readiness terbaru diperbarui. Dokumen setup kini menjelaskan CPU tests dan explicit optional SKIP dengan benar.

[Patch perubahan](../results/milestone_9a20_final_readiness/changes.patch) dan [integrity proof](../results/milestone_9a20_final_readiness/protected_integrity.json) disertakan. Historical baseline hashes/audit records tidak diedit.

## 4. Regression dan environment-specific results

| Run final | Total | PASS | SKIP | Failure/error | Exit |
|---|---:|---:|---:|---:|---:|
| Working tree, CPU combined environment | 202 | 201 | 1 | 0/0 | 0 |
| Fresh isolated candidate, CPU environment | 202 | 201 | 1 | 0/0 | 0 |
| Targeted Colab + local encoding provenance pada `.venv-ml` asal | 9 | 9 | 0 | 0/0 | 0 |
| Targeted query safety/cache boundary | 16 | 16 | 0 | 0/0 | 0 |

Suite bertambah dari 196 menjadi 202: empat integrity regression tests, satu local-provenance test terpisah, dan satu real cache-boundary test. Tidak ada existing test dihapus/dinonaktifkan. Delapan original Colab contract tests berjalan pada CPU. Satu SKIP bernama `test_full_colab.LocalEncodingEnvironmentTests.test_pinned_local_encoding_provenance`, karena **Torch distribution metadata tidak tersedia** pada CPU quick start. SKIP tidak dihitung PASS. Apabila dependencies/cache/implementation tersedia tetapi versi/hash salah, test gagal, bukan di-skip. Pada ML environment asal test tersebut benar-benar PASS tanpa loading/inference model; ia memeriksa metadata/file hashes/provenance.

Evidence: [working CPU](../results/milestone_9a20_final_readiness/working_final_tests.json), [candidate CPU](../results/milestone_9a20_final_readiness/candidate_tests.json), [candidate log](../results/milestone_9a20_final_readiness/candidate_tests.log), [local environment log](../results/milestone_9a20_final_readiness/local_encoding_final.log). CLI error messages dan fixture “embedded” pada logs adalah expected negative/synthetic tests, bukan inference baru atau unexplained suite failure.

Perintah full suite yang benar:

```powershell
$env:PYTHONPATH = (Join-Path $PWD 'src')
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Structured audit harness menjalankan unittest discovery yang sama, mencatat totals/skip reason/Torch state, kemudian menjalankan verification dan Word smoke. Runtime guards hanya bagian harness audit; tidak dimasukkan ke production modules.

## 5. Clean candidate dan setup

Fresh venv pada kandidat dibuat menggunakan Python 3.12.14 Windows x64. README installation command benar-benar dieksekusi dari candidate root:

```powershell
.\.venv\Scripts\python.exe -m pip install -c requirements.lock -c docs/offline_constraints.txt -r experiments/configs/lexical_environment.lock.txt -e ".[lexical]" psutil==7.2.2
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/verify_repository.py --query-id WO-DEV-001
.\.venv\Scripts\python.exe scripts/human_annotation.py status
```

Dependency installation, `pip check`, ingestion/numerical imports, full suite, retrieval example, human status, saved evaluator parity, dan Word generator semuanya berhasil. [Install log](../results/milestone_9a20_final_readiness/candidate_install.log), [dependency inventory](../results/milestone_9a20_final_readiness/candidate_dependencies.txt), [candidate checks](../results/milestone_9a20_final_readiness/candidate_checks.json). Instalasi memakai cached distribution wheels dan editable build dependencies; tidak diklaim fresh download semua packages dari internet. Tidak membutuhkan Torch, Transformers, FlagEmbedding, atau model weights untuk jalur CPU ini.

Required V1/V2 assets, lexical/Dense indexes, 18 query vectors, frozen human package dependencies, reports/manifests, dan official judgment exports tersedia pada candidate. Tidak ada root archive/environment/cache yang diam-diam dipakai untuk melengkapi missing assets. Final publication candidate disinkronkan dan setiap selected file dibandingkan hash dengan primary.

Ini **clean publication staging verification**, bukan actual remote clone: primary belum memiliki `.git`, remote, atau commit, dan user melarang Git init. URL `git clone` belum dapat dijalankan. Linux/macOS belum diverifikasi. Tidak ada actual cloud runtime/GPU execution pada audit ini. Batasan tersebut tidak menghalangi initial commit private untuk scope CPU development yang terbukti berjalan.

## 6. Protected artifacts dan hasil penelitian

Baseline 9A.20 mencakup **463 files** di luar environment/generated metadata. Tujuh existing changes di atas authorized; **456/456 remaining baseline files identik**, 0 missing/mutated. Seluruh source scientific/production, data, indeks/vectors, qrels, judgments/history, ranking, evaluation outputs, serta laporan dan manifests 9A.19 dan sebelumnya termasuk pemeriksaan. [Hashes](../results/milestone_9a20_final_readiness/protected_integrity.json).

[Working verification](../results/milestone_9a20_final_readiness/working_final_verification.json) dan [candidate verification](../results/milestone_9a20_final_readiness/candidate_verification.json) memvalidasi:

- Corpus V1/V2 masing-masing 50 source documents (26 DOCX, 9 PDF, 10 XLSX, 5 TXT), 0 audit errors; V1 mempunyai historical root-README packaging notice yang sudah didukung auditor existing.
- 371 canonical V2 chunks, snapshot fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`, 18 development queries dan frozen bindings.
- R1–R4 retrieval smoke pada seluruh existing queries; **72 full saved rankings exact parity** untuk IDs/ranks/scores/snapshot/method tanpa rounding. Top-10 untuk `WO-DEV-001` tersedia pada JSON verification.
- 194 frozen source hashes annotation package; **654/654 RESOLVED**, Grade 0/1/2 **429/152/73**, missing/unresolved 0.
- **695 human history events**, hash chain, bindings, revisions, dan provenance valid; official exports dipertahankan.
- Seluruh output evaluator di memori **exact sama dengan saved 9A.18 evaluation.json**, termasuk macro/per-query/by-style/protocol/provenance. Tidak menggunakan expected numbers hardcoded untuk membuat checks PASS.
- Word generator: actual saved evaluation dipakai menghasilkan DOCX temporary di luar repository; terbaca, 22 tables, formatted macro cells exact. Existing Word tidak diubah; visual rendering ulang tidak dilakukan.

Metrik tetap:

| Method | P@5 | P@10 | MRR@10 | nDCG@5 pooled | nDCG@10 pooled |
|---|---:|---:|---:|---:|---:|
| TF-IDF | 0.633333 | 0.494444 | 0.722222 | 0.486942 | 0.517324 |
| BM25 | 0.622222 | 0.500000 | 0.784722 | 0.497634 | 0.524130 |
| BGE-M3 Dense | 0.744444 | 0.577778 | 0.972222 | 0.646561 | 0.663459 |
| Hybrid RRF | 0.711111 | 0.588889 | 0.944444 | 0.627933 | 0.646549 |

Ini pooled development evaluation dengan satu peneliti, bukan final evaluation, domain validation, atau signifikansi statistik. Main evaluation tetap pending; tidak dibuat query/embedding/benchmark baru.

## 7. Security, privasi, hak publikasi, ukuran

[Security scan](../results/milestone_9a20_final_readiness/security.json) memeriksa **2.709 text members**, mencakup source/config/docs/logs/data, Office XML/PDF text/metadata, notebooks, dan ZIP members, termasuk root archive lokal. Pattern scan private keys, token/API credentials, assignments, dan credential URLs menemukan **0 secret candidates**. New/modified publication files diperiksa lagi saat manifest difinalkan. Ini bukan jaminan identifikasi arbitrary secrets atau audit dependency vulnerabilities. Git history tidak tersedia untuk diperiksa.

Parser review **100 source documents V1/V2** kembali menghasilkan 0 email/phone candidates; author metadata merupakan researcher-composed/synthetic organization/peneliti/openpyxl. Kedua notebooks memiliki 0 outputs dan 0 execution counts. [Privacy details](../results/milestone_9a20_final_readiness/privacy_details.json). Nama peneliti, assessment notes/provenance/timestamps, historical local paths, dan private alias mapping tetap ada sebagai evidence. Paths tersebut adalah metadata historis, bukan instruksi wajib clone atau credential. Mereka **tidak disanitasi** dengan mengubah frozen files. Audience yang direkomendasikan dan diminta adalah private repository + dosen collaborator.

Corpus diidentifikasi manifests sebagai researcher-composed synthetic operational draft; tidak ada authentic private client/contact dataset terdeteksi dalam source review. Tidak ada model weights, third-party dependency installation, venv, live server locks, `.env`, temporary download, atau root `data.zip` dipilih untuk Git. ZIP yang tetap dipilih adalah **official frozen assessment/Colab input/exchange evidence**, diperlukan atau berguna untuk reproducibility, bukan temporary transfer ZIP yang dibuang.

Belum ada LICENSE repository/dataset formal. Tidak mengarang lisensi, mengklaim hak pihak lain, atau memberi izin public redistribution. Initial commit private atas project penelitian yang user minta siap merupakan scope keputusan SAFE ini. Keputusan lisensi dan redistribusi **public** dataset/code/model tetap review terpisah sebelum public release; domain content belum expert-validated. Private visibility bukan pengganti izin pihak ketiga apabila kelak data eksternal ditambahkan.

[Git publication manifest](../results/milestone_9a20_final_readiness/git_publication_manifest.json) mencatat exact semua selected paths, bytes, SHA-256, total size/count, exclusions, modified/new paths, branch/message yang direncanakan. Environment/bytecode/egg-info/model-cache/root archive dikecualikan; seluruh official research assets retained. Scientific logs yang terikat manifests tetap ikut, temporary testing DOCX/venv/harness tetap di luar primary.

File terbesar tetap `experiments/results/milestone_9a12_development_pilot/rankings.jsonl`, **7.362.402 bytes (7,021 MiB)**. Semua selected files berada di bawah 50 MiB; tidak ada candidate file mendekati batas GitHub 100 MiB yang dijelaskan pada [GitHub documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Total final size tersedia pada manifest; bukan ukuran 4,6 GiB environment ML lokal yang tidak dipublikasikan. Tidak ada disk cleanup/destructive deletion.

## 8. Git checks dan keputusan akhir

Primary tetap **NOT INITIALIZED**. `git status`, remote, dan log tidak tersedia; tidak ada tracked/untracked status native atau Git history. Git ignore rules diuji pada existing 9A.19 oracle yang identik; [ignore proof](../results/milestone_9a20_final_readiness/ignore_verification.json). Semua required publication assets tetap visible. Ini selection manifest, bukan klaim files telah staged/committed.

`git diff --check` pada primary belum dapat tersedia tanpa Git init. Actual equivalent `git diff --no-index --check` dijalankan terhadap pre-change copies untuk seluruh modified files, serta empty input untuk new code/docs; tidak ada whitespace diagnostics. Exit 1 pada no-index berarti ada content differences, bukan whitespace error. Patch dan baseline integrity digunakan untuk review seluruh perubahan. Documentation links dan publication hashes divalidasi saat finalization.

**Blocking regression failures: 0. Missing required CPU assets: 0. Detected secret candidates: 0. Unexplained failures: 0.** Expected optional SKIP: 1, tercatat dan dibuktikan PASS pada environment asal ketika prasyarat tersedia.

**Final: MILESTONE 9A.20 — SAFE TO INITIAL COMMIT**, khusus private supervisor-review repository sesuai manifest. Belum ada tindakan initial Git setup/commit/push. Actual remote clone, cloud execution, perangkat/platform lain, public licensing/release, dan main research evaluation belum diuji/diselesaikan; tidak diklaim selesai dan bukan blocker initial private commit scope ini. STOP sesudah audit, verification, manifest, dan laporan; tunggu instruksi commit terpisah.
