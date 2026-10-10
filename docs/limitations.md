# Batasan dataset, penilaian, dan evaluasi

Corpus adalah 50 dokumen WO sintetis; orang/event/venue/vendor disimulasikan. Parsing, hash, dan konsistensi struktur bukan bukti validitas praktik WO nyata. V2 masih `ai_corrected_pilot_not_human_validated`; review praktisi diperlukan untuk validasi domain.

18 queries merupakan development queries. Queries untuk pengembangan/tuning tidak boleh diperlakukan sebagai evaluation set independen. Main evaluation belum dijalankan; usulan jumlah evaluation queries belum merupakan rancangan disetujui.

654 judgments berasal dari satu peneliti, berlabel `Researcher-annotated relevance judgments`, belum expert-validated atau independently validated. AI silver qrels dan pilot assessments terpisah. Kedua penilai AI pilot tidak sepenuhnya terisolasi; agreement adalah consistency audit terbatas, bukan bukti correctness relevance.

Assessed pool adalah union Top-20 empat metode. Unresolved dan chunk di luar pool tidak dijadikan Grade 0. Precision/MRR memakai Grade ≥1; nDCG memakai pooled IDCG, bukan exhaustive corpus judgments. Recall tidak dihitung. Perbandingan macro/style deskriptif; signifikansi statistik belum diuji.

Evaluasi utama perlu query kebutuhan informasi independen, development/evaluation split yang disepakati dan dibekukan, pooling memadai, assessor yang tidak melihat ranking/scores/label sebelumnya, serta adjudikasi disagreements tanpa menghapus label awal. Praktisi WO atau second human assessor dapat menilai scope baru secara independen; kompetensi, identitas, rubric, waktu, dan provenance harus dicatat. Agreement dilaporkan bersama disagreements dan unresolved, tanpa memaksakan grade final.

Publikasi public memerlukan review privasi dan izin redistribusi. Identitas peneliti, metadata penulis, notes/provenance, paths perangkat, dan bukti historis ada di repository. Jangan menyanitasi file frozen tanpa prosedur versi baru. LICENSE belum tersedia; weights tidak disertakan. Private repository untuk pembimbing adalah pilihan awal yang disarankan.
