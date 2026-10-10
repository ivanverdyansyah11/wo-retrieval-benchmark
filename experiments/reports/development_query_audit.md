# Milestone 7A — Development query audit (DRAFT)

Created at: 2026-10-08T16:07:58.121Z
Dataset version: development-v1-draft
Every query/provenance status: `draft_pending_expert_review`.
Snapshot: `WO-CORPUS-V1-DRAFT-PILOT-001`; corpus `v1-draft`; validation `pending_practitioner_validation`.

## Scope and provenance

Prepared 18 candidate development questions, 18 linked provenance records and an unfilled practitioner review/timing template. All outputs are DRAFT, not validated or frozen. No practitioner judgments or timings have yet been collected.

Read both Milestone 6 protocols and parsed TOML with Python standard-library `tomllib`. Studied all 50 canonical operational documents through titles, sections, operational passages and structured table context; selected evidence passages were read in full. Existing canonical extraction was used rather than rerendering all 50 binary originals. Source files were hashed read-only. The inventory below identifies the scope of the document study.

Only operational document blocks ground the queries. Summaries, quality reports, manifests and inventories are not answer-bearing evidence. The underlying documents are researcher-composed operational drafts. These are AI-assisted corpus-grounded candidates, not collected practitioner utterances or confirmed real-company incidents. `author_id=codex_ai_assisted_draft` records this explicitly; `expert_review_id` is null.

Evidence pointers are non-exhaustive manual navigation aids selected while drafting. They are not retrieved candidates, qrels, grades, an answer key or a final relevant chunk set. Other sections/documents may also address the information need.

## Protocol consistency and decisions

- Kept protocol-required fields, `split="pilot"` for development, style values and separate provenance. Each query also carries information need, scenario, role, family ID and snapshot context.
- Current TOML validation enum is `draft/expert_reviewed/frozen`. The user explicitly requires `draft_pending_expert_review` for this milestone; that status is used as an intentional exception, not claimed to satisfy the older enum. A future authorized schema alignment is needed for strict loaders.
- TOML still says `queries.status="DESIGN_ONLY_NO_RECORDS"`. These newly authorized draft records make that descriptive status historically stale; the protocol was left untouched as instructed.
- Lexical-oriented means ordinary operational terminology, not keyword stuffing; semantic/paraphrase means everyday wording of a different need, not six paraphrases of lexical questions; mixed/natural combines scenario language and operational terms.
- Styles do not label expected method winners. No retrieval scores, embeddings or method-specific expansions informed wording. Corpus-grounded drafting may still induce vocabulary/source-selection bias; practitioner review must assess that.
- All 18 information-need families are distinct and reserved for development. Future main queries must not reuse their intent/paraphrase families. Main queries do not exist yet, so cross-split separation cannot yet be certified.
- R1–R4 settings, corpus, chunks, snapshot, parser/chunker and environments remain unchanged. Draft preparation authorizes no retrieval implementation.

## Distribution

| Primary category | Lexical-oriented | Semantic/paraphrase | Mixed/natural | Total |
| --- | ---: | ---: | ---: | ---: |
| A. Struktur Tim dan Job Description | 1 | 1 | 0 | 2 |
| B. Persiapan Sebelum Acara | 1 | 1 | 0 | 2 |
| C. Wedding Day Operation | 1 | 0 | 1 | 2 |
| D. Vendor Management | 1 | 0 | 1 | 2 |
| E. Contingency / Problem Handling | 1 | 1 | 1 | 3 |
| F. Venue Operation | 0 | 1 | 0 | 1 |
| G. Guest dan Family Handling | 0 | 1 | 1 | 2 |
| H. Rundown dan Timeline | 0 | 0 | 1 | 1 |
| I. Internal Communication / Escalation | 0 | 0 | 1 | 1 |
| J. Post-event / Evaluation | 1 | 1 | 0 | 2 |
| Total | 6 | 6 | 6 | 18 |

Coverage spans all 10 categories and preparation, on-day execution, disruptions, venue survey and post-event needs. The allocation is for this small development draft, not a claim about operational frequency or the final main-query allocation.

## All 18 candidates

