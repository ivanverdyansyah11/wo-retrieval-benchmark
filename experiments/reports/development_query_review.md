# Milestone 7B — Development Query Review and Validation Preparation

Created at: 2026-10-09T00:34:36+08:00 (Asia/Singapore).
Snapshot: `WO-CORPUS-V1-DRAFT-PILOT-001`; corpus `v1-draft`, `pending_practitioner_validation`.
Query dataset: `development-v1-draft`; 18 queries remain `draft_pending_expert_review`.

## Result and scope

All 18 candidates have a defined WO operational information need and documentary support. Editorial review found 12 without a specific wording issue and 6 requiring focused clarification/jargon review. This is an AI-assisted documentary/editorial precheck, not practitioner validation, certification of operational practice, final relevance labeling, or a freeze decision. No query or provenance JSONL was rewritten. Proposed wording below is not applied.

Read all 18 query records, scenarios and information needs and all 42 referenced operational passages. Reparsed the 22 referenced original source documents read-only using existing ingestion parsers (12 DOCX, 4 PDF, 4 XLSX, 2 TXT). All 42 pointers match original source text after existing normalization, heading and exact source locator. Parser code and canonical data were not changed. This verifies traceability with the existing parser, not an independent parser-validation experiment.

## Per-query review (author analysis, not reviewer decisions)

Clear means no specific editorial defect found in this pass; it does not mean human acceptance. Needs attention means a proposed clarification, not automatic rejection. Every query retains one information need; related checks within a single procedure do not automatically create separate needs.

