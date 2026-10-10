# Milestone 9A.15 — Second AI assessor agreement audit & supervisor review readiness

**MILESTONE 9A.15 — INTER-ASSESSOR PILOT AUDITED, READY FOR SUPERVISOR REVIEW**

Audit selesai pada 9 Oktober 2026. **AI SILVER — PROVISIONAL; belum human/expert validated.** Ready for supervisor review berarti artefak dan batas klaim siap ditelaah, bukan persetujuan pembimbing, qrels accepted, atau evaluasi efektivitas selesai. Tidak ada grade final/adjudikasi baru pada milestone ini.

## 1. Hasil yang direkomputasi

Seluruh 30 output kedua berhasil dicocokkan melalui private alias mapping ke pilot original dan first-pass. Angka awal pengguna terkonfirmasi dari script dan file repository, bukan diterima sebagai input perhitungan.

| Ukuran | Hasil | Denominator / makna |
|---|---:|---|
| Exact grade agreement, seluruh pilot | 26/30 = 86,67% | Semua 30 pasangan; keputusan null tidak dihitung sebagai kesamaan grade resolved |
| Exact grade agreement, both-resolved | 26/29 = 89,66% | Hanya kedua assessor berstatus RESOLVED |
| Cohen's kappa tanpa bobot | 0,8364661654 | 29 common-resolved; nominal grade 0/1/2 |
| Cohen's kappa berbobot linear | 0,8655332303 | 29 common-resolved; keluaran script existing |
| Perbedaan grade resolved | 3 | Seluruhnya first 0 → second 1; jarak 1 |
| Perbedaan status | 1 | First UNRESOLVED/null → second RESOLVED/1 |
| Kandidat adjudikasi | 4 | Tiga konflik grade dan satu konflik status; tidak digabung otomatis |

Kappa adalah statistik deskriptif consistency antar-AI pada pilot purposive kecil. Tidak menjadi estimasi akurasi terhadap praktik WO, bukti penilai kedua lebih benar, atau bukti independensi ilmiah. Tidak dihitung confidence interval, p-value, maupun significance. Pair dalam query yang sama saling bergantung; subset common-resolved juga dipengaruhi keputusan uncertainty.

## 2. Audit input, binding, evidence, dan provenance

