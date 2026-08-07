"""Reiko — KEPALA (penyusun laporan).

Baca hasil riset (employees/reiko/latest.json) lalu susun jadi laporan
terstruktur (isi konten, caption, hashtag, prompt gambar/video) dan kirim
via core/send.py (satu-satunya pintu ke Discord).

Tidak "berpikir"/menebak: bekerja dari data nyata yang terkumpul. Output
berupa bagian-bagian laporan yang disusun dari tren dengan skor niche.

Mode: 'latihan' (default) -> tampilkan saja. 'kirim' -> benar2 ke Discord.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from core import send  # noqa: E402

LATEST = ROOT / "employees" / "reiko" / "latest.json"


def load_trends() -> list:
    if not LATEST.exists():
        return []
    data = json.loads(LATEST.read_text(encoding="utf-8"))
    return data.get("trends", [])


def build_sections(trends: list) -> list:
    """Buat bagian laporan (heading+body) dari tiap tren."""
    sections = []
    for i, t in enumerate(trends[:5], 1):
        title = t.get("title", "(tanpa judul)")
        sections.append({"heading": f"Ide {i}: {title}", "body": (
            f"**Caption:** Coba ide konten tren ini dalam niche AI x Jepang.\n"
            f"**Hashtag:** #AI #Jepang #trend #fyp\n"
            f"**Prompt gambar/video:** Ilustrasi {title} gaya anime Jepang, "
            f"Narasi pendek soal AI."
        )})
    return sections


def main() -> None:
    trends = load_trends()
    if not trends:
        title = "📊 Tren Konten Reiko — tidak ada data"
        sections = [{"heading": "Info", "body": "Belum ada tren terkumpul. Jalankan run.py dulu."}]
    else:
        title = f"📊 Tren Konten Reiko — {trends[0]['title']}"
        sections = build_sections(trends)
    mode = sys.argv[1] if len(sys.argv) > 1 else "latihan"
    ok = send.report("reiko", title, sections, mode=mode, source="GoogleTrends+HN")
    print("OK" if ok else "GAGAL")


if __name__ == "__main__":
    main()