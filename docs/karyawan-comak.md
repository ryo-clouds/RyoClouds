# Komak — Pembuat Konten Visual

**Peran:** Membuat konten visual (GAMBAR + teks) dari hasil riset **Reiko**,
lalu kirim ke Telegram sebagai pesan bergambar.

> Comak TIDAK riset sendiri. Dia makan data riset dari Reiko
> (`employees/reiko/latest.json`) dan menambahkan gambar.

## Alur kerja

```
Reiko riset →  Comak baca latest.json →  buat prompt gambar →  generate
via core/imagegen (Pollinations) →  kirim GAMBAR + caption via core/send
```

1. **Segarkan data** — jalankan `python3 employees/reiko/run.py` (biar data fresh).
2. **Baca riset** — `employees/reiko/latest.json`, 2 niche terpisah (ai, japan).
3. **Pilih ide** — 1-2 judul skor tertinggi per niche.
4. **Generate gambar** — via `core/imagegen.py` (Pollinations.ai, gratis).
5. **Kirim** — `core/send.send_image(...)` → foto + caption ke Telegram.

## Jadwal
Tiap 2 jam (via Hermes cron, job `4a22b39d9d24`). Comak self-contained:
ia jalankan run.py Reiko dulu tiap siklus biar data fresh (tidak tergantung
urutan cron Reiko).

## Gambar
- Provider free: **Pollinations.ai** — tanpa daftar, output file PNG ke `assets/`.
- Gaya per niche: ai → futuristic/tech; japan → anime/japanese aesthetic.
- Setiap siklus generate gambar BARU (tidak pakai cache lama).

## Tidak boleh
- TIDAK riset sendiri. · TIDAK posting. · TIDAK beli follower. · TIDAK audio/video.

Lihat juga: [[PRD-comak]] · [[karyawan-reiko]] · [[fondasi]] · [[catatan-sistem]] · [[index]]