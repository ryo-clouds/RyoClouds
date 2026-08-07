# RyoClouds — Rumah Para Karyawan AI

Repositori ini adalah rumah untuk **karyawan AI** (agent otomatis berjadwal)
milik kamu. Tiap karyawan punya folder sendiri di `employees/`, dan semua
berbagi fondasi yang sama di `core/`, `config/`, dan `docs/`.

## Struktur

```
employees/<nama>/run.py   # pengumpul data (keras, deterministik)
employees/<nama>/head.py  # penyusun laporan
core/send.py              # PENGIRIM TUNGGU ke Discord (mode latihan/kirim)
core/log.py                # pencatat semua kegiatan (.jsonl)
core/settings.py          # baca rahasia dari config/secret.env
config/secret.env         # SATU tempat isi rahasia (TIDAK di-commit)
config/secret.env.example # contoh kosong (aman di-commit)
plans/                    # file rencana kerja
docs/                     # dokumentasi (markdown + wikilink)
logs/                     # catatan runtime (tidak di-commit)
```

## Cara pakai (non-programmer)

Jangan pernah edit `config/secret.env` selain isi nilai di "=".
Karyawan baru = salin pola dari `employees/reiko/`.

## Status saat ini

Sedang membangun **karyawan #1: Reiko** (research konten AI x Jepang).
Lihat [[plans/PRD-reiko]] untuk rencana lengkap.