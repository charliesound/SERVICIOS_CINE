from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.app import app
from src.settings import settings


def main() -> int:
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    required_official_paths = {
        "/api/health",
        "/api/health/details",
        "/api/config",
        "/api/storage/summary",
        "/api/storage/project",
        "/api/storage/shots",
        "/api/shots",
        "/api/render/jobs",
        "/api/render/jobs/{job_id}/retry",
        "/api/ops/status",
    }

    missing = sorted(required_official_paths - paths)
    if missing:
        print("SMOKE_FAIL missing official paths:")
        for path in missing:
            print(f"- {path}")
        return 1

    legacy_paths = {"/projects", "/scenes", "/shots", "/jobs"}

    if not settings.enable_legacy_routes:
        still_present = sorted(legacy_paths & paths)
        if still_present:
            print("SMOKE_FAIL legacy paths are enabled but should be disabled:")
            for path in still_present:
                print(f"- {path}")
            return 1

    print("SMOKE_OK official routes loaded")
    print(f"SMOKE_INFO enable_legacy_routes={settings.enable_legacy_routes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
