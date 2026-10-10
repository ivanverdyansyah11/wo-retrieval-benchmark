# Milestone 6 — Research benchmark protocol v1

**PROPOSED — untuk review sebelum implementasi.** Milestone 5 telah diterima pengguna. Ini desain preliminary benchmark, bukan laporan hasil retrieval. Konfigurasi inti R1–R4 berstatus LOCKED FOR PILOT sesuai instruksi pengguna; kebijakan judgment/candidate/evaluation masih PROPOSED atau OPEN. Implementation/main evaluation authorization tetap false. 18 development queries kini tersedia sebagai draft_pending_expert_review (Milestone 7A/7B); belum ada query tervalidasi/frozen, main queries, qrels, indeks atau performance scores.

## 1. Snapshot dan fair comparison

Snapshot **WO-CORPUS-V1-DRAFT-PILOT-001**: 50 source documents,50 canonical documents, **371 frozen chunks**, corpus_version **v1-draft**, validation_status **pending_practitioner_validation**. Sumber retrievable hanya operational documents di `data/source_corpus/documents/` melalui frozen chunks. Manifest, inventory, DOCUMENT_SUMMARIES, QUALITY_REPORT, VALIDATION_CHECKLIST dan snapshot bukan input retrieval.

Semua R1–R4 memakai chunk IDs, serialized text, queries, qrels, splits dan cutoffs identik. Tidak ada query-dependent metadata filter atau boost khusus metode. Unit evaluasi chunk; tanpa parent-document collapse. Frozen overlap tetap ada: kredit ke beberapa chunk bertumpang tindih bisa terjadi, sehingga metrik tidak mengukur kelengkapan jawaban/fakta unik.

Corpus masih draft komposisi peneliti. Judgment query/qrels oleh pakar tidak otomatis memvalidasi corpus. Revisi corpus setelah practitioner validation memerlukan snapshot/protocol/dataset version baru, bukan menimpa baseline.

## 2. Deterministic serialization

Policy **wo_operational_context_dedup_v1**, **O2 OPEN**.

Audit aktual: seluruh371 chunk mempunyai title,heading,category,text nonempty. `metadata.guide_context` berbentuk list, nonempty pada53 dari63 XLSX chunks;10 sisanya adalah sheet Panduan. Metadata ini mencampur konteks dan instruksi administratif. Existing chunker sudah memasukkan definisi RACI terpilih dalam text; Panduan operasional juga memiliki chunk tersendiri.

Aturan:

1. Required fields harus string nonempty; gagal eksplisit jika schema tidak sesuai. Normalisasi Unicode NFC, CRLF/CR ke LF, trim outer whitespace. Pertahankan seluruh body internal.
2. Comparison key hanya untuk dedup: NFC, casefold, collapse whitespace Unicode menjadi satu spasi.
3. Seleksi **heading → title → category**. Suppress kandidat bila seluruh nilainya sudah terkandung dalam body atau satu nilai field sebelumnya terpilih. Cari escaped normalized whole-field string dengan boundary Unicode `(?<!\w)` dan `(?!\w)`; bukan fuzzy match atau bag-of-words.
4. Emit field terpilih **title → heading → category**, label `Judul: `, `Heading: `, `Konteks kategori: `. LF antar prefix; blank line sebelum body. Jika prefix kosong, emit body saja. Tanpa trailing newline tambahan.
5. Tidak menghapus pengulangan internal body. Prioritas heading membuat title yang sudah ada dalam heading tidak diulang sebagai prefix.
6. Guide metadata **audit-only**, tidak diinjeksi massal. Pertahankan operational guide yang sudah ada di text. Penambahan guide nanti memerlukan pemilihan operasional yang disetujui, serialization version baru dan tokenizer audit ulang bagi semua metode.
7. Allowlist informasi input hanya title/heading/category/text. IDs, hash, paths, locators, status dan metadata administratif terpisah tidak ditambahkan. Kode staff/event/row yang memang ada dalam operational text tetap utuh.
8. Query hanya text yang dinormalisasi NFC/LF/outer trim: tanpa tag kategori, answer hints, expansion atau retrieval instruction.

Format konseptual, hanya baris terpilih yang diemit:

```text
Judul: {title_if_selected}
Heading: {heading_if_selected}
Konteks kategori: {category_if_selected}

{text}
```

Audit tokenizer-only lokal pinned BGE-M3, special tokens included, truncation=False: title emitted318,heading63,category371; heading308/title53 disuppress sebagai konteks yang sudah terkandung. Maksimum **573 token**, zero overflow640; berbeda dari scenario B lama588 karena prefix dedup. Tidak ada neural model loading/embedding pada milestone ini. Query baru tetap wajib dicek panjangnya.

