# Karyawan AI #2 — "Comak", Pembuat Konten Visual

> Dokumen ini adalah RENCANA KERJA (PRD). Belum ada kode yang dibuat untuk
> Comak. Kamu setujui dulu, baru aku kerjakan.

---

## 1. Tujuan & hasil akhir

**Comak** adalah karyawan AI yang **membuat konten visual** (gambar + teks)
berdasarkan hasil riset dari **Reiko**. Outputnya bukan cuma teks — Comak
menghasilkan **gambar asli**, lalu mengirimnya sebagai **pesan gambar** ke
**Telegram** (dengan teks caption menyertainya).

Comak TIDAK riset sendiri. Dia makan data riset yang sudah dikumpulkan
Reiko (`employees/reiko/latest.json`).

Alur singkat:
```
Reiko riset tren  →  Comak baca hasil riset  →  Comak buat gambar + teks  →  kirim gambar+teks ke Telegram
```

## 2. Fondasi tambahan (di luar Reiko)

Semua tetap di satu folder `/root/hermes`. Comak pakai fondasi yang sudah ada
(core/send.py, core/log.py, config/secret.env) dan menambah satu modul baru:

```
employees/comak/
  run.py          <- otak Comak: baca riset, susun konten, kirim gambar
core/
  imagegen.py     <- BARU: pembuat gambar (Pollinations gratis)
```

- **core/imagegen.py** — satu titik pembuat gambar (semua karyawan bisa pakai,
  seperti core/send.py). Sekarang pakai **Pollinations.ai** (gratis, tanpa
  daftar, sudah teruji jalan dari mesin ini). Tiap gambar = URL request +
  simpan file PNG lokal.
- Comak memakai **core/send.py** yang sama (pengirim tunggu) — TIDAK membuat
  pengirim baru. Mode `latihan`/`kirim` tetap berlaku.

## 3. Urutan kerja Comak (tiap 2 jam)

1. **Baca riset Reiko** — baca `employees/reiko/latest.json`, ambil tren
   terbaik per niche (AI & Jepang, terpisah).
2. **Pilih 1-2 ide utama** — utk tiap niche, pilih konten yang paling bisa
   jadi gambar menarik.
3. **Buat prompt gambar** — dari judul tren → prompt bahasa Inggris untuk
   Pollinations (gaya anime / ilustrasi / realistis sesuai niche).
4. **Generate gambar** — via `core/imagegen.py` → file PNG lokal.
5. **Susun teks** — caption siap tempel (hook, hashtag) pakai ide tren.
6. **Kirim ke Telegram** — kirim **gambar + caption** sebagai pesan bergambar
   (bukan teks kosong), via pengirim.

## 4. Yang TIDAK dikerjakan Comak

- TIDAK riset sendiri → makan data dari Reiko saja.
- TIDAK posting ke platform. Hanya menyiapkan aset konten.
- TIDAK beli follower / cara abu-abu.
- TIDAK generate suara/video (gambar saja dulu).

## 5. Risiko gagal + cara atasi

| Masalah | Cara atasi |
|---|---|
| Pollinations kadang gagal/lambat | retry 3x; kalau tetap, kirim teks saja dengan catatan |
| Gambar korup / jelek | review manual dulu; kalau jelek, skip + catat log |
| Kualitas gambar | upgrade ke API bayar (OpenAI dll) kapan kamu mau |
| Telegram blokir | sudah ada fallback ke Discord (coba dulu) |
| Reiko tak ada data | jangan kirim kosong; tunggu siklus berikutnya |

## 6. Persetujuan

Setuju? Aku bangun `core/imagegen.py` + `employees/comak/main.py`, uji mode
latihan (lihat output tanpa kirim), lalu jalankan cron tiap 2 jam bersama
Reiko. Setelah itu conversation lanjut ke Discord nanti.

> (Sumber gambar: Pollinations gratis. Bisa upgrade ke API berbayar kapan pun.)