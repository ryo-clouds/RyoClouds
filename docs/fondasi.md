# Fondasi Sistem

Semua karyawan berbagi fondasi yang sama. Jangan duplikasi.

## core/send.py — Pengirim Tunggu

Satu-satunya pintu ke Discord. Panggil `send.report(...)`, jangan pernah
memanggil webhook langsung dari tempat lain.

```python
from core import send
send.report(actor="reiko", title="...", sections=[{"heading":"...", "body":"..."}],
            mode="latihan" | "kirim")
```

- **mode="latihan"** — tampilkan laporan ke terminal/log. TIDAK kirim.
- **mode="kirim"** — kirim beneran ke Discord via webhook.
- Ada retry 3x + backoff. Gagal? dicatat di log.

## core/log.py — Pencatat

Semua kegiatan ditulis sebagai baris JSON ke `logs/<nama>.jsonl`:
event `send`, `research`, `source_fail`, `test_webhook`, dll.
Bisa dibaca ulang utk cek dedup 24 jam.

## config/secret.env — Satu tempat rahasia

- Berisi: `DISCORD_WEBHOOK_URL` (dan rahasia lain).
- File ini **tidak di-commit** git (.gitignore).
- Salinan kosong: `config/secret.env.example` (aman di-commit).
- Setiap rahasia baru tambahkan di file ini + contohnya.

Lihat juga: [[index]] · [[karyawan-reiko]] · [[catatan-sistem]]