| Query | Existing question (unchanged) | Editorial finding | Reason / documentary limits |
| --- | --- | --- | --- |
| WO-DEV-001 | Untuk pengelolaan daftar registrasi, bagaimana pembagian peran A dan R dalam matriks RACI tim? | Clear for human review | Pembagian peran A/R terarah; definisi dan baris registrasi tersedia. Kepanjangan RACI tidak perlu diasumsikan sudah dipahami staf baru. |
| WO-DEV-002 | Pada H-1, apa yang harus diperiksa dalam final confirmation ketika kebutuhan loading vendor berbeda dari izin venue? | Clear for human review | Konflik waktu akses dijelaskan dalam source; H-1 adalah saat pemeriksaan ulang, bukan tenggat universal semua loading. |
| WO-DEV-003 | Apa saja prasyarat cue C03 entrance sebelum floor memberi aba-aba jalan? | Needs focused review | C03 adalah kode cue resepsi EVT-02 di ballroom, tetapi query belum menyebut konteks tersebut. Familiaritas kode/floor perlu dikonfirmasi. |
| WO-DEV-004 | Apa yang harus dikonfirmasi kepada makeup artist agar jadwal makeup tidak berbenturan dengan standby akad? | Clear for human review | Satu kebutuhan perencanaan layanan makeup; source memuat data vendor dan hubungan dengan jadwal standby. Tidak meminta durasi universal. |
| WO-DEV-005 | Jika mikrofon gagal saat sambutan, bagaimana alur penanganan dan pemeriksaan sebelum audio dipakai lagi? | Clear for human review | Penanganan dan pemeriksaan pemulihan merupakan satu alur gangguan mikrofon. Source membedakan koordinasi WO dari tindakan teknisi. |
| WO-DEV-006 | Saat checkout, apa yang perlu dicocokkan pada daftar aset WO sebelum barang diserahterimakan? | Needs focused review | Aset WO sudah jelas, tetapi checkout dapat dibaca sebagai checkout vendor, kru, atau venue. Perjelas objek serah terima. |
| WO-DEV-007 | Dua atasan memberi arahan yang saling bertentangan kepada kru yang sama. Apa yang sebaiknya dilakukan kru? | Clear for human review | Konflik dua instruksi merupakan satu kebutuhan kendali kerja; tidak perlu menetapkan dua jabatan tertentu untuk menjawab. |
| WO-DEV-008 | Seminggu menjelang acara, bagaimana mencatat pekerjaan yang belum tuntas agar tetap ditindaklanjuti sampai hari pelaksanaan? | Clear for human review | Satu kebutuhan pelacakan pekerjaan terbuka selama persiapan. Pointer H-1 adalah contoh akhir periode; panduan checklist mendukung pencatatan umum. Catatan keputusan D010 bersifat pendukung, bukan bukti pemantauan tujuh hari penuh. |
| WO-DEV-009 | Hujan turun menjelang tamu masuk ke taman. Apa yang perlu dipastikan sebelum kegiatan dialihkan ke ruang tertutup? | Clear for human review | Satu keputusan kesiapan pengalihan lokasi akibat hujan. Adanya ruang tertutup dalam skenario bukan bukti ruang itu telah diizinkan/siap; query justru meminta pemeriksaan. Bukti pembukaan ulang melengkapi bukti sebelum perpindahan. |
| WO-DEV-010 | Saat meninjau lokasi di tepi pantai, apa yang perlu diperiksa agar tamu dan perlengkapan bisa mencapai area acara? | Clear for human review | Akses orang dan perlengkapan merupakan satu kebutuhan survei. Source mendukung pemeriksaan akses, bukan ukuran jalur/kapasitas teknis yang tidak ditulis. |
| WO-DEV-011 | Ada orang yang menanyakan apakah seorang tamu sudah datang. Informasi apa yang boleh disampaikan petugas penerima tamu? | Clear for human review | Satu kebutuhan batas pengungkapan kehadiran. Identitas penanya tidak ditentukan; jawabability dari kebijakan umum source, bukan asumsi bahwa penanya berwenang. D045 hanya konteks privasi kanal, bukan sumber izin pemberian data. |
| WO-DEV-012 | Bagaimana mengubah hasil pembahasan setelah acara menjadi perbaikan yang bisa dipantau sampai selesai? | Clear for human review | Penyusunan dan pemantauan tindakan perbaikan merupakan satu kebutuhan tindak lanjut evaluasi. Tidak meminta kebijakan yang telah tervalidasi. |
| WO-DEV-013 | Menjelang prosesi, makeup sudah selesai tetapi pengantin belum tiba di titik standby. Apa yang harus dicek sebelum menyatakan pasangan siap? | Needs focused review | Makna siap dapat dibaca sebagai makeup selesai atau siap menjalankan prosesi. Source membedakan kesiapan persiapan, posisi standby, dan izin cue; pertanyaan perlu mempertahankan pembedaan ini. |
| WO-DEV-014 | Setelah foto di chapel, beberapa tamu akan naik shuttle ke lokasi dinner. Bagaimana LO memastikan tidak ada kelompok yang tertinggal? | Needs focused review | Tidak ada kelompok tertinggal dapat disalahartikan bahwa semua tamu wajib memakai shuttle. Source juga mengizinkan perjalanan sendiri yang dicatat. Chapel/dinner/LO perlu konfirmasi istilah praktisi. |
| WO-DEV-015 | Tamu yang datang melebihi daftar dan ada kursi kosong di ballroom. Apa yang perlu diperiksa sebelum menambah atau mengubah seating? | Needs focused review | Kalimat pembuka 'Tamu yang datang melebihi daftar dan ada...' kurang utuh. Kursi kosong perlu dibaca sebagai tampak kosong, bukan otomatis tersedia. |
| WO-DEV-016 | Seorang tamu meminta makanan khusus. Bagaimana guest desk menindaklanjuti permintaan itu dan apa batas informasi yang boleh dijanjikan? | Needs focused review | Frasa informasi yang boleh dijanjikan kurang alami. Makanan khusus sengaja umum; query tidak boleh diasumsikan meminta diagnosis atau jaminan menu tertentu. |
| WO-DEV-017 | Sambutan melewati durasi rencana, sementara dinner belum dimulai. Apa yang perlu dipertimbangkan untuk menyesuaikan rundown? | Clear for human review | Satu kebutuhan penyesuaian rundown karena sambutan berlebih; source memuat kondisi banquet, buffer dan versi berlaku, tanpa mengharuskan jam tertentu dalam query. |
| WO-DEV-018 | PIC pengganti akan mengambil alih di tengah acara. Apa isi handover dan bagaimana memastikan pekerjaan benar-benar sudah diterima? | Clear for human review | Isi handover dan pengakuan penerimaan adalah satu kebutuhan transfer kendali pekerjaan. Source mendukung keduanya dan batas saat pengganti belum siap. |

