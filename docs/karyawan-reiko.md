# Karyawan #1 — Reiko

**Peran:** Research konten trending niche **AI** dan **Budaya Jepang** untuk
growth follower 0 → 100k di platform sosial.

## Alur kerja

```
run.py (pengumpul tren)  →  latest.json  →  head.py / Hermes cron (penyusun)  →  core/send.py → Discord
```

1. **run.py** — ambil tren nyata: Google Trends (US, JP) + Hacker News front page.
   Simpan ringkasan ke `employees/reiko/latest.json`. (Keras, tidak "berpikir".)
2. **Kepala** (Hermes cron, LLM) — baca `latest.json`, susun jadi laporan
   konten: isi, caption, hashtag, prompt gambar/video.
3. **core/send.py** — kirim ke Discord (atau tampil dulu di mode latihan).

## Jadwal
- Tiap **2 jam** (via Hermes cron).

## Tidak boleh
- Laporan dobel (dedup di kolektor + cek 24 jam terakhir).
- SELF posting / beli follower.
- "Berpikir sendiri" — keputusan besar tetap di persetujuan.

## Sumber yang dipakai
Google Trends (RSS) · Hacker News (Algolia) · (Reddit ditangguhkan: IP cloud diblokir 403).

Lihat juga: [[PRD-reiko]] · [[catatan-sistem]] · [[index]]