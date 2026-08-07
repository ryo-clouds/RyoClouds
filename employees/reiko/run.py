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

AI_KEYWORDS = ["ai", "artificial", "chatgpt", "gpt", "llm", "machine learning",
               "stable diffusion", "midjourney", "openai", "deepseek",
               "copilot", "ai art", "prompt", "robot", "neural"]
JAPAN_KEYWORDS = ["japan", "tokyo", "anime", "manga", "sushi", "kyoto", "osaka",
                  "japanese", "nihongo", "j-pop", "cosplay", "shinkansen",
                  "studio ghibli", "kawaii", "hololive"]


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


def score(title: str) -> int:
    t = title.lower()
    s = 0
    if any(k in t for k in AI_KEYWORDS):
        s += 2
    if any(k in t for k in JAPAN_KEYWORDS):
        s += 3  # fokus niche AI x Jepang
    return s


def main() -> None:
    raw: list = []
    for geo in ("US", "JP"):
        raw += google_trends(geo)
    raw += hackernews_top()  # Reddit diblokir 403 -> HN sebagai sumber tren tech

    # dedup
    seen = {}
    for t in raw:
        ts = t.strip()
        if not ts:
            continue
        key = ts.lower()
        if key in seen:
            seen[key]["score"] = max(seen[key]["score"], score(ts))
        else:
            seen[key] = {"title": ts, "score": score(ts)}

    scored = list(seen.values())
    scored.sort(key=lambda x: x["score"], reverse=True)
    relevant = [s for s in scored if s["score"] > 0][:10]
    if not relevant:
        relevant = scored[:5]

    bundle = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "regions": ["US", "JP"],
        "trends": relevant,
        "total_raw": len(scored),
    }
    path = ROOT / "employees" / "reiko" / "latest.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    log.write("reiko", "research", trend_count=len(relevant), raw_count=len(scored))
    print(json.dumps(bundle, ensure_ascii=False))


if __name__ == "__main__":
    main()