## Proposed wording — not applied

Only these six edits are suggested. The reviewer can retain, revise or reject each suggestion. No proposal is inserted into the workbook judgment column or query JSONL. Style/category assignments remain the original 6/6/6 until any authorized revision is audited.

| Query | Proposed question | Reason |
| --- | --- | --- |
| WO-DEV-003 | Menjelang entrance resepsi di ballroom, apa saja prasyarat sebelum floor memberi aba-aba jalan? | Menghapus ketergantungan kode C03 dan memperjelas fase acara; information need tetap prasyarat pelepasan entrance. Proposed only. |
| WO-DEV-006 | Saat serah terima aset WO setelah acara, apa yang perlu dicocokkan dengan daftar aset? | Mengganti istilah checkout yang luas dengan objek kegiatan tanpa menambah langkah jawaban. Proposed only. |
| WO-DEV-013 | Menjelang prosesi, makeup pasangan sudah selesai, tetapi pasangan belum tiba di titik standby. Apa yang perlu diperiksa sebelum melaporkan pasangan siap mengikuti prosesi? | Memperjelas pasangan dan tingkat kesiapan yang dilaporkan; tidak mengasumsikan makeup selesai berarti cue sudah diizinkan. Proposed only. |
| WO-DEV-014 | Setelah foto di chapel, bagaimana LO mencocokkan kelompok tamu pengguna shuttle yang berangkat dan tiba di lokasi dinner? | Membatasi pemeriksaan pada pengguna shuttle sesuai skenario beberapa tamu, dengan kebutuhan rekonsiliasi keberangkatan/kedatangan tetap sama. Proposed only. |
| WO-DEV-015 | Jumlah tamu yang datang melebihi daftar, sementara beberapa kursi di ballroom tampak kosong. Apa yang perlu diperiksa sebelum menambah atau mengubah seating? | Memperbaiki tata bahasa dan membedakan pengamatan kursi dari ketersediaan alokasi; tidak mengubah kebutuhan keputusan seating. Proposed only. |
| WO-DEV-016 | Seorang tamu meminta makanan khusus. Bagaimana guest desk menindaklanjutinya, dan sejauh mana petugas boleh memberi kepastian tentang makanan tersebut? | Memperhalus batas informasi layanan tanpa mempersempit ke jenis kebutuhan makanan atau menyisipkan jawaban. Proposed only. |

## Evidence audit: all 42 pointers

All document IDs, canonical block IDs, document titles, source paths, headings and locators match the referenced canonical records and reparsed original files. XLSX header blocks, column labels, sheet names, row ranges and header coordinates match. PDF page/block numbers follow the existing parser typography/callback rule; DOCX uses body/paragraph positions; TXT uses line ranges. No broken pointer or unsupported evidence claim was found.

40 pointers provide direct documentary support for the need or its requested component. Two are supplementary context: WO-DEV-008 / WO-DOC-010 / b0016 (decision-record fields, not proof of tracking across the entire week), and WO-DEV-011 / WO-DOC-045 / b0018 (general communication privacy, not authority to disclose attendance). These are editorial descriptions of evidence use, not chunk relevance grades.

Pointer absence means nothing about relevance of other chunks. No pointer is automatically grade 2, no missing chunk is grade 0, and no qrels or exhaustive relevant set is produced.

