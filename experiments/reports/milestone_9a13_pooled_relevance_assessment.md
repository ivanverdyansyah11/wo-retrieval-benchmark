# Milestone 9A.13 — Pooled relevance assessment preparation

**MILESTONE 9A.13 — JUDGMENT POOL PREPARED, ASSESSMENT PENDING**

**AI SILVER — PROVISIONAL. NOT FINAL EVALUATION.** Paket pool/ledger/rubric siap; assessment pilot maupun batch lanjutan belum dijalankan. Tidak ada proposed grade baru, merge qrels, tuning atau evaluasi efektivitas.

## 1. Audit inputs dan scope

Laporan Milestone 9A.11 dan 9A.12 dibaca lengkap. Input 9A.12 diperiksa ulang terhadap run manifest: outputs SHA-256, 18 original texts/hashes, V2 silver qrels SHA-256, driver SHA-256, konfigurasi efektif serta R3 manifest. Existing full-cloud loader memverifikasi bindings, source/snapshot V1/V2, serialization, pinned model/config, indices dan query caches tanpa inference. Tidak menjalankan ulang retrieval.

Snapshot `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`; fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`. 50 documents, 371 canonical chunks, 18 existing development queries, 72 saved rankings tetap identik. Canonical ordering/text dan snapshot binding diperiksa melalui loader existing.

Scope perubahan hanya additive preparation script, tests, paket hasil baru dan laporan ini. Retrieval implementations, protocol parameters, protected inputs dan output rankings 9A.12 tidak diubah. TOML historical human-assessment design tetap tidak diubah: izin AI silver development terbaru berasal dari instruksi Milestone 9A.13, bukan persetujuan metodologi evaluasi utama.

## 2. Judgment pool

Union top-20 R1–R4 dari ranking saved, exact dedup `(query_id, chunk_id)`: **654 pasangan unik**. 1.440 source occurrences (18×4×20) menjadi 654 records. Masing-masing metode menyumbang 360 occurrences, tetapi kontributor saling overlap dan R4 bukan sumber independen dari komponennya.

| Status existing dalam pool | Count |
|---|---:|
| Existing grade 0 | 46 |
| Existing grade 1 | 14 |
| Existing grade 2 | 30 |
| Existing judged total | 90 |
| UNJUDGED | 564 |

Hanya 564 pairs berpotensi memperoleh label baru. Seluruh 654 masuk blind ledger untuk memungkinkan re-assessment 90 existing pairs sebagai consistency check; label lama tidak diberikan kepada assessor. Existing qrels tetap 684 records: 594 judged pairs lainnya berada di luar top-20 union.

| Query | Style | Pooled | Existing judged | UNJUDGED | Grade 0/1/2 existing | Multi-method |
|---|---|---:|---:|---:|---|---:|
| WO-DEV-001 | lexical_oriented | 39 | 3 | 36 | 1/1/1 | 21 |
| WO-DEV-002 | lexical_oriented | 32 | 6 | 26 | 4/1/1 | 23 |
| WO-DEV-003 | lexical_oriented | 36 | 7 | 29 | 4/1/2 | 23 |
| WO-DEV-004 | lexical_oriented | 30 | 3 | 27 | 0/1/2 | 25 |
| WO-DEV-005 | lexical_oriented | 29 | 4 | 25 | 2/0/2 | 22 |
| WO-DEV-006 | lexical_oriented | 39 | 6 | 33 | 3/1/2 | 26 |
| WO-DEV-007 | semantic_paraphrase | 36 | 4 | 32 | 2/1/1 | 23 |
| WO-DEV-008 | semantic_paraphrase | 38 | 4 | 34 | 3/1/0 | 23 |
| WO-DEV-009 | semantic_paraphrase | 43 | 6 | 37 | 3/0/3 | 23 |
| WO-DEV-010 | semantic_paraphrase | 37 | 4 | 33 | 2/1/1 | 24 |
| WO-DEV-011 | semantic_paraphrase | 39 | 6 | 33 | 4/0/2 | 23 |
| WO-DEV-012 | semantic_paraphrase | 38 | 6 | 32 | 4/0/2 | 23 |
| WO-DEV-013 | mixed_natural | 37 | 6 | 31 | 2/2/2 | 24 |
| WO-DEV-014 | mixed_natural | 33 | 3 | 30 | 1/1/1 | 23 |
| WO-DEV-015 | mixed_natural | 31 | 4 | 27 | 0/2/2 | 22 |
| WO-DEV-016 | mixed_natural | 36 | 4 | 32 | 3/0/1 | 24 |
| WO-DEV-017 | mixed_natural | 37 | 8 | 29 | 5/1/2 | 26 |
| WO-DEV-018 | mixed_natural | 44 | 6 | 38 | 3/0/3 | 25 |

| Metode | Occurrences | Kandidat eksklusif metode ini |
|---|---:|---:|
| R1 | 360 | 50 |
| R2 | 360 | 37 |
| R3 | 360 | 122 |
| R4 | 360 | 22 |

| Jumlah metode yang menemukan pair | Unique pairs |
|---:|---:|
| 1 | 231 |
| 2 | 183 |
| 3 | 117 |
| 4 | 123 |

423 pairs multi-method; 231 ditemukan satu metode saja. Kombinasi asal, ranks dan scores exact dipersist hanya dalam pool_origin_audit.jsonl; pool_summary.csv memuat distribusi per-query/style/topik. Pool dibentuk dari metode locked; kontribusi/overlap tidak digunakan untuk menetapkan grade atau target distribusi labels.

## 3. Blind assessment ledger

- `blind_assessment_ledger.jsonl`: 654 records, semua `PENDING`, grade null.
- `blind_pilot_30.jsonl`: subset 30 records, semua `PENDING`, grade null.
- `pool_origin_audit.jsonl`: audit internal, bukan input assessor; memuat origins, ranks/scores dan existing grades untuk comparison setelah assessment.

Allowlist ledger: assessment_id, query_id, chunk_id, exact query_text, exact serialized_chunk_text, source_snapshot_id/fingerprint, document_id, kedua text hashes, assessment_status, relevance_grade, evidence, rationale, ambiguity_flag, uncertainty_notes, context_opened, assessor_provenance. Semua fields judgment/provenance masih null atau empty list. Tidak ada reviewer/model identity atau timestamp assessment palsu. Manifest timestamp hanya creation time sistem.

Tidak ada method, rank, score, existing label, preferred method, performance atau style/topic selection fields pada payload assessor. Serialized text sama dengan retrieval input, bukan ringkasan atau potongan. Title/heading/category/guide_context yang telah menjadi retrieval serialization existing tetap tersedia; operational status di dalam sumber bukan relevance label. Query ID dan document ID tetap ada sesuai binding yang diminta.

Assessment IDs ditetapkan stabil dari sorted `(query_id,chunk_id)`, kemudian Python `random.Random(42).shuffle` dengan Python 3.12.14. IDs tidak berasal dari ranks. Stored JSONL order dan checksums adalah acuan reproducibility. Membalik urutan input ranking menghasilkan pool dan ledger identik; duplicates ditolak.

## 4. Rubric dan pilot workflow

[Rubric/workflow assessor](../results/milestone_9a13_judgment_pool/rubric_workflow.md) memisahkan grade 2 (direct substantive support), grade 1 (useful partial support), grade 0 (examined, no useful support), UNRESOLVED (grade null) dan PENDING (belum dinilai). Tidak ada keyword/similarity classifier untuk menghasilkan relevance. Grade tetap untuk chunk, bukan jawaban dari dokumen lain; jika konteks dibuka, catat locator/hash/excerpt dan jangan memindahkan jawaban ke chunk.

Pilot dipilih sebelum labels: setiap query satu kandidat dalam shuffled order, lalu tambah kandidat hingga 10 per style. Hasilnya 30 pairs, 18 query terwakili, 10 lexical_oriented + 10 semantic_paraphrase + 10 mixed_natural. Selection tidak menggunakan rank, skor atau existing grade. Format chunk pilot: 20 DOCX, 5 PDF, 2 XLSX, 3 TXT; serialized text 433–1.859 karakter. Variasi ini memberi materi berbeda untuk kalibrasi, tetapi tingkat kesulitan sebenarnya belum dinilai; tidak mengklaim balance easy/hard berdasarkan labels yang belum ada.

Quality gate menuntut pemeriksaan seluruh pilot untuk exact evidence, direct answer vs topical similarity, substantive consistency, assumptions, ambiguity/unresolved dan lexical anchoring. Distribusi grade hanya dideskripsikan, tidak dipaksa seimbang. Schema PASS tidak membuktikan semantic correctness. Review kedua jika tersedia harus menerima input tanpa grade/rationale pertama; simpan kedua outputs dan disagreement sebelum reconciliation. Sesi AI kedua tidak otomatis independent expert validation.

## 5. Keterbatasan mekanisme assessment

**Assessment NOT RUN.** Tool catalog yang tersedia tidak menyediakan endpoint configured untuk isolated structured relevance assessment dengan actual model/session provenance yang digunakan pada task ini. Tidak ada layanan grading eksternal atau model lokal dipanggil. Konteks assistant saat ini sudah membaca ranking dan label lama dari pekerjaan sebelumnya; menilai langsung dalam konteks ini lalu menyebutnya blind akan menyesatkan. Tidak membuat sesi assessor baru atau mengklaim independent/blind grading yang tidak terjadi.

Ini menerapkan fallback eksplisit pada instruksi pengguna: jika mekanisme assessment yang dapat diandalkan tidak tersedia, siapkan ledger, rubric dan workflow, lalu STOP. Batas ini berasal dari kondisi assessment/task, bukan kewajiban approval skill. Tidak mengarang labels untuk memenuhi completion target.

| Assessment result | Status |
|---|---|
| Pilot grading | NOT RUN; 30 PENDING |
| Remaining batch grading | NOT RUN |
| Proposed new judgments | 0 |
| Blind re-assessment existing 90 pairs | NOT RUN |
| Assessor provenance | null / NOT RUN |
| Second blind review | NOT RUN |
| Existing/new disagreements | NOT COMPUTED, bukan zero confirmed disagreements |
| UNRESOLVED decisions | NOT ASSESSED, bukan zero confirmed ambiguity |
| All pool records | 654 PENDING |

PENDING dan UNRESOLVED dibedakan: tidak menilai record sama sekali bukan keputusan bahwa chunk ambigu/tidak relevan. Tidak dibuat proposed qrels atau disagreement records kosong yang dapat disalahartikan sebagai assessment selesai.

## 6. Coverage re-audit

Coverage existing dihitung ulang dari saved rankings dan unchanged V2 silver qrels untuk 18 queries ×4 methods ×5 cutoffs =360 records. File coverage_existing.csv memisahkan grade0/1/2, UNJUDGED, returned count dan missing slots. Judged coverage=judged/returned, bukan relevansi atau ketepatan retrieval. Grade0 tetap judged; absent label tetap UNJUDGED, bukan0. Tidak ada missing top-k slots pada hasil ini.

| Method | k | Grade 0 | Grade 1 | Grade 2 | Judged/returned | UNJUDGED % |
|---|---:|---:|---:|---:|---:|---:|
| R1 | 1 | 0 | 1 | 5 | 6/18 | 66.67 |
| R1 | 3 | 1 | 4 | 11 | 16/54 | 70.37 |
| R1 | 5 | 2 | 5 | 13 | 20/90 | 77.78 |
| R1 | 10 | 12 | 8 | 19 | 39/180 | 78.33 |
| R1 | 20 | 26 | 10 | 22 | 58/360 | 83.89 |
| R2 | 1 | 0 | 0 | 6 | 6/18 | 66.67 |
| R2 | 3 | 2 | 2 | 11 | 15/54 | 72.22 |
| R2 | 5 | 3 | 5 | 13 | 21/90 | 76.67 |
| R2 | 10 | 8 | 5 | 18 | 31/180 | 82.78 |
| R2 | 20 | 25 | 9 | 24 | 58/360 | 83.89 |
| R3 | 1 | 0 | 1 | 8 | 9/18 | 50.00 |
| R3 | 3 | 2 | 3 | 14 | 19/54 | 64.81 |
| R3 | 5 | 4 | 5 | 21 | 30/90 | 66.67 |
| R3 | 10 | 10 | 8 | 26 | 44/180 | 75.56 |
| R3 | 20 | 22 | 11 | 27 | 60/360 | 83.33 |
| R4 | 1 | 0 | 1 | 9 | 10/18 | 44.44 |
| R4 | 3 | 1 | 4 | 16 | 21/54 | 61.11 |
| R4 | 5 | 3 | 7 | 20 | 30/90 | 66.67 |
| R4 | 10 | 8 | 8 | 25 | 41/180 | 77.22 |
| R4 | 20 | 19 | 11 | 29 | 59/360 | 83.61 |

Remaining corpus-wide UNJUDGED tetap **5.994/6.678**; existing grade distribution tetap **621/32/31**. Actual projected proposed coverage **NOT COMPUTED**, karena belum ada proposed assessments/quality checks semantic. Tidak menyajikan 100% sebagai hasil ekspansi yang sudah selesai.

Batas hipotetis administratif saja: jika seluruh 564 unjudged pooled pairs kelak mendapat grade valid dan accepted, dengan existing labels tetap dipertahankan, total labeled-pair presence menjadi 1.248/6.678 (18,69%) dan remaining unknown 5.430. Coverage top-1/3/5/10/20 pada saved contributor rankings dapat mencapai100% karena seluruh window berada dalam union20. Ini bukan achieved/projected result dari assessment, bukan relevant-set completeness, bukan human validation dan bukan bukti metric validity. UNRESOLVED serta conflicts dapat menghalangi acceptance; jangan memakai asumsi ini untuk evaluasi.

## 7. Tests, reproducibility dan integrity

**153 tests PASS**: 124 retrieval/offline tests in `.venv-ml` (51,113s) +29 ingestion/versioned pipeline tests in `.venv` (10,576s). Termasuk 8 tests baru: exact dedup, deterministic shuffle/reconstruction, pilot strata/all-query inclusion, exact binding, strict blind fields, text tamper rejection, grade schema/bool rejection, unresolved preservation, exact evidence substring, published-pool/source mapping dan protected hashes. Synthetic grade fixtures adalah test-only, tidak dipersist sebagai judgments nyata.

Coverage baru360 rows dibandingkan field-by-field dengan existing 9A.12 coverage.csv: PASS, unchanged. Seluruh experiment TOML parse PASS; existing protocol consistency/version isolation/cache regressions PASS. Real evidence relevance dan semantic grading consistency NOT TESTED karena assessment NOT RUN. Retrieval/offline suite memastikan Torch tidak diimpor. Expected CLI rejection/mock STOPPED messages pada logs adalah negative-path fixtures, bukan live GPU executions.

716 existing files dibandingkan SHA-256 sebelum dan setelah pool preparation: PASS. Baseline meliputi protected corpus/query/qrels/snapshot/index V1/V2, protocol/environment files serta seluruh 9A.12 ranking/output artifacts dan existing code/tests. Before hashes dipersist dalam protected_integrity.json. Input/output hashes, effective snapshot, shuffle/seed, timestamps dan driver hash dicatat pada manifest.json. Artifact status POOL_PREPARED_ASSESSMENT_PENDING tidak berarti qrels COMPLETE.

Preparation command: `PYTHONPATH=src .venv-ml/Scripts/python.exe -B scripts/prepare_judgment_pool.py` dengan PYTHONDONTWRITEBYTECODE=1, UTF-8, TMP/TEMP di D:. Baseline input audit di D:/ModelCache/tmp/wo-m9a13/baseline.json. Script menolak target yang sudah ada; jangan rerun menimpa paket. Tidak ada retrieval run, Torch import, GPU/model loading, installation/download atau index rebuild.

## 8. Files created / changed

- `scripts/prepare_judgment_pool.py` — additive reconstruction, blind ledger, schema/evidence checks dan unchanged-qrels coverage.
- `tests/test_judgment_pool.py` — synthetic/published pool tests; tidak menghasilkan real grades.
- `experiments/reports/milestone_9a13_pooled_relevance_assessment.md` — laporan ini.
- `experiments/results/milestone_9a13_judgment_pool/`: manifest.json, blind_assessment_ledger.jsonl, blind_pilot_30.jsonl, pool_origin_audit.jsonl, pool_summary.csv, coverage_existing.csv, rubric_workflow.md, protected_integrity.json.

Tidak ada existing file changed. Semua output baru terpisah dari benchmark resmi. Existing 684 judgments tetap immutable; tidak ada proposed expanded qrels yang di-merge.

## 9. Risks dan recommended next milestone

Pooling top20 hanya mencakup hasil empat locked methods; outside-pool relevance tetap tidak diketahui. Coverage tinggi setelah labeling pun tidak menyelesaikan pooling bias. AI-correlated errors, lexical anchoring, permissive topical judgments dan synthetic/AI-corrected corpus bias tetap mungkin. Metadata blinding mengurangi satu sumber bias, bukan menghilangkan training/model/researcher bias. Query editorial ambiguities tidak diperbaiki berdasarkan hasil retrieval.

Usulan next milestone: configured isolated blind pilot assessment. Pengelola menyerahkan hanya rubric_workflow.md dan blind_pilot_30.jsonl ke assessor dengan konteks baru, actual model/version/session/parameters dan audit hashes tercatat. Jangan memberikan laporan ini, origin audit, run manifest, existing qrels atau riwayat percakapan. Tinjau30 output terhadap rubric dan evidence sebelum batch lanjutan; lakukan blind second review bila tersedia, dengan status NOT RUN bila tidak. Setelah quality checks PASS, simpan proposed assessments separately dan comparison disagreements; assessment di luar pool memerlukan sampling plan/approval terpisah.

Untuk manusia/expert/researcher: nilai dalam ledger terpisah dengan actual role, rationale, durasi dan provenance nyata; jangan otomatis menyalin AI grade sebagai sign-off. Persetujuan pembimbing diperlukan untuk peran single-assessor, penggunaan silver atau pooled metrics dan metodologi utama. Jangan tuning retrieval atau final test berdasarkan proposed labels. Corpus/query/final-methodology validation status tidak dinaikkan oleh paket ini.

**STOP — JUDGMENT POOL PREPARED, ASSESSMENT PENDING.**
