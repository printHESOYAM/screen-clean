"""
Desktop Cleaner — основная логика + pywebview UI.
Логика переноса файлов идентична оригиналу, изменился только слой окна настроек.
"""

import os
import sys
import json
import shutil
import socket
import ctypes
import time
import threading
import functools
import http.server
from pathlib import Path
from datetime import datetime, timedelta

import winreg
import pystray
from PIL import Image, ImageDraw
import webview

import stats as stats_module
import desktop_state as desktop_state_module
import telemetry as telemetry_module

APP_NAME = "ScreenClean"
APP_VERSION = telemetry_module.APP_VERSION
DISPLAY_NAME = "Screen Clean"
# Crypto wallets for the donate button (override via env if needed).
DONATE_BTC = os.getenv("SCREENCLEAN_DONATE_BTC", "12JECJCE6C55RJ55CXq5unGHmjor74ZjuC")
DONATE_USDT_TRC20 = os.getenv("SCREENCLEAN_DONATE_USDT_TRC20", "TLPrZ5WgRH55Yhj6PaMAGJCwR9nJFoA8dH")
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))  # для PyInstaller
# index.html / style.css / app.js лежат рядом с desktop_cleaner.py;
# фоновые изображения — в assets/ (bg-waves, bg-glow, bg-leaf и др.).

DESKTOP = Path.home() / "Desktop"


def _resolve_desktop() -> Path:
    """Реальный путь к рабочему столу из реестра Windows (OneDrive, локализация)."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        path, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        return Path(path)
    except Exception:
        return DESKTOP


def _desktop_paths() -> list[Path]:
    """Личный + общий рабочий стол (ярлыки Opera/Chrome часто на Public Desktop)."""
    paths: list[Path] = []
    seen: set[str] = set()

    def add(p: Path):
        try:
            resolved = str(p.resolve())
        except Exception:
            resolved = str(p)
        if p.exists() and resolved not in seen:
            seen.add(resolved)
            paths.append(p)

    add(_resolve_desktop())

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        common, _ = winreg.QueryValueEx(key, "Common Desktop")
        winreg.CloseKey(key)
        add(Path(common))
    except Exception:
        add(Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop")

    return paths


def _iter_desktop_items():
    """Все элементы со всех рабочих столов, без дубликатов по полному пути."""
    seen: set[str] = set()
    for desktop in _desktop_paths():
        try:
            for item in desktop.iterdir():
                try:
                    key = str(item.resolve())
                except Exception:
                    key = str(item)
                if key in seen:
                    continue
                seen.add(key)
                yield item
        except Exception:
            continue


def _delay_hours(cfg) -> float:
    try:
        return float(cfg.get("delay_hours", 24))
    except (TypeError, ValueError):
        return 24.0


def _native_hwnd(window):
    native = window.native
    if native is None:
        return None
    try:
        if hasattr(native, "Handle"):
            h = native.Handle
            return h.ToInt32() if hasattr(h, "ToInt32") else int(h)
        if hasattr(native, "handle"):
            return int(native.handle)
    except Exception:
        pass
    return None


def _patch_pywebview_drag_bridge():
    """scDrag* через js_bridge_call — синхронно на UI-потоке (WebApi идёт в Thread и не годится)."""
    import webview.util as wutil

    if getattr(wutil, "_sc_drag_patched", False):
        return

    _orig = wutil.js_bridge_call
    _drag = {"active": False, "win_x": 0, "win_y": 0, "start_x": 0, "start_y": 0}

    def _patched(window, func_name, param, value_id):
        if func_name == "scDragStart":
            _drag["win_x"] = window.x
            _drag["win_y"] = window.y
            _drag["start_x"] = int(param[0])
            _drag["start_y"] = int(param[1])
            _drag["active"] = True
            return
        if func_name == "scDragMove":
            if not _drag["active"]:
                return
            sx, sy = int(param[0]), int(param[1])
            x = _drag["win_x"] + sx - _drag["start_x"]
            y = _drag["win_y"] + sy - _drag["start_y"]
            window.move(x, y)
            return
        if func_name == "scDragEnd":
            _drag["active"] = False
            return
        return _orig(window, func_name, param, value_id)

    wutil.js_bridge_call = _patched
    wutil._sc_drag_patched = True


def _defer_gui(action):
    """На Windows нельзя hide/show синхронно из closing — только из другого потока (pywebview #1103)."""
    def _run():
        try:
            time.sleep(0.05)
            action()
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


def _hide_window(window):
    if sys.platform == "win32":
        try:
            hwnd = _native_hwnd(window)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
                return
        except Exception:
            pass
    try:
        window.hide()
    except Exception:
        pass


def _minimize_window(window):
    if sys.platform == "win32":
        try:
            hwnd = _native_hwnd(window)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
                return
        except Exception:
            pass
    try:
        window.minimize()
    except Exception:
        pass


def _show_window(window):
    try:
        window.show()
        window.restore()
    except Exception:
        if sys.platform == "win32":
            try:
                hwnd = _native_hwnd(window)
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass


# ─── Локальный HTTP-сервер для UI ─────────────────────────────────────────
# pywebview на Windows блокирует часть ресурсов через file:// из-за CORS.
# Поднимаем свой сервер на localhost, отдающий BASE_DIR (папку со скриптом),
# где лежат index.html / style.css / app.js — без вложенных подпапок.

def _find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_ui_server():
    port = _find_free_port()
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(BASE_DIR)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port
CONFIG_PATH = Path(os.getenv("APPDATA")) / "DesktopCleaner" / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "target_folder": str(Path.home() / "Desktop" / "Archive"),
    "delay_hours": 24,
    "exclusions": ["Archive"],
    "enabled": True,
    "autostart": True,
    "sort_by_type": True,
    "language": "en",
    "telemetry_enabled": True,
}