| Query | Document / canonical block | Heading | Source locator | Documentary use |
| --- | --- | --- | --- | --- |
| WO-DEV-001 | WO-DOC-006 / s1-r0016 | Matriks Pembagian Tanggung Jawab Tim Wedding Day / Operasional | sheet Operasional, A16:F16, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-001 | WO-DOC-006 / s2-r0011 | Panduan / Panduan | sheet Panduan, A11:B11, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-002 | WO-DOC-009 / b0014 | Menemukan selisih dan menguji dampak | body 14, paragraph 14 | Direct support for requested need/component; source match PASS |
| WO-DEV-002 | WO-DOC-009 / b0019 | Pemeriksaan ulang H-1 dan hari acara | body 19, paragraph 19 | Direct support for requested need/component; source match PASS |
| WO-DEV-003 | WO-DOC-017 / p001-b011 | C02 standby entrance pukul 17.20 | page 1, block 11 | Direct support for requested need/component; source match PASS |
| WO-DEV-003 | WO-DOC-017 / p001-b013 | C03 entrance pukul 17.30 | page 1, block 13 | Direct support for requested need/component; source match PASS |
| WO-DEV-004 | WO-DOC-024 / b0008 | Data yang dikonfirmasi sebelum H-1 | body 8, paragraph 8 | Direct support for requested need/component; source match PASS |
| WO-DEV-004 | WO-DOC-024 / b0011 | Urutan simulasi pagi EVT-02 | body 11, paragraph 11 | Direct support for requested need/component; source match PASS |
| WO-DEV-005 | WO-DOC-031 / p002-b003 | Mikrofon gagal saat sambutan | page 2, block 3 | Direct support for requested need/component; source match PASS |
| WO-DEV-005 | WO-DOC-031 / p002-b011 | Pemulihan dan penutupan insiden | page 2, block 11 | Direct support for requested need/component; source match PASS |
| WO-DEV-006 | WO-DOC-048 / s1-r0022 | Checklist Breakdown Venue, Vendor Checkout, dan Pengembalian Aset / Operasional | sheet Operasional, A22:G22, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-006 | WO-DOC-019 / b0013 | Mengembalikan barang dan aset | body 13, paragraph 13 | Direct support for requested need/component; source match PASS |
| WO-DEV-007 | WO-DOC-001 / b0020 | Ketika perintah bertentangan | body 20, paragraph 20 | Direct support for requested need/component; source match PASS |
| WO-DEV-008 | WO-DOC-008 / s1-r0033 | Checklist Final Preparation H-7 hingga H-1 / Operasional | sheet Operasional, A33:G33, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-008 | WO-DOC-008 / s2-r0012 | Panduan / Panduan | sheet Panduan, A12:B12, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-008 | WO-DOC-010 / b0016 | Menuliskan keputusan dengan benar | body 16, paragraph 16 | Supporting context; source match PASS |
| WO-DEV-009 | WO-DOC-027 / b0013 | Pemeriksaan awal dan pembatasan area | body 13, paragraph 13 | Direct support for requested need/component; source match PASS |
| WO-DEV-009 | WO-DOC-027 / b0016 | Kewenangan dan pilihan tindakan | body 16, paragraph 16 | Direct support for requested need/component; source match PASS |
| WO-DEV-009 | WO-DOC-027 / b0022 | Pemeriksaan ulang sebelum kegiatan dibuka | body 22, paragraph 22 | Direct support for requested need/component; source match PASS |
| WO-DEV-010 | WO-DOC-037 / p001-b009 | Verifikasi sebelum komitmen layout | page 1, block 9 | Direct support for requested need/component; source match PASS |
| WO-DEV-010 | WO-DOC-037 / p001-b012 | Akses orang dan barang | page 1, block 12 | Direct support for requested need/component; source match PASS |
| WO-DEV-011 | WO-DOC-041 / l0029-0029 | Apakah seseorang sudah hadir | lines 29-29: Apakah seseorang sudah hadir | Direct support for requested need/component; source match PASS |
| WO-DEV-011 | WO-DOC-045 / b0018 | Privasi pada kanal lapangan | body 18, paragraph 18 | Supporting context; source match PASS |
| WO-DEV-012 | WO-DOC-049 / b0018 | Menulis tindakan perbaikan | body 18, paragraph 18 | Direct support for requested need/component; source match PASS |
| WO-DEV-012 | WO-DOC-049 / b0020 | Menutup rapat dan memantau | body 20, paragraph 20 | Direct support for requested need/component; source match PASS |
| WO-DEV-013 | WO-DOC-014 / b0014 | Pemeriksaan siap dan handover ke floor | body 14, paragraph 14 | Direct support for requested need/component; source match PASS |
| WO-DEV-013 | WO-DOC-014 / b0015 | Pemeriksaan siap dan handover ke floor | body 15, paragraph 15 | Direct support for requested need/component; source match PASS |
| WO-DEV-013 | WO-DOC-024 / b0012 | Urutan simulasi pagi EVT-02 | body 12, paragraph 12 | Direct support for requested need/component; source match PASS |
| WO-DEV-014 | WO-DOC-025 / s1-r0018 | Matriks Penugasan Transport, Driver, Shuttle, dan Logistik / Operasional | sheet Operasional, A18:G18, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-014 | WO-DOC-025 / s1-r0025 | Matriks Penugasan Transport, Driver, Shuttle, dan Logistik / Operasional | sheet Operasional, A25:G25, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-014 | WO-DOC-025 / s1-r0026 | Matriks Penugasan Transport, Driver, Shuttle, dan Logistik / Operasional | sheet Operasional, A26:G26, header row 5 | Direct support for requested need/component; source match PASS |
| WO-DEV-014 | WO-DOC-043 / b0024 | 16.40 sampai 17.00 perpindahan 20 menit | body 24, paragraph 24 | Direct support for requested need/component; source match PASS |
| WO-DEV-015 | WO-DOC-032 / b0010 | Pemeriksaan awal | body 10, paragraph 10 | Direct support for requested need/component; source match PASS |
| WO-DEV-015 | WO-DOC-032 / b0014 | Pilihan penataan | body 14, paragraph 14 | Direct support for requested need/component; source match PASS |
| WO-DEV-015 | WO-DOC-032 / b0017 | Perubahan seating yang dapat ditelusuri | body 17, paragraph 17 | Direct support for requested need/component; source match PASS |
| WO-DEV-016 | WO-DOC-041 / l0026-0026 | Tamu meminta makanan tertentu | lines 26-26: Tamu meminta makanan tertentu | Direct support for requested need/component; source match PASS |
| WO-DEV-016 | WO-DOC-021 / p001-b010 | Menetapkan dasar layanan | page 1, block 10 | Direct support for requested need/component; source match PASS |
| WO-DEV-017 | WO-DOC-030 / l0011-0011 | Sebelum memilih tindakan | lines 11-11: Sebelum memilih tindakan | Direct support for requested need/component; source match PASS |
| WO-DEV-017 | WO-DOC-030 / l0014-0014 | Pilihan berurutan | lines 14-14: Pilihan berurutan | Direct support for requested need/component; source match PASS |
| WO-DEV-017 | WO-DOC-030 / l0017-0017 | Contoh EVT-02 | lines 17-17: Contoh EVT-02 | Direct support for requested need/component; source match PASS |
| WO-DEV-018 | WO-DOC-047 / b0008 | Isi paket serah terima | body 8, paragraph 8 | Direct support for requested need/component; source match PASS |
| WO-DEV-018 | WO-DOC-047 / b0010 | Urutan pemberi dan penerima | body 10, paragraph 10 | Direct support for requested need/component; source match PASS |

