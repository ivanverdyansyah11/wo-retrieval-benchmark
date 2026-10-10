# Milestone 8D-A — Non-GPU Four-Retriever Equivalence Audit

**PASS untuk parity, interface fixtures, matematika RRF dan index integrity secara non-GPU. Live R4 end-to-end NOT TESTED; Milestone8C tetap `end_to_end_pending`.**

Kesetaraan di sini berarti input/information access, mapping dan kontrak interface yang konsisten; bukan identik ranking R1–R4, bukan benchmark efektivitas atau bukti bahwa satu metode unggul. Corpus/query tetap pending expert validation.

## 1. Scope dan execution guard

Inspect shared lexical/text, dense/index/model/resources/CLI, hybrid/retrieval/CLI serta benchmark Markdown/TOML existing. Tidak ada perubahan kode, parameter, threshold atau indeks. Actual loaders dipanggil secara langsung; tidak memakai hybrid.ready/CLI audit karena jalur itu membuat BGEEncoder/AutoTokenizer.

Satu audit subprocess memasang import guard yang menolak torch, transformers dan FlagEmbedding; BGEEncoder constructor/load/encode juga assertion-only in-memory. Guard tetap aktif selama tests. Ketiga module tidak ada di sys.modules saat selesai. Tidak ada BGE/tokenizer initialization, CUDA call, model loading, live query encoding atau inference. Local checkpoint12 files hanya di-stream untuk SHA256; package versions dibaca melalui metadata, bukan runtime imports.

External audit script: `D:/ModelCache/tmp/wo-m8d-a/audit.py`; raw results/tests logs di folder sama. Tiny synthetic regression matrices/checkpoints ditulis hanya ke disposable temporary directories; tidak ada actual corpus indexing/embedding atau production cache writes.

## 2. Status matrix

| Area | Status |
|---|---|
| 371 unique IDs/shared snapshot/serialized input/XLSX context | PASS_NON_GPU |
| Common interface and error/tie/uniqueness behavior | PASS_NON_GPU_FIXTURES |
| RRF exact math/eligibility/full Dense371 | PASS_NON_GPU |
| R1/R2/R3 complete index identity/hash/shape/norm integrity | PASS_NON_GPU |
| R3/R4 live query-vector identity and actual R4 GPU end-to-end | NOT TESTED |
| Query vector cache reuse from prior R3 | NOT AVAILABLE_IN_AUDITED_LOCATIONS |
| WO corpus/query relevance and answerability validation | PENDING_EXPERT_VALIDATION |

## 3. Shared371 universe, snapshot dan independent serialization

R1/R2 actual persisted documents.json dibandingkan persis dengan current shared prepare output. R3 rows.json diverifikasi independently chunk_id/document_id/serialized_text_sha256 terhadap frozen chunks, kemudian existing load_vectors memverifikasi complete identity/checksum/shape/norm. R4 constructor memverifikasi cross-index identity, universe dan text-hash mapping lalu memakai R2/R3 existing; tidak ada R4 corpus index atau serializer baru.

Independent reference serializer memakai literal approved field set title/heading/category/text, NFC/LF/outer trim, casefold/collapsed-whitespace Unicode word-boundary dedup, selection heading→title→category, emission title→heading→category dan exact prefix/body separators. Hasil371/371 byte-identical dengan shared serializer dan persisted lexical input. JSON canonicalization/hash dihitung ulang dengan hashlib, bukan hanya membandingkan dua manifest yang mungkin sama-sama stale.

