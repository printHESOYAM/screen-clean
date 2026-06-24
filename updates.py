"""
updates.py — проверка новых релизов на GitHub.
"""

import json
import re
import urllib.error
import urllib.request

GITHUB_REPO = "printHESOYAM/screen-clean"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
REQUEST_TIMEOUT = 8


def parse_version(raw: str) -> tuple[int, ...]:
    """Parse 'v3.1.0' or '3.1' into (3, 1, 0)."""
    if not raw:
        return (0,)
    cleaned = raw.strip().lstrip("vV")
    parts: list[int] = []
    for segment in cleaned.split("."):
        match = re.match(r"(\d+)", segment)
        if not match:
            break
        parts.append(int(match.group(1)))
    return tuple(parts) if parts else (0,)


def version_gt(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    length = max(len(left), len(right))
    left_padded = left + (0,) * (length - len(left))
    right_padded = right + (0,) * (length - len(right))
    return left_padded > right_padded


def _pick_download_url(release: dict) -> str:
    for asset in release.get("assets") or []:
        name = (asset.get("name") or "").lower()
        if name.endswith(".exe") or name.endswith(".msi"):
            url = asset.get("browser_download_url")
            if url:
                return url
    return release.get("html_url") or ""


def fetch_latest_release() -> dict | None:
    req = urllib.request.Request(
        GITHUB_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ScreenClean-UpdateCheck",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def check_for_updates(current_version: str, dismissed_version: str = "") -> dict:
    current = current_version or "0"
    result = {
        "available": False,
        "current": current,
        "latest": current,
        "tag": "",
        "url": "",
        "dismissed": False,
        "error": None,
    }

    release = fetch_latest_release()
    if not release:
        result["error"] = "fetch_failed"
        return result

    tag = (release.get("tag_name") or "").strip()
    latest = tag.lstrip("vV") if tag else current
    result["latest"] = latest
    result["tag"] = tag
    result["url"] = _pick_download_url(release)

    if not version_gt(parse_version(latest), parse_version(current)):
        return result

    result["available"] = True
    if dismissed_version and parse_version(dismissed_version) >= parse_version(latest):
        result["dismissed"] = True
    return result
