# Milestone 9A.14 — Pilot assessment audit & second review preparation

**MILESTONE 9A.14 — FIRST-PASS AUDITED, SECOND BLIND ASSESSMENT PACKAGE READY**

**AI SILVER — PROVISIONAL. NOT HUMAN VALIDATED.** Tidak ada penilaian kedua, perubahan grade first-pass, ekspansi/merge qrels, tuning atau evaluasi efektivitas dilakukan. Paket siap diberikan pada sesi assessor baru yang benar-benar terpisah.

## 1. Preflight dan integritas

Laporan 9A.12 dan 9A.13 dibaca lengkap. Laporan 9A.13 adalah catatan preparation sebelum first assessment dijalankan; status historical ASSESSMENT_PENDING pada manifest tersebut tidak diubah. File assessment pertama yang dibuat sesudahnya diaudit sebagai artefak terpisah.

Input ditemukan: original pilot30, first assessment30, rubric, pool manifest, frozen V2 chunks, original development queries, existing V2 silver qrels. Input/output checksums pada manifest9A.13 serta baseline protected728 diperiksa ulang. Tidak merekonstruksi assessment yang hilang.

First-pass SHA-256: `398031a6e92eccf26a582038851cfa05d4f7e43021a7589256e6d25cd0f259a6`, cocok dengan hash output yang dicatat saat creation. Pilot/rubric hashes pada provenance cocok dengan source bytes.