Evidence IDs identify canonical blocks within documents. Full source filenames, document titles, headings and source locators appear in the provenance JSONL. XLSX references include original sheet, row and header context. Header/guide pointers are aids, not relevance labels.

| Query ID | Question | Category | Style | Information need | Evidence pointers (not qrels) |
| --- | --- | --- | --- | --- | --- |
| WO-DEV-001 | Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim? | A | lexical_oriented | Mengetahui pengesah operasional dan pelaksana pengelolaan daftar registrasi. | WO-DOC-006/s1-r0016; WO-DOC-006/s2-r0011 |
| WO-DEV-002 | Pada H-1, apa yang harus diperiksa dalam final confirmation ketika kebutuhan loading vendor berbeda dari izin venue? | B | lexical_oriented | Mengetahui pemeriksaan dan penyelesaian selisih kebutuhan akses vendor dengan izin lokasi. | WO-DOC-009/b0014; WO-DOC-009/b0019 |
| WO-DEV-003 | Apa saja prasyarat cue C03 entrance sebelum floor memberi aba-aba jalan? | C | lexical_oriented | Mengetahui prasyarat operasional pelepasan cue entrance resepsi. | WO-DOC-017/p001-b011; WO-DOC-017/p001-b013 |
| WO-DEV-004 | Apa yang harus dikonfirmasi kepada makeup artist agar jadwal makeup tidak berbenturan dengan standby akad? | D | lexical_oriented | Mengetahui data layanan makeup yang harus diselaraskan dengan jadwal kesiapan pasangan. | WO-DOC-024/b0008; WO-DOC-024/b0011 |
| WO-DEV-005 | Jika mikrofon gagal saat sambutan, bagaimana alur penanganan dan pemeriksaan sebelum audio dipakai lagi? | E | lexical_oriented | Mengetahui koordinasi pemulihan gangguan mikrofon dan pemeriksaan sebelum kegiatan dilanjutkan. | WO-DOC-031/p002-b003; WO-DOC-031/p002-b011 |
| WO-DEV-006 | Saat checkout, apa yang perlu dicocokkan pada daftar aset WO sebelum barang diserahterimakan? | J | lexical_oriented | Mengetahui pemeriksaan aset WO dan pencatatan penerima saat penutupan kerja. | WO-DOC-048/s1-r0022; WO-DOC-019/b0013 |
| WO-DEV-007 | Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru? | A | semantic_paraphrase | Mengetahui tindakan kru ketika menerima instruksi operasional yang bertentangan. | WO-DOC-001/b0020 |
| WO-DEV-008 | Seminggu menjelang acara, bagaimana mencatat pekerjaan yang belum tuntas agar tetap ditindaklanjuti sampai hari pelaksanaan? | B | semantic_paraphrase | Mengetahui pencatatan dan kesinambungan tindak lanjut pekerjaan persiapan yang belum selesai. | WO-DOC-008/s1-r0033; WO-DOC-008/s2-r0012; WO-DOC-010/b0016 |
| WO-DEV-009 | Hujan turun menjelang tamu masuk ke taman. Apa yang perlu dipastikan sebelum kegiatan dialihkan ke ruang tertutup? | E | semantic_paraphrase | Mengetahui pemeriksaan dan kewenangan untuk pengalihan acara dari area luar ke alternatif tertutup. | WO-DOC-027/b0013; WO-DOC-027/b0016; WO-DOC-027/b0022 |
| WO-DEV-010 | Saat meninjau lokasi di tepi pantai, apa yang perlu diperiksa agar tamu dan perlengkapan bisa mencapai area acara? | F | semantic_paraphrase | Mengetahui pemeriksaan akses orang dan perlengkapan pada survei lokasi pantai. | WO-DOC-037/p001-b009; WO-DOC-037/p001-b012 |
| WO-DEV-011 | Ada orang yang menanyakan apakah seorang tamu sudah datang. Informasi apa yang boleh disampaikan petugas penerima tamu? | G | semantic_paraphrase | Mengetahui batas pengungkapan informasi kehadiran tamu kepada pihak yang bertanya. | WO-DOC-041/l0029-0029; WO-DOC-045/b0018 |
| WO-DEV-012 | Bagaimana mengubah hasil pembahasan setelah acara menjadi perbaikan yang bisa dipantau sampai selesai? | J | semantic_paraphrase | Mengetahui penyusunan tindakan perbaikan dan pemantauannya setelah evaluasi acara. | WO-DOC-049/b0018; WO-DOC-049/b0020 |
| WO-DEV-013 | Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap? | C | mixed_natural | Mengetahui kriteria kesiapan pasangan dan perpindahan ke titik standby sebelum prosesi. | WO-DOC-014/b0014; WO-DOC-014/b0015; WO-DOC-024/b0012 |
| WO-DEV-014 | Setelah foto di chapel, beberapa tamu akan naik shuttle ke lokasi dinner. Bagaimana LO memastikan tidak ada kelompok yang tertinggal? | D | mixed_natural | Mengetahui rekonsiliasi kelompok saat keberangkatan dan kedatangan transport antarlokasi. | WO-DOC-025/s1-r0018; WO-DOC-025/s1-r0025; WO-DOC-025/s1-r0026; WO-DOC-043/b0024 |
| WO-DEV-015 | Tamu yang datang melebihi daftar dan ada kursi kosong di ballroom. Apa yang perlu diperiksa sebelum menambah atau mengubah seating? | E | mixed_natural | Mengetahui pemeriksaan alokasi, kapasitas, dan layanan sebelum perubahan tempat duduk. | WO-DOC-032/b0010; WO-DOC-032/b0014; WO-DOC-032/b0017 |
| WO-DEV-016 | Seorang tamu meminta makanan khusus. Bagaimana guest desk menindaklanjuti permintaan itu dan apa batas informasi yang boleh dijanjikan? | G | mixed_natural | Mengetahui koordinasi permintaan makanan khusus dan batas kepastian informasi layanan. | WO-DOC-041/l0026-0026; WO-DOC-021/p001-b010 |
| WO-DEV-017 | Sambutan melewati durasi rencana, sementara dinner belum dimulai. Apa yang perlu dipertimbangkan untuk menyesuaikan rundown? | H | mixed_natural | Mengetahui pertimbangan penyesuaian urutan atau waktu akibat sambutan yang melampaui rencana. | WO-DOC-030/l0011-0011; WO-DOC-030/l0014-0014; WO-DOC-030/l0017-0017 |
| WO-DEV-018 | PIC pengganti akan mengambil alih di tengah acara. Apa isi handover dan bagaimana memastikan pekerjaan benar-benar sudah diterima? | I | mixed_natural | Mengetahui isi serah terima dan konfirmasi penerimaan tanggung jawab antar-PIC. | WO-DOC-047/b0008; WO-DOC-047/b0010 |