## Topic/style balance and potential redundancy

| Category | Lexical-oriented | Semantic/paraphrase | Mixed/natural | Total |
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

All 10 categories are represented; E has 3, F/H/I have 1 each, and A/B/C/D/G/J have 2 each. Counts describe development coverage, not empirical WO demand frequencies. Lexical/semantic/mixed labels describe wording; they do not predict superiority of BM25, Dense, or Hybrid.

Exact/normalized duplicate questions: 0. Unicode word-set Jaccard (casefold, no stopword removal), candidate threshold >=0.45, all 153 query pairs: 0 candidates. This deterministic lexical screen cannot rule out semantic duplicates. Author-level intent review found no same-need pair; practitioners must confirm these neighboring families:

- 004/013: pre-event makeup vendor planning versus actual day-of couple readiness.
- 003/013: whole entrance cue readiness versus couple-specific handover.
- 008/018: preparation outstanding tracking versus live PIC takeover.
- 005/017: microphone recovery versus timeline adjustment during a speech.
- 006/012: asset return verification versus post-event corrective-action follow-up.
- 011/016: attendance privacy versus food-service information boundaries.

No query requires invented numerical thresholds, capacities, response durations or event facts to locate documentary support. Source times/capacities are simulated, not universal instructions. Queries 003/014 are especially scenario-specific; 013 distinguishes readiness stages; 015 distinguishes an apparently empty seat from confirmed availability. The rewrite proposals address those scopes without claiming a final answer.

