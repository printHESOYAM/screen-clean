# Screen Clean

**EN:** Automatic desktop organizer for Windows — keeps your desktop clean without manual sorting.  
**RU:** Автоматическая сортировка рабочего стола для Windows — порядок без ручной уборки.

![Windows](https://img.shields.io/badge/platform-Windows-0078D6)
![Python](https://img.shields.io/badge/python-3.10+-3776AB)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/github/v/release/printHESOYAM/screen-clean?label=release)

---

## GitHub About (copy-paste)

**Description (EN):**
```
Automatic desktop organizer for Windows. Moves old files to an archive folder, sorts by type, runs in the system tray. EN/RU/ES/JA.
```

**Description (RU):**
```
Автосортировка рабочего стола для Windows. Переносит файлы в архив, сортирует по типу, работает в трее. Языки: EN/RU/ES/JA.
```

**Website:** `https://github.com/printHESOYAM/screen-clean/releases/latest`

**Topics:** `windows` `desktop` `productivity` `python` `pywebview` `system-tray` `file-organizer` `desktop-cleaner`

---

## English

### What is Screen Clean?

Screen Clean is a lightweight Windows utility that monitors your desktop and automatically moves files to a destination folder after a delay you choose (1 hour to 7 days). Optionally, files are grouped into subfolders by type — images, documents, code, video, and more.

The app lives in the **system tray**, starts with Windows if you want, and opens a modern settings window with dark/light themes.

### Download

[Latest release](https://github.com/printHESOYAM/screen-clean/releases/latest)

| File | Description |
|---|---|
| **ScreenClean-Setup.exe** | Recommended — installer, Start menu, uninstaller |
| **ScreenClean.exe** | Portable — single file, no install |

**Requirements:** Windows 10/11, [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)

> **SmartScreen:** the app is not code-signed yet. If Windows shows a warning, click **More info → Run anyway**.

### Features

- Scheduled auto-clean (1 h – 7 days)
- Sort by file type into subfolders
- System tray + background worker
- Launch at Windows startup
- Exclusion list (skip specific names)
- **Frameless settings window** — custom title bar, drag to move, minimize / hide to tray
- **Smart archive path** — remembers folder in config; if you move the archive manually, Screen Clean finds it **across all drives** by folder name + category structure; recreates on the same drive if deleted
- **Safe paths** — normalizes broken Desktop paths (invisible space characters on Windows)
- Scans user + Public Desktop (shortcuts on shared desktop)
- Dark / light theme
- Languages: **EN**, **RU**, **ES**, **JA**
- Optional anonymous analytics (opt-out in settings)
- BTC / USDT TRC20 donate button in the app

### How it works

1. You pick an **archive folder** anywhere (e.g. `D:\Archive` or `Desktop\Archive`)
2. Files stay on the desktop for the **delay** you set
3. After that, Screen Clean moves them — optionally into category subfolders
4. Stats show how many files were moved in the last 24 hours

### Archive folder

- Path is stored in `%APPDATA%\DesktopCleaner\config.json` (`target_folder` + `archive_name`)
- **Move archive in Explorer** → app detects new location on next clean / when opening settings (search: profile folders → same drive → all drives; skips `Windows`, `Program Files`, etc.)
- **Pick path in settings** → works as before
- **Delete archive** → empty folder recreated on the **same drive** as before (e.g. `D:\Archive`)
- Use a **distinct folder name** (e.g. `ScreenClean-Archive`) if you have many folders named `Archive` on one disk

### Run from source

```powershell
pip install -r requirements.txt
python desktop_cleaner.py
```

### Build

```powershell
pip install -r requirements.txt pyinstaller
pyinstaller DesktopCleaner.spec
python installer/generate_assets.py
# Optional installer (Inno Setup 6):
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" installer\ScreenClean.iss
```

### Privacy

- Settings: `%APPDATA%\DesktopCleaner\config.json`
- Stats: `%APPDATA%\DesktopCleaner\stats.json`
- Analytics (if enabled): anonymous events only — app version, OS, language, feature toggles. **No file names or paths.**

---

## Русский

### Что такое Screen Clean?

Screen Clean — лёгкая утилита для Windows, которая следит за рабочим столом и **автоматически переносит файлы** в выбранную папку-архив через заданное время (от 1 часа до 7 дней). По желанию файлы раскладываются **по типу** — картинки, документы, код, видео и т.д.

Приложение работает в **системном трее**, может запускаться с Windows и открывает окно настроек в тёмной или светлой теме.

### Скачать

[Последний релиз](https://github.com/printHESOYAM/screen-clean/releases/latest)

| Файл | Описание |
|---|---|
| **ScreenClean-Setup.exe** | Рекомендуется — установщик, меню «Пуск», удаление через Windows |
| **ScreenClean.exe** | Portable — один файл, без установки |

**Требования:** Windows 10/11, [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)

> **SmartScreen:** приложение пока без платной подписи. Если Windows предупреждает — **Подробнее → Выполнить в любом случае**.

### Возможности

- Автоочистка по расписанию (1 ч – 7 дней)
- Сортировка по типу файлов в подпапки
- Работа в трее в фоне
- Автозапуск с Windows
- Список исключений
- **Окно без системной рамки** — своя шапка, перетаскивание, свернуть / в трей
- **Умный путь архива** — запоминает папку в конфиге; если перенесли вручную, ищет **по всем дискам** по имени и структуре подпапок; при удалении создаёт заново на том же диске
- **Безопасные пути** — исправляет битые пути Desktop (невидимые символы в имени папки)
- Сканирует личный и общий рабочий стол (Public Desktop)
- Тёмная / светлая тема
- Языки: **EN**, **RU**, **ES**, **JA**
- Анонимная аналитика (можно отключить в настройках)
- Кнопка доната BTC / USDT TRC20

### Как это работает

1. Выбираешь **папку-архив** где угодно (например `D:\Архив` или `Desktop\Archive`)
2. Файлы остаются на столе заданное **время**
3. После этого Screen Clean переносит их — при желании в подпапки по категориям
4. В интерфейсе видно, сколько файлов перенесено за 24 часа

### Папка-архив

- Путь хранится в `%APPDATA%\DesktopCleaner\config.json` (`target_folder` + `archive_name`)
- **Перенесли папку в Проводнике** → программа найдёт новое место при очистке / открытии настроек (поиск: профиль → тот же диск → все диски; пропускает `Windows`, `Program Files` и т.д.)
- **Выбрали путь в настройках** → как раньше
- **Удалили архив** → создастся пустая папка на **том же диске** (например `D:\Архив`)
- Лучше **уникальное имя** папки (`ScreenClean-Archive`), если на диске много папок «Архив»

### Запуск из исходников

```powershell
pip install -r requirements.txt
python desktop_cleaner.py
```

### Сборка

```powershell
pip install -r requirements.txt pyinstaller
pyinstaller DesktopCleaner.spec
python installer/generate_assets.py
# Установщик (Inno Setup 6):
& "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" installer\ScreenClean.iss
```

### Конфиденциальность

- Настройки: `%APPDATA%\DesktopCleaner\config.json`
- Статистика: `%APPDATA%\DesktopCleaner\stats.json`
- Аналитика (если включена): только анонимные события — версия, ОС, язык, настройки. **Без имён файлов и путей.**

---

## Changelog / История версий

### v3.1

- Frameless window + title bar drag (`scDrag` bridge)
- Archive auto-discovery after manual move (all drives)
- Path normalization for invisible Desktop folder names
- Public Desktop scanning; PSD and more image formats

### v3.0

- Initial public release (Screen Clean rebrand, i18n, telemetry, installer)

---

## Project structure / Структура

```
desktop_cleaner.py   — main app (tray, logic, pywebview, archive resolver)
desktop_state.py   — tracks file age on desktop
stats.py           — move statistics
telemetry.py       — optional anonymous analytics
index.html / style.css / app.js / i18n.js — settings UI
installer/         — Inno Setup script + wizard assets
assets/            — background images
```

## Author / Автор

**GitHub:** [printHESOYAM](https://github.com/printHESOYAM)

## License

MIT — see [LICENSE](LICENSE).
