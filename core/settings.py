"""Pembaca pengaturan rahasia.
Membaca satu-satunya file rahasia: config/secret.env
File itu di-ignore git. Tiap employee pakai ini.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET_FILE = ROOT / "config" / "secret.env"


def load_secret_env(path: Path = SECRET_FILE) -> dict:
    """Parse file KEY=VALUE sederhana, abaikan baris kosong/#/-komentar."""
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def get_secret(name: str, default: str = "") -> str:
    """Cari nama di secret.env, lalu fallback ke env sistem."""
    return load_secret_env().get(name) or os.environ.get(name, default)


def discord_webhook() -> str:
    return get_secret("DISCORD_WEBHOOK_URL").strip()


def telegram_bot_token() -> str:
    return get_secret("TELEGRAM_BOT_TOKEN").strip()


def telegram_chat_id() -> str:
    return get_secret("TELEGRAM_CHAT_ID").strip()


if __name__ == "__main__":
    # bukti kecil: webhook terisi atau kosong (JANGAN print isinya)
    wh = discord_webhook()
    print("DISCORD webhook:", "TERISI" if wh else "KOSONG")