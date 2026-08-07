"""Novel Publishing Department — orchestrator.

Menjalankan pipeline produksi novel sesuai hierarki role. Setiap "role" =
SOP markdown + folder output. Orchestrator memanggil tiap stage sesuai urutan
workflow, mencatat ke log, dan meneruskan konteks antar stage.

Arsitektur: role-role yang "berpikir" (research, planning, editing, review)
dieksekusi oleh LLM (lewat agent/cron). Role-role mekanis (rendering PDF,
mengumpulkan output) dieksekusi script ini. Pipeline nyata = kombinasi keduanya.

Sekarang: scaffolding framework. Eksekusi per-stage akan dijalankan oleh
agen (Hermes) yang memanggil core/send.py utk hasilnya.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core import log  # noqa: E402

# Urutan pipeline produksi (sesuai workflow dept)
PIPELINE = [
    # Research
    ("research", "trend-researcher"),
    ("research", "market-analyst"),
    # Creative
    ("creative", "story-planner"),
    ("creative", "character-designer"),
    ("creative", "world-builder"),
    ("creative", "outline-architect"),
    # Production (loop per chapter)
    ("production", "chapter-planner"),
    ("production", "novel-writer"),
    ("production", "continuity-checker"),
    ("production", "editor"),
    ("production", "quality-reviewer"),
    # Publishing
    ("publishing", "seo-specialist"),
    ("publishing", "cover-designer"),
    ("publishing", "metadata-manager"),
    ("publishing", "publisher"),
    # Growth
    ("growth", "revenue-analyst"),
    ("growth", "improvement-analyst"),
    ("growth", "knowledge-manager"),
]


def pipeline() -> list:
    """Return daftar (team, role) sesuai urutan."""
    return list(PIPELINE)


def log_pipeline_run() -> None:
    log.write("novel_dept", "pipeline", stage_count=len(PIPELINE))


if __name__ == "__main__":
    print(f"Novel Publishing pipeline: {len(PIPELINE)} stages")
    for team, role in PIPELINE:
        print(f"  {team:12s} -> {role}")