"""Pencatat kegiatan semua employee.
Setiap kejadian ditulis sebagai satu baris JSON ke logs/<nama>.jsonl
Tambahkan secara berurutan (append). Aman untuk multi-session.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
# logs/ berisi data kerja, bukan rahasia -> ikut git biar terlacak
LOG_DIR.mkdir(exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write(actor: str, event: str, **extra) -> dict:
    """Catat satu event. actor=mis. 'reiko'; event='send'|'trend'|...
    Return dict yang barusan ditulis."""
    rec = {"ts": _now(), "actor": actor, "event": event, **extra}
    path = LOG_DIR / f"{actor}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def recent(actor: str, hours: float = 24.0) -> list:
    """Baca semua catatan <nama> dalam N jam terakhir (utk dedup)."""
    path = LOG_DIR / f"{actor}.jsonl"
    if not path.exists():
        return []
    out = []
    # ukuran kecil; baca & filter. Gunakan garis waktu dgn patokan waktu parsing akhir.
    now = datetime.now(timezone.utc)
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
            ts = datetime.fromisoformat(rec["ts"])
            if (now - ts).total_seconds() <= hours * 3600:
                out.append(rec)
        except Exception:
            continue
    return out