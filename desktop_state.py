"""
desktop_state.py — когда файл впервые появился на рабочем столе.

Таймер «хранить N часов» считается от первого обнаружения приложением,
а не от даты изменения файла (mtime). Иначе скопированные/скачанные файлы
с «старой» датой переносятся сразу.
"""

import json
import os
from pathlib import Path
from datetime import datetime

STATE_PATH = Path(os.getenv("APPDATA")) / "DesktopCleaner" / "desktop_state.json"
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load():
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sync(names_on_desktop: set[str]) -> dict:
    """Обновить журнал: новые имена — с текущим временем, пропавшие — удалить."""
    state = _load()
    now = datetime.now().isoformat()
    for name in names_on_desktop:
        if name not in state:
            state[name] = now
    for name in list(state):
        if name not in names_on_desktop:
            del state[name]
    _save(state)
    return state


def forget(names):
    if not names:
        return
    state = _load()
    changed = False
    for name in names:
        if name in state:
            del state[name]
            changed = True
    if changed:
        _save(state)


def first_seen(name: str) -> datetime | None:
    state = _load()
    raw = state.get(name)
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None
