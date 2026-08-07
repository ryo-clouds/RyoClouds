# Karyawan AI #1 — "Reiko", Research Konten

> Dokumen ini adalah RENCANA KERJA (PRD). Belum ada kode yang dibuat.
> Kamu setujui dulu, baru aku kerjakan.

---

## 1. Tujuan & hasil akhir

**Reiko** adalah karyawan AI yang otomatis riset konten yang sedang tren di niche **AI** dan **Budaya Jepang**, lalu mengirim laporan siap-pakai ke **Discord** setiap **2 jam**.

Laporan berisi, untuk tiap ide konten:
- isi konten
- caption siap tempel
- hashtag
- prompt untuk membuat gambar / video

Hasil bertahap (biar aman dan kualitasnya terjaga):
- **Tahap 1 — Mode latihan:** 1 laporan per hari, TIDAK benar-benar dikirim ke Discord (cuma ditampilkan untuk dicek).
- **Tahap 2 — Mode kirim:** naik ke jadwal 2 jam sekali, laporan benar-benar terkirim ke Discord.

Mengapa bertahap: lebih baik cek dulu isinya layak, sebelum 12 laporan per hari membanjiri Discord-mu.

---

## 2. Fondasi yang aku bangun lebih dulu

Semua rapi di dalam satu folder kerja: `/root/hermes`

```
hermes/
  employees/           <- tempat tiap karyawan (masing-masing punya folder sendiri)
    reiko/             <- folder khusus Reiko
      run.py           <- otak: urutan kerja
  core/
    send.py            <- PENGIRIM SATU-SATUNYA ke Discord
                         punya 2 mode: "latihan" (tampil saja) dan "kirim" (beneran)
    log.py             <- pencatat semua kegiatan
  config/
    secret.env         <- SATU tempat isi semua rahasia (alamat Discord dll)
    secret.env.example <- contoh kosong (aman di-commit git)
  plans/               <- file rencana kerja
  docs/                <- dokumentasi, semua dalam markdown + wikilink
  .hermes/plans/       <- PRD ini
```

### Penjelasan fondasi

- **Folder per-karyawan (`employees/`)** — tiap karyawan punya folder sendiri. Karyawan baru tinggal tambah folder baru. Yang terisolasi.
- **File rahasia tunggal (`config/secret.env`)** — kamu isi alamat Discord dan rahasia lainnya cukup SATU KALI di satu tempat. Versi contoh (`secret.env.example`) tidak berisi rahasia, jadi aman di git. `secret.env` sendiri diedad diblokir dari git (lihat `.gitignore`).
- **"Pengirim tunggu" (`core/send.py`)** — satu pintu tunggal ke Discord. Karyawan baru cukup pakai, tidak perlu konfigurasi ulang. Dua mode:
  - **LATIHAN** — tampilkan laporan ke log/terminal, TIDAK mengirim. Untuk menilai kualitas.
  - **KIRIM** — kirim benar-benar lewat webhook Discord.
- **Dokumentasi** — semua keputusan dan kegiatan sasaran dicatat dalam markdown dan memakai wikilink, biar mudah dilacak.

---

## 3. Urutan kerja Reiko (tiap kali jalan)

1. **Deteksi tren** — lihat Google Trends + sumber lain yang aku kenal (crawl web/blog trending, Reddit, YouTube trending) untuk niche AI & Budaya Jepang.
2. **Pilih ide terbaik** — saring jadi 3-5 ide yang paling tahan peluang tinggi (yang sedang naik + relevan niche kamu).
3. **Susun laporan** — untuk tiap ide: isi konten, caption, hashtag, prompt gambar/video.
4. **Cegar laporan dobel** — bandingkan dengan laporan 24 jam terakhir; ide yang sama otomatis dibuang.
5. **Kirim hasil** — lewat `send.py` ke Discord (mode sesuai kesepakatan di atas).

---

## 4. Yang TIDAK dikerjakan Reiko

- TIDAK posting langsung ke platform media sosial. Hanya menyiapkan bahan.
- TIDAK beli follower / jasa bot / cara tidak sehat. Pertumbuhan = konten bagus.
- TIDAK membuat gambar/video beneran — hanya prompt-nya.
- TIDAK mengambil keputusan besar sendiri (kamu yang setujui). "Perlu mikir sendiri? tidak."

---

## 5. Risiko gagal + cara mengatasinga

| Masalah | Cara atasi |
|---|---|
| Alamat Discord salah | Semua rahasia di satu tempat (`secret.env`); uji dulu di mode latihan |
| Laporan dobel/ganda | Pengecpetan: cek laporan 24 jam terakhir |
| API/sumber kehabisan kuota | Retry 3x; kalau tetap gagal, catat di log + lewati putaran ini |
| Kualitas konten tidak bagus | Tahap latihan dulu, lalu kamu + aku sesuaikan |
| Jaringan/situs tidak bisa diakses | Retry 3x, lalu log dan lanjut jadwal berikutnya |
| Discord sedang down | Adakan port ke log, dicoba lagi nanti |

---

## 6. Persetujuan

Setuju? Aku eksekusi fondasi + **mode latihan** (1 laporan/hari). Setelah kamu merasa
laporan sudah bagus, aku naikkan ke **jadwal 2 jam sekali + kirim beneran**.