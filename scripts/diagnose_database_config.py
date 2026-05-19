#!/usr/bin/env python3
"""
Diagnose database URL configuration across all config layers.

Prints the resolved DATABASE_URL from each layer and the actual DB file state.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/opt/SERVICIOS_CINE")
os.chdir(str(PROJECT_ROOT))

sys.path.insert(0, str(PROJECT_ROOT / "src"))


SUPPORTED_PREFIXES = ("sqlite+aiosqlite:///", "sqlite:///")


def resolve_sqlite_path(database_url: str) -> Path | None:
    """Resolve a SQLite DATABASE_URL to an absolute Path regardless of format."""
    if not database_url:
        return None
    for prefix in SUPPORTED_PREFIXES:
        if database_url.startswith(prefix):
            raw = database_url[len(prefix):]
            if not raw:
                return None
            if os.path.isabs(raw):
                return Path(raw).resolve()
            return (PROJECT_ROOT / raw).resolve()
    return None


def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main() -> int:
    print_header("1. ENVIRONMENT")
    env_val = os.getenv("DATABASE_URL")
    print(f"  os.environ['DATABASE_URL']: {env_val or '(not set)'}")

    print_header("2. PYDANTIC SETTINGS (core.config)")
    try:
        from core.config import get_settings, reload_settings

        reload_settings()
        s = get_settings()
        print(f"  settings.database_url: {s.database_url}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print_header("3. LEGACY CONFIG (config.py)")
    try:
        from config import get_database_url, get_database_settings

        url = get_database_url()
        print(f"  get_database_url(): {url}")
        dbs = get_database_settings()
        print(f"  get_database_settings()['url']: {dbs.get('url')}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print_header("4. RUNTIME RESOLUTION (database.py)")
    try:
        from database import DATABASE_URL, IS_SQLITE

        print(f"  database.DATABASE_URL: {DATABASE_URL}")
        print(f"  database.IS_SQLITE: {IS_SQLITE}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print_header("5. RESOLVED SQLITE PATH")
    try:
        from config import get_database_url

        url = get_database_url()
        p = resolve_sqlite_path(url)
        if p:
            print(f"  Resolved path: {p}")
            print(f"  File exists:   {p.exists()}")
            print(f"  File size:     {p.stat().st_size if p.exists() else 'N/A'}")
            print(f"  Writable:      {os.access(str(p), os.W_OK) if p.exists() else 'N/A'}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print_header("6. CONFIG.YAML DEFAULT")
    try:
        import yaml
        yaml_path = PROJECT_ROOT / "src/config/config.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                data = yaml.safe_load(f) or {}
            db_cfg = data.get("database", {})
            print(f"  database.url: {db_cfg.get('url')}")
        else:
            print(f"  config.yaml not found at {yaml_path}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print_header("7. ALEMBIC RESOLUTION")
    alembic_url = None
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
        alembic_url = os.getenv("DATABASE_URL")
        print(f"  alembic DATABASE_URL (via load_dotenv): {alembic_url or '(not set)'}")
        p = resolve_sqlite_path(alembic_url)
        if p:
            print(f"  alembic resolved path: {p}")
            print(f"  File exists: {p.exists()}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── Collect URLs from all layers ──
    layers: dict[str, tuple[str | None, Path | None]] = {}

    try:
        from database import DATABASE_URL as r_url
        layers["Runtime (database)"] = (r_url, resolve_sqlite_path(r_url))
    except Exception:
        pass

    try:
        from core.config import get_settings
        s = get_settings()
        layers["Pydantic (settings)"] = (s.database_url, resolve_sqlite_path(s.database_url))
    except Exception:
        pass

    try:
        from config import get_database_url
        legacy_url = get_database_url()
        layers["Legacy (config.py)"] = (legacy_url, resolve_sqlite_path(legacy_url))
    except Exception:
        pass

    if alembic_url:
        layers["Alembic (load_dotenv)"] = (alembic_url, resolve_sqlite_path(alembic_url))

    print_header("8. SUMMARY")
    print(f"  {'Config layer':<22} | {'Raw URL'}")
    print(f"  {'-'*22}-+-{'-'*55}")
    for name, (raw, _resolved) in layers.items():
        display = (raw[:55] + "...") if raw and len(raw) > 55 else (raw or "N/A")
        print(f"  {name:<22} | {display}")

    print()
    resolved_paths = [rp for _, rp in layers.values() if rp is not None]
    if resolved_paths:
        first = resolved_paths[0]
        all_match = all(rp == first for rp in resolved_paths)
        if all_match:
            print(f"  ✅ ALIGNMENT OK — all layers resolve to: {first}")
        else:
            print(f"  ❌ MISALIGNMENT — layers resolve to different paths:")
            for name, (_raw, rp) in layers.items():
                print(f"     {name:<22} → {rp or 'N/A'}")
    else:
        print("  ⚠️  Could not resolve any SQLite path from loaded layers")

    return 0


if __name__ == "__main__":
    sys.exit(main())
