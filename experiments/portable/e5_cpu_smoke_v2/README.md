# E5-Small CPU v2: panduan Kaggle

Status: Windows unit/mock dan pemeriksaan snapshot dilakukan pada 15 Oktober 2026.
**Clean install Linux dan inference Kaggle NOT TESTED.** WSL lokal terdaftar tetapi
gagal start dengan `Wsl/Service/CreateInstance/MountDisk/ERROR_PATH_NOT_FOUND`.
Itu bukan diagnosis hardware dan bukan error Kaggle pengguna.

Runner v2 berdiri sendiri. Ia tidak mengimpor encoder/recovery historis, BGE,
FlagEmbedding, datasets, scipy atau sklearn. Revision, 384 dimensi, batch 1,
256 token, dua thread, CPU FP32, prefix query/passage, pooling mask-mean dan L2
tetap sama. Baseline dan cache v1 tidak ditulis. Sample disimpan di
`experiments/embedding_portability/v2/`, bukan indeks evaluator.

## Input dan environment

Gunakan sesi Kaggle baru, accelerator **None**, Internet aktif untuk pip/model.
Salin source bundle ke `/kaggle/working/wo-retrieval-benchmark`. Jangan menjalankan
dari `/kaggle/input` yang read-only. Untuk download/short diperlukan `src/wo_retrieval`
(`__init__.py`, `e5_portable_v2.py`), script v2, dan seluruh bundle konfigurasi ini.
Untuk tahap chunks, sediakan sendiri frozen
`data/versions/v2_ai_corrected/reports/serialized_inputs.jsonl` yang SHA256-nya
terikat di `corpus-binding.json`. Dataset tidak disertakan ke bundle source publik.
Path mount alternatif dapat diberikan dengan `--chunks-file`.

Python harus **3.12**. Jika tidak tersedia, status BLOCKED; jangan mengganti versi
kontrak. Notebook berikut memakai venv baru agar tidak mencampurkan stack bawaan
Kaggle/BGE/CUDA. Periksa status setiap sel sebelum melanjutkan.

```python
import subprocess
from pathlib import Path

repo = Path('/kaggle/working/wo-retrieval-benchmark')
venv = repo / '.cache/e5-cpu-linux-v2'
assert not venv.exists(), 'Gunakan direktori environment baru'
subprocess.run(['python3.12', '-m', 'venv', str(venv)], check=True)
python = str(venv / 'bin/python')
bundle = 'experiments/portable/e5_cpu_smoke_v2'

def checked(*args):
    subprocess.run([python, '-B', *args], cwd=repo, check=True)
```

Lock `linux-wheels.lock.txt` berisi 27 artifact dengan SHA256 yang benar-benar
di-resolve dari Windows untuk wheel Linux cp312 x86_64. Torch memakai URL CPU
resmi dan semua versi library kontrak dipertahankan. Lock cross-resolved ini
belum diuji dengan installer/interpreter Linux; colorama pure-Python juga ikut
terpilih karena marker resolver host Windows. Jangan menafsirkan hasil resolusi
sebagai clean install Linux.

Periksa instalasi lock pada Kaggle dan catat report aktual:

```python
checked('-m', 'pip', '--isolated', 'install', '--dry-run',
        '--report', '.cache/e5-linux-locked-resolution.json',
        '-r', f'{bundle}/linux-wheels.lock.txt')
```

Sesudah resolusi lulus, pasang lock itu. Pin `+cpu` wajib;
`+cu126` ditolak runner meskipun nomor release sama.

```python
checked('-m', 'pip', '--isolated', 'install',
        '-r', f'{bundle}/linux-wheels.lock.txt')
checked('-m', 'pip', 'check')
with (repo / '.cache/e5-cpu-linux-v2.actual-lock.txt').open('w') as log:
    subprocess.run([python, '-m', 'pip', 'freeze', '--all'], cwd=repo, stdout=log, check=True)
```

`runtime.txt`, `torch-cpu.txt`, dan constraints juga disertakan untuk menjelaskan
pin sumber resolusi, bukan jalur fallback mengganti versi. Wheel torch CPU cp312
x86_64 tercantum di
[index resmi](https://download.pytorch.org/whl/cpu/torch/); keberadaan wheel tidak
membuktikan instalasi sukses. Jika resolver menolak pin, simpan output sebagai
BLOCKED. Jangan upgrade/downgrade untuk memaksakan PASS.

## Smoke bertahap

```python
def stage(name, output, *extra):
    checked('scripts/e5_portable_v2.py', name, '--output',
            f'experiments/embedding_portability/v2/{output}', *extra)
```

Jika snapshot model belum ada, download eksplisit ke cache workspace:

```python
stage('download', 'kaggle_download_v1')
```

Untuk mode offline, gunakan snapshot lengkap dengan basename revision
`614241f622f53c4eeff9890bdc4f31cfecc418b3` dan tambahkan `--snapshot`, path snapshot
pada setiap perintah. Keenam file diverifikasi SHA256. Snapshot parsial/korup
dilewati saat autodiscovery; snapshot eksplisit yang salah langsung ditolak.
Pencarian menghormati HF_HUB_CACHE, HF_HOME, XDG_CACHE_HOME, home dan workspace.

Jalankan di **sel terpisah**, baca receipt sebelum langkah berikutnya:

```python
stage('preflight', 'kaggle_preflight_v1')
stage('short', 'kaggle_short_v1')
stage('chunks', 'kaggle_one_v1', '--limit', '1')
stage('chunks', 'kaggle_five_v1', '--limit', '5')
```

Query pendek hanya di-encode sekali per invocation. Tahap chunks meng-encode
query lalu 1–5 passage berturut-turut, dengan prefix yang sesuai. Dense ranking
sample memakai query vector yang sama. Shape query harus `(1,384)`, passage
`(N,384)`, CPU, FP32, finite dan L2 unit. Baca `receipt.json`, hash output,
token/truncation receipt, serta memory samples. Output lama tidak ditimpa.

`inspect` boleh memeriksa snapshot/resource pada mesin legacy; receipt dapat
PASS untuk inspeksi dengan `cpu_environment_ready=false`. Itu **bukan** preflight
atau inference PASS. Semua tahap selain inspect menuntut pin CPU-only persis.

Gate tetap aktif: RAM efektif >=3 GiB sebelum load dan >=1,5 GiB saat forward,
host memory load <90%, visible cgroup v1/v2 dan ancestor limits, serta Linux
strict-overcommit headroom >=2 GiB ketika mode strict berlaku. Windows commit
API tidak dipakai; Windows commit-headroom tidak diklaim terukur oleh v2.
Pemeriksaan proses menolak Python lain di luar keluarga launcher; kernel induk
diizinkan, sibling kernel/workload tidak. Lock eksklusif tidak dicuri otomatis.
Jika STOP: periksa receipt/workload atau gunakan sesi baru. Jangan retry otomatis,
mematikan proses asing, atau menghapus lock aktif. Keterbatasan: sampel memori di
batas operasi, bukan watchdog kontinu atau jaminan terhadap OOM lonjakan/native
process yang tidak terlihat. Tidak ada opsi full-corpus di runner ini.

Sesudah smoke target selesai, simpan receipt dan actual environment lock sebagai
bukti lokal yang direview. Jangan mengubah hash/identity cache v1 agar menerima
hasil v2. Evaluasi utama, full-corpus inference dan impor hasil cloud memerlukan
prosedur/otorisasi terpisah.
