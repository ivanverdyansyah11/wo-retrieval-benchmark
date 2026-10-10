# Rubric dan workflow blind AI silver assessment

Rubric version: `wo_pooled_silver_rubric_v1`.

Status semua calon penilaian: **AI SILVER — PROVISIONAL**, bukan human validated,
expert ground truth, gold standard atau independently validated.
Paket ini belum berisi penilaian selesai.

## Paket yang boleh diberikan kepada assessor

Untuk pilot, berikan **hanya** file ini dan `blind_pilot_30.jsonl` ke sesi assessor
baru yang tidak membawa riwayat penelitian atau akses otomatis ke repository.
Setelah pilot quality gate PASS, berikan batch berikutnya dari
`blind_assessment_ledger.jsonl`, tanpa mengulang assessment_id yang telah selesai.
Urutan ledger telah diacak deterministik; jangan mengurutkannya kembali berdasarkan
hasil pencarian. Pertahankan exact query text dan exact serialized chunk text.

Jangan memberikan audit asal kandidat, manifest penelitian, ranking, skor,
metode retrieval, label lama, hasil evaluasi atau percakapan peneliti kepada
assessor. Dokumen ini tidak menyediakan informasi tersebut. IDs hanya untuk
binding dan pelacakan; jangan menggunakan pola ID untuk memprediksi grade.

## Unit penilaian

Nilai satu pasangan query–chunk, bukan seluruh dokumen. Baca query sampai jelas
kebutuhan informasi yang dicari. Baca seluruh serialized chunk, termasuk konteks
yang memang tersedia di dalam input. Nilai kontribusi isi terhadap kebutuhan
tersebut, bukan jumlah kata yang sama. Jangan menganggap sebuah chunk menjawab
query hanya karena judulnya tampak cocok.

| Status / grade | Aturan |
|---|---|
| ASSESSED / 2 | Chunk langsung memberi informasi substantif yang menjawab kebutuhan query. Tidak harus menjadi satu-satunya chunk yang mencakup semua aspek tugas, tetapi kontribusinya harus langsung dan nyata. |
| ASSESSED / 1 | Chunk memberi dukungan berguna atau sebagian aspek kebutuhan, tetapi belum menjawab kebutuhan utama secara memadai. Kedekatan topik saja tidak cukup. |
| ASSESSED / 0 | Isi telah diperiksa dan tidak memberi informasi yang relevan untuk menjawab kebutuhan tersebut, meski domain atau istilahnya serupa. |
| UNRESOLVED / null | Bukti tidak cukup, query ambigu, konteks penting hilang atau penilai tidak dapat mempertanggungjawabkan grade. Jangan menggantinya dengan 0. |
| PENDING / null | Belum dinilai. Bukan keputusan UNRESOLVED dan bukan grade 0. |

Perbedaan peran, event, waktu dan batas kewenangan diperiksa hanya sejauh tertulis.
Jangan menambahkan asumsi operasional untuk membuat jawaban cocok. Informasi
umum bisa bernilai 1 jika membantu kebutuhan spesifik; domain WO semata tidak
cukup. Overlap antar-chunk dinilai sendiri, tidak auto-copy grade.

## Format hasil

Pertahankan semua field binding dari input. Ubah hanya field assessment:

- `assessment_status`: `ASSESSED` atau `UNRESOLVED`.
- `relevance_grade`: integer 0/1/2 untuk ASSESSED; null untuk UNRESOLVED.
- `evidence`: list kutipan verbatim yang menjadi substring exact serialized
  chunk. Wajib ada sedikitnya satu untuk ASSESSED, termasuk grade 0; pada grade
  0, rationale menjelaskan mengapa kutipan itu tidak mendukung kebutuhan.