| Identity | Value |
|---|---|
| Snapshot | `WO-CORPUS-V1-DRAFT-PILOT-001` |
| Snapshot aggregate fingerprint | `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40` |
| Chunk universe hash | `6bc63ce997da6e80df7b954a476dc46f959bf339986e8c28d389aa8f28f8d6c3` |
| Serialized retrieval input hash | `dfad6b5237f3a0d2538b3c4da8e86cbc73fb392f0a9602c661fe93d9f8e4961c` |
| Snapshot JSON SHA256 | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` |
| Protocol TOML SHA256 | `dbfc1e5b5ab21fa09b429c5fa4f25c390abaa1d8cc137c32ae63f8fae83b2300` |

Only title/heading/category/text dapat memengaruhi retrieval input; source locators/IDs/status/event metadata/guide_context tetap audit metadata. Sentinel query_evidence/qrels/guide metadata serta perubahan source_locator/document_id/status pada371 in-memory test copies tidak mengubah serialization. Tidak ada file query/provenance/qrels dibaca oleh shared serializer/index constructor. Uji ini membuktikan tidak ada injection dari field tersebut; tidak mengklaim menilai semantic leakage authoring secara otomatis. Source text memang boleh berisi istilah event/operasional sebagai bagian corpus.

XLSX: 63 chunks, 53 dengan metadata guide_context, 356 row-locator occurrences checked. Semua serialized body mempertahankan Sheet/Section/Header/Row dan nomor row source. Body frozen dipertahankan utuh; operational guide yang sudah berada dalam text tetap retrievable untuk semua metode. Full metadata guide_context tidak diinjeksi ulang. Header semantics/kecukupan domain tetap membutuhkan review manusia.

Cached token-count fingerprint juga cocok approved audit, tetapi token count tidak dihitung ulang menggunakan tokenizer live; task melarang BGE initialization. Model/tokenizer hashes dan saved rows binding diverifikasi. R1/R2 lexical preprocessing serta BGE tokenizer berbeda merupakan bagian metode, bukan tambahan informasi eksklusif.

## 4. Shared interface audit

Common dataclass fields: `method_id`, `chunk_id`, `document_id`, `rank`, `score`, `snapshot_id`. R1/R2/R3/R4 mengembalikan list[RetrievalResult], rank1-based, finite scores dan ID/document/snapshot yang sesuai. Real-index constructors R1/R2/R3/R4 PASS tanpa query inference; empty/whitespace, invalid query types serta invalid top_k diverifikasi pada keempat actual objects. Synthetic fixtures memverifikasi nonempty output schema, ranking, top-K dan duplicates.

| Behavior | R1/R2 | R3 | R4 |
|---|---|---|---|
| Eligible candidates | score>0; zero/negative excluded | all finite including zero/negative | full Dense union positive BM25 |
| Empty whitespace | [] | [] without encoder call | [] without component calls |
| Invalid query type | ValueError | ValueError | ValueError |
| Invalid top_k | reject bool/noninteger/<=0 | same | same |
| Tie policy | unrounded score desc,ID asc | same | same on RRF score |
| Nonempty unknown-vocabulary query | may return [] | requires query vector; full ranking | Dense-only if BM25 empty |

Different OOV/eligibility behavior is intentional per protocol. Finite/duplicates/missing Dense ranks/metadata mismatches fail; no dummy result filling. Deterministic ties do not imply semantic relevance or cross-device bitwise neural reproducibility. Actual BGE query output validity and R3/R4 same live query vectors remain NOT TESTED in this audit.

## 5. Independent RRF mathematical audit

Oracle memakai fractions.Fraction exact rational arithmetic, independent dari production fuse. Synthetic BM25 B9/A2/C0/D−1 dan Dense A0.9/C0.2/D0/B−0.1. Eligible BM25 ranks B1/A2; C/D absent, tanpa pseudo-rank. Dense ranks1–4. Formula sum1/(60+one-based rank); float outputs cocok rational oracle tolerance1e−16.

| Chunk | BM25 rank | Dense rank | BM25 contribution | Dense contribution | RRF total | Rank |
|---|---:|---:|---:|---:|---:|---:|
| A | 2 | 1 | 0.016129032258064516 | 0.016393442622950821 | 0.03252247488101534 | 1 |
| B | 1 | 4 | 0.016393442622950821 | 0.015625 | 0.032018442622950824 | 2 |
| C | absent | 2 | 0 | 0.016129032258064516 | 0.016129032258064516 | 3 |
| D | absent | 3 | 0 | 0.015873015873015872 | 0.015873015873015872 | 4 |

BM25 score magnitude×100 tanpa rank/eligibility changes menghasilkan RRF identik. Synthetic371 Dense candidates menempatkan C370 pada Dense rank371 dan BM25 rank1; hasil tersebut tetap ikut fusion dan menjadi top result menurut formula, membuktikan tidak ada hidden top100 cutoff. Tests existing juga memverifikasi equal-score ties/ID order, zero/all-absent BM25 dense-only, malformed/duplicate/incomplete coverage rejection, same normalized query/depth dan top-K. Fixtures bukan query embeddings, qrels atau benchmark score.

## 6. Index and protected integrity

R1/R2 existing loaders memverifikasi metadata identity/config/code/dependency, complete status, artifacts dan reserialized source rows. Audit juga melakukan independent artifact SHA256. R3 expected identity dibangun ulang dari current config/code/dependency metadata,12 freshly hashed local model/tokenizer files dan saved mapping; directory key cocok current COMPLETE index. Manifest/row/vector hashes juga cocok accepted8B audit.

Matrix actual shape[371, 1024], dtypefloat32, finite, norm min0.9999998808/max1.0000001192. Tidak ada similarity scoring menggunakan corpus vector sebagai query. R4 cross-index constructor PASS; no new fusion index.

All139 existing repo files byte-identical. 50 source document SHA256 cocok corpus_manifest masing-masing; snapshot/protected artifact hashes cocok. Source, canonical, frozen chunks, pilot/snapshot, protocol, queries/provenance/review workbook, existing reports/code/tests/README dan R1/R2 indices unchanged. R3 loaders memverifikasi against accepted identity/payload hashes. Git unavailable; checks menggunakan SHA256. Tidak ada install atau environment change.

## 7. Tests

**51 tests PASS**: R416, lexical14, Dense16, protocol5. Tests berjalan dengan ML import/BGE initialization guards. TOML parse dan Markdown consistency PASS via existing protocol tests. Corrupt/incomplete/stale index, snapshot mismatch, shared input/source mutation, mathematical expected score, interface/empty/invalid/topK/tie cases tercakup. Parser/chunker25 tests tidak diulang karena kode tidak berubah. Test logs: `D:/ModelCache/tmp/wo-m8d-a/tests.log`.

## 8. Existing query vector cache availability

**NOT FOUND pada audited locations.** Inventory benchmark cache387 files: 372 arrays =1 complete corpus NPY371×1024 +371 incomplete corpus-row NPY checkpoints. Tidak ada unclassified query array. Seluruh371 checkpoint diverifikasi terhadap progress identity/mapping, chunk ID, per-row SHA256 dan exact equality dengan row COMPLETE corpus matrix; klasifikasi corpus tidak hanya berdasarkan filename. Repository experiments/data benchmark hanya memiliki R1 matrix.npz sebagai array lain; bukan dense query cache.

R3 accepted run menyimpan3 smoke_results dengan keys actual_tokens/query_id/results/seconds/text/validation_status. Stored top5 scores/ranks, token count dan shape/finite summaries bukan payload embedding. JSON key scan dan numeric1024-vector candidate scan pada run/report JSON tidak menemukan query payload. Pipeline source juga menunjukkan query vector sebagai local ephemeral value; writes NPY hanya pada corpus checkpoint path.

Tidak ada query-vector revision/dimension/input-hash/payload binding yang dapat diverifikasi karena artifact tersebut tidak tersedia. Pinned corpus model revision diketahui, tetapi tidak dipromosikan menjadi metadata embedding query yang tidak ada. Tidak membuat, menebak atau memakai corpus vectors sebagai query. Scan terbatas pada approved benchmark cache, repository experiments/data benchmark dan saved run/report JSON; bukan forensic seluruh drive.

## 9. Separate query encoding — design only

**Feasible sebagai desain; belum diimplementasikan/disetujui untuk run.** ProcessA memakai existing BGEEncoder dengan pinned checkpoint, token cap/no-truncation dan resource gates. Encode each approved query once, atomically publish payload+manifest, lalu release model/exit. ProcessB memverifikasi frozen snapshot dan COMPLETE corpus indices, memakai CPU exact dot/BM25/RRF tanpa BGE/tokenizer creation.

Minimal future addition: validated cached-vector encoder adapter dengan encode(text)->payload, diinjeksi ke existing DenseRetriever; HybridRetriever memakai DenseRetriever yang sama. Tambahkan command producer/consumer di module baru di luar shared retrieval/dense hash-glob folders. Algorithm/serializer/BM25/RRF/exact dot dapat tetap existing. Consumer loader perlu mengikuti validated model_files/cache_identity/load_vectors metadata-only path, bukan hybrid.ready yang membangun BGEEncoder.

Query payload stage harus eksplisit. Opsi paling kecil untuk unchanged DenseRetriever adalah menyimpan exact float32 output BGEEncoder.encode **sebelum** project unit_vectors; adapter mengembalikan payload tersebut, sehingga normalization existing terjadi sekali seperti jalur live. Official model mungkin sudah menormalisasi output pada FP16; label stage tetap diperlukan. Jangan menyimpan post-unit_vectors lalu diam-diam menormalisasi ulang dan mengklaim bitwise equivalence.

Metadata wajib: query ID/dataset version/file SHA; raw dan normalized effective text hashes; query normalization/policy; snapshot fingerprint dan Dense index identity; model/revision/checkpoint/tokenizer hashes; actual tokens incl specials/max_length/truncation=false; pooling/dense-only/device/precision/batch; shape/dtype/exact normalization stage/norm stats; payload SHA; dependency/code/config hashes; UTC timestamp dan COMPLETE marker. R3 standalone dan R4 component harus membaca identical checksummed payload untuk same normalized text dan same corpus matrix, tanpa second neural encode.

Cache safety: NPY allow_pickle=False, bounded1×1024 float32, finite/nonzero/norm-stage checks, strict all identities/input/payload hashes, atomic publication; reject stale/missing/corrupt cache, no automatic encoding/regeneration/fallback. Same query_id dengan changed text tetap cache miss. Source/wording/model/protocol/device/normalization changes memerlukan explicit new cache identity.

Quality dan latency berbeda: offline scoring dengan common precomputed query vectors dapat membantu future quality comparison setelah human qrels dan protocol approval; tidak mengukur query encoding. Ukur query encoding/model loading, cache I/O/IPC, CPU scoring+BM25+RRF, dan actual complete two-process wall time secara terpisah. Cache-hit CPU time tidak disebut R3/R4 end-to-end latency. Two-process cold/load timings bukan resident-model protocol timings. Current TOML cache_query_embeddings_for_latency=false; alternatif ini memerlukan approval protokol/timing sebelum implementasi/evaluasi, bukan silently replacing pipeline.

Mengubah dense/*.py atau retrieval/*.py akan mengubah code-bound component identity dan menolak existing index; jangan bypass/relabel cache lama. Separate adapter dapat menjaga component code untouched, tetapi new mode/code/R4/run identity harus dicatat. Tidak ada kode alternatif dibuat sekarang.

## 10. Remaining risks dan readiness

Non-GPU parity/interface/math/integrity siap untuk review dan perencanaan human validation. Live BGE query encoding, identical actual R3/R4 query-vector usage, full R4 GPU model loading/end-to-end, resource stability dan latency belum diuji sekarang. Historical R3 GPU PASS bukan bukti current R4 end-to-end PASS. Milestone8C tetap end_to_end_pending.

Corpus masih pending_practitioner_validation;18 queries draft_pending_expert_review; no qrels. Domain expert harus menilai kebutuhan informasi, answerability, naturalitas, operational relevance dan source sufficiency. Tidak ada Recall/MRR/nDCG, method superiority atau relevance labels otomatis.

Output hanya dua report yang diminta. Tidak ada protocol/code/index/corpus/query changes, GPU/CPU model fallback, retry, threshold override, download/install, commit/push/PR/deploy. **STOP setelah Milestone8D-A; langkah lanjut memerlukan review/persetujuan terpisah.**
