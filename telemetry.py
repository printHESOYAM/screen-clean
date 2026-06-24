"""
telemetry.py — анонимная телеметрия для маркетинговой аналитики.

Собирает только агрегируемые метрики без персональных данных:
  install_id (случайный UUID), версия ОС, язык, настройки функций,
  число сессий, даты первого/последнего запуска, события очистки.

Настройка приёмника (один из вариантов):
  1. Переменная окружения SCREENCLEAN_TELEMETRY_URL
  2. Константа TELEMETRY_ENDPOINT ниже (PostHog, свой API, Google Apps Script)

Формат POST — JSON с полем "event". PostHog: задайте TELEMETRY_ENDPOINT
  https://us.i.posthog.com/capture/ и TELEMETRY_API_KEY = project API key;
  события автоматически оборачиваются в формат PostHog.
"""

import json
import os
import platform
import sys
import threading
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ─── PostHog (optional) ────────────────────────────────────────────────────
# Set via environment variables — see .env.example. Never commit real keys.
TELEMETRY_ENDPOINT = os.getenv("SCREENCLEAN_TELEMETRY_URL", "")
TELEMETRY_API_KEY = os.getenv("SCREENCLEAN_TELEMETRY_KEY", "")
APP_VERSION = "3.2"

TELEMETRY_PATH = Path(os.getenv("APPDATA")) / "DesktopCleaner" / "telemetry.json"
TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_local():
    if TELEMETRY_PATH.exists():
        try:
            with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_local(data):
    with open(TELEMETRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _install_id():
    data = _load_local()
    iid = data.get("install_id")
    if not iid:
        iid = str(uuid.uuid4())
        data["install_id"] = iid
        _save_local(data)
    return iid


def _utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _platform_info():
    return {
        "platform": sys.platform,
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
    }


def _feature_snapshot(cfg):
    return {
        "language": cfg.get("language", "en"),
        "autostart": bool(cfg.get("autostart", False)),
        "auto_clean_enabled": bool(cfg.get("enabled", True)),
        "sort_by_type": bool(cfg.get("sort_by_type", True)),
        "delay_hours": cfg.get("delay_hours", 24),
    }


def _endpoint_configured():
    return bool(TELEMETRY_ENDPOINT.strip())


def _posthog_payload(event: str, properties: dict) -> dict:
    return {
        "api_key": TELEMETRY_API_KEY,
        "event": event,
        "distinct_id": properties.get("install_id"),
        "properties": {
            **properties,
            "$lib": "screen-clean-desktop",
            "$lib_version": APP_VERSION,
        },
        "timestamp": _utc_now(),
    }


def _send_async(payload: dict):
    if not _endpoint_configured():
        return

    def _worker():
        try:
            body = payload
            if "posthog.com" in TELEMETRY_ENDPOINT and TELEMETRY_API_KEY:
                body = _posthog_payload(payload.get("event", "unknown"), payload)

            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                TELEMETRY_ENDPOINT,
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": f"ScreenClean/{APP_VERSION}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                resp.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def _base_payload(cfg, local: dict) -> dict:
    return {
        "install_id": local.get("install_id"),
        "app_version": APP_VERSION,
        "session_count": local.get("session_count", 0),
        "first_seen": local.get("first_seen"),
        "last_seen": local.get("last_seen"),
        "total_clean_events": local.get("total_clean_events", 0),
        "total_files_moved": local.get("total_files_moved", 0),
        **_platform_info(),
        **_feature_snapshot(cfg),
    }


def is_enabled(cfg) -> bool:
    return cfg.get("telemetry_enabled", True)


def track_session(cfg):
    """Вызывать один раз при старте приложения."""
    if not is_enabled(cfg):
        return

    local = _load_local()
    now = _utc_now()
    if "install_id" not in local:
        local["install_id"] = str(uuid.uuid4())
    if "first_seen" not in local:
        local["first_seen"] = now
    local["last_seen"] = now
    local["session_count"] = local.get("session_count", 0) + 1
    _save_local(local)

    payload = {**_base_payload(cfg, local), "event": "session_start"}
    _send_async(payload)


def track_clean(cfg, moved: int, force: bool = False):
    """Вызывать после do_clean() при moved > 0 или force-очистке."""
    if not is_enabled(cfg):
        return

    local = _load_local()
    if "install_id" not in local:
        local["install_id"] = _install_id()
    local["total_clean_events"] = local.get("total_clean_events", 0) + 1
    if moved > 0:
        local["total_files_moved"] = local.get("total_files_moved", 0) + moved
    local["last_seen"] = _utc_now()
    _save_local(local)

    payload = {
        **_base_payload(cfg, local),
        "event": "clean_completed",
        "moved": moved,
        "force": force,
    }
    _send_async(payload)


def track_settings_saved(cfg):
    """Вызывать при сохранении настроек из UI."""
    if not is_enabled(cfg):
        return

    local = _load_local()
    if "install_id" not in local:
        local["install_id"] = _install_id()
    local["last_seen"] = _utc_now()
    _save_local(local)

    payload = {**_base_payload(cfg, local), "event": "settings_saved"}
    _send_async(payload)


def get_local_summary():
    """Локальная сводка (для отладки на своей машине)."""
    return _load_local()