- `rationale`: alasan ringkas yang menghubungkan isi kutipan dan kebutuhan query.
- `ambiguity_flag`: boolean, wajib true untuk UNRESOLVED.
- `uncertainty_notes`: catatan batas bukti; jangan membuat confidence numerik
  yang tidak terkalibrasi. Bedakan keyakinan membaca teks dari validitas praktik WO.
- `context_opened`: kosong bila tidak membuka sumber tambahan. Jika diperlukan,
  minta materi melalui pengelola yang tidak memberi label/ranking, lalu catat
  document_id, source path, heading/block/locator, hash materi, exact excerpt dan
  alasan dibuka. Grade tetap merujuk kontribusi chunk ini, bukan jawaban yang
  hanya muncul pada sumber tambahan. Bila konteks belum tersedia, UNRESOLVED.
- `assessor_provenance`: actual model_id, model_revision, session_id, assessed_at
  UTC, rubric_version, label `AI SILVER — PROVISIONAL`, human_validated false.
  Jika provider tidak mengekspos revision, tulis `not_exposed` dan catat batasnya;
  jangan menebak model, revision atau timestamp. Pengelola juga mencatat prompt
  hash, input/output file hashes, konfigurasi sampling yang benar-benar tersedia,
  batch IDs dan apakah sesi bebas dari metadata retrieval/label lama.

Tidak ada output ASSESSED yang sah hanya karena schema-nya benar; kualitas
rationale dan hubungan substantif dengan query tetap harus ditelaah.

## Pilot dan quality gate sebelum ekspansi

Pilot berisi 30 pasangan, dipilih sebelum penilaian. Proses dalam satu atau
beberapa batch kecil dengan rubric yang sama. Pengelola harus memeriksa seluruh
30 hasil: binding/hash, schema, kutipan verbatim, direct answer vs supporting
information vs topical similarity, asumsi tak tertulis, ambiguity, unresolved,
serta kemungkinan lexical anchoring. Jangan memaksakan distribusi grade tertentu.

Jika tersedia assessor kedua dengan konteks terisolasi, berikan input pilot yang
sama dalam urutan acak terdokumentasi lain, tanpa grade/rationale pertama dan
tanpa metadata retrieval. Bandingkan hasil setelah kedua outputs disegel dengan
checksum. Simpan grade, rationale dan disagreement masing-masing. Model/sesi
kedua dari keluarga model sama bukan validasi manusia atau bukti independensi
ilmiah. Jika tidak tersedia, catat NOT RUN, jangan mengklaim inter-rater agreement.

Schema/evidence checks dapat otomatis. Rubric consistency, substantive relevance
dan lexical bias tidak dapat dibuktikan hanya dari checksum atau grade histogram.
Jika ada kebingungan sistematis pada pilot, STOP, dokumentasikan perubahan rubric
secara versioned, dan nilai ulang pilot blind sebelum batch lanjutan. Jangan
melanjutkan karena output lengkap atau karena labels mendukung hasil yang diinginkan.

## Setelah penilaian selesai

Pengelola membuka audit internal hanya setelah output blind selesai dan hashes
disimpan. Untuk pasangan berlabel lama, lakukan comparison sebagai consistency
check; disagreement dilog, bukan overwrite. Untuk pasangan belum dinilai, simpan
proposed grade terpisah setelah quality gate. UNRESOLVED tetap tidak menjadi qrel.

Re-audit coverage dengan existing labels dan proposed labels sebagai dua scope
berbeda. Existing conflict dipertahankan sebagai konflik, tidak memilih grade
berdasarkan hasil pencarian. Laporkan count, grade distribution, unresolved,
disagreements dan keterbatasan pool. Jangan merge ke benchmark resmi tanpa review.

AI labels tidak membuktikan kebenaran praktik WO atau validitas scientific ground
truth. Human/researcher/expert review harus mempunyai provenance dan ledger
terpisah, tanpa mengangkat persetujuan AI menjadi keputusan manusia. Metodologi
utama, assessor dan penggunaan silver metrics memerlukan persetujuan pembimbing.
