"""
Тестовый запуск Screen Clean с версией 3.0 — чтобы сработало уведомление о v3.1.0.

Использование:
  python scripts/test_update_notify.py

Перед запуском закройте Screen Clean в трее, если он уже работает.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import telemetry
import desktop_cleaner

TEST_VERSION = "3.0"

telemetry.APP_VERSION = TEST_VERSION
desktop_cleaner.APP_VERSION = TEST_VERSION

if __name__ == "__main__":
    print(f"[test] Screen Clean запущен как v{TEST_VERSION} — ждите balloon через ~5 сек")
    desktop_cleaner.main()
