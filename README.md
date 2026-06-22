# Screen Clean

Automatic desktop sorting for Windows. Moves old files from your desktop into an archive folder, optionally grouped by type (images, documents, code, etc.).

![Windows](https://img.shields.io/badge/platform-Windows-0078D6)
![Python](https://img.shields.io/badge/python-3.10+-3776AB)
![License](https://img.shields.io/badge/license-MIT-green)

## Download

Get the latest **`ScreenClean.exe`** from [Releases](https://github.com/printHESOYAM/screen-clean/releases/latest).

**Requirements:** Windows 10/11, [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/) (pre-installed on most systems).

## Features

- Auto-clean on a schedule (1 hour – 7 days)
- Sort by file type into subfolders
- System tray — runs in the background
- Launch at Windows startup
- Exclusion list
- Dark / light theme
- Languages: **EN**, **RU**, **ES**, **JA**

## Quick start (from source)

```powershell
pip install -r requirements.txt
python desktop_cleaner.py
```

The tray icon appears. Double-click or open **Settings** from the menu to configure the app.

## Build `.exe`

```powershell
pip install -r requirements.txt pyinstaller
pyinstaller DesktopCleaner.spec
```

Output: `dist/ScreenClean.exe`

### Optional: analytics in release builds

Set environment variables before building (or add them as GitHub Actions secrets):

```powershell
$env:SCREENCLEAN_TELEMETRY_URL = "https://us.i.posthog.com/capture/"
$env:SCREENCLEAN_TELEMETRY_KEY = "phc_your_project_key"
pyinstaller DesktopCleaner.spec
```

Users can disable analytics anytime in **Settings → Anonymous analytics**.

## Data stored locally

```
%APPDATA%\DesktopCleaner\config.json    — settings
%APPDATA%\DesktopCleaner\stats.json     — file move history
%APPDATA%\DesktopCleaner\telemetry.json — local analytics counters
```

## Anonymous analytics

When enabled, the app sends anonymous usage events (app version, OS version, UI language, feature toggles, clean counts). No file names, paths, or personal data.

Disable in the app settings or set `"telemetry_enabled": false` in `config.json`.

## Project structure

```
desktop_cleaner.py   — main app (tray, cleaner logic, pywebview UI)
desktop_state.py     — tracks when files appeared on desktop
stats.py             — move statistics
telemetry.py         — optional anonymous analytics
index.html / style.css / app.js / i18n.js — settings window UI
assets/              — background images
```

## Release on GitHub

1. Push code to a public repository
2. Add secrets (optional): `SCREENCLEAN_TELEMETRY_URL`, `SCREENCLEAN_TELEMETRY_KEY`
3. Create and push a tag:

```powershell
git tag v3.0.0
git push origin v3.0.0
```

GitHub Actions builds `ScreenClean.exe` and attaches it to the release automatically.

## License

MIT — see [LICENSE](LICENSE).