## Consistency and editorial audit

- PASS: 18 query records and 18 provenance records; contiguous IDs `WO-DEV-001` to `WO-DEV-018`; unique need, family and provenance IDs; one-to-one joins.
- PASS: all required metadata populated, 6/6/6 styles, 10 valid canonical category labels, every record has the requested draft status.
- PASS: all 42 evidence pointers resolve to nonempty operational blocks; XLSX rows retain header and source-location context.
- PASS: exact and normalized question duplicates = 0. Deterministic query-to-query Unicode word-set Jaccard, casefold, no stopword removal, threshold >=0.45 examined 153 pairs: 0 candidates. This is an editorial duplicate screen, not retrieval evaluation or proof of semantic uniqueness.
- Author editorial review found no apparent same-intent duplicate, mechanically converted document title or embedded answer. Answerability and naturalness remain unvalidated by a domain expert.
- Information needs and scenarios describe the decision/task to research; they do not supply operational response steps or target values. Evidence stays outside the query text.
- Practitioners should confirm local usage of `RACI`, `C03`, `checkout`, `standby`, `chapel` and `dinner`. C03 identifies the simulated cue in the corpus; it is not an answer. If its wording is unrealistic, revise through recorded expert review rather than retaining it merely for lexical matching.

Related families needing explicit expert confirmation:
- 004 vs 013: pre-event vendor schedule planning vs actual day-of couple readiness.
- 003 vs 013: whole entrance cue vs couple handover.
- 008 vs 018: pre-event outstanding tracking vs live PIC transfer.
- 005 vs 017: audio recovery vs schedule adjustment.
- 006 vs 012: asset checkout vs post-event corrective-action follow-up.
- 011 vs 016: attendance privacy vs food-service information.

