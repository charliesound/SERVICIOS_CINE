from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageDraw


DEFAULT_DB_PATH = Path("/opt/SERVICIOS_CINE/ailinkcinema_s2.db")
DEFAULT_PROJECT_ID = "32fb858f66ef4569a7bc12db3b5ef2fd"
DEFAULT_ORGANIZATION_ID = "db4d7a5dadc9457ebaa2993a30d48201"
DEFAULT_STORAGE_SOURCE_ID = "d7fac025-fa34-487d-a83a-d81ce2aadcac"
DEFAULT_PROJECT_ROOT = Path("/opt/SERVICIOS_CINE/data/smoke_tenant_A/project_alpha")
DEFAULT_STORYBOARD_DIR = DEFAULT_PROJECT_ROOT / "storyboard"


@dataclass(frozen=True)
class VisualAssetSpec:
    asset_id: str
    file_name: str
    shot_order: int
    shot_type: str
    color: tuple[int, int, int]
    title: str


VISUAL_ASSET_SPECS = (
    VisualAssetSpec(
        asset_id="157c1828-990c-44e8-91c9-610fa3f12bf5",
        file_name="seqA_shot01.png",
        shot_order=1,
        shot_type="wide",
        color=(30, 76, 140),
        title="Sequence A / Shot 1",
    ),
    VisualAssetSpec(
        asset_id="05f375ba-53d8-40dc-a2b9-d82d40e08a67",
        file_name="seqA_shot02.png",
        shot_order=2,
        shot_type="close_up",
        color=(154, 52, 87),
        title="Sequence A / Shot 2",
    ),
)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _build_metadata(spec: VisualAssetSpec) -> str:
    return json.dumps(
        {
            "sequence_id": "SEQ_A",
            "shot_order": spec.shot_order,
            "shot_type": spec.shot_type,
            "visual_mode": "storyboard",
            "prompt_summary": f"Smoke storyboard frame {spec.shot_order} for visual validation",
        }
    )


def _ensure_fixture_image(path: Path, spec: VisualAssetSpec) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return

    image = Image.new("RGB", (1280, 720), color=spec.color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 1240, 680), outline=(245, 245, 245), width=8)
    draw.text((90, 90), spec.title, fill=(255, 255, 255))
    draw.text((90, 150), "Smoke visual validation asset", fill=(255, 255, 255))
    image.save(path)


def ensure_visual_smoke_assets(
    *,
    db_path: Path = DEFAULT_DB_PATH,
    project_id: str = DEFAULT_PROJECT_ID,
    organization_id: str = DEFAULT_ORGANIZATION_ID,
    storage_source_id: str = DEFAULT_STORAGE_SOURCE_ID,
    project_root: Path = DEFAULT_PROJECT_ROOT,
) -> list[dict[str, str]]:
    storyboard_dir = project_root / "storyboard"
    results: list[dict[str, str]] = []

    connection = sqlite3.connect(str(db_path))
    try:
        cursor = connection.cursor()
        for spec in VISUAL_ASSET_SPECS:
            file_path = storyboard_dir / spec.file_name
            _ensure_fixture_image(file_path, spec)

            relative_path = str(file_path.relative_to(project_root))
            stat = file_path.stat()
            modified_at = datetime.fromtimestamp(stat.st_mtime, UTC).isoformat()
            metadata_json = _build_metadata(spec)
            discovered_at = _utc_now_iso()
            created_at = _utc_now_iso()

            cursor.execute("SELECT id FROM media_assets WHERE id = ?", (spec.asset_id,))
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO media_assets (
                        id, organization_id, project_id, storage_source_id, watch_path_id,
                        ingest_scan_id, file_name, relative_path, canonical_path, file_extension,
                        mime_type, asset_type, metadata_json, file_size, modified_at, discovered_at,
                        created_at, status, created_by, job_id, asset_source, content_ref
                    ) VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, NULL)
                    """,
                    (
                        spec.asset_id,
                        organization_id,
                        project_id,
                        storage_source_id,
                        spec.file_name,
                        relative_path,
                        str(file_path),
                        file_path.suffix,
                        "image/png",
                        "image",
                        metadata_json,
                        stat.st_size,
                        modified_at,
                        discovered_at,
                        created_at,
                        "indexed",
                        "smoke_visual_validation",
                    ),
                )
            else:
                cursor.execute(
                    """
                    UPDATE media_assets
                    SET organization_id = ?,
                        project_id = ?,
                        storage_source_id = ?,
                        watch_path_id = NULL,
                        ingest_scan_id = NULL,
                        file_name = ?,
                        relative_path = ?,
                        canonical_path = ?,
                        file_extension = ?,
                        mime_type = ?,
                        asset_type = ?,
                        metadata_json = ?,
                        file_size = ?,
                        modified_at = ?,
                        discovered_at = COALESCE(discovered_at, ?),
                        created_at = COALESCE(created_at, ?),
                        status = 'indexed',
                        created_by = NULL,
                        job_id = NULL,
                        asset_source = ?,
                        content_ref = NULL
                    WHERE id = ?
                    """,
                    (
                        organization_id,
                        project_id,
                        storage_source_id,
                        spec.file_name,
                        relative_path,
                        str(file_path),
                        file_path.suffix,
                        "image/png",
                        "image",
                        metadata_json,
                        stat.st_size,
                        modified_at,
                        discovered_at,
                        created_at,
                        "smoke_visual_validation",
                        spec.asset_id,
                    ),
                )

            results.append(
                {
                    "asset_id": spec.asset_id,
                    "file_name": spec.file_name,
                    "canonical_path": str(file_path),
                    "relative_path": relative_path,
                }
            )

        connection.commit()
        return results
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed reproducible presentation visual smoke assets")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--organization-id", default=DEFAULT_ORGANIZATION_ID)
    parser.add_argument("--storage-source-id", default=DEFAULT_STORAGE_SOURCE_ID)
    parser.add_argument("--project-root", default=str(DEFAULT_PROJECT_ROOT))
    args = parser.parse_args()

    results = ensure_visual_smoke_assets(
        db_path=Path(args.db_path),
        project_id=args.project_id,
        organization_id=args.organization_id,
        storage_source_id=args.storage_source_id,
        project_root=Path(args.project_root),
    )
    for row in results:
        print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
