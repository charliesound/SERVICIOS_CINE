from __future__ import annotations

import asyncio
import json
import os
import struct
import sys
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_dual_system_fcpxml.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal, Base, engine
import models.matcher  # noqa: F401
from models.core import Organization, Project, User
from models.postproduction import Take
from models.storage import MediaAsset, MediaAssetType
from routes.editorial_routes import _build_editorial_export_bundle
from services.assembly_service import assembly_service
from services.editorial_reconciliation_service import editorial_reconciliation_service
from services.take_scoring_service import take_scoring_service


def _chunk(chunk_id: bytes, payload: bytes) -> bytes:
    data = chunk_id + struct.pack("<I", len(payload)) + payload
    if len(payload) % 2 == 1:
        data += b"\x00"
    return data


def _wav_bytes() -> bytes:
    sample_rate = 48000
    channels = 2
    bits_per_sample = 16
    block_align = channels * 2
    byte_rate = sample_rate * block_align
    data_payload = b"\x00\x00" * channels * sample_rate
    fmt_payload = struct.pack("<HHIIHH", 1, channels, sample_rate, byte_rate, block_align, bits_per_sample)
    ixml = (
        "<BWFXML><PROJECT>CID</PROJECT><SCENE>1</SCENE><TAKE>1</TAKE><TAPE>SR001</TAPE>"
        "<CIRCLED>TRUE</CIRCLED><NOTE>clean boom</NOTE><START_TIMECODE>01:00:00:00</START_TIMECODE>"
        "<FRAME_RATE>24</FRAME_RATE></BWFXML>"
    ).encode("utf-8")
    riff_payload = b"WAVE" + _chunk(b"fmt ", fmt_payload) + _chunk(b"iXML", ixml) + _chunk(b"data", data_payload)
    return b"RIFF" + struct.pack("<I", len(riff_payload)) + riff_payload


async def main() -> None:
    db_path = ROOT / "smoke_dual_system_fcpxml.db"
    if db_path.exists():
        db_path.unlink()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    smoke_dir = ROOT / "tmp" / "smoke_dual_system_fcpxml"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    video_path = smoke_dir / "scene_1_shot_1_take_1.mov"
    audio_path = smoke_dir / "sound_roll_sr001_take_1.wav"
    video_path.write_bytes(b"dual-system-video")
    audio_path.write_bytes(_wav_bytes())

    async with AsyncSessionLocal() as session:
        org = Organization(id=uuid.uuid4().hex, name="CID Org")
        user = User(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            username="dual_system",
            email=f"dual-system-fcpxml-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="smoke",
            role="admin",
            billing_plan="studio",
        )
        project = Project(id=uuid.uuid4().hex, organization_id=org.id, name="Dual System FCPXML")
        session.add_all([org, user, project])
        await session.commit()

        camera_asset = MediaAsset(
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
            metadata_json=json.dumps({"scene_number": 1, "shot_number": 1, "take_number": 1, "fps": 24, "duration_frames": 96, "start_timecode": "01:00:00:00"}),
            file_size=video_path.stat().st_size,
        )
        sound_asset = MediaAsset(
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
            metadata_json=json.dumps({"sound_roll": "SR001"}),
            file_size=audio_path.stat().st_size,
        )
        session.add_all([camera_asset, sound_asset])
        await session.commit()

        await editorial_reconciliation_service.reconcile_project(session, project=project)
        await take_scoring_service.score_project_takes(session, project_id=project.id)
        assembly = await assembly_service.generate_assembly(
            session,
            project_id=project.id,
            organization_id=org.id,
            created_by=user.id,
        )
        export_bundle = await _build_editorial_export_bundle(session, project=project, payload=assembly)
        fcpxml_text = export_bundle["file_bytes"].decode("utf-8")
        xml_root = ET.fromstring(export_bundle["file_bytes"])
        asset_nodes = xml_root.findall(".//asset")
        relink_entries = export_bundle["media_relink_report"]["entries"]

        assert export_bundle["validation"]["valid"] is True, export_bundle["validation"]
        assert any("dual_system_audio_export_partial" == warning for warning in export_bundle["warnings"]), export_bundle["warnings"]
        assert len(asset_nodes) >= 2, len(asset_nodes)
        assert any(entry.get("role") == "audio" and entry.get("sync_method") for entry in relink_entries), relink_entries
        assert any(entry.get("dual_system_status") == "matched" for entry in relink_entries), relink_entries
        assert "_AUDIO" in fcpxml_text, fcpxml_text

        take_result = await session.execute(select(Take).where(Take.project_id == project.id))
        take = take_result.scalars().first()

        print(
            json.dumps(
                {
                    "status": "PASS",
                    "validation": export_bundle["validation"],
                    "warnings": export_bundle["warnings"],
                    "take": {
                        "sync_method": take.sync_method if take else None,
                        "dual_system_status": take.dual_system_status if take else None,
                    },
                    "media_relink_report": export_bundle["media_relink_report"],
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )


if __name__ == "__main__":
    from sqlalchemy import select

    asyncio.run(main())
