"""
stats.py — журнал перемещённых файлов для отображения в UI.

Каждый успешный вызов do_clean() с moved > 0 добавляет событие
{timestamp, count}. get_stats(hours) суммирует count по событиям
в пределах окна времени — на этом строится "29 файлов за 24 часа".
total_all_time считается отдельно и хранится всегда (не зависит от окна).
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

STATS_PATH = Path(os.getenv("APPDATA")) / "DesktopCleaner" / "stats.json"
STATS_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_EVENTS = 2000  # ограничение, чтобы файл не рос бесконечно


def _load():
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"events": [], "total_all_time": 0}


def _save(data):
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_event(count: int):
    """Вызывать после do_clean(), если count > 0."""
    if count <= 0:
        return
    data = _load()
    data["events"].append({
        "timestamp": datetime.now().isoformat(),
        "count": count,
    })
    data["events"] = data["events"][-MAX_EVENTS:]
    data["total_all_time"] = data.get("total_all_time", 0) + count
    _save(data)


def get_stats(hours: int = 24):
    """Возвращает {window_count, total_all_time} за последние `hours` часов."""
    data = _load()
    cutoff = datetime.now() - timedelta(hours=hours)
    window_count = 0
    for ev in data["events"]:
        try:
            ts = datetime.fromisoformat(ev["timestamp"])
            if ts >= cutoff:
                window_count += ev["count"]
        except Exception:
            continue
    return {
        "window_count": window_count,
        "total_all_time": data.get("total_all_time", 0),
    }