## Human-review workbook

`data/validation/development_query_review.xlsx` contains three sheets:

- Review: all 18 original questions and metadata. Required judgment columns F–P are blank (198 cells), including reviewer_decision, suggested_rewording, yes/no assessments, notes, actual duration, reviewer identity, reviewed_at and validation_status. Q separately preserves current_draft_status; it is not a completed review.
- Panduan: Indonesian instructions, decision/yes-no meanings, timing method, independent-review guidance and research limits.
- Evidence: 42 rows with verbatim canonical/source passages, block IDs, headings, source locators, original file paths and XLSX header context. No generated answers or grade columns.

Filterable tables and C2 freeze panes retain identifiers/header while scrolling; yellow cells identify human inputs. Reviewer decision dropdowns permit accept/revise/reject/needs_discussion; yes/no fields also allow uncertain. Validation-status input offers pending or expert_reviewed; frozen is not offered. No formulas or automatic status transitions exist. All human inputs remain empty.

Practitioners should judge plausibility and wording first, then consult evidence for answerability. Use a traceable real/pseudonymous reviewer ID and actual timestamp; record only measured active review seconds including evidence consultation and excluding pauses. No person, review date, decision, score or duration has been invented. Multiple reviewers should use separate initially blank copies. Agreement/adjudication is future human work, not computed now.

Query review duration is not query–chunk judgment duration. Do not extrapolate it to the 27,825 pairs of 75 x 371. Obtain separately authorized manual pair-timing calibration before choosing main qrels workload with the supervisor. A workbook acceptance does not rewrite JSONL, validate the corpus, freeze queries or authorize retrieval.

## Minimal protocol corrections

The intended existing policy was verified in both Markdown and TOML: serialization normalization (NFC and line endings), casefold, U+2019 to ASCII apostrophe, then Unicode word matching. Numbers, underscores, single-character tokens and internal ASCII hyphens/apostrophes are retained. No stemming, stopwords or accent stripping.

- Confirmed stored mojibake U+00E2/U+20AC/U+2122 was replaced with U+2019 in `(?u)\b\w+(?:[-'’]\w+)*\b`. U+2019 in the class is redundant after apostrophe normalization but preserves the intended representation with the smallest correction. En/em dash, euro and trademark symbols are not connectors.
- Added draft_pending_expert_review to the status enum; both draft states are explicitly not validated or frozen. expert_reviewed requires documented human sign-off; frozen requires a separate freeze decision.
- Updated descriptive queries.status to DEVELOPMENT_DRAFTS_PENDING_EXPERT_REVIEW_MAIN_NOT_CREATED. This records existing drafts; implementation_authorized and main_evaluation_authorized remain false.
- Aligned Markdown status text and lexical policy, refreshed TOML SHA binding, and added a 7B historical note. Prior Milestone 6 validation counts remain historical. The Milestone 7A audit has a follow-up note rather than rewriting historical results.
- Verified that every other TOML table/value remains identical, including all R1–R6 parameters, serialization, RRF candidate policy, split budgets, qrels workflow, evaluation metrics and authorization gates.

## Tests and integrity

