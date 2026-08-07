"""Reiko — pengumpul tren nyata (data lapangan).

Bukan AI "berpikir sendiri": script ini KERAS, hanya menarik data tren nyata lewat
jaringan, memfilter topik yang relevan niche "AI" dan "Jepang", lalu menyimpan
ringkasan ke employees/reiko/latest.json.

Ringkasan itu lalu dibaca oleh "kepala" (Hermes cron) utk disusun jadi laporan
konten siap-pakai (isi, caption, hashtag, prompt) dan dikirim ke Discord.

Sumber (tanpa SDK tambahan, murni stdlib):
  1. Google Trends RSS (per region)
  2. Reddit trending (r/artificial, r/Anime, r/japanese) via RSS JSON
Kegagalan satu sumber hanya di-log, tidak menggagalkan semuanya.
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from core import log  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; Reiko/1.0)"}

# "ai" harus word-boundary (jangan match substring: "raiders", "taiwan", "said")
AI_KEYWORDS = ["ai", "artificial", "chatgpt", "gpt", "llm", "machine learning",
               "stable diffusion", "midjourney", "openai", "deepseek",
               "copilot", "ai art", "prompt", "robot", "neural",
               # model & istilah tech yang sering tren di HN/tech
               "qwen", "gemini", "claude", "sora", "llama", "agent",
               "inference", "nvidia", "gpu", "ml", "deeplearning", "model",
               "algorithm", "dataset", "transformer", "open source model"]
# Keyword Jepang: romaji + kanji/kana umum (Google Trends JP isinya kanji)
JAPAN_KEYWORDS = ["japan", "tokyo", "anime", "manga", "sushi", "kyoto", "osaka",
                  "japanese", "nihongo", "j-pop", "cosplay", "shinkansen",
                  "studio ghibli", "kawaii", "hololive",
                  "fujifilm", "sumo", "kabuki", "jleague", "j-league",
                  "日本", "東京", "アニメ", "漫画", "富士", "大阪", "京都",
                  "桜", "初音ミク", "ポケモン", "任天堂"]


def _has_ai(t: str) -> bool:
    """AI match: word-boundary utk 'ai', substring utk istilah lain."""
    if re.search(r"\bai\b", t):
        return True
    return any(k in t for k in AI_KEYWORDS if k != "ai")


def _has_japan(t: str) -> bool:
    return any(k in t for k in JAPAN_KEYWORDS)


def fetch(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def google_trends(region: str = "US", limit: int = 15) -> list:
    out = []
    try:
        xml_src = fetch(f"https://trends.google.com/trending/rss?geo={region}")
        root = ET.fromstring(xml_src)
        for item in root.iter("item"):
            if len(out) >= limit:
                break
            t = item.find("title")
            if t is not None and t.text and t.text.strip():
                out.append(t.text.strip())
    except Exception as e:
        log.write("reiko", "source_fail", source=f"google_trends_{region}", reason=str(e))
    return out


def hackernews_top(limit: int = 8) -> list:
    """Hacker News front page via Algolia API -> list of titles (tech-forward)."""
    out = []
    try:
        data = json.loads(fetch(f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={limit}"))
        for hit in data.get("hits", []):
            t = hit.get("title", "").strip()
            if t:
                out.append(t)
    except Exception as e:
        log.write("reiko", "source_fail", source="hackernews", reason=str(e))
    return out


def classify(title: str) -> str:
    """Klasifikasi niche terpisah: 'ai', 'japan', atau '' (luar niches)."""
    t = title.lower()
    if _has_ai(t):
        return "ai"
    if _has_japan(t):
        return "japan"
    return ""


def base_score(title: str) -> int:
    """Skor kontekstual (bobot kata kunci), bukan cross-niche."""
    t = title.lower()
    s = 0
    if _has_ai(t):
        s += 1 + sum(t.count(k) for k in AI_KEYWORDS)
        if re.search(r"\bai\b", t):
            s += 1
    if _has_japan(t):
        s += 1 + sum(t.count(k) for k in JAPAN_KEYWORDS)
    return s


def main() -> None:
    raw: list = []
    for geo in ("US", "JP"):
        raw += google_trends(geo)
    raw += hackernews_top()  # Reddit diblokir 403 -> HN sumber tren tech

    # dedup + klasifikasi 2 niche terpisah
    items = {}
    for t in raw:
        ts = t.strip()
        if not ts:
            continue
        niche = classify(ts)
        if not niche:
            continue
        key = niche + "|" + ts.lower()
        items[key] = {"title": ts, "niche": niche, "score": base_score(ts)}

    # pisahkan ke 2 bucket, ambil top 5 masing-masing (urut skor)
    by_niche = {"ai": [], "japan": []}
    for it in items.values():
        by_niche[it["niche"]].append(it)
    for n in by_niche:
        by_niche[n].sort(key=lambda x: x["score"], reverse=True)
        by_niche[n] = by_niche[n][:5]

    bundle = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": ["US", "JP"],
        "niches": by_niche,          # {'ai':[...5], 'japan':[...5]}
        "counts": {"ai": len(by_niche["ai"]), "japan": len(by_niche["japan"])},
        "total_raw": len(raw),
    }
    path = ROOT / "employees" / "reiko" / "latest.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    log.write("reiko", "research", ai=len(by_niche["ai"]), japan=len(by_niche["japan"]))
    print(json.dumps(bundle, ensure_ascii=False))


if __name__ == "__main__":
    main()