Serialization fingerprint: SHA256 UTF8 compact sorted-key JSON array, chunk_id ascending; objects berisi chunk_id,text_sha256,tokens. ensure_ascii=False, separators=(',',':'), tanpa newline. Ini identitas input usulan, bukan pengganti snapshot fingerprint. Tabel audit terikat konfigurasi ada di bagian akhir.

## 3. Proposed method configurations

Konfigurasi inti berikut LOCKED FOR PILOT, bukan parameter yang diklaim optimal. Subkebijakan yang belum disetujui tetap PROPOSED/OPEN; tidak ada tuning sekarang atau tuning terhadap final test set.

Common lexical R1/R2: serialized text di-casefold, U+2019 menjadi ASCII apostrophe, lalu Unicode re.findall memakai pattern TOML. Pattern yang dimaksud: `(?u)\b\w+(?:[-'’]\w+)*\b`. U+2019 di character class dipertahankan sebagai representasi apostrof yang benar, meski normalisasi telah menyamakannya ke ASCII. Hyphen ASCII dan apostrof hanya internal token; en/em dash dan tanda euro/trademark bukan penghubung token. Pertahankan angka, underscore, single-character tokens serta hyphen/apostrof internal. Tanpa stopwords/stemming/lemmatization/accent stripping. Query/corpus memakai aturan sama; pengulangan query token dipertahankan.

**R1 — TF-IDF + exact cosine.** Usulan sklearn1.9.1, custom lexical unigram tokenizer, raw TF, smoothed IDF `ln((1+N)/(1+df))+1`, L2 norm,float64; min_df1,max_df1.0,no vocabulary cap. Fit hanya371 serialized chunks; query transform tanpa refit. Score sparse normalized dot product. Kandidat hanya score>0; all-OOV query menghasilkan empty ranking. [Official TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).

**R2 — BM25Okapi.** Usulan rank-bm250.2.2,k1=1.5,b=0.75,epsilon=0.25. IDF=ln((N-df+0.5)/(df+0.5)); negative IDF diganti epsilon×mean raw IDF. Score sum per kemunculan token query: `IDF*tf*(k1+1)/(tf+k1*(1-b+b*len/avgdl))`. Pretokenized lists,tokenizer=None; get_scores lalu sort sendiri. Zero/negative scores dibuang sebelum ranking. Mean raw IDF<=0 memblokir review baseline; jangan diam-diam ganti variant. Package belum diinstal. [Official source](https://github.com/dorianbrown/rank_bm25/blob/master/rank_bm25.py), [release0.2.2](https://pypi.org/project/rank-bm25/0.2.2/).

**R3 — BGE-M3 Dense.** BAAI/bge-m3 revision **5617a9f61b028005a4858fdac845db406aefb181**, FlagEmbedding1.4.2,Transformers4.57.6,torch2.12.1+cu126. CUDA FP16,batch1,single process; official CLS pooling,1024-d dense output; sparse/ColBERT disabled. Cap640 bagi corpus dan query termasuk special tokens; fail overflow, tanpa truncation/re-chunking. Official inference forward,eval+inference_mode; hindari wrapper automatic OOM retry. Cast output float32 dan L2-normalize ulang; assert finite/nonzero norm/dimension. Exact cosine=CPU float32 normalized inner product seluruh371 rows. Semua finite scores termasuk negatif eligible. Tokenizer berbeda adalah bagian algoritma; informasi input tetap sama. [Official BGE-M3](https://huggingface.co/BAAI/bge-m3).

Cache corpus di D: berupa float32 NPY + JSON row manifest, chunk_id ascending. Payload371×1024×4=**1,519,616 bytes**, bukan measured index size. Key mencakup snapshot,policy/serialized inputs,model/tokenizer file hashes,precision,normalization,cap,versions,code hash. Atomic publication; mismatch ditolak. Partial cache incomplete tidak boleh dievaluasi; resume hanya setelah resource diperbaiki dan diizinkan. Tidak ada cache embedding dibuat sekarang.

**R4 — equal-weight RRF, k=60 LOCKED FOR PILOT.** Reuse R2/R3 configurations dan score ordering persis. Candidate policy berikut **PROPOSED**, dipilih karena ukuran corpus dan interpretasi rank, bukan dari hasil evaluasi.

| Opsi | Kandidat dan ranks | Zero BM25 / eligibility | Recall ceiling dan trade-off |
|---|---|---|---|
| A: top100 tiap component | Potong setelah sorting/eligibility; pertahankan rank1-based, union maksimal200 | BM25 hanya positive; absent component contribution0 | Relevant chunk di luar union tidak dapat ditemukan oleh R4. Batas kandidat menambah parameter walau scoring dense seluruh371 sudah murah secara ukuran |
| B: full Dense + positive BM25 | Dense rank1–371; BM25 rank1–m untuk semua score>0, m<=371 | Zero/negative BM25 absent, contribution0; Dense finite termasuk negative cosine tetap eligible | Union seluruh371, tanpa candidate-truncation ceiling; cutoff5/10 tetap membatasi retrieved relevant. Tidak membuktikan recall atau akurasi lebih tinggi |
| C: full ranking kedua component | Rank seluruh371 termasuk tail BM25 tied-zero | Jika zeros ikut voting, ID tie order memberi kontribusi tanpa lexical evidence; jika kontribusi zeros ditetapkan0, praktis ekuivalen B untuk positive candidates | Universe penuh, tetapi arbitrary tail votes harus dijelaskan; lebih rumit tanpa manfaat metodologis yang diketahui |

**Rekomendasi B**: full Dense ranking + seluruh BM25 berskor positif. `RRF(c)=1/(60+rank_dense(c)) + I(BM25_score(c)>0)/(60+rank_BM25_positive(c))`. Absent contribution0; jangan dummy-rank. Karena scores>0 mendahului scores<=0, positive ranks tidak berubah oleh pembuangan tail. All-zero BM25 memberi dense-only RRF ordering. Tidak ada minimum cosine threshold atau top100 candidate cutoff.

Component exact ties: score descending tanpa rounding, lalu chunk_id ascending Unicode codepoint. RRF ties memakai chunk_id yang sama. Determinism tidak berarti tie order mengandung relevansi; policy hanya memastikan reproducibility. Source formula: [original RRF paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf). Opsi B adalah adaptasi eligibility eksplisit, bukan klaim bahwa paper menetapkan kebijakan ini.

Export ranking sampai371 sesuai eligible result length; evaluasi tetap cutoff5/10. Nonfinite/duplicate IDs fail run. Ranking pendek tidak diisi dummy chunk. Policy yang sama diterapkan pada R2 standalone dan R2 component R4.

**R5/R6 optional, disabled:** R5 official token-ID sparse weights matched-token dot product. R6 official normalized ColBERT vectors: maximum passage-token dot per query token, kemudian mean sepanjang query tokens sesuai official colbert_score. Sparse aggregation, token masking, exact scoring/storage/resource dan activation perlu approval/test terpisah. Dense PASS bukan bukti sparse/multi-vector feasible.

## 4. Query design — schema dan draft development

Usulan **18 development** (6 setiap lexical-oriented,semantic/paraphrase,mixed/natural) dan **75 main** (25 setiap style). Sepuluh kategori domain: lima mendapat8 dan lima7 main queries. Kategori mana mendapat8 dan cross-tab style/category ditetapkan sebelum drafting (**O3 OPEN**). Cakup peran,pre-event/on-day/post-event,keputusan/prosedur,informasi event; jangan hanya kode.

Lexical-oriented memakai istilah domain eksplisit; semantic/paraphrase mengungkap kebutuhan dengan padanan ungkapan; mixed/natural menggabungkan istilah dan bahasa percakapan yang wajar. Label ini tidak bergantung pada skor retriever. Sepuluh kategori mengikuti kategori operasional corpus.

Mulai dari kebutuhan informasi praktisi, bukan output ranking. Pakar menyusun/review needs dan answerability corpus; style adalah anotasi kebutuhan valid, bukan rekayasa menguntungkan metode. Jangan menyalin jawaban menjadi lexical query atau membuat paraphrase tidak wajar. Author/reviewer tidak melihat ranking metode. Catat provenance,anonymization/izin jika bersumber dari praktik nyata.

Split berdasarkan **information_need_family** sebelum paraphrase. Variasi kebutuhan sama harus satu split. Audit exact/normalized duplicates dan human semantic review; larangan overlap langsung saja tidak cukup. Topik umum boleh sama, intent spesifik lintas split tidak sama. Main tersegel setelah validation; tidak dipakai memilih parameter/depth/serialization.

UTF8 JSONL fields: query_id:string unique,query_dataset_version:string,split:pilot|main,text:string nonempty,style:enum3,primary_category:string,information_need_id:string,provenance_id:string,author_id:pseudonym,created_at:ISO8601,validation_status:enum. Provenance ledger terpisah berisi need description,domain role,scenario basis,source evidence refs,expert review ID,revision history. Hanya text dikirim ke retriever. 18 development query records tersimpan sebagai draft_pending_expert_review; teks existing dipertahankan pada Milestone 7B dan masih menunggu review praktisi. Main query records belum dibuat.

Validation status yang diperbolehkan: draft, draft_pending_expert_review, expert_reviewed, frozen. Status draft dan draft_pending_expert_review bukan validated atau frozen. expert_reviewed memerlukan sign-off manusia yang terdokumentasi; frozen memerlukan keputusan freeze terpisah. queries.status = DEVELOPMENT_DRAFTS_PENDING_EXPERT_REVIEW_MAIN_NOT_CREATED hanya mencatat kesiapan draft, bukan izin implementasi atau evaluasi. Status frozen dan version/hash yang immutable diwajibkan sebelum main evaluation.

## 5. Relevance judgments: opsi, workload dan rekomendasi S1

Grade ditentukan manusia atas kontribusi chunk terhadap information need, bukan karena kata query cocok atau retriever menempatkannya tinggi.

| Grade | Rubric |
|---|---|
| 0 | Human-judged nonrelevant: tidak membantu kebutuhan, hanya topik mirip atau konteks/peran/event tidak sesuai |
| 1 | Evidence membantu secara nyata tetapi parsial/pendukung |
| 2 | Evidence operasional langsung dan substantif menjawab fokus kebutuhan dengan konteks sesuai |

Kebutuhan multi-chunk: nilai setiap kontribusi secara independen, bukan memaksa satu chunk menjawab seluruh tugas. Title saja tidak cukup untuk grade2. Bukti ambigu diperiksa pada operational source/locator. Tidak mampu menilai berstatus needs_review, bukan grade0. Overlap chunks dinilai sendiri, tidak auto-copy label.

### A/B/C dan workload sebelum memilih assessor coverage

Asumsi perencanaan **20–40 detik per labeling action**, belum diukur, bukan angka benchmark atau estimasi jam pakar yang sudah disetujui. Kalibrasi menggunakan development untuk mengukur waktu sebenarnya. Tabel hanya main75 queries; initial upper bounds pool mengabaikan overlap yang dapat mengurangi jumlah, dan tidak mencakup calibration, breaks, tambahan evidence pakar, adjudikasi atau revisi.

| Pendekatan | Initial main workload | Jam indikatif dengan asumsi20–40s/action | Implikasi |
|---|---|---|---|
| A: exhaustive satu assessor | 75×371 =27,825 actions | 154.6–309.2 | Denominator Recall/ideal nDCG lengkap, tetapi single-assessor variability tetap ada |
| A: exhaustive dua independen | 55,650 actions | 309.2–618.3 | Independent labels seluruh corpus, workload tertinggi; bukan persyaratan mutlak |
| B: balanced candidate pool + outside audit | <=75×(80+10)=6,750 primary actions | <=37.5–75.0 | Tidak exhaustive; perlu scoped metric labels dan independent subset review |
| B: ditambah20% independent subset | <=8,100 actions total | <=45.0–90.0 | Lebih ringan, tetapi completeness tidak terbukti |
| C: pooled human judgments + exhaustive audit10 queries | <=9,560 primary +4,880 secondary =14,440 actions total | <=80.2–160.4 | Audit completeness langsung pada subset, independent coverage terarah, tidak mengklaim seluruh75 lengkap |

Untuk C, primary workload =10×371 +65×90=9,560. Secondary =10×371 +65×ceil(20%×90)=4,880. Semua angka adalah initial planning bounds, **bukan cap yang membatasi evidence**: expert additions/ambiguities harus dinilai dan dicatat walau budget bertambah. Pilot18 pooled queries memerlukan <=1,620 primary +324 secondary =1,944 actions, atau <=10.8–21.6 jam indikatif tambahan. Jika pilot exhaustive dipilih, satu assessor6,678 actions; dua13,356, belum termasuk adjudikasi.

A paling kuat untuk completeness, tetapi memerlukan waktu besar. B cocok bila budget sangat terbatas, dengan hasil secara eksplisit berbasis pool. **Rekomendasi S1: C, pending supervisor approval**; bukan AI judgment workflow. C tetap menuntut waktu pakar yang nyata (primary sekitar53.1–106.2 jam pada batas awal). Jika tidak tersedia, pembimbing harus menyetujui B atau revisi ukuran/budget secara prospektif; jangan menutup kekurangan dengan auto-qrels atau mengklaim dua assessor penuh.

### Human-only C workflow yang dapat diaudit

1. Domain expert WO yang berpengalaman sebagai EC/WC atau peran operasional sepadan memvalidasi information needs, answerability, istilah, batas kewenangan, event context dan rubric. Catat peran/pengalaman/konflik kepentingan, bukan mengarang nama validator. Expert ini menilai **semua selected pairs** sebagai primary assessor.
2. Sebelum ranking/label/performance dilihat, tetapkan10 main queries untuk exhaustive audit, satu per kategori dengan style allocation4/3/3 dan seed42. ID subset di-hash dan dibekukan. Validasi feasibility alokasi dari desain query; bila tidak feasible, perbaiki rencana sebelum retrieval, bukan pilih query yang menguntungkan metode.
3. Setelah metode/protocol terkunci dan pelaksanaan pooling diotorisasi terpisah, union top20 R1–R4 per query, tanpa method/rank labels pada assessor. Maksimum80 unique dari rank pool; R4 bergantung R2/R3 sehingga bukan empat sumber independen. Corpus kecil tidak membuat pool otomatis lengkap.
4. Pada65 pooled main queries dan18 dev queries, tambah10 unique outside-pool chunks: satu per kategori yang tersedia; strata habis didistribusikan deterministik ke kategori tersisa. Seed42, ordered IDs dan per-query/category shuffle version dicatat; simpan inclusion probability/stratum. Sampling dipilih sebelum judgment. Pada10 audit queries, semua371 dinilai, bukan menambah pool90 di atas census.
5. Expert menambahkan chunk relevan yang ditemukan melalui pemeriksaan source/related evidence; provenance dan workload tambahan dicatat, tanpa limit artifisial. Peneliti hanya mengelola UI, candidate dedup, schema dan audit. **Tidak ada AI/LLM auto-label, auto-grade0, atau prelabel yang menambatkan assessor.**
6. Secondary reviewer berbeda orang dan qualified: idealnya praktisi WO kedua; bila tidak tersedia, reviewer berpelatihan domain dengan qualification/calibration terdokumentasi dan WO-expert adjudication. Independent judgment mencakup seluruh10 exhaustive queries plus20% per pooled query, terstratifikasi rank-pool/outside-pool, dipilih sebelum labels dan dibutakan dari primary grades. Tambahkan semua ambiguous cases untuk review; tambahan ini bukan bagian bound awal.
7. Pertahankan original grades/rationale/evidence/timestamps. Adjudikasikan seluruh double-judged disagreements bersama domain expert; unresolved memakai expert ketiga atau status needs_review, bukan grade otomatis. Agreement dan weighted kappa dihitung sebelum adjudikasi **pada subset double-judged saja**, disertai ukuran/strata/grade distribution. Tidak mengekstrapolasi agreement ke semua pairs tanpa weighting/design justification.

### Coverage, bias dan qrels representation

Future qrels UTF8 TSV: `query_id,0,chunk_id,grade`, tanpa header, unique pair, valid IDs, integer0/1/2. Explicit0 berarti manusia menilai nonrelevant; absent pair adalah **unjudged/unknown**. Evidence ledger menyimpan qualification,reason,locator,selection stratum,probability atau census,independent-review flag,original/adjudicated grades dan versions.

Audit future wajib: judged@5/10 setiap metode, judged fraction dari371 per query, overlap/contribution tiap pool method, outside-pool relevant yield per stratum, serta pooled-vs-exhaustive metric sensitivity pada10 audit queries. Hit luar pool membuktikan pool melewatkan evidence; zero sampled hits **tidak membuktikan** completeness. Tidak mengestimasi global Recall dari sampling kecil ini. Pooling dapat menguntungkan kontributor dan query wording; [NIST pooling-bias research](https://www.nist.gov/publications/bias-and-limits-pooling-large-collections) menjadi alasan melaporkan keterbatasan, bukan bukti besar bias pada corpus ini.

Unknown top10 hasil metode mana pun: block evaluation run-set sampai manusia menilai; jangan skip unknown atau drop query untuk satu metode. Unknown di luar top10 tetap unknown. Depth20 pada empat locked methods memberi peluang coverage top10, tetapi coverage tetap diverifikasi, termasuk ranking pendek. R5/R6 atau metode baru memerlukan pool/qrels version diperluas dan **semua** metode dibandingkan ulang pada qrels sama.

C tidak mengharuskan exhaustive seluruh75 atau dua full assessors. Freeze gates: selected-pair reviews/adjudication selesai, semua returned top10 terlabel,10 census queries lengkap, provenance dan metric scope disetujui. Pembimbing dapat menolak limited scope dan meminta A; keputusan masih OPEN.

## 6. Operational metrics, missingness dan paired analysis

**nDCG@10 proposed primary, pending supervisor approval.** Rekomendasi C menghasilkan main75 dengan pooled qrels; primary report label harus **nDCG@10 (pooled qrels,75 main queries)**. Full-qrels10 audit queries adalah sensitivity scope terpisah, bukan bukti metric completeness seluruh75. Pembimbing perlu menyetujui scope ini atau memilih primary exhaustive scope. [NIST TREC guidance](https://ir.nist.gov/trec-covid/round1.html) menunjukkan pentingnya membatasi klaim recall-based measures pada incomplete judgments.

### Definisi

Untuk q, `R_q={c:grade(q,c)>=1}`. Grade0/1/2, gains `2^grade-1` =0/1/3. Ranking1-based, setiap chunk ID hanya sekali.

- **Recall@5/10**: `|top_k(q) intersect R_q| / |R_q|` dengan R_q lengkap atas371 chunks. Untuk C, label standar ini hanya pada10 exhaustive queries. Pada pooled75 gunakan **Recall_known@5/10**, denominator hanya known human-relevant set; bukan estimasi corpus Recall.
- **RR@10**:1/rank first grade>=1 pada rank<=10; tidak ada hit berarti0. **MRR@10** adalah macro mean RR. Dengan semua returned top10 judged, ukuran ini tidak membutuhkan relevant denominator luar top10, meskipun assessor error tetap ada.
- **DCG@k**: `sum_(i=1..k) (2^grade_i-1)/log2(i+1)`, k5/10.
- **nDCG@5/10**:DCG/IDCG. Complete qrels: ideal sorted grades seluruh371. Pooled qrels: ideal hanya known graded relevant chunks, label **nDCG@k (pooled qrels)**; unknown di luar top10 tidak diberi grade0, melainkan di luar observed ideal universe.

Jika top10 seluruhnya judged, numerator Recall/DCG benar terhadap labels yang tersedia; relevant luar pool dapat memperbesar true denominator/IDCG. Karena itu Recall_known dan pooled nDCG dapat optimistis dibanding full-qrels values. Tidak membuat completeness claim, inferred relevance estimate atau condensed ranking. Kasus tidak ada known relevant memerlukan aturan berikut, bukan pembagian nol.

### Edge cases dan macro aggregation

| Kondisi | Aturan eksplisit |
|---|---|
| Zero returned results, ada known relevant | Recall/MRR/nDCG bernilai0; tidak ada dummy qrel |
| Ranking kurang dari k | Missing returned positions gain0/no hit; berbeda dari unknown chunk yang benar-benar dikembalikan |
| Unknown returned top10 | Block run-set evaluation; judgment manusia tambahan, tanpa imputasi/drop |
| Pooled query tanpa known relevant | Needs expert evidence search; belum dapat dianggap no-answer. Block query/run-set sampai evidence ditemukan atau no-answer dikonfirmasi exhaustive |
| Confirmed no relevant sebelum freeze | Benchmark dirancang answerable; expert revisi/replace secara versioned sebelum hasil dilihat |
| Confirmed no relevant setelah freeze | Query tetap tercatat; Recall dan nDCG **NA** (denominator0),RR10=0. Laporkan ID/count; jangan replace/drop berdasarkan metode yang kalah |
| Macro mean | Mean per-query dalam scope common-ID yang dipublikasikan. Recall/nDCG mengecualikan confirmed denominator0 sesuai aturan prospektif yang sama untuk semua metode; MRR menyertakan0 tersebut |
| Scope laporan | Dev terpisah; pooled75 terpisah; exhaustive10 terpisah. Selalu tampilkan denominator query valid/NA dan coverage; tidak menggabung untuk menutupi incomplete labels |

Blocked/unfinished judgment bukan kasus no-answer dan tidak boleh hilang sebagai complete-case subset pilihan metode. Primary reported only when common run-set quality gates terpenuhi. Unknown bukan nonrelevant. Rubric2 tidak otomatis disamakan1 pada nDCG. Future evaluator memerlukan hand-calculated synthetic checks untuk graded gains,cutoffs,ties,zero results,NA dan unjudged gates; tidak dibuat atau dijalankan sekarang. Default library gain/tie averaging harus diselaraskan secara eksplisit; [official nDCG API](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html).

### Paired per-query plan — PROPOSED, belum dijalankan

Predeclare R4−R2 dan R4−R3 pada primary scope/metric yang disetujui. Simpan paired query deltas,mean/median difference,wins/ties/losses. Bootstrap pasangan query10,000 resamples seed42 untuk percentile95% CI; tidak mengasumsikan normalitas score/delta. Jika ada lebih dari satu main query per information-need family, resample seluruh family sebagai cluster, bukan memperlakukan paraphrase independen.

Optional significance setelah persetujuan: two-sided paired label-swap randomization test dengan exchangeability null dinyatakan; Holm adjustment untuk dua contrasts. Bukan otomatis t-test atau Wilcoxon hanya karena sample kecil. [IR significance-test research](https://ciir-publications.cs.umass.edu/getpdf.php?id=744) mendukung pemilihan paired analysis secara sadar.

Bootstrap query tidak mengukur uncertainty dari missing labels/assessor; laporkan itu melalui coverage/independent assessment/exhaustive sensitivity terpisah. n10 audit hanya descriptive sensitivity dengan power terbatas; tidak infer seluruh75. Tidak ada statistik/p-value/CI aktual sebelum data tersedia.

## 7. Timing, storage dan hardware

Online query latency mencakup query normalization/tokenization,neural forward bila ada,scoring,sorting; R4 kedua component pipelines sekali plus fusion. perf_counter+CUDA synchronize. Reuse component rankings untuk effectiveness boleh; fusion-only latency tidak disebut hybrid end-to-end.

Pisahkan model loading,warm-up,cold corpus indexing,cache loading,query execution. Cold indexing termasuk serialization/tokenization/embedding/write,exclude model load. Usulan3 warm-ups fixed development inputs,5 timed repeats/query; seeded42 query order identik lintas metode dan direkam. Query embeddings tidak dicache untuk timing; corpus cache resident. Simpan raw latency,query length,median,p95 nearest-rank,mean. Jangan smoke latency menjadi retrieval result.

Ukur RSS/Windows peak working set,min available RAM/commit,PyTorch peak allocated/reserved,sampled nvidia-smi device memory. Laporkan sampling overhead; device memory bukan process attribution otomatis. Logical/allocated index storage terpisah; shared checkpoint dilaporkan terpisah. CPU R1/R2 vsGPU encoder R3/R4 merupakan **system pipeline comparison**, bukan intrinsic algorithm speed. Jangan campur local/cloud atau cold/warm state.

Laptop i7-7700HQ,16GB,GTX1050 4GB;4 CPU threads,batch1,single model process. Historical smoke PASS588 tokens,peak working set4.136GiB,min available RAM sekitar1GiB. Target available6GiB margin rekomendasi,bukan minimum resmi. Persetujuan satu smoke pada4GiB tidak otomatis memberi izin future corpus batch pada kondisi sama. Preflight dinamis dan recorded approval untuk low-margin override diperlukan (**O7 OPEN**).

Usulan watchdog RAM/commit0.2s,GPU2s: stop proses run sendiri jika available<768MiB,commit headroom<1GiB atau memory load>=97% selama>=2s. OOM: log traceback/ID,stop tanpa retry atau cap change,release GPU,partial cache incomplete. Jangan membunuh aplikasi pengguna. CPU FP32 hanya setelah RAM reassessment/approval dan validation terpisah; jangan campur device/precision satu run. Cache/temp/artifacts besar D:. Colab alternatif declared run terpisah,belum diuji.

## 8. Dataset lifecycle, reproducibility dan decision log

18 development dan sekitar75 main tetap usulan. Information needs WO divalidasi pakar sebelum authoring; family separation, main sealing, serta larangan tuning pada final test set tetap berlaku. Pool formation boleh memakai locked main rankings hanya untuk memilih judgment candidates; author/assessor tidak memakai skor effectiveness untuk mengubah queries,parameters,serialization atau pool depth. Freeze parameters sebelum main ranking untuk pooling; freeze adjudicated qrels sebelum metric computation.

Setelah practitioner validation mengubah corpus: buat snapshot baru; simpan snapshot/query/qrels lama read-only. Recheck setiap query answerability dan source evidence pada snapshot baru, generate version baru dari dataset yang disetujui. Mapping old/new chunk IDs memakai source/block provenance untuk review manusia, **bukan otomatis memindah grade karena ID sama**. Semua changed/new chunks dan keputusan relevant diperiksa ulang; carry-forward yang benar-benar identik memerlukan reviewer sign-off dan evidence hash. Main yang sudah pernah dibuka tidak lagi pristine test untuk tuning lanjutan; future tuning memakai development dan test baru yang disetujui atau jelas dilabel exploratory.

Run manifest tetap mencatat snapshot/artifact hashes,fingerprint,protocol SHA,serialization/input hashes,method/model/tokenizer identity,precision/device/hardware,dependency lock,normalization,BM25/RRF params,cutoffs,query/qrels versions+hashes,UTC timestamp,seed,code/cache/resource/completion status. Tambahkan judgment workflow,exhaustive query IDs hash,coverage audit dan metric scope. Uncommitted code dicatat dirty status dan file hashes; tidak perlu commit. Stable ties bukan bitwise floating-point guarantee lintas libraries/GPU.

| Status | Decision | Batas |
|---|---|---|
| **LOCKED FOR PILOT** | L1:R1 unigram TF-IDF,smoothed IDF,L2,exact cosine | Baseline user-specified, bukan optimal |
| **LOCKED FOR PILOT** | L2:R2 BM25Okapi,k1=1.5,b=0.75,epsilon=0.25 | Variant/parameter tidak dituning dari main |
| **LOCKED FOR PILOT** | L3:R3 pinned BGE-M3 CUDA FP16,batch1,max_length640,exact cosine | No truncation; single process |
| **LOCKED FOR PILOT** | L4:R4 BM25+Dense RRF,k=60,equal weights | Shared R2/R3 configurations |
| **PROPOSED** | P1:full Dense371 + semua positive BM25 | Tidak ada top100 candidate cutoff |
| **PROPOSED** | P2:human hybrid C,pool20+outside10,exhaustive10-main,independent subset20% | Budget dan domain-expert availability belum disetujui |
| **PROPOSED** | P3:18dev/75main,family-based split | Counts/category/style allocation perlu finalisasi |
| **PROPOSED** | P4:serialization dedup,scoped metrics,paired analysis | Input info sama; unknown tidak dilabel0 |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O1:primary nDCG@10 pooled75 vs complete scope,paired inference plan | Tidak klaim signifikansi sekarang |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O2:category context/guide metadata-only serialization | Policy dan fingerprint tetap |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O3:query allocation dan predeclared audit10 selection | Sebelum rankings/labels terlihat |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O4:workflow C vs A/B,assessors,time budget,rubric | Dua full assessors bukan syarat mutlak |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O5:candidate policy B dan lexical positive eligibility | Core values locked, candidate recommendation belum final |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O6:preliminary draft dan dataset revision workflow | Practitioner corpus validation pending |
| **OPEN / NEEDS SUPERVISOR APPROVAL** | O7:implementation lock,resource/timing protocol | R5/R6 disabled; belum izin implementation |

Sebelum implementation/evaluation: persetujuan scope,baseline config freeze,validator/schema checks,development calibration,assessor availability,query/qrels provenance/versioning dan resource gates. LOCKED FOR PILOT hanya merekam keputusan konfigurasi inti; tidak memberikan izin coding retrieval atau menjalankan eksperimen. Tidak ada instalasi,model loading,indexing,embedding corpus,query generation,qrels generation,statistical test,commit,push,PR atau deploy pada revisi ini.


## 9. Revision validation, configuration binding dan integrity

TOML SHA-256: **dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300**. Tabel dihasilkan langsung dari TOML dan dicek lagi dengan tomllib Python3.12; Markdown/TOML harus direview bersama jika nilai berubah.

| Config key | Value |
|---|---|
| R1.ngram_range / smooth_idf / norm | [1, 1] / True / l2 |
| R2.k1 / b / epsilon | 1.5 / 0.75 / 0.25 |
| R3.revision | 5617a9f61b028005a4858fdac845db406aefb181 |
| R3.device / precision / batch / cap | cuda:0 / float16 / 1 / 640 |
| R4.k / full_dense_depth / truncated | 60 / 371 / False |
| qrels.exhaustive_two_assessors_required | False |
| qrels.pool.depth / outside | 20 / 10 |
| qrels.exhaustive_audit.main_queries / styles | 10 / [4, 3, 3] |
| qrels.workload.main_primary / secondary / total | 9560 / 4880 / 14440 |
| queries.dev / main | 18 / 75 |
| evaluation.primary_candidate / approved | nDCG@10 / False |
| evaluation.primary_label | nDCG@10 (pooled qrels,75 main queries) |
| evaluation.paired_analysis.normality_assumed | False |
| serialization.max_tokens / overflow640 | 573 / 0 |

Serialization audit diulang dengan tokenizer lokal saja: min83,median136,mean194.33962264150944,p95=497,max573,overflow640=0. Fingerprint tetap **2f4e59835ad4cf81e84f60a5177b6b721c821ddc23970b484de01dd23613ef37**. Semua371 input mempertahankan body; perubahan synthetic administrative metadata/guide tidak memengaruhi serialization. Ini uji allowlist/dedup, bukan jaminan semantik seluruh bahasa body. Semua63 XLSX mempertahankan Sheet/Header/Row context;53 mempunyai guide metadata nonempty. Tidak ada exclusive metadata injection bagi retriever tertentu.

Integrity PASS: **104 protected existing repository files** tetap SHA-256 identik; hanya dua file protokol yang diubah. Source documents tetap50. Keempat artifact hashes cocok dengan frozen snapshot.

Snapshot JSON SHA-256: **279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e**.

Aggregate fingerprint: **7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40**.

Environment check: .venv (1822 files) dan .venv-ml (39774 files) mempunyai path/size/mtime fingerprint identik; package METADATA,pyvenv.cfg,Python executable content hashes identik. Ini metadata/stat verification, bukan rehash setiap model/DLL byte. Tidak ada install atau model loading.

Checks PASS: TOML parse, locked core invariants, workload arithmetic, query/style budgets, complete-vs-pooled metric policy, paired no-normality flags, serialization assertions/fingerprint, XLSX structural context, admin-field exclusion and protected hashes. Validation evidence berada di D:/ModelCache/tmp/method_revision_*; tidak ada module retrieval/benchmark yang ditambahkan.

**STOP setelah focused methodological revision.** Tidak ada retrieval/indexing/corpus embedding/query atau qrels generation/evaluation/statistical tests, commit,push,PR atau deploy.


## 10. Milestone 7B — koreksi encoding dan status draft

Mojibake U+00E2/U+20AC/U+2122 pada character class terbukti dari UTF-8 dan dikoreksi menjadi U+2019. Ini perbaikan representasi policy apostrof existing, bukan tuning lexical dari hasil retrieval. Enum ditambah draft_pending_expert_review dan status penyimpanan draft diselaraskan. Tidak ada perubahan R1–R4, R5/R6, parameter, serialization, candidate policy, split, rubric, metric atau desain eksperimen lain.

18 query dan provenance existing tidak ditulis ulang. Human review package berisi judgment kosong; evidence hanya navigation aid. Validasi Milestone 6 di bagian 9 adalah catatan historis; binding SHA-256 TOML di atas telah diperbarui. Hasil pemeriksaan Milestone 7B berada di development_query_review.md.