Kontrak CLI dibaca dari `scripts/audit_pilot_assessments.py` dan diverifikasi dengan `--help`: positional action `prepare|compare`; compare wajib memakai `--second` dan `--out`. Action prepare tidak dijalankan. Command aktual:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
.\.venv\Scripts\python.exe -B scripts/audit_pilot_assessments.py --help
.\.venv\Scripts\python.exe -B scripts/audit_pilot_assessments.py compare --second 'D:/Project/wo-retrieval-benchmark/pilot_second_assessments.jsonl' --out 'experiments/results/milestone_9a15_second_assessor_agreement_audit'
.\.venv\Scripts\python.exe -B scripts/audit_second_assessor_agreement.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_pilot_assessment_audit.py -v
```

Script supplemental bersifat additive. Ia membaca hasil compare, menggunakan validator/preflight existing, memeriksa seluruh binding tambahan, menghitung kappa nominal dengan rational arithmetic, mengekspor ledger review dan contoh Top-10 dari ranking tersimpan. Tidak memanggil retriever, encoder, model, atau evaluator efektivitas. Target supplemental yang sudah ada ditolak; untuk reproduksi gunakan salinan checkout dengan direktori hasil baru dan sesuaikan target tetap supplemental secara eksplisit. Jangan menghapus atau menimpa hasil tersegel untuk rerun.

| Pemeriksaan seluruh input/output | Hasil |
|---|---|
| Tepat 30 assessment IDs unik, tanpa missing/extra/duplicate | PASS |
| Round-trip assessment/query/chunk aliases ke original IDs | PASS 30/30 |
| Mapping direkonstruksi dengan algoritme/seed 14042 existing | PASS; urutan second input identik dengan paket |
| Semua field binding second tetap exact, termasuk query/chunk text dan SHA-256 | PASS 30/30 |
| Original query, frozen chunk serialization, document/snapshot bindings first | PASS melalui preflight existing |
| Snapshot V2 fingerprint dan hashes sumber/artefak | PASS |
| ZIP allowlist dua entries, CRC, file bytes, embedded original rubric bytes | PASS |
| Grade integer 0/1/2; null UNRESOLVED; rationale nonempty | PASS |
| Evidence substring exact serialized chunk | PASS pada semua 30 output kedua; first juga lulus validator |
| Uncertainty reason null untuk second RESOLVED; alasan untuk first UNRESOLVED | PASS; null tidak menggantikan unknown dengan 0 |
| Provenance tersedia dan disclosure sesuai schema | PASS 30/30; bukan verifikasi independen identitas provider |
| Model/revision/session aktual dan sampling terverifikasi independen | NOT AVAILABLE / not_exposed |
| Validitas substantif terhadap praktik WO | NOT ESTABLISHED; perlu penilai manusia/praktisi |

Snapshot tetap `WO-CORPUS-V2-AI-CORRECTED-PILOT-001`, fingerprint `78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6`.

| Artefak input | SHA-256 |
|---|---|
| Original pilot30 | `1e48ff74a12218746094357e298ceb65afdad40d608f408ed51eba7ab6c2f546` |
| First-pass assessments | `398031a6e92eccf26a582038851cfa05d4f7e43021a7589256e6d25cd0f259a6` |
| Original second blind input | `e7fc424f7e2ec0759ab61b9b349d0774827ec6f73f1fea81f9db3e067818ff4e` |
| Second assessments | `9f19cd6033258dc290337ece685a0f4fd7d3025cb0052b4a31bf907e11abf66d` |
| Private alias mapping | `8c36ba5feb4e36031152db763090fddb4b7b26ef23cd1159f5cc5a9c89fd1589` |
| Second prompt | `4c5c1cbcedf017087df63eb40e130a0dac70805bb9b41ea6ed69382ed00683dd` |

Complete hashes dan provenance disimpan dalam `second_input_qc.json`. Hash mengikat bytes yang diaudit, tidak membuktikan label benar.

## 3. Distribusi dan UNRESOLVED handling

| Keputusan | First | Second |
|---|---:|---:|
| Grade 0 | 13 | 10 |
| Grade 1 | 11 | 15 |
| Grade 2 | 5 | 5 |
| UNRESOLVED/null | 1 | 0 |
| Total | 30 | 30 |

Confusion matrix berikut hanya common-resolved: rows first, columns second, n=29.

| First \ Second | 0 | 1 | 2 | Total |
|---|---:|---:|---:|---:|
| 0 | 10 | 3 | 0 | 13 |
| 1 | 0 | 11 | 0 | 11 |
| 2 | 0 | 0 | 5 | 5 |
| Total | 10 | 14 | 5 | 29 |

Accounting di luar matrix: first UNRESOLVED → second Grade 1 = 1; kedua UNRESOLVED = 0; hanya second UNRESOLVED = 0. Karena itu marginal second Grade 1 dalam matrix adalah 14, berbeda dari distribusi seluruh pilot 15. UNRESOLVED tetap null pada assessment original; tidak diberi distance ordinal, tidak dimasukkan ke kappa, dan tetap masuk ledger. Tidak dihitung sebagai grade 0, tidak dibuang diam-diam.

Untuk kappa tanpa bobot: observed `Po=26/29`; expected `Pe=(13×10 + 11×14 + 5×5)/29² = 309/841`; `κ=(Po−Pe)/(1−Pe)=445/532=0,8364661654`. Script existing menggunakan linear distance `|left−right|` dan menghasilkan 0,8655332303. Kedua definisi dilaporkan terpisah; angka tanpa bobot tidak diatribusikan sebagai keluaran existing CLI.

Mean second-minus-first pada 29 resolved = 3/29 = 0,103448. Ini menunjukkan arah tiga disagreement yang teramati, bukan calibration score atau kecenderungan yang dapat digeneralisasi ke seluruh corpus.

## 4. Disagreement by query style

| Style | Pairs | Both resolved | Exact/all | Exact/both resolved | Konflik grade | Konflik status | κ tanpa bobot | κ linear |
|---|---:|---:|---|---|---:|---:|---:|---:|
| lexical_oriented | 10 | 9 | 8/10 = 80% | 8/9 = 88,89% | 1 | 1 | 0,780488 | 0,780488 |
| semantic_paraphrase | 10 | 10 | 8/10 = 80% | 8/10 = 80% | 2 | 0 | 0,687500 | 0,761905 |
| mixed_natural | 10 | 10 | 10/10 = 100% | 10/10 = 100% | 0 | 0 | 1,000000 | 1,000000 |

Strata berisi 10 pairs, bukan 10 queries independen. Pilot mencakup 18 development queries. Angka mixed 100% tidak membuktikan kebenaran labels atau keunggulan pada mixed queries. Tidak dilakukan pengujian beda antar-style. Matrix tiap style tersedia dalam `comparison.json`; kappa tanpa bobot tiap style dalam `agreement_statistics.json`.

## 5. Audit substantif keempat disagreement

Penelaahan membaca query dan seluruh serialized chunk original, bukan hanya evidence excerpt atau judul. Tidak mengubah keputusan kedua assessor atau menambah jawaban dari chunk lain. Semua kasus berstatus **PENDING_HUMAN_EXPERT_REVIEW**, grade adjudikasi null.

### WO-POOL-V2-0003 / PILOT2-001

Query `WO-DEV-001` meminta pembagian A dan R dalam RACI pengelolaan daftar registrasi. Chunk `WO-DOC-001-C004` menjelaskan jalur kerja antarfungsi. First 0; second 1.

> Guest desk melaporkan jumlah datang serta masalah seating kepada PIC keluarga dan EC sesuai dampaknya.

First menolak kontribusinya karena hubungan pelaporan tidak menetapkan A/R; second menganggap sebagian alur peran berguna sambil tetap mengakui A/R tidak dapat dipetakan. Keduanya sepakat tidak ada penugasan A/R eksplisit. Sengketa terletak pada ambang useful support versus konteks operasional saja. Adjudikator perlu memutuskan manfaat konkret bagi kebutuhan pembagian mandat, tanpa menyamakan penerima laporan dengan A atau pelapor dengan R.

### WO-POOL-V2-0107 / PILOT2-004

Query `WO-DEV-003` meminta prasyarat cue C03 entrance. Chunk `WO-DOC-047-C004` adalah handover EVT-01 ketika pindah akibat hujan. First UNRESOLVED/null; second 1.

> PIC venue menyerahkan status area tertutup serta rute kepada floor setelah pengelola menilai. PIC vendor menyerahkan kesiapan dekor esensial, catering, dan AV setelah pemeriksaan ulang.

Chunk tidak menyebut C03; first quote tentang cue pengganti juga tidak memetakan kodenya. First membutuhkan mapping untuk mempertanggungjawabkan grade; second menilai status area/rute/vendor sebagai dukungan umum. Tidak boleh menganggap pembukaan area, cue pengganti, dan cue C03 identik. Pertanyaan adjudikasi: apakah kebutuhan spesifik cukup jelas untuk menilai dukungan umum, atau konteks hilang mengharuskan unresolved? Jika konteks sumber kelak diperlukan, pengelola memberikan materi tanpa labels/ranks, dengan locator/hash/excerpt serta alasan dibuka. Grade tetap mengenai kontribusi chunk ini, bukan jawaban yang hanya ditemukan dalam materi tambahan. Konteks tersebut tidak dibuka pada audit ini.

### WO-POOL-V2-0246 / PILOT2-013

Query `WO-DEV-008` meminta pencatatan pekerjaan belum tuntas pada H-7 dan tindak lanjut sampai hari acara. Chunk `WO-DOC-007-C004` membahas H-20 hingga H-17. First 0; second 1.

> Keputusan yang menyangkut biaya tambahan dibawa WC kepada client bersama opsi, batas waktu, dan dampak jika tidak disetujui.

First menilai tidak ada pencatatan/follow-up outstanding yang dicari. Second mengambil dukungan terbatas dari koordinasi WC, opsi, tenggat, dan dampak keputusan biaya. Pernyataan ini bukan ledger seluruh outstanding atau mekanisme pemantauan H-7. Adjudikator perlu menilai apakah aspek batas waktu tetap membantu secara substantif meski tahap dan cakupan berbeda, tanpa mengarang kolom log, cadence, atau bukti penyelesaian.

### WO-POOL-V2-0325 / PILOT2-017

Query `WO-DEV-010` meminta pemeriksaan akses tamu dan perlengkapan saat meninjau lokasi pantai. Chunk `WO-DOC-009-C001` membahas final confirmation vendor. First 0; second 1.

> Ia membandingkan lingkup, kuantitas, jam kedatangan, jam selesai setup, area kerja, kebutuhan fasilitas, dan PIC pengganti.

First menilai area/fasilitas umum tidak menjawab inspeksi rute dan kondisi akses. Second menganggap area, fasilitas dan waktu berguna bagi kesiapan perlengkapan. Tidak ada pemeriksaan jalur tamu atau akses pantai dalam teks. Pertanyaan adjudikasi adalah manfaat langsung dukungan tersebut, tanpa menambahkan kondisi permukaan, kendaraan, pasang-surut, atau izin pantai yang tidak tertulis.

### Agreement tidak meniadakan kasus borderline

Empat flags pada audit 9A.14 tetap relevan: WO-POOL-V2-0107 kini disagreement; WO-POOL-V2-0438, WO-POOL-V2-0526, dan WO-POOL-V2-0163 sama-sama mendapat Grade 1 tetapi masih menyangkut konteks pergantian koordinator versus kesiapan pasangan, penutupan seating versus pemeriksaan sebelum perubahan, dan readiness umum versus pemulihan mikrofon. Consensus AI bukan alasan menghapus kebutuhan review kasus-kasus ini. Pilot manusia sebaiknya meliputi seluruh 30, bukan hanya empat konflik, untuk mendeteksi shared errors.

## 6. Isolation dan batas provenance

First mencatat `NOT_FULLY_BLIND_PRIOR_CONTEXT_EXPOSED` serta `human_validated=false`. Second mencatat akses workspace dan generic workspace context; sesi kedua tidak memenuhi isolasi repository/fresh-session penuh yang diminta paket. Disclosure second menyatakan selama grading hanya isi dua file paket dipakai, tanpa membuka ranking, skor, labels sebelumnya atau sumber substantif luar. Itu disclosure assessor, bukan bukti audit logging independen mengenai seluruh exposure.

Kedua file memakai model_id/model_revision/session_id `not_exposed`. Timestamp tercatat first `2026-10-09T11:52:54.587955+00:00`, second `2026-10-09T12:32:44Z`; schema UTC valid, tetapi keunikan sesi, model aktual, revision, dan sampling tidak dapat diverifikasi dari nilai tersebut. Tidak mengklaim model berbeda atau independensi keluarga model. Tidak ada human/expert validation pada keduanya. Membuka mapping/rankings pada tahap audit ini dilakukan setelah hasil kedua telah dibuat dan SHA-256 tetap sama; tidak merevisi assessment kedua.

Status historical NOT RUN/PENDING dalam manifest/laporan 9A.13/14 dipertahankan sebagai catatan waktu pembuatan. Milestone ini menambahkan hasil comparison tersendiri, tanpa menulis ulang sejarah atau qrels. Conflict old-silver WO-POOL-V2-0514 (old1 vs first2) juga tetap terbuka; first dan second sama-sama 2 tidak otomatis menghapus konflik terhadap old qrel.

## 7. Ringkasan akademik implementasi dan pilot retrieval

Repository menyediakan empat metode dengan input serialized chunk identik pada frozen V2, 50 dokumen dan 371 chunks. Konfigurasi di bawah diverifikasi terhadap run manifest existing; tidak diubah.

| Metode | Implementasi pilot yang tersedia |
|---|---|
| R1 | TF-IDF unigram, smoothed IDF, L2, exact cosine |
| R2 | BM25Okapi, k1=1.5, b=0.75, epsilon=0.25 |
| R3 | BGE-M3 Dense, exact cosine terhadap full corpus vectors dan query cache existing |
| R4 | BM25 + BGE-M3 Dense melalui RRF, k=60, weights 1/1; komponen shared R2/R3 |

BGE-M3 revision `5617a9f61b028005a4858fdac845db406aefb181`, dimension 1024, max_length 640. Encoding corpus/query pernah dilakukan di Colab; audit ini tidak melakukan encoding, local live GPU inference, indeks baru atau scoring ulang. Implementasi/reproducibility artefak tidak membuktikan metode paling efektif atau kebenaran praktik WO.

Saved pilot memiliki **18 development queries × 4 metode = 72 ranking**, serta **720 Top-10 rows**. Semua output 9A.12 dicocokkan SHA-256 terhadap run manifest; jumlah ranking, query/method combinations, qrels dan coverage direkomputasi lewat pembacaan file tersimpan. Tabel lengkap seluruh query ada pada [Top-10 9A.12](../results/milestone_9a12_development_pilot/top10.md).

Contoh actual Top-10 `WO-DEV-006`: “Saat checkout, apa yang perlu dicocokkan pada daftar aset WO sebelum barang diserahterimakan?” Sel berikut memuat chunk IDs; skor metode berbeda tidak dibandingkan secara numerik. Ekspor CSV tersedia sebagai `supervisor_top10_example.csv`.

| Rank | R1 | R2 | R3 | R4 |
|---:|---|---|---|---|
| 1 | WO-DOC-033-C003 | WO-DOC-033-C003 | WO-DOC-019-C004 | WO-DOC-019-C004 |
| 2 | WO-DOC-019-C004 | WO-DOC-048-C003 | WO-DOC-048-C004 | WO-DOC-048-C003 |
| 3 | WO-DOC-048-C003 | WO-DOC-019-C004 | WO-DOC-048-C006 | WO-DOC-048-C004 |
| 4 | WO-DOC-033-C001 | WO-DOC-022-C006 | WO-DOC-048-C001 | WO-DOC-022-C006 |
| 5 | WO-DOC-022-C006 | WO-DOC-034-C005 | WO-DOC-048-C003 | WO-DOC-033-C005 |
| 6 | WO-DOC-033-C005 | WO-DOC-043-C016 | WO-DOC-048-C005 | WO-DOC-033-C003 |
| 7 | WO-DOC-010-C003 | WO-DOC-028-C002 | WO-DOC-048-C002 | WO-DOC-048-C006 |
| 8 | WO-DOC-043-C016 | WO-DOC-048-C004 | WO-DOC-019-C006 | WO-DOC-048-C001 |
| 9 | WO-DOC-014-C002 | WO-DOC-010-C003 | WO-DOC-033-C005 | WO-DOC-004-C005 |
| 10 | WO-DOC-028-C002 | WO-DOC-047-C006 | WO-DOC-011-C002 | WO-DOC-011-C002 |

WO-DOC-019-C004 berjudul “Mengembalikan barang dan aset” dan memuat: “Setiap aset dicocokkan dengan daftar pinjam: kode, jumlah, kondisi awal yang diketahui, pemegang terakhir, dan penerima.” Ranking chunk tersebut R1=2, R2=3, R3=1, R4=1. WO-DOC-033-C003 membahas pemeriksaan awal barang hilang. Contoh ini menunjukkan urutan hasil dan isi tersimpan; bukan judgment tambahan, bukti superiority umum, atau hasil efektivitas final.

### Keterbatasan qrels

Qrels V2 tetap **684/6.678 pairs**, Grade 0/1/2 = **621/32/31**, sehingga **5.994 pairs UNJUDGED**. Grade 0 termasuk judged; absent label tetap unknown. Corpus AI-corrected/sintetis dan development queries AI-assisted belum expert validated. Penggunaan chunk overlap serta clustering query juga membatasi klaim generalisasi.

| Metode | Judged Top-10 | UNJUDGED Top-10 | UNJUDGED % |
|---|---:|---:|---:|
| R1 | 39/180 | 141/180 | 78,33% |
| R2 | 31/180 | 149/180 | 82,78% |
| R3 | 44/180 | 136/180 | 75,56% |
| R4 | 41/180 | 139/180 | 77,22% |

Union Top-20 stored R1–R4 kembali dihitung **654 unique pairs**, **90 existing judged**, **564 UNJUDGED**. Kedua assessments baru hanya 30 pasangan pilot; tidak membuat sisa 624 assessed dan tidak menambah qrels accepted. Coverage administratif berbeda antar-metode, sehingga metrik terhadap pool kecil rawan mengukur ketersediaan judgment, bukan efektivitas. Tidak menghitung nDCG/MRR/Recall/Precision/MAP final atau menetapkan metode terbaik. Tidak memperlakukan UNJUDGED sebagai 0.

## 8. Rekomendasi pengumpulan relevance judgments untuk evaluasi utama

Bagian ini adalah usulan untuk keputusan pembimbing, bukan pekerjaan yang sudah dijalankan. Pooling multi-system dan assessor manusia merupakan praktik test collection yang dijelaskan [NIST How to TREC](https://trec.nist.gov/howto.html). Pemisahan development dan test untuk mencegah bias tuning dijelaskan [Manning, Raghavan & Schütze, Information Retrieval System Evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/information-retrieval-system-evaluation-1.html). Penggabungan shallow pool dengan sampel tambahan mempunyai contoh penelitian [NIST, Pooled and Sampled Relevance Judgments](https://www.nist.gov/publications/comparison-pooled-and-sampled-relevance-judgments-trec-2006-terabyte-track). Angka operasional usulan berikut berasal dari desain repository, bukan kewajiban universal dari sumber tersebut.

1. **Pilot manusia sebelum ekspansi.** Rekrut praktisi WO yang pengalaman/perannya dicatat dan reviewer qualified kedua. Keduanya menilai seluruh 30 secara independen, dari query + exact chunk dengan method/rank/score/AI grade/rationale disembunyikan. Kalibrasi rubric pada contoh terpisah sebelum sealed pilot, terutama batas Grade 1/0, perbedaan tahap kerja, mandat peran dan konteks cue. Simpan judgment manusia terpisah dari dua file AI. Seluruh konflik, unresolved, dan consensus borderline ditelaah; agreement manusia dihitung sebelum adjudikasi. Jika rubric diubah, beri versi baru dan lakukan re-assessment transparan, bukan overwrite.

2. **Pisahkan validitas corpus dari relevansi.** Praktisi menelaah isi WO, batas kewenangan, skenario, answerability dan kebutuhan informasi. Relevance terhadap teks tidak otomatis membuktikan praktik WO benar. Bila corpus berubah, buat snapshot/query/qrels/index versions baru dan audit ulang binding. Jangan mengangkat AI correction atau persetujuan informal menjadi expert provenance.

3. **Development dan evaluation queries dipisah menurut information_need_family.** Tetapkan 18 query ini sebagai development; main 75 (25/style) masih desain yang memerlukan review. Penulis/praktisi membuat kebutuhan realistis dan validasi answerability sebelum ranking, dengan pemeriksaan exact/normalized serta overlap semantik intent/paraphrase. Jangan memindahkan paraphrase kebutuhan yang sama ke split berbeda. Seal main queries, family IDs, corpus dan protocol sebelum hasil main; jangan memakai main results untuk tuning atau perubahan rubric yang menguntungkan metode. Tidak membuat main queries pada audit ini.

4. **Pilihan kuat: exhaustive manusia.** Untuk 75 queries × 371 chunks diperlukan 27.825 primary decisions; double assessment penuh 55.650 actions sebelum adjudikasi/kalibrasi. Exhaustive development18 membutuhkan 6.678 pairs. Ini jumlah pasangan/actions, bukan estimasi waktu terukur; pilih setelah pilot workload nyata dan persetujuan pembimbing.

5. **Pilihan realistis sesuai desain existing: human hybrid.** Primary praktisi menilai union Top-20 R1–R4 plus 10 outside-pool samples per main query, terstratifikasi kategori dan dipilih sebelum labels (seed/inclusion probabilities dicatat). Sepuluh main queries dipilih dan di-hash sebelum ranking, satu per kategori dengan style allocation 4/3/3, untuk exhaustive 371 chunks. Secondary menilai seluruh exhaustive-audit pairs dan 20% per pooled query yang dipilih sebelum labels. Upper planning bound existing: primary 9.560, secondary 4.880, total 14.440 actions; overlap pool dapat menurunkan jumlah, expert additions dan adjudikasi menambahnya. Jangan mengklaim workload ini sudah terjadi atau cukup universal. Semua selected pairs memperoleh primary judgment manusia; existing AI qrels tidak menggantikan pekerjaan manusia. Semua metode Top-10 harus judged sebelum scope tersebut dibekukan.

6. **Adjudikasi dan provenance.** Simpan keputusan dua penilai, evidence/locator, rationale, timestamp aktual, qualifications, context opened/hash, strata/probability, rubric/qrels versions dan independence disclosure. Praktisi/third expert menyelesaikan setiap double-judged disagreement serta ambiguity dengan alasan tertulis; final outcome memakai ledger terpisah. Unknown tetap unknown sampai diputuskan; tidak ada voting AI atau overwrite old qrels. Ledger pada milestone ini adalah bahan review internal, jangan diberikan ke assessor manusia sebelum independent grading karena mengandung kedua AI labels.

7. **Freeze dan scope klaim.** Bedakan pooled main scope dari 10-query exhaustive subset. Pool coverage 100% Top-10 tidak membuktikan seluruh relevant set ditemukan; outside-pool yield dan pooled-vs-exhaustive sensitivity dilaporkan. Recall dengan complete denominator hanya layak pada scope exhaustive yang sudah lengkap, bukan seluruh 75 secara otomatis. Kebijakan UNJUDGED/UNRESOLVED, no-answer, gain scale, primary metrics dan paired analysis ditetapkan sebelum evaluasi bersama pembimbing. Bila unknown pada Top-10 belum selesai, blok freeze/evaluasi scope itu. AI pilot agreement tidak membuka gate evaluasi utama.

Jika anggaran hanya memungkinkan satu praktisi, catat single-assessor limitation dan cari independent second review untuk subset yang dipilih sebelumnya; jangan menyebutnya double assessment penuh. Jika penilaian manusia belum tersedia, pertahankan status development AI SILVER — PROVISIONAL dan tunda klaim efektivitas utama.

## 9. Ringkasan siap diberikan kepada dosen

Implementasi R1 TF-IDF, R2 BM25, R3 BGE-M3 Dense dan R4 Hybrid RRF tersedia pada corpus V2 berisi 50 dokumen/371 chunks dengan konfigurasi dan artefak yang dapat ditelusuri. Pilot development 18 queries telah menghasilkan 72 ranking tersimpan beserta Top-10; ini menunjukkan pipeline menghasilkan output, bukan bahwa satu metode lebih efektif.

Audit relevance pilot membandingkan dua AI assessments atas 30 pasangan yang sama. Agreement seluruh pilot 26/30 (86,67%), both-resolved 26/29 (89,66%), kappa tanpa bobot 0,836466, dan kappa linear 0,865533. Empat kasus masih menunggu adjudikasi; tidak dipilih grade final. Kedua penilai tidak sepenuhnya terisolasi, identitas model/sesi detail tidak diekspos, dan belum ada human/expert validation. Hasil ini merupakan consistency assessment AI SILVER — PROVISIONAL.

Evaluasi efektivitas masih pending karena qrels hanya 684/6.678 pairs dan 75,56–82,78% hasil Top-10 belum judged. Tidak ada nDCG/MRR/Recall final, klaim metode terbaik, atau signifikansi. Mohon review desain main queries terpisah menurut information-need family, keterlibatan praktisi WO, opsi exhaustive/hybrid human judgments, prosedur independent second review/adjudikasi, serta freeze dan scope metrics sebelum evaluasi utama. Persetujuan pembimbing belum diasumsikan.

## 10. Validasi, artefak, dan STOP

PASS: existing audit CLI real-data compare, supplemental binding/provenance/evidence/readback checks, empat arithmetic self-checks (perfect agreement, opposite agreement, unknown exclusion, degenerate kappa), dan **8 targeted unittest tests** (3,145 detik; semua OK). Seluruh 740 protected files SHA-256 identik, termasuk 728-file historical baseline serta input/artefak paket dan second output tambahan. Baseline historical diverifikasi oleh preflight sebelum compare; supplemental menyimpan before/after hashes tambahan selama prosesnya. Tidak mengklaim full repository regression suite dijalankan pada milestone ini. Supplemental memastikan Torch tidak terimpor.

Artefak baru di `experiments/results/milestone_9a15_second_assessor_agreement_audit/`:

- `comparison.json`: accounting existing CLI, linear kappa, per-style matrices dan distribusi.
- `all_pair_comparisons.jsonl`: kedua keputusan/rationale/evidence untuk seluruh 30 pairs.
- `adjudication_candidates.jsonl`: empat kandidat raw dari existing CLI.
- `agreement_statistics.json`: kappa tanpa bobot, denominator eksplisit, by-style dan saved-ranking readback.
- `second_input_qc.json`: seluruh binding/provenance/input hashes dan keterbatasan isolasi.
- `disagreement_ledger.jsonl`: empat kasus dengan query/full chunk, exact kedua assessments, audit substantif, pertanyaan adjudikasi dan field keputusan manusia masih null.
- `supervisor_top10_example.csv`: contoh Top-10 dari saved ranking, tanpa scoring ulang.
- `protected_integrity.json`: protected hashes dan status pemeriksaan.
- `manifest.json`: perintah, validasi, hashes code/report/outputs dan status audit tersegel.

File additive lainnya: `scripts/audit_second_assessor_agreement.py`, laporan ini, dan [ringkasan terpisah untuk dosen](milestone_9a15_supervisor_review_summary.md). Tidak mengubah script audit existing, original qrels, grades/status/rationale assessments, corpus, embeddings, indices, retrieval parameters, atau ranking outputs. Tidak menjalankan retrieval/effectiveness evaluation, GPU inference, tuning, merge qrels, commit, push atau deploy. Tidak mengekspansi assessment ke pasangan lain.

**STOP — audit dan laporan selesai; supervisor review, human judgments, adjudikasi, dan evaluasi efektivitas utama tetap pending.**