These share contexts but request distinct decisions. Expert review can still merge/reject them; any resulting style/category imbalance must be audited again before freeze.

## Practitioner review and actual timing

CSV: 18 rows, quoted comma-separated UTF-8 with BOM; no formulas or prefilled human decisions. CSV does not preserve spreadsheet formatting or dropdown validation. Practitioner-input columns are blank, not zero or PASS. A temporary preview of the authored table was inspected separately.

1. Record reviewer ID (pseudonym permitted), WO role and actual experience. Prefer a practicing WO coordinator/PIC familiar with the tasks.
2. Read each question first for plausible need and natural language. Then inspect evidence and other operational sections as needed; record consulted IDs in `evidence_checked_refs`. Pointers do not restrict answerability checks to those sections.
3. Fill `need_plausible`, `language_natural`, `style_appropriate`, `category_appropriate` and `answer_leakage_detected` with `yes/no/uncertain`. Fill `answerability_in_corpus` with `supported/partially_supported/not_supported/uncertain`. These evaluate the question and do not grade chunk relevance.
4. Record duplicates, suggested text, rationale and `review_decision=accept/revise/reject/needs_discussion`. Acceptance in CSV does not automatically change JSONL or freeze anything. Revisions require an authorized traceable pass.
5. Record ISO-8601 start/finish timestamps with timezone, pauses in seconds, and measured `review_active_seconds` = elapsed minus pauses. Include evidence-consultation time; explain unusual delays. Leave unmeasured values blank.
6. Blank `pair_calibration_*` fields are placeholders for a later explicitly authorized manual query–chunk judgment timing exercise, not permission to start judging now. Record scope, actual inspected chunk IDs, true pair count, timestamps, pauses and total active seconds. No pairs or grades are generated in this milestone. Retain separate copies for multiple reviewers/sessions.

Question review time is not pair relevance-judgment time and must not be extrapolated as ground-truth workload. After separately authorized pair calibration, report actual seconds/pair with sample count, task complexity, median and range/percentiles. Account separately for familiarization, independent assessment and adjudication. Never invent timings. Exhaustive main assessment remains 75 x 371 = 27,825 pairs per assessor. Main judgment workflow/workload requires supervisor approval based on actual observations; no workload duration is claimed here.

Where another assessor reviews a subset independently, give a blank copy and retain reviewer-specific decisions. Resolve disagreement with documented expert/adjudicator rationale before any future query validation or freeze.

## Lexical tokenizer encoding — held for future authorization

Read-only UTF-8 inspection confirms `lexical.token_pattern` contains `â€™` (U+00E2, U+20AC, U+2122), not a single U+2019 typographic apostrophe. It is inside the token character class and can change punctuation boundaries. This is an actual stored encoding issue, not inferred from terminal display. No tokenizer was run and TOML was not changed. Before retrieval implementation, authorize an encoding correction and checks for straight/typographic apostrophes, hyphenation and Indonesian terms consistently for R1/R2.

## Integrity and checks

SHA-256 compared all 106 existing baseline project files before/after authoring, excluding environments, Git internals and bytecode caches: unchanged. All 57 source-corpus files present in the snapshot source hash map also match; there are 50 operational source documents. Snapshot artifact hashes and the aggregate fingerprint match the frozen reference.

