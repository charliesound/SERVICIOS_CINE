from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_editorial_package.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal
from routes.editorial_routes import _build_editorial_export_bundle, _build_editorial_package_bytes
from smoke_fcpxml_real_paths import setup_editorial_project


async def main() -> None:
    setup = await setup_editorial_project(db_name="smoke_editorial_package.db")
    project = setup["project"]
    assembly = setup["assembly"]
    smoke_dir = setup["smoke_dir"]

    async with AsyncSessionLocal() as session:
        export_bundle = await _build_editorial_export_bundle(session, project=project, payload=assembly)
    validation = export_bundle["validation"]
    if not validation["valid"]:
        raise RuntimeError(f"Invalid FCPXML for package smoke: {validation['errors']}")

    archive_path = smoke_dir / f"{project.name.replace(' ', '_')}_editorial_package.zip"
    archive_path.write_bytes(_build_editorial_package_bytes(project=project, export_bundle=export_bundle, recommended_takes=[]))

    with zipfile.ZipFile(archive_path, "r") as archive:
        names = sorted(archive.namelist())
    required = {
        "assembly.fcpxml",
        "assembly_summary.json",
        "media_relink_report.json",
        "recommended_takes.json",
        "editorial_notes.txt",
    }
    if not required.issubset(set(names)):
        raise RuntimeError(f"Missing package entries: {sorted(required.difference(set(names)))}")

    print(json.dumps({"zip_path": str(archive_path), "entries": names}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