Snapshot `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`, fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`. Fingerprint direkomputasi dari sorted-key compact UTF8 JSON artifact_sha256 dan cocok dengan aggregate_fingerprint.value. V2 source/artifact checksums PASS. Original query texts dicocokkan langsung ke queries JSONL; exact serialized input direkomputasi dari frozen chunk menggunakan shared serializer/policy unchanged.

| Check | Result |
|---|---|
| Exactly30 unique assessment IDs/pairs, no missing/extra | PASS |
| Exact query/chunk/document IDs, text hashes, snapshot bindings | PASS |
| Integer0/1/2 or null; RESOLVED/UNRESOLVED mapping | PASS |
| UNRESOLVED null, never0 | PASS |
| Evidence exact substring | PASS30/30 |
| Nonempty rationale | PASS30/30 |
| Uncertainty reason on UNRESOLVED | PASS1/1; null for29 RESOLVED |
| Actual provenance disclosure | PASS: prior context exposure explicitly recorded |
| Semantic validity | NOT ESTABLISHED; technical QC does not prove relevance |

Initial new-validator execution compared the structured fingerprint object against a hash string and stopped before package creation. The audit code was corrected to use `.value` and independently recompute the fingerprint; no research input was repaired or modified. A package test subsequently detected Windows newline conversion in the embedded rubric. The new prompt/ZIP was corrected to preserve original rubric bytes verbatim; no original rubric, first assessment or protected source was rewritten.

## 2. First-pass distribution dan uncertainty

Actual distribution sama dengan reported: **grade0=13, grade1=11, grade2=5, UNRESOLVED=1**. Ini counts, bukan evaluasi ranking atau correctness against human judgment.

| Flagged assessment | First decision unchanged | Audit observation |
|---|---|---|
| WO-POOL-V2-0107 | UNRESOLVED/null | Query meminta cueC03 entrance; chunk memberi handover EVT-01/pemindahan tetapi tidak memetakan C03. Evidence cue pengganti benar ada; uncertainty membutuhkan mapping sumber. Tidak dipaksa0 atau diberi grade baru. |
| WO-POOL-V2-0438 | Grade1 | Position pengantin/vendor/cue terdapat dalam checklist pergantian koordinator. Apakah dukungan itu cukup untuk pertanyaan kesiapan pra-prosesi tetap borderline karena konteks tugas berbeda. |
| WO-POOL-V2-0526 | Grade1 | Headcount dan tambahan terverifikasi ada, tetapi chunk membahas penutupan/evaluasi, bukan pemeriksaan sebelum perubahan seating. Batas useful support vs mismatch tahap perlu ditelaah assessor berikutnya. |
| WO-POOL-V2-0163 | Grade1 | Prinsip peninjauan ulang dan teknisi ada pada readiness garden. Keterkaitan terhadap mikrofon gagal belum memuat alur pemulihan audio khusus; general-to-specific relevance tetap borderline. |

Structural QC, quotation integrity, semantic uncertainty dan assessor independence dilaporkan terpisah. Rationale first-pass tersedia, namun bukan bukti keputusan tersebut benar. Compact export memakai `grade/status/evidence/uncertainty_reason`, berbeda dari nama field rubric asli; mapping ASSESSED→RESOLVED dan evidence-list→single quote terdokumentasi, tanpa mengubah grade/teks. Null uncertainty untuk keputusan RESOLVED tidak berarti tanpa batas konteks; keterbatasan kasus borderline masih disebut rationale dan audit ini.

Provenance first assessor: Codex current conversation; model_id/model_revision/session_id `not_exposed`, bukan identitas yang diverifikasi independen. Timestamp actual recording tersedia; human_validated=false; blindness_status=NOT_FULLY_BLIND_PRIOR_CONTEXT_EXPOSED; no additional context opened; QC same-assessor only; second review NOT RUN. Tidak mengklaim blind independence atau model reproducibility penuh dari field yang tidak diekspos.

## 3. Comparison dengan old silver setelah first-pass QC

**Hanya3 dari30 pairs sudah judged pada old silver; 27 sebelumnya UNJUDGED.** Pada3 common-resolved pairs:2 exact agreement,1 grade conflict. Descriptive fraction2/3=66,67% hanya untuk tiga pasangan itu; bukan high-agreement claim atau estimasi reliability30/654/corpus. UNJUDGED27 bukan old grade0 dan tidak masuk denominator.

| Assessment | Query/chunk | Old grade | First grade | Result |
|---|---|---:|---:|---|
| WO-POOL-V2-0514 | WO-DEV-015 / WO-DOC-016-C004 | 1 | 2 | GRADE_CONFLICT |
| WO-POOL-V2-0236 | WO-DEV-007 / WO-DOC-041-C013 | 1 | 1 | AGREEMENT |
| WO-POOL-V2-0385 | WO-DEV-011 / WO-DOC-041-C003 | 0 | 0 | AGREEMENT |

Grade distance:0 pada2 pasangan,1 pada1 pasangan; tidak ada distance2 pada overlap ini. Conflict **WO-POOL-V2-0514**, old1 vs first2, tetap disimpan dengan kedua labels. Tidak memilih grade pemenang dan tidak overwrite qrel lama.

Raw cross-tab berikut hanya accounting tiga observations, bukan inferential confusion-matrix validation. Rows=old, columns=first:

| Old \ First | 0 | 1 | 2 |
|---|---:|---:|---:|
| 0 | 1 | 0 | 0 |
| 1 | 0 | 1 | 1 |
| 2 | 0 | 0 | 0 |

Weighted kappa old-vs-first **NOT REPORTED**: overlap3 terlalu kecil untuk interpretasi reliability dan exposure konteks membuat independence bermasalah. Tidak melaporkan CI, p-value atau significance. Detailed pair accounting disimpan dalam old_silver_comparison_private.jsonl dan first_pass_audit.json.

## 4. Paket assessor kedua

Berikan **hanya [second_assessor_package.zip](../results/milestone_9a14_pilot_assessment_audit/second_assessor_package.zip)** kepada assessor dalam sesi baru tanpa repository/history. Jangan berikan direktori audit penuh atau laporan ini. ZIP tepat dua entries:

- `pilot_second_input.jsonl`:30 exact same query/chunk texts, aliases dan hashes; tidak memuat grades, scores/ranks/method, styles, old labels, first rationale atau QC conclusions.
- `second_assessor_prompt.md`:instruksi penilaian, output format, safeguards dan **rubric original embedded byte-for-byte**, tanpa grade distribution atau target performance.

Seed baru **14042**, berbeda dari42 pada ledger awal. Inputs diurutkan menurut original assessment_id untuk menetapkan aliases, kemudian di-shuffle Python Random(14042). Assessment/query/chunk IDs memakai PILOT2/QUERY/CHUNK aliases; presentation order berubah, exact text tidak berubah. Private alias_mapping_private.jsonl menyimpan round-trip ke original IDs dan style untuk reconciliation. Natural document references di dalam source text tidak dihapus karena teks harus exact.

ZIP CRC/allowlist/readback, alias round-trip, exact text binding, protected metadata separation dan unchanged embedded rubric PASS. Prompt tidak mengungkap bahwa first assessor tidak blind, grade conflict, flagged cases atau assessment distribution. Alias mapping, old comparison, manifest dan audit files tidak termasuk ZIP.

Readiness bukan proof actual isolation: pengguna harus membuat sesi baru tanpa memory/history/repository/connector access. Catat actual assessor model/revision/session jika tersedia, timestamp, settings, input/output hashes dan exposure disclosure. Kedua AI dapat berbagi model/training bias; sesi terpisah bukan independent human/expert validation.

## 5. Tool comparison setelah hasil kedua tersedia

`scripts/audit_pilot_assessments.py` menyediakan `prepare` dan `compare`. Prepare menolak target existing; jangan rerun menimpa paket saat ini. Compare tidak melakukan model loading/assessment: hanya membaca hasil yang telah diberikan, memvalidasi complete30 aliases/status/evidence, mengembalikan original IDs dan mengeluarkan accounting/adjudication candidates.

Contoh command sesudah actual second output tersedia (belum dijalankan terhadap real second assessments):

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python.exe -B scripts/audit_pilot_assessments.py compare --second 'D:/path/pilot_second_assessments.jsonl' --out 'experiments/results/milestone_9a14_second_comparison'
```