PASS: five standard-library unit tests in tests/test_protocol_config.py, run with `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_protocol_config.py -v`. These validate the declared regex/normalization examples only, not a retrieval implementation. Fixtures cover straight/curly apostrophes, ASCII hyphen versus en/em dash, digits/underscore/single tokens, euro/trademark punctuation, repeated terms, NFC accents and whitespace. Also checked enum semantics, existing draft statuses and Markdown/TOML SHA binding.

PASS: all 42 original-source/canonical/provenance matches, workbook saved-file readback, exact copying of 18 query texts, 198 blank judgment cells, 42 evidence rows, four validation rules, no workbook formulas and C2 freeze panes. Temporary previews of all sheets and judgment region were visually inspected. Excel itself was not launched; native Excel interaction is not claimed.

PASS: SHA-256 snapshot integrity and deterministic aggregate fingerprint. All 57 source-corpus files in the snapshot hash map, including the 50 operational source files, remain identical. Canonical documents, chunks, pilot configuration and snapshot JSON remain identical. Draft query/provenance JSONL and prior CSV review template are unchanged.

| Protected artifact | SHA-256 unchanged |
| --- | --- |
| `data/source_corpus/corpus_manifest.json` | `3bc162662521b44e2d8abd06d75729a5e19abba535eb6e2c8bcbb3c5f80cd44f` |
| `data/processed/documents.jsonl` | `314a1e44a769aad9b6e64c1fb2ef42bc04a722b38e8e87589de7e3fb3a046e01` |
| `data/chunks/chunks.jsonl` | `2663e23db9e2c9bd15aa75be1bd7931bb0482079cdd6183c2e1065011b10a6a0` |
| `experiments/configs/pilot.toml` | `958508999a7285dc7e0caf65a6b3b55106bdcc4d8791e6e665529f0f84812a26` |
| `data/validation/pilot_snapshot.json` | `279157bab95e3c899091ea7576e6388829823635f1bb158a5ff2a1e72ebd9a4e` |
| `data/benchmark/development_queries_draft.jsonl` | `27394ff5e4e1d66ebb562c05a67cd5e4e9d37c68479bdc6039fb6040d7281b95` |
| `data/benchmark/development_query_provenance.jsonl` | `a880b60972e64c559e7dbe61e6b446a6d258914182e35c22e5c2520f62d05d59` |

Snapshot aggregate fingerprint: `7a7a832fe52e8fae87f1d5697c359437b3b28347ba8decd8c6f1bd141990dc40`.

Before/after repository audit: 110 baseline existing project files excluding environments/Git/bytecode caches. Only the three authorized documentation/protocol files changed; the other 107 retain their original SHA-256. Three files were added. Existing ingestion/ML environments were not installed into or configured; no model/runtime package was imported for this audit. Git metadata is absent; no Git diff/status tracking is available.

Created:

- experiments/reports/development_query_review.md
- data/validation/development_query_review.xlsx
- tests/test_protocol_config.py

Modified:

- experiments/configs/retrieval_protocol_v1.toml
- experiments/reports/benchmark_protocol_v1.md
- experiments/reports/development_query_audit.md

## Limits and next milestone

The 18 queries derive from a small, researcher-composed synthetic corpus, not a measured sample of staff requests. Source vocabulary, event scenarios and supplied pointers may anchor assessment; styles are author annotations, and semantic-family separation is not established by a word-overlap screen. Source policies themselves remain pending practitioner validation. Documentary answerability does not certify correct real-world operating procedure or completeness of all relevant chunks.

The package is ready for human review preparation, not a validated/frozen dataset. Recommended next milestone: practitioner review of all 18 needs/questions with actual timing, independent review where available, and documented resolution of ambiguity/wording proposals. Apply only approved revisions in a separately authorized versioned pass; audit style/category/family distribution again. Supervisor approval and separate pair-judgment timing calibration precede main ground-truth workload. Do not begin main query generation, qrels or retrieval on the strength of this precheck alone.

No BGE-M3/PyTorch/CUDA execution, indexing, benchmark, query-performance evaluation, automatic qrels, main query generation, LLM answers, dependency installation, commit, push, PR or deploy occurred. STOP after Milestone 7B.
