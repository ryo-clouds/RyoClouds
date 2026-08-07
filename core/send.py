"""PENGIRIM SATU-SATUNYA ke Discord.

Dipakai SEMUA employee. Jangan panggil webhook langsung dari tempat lain.

Mode:
  "latihan"  -> hanya tampilkan laporan (ke stdout) + catat log. TIDAK kirim.
  "kirim"    -> benar-benar kirim ke Discord via webhook.

Cara pakai (dari run.py employee):
    from core import send
    ok = send.report(actor="reiko", title="...", sections=[...], mode="latihan")

Kontrak pesan (agar seragam):
  title      = judul laporan (str)
  sections   = list of dict {heading, body}  (body boleh multiline)
  mode       = "latihan" | "kirim"
  source     = sumber tren (opsional, tampil di footer)
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from core import log, settings

MAX_BLOCKS = 8          # Discord embed: maks 25; kita batasi 8 biar aman
MAX_BODY_CHARS = 900    # batas tiap blok biar tidak kepanjangan


def _build_message(title: str, sections: list, source: str = "") -> dict:
    desc_parts = []
    for s in sections[:MAX_BLOCKS]:
        head = s.get("heading", "")
        body = (s.get("body", "") or "").strip()
        if not body:
            continue
        if head:
            desc_parts.append(f"**{head}**\n{body}")
        else:
            desc_parts.append(body)
    desc = "\n\n".join(desc_parts)[:5800]  # batas deskripsi embed Discord
    footer = f"dikirim oleh {settings.get_secret('BOT_NAME', 'Reiko')}"
    if source:
        footer += f" · sumber: {source}"
    return {
        "embeds": [
            {
                "title": title[:256],
                "description": desc,
                "color": 0x58B9FF,
                "footer": {"text": footer[:200]},
            }
        ]
    }


def _display(title: str, sections: list, source: str = "") -> None:
    """Tampilkan laporan ke terminal (mode latihan)."""
    print("=" * 60)
    print("LATIHAN - belum dikirim ke Discord")
    print("=" * 60)
    print(title)
    for s in sections:
        head = s.get("heading", "")
        body = (s.get("body", "") or "").strip()
        if head:
            print(f"\n### {head}")
        if body:
            print(body)
    if source:
        print(f"\n(sumber: {source})")
    print("=" * 60)


def _send_discord(payload: dict) -> bool:
    """Kirim payload JSON ke webhook. Return True kalau sukses."""
    url = settings.discord_webhook()
    if not url:
        print("ERROR: DISCORD_WEBHOOK_URL kosong. Isi config/secret.env")
        return False
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    last_err = None
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status in (200, 204)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(2 * attempt)  # backoff 2s, 4s, 6s
    print(f"ERROR kirim gagal setelah 3x: {last_err}")
    return False


def _send_telegram(text: str) -> bool:
    """Kirim teks ke Telegram via Bot API. Return True kalau sukses."""
    token = settings.telegram_bot_token()
    chat = settings.telegram_chat_id()
    if not token or not chat:
        print("ERROR: TELEGRAM_BOT_TOKEN/CHAT_ID kosong. Isi config/secret.env")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat, "text": text,
                          "parse_mode": "Markdown", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    last_err = None
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                return bool(data.get("ok"))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(2 * attempt)
    print(f"ERROR Telegram gagal setelah 3x: {last_err}")
    return False


def _send_telegram_photo(photo_path: str, caption: str = "") -> bool:
    """Kirim GAMBAR + caption ke Telegram via sendPhoto (multipart).
    Return True kalau sukses."""
    token = settings.telegram_bot_token()
    chat = settings.telegram_chat_id()
    if not token or not chat:
        print("ERROR: TELEGRAM_BOT_TOKEN/CHAT_ID kosong.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    # multipart/form-data manual (hindari dependency requests)
    boundary = "----ReikoBoundary" + str(int(time.time() * 1000))
    fields = {"chat_id": chat, "caption": caption or ""}
    # baca file
    with open(photo_path, "rb") as f:
        file_bytes = f.read()
    body = bytearray()
    for k, v in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; "
             f"filename=\"image.png\"\r\nContent-Type: image/png\r\n\r\n").encode()
    body += file_bytes
    body += f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        url, data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    last_err = None
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return bool(data.get("ok"))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(2 * attempt)
    print(f"ERROR kirim foto Telegram gagal: {last_err}")
    return False


def send_image(actor: str, photo_path: str, caption: str = "", mode: str = "latihan") -> bool:
    """Kirim gambar + caption ke tujuan. mode 'latihan' tampil saja (path).
    Telegram sekarang; kalau nanti Discord didukung, tambah di sini.
    Return True kalau sukses / display latihan."""
    if mode == "kirim":
        ok = _send_telegram_photo(photo_path, caption)
        log.write(actor, "send_image", mode="kirim", channel="telegram", ok=ok,
                  path=photo_path, caption=caption[:50])
        return ok
    # latihan
    print("=" * 60)
    print(f"LATIHAN - kirim GAMBAR (belum ke Telegram): {photo_path}")
    if caption:
        print(f"CAPTION: {caption}")
    print("=" * 60)
    log.write(actor, "send_image", mode="latihan", channel="telegram", ok=True,
              path=photo_path)
    return True


def report(actor: str, title: str, sections: list, mode: str = "latihan",
           source: str = "") -> bool:
    """Kirim/tampilkan laporan. Return True kalau sukses (atau sukses display)."""
    payload = _build_message(title, sections, source)
    if mode == "kirim":
        if _send_discord(payload):
            log.write(actor, "send", mode="kirim", channel="discord", ok=True, title=title[:80])
            return True
        # Discord gagal (mis. IP cloud diblokir 1010) -> fallback ke Telegram
        print("Discord gagal, coba kirim via Telegram...")
        text = f"*{title}*\n\n" + "\n\n".join(
            f"**{s.get('heading','')}**\n{s.get('body','')}" for s in sections if s.get('body')
        )
        if _send_telegram(text):
            log.write(actor, "send", mode="kirim", channel="telegram", ok=True, title=title[:80])
            return True
        log.write(actor, "send", mode="kirim", channel="discord+telegram", ok=False, title=title[:80])
        return False
    # default = latihan
    _display(title, sections, source)
    log.write(actor, "send", mode="latihan", ok=True, title=title[:80])
    return True


def test_webhook() -> bool:
    """Kirim pesan uji kecil. Dipakai sekali pas setup (mode kirim)."""
    ok = _send_discord({"content": "✅ Uji koneksi: Reiko siap kerja!"})
    log.write("reiko", "test_webhook", ok=ok)
    return ok


if __name__ == "__main__":
    # CLI manual: python -m core.send latihan|kirim
    mode = sys.argv[1] if len(sys.argv) > 1 else "latihan"
    report(
        actor="reiko",
        title="Laporan Uji",
        sections=[{"heading": "Contoh", "body": "Ini hanya tes."}],
        mode=mode,
    )