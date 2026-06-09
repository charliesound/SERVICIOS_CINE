#!/usr/bin/env python3
"""
Diagnose database URL configuration across all config layers.

Prints the resolved DATABASE_URL from each layer and reports whether the
current configuration is PostgreSQL-only.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/opt/SERVICIOS_CINE")
os.chdir(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

POSTGRES_PREFIX = "postgresql+asyncpg://"


def print_header(title: str) -> None:
    print()
    print(f"{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def is_postgres_url(value: str | None) -> bool:
    return bool(value) and value.startswith(POSTGRES_PREFIX)


def print_postgres_status(label: str, value: str | None) -> None:
    if value:
        print(f"  {label}: {value}")
        print(f"  {label} postgres-only: {'yes' if is_postgres_url(value) else 'no'}")
    else:
        print(f"  {label}: (not set)")


def main() -> int:
    print_header("1. ENVIRONMENT")
    env_val = os.getenv("DATABASE_URL")
    print_postgres_status("os.environ['DATABASE_URL']", env_val)

    print_header("2. PYDANTIC SETTINGS (core.config)")
    try:
        from core.config import get_settings, reload_settings

        reload_settings()
        settings = get_settings()
        print_postgres_status("settings.database_url", settings.database_url)
    except Exception as exc:
        print(f"  ERROR: {exc}")

    print_header("3. LEGACY CONFIG (config.py)")
    try:
        from config import get_database_url, get_database_settings

        legacy_url = get_database_url()
        print_postgres_status("get_database_url()", legacy_url)
        legacy_settings = get_database_settings()
        print_postgres_status("get_database_settings()['url']", legacy_settings.get("url"))
    except Exception as exc:
        print(f"  ERROR: {exc}")

    print_header("4. RUNTIME RESOLUTION (database.py)")
    try:
        from database import DATABASE_URL

        print_postgres_status("database.DATABASE_URL", DATABASE_URL)
    except Exception as exc:
        print(f"  ERROR: {exc}")

    print_header("5. OVERALL DIAGNOSTIC")
    candidates: list[tuple[str, str | None]] = []

    candidates.append(("os.environ['DATABASE_URL']", env_val))

    try:
        from core.config import get_settings

        settings = get_settings()
        candidates.append(("settings.database_url", settings.database_url))
    except Exception:
        pass

    try:
        from config import get_database_url

        candidates.append(("get_database_url()", get_database_url()))
    except Exception:
        pass

    try:
        from database import DATABASE_URL

        candidates.append(("database.DATABASE_URL", DATABASE_URL))
    except Exception:
        pass

    postgres_hits = [name for name, value in candidates if is_postgres_url(value)]
    if not is_postgres_url(env_val):
        print("  CID requires postgresql+asyncpg:// DATABASE_URL.")

    if postgres_hits:
        print(f"  PostgreSQL-only sources: {', '.join(postgres_hits)}")
    else:
        print("  PostgreSQL-only sources: none")

    return 0


if __name__ == "__main__":
    sys.exit(main())
