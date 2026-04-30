from __future__ import annotations

import asyncio
import json
import os
import struct
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_dual_system_reconcile.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal, Base, engine
import models.matcher  # noqa: F401
from models.core import Organization, Project, User
from models.postproduction import Take
from models.storage import MediaAsset, MediaAssetType
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
    db_path = ROOT / "smoke_dual_system_reconcile.db"
    if db_path.exists():
        db_path.unlink()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    smoke_dir = ROOT / "tmp" / "smoke_dual_system_reconcile"
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
            email=f"dual-system-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="smoke",
            role="admin",
            billing_plan="studio",
        )
        project = Project(id=uuid.uuid4().hex, organization_id=org.id, name="Dual System Reconcile")
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

        reconcile = await editorial_reconciliation_service.reconcile_project(session, project=project)
        score = await take_scoring_service.score_project_takes(session, project_id=project.id)

        take_result = await session.execute(select(Take).where(Take.project_id == project.id))
        take = take_result.scalars().first()
        assert take is not None
        assert take.camera_media_asset_id == camera_asset.id
        assert take.sound_media_asset_id == sound_asset.id
        assert take.sync_method == "ixml_scene_take", take.sync_method
        assert take.sync_confidence and take.sync_confidence >= 0.9, take.sync_confidence
        assert take.audio_metadata_status == "parsed", take.audio_metadata_status
        assert take.dual_system_status == "matched", take.dual_system_status
        assert take.is_recommended is True
        assert "sync ixml scene take" in (take.recommended_reason or "").lower(), take.recommended_reason

        print(
            json.dumps(
                {
                    "status": "PASS",
                    "reconcile": reconcile,
                    "score": score,
                    "take": {
                        "id": str(take.id),
                        "scene_number": take.scene_number,
                        "shot_number": take.shot_number,
                        "take_number": take.take_number,
                        "camera_media_asset_id": take.camera_media_asset_id,
                        "sound_media_asset_id": take.sound_media_asset_id,
                        "sync_method": take.sync_method,
                        "sync_confidence": take.sync_confidence,
                        "dual_system_status": take.dual_system_status,
                        "audio_metadata_status": take.audio_metadata_status,
                        "recommended_reason": take.recommended_reason,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    from sqlalchemy import select

    asyncio.run(main())