| Protected existing file | SHA-256, unchanged | Result |
| --- | --- | --- |
| `data/source_corpus/corpus_manifest.json` | `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f` | PASS |
| `data/processed/documents.jsonl` | `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01` | PASS |
| `data/chunks/chunks.jsonl` | `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0` | PASS |
| `experiments/configs/pilot.toml` | `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26` | PASS |
| `data/validation/pilot_snapshot.json` | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` | PASS |
| `experiments/reports/benchmark_protocol_v1.md` | `e803732c957fe9a3556fb9c611bbeb3407ce022f39f969469c93fe6125fc99f3` | PASS |
| `experiments/configs/retrieval_protocol_v1.toml` | `dc0274bc64894e7e3ddf77f7bb46551a7345c6e13888db18bed8b2d53dad274a` | PASS |

Snapshot fingerprint: `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`.

Checks: standard-library TOML parse; required fields, counts, IDs and provenance assertions; reference/header validation; category cross-tab; deterministic query duplicate screen; Artifact Tool table value round-trip; final on-disk JSONL/CSV parse and allowed-file delta verification. Git metadata is absent; no Git status/diff evidence is available.

Only these four project files were created:
- `data/benchmark/development_queries_draft.jsonl`
- `data/benchmark/development_query_provenance.jsonl`
- `experiments/reports/development_query_audit.md`
- `data/validation/development_query_review_template.csv`

No model execution, corpus embedding, indexing, retrieval, qrels, main queries, performance scores, dependency installation, commit, push, PR or deployment was performed.

## Document study inventory

Scope inventory only: not a relevance judgment or assertion every document should contribute a question. Formats: 26 DOCX, 9 PDF, 10 XLSX, 5 TXT.

| Document | Title | Category | Format |
| --- | --- | --- | --- |
| WO-DOC-001 | Struktur Organisasi Lapangan dan Alur Komando Wedding Organizer | A | DOCX |
| WO-DOC-002 | Uraian Tugas Event Coordinator dan Wedding Coordinator | A | DOCX |
| WO-DOC-003 | Panduan Tanggung Jawab PIC Pengantin dan PIC Keluarga | A | DOCX |
| WO-DOC-004 | Uraian Tugas PIC Vendor dan PIC Venue | A | DOCX |
| WO-DOC-005 | Panduan Operasional Runner, Liaison Officer, dan Guest Desk | A | PDF |
| WO-DOC-006 | Matriks Pembagian Tanggung Jawab Tim Wedding Day | A | XLSX |
| WO-DOC-007 | Panduan Tahapan Persiapan Wedding H-30 hingga H-14 | B | DOCX |
| WO-DOC-008 | Checklist Final Preparation H-7 hingga H-1 | B | XLSX |
| WO-DOC-009 | Prosedur Final Confirmation dan Rekonsiliasi Kesiapan Vendor | B | DOCX |
| WO-DOC-010 | Panduan Technical Meeting dan Catatan Keputusan Pra-Acara | B | DOCX |
| WO-DOC-011 | Checklist Site Inspection, Venue Readiness, dan Sound Check | B | XLSX |
| WO-DOC-012 | Catatan Briefing Kru Menjelang Wedding Day | B | TXT |
| WO-DOC-013 | SOP Kedatangan Kru, Check-in, dan Persiapan Area Kerja | C | DOCX |
| WO-DOC-014 | Prosedur Pendampingan Persiapan Pengantin dan Keluarga Inti | C | DOCX |
| WO-DOC-015 | Panduan Floor Coordination dan Alur Prosesi Wedding Ceremony | C | PDF |
| WO-DOC-016 | Panduan Guest Reception, Registrasi, dan Pengarahan Tamu | C | DOCX |
| WO-DOC-017 | Cue Sheet Koordinasi MC, Banquet, dan Reception Flow | C | PDF |
| WO-DOC-018 | Catatan Handover dan Perubahan Situasi pada Wedding Day | C | TXT |
| WO-DOC-019 | Prosedur Penutupan Acara dan Serah Terima Area Operasional | C | DOCX |
| WO-DOC-020 | Panduan Koordinasi Vendor Dekorasi, Lighting, dan Area Setup | D | DOCX |
| WO-DOC-021 | Panduan Sinkronisasi Catering dan Banquet Service | D | PDF |
| WO-DOC-022 | Brief Operasional Photography dan Videography Wedding Day | D | DOCX |
| WO-DOC-023 | Panduan Koordinasi MC, Entertainment, dan Audio Cue | D | DOCX |
| WO-DOC-024 | Panduan Sinkronisasi Makeup Artist dan Jadwal Persiapan Pengantin | D | DOCX |
| WO-DOC-025 | Matriks Penugasan Transport, Driver, Shuttle, dan Logistik | D | XLSX |
| WO-DOC-026 | Matriks Kesiapan Vendor dan Saluran Koordinasi Operasional | D | XLSX |
| WO-DOC-027 | Prosedur Antisipasi dan Respons Hujan pada Outdoor Wedding | E | DOCX |
| WO-DOC-028 | Prosedur Penanganan Gangguan Listrik dan Koordinasi Backup Power | E | DOCX |
| WO-DOC-029 | Prosedur Penanganan Vendor Terlambat atau Tidak Hadir | E | DOCX |
| WO-DOC-030 | Panduan Penyesuaian Rundown dan Penanganan Keterlambatan Acara | E | TXT |
| WO-DOC-031 | Panduan Penanganan Masalah Sound System, Mikrofon, dan Audio Cue | E | PDF |
| WO-DOC-032 | Prosedur Penanganan Tamu Melebihi Kapasitas dan Perubahan Seating | E | DOCX |
| WO-DOC-033 | Prosedur Penanganan Barang Hilang, Vendor Property, dan Lost and Found | E | DOCX |
| WO-DOC-034 | Matriks Kategori Insiden, Prioritas Respons, dan Eskalasi | E | XLSX |
| WO-DOC-035 | Panduan Operasional Wedding pada Hotel Ballroom dan Indoor Venue | F | DOCX |
| WO-DOC-036 | Panduan Setup dan Koordinasi Operasional Garden Villa Wedding | F | PDF |
| WO-DOC-037 | Panduan Operasional Beach Wedding dan Mitigasi Kondisi Lokasi | F | PDF |
| WO-DOC-038 | Matriks Site Survey, Kelayakan Venue, dan Kebutuhan Fasilitas | F | XLSX |
| WO-DOC-039 | Panduan Pendampingan Keluarga Inti, VIP, dan Tamu Khusus | G | DOCX |
| WO-DOC-040 | Matriks Seating Allocation dan Penugasan Guest Escort | G | XLSX |
| WO-DOC-041 | FAQ Internal Guest Desk dan Penanganan Kebutuhan Tamu | G | TXT |
| WO-DOC-042 | Rundown Operasional Akad dan Resepsi Hotel Ballroom | H | XLSX |
| WO-DOC-043 | Rundown Pemberkatan, Perpindahan Venue, dan Intimate Dinner | H | DOCX |
| WO-DOC-044 | Timeline Koordinasi International Wedding dan Outdoor Reception | H | PDF |
| WO-DOC-045 | SOP Komunikasi Internal, Radio, dan Grup Koordinasi Wedding Day | I | DOCX |
| WO-DOC-046 | Panduan Singkat Jalur Eskalasi dan Hak Pengambilan Keputusan | I | TXT |
| WO-DOC-047 | Panduan Handover Antar-PIC dan Pencatatan Keputusan Lapangan | I | DOCX |
| WO-DOC-048 | Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset | J | XLSX |
| WO-DOC-049 | Panduan Debrief dan Evaluasi Operasional Setelah Wedding | J | DOCX |
| WO-DOC-050 | Laporan Penyelesaian Insiden dan Catatan Perbaikan Operasional | J | PDF |

## Next decision

Practitioner review of these drafts and actual timing observations precede validation/freeze and approval of the main ground-truth workload. Resolve protocol status/enum and tokenizer encoding only through a later authorized protocol change. Preserve development-family separation during future main-query drafting. STOP after Milestone 7A.


## Milestone 7B follow-up — historical audit retained

Laporan di atas merekam keadaan saat Milestone 7A; hash protokol dan catatan exception berlaku untuk tahap tersebut. Pada Milestone 7B, mojibake tokenizer diperbaiki menjadi U+2019, enum draft_pending_expert_review ditambahkan, dan status draft pada protokol diselaraskan. Exception enum/encoding yang dicatat di atas sudah ditangani; query tetap DRAFT, bukan validated/frozen. Teks 18 query dan provenance tidak diubah. Review terbaru, usulan wording yang belum diterapkan, audit 42 pointer, dan hasil integritas berada di development_query_review.md; workbook praktisi berada di data/validation/development_query_review.xlsx.
