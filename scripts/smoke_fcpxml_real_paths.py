from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_fcpxml_real_paths.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal, Base, engine
import models.matcher  # noqa: F401
from models.core import Organization, Project, User
from models.storage import MediaAsset, MediaAssetType
from routes.editorial_routes import _build_editorial_export_bundle
from services.assembly_service import assembly_service
from services.editorial_reconciliation_service import editorial_reconciliation_service
from services.report_service import report_service
from services.script_intake_service import analysis_service
from services.take_scoring_service import take_scoring_service


SCRIPT_TEXT = """
INT. STUDIO - DAY
ANA opens the slate and waits for cue.

EXT. ALLEY - NIGHT
ANA runs past the wall with the recorder in hand.
""".strip()


async def setup_editorial_project(db_name: str = "smoke_fcpxml_real_paths.db") -> dict:
    db_path = ROOT / db_name
    if db_path.exists():
        db_path.unlink()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    smoke_dir = ROOT / "tmp" / "editorial_real_paths"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    video_path = smoke_dir / "scene_1_shot_1_take_1.mov"
    audio_path = smoke_dir / "scene_1_shot_1_take_1.wav"
    video_path.write_bytes(b"real-path-video")
    with open(audio_path, "wb") as file_handle:
        file_handle.write(b"RIFF$\x00\x00\x00WAVEfmt ")

    async with AsyncSessionLocal() as session:
        org = Organization(id=uuid.uuid4().hex, name="Editorial Real Paths Org")
        user = User(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            username="editorial_real_paths",
            email=f"editorial-real-paths-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="smoke",
            role="admin",
            billing_plan="studio",
        )
        project = Project(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            name=f"Editorial Real Paths {uuid.uuid4().hex[:6]}",
            description="Smoke test for real path fcpxml",
            script_text=SCRIPT_TEXT,
        )
        session.add_all([org, user, project])
        await session.commit()

        await analysis_service.run_analysis(session, project.id, org.id, SCRIPT_TEXT)

        media_assets = [
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=video_path.name,
                relative_path=video_path.name,
                canonical_path=str(video_path),
                content_ref=video_path.as_uri(),
                file_extension="mov",
                asset_type=MediaAssetType.VIDEO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 1, "fps": 24, "duration_frames": 96, "start_timecode": "01:00:00:00", "end_timecode": "01:00:04:00", "file_path": str(video_path)}),
            ),
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=audio_path.name,
                relative_path=audio_path.name,
                canonical_path=str(audio_path),
                content_ref=audio_path.as_uri(),
                file_extension="wav",
                asset_type=MediaAssetType.AUDIO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 1, "fps": 24, "duration_frames": 96, "sample_rate": 48000, "channels": 2, "possible_timecode": "01:00:00:00", "file_path": str(audio_path)}),
            ),
        ]
        session.add_all(media_assets)
        await session.commit()

        await report_service.create_report(
            session,
            "camera",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "take_reference": "1", "camera_label": "A Cam", "card_or_mag": "A001", "media_asset_id": media_assets[0].id, "notes": "usable"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "sound",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "sound_roll": "S001", "media_asset_id": media_assets[1].id, "timecode_notes": "take 1 01:00:00:00", "notes": "clean"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "script",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "best_take": "1", "continuity_notes": "preferred"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "director",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "preferred_take": "1", "intention_note": "base take"},
            user_org_id=org.id,
            created_by=user.id,
        )

        await editorial_reconciliation_service.reconcile_project(session, project=project)
        await take_scoring_service.score_project_takes(session, project_id=project.id)
        assembly = await assembly_service.generate_assembly(
            session,
            project_id=project.id,
            organization_id=org.id,
            created_by=user.id,
        )
        return {
            "project": project,
            "organization_id": org.id,
            "assembly": assembly,
            "assets": media_assets,
            "smoke_dir": smoke_dir,
        }


async def main() -> None:
    setup = await setup_editorial_project()
    project = setup["project"]
    assembly = setup["assembly"]
    smoke_dir = setup["smoke_dir"]

    async with AsyncSessionLocal() as session:
        export_bundle = await _build_editorial_export_bundle(session, project=project, payload=assembly)
    fcpxml_bytes = export_bundle["file_bytes"]
    file_name = export_bundle["file_name"]
    manifest = export_bundle["manifest"]
    xml_path = smoke_dir / file_name
    xml_path.write_bytes(fcpxml_bytes)
    xml_text = xml_path.read_text(encoding="utf-8")
    if 'src="file:///tmp/' in xml_text:
        raise RuntimeError("FCPXML still contains /tmp fallback despite real paths")
    validation = export_bundle["validation"]
    if not validation["valid"]:
        raise RuntimeError(f"FCPXML validation failed: {validation['errors']}")
    print(json.dumps(
        {
            "project_id": project.id,
            "fcpxml_path": str(xml_path),
            "manifest": manifest,
            "validation": validation,
            "media_relink_report": export_bundle["media_relink_report"],
        },
        ensure_ascii=False,
        indent=2,
        default=str,
    ))


if __name__ == "__main__":
    asyncio.run(main())