UI_STRINGS = {
    "ru": {
        "settings": "⚙ Настройки",
        "pause": "⏸ Остановить",
        "start": "▶ Запустить",
        "clean_now": "🧹 Очистить сейчас (всё)",
        "quit": "❌ Выйти",
        "moved": "Перемещено файлов: {n}",
        "move_error": "Ошибка перемещения {name}: {err}",
        "file_locked": "файл занят другой программой",
    },
    "en": {
        "settings": "⚙ Settings",
        "pause": "⏸ Pause",
        "start": "▶ Start",
        "clean_now": "🧹 Clean now (all)",
        "quit": "❌ Quit",
        "moved": "Files moved: {n}",
        "move_error": "Move error {name}: {err}",
        "file_locked": "file is in use by another program",
    },
    "es": {
        "settings": "⚙ Ajustes",
        "pause": "⏸ Pausar",
        "start": "▶ Iniciar",
        "clean_now": "🧹 Limpiar ahora (todo)",
        "quit": "❌ Salir",
        "moved": "Archivos movidos: {n}",
        "move_error": "Error al mover {name}: {err}",
        "file_locked": "el archivo está en uso por otro programa",
    },
    "ja": {
        "settings": "⚙ 設定",
        "pause": "⏸ 一時停止",
        "start": "▶ 開始",
        "clean_now": "🧹 今すぐ整理（すべて）",
        "quit": "❌ 終了",
        "moved": "移動したファイル: {n}",
        "move_error": "移動エラー {name}: {err}",
        "file_locked": "他のプログラムが使用中です",
    },
}

