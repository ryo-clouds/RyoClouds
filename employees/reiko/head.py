"""Reiko — KEPALA (penyusun laporan).

Baca hasil riset (employees/reiko/latest.json) yang berisi 2 niche TERPISAH
('ai' dan 'japan'), lalu susun laporan konten per-niche dan kirim via
core/send.py (pintu tunggu). Discord diblokir dari IP cloud, sehingga mode
'kirim' otomatis fallback ke Telegram.

Tidak "berpikir"/menebak: bekerja dari data nyata terkumpul. Output bagian
laporan terstruktur, dibagi rapi per niche.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from core import send  # noqa: E402

LATEST = ROOT / "employees" / "reiko" / "latest.json"

NICHE_LABEL = {"ai": "🤖 AI", "japan": "🇯🇵 Budaya Jepang"}


def load() -> dict:
    if not LATEST.exists():
        return {}
    return json.loads(LATEST.read_text(encoding="utf-8"))


def build_sections_for_niche(niche: str, items: list, limit: int = 5) -> list:
    """Susun bagian laporan dari item-item niche tertentu."""
    label = NICHE_LABEL.get(niche, niche.upper())
    sections = []
    for i, it in enumerate(items[:limit], 1):
        title = it.get("title", "(tanpa judul)")
        sections.append({"heading": f"{label} · Ide {i}: {title}", "body": (
            f"**Isi konten:** Ide dari tren \"{title}\" untuk konten viral.\n"
            f"**Caption:** hook kuat, bahasa Indonesia. + #hashtag niche.\n"
            f"**Prompt gambar/video:** deskripsi spesifik (gaya, subjek, cahaya).\n"
            f"**Sumber:** {it.get('source', '-')}"
        )})
    return sections


def render_text(title: str, sections: list) -> str:
    """Render laporan jadi teks polos (utk Telegram preview)."""
    parts = [f"*{title}*"]
    for s in sections:
        parts.append(f"**{s.get('heading','')}**\n{s.get('body','')}")
    return "\n\n".join(parts)


def main() -> None:
    data = load() or {}
    niches = data.get("niches", {})
    mode = sys.argv[1] if len(sys.argv) > 1 else "latihan"

    # Grup laporan: heading seksi per niche + kirim satu pesan per niche
    # (agar 2 niche terpisah jelas di kirim).
    sent = 0
    for niche in ("ai", "japan"):
        items = niches.get(niche, [])
        if not items:
            continue
        label = NICHE_LABEL.get(niche, niche.upper())
        title = f"📊 Konten {label} — Reiko"
        sections = build_sections_for_niche(niche, items)
        ok = send.report("reiko", title, sections, mode=mode,
                         source="GoogleTrends+HN")
        sent += 1

    if sent == 0:
        print("Tidak ada data untuk kedua niche. Jalankan run.py dulu.")
    else:
        print(f"OK ({sent} niche dikirim)") if mode == "kirim" else print("OK (latihan)")


if __name__ == "__main__":
    main()