Output comparison.json memuat common-resolved exact grade agreement,3×3 confusion matrix, distance, grade0↔1/1↔2 conflicts, all grade/unresolved distributions, signed difference tendency, serta scope per query style. all_pair_comparisons.jsonl mempertahankan grade/status/rationale/evidence/reason kedua pass; adjudication_candidates.jsonl memuat differences dan seluruh unresolved (termasuk both unresolved), tanpa membuat keputusan otomatis. Output harus berada pada direktori baru; existing targets ditolak.

UNRESOLVED tidak dikonversi0. Common-resolved denominator dicatat eksplisit; excluded cases dihitung sebagai unresolved satu/kedua sisi dan tidak dibuang dari ledger. Weighted Cohen kappa memakai **linear ordinal weights**, disagreement distance |grade_left-grade_right| (normalisasi /2 saling menghilangkan pada ratio), κ=1-observed_distance/expected_distance_from_marginals. Calculable bila n>=2, kedua marginals punya>=2 grade classes dan expected distance>0; selain itu null dengan alasan. Ini syarat mathematical definability, bukan syarat kecukupan statistik. Bila denominator kecil/grade skew sangat tinggi, interpretasi reliability harus ditahan walaupun nilai matematis tersedia. Tidak ada agreement threshold atau majority vote yang mengubah qrels.

Semua kappa yang kelak dihitung berlabel DESCRIPTIVE ONLY pada purposive common-resolved subset. Pair dependence/query clustering, selective unresolved dan shared AI biases membatasi interpretasi; tidak ada klaim human validation, normality, confidence interval atau causality. Style subgroup kecil dan systematic tendency hanya descriptive, bukan bukti assessor superior. Comparison runner mencatat tersedia/tidaknya assessor provenance, tetapi tidak dapat membuktikan konteks sesi secara otomatis.

## 6. Tests dan research integrity

**PASS: 161 distinct regression tests** — 132 offline retrieval/audit tests in `.venv-ml` (57.729 s), including the 8 new targeted tests; 29 ingestion/versioned-pipeline tests in `.venv` (11.216 s). Offline suite additionally verified `TORCH_NOT_IMPORTED PASS`. After making the future comparison use the persisted protected hash ledger instead of depending on temporary baseline availability, all 8 targeted tests were repeated: PASS (0.579 s). Tests cover schema/IDs/evidence, unresolved accounting, alias round-trip, hand-calculated kappa, synthetic-only comparison CLI, frozen bindings and exact rubric bytes/ZIP allowlist. No actual second assessment was generated. The CLI approval-note error in the regression log is an expected negative-test case, not a failed run.

728 existing protected files tetap SHA-256 identik. Termasuk50 source V1/V2,371 chunks, snapshots/fingerprints, original18 queries, qrels, R1–R4 implementation/config dan indices, previous72 rankings, original pilot/rubric/first assessments, serta seluruh artefak9A.12/13. Source/artifact snapshot checks dan input hashes juga diperiksa independen. Baseline/private integrity hashes dipersist dalam protected_integrity.json.

## 7. Files created / changed

- `scripts/audit_pilot_assessments.py` — additive stdlib audit/preparation/comparison CLI + shared serializer existing; tidak mengubah retrieval code.
- `tests/test_pilot_assessment_audit.py` — structural, alias, comparison math/unresolved, synthetic CLI dan published package tests.
- `experiments/reports/milestone_9a14_pilot_assessment_audit.md` — laporan ini.
- `experiments/results/milestone_9a14_pilot_assessment_audit/`:manifest.json, first_pass_audit.json, old_silver_comparison_private.jsonl, alias_mapping_private.jsonl, pilot_second_input.jsonl, second_assessor_prompt.md, second_assessor_package.zip, protected_integrity.json.

Tidak ada existing file changed. Preparation memakai Python existing, UTF8,-B,PYTHONDONTWRITEBYTECODE=1 dan TMP/TEMP D:. Tidak install/download, inferensi GPU/BGE-M3, retrieval/scoring, re-chunk, grading564/654, new qrels, merge, commit/push/deploy.

## 8. Next action dan remaining risks

Pengguna membuka sesi assessor baru yang benar-benar terpisah dan memberikan hanya ZIP dua file tersebut. Jangan membuka mapping/labels lama untuk assessor. Setelah hasil second tersedia, jalankan comparison offline dan review unresolved/conflicts secara terdokumentasi; keputusan akhir tetap memerlukan workflow adjudication/researcher/human review terpisah dan persetujuan pembimbing untuk metodologi utama.

Satu conflict lama tidak membuktikan salah satu grade benar. Nonblind first pass, small purposive pilot, ambiguities antar tahap/event, synthetic corpus dan AI-correlated errors tetap menjadi risiko. Agreement AI-to-AI tidak menaikkan corpus/query/qrels menjadi human/expert ground truth. Tidak melanjutkan expansion atau final evaluation pada task ini.

**STOP — second assessment NOT RUN; package/tools ready.**