CATEGORY_EXTENSIONS = {
    "images":    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".heic", ".raw",
                  ".psd", ".psb", ".ai", ".eps", ".xd"},
    "video":     {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"},
    "music":     {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"},
    "documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".txt", ".rtf", ".csv"},
    "apps":      {".exe", ".msi", ".bat", ".cmd", ".ps1", ".sh", ".apk"},
    "archives":  {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"},
    "code":      {".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yml", ".yaml", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt"},
    "shortcuts": {".lnk", ".url"},
}

CATEGORY_LABELS = {
    "ru": {
        "folders": "📁 Папки",
        "images": "🖼 Картинки",
        "video": "🎬 Видео",
        "music": "🎵 Музыка",
        "documents": "📄 Документы",
        "apps": "💾 Приложения",
        "archives": "🗜 Архивы",
        "code": "💻 Код",
        "shortcuts": "🔗 Ярлыки",
        "other": "📦 Разное",
    },
    "en": {
        "folders": "📁 Folders",
        "images": "🖼 Images",
        "video": "🎬 Video",
        "music": "🎵 Music",
        "documents": "📄 Documents",
        "apps": "💾 Apps",
        "archives": "🗜 Archives",
        "code": "💻 Code",
        "shortcuts": "🔗 Shortcuts",
        "other": "📦 Other",
    },
    "es": {
        "folders": "📁 Carpetas",
        "images": "🖼 Imágenes",
        "video": "🎬 Vídeo",
        "music": "🎵 Música",
        "documents": "📄 Documentos",
        "apps": "💾 Aplicaciones",
        "archives": "🗜 Archivos",
        "code": "💻 Código",
        "shortcuts": "🔗 Accesos directos",
        "other": "📦 Otros",
    },
    "ja": {
        "folders": "📁 フォルダ",
        "images": "🖼 画像",
        "video": "🎬 動画",
        "music": "🎵 音楽",
        "documents": "📄 ドキュメント",
        "apps": "💾 アプリ",
        "archives": "🗜 アーカイブ",
        "code": "💻 コード",
        "shortcuts": "🔗 ショートカット",
        "other": "📦 その他",
    },
}


def tr(key: str, cfg, **kwargs) -> str:
    lang = cfg.get("language", "en")
    text = UI_STRINGS.get(lang, UI_STRINGS["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text


# ─── Конфиг ───────────────────────────────────────────────────────────────

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ─── Автозапуск (Windows) ───────────────────────────────────────────────

def set_autostart(enabled: bool):
    exe = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Autostart error: {e}")


# ─── Категоризация ───────────────────────────────────────────────────────

def get_category(item: Path, cfg) -> str:
    lang = cfg.get("language", "en")
    labels = CATEGORY_LABELS.get(lang, CATEGORY_LABELS["en"])
    if item.is_dir():
        return labels["folders"]
    ext = item.suffix.lower()
    for key, extensions in CATEGORY_EXTENSIONS.items():
        if ext in extensions:
            return labels[key]
    return labels["other"]


# ─── Отбор файлов ─────────────────────────────────────────────────────────

def _item_key(item: Path) -> str:
    try:
        return str(item.resolve())
    except Exception:
        return str(item)


def _should_skip_item(item: Path, target: Path, exclusions: set) -> bool:
    name_lower = item.name.lower()
    if item.name in exclusions:
        return True
    if name_lower in ("desktop.ini", "thumbs.db"):
        return True
    if item.name.startswith("."):
        return True
    try:
        item_r = item.resolve()
        target_r = target.resolve()
        if item_r == target_r:
            return True
        # не трогаем папку-архив и всё, что уже лежит внутри неё
        try:
            item_r.relative_to(target_r)
            return True
        except ValueError:
            pass
        try:
            target_r.relative_to(item_r)
            return True
        except ValueError:
            pass
    except Exception:
        pass
    return False


def _friendly_error(err: Exception, cfg) -> str:
    if isinstance(err, PermissionError) or getattr(err, "winerror", None) in (5, 32):
        return tr("file_locked", cfg)
    return str(err)


def get_files_to_move(cfg):
    exclusions = set(cfg.get("exclusions", []))
    target = Path(cfg["target_folder"])
    delay = timedelta(hours=_delay_hours(cfg))
    now = datetime.now()

    eligible = []
    for item in _iter_desktop_items():
        if _should_skip_item(item, target, exclusions):
            continue
        eligible.append(item)

    state = desktop_state_module.sync({_item_key(item) for item in eligible})

    to_move = []
    for item in eligible:
        try:
            seen = datetime.fromisoformat(state[_item_key(item)])
            if now - seen >= delay:
                to_move.append(item)
        except Exception:
            continue
    return to_move


def get_all_files_to_move(cfg):
    exclusions = set(cfg.get("exclusions", []))
    target = Path(cfg["target_folder"])
    to_move = []
    for item in _iter_desktop_items():
        if _should_skip_item(item, target, exclusions):
            continue
        to_move.append(item)
    return to_move


# ─── Перенос ──────────────────────────────────────────────────────────────

def do_clean(cfg, force=False):
    base_target = Path(cfg["target_folder"])
    base_target.mkdir(parents=True, exist_ok=True)
    moved = 0
    sort_by_type = cfg.get("sort_by_type", True)
    failed = []

    files_to_move = get_all_files_to_move(cfg) if force else get_files_to_move(cfg)

    moved_keys = []
    for item in files_to_move:
        try:
            target = base_target / get_category(item, cfg) if sort_by_type else base_target
            target.mkdir(parents=True, exist_ok=True)
            dest = target / item.name
            if dest.exists():
                stem = dest.stem if dest.is_file() else dest.name
                suffix = dest.suffix if dest.is_file() else ""
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = target / f"{stem}_{ts}{suffix}"
            shutil.move(str(item), str(dest))
            moved += 1
            moved_keys.append(_item_key(item))
        except Exception as e:
            err = _friendly_error(e, cfg)
            print(tr("move_error", cfg, name=item.name, err=err))
            failed.append({"name": item.name, "error": err})

    if moved_keys:
        desktop_state_module.forget(moved_keys)

    if moved > 0:
        stats_module.record_event(moved)
    if moved > 0 or force:
        telemetry_module.track_clean(cfg, moved, force=force)
    return {"moved": moved, "failed": failed}


# ─── Фоновый поток ────────────────────────────────────────────────────────

class CleanerWorker:
    def __init__(self, get_cfg):
        self.get_cfg = get_cfg
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.wait(60):
            cfg = self.get_cfg()
            if cfg.get("enabled", True):
                do_clean(cfg, force=False)

    def stop(self):
        self._stop.set()


# ─── Иконка трея ──────────────────────────────────────────────────────────

def make_icon(active=True):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (255, 107, 53) if active else (142, 142, 147)  # оранжевый акцент вместо зелёного
    d.rectangle([4, 20, 60, 54], fill=color)
    d.rectangle([4, 14, 28, 24], fill=color)
    cx, cy, aw = 32, 37, 10
    d.polygon([
        (cx, cy + 10), (cx - aw, cy - 2), (cx - 5, cy - 2),
        (cx - 5, cy - 10), (cx + 5, cy - 10), (cx + 5, cy - 2),
        (cx + aw, cy - 2)
    ], fill="white")
    return img


# ─── JS API мост для pywebview ───────────────────────────────────────────

class WebApi:
    def __init__(self, get_cfg, update_cfg):
        self._get_cfg = get_cfg
        self._update_cfg = update_cfg

    def get_config(self):
        return self._get_cfg()

    def save_config(self, new_cfg):
        self._update_cfg(new_cfg)
        set_autostart(new_cfg.get("autostart", True))
        telemetry_module.track_settings_saved(new_cfg)
        return {"ok": True}

    def pick_folder(self):
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def clean_now(self, temp_cfg):
        temp_cfg["enabled"] = True
        return do_clean(temp_cfg, force=True)

    def get_stats(self):
        return stats_module.get_stats(hours=24)

    def hide_to_tray(self):
        _defer_gui(lambda: _hide_window(webview.windows[0]))
        return {"ok": True}

    def minimize_window(self):
        _defer_gui(lambda: _minimize_window(webview.windows[0]))
        return {"ok": True}

    def get_donate_wallets(self):
        wallets = {}
        btc = (DONATE_BTC or "").strip()
        usdt = (DONATE_USDT_TRC20 or "").strip()
        if btc:
            wallets["btc"] = btc
        if usdt:
            wallets["usdt_trc20"] = usdt
        return wallets


# ─── main ─────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    telemetry_module.track_session(cfg)

    def get_cfg():
        return cfg

    def update_cfg(new_cfg):
        nonlocal cfg
        cfg = new_cfg
        save_config(cfg)
        refresh_icon()

    worker = CleanerWorker(get_cfg)
    icon_holder = {}
    window_holder = {}

    def refresh_icon():
        if "icon" in icon_holder:
            icon_holder["icon"].icon = make_icon(cfg.get("enabled", True))
            update_menu()

    def open_settings(icon=None, item=None):
        _defer_gui(lambda: _show_window(window_holder["window"]))

    def toggle_enabled(icon=None, item=None):
        cfg["enabled"] = not cfg.get("enabled", True)
        save_config(cfg)
        refresh_icon()

    def clean_now(icon=None, item=None):
        result = do_clean(cfg, force=True)
        msg = tr("moved", cfg, n=result["moved"])
        if result["failed"]:
            names = ", ".join(f["name"] for f in result["failed"][:3])
            msg += f" ({len(result['failed'])} err: {names})"
        icon_holder["icon"].notify(msg, DISPLAY_NAME)

    def quit_app(icon=None, item=None):
        worker.stop()
        try:
            icon_holder["icon"].stop()
        except Exception:
            pass
        os._exit(0)

    def update_menu():
        status = tr("pause" if cfg.get("enabled", True) else "start", cfg)
        icon_holder["icon"].menu = pystray.Menu(
            pystray.MenuItem(tr("settings", cfg), open_settings, default=True),
            pystray.MenuItem(status, toggle_enabled),
            pystray.MenuItem(tr("clean_now", cfg), clean_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(tr("quit", cfg), quit_app),
        )

    menu = pystray.Menu(
        pystray.MenuItem(tr("settings", cfg), open_settings, default=True),
        pystray.MenuItem(tr("pause" if cfg.get("enabled", True) else "start", cfg), toggle_enabled),
        pystray.MenuItem(tr("clean_now", cfg), clean_now),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(tr("quit", cfg), quit_app),
    )

    icon = pystray.Icon(APP_NAME, make_icon(cfg.get("enabled", True)), DISPLAY_NAME, menu)
    icon_holder["icon"] = icon

    set_autostart(cfg.get("autostart", True))

    # ── Локальный сервер + pywebview-окно, создаём один раз, скрытым ──
    server, port = start_ui_server()
    api = WebApi(get_cfg, update_cfg)
    window = webview.create_window(
        DISPLAY_NAME,
        url=f"http://127.0.0.1:{port}/index.html",
        js_api=api,
        width=420,
        height=740,
        resizable=False,
        frameless=True,
        easy_drag=False,
        background_color="#0c0b0a",
    )
    window_holder["window"] = window
    startup_hide = {"done": False}

    def on_loaded():
        if startup_hide["done"]:
            return
        startup_hide["done"] = True
        _defer_gui(lambda: _hide_window(window))

    window.events.loaded += on_loaded

    def on_closing():
        _defer_gui(lambda: _hide_window(window))
        return False

    window.events.closing += on_closing

    # Трей — в фоновом потоке (pystray поддерживает detached-режим)
    icon.run_detached()

    _patch_pywebview_drag_bridge()

    # webview ОБЯЗАН работать в главном потоке — поэтому он здесь, последним
    webview.start()


if __name__ == "__main__":
    main()
