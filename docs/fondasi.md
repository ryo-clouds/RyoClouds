# Fondasi Sistem

Semua karyawan berbagi fondasi yang sama. Jangan duplikasi.

## core/send.py — Pengirim Tunggu

Satu-satunya pintu ke Discord. Panggil `send.report(...)`, jangan pernah
memanggil webhook langsung dari tempat lain.

```python
from core import send
send.report(actor="reiko", title="...", sections=[{"heading":"...", "body":"..."}],
            mode="latihan" | "kirim")
send.send_image(actor="comak", photo_path="...", caption="...", mode="kirim")  # gambar
```

- **mode="latihan"** — tampilkan laporan ke terminal/log. TIDAK kirim.
- **mode="kirim"** — kirim beneran via webhook/Telegram.
- `send_image()` — kirim FOTO + caption ke Telegram (sendPhoto, multipart).
- Ada retry 3x + backoff. Gagal? dicatat di log.

## core/imagegen.py — Pembuat Gambar

Satu titik untuk membuat gambar (seperti send.py utk pesan).

```python
from core import imagegen
path = imagegen.generate_image("prompt ...", actor="comak", tag="ai")
```

- Provider: **Pollinations.ai** (gratis, tanpa daftar, HTTP GET).
- Simpan PNG ke `assets/`, return path absolut. Retry 3x + backoff.
- Gagal total → return None + catat log.

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