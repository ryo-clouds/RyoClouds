"""Comak — Pembuat Konten Visual.

Membuat GAMBAR + teks dari hasil riset Reiko (employees/reiko/latest.json),
lalu mengirimnya sebagai pesan bergambar ke Telegram.

Alur: baca riset Reiko -> pilih 1-2 ide/niche -> buat prompt gambar ->
generate via core/imagegen -> susun caption -> kirim via core/send.send_image.

Tidak "berpikir": bekerja dari data riset Reiko yang sudah nyata.
Mode: 'latihan' (default) atau 'kirim' (benar2 ke Telegram).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from core import imagegen, send, log  # noqa: E402

LATEST = ROOT / "employees" / "reiko" / "latest.json"

# Prompt-style per niche (biar gambar sesuai tema, bukan campur)
STYLE = {
    "ai": ("futuristic, glowing holographic interface, cinematic lighting, "
           "high detail, 4k"),
    "japan": ("japanese anime style, vibrant colors, cherry blossoms, "
              "traditional japanese aesthetic, high detail, 4k"),
}


def load_trends() -> dict:
    if not LATEST.exists():
        return {}
    try:
        return json.loads(LATEST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_image_prompt(niche: str, title: str) -> str:
    """Jadikan judul tren jadi prompt gambar bahasa Inggris (spesifik)."""
    style = STYLE.get(niche, "modern, clean, high detail, 4k")
    return f"{title}, {style}"


def build_caption(niche: str, title: str) -> str:
    """Caption siap tempel (bahasa Indonesia, hook, hashtag)."""
    if niche == "ai":
        tags = "#AI #TeknologiAI #ArtificialIntelligence #FutureTech #Automasi"
    else:
        tags = "#Jepang #Anime #BudayaJepang #Japan #Kawaii"
    return (f"{title}\U0001F525\n\n"
            f"Ikuti buat konten AI & Jepang harian!\n\n{tags}")


def main() -> None:
    data = load_trends()
    if not data or not data.get("niches"):
        print("Tidak ada data riset Reiko. Jalankan run.py Reiko dulu.")
        return

    mode = sys.argv[1] if len(sys.argv) > 1 else "latihan"
    niches = data["niches"]
    sent = 0

    for niche in ("ai", "japan"):
        items = niches.get(niche, [])
        if not items:
            continue
        # ambil ide skor tertinggi utk gambar (maks 2/niche)
        top = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[:2]
        for it in top:
            title = it.get("title", "(tanpa judul)")
            prompt = build_image_prompt(niche, title)
            img = imagegen.generate_image(prompt, actor="comak",
                                          tag=niche[:4])
            if not img:
                print(f"[{niche}] generate gambar GAGAL: {title[:40]}")
                continue
            caption = build_caption(niche, title)
            ok = send.send_image("comak", img, caption=caption, mode=mode)
            if ok:
                sent += 1

    log.write("comak", "run", mode=mode, sent=sent)
    print(f"DONE: {sent} gambar dikirim (mode={mode})")


if __name__ == "__main__":
    main()