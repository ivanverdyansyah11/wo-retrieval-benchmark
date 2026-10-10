# Ringkasan untuk dosen — Milestone 9A.15

**INTER-ASSESSOR PILOT AUDITED, READY FOR SUPERVISOR REVIEW**

| Jenis hasil | Capaian yang tersedia | Batas klaim |
|---|---|---|
| Implementasi | R1 TF-IDF, R2 BM25, R3 BGE-M3 Dense, R4 Hybrid RRF; snapshot V2 berisi 50 dokumen/371 chunks | Implementasi dan artefak tersedia; belum membuktikan keunggulan efektivitas atau validitas praktik WO |
| Pilot retrieval | 18 development queries × 4 metode = 72 ranking tersimpan; 720 Top-10 rows | Output development, bukan final/main evaluation; tidak ada scoring ulang pada audit ini |
| Consistency assessment | Dua AI assessments atas 30 pasangan; agreement 26/30 = 86,67%; both-resolved 26/29 = 89,66% | AI SILVER — PROVISIONAL; kedua penilai tidak sepenuhnya terisolasi dan belum human/expert validated |
| Evaluasi efektivitas | Masih pending | Tidak ada nDCG/MRR/Recall final, metode terbaik, atau signifikansi |

Kappa tanpa bobot direkomputasi sebesar **0,836466**, sedangkan kappa berbobot linear dari script existing sebesar **0,865533**. Keduanya menggunakan 29 pasangan yang sama-sama RESOLVED; satu keputusan UNRESOLVED tetap null dan tidak menjadi Grade 0. Statistik ini deskriptif untuk pilot purposive kecil dengan pasangan yang berkelompok per query, bukan ukuran akurasi terhadap judgment manusia.

Distribusi first: Grade 0/1/2 = 13/11/5, UNRESOLVED 1. Distribusi second: 10/15/5, UNRESOLVED 0. Terdapat tiga perbedaan Grade 0→1 dan satu UNRESOLVED→1, pada WO-POOL-V2-0003, WO-POOL-V2-0107, WO-POOL-V2-0246, WO-POOL-V2-0325. Keempat kasus disimpan dengan kedua rationale/evidence dan pertanyaan adjudikasi; tidak ditetapkan grade final.

Qrels existing hanya mencakup **684/6.678 pasangan**, dengan **5.994 UNJUDGED**. Proporsi Top-10 belum judged adalah R1 78,33%, R2 82,78%, R3 75,56%, R4 77,22%. Coverage tersebut membatasi interpretasi efektivitas; agreement AI tidak menyelesaikan missing judgments. Corpus AI-corrected dan queries development juga masih membutuhkan review praktisi.

Keputusan metodologi yang dimohonkan kepada pembimbing:

1. Tetapkan development dan evaluation queries terpisah berdasarkan information-need family, termasuk paraphrase; rencana 75 main queries masih proposal, belum dibuat pada audit ini.
2. Libatkan praktisi WO sebagai primary relevance assessor dan reviewer qualified kedua yang menilai secara independen tanpa ranking, scores, atau labels AI. Pilot manusia sebaiknya mencakup seluruh 30 pasangan, termasuk consensus borderline.
3. Pilih exhaustive human judgments atau workflow hybrid: union Top-20 R1–R4, sampel outside-pool, 10 predeclared exhaustive queries dan independent second review subset. Kalibrasi workload nyata sebelum ekspansi; semua selected pairs tetap memerlukan judgment manusia.
4. Simpan original judgments, konteks dan adjudikasi secara versioned; jangan overwrite AI assessments/qrels atau mengubah unknown menjadi 0. Bekukan rubric, query families, corpus, qrels scope, primary metrics dan kebijakan incomplete judgments sebelum evaluasi utama.

Rekomendasi separation dan pooling mengikuti praktik [NIST TREC](https://trec.nist.gov/howto.html) dan prinsip [development/test separation dalam Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/information-retrieval-system-evaluation-1.html). Detail desain dan batas klaim ada dalam [laporan audit 9A.15](milestone_9a15_second_assessor_agreement_audit.md).

Audit teknis lulus: 30/30 binding cocok, evidence verbatim, provenance disclosure tercatat, 8 targeted tests dan arithmetic self-checks lulus, 740 protected files tetap identik. Tidak menjalankan evaluasi final, GPU inference, tuning, commit/push/deploy. Persetujuan pembimbing, human/expert validation, adjudikasi dan evaluasi efektivitas tetap pending.
