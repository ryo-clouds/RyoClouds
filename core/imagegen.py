"""core/imagegen.py — Pembuat gambar untuk semua karyawan.

Satu titik untuk membuat gambar (seperti core/send.py utk kirim pesan).
Karyawan tidak perlu tahu detail provider.

Provider sekarang: Pollinations.ai (gratis, tanpa daftar, murni HTTP GET).
  URL: https://image.pollinations.ai/prompt/<prompt>?width=W&height=H&nologo=true
  Download hasilnya sebagai file gambar lokal.

Mode: selalu simpan file ke disk (assets/<nama>.png) lalu kembalikan path.
"""
import time
import urllib.parse
import urllib.request
from pathlib import Path

from core import log

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (compatible; Reiko/1.0)"}


def generate_image(prompt: str, width: int = 1024, height: int = 1024,
                   actor: str = "default", tag: str = "img",
                   retries: int = 3) -> str | None:
    """Buat gambar dari prompt. Simpan file, return path absolut (atau None).
    tag dipakai utk nama file biar unik per seansa (mis. 'qwen', 'anime')."""
    if not prompt:
        log.write(actor, "img_fail", reason="prompt kosong")
        return None

    safe = str(int(time.time()))
    out_path = ASSETS / f"{actor}_{tag}_{safe}.png"
    encoded = urllib.parse.quote(prompt)
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           f"?width={width}&height={height}&nologo=true")

    last = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if not data:
                raise ValueError("respons kosong")
            out_path.write_bytes(data)
            log.write(actor, "image_generated", ok=True, prompt=prompt[:60],
                      path=str(out_path))
            return str(out_path)
        except Exception as e:
            last = e
            log.write(actor, "image_retry", prompt=prompt[:60], attempt=attempt,
                      error=str(e)[:100])
            time.sleep(2 * attempt)
    log.write(actor, "image_fail", prompt=prompt[:60], error=str(last)[:100])
    return None