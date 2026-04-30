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

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_editorial_mvp.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal, Base, engine
import models.matcher  # noqa: F401
from models.core import Organization, Project, User
from models.storage import MediaAsset, MediaAssetType
from services.script_intake_service import analysis_service
from services.report_service import report_service
from services.editorial_reconciliation_service import editorial_reconciliation_service
from services.take_scoring_service import take_scoring_service
from services.assembly_service import assembly_service
from services.fcpxml_export_service import fcpxml_export_service


SCRIPT_TEXT = """
INT. CAFE - DAY
MARTA sits with a folder and watches the door.
LUIS enters and smiles.

EXT. STREET - NIGHT
MARTA and LUIS cross the avenue in silence.

INT. OFFICE - NIGHT
They review the evidence and whisper about the next move.
""".strip()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    smoke_dir = ROOT / "tmp" / "editorial_smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as session:
        org = Organization(id=uuid.uuid4().hex, name="Editorial Smoke Org")
        user = User(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            username="editorial_smoke",
            email=f"editorial-smoke-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="smoke",
            role="admin",
            billing_plan="studio",
        )
        project = Project(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            name=f"Editorial Smoke {uuid.uuid4().hex[:6]}",
            description="Smoke test project",
            script_text=SCRIPT_TEXT,
        )
        session.add_all([org, user, project])
        await session.commit()

        analysis = await analysis_service.run_analysis(session, project.id, org.id, SCRIPT_TEXT)
        print("1. analysis", json.dumps(analysis, ensure_ascii=False))

        video_a = smoke_dir / "scene_1_shot_1_take_1.mov"
        video_b = smoke_dir / "scene_1_shot_1_take_2.mov"
        audio_a = smoke_dir / "scene_1_shot_1_take_1.wav"
        audio_b = smoke_dir / "scene_1_shot_1_take_2.wav"
        for path in (video_a, video_b, audio_a, audio_b):
            path.write_bytes(b"smoke")

        media_assets = [
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=video_a.name,
                relative_path=video_a.name,
                canonical_path=str(video_a),
                file_extension="mov",
                asset_type=MediaAssetType.VIDEO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 1, "fps": 24, "duration_frames": 96, "start_timecode": "01:00:00:00", "end_timecode": "01:00:04:00", "camera_roll": "A001"}),
            ),
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=video_b.name,
                relative_path=video_b.name,
                canonical_path=str(video_b),
                file_extension="mov",
                asset_type=MediaAssetType.VIDEO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 2, "fps": 24, "duration_frames": 120, "start_timecode": "01:00:10:00", "end_timecode": "01:00:15:00", "camera_roll": "A001"}),
            ),
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=audio_a.name,
                relative_path=audio_a.name,
                canonical_path=str(audio_a),
                file_extension="wav",
                asset_type=MediaAssetType.AUDIO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 1, "fps": 24, "duration_frames": 96, "sound_roll": "S001"}),
            ),
            MediaAsset(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                project_id=project.id,
                storage_source_id=None,
                watch_path_id=None,
                ingest_scan_id=None,
                file_name=audio_b.name,
                relative_path=audio_b.name,
                canonical_path=str(audio_b),
                file_extension="wav",
                asset_type=MediaAssetType.AUDIO,
                metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 2, "fps": 24, "duration_frames": 120, "sound_roll": "S001"}),
            ),
        ]
        session.add_all(media_assets)
        await session.commit()
        print("2. media_assets", len(media_assets))

        await report_service.create_report(
            session,
            "camera",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "take_reference": "1", "camera_label": "A Cam", "card_or_mag": "A001", "media_asset_id": media_assets[0].id, "notes": "focus issue"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "camera",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "take_reference": "2", "camera_label": "A Cam", "card_or_mag": "A001", "media_asset_id": media_assets[1].id, "notes": "camera ok"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "sound",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "sound_roll": "S001", "media_asset_id": media_assets[2].id, "timecode_notes": "take 1 01:00:00:00", "notes": "rf noise"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "sound",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "sound_roll": "S001", "media_asset_id": media_assets[3].id, "timecode_notes": "take 2 01:00:10:00", "notes": "clean"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "script",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "best_take": "2", "continuity_notes": "circled take"},
            user_org_id=org.id,
            created_by=user.id,
        )
        await report_service.create_report(
            session,
            "director",
            {"project_id": project.id, "scene_id": "1", "shot_id": "1", "preferred_take": "2", "intention_note": "best energy"},
            user_org_id=org.id,
            created_by=user.id,
        )
        print("3. reports created")

        reconcile = await editorial_reconciliation_service.reconcile_project(session, project=project)
        print("4. reconcile", json.dumps(reconcile, ensure_ascii=False))

        score = await take_scoring_service.score_project_takes(session, project_id=project.id)
        print("5. score", json.dumps(score, ensure_ascii=False))

        assembly = await assembly_service.generate_assembly(
            session,
            project_id=project.id,
            organization_id=org.id,
            created_by=user.id,
        )
        print("6. assembly_items", assembly["items_created"])

        fcpxml_bytes, file_name, manifest = fcpxml_export_service.build_fcpxml(
            project_name=project.name,
            assembly_cut=assembly,
        )
        xml_path = smoke_dir / file_name
        xml_path.write_bytes(fcpxml_bytes)
        xml_text = xml_path.read_text(encoding="utf-8")
        if "<fcpxml" not in xml_text or "<asset-clip" not in xml_text:
            raise RuntimeError("FCPXML structure validation failed")
        print("7. fcpxml", json.dumps({"path": str(xml_path), "manifest": manifest}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
