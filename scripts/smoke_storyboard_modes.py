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

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_storyboard_modes.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from database import AsyncSessionLocal, Base, engine
import models.matcher  # noqa: F401
from models.core import Organization, Project, User
from schemas.auth_schema import TenantContext
from services.script_intake_service import analysis_service
from services.storyboard_service import storyboard_service, StoryboardGenerationMode


SCRIPT_TEXT = """
INT. APARTMENT - DAY
ANA wakes up and checks a hidden phone.

EXT. PARK - DAY
ANA meets BRUNO near the lake and passes an envelope.

INT. GARAGE - NIGHT
BRUNO opens the envelope and discovers the key.

EXT. ROOFTOP - NIGHT
ANA watches the skyline and prepares for the escape.
""".strip()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        org = Organization(id=uuid.uuid4().hex, name="Storyboard Smoke Org")
        user = User(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            username="storyboard_smoke",
            email=f"storyboard-smoke-{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="smoke",
            role="admin",
            billing_plan="studio",
        )
        project = Project(
            id=uuid.uuid4().hex,
            organization_id=org.id,
            name=f"Storyboard Smoke {uuid.uuid4().hex[:6]}",
            description="Storyboard mode smoke test",
            script_text=SCRIPT_TEXT,
        )
        session.add_all([org, user, project])
        await session.commit()

        await analysis_service.run_analysis(session, project.id, org.id, SCRIPT_TEXT)
        tenant = TenantContext(user_id=user.id, organization_id=org.id, plan="studio", role="admin", is_admin=True)

        sequences = await storyboard_service.list_storyboard_sequences(session, project_id=project.id, tenant=tenant)
        print("1. sequences", json.dumps(sequences, ensure_ascii=False))
        if len(sequences) < 2:
            raise RuntimeError("Expected at least two detected sequences")

        full = await storyboard_service.generate_storyboard(
            session,
            project_id=project.id,
            tenant=tenant,
            mode=StoryboardGenerationMode.FULL_SCRIPT,
            sequence_id=None,
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            style_preset="cinematic_realistic",
            shots_per_scene=2,
            overwrite=True,
        )
        print("2. full_storyboard", json.dumps(full, ensure_ascii=False, default=str))

        sequence_id = sequences[1]["sequence_id"]
        sequence_generate = await storyboard_service.generate_storyboard(
            session,
            project_id=project.id,
            tenant=tenant,
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id=sequence_id,
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            style_preset="graphic_novel",
            shots_per_scene=3,
            overwrite=True,
        )
        print("3. sequence_storyboard", json.dumps(sequence_generate, ensure_ascii=False, default=str))

        sequence_detail, shots = await storyboard_service.get_sequence_storyboard(
            session,
            project_id=project.id,
            sequence_id=sequence_id,
            tenant=tenant,
        )
        print("4. sequence_detail", json.dumps({"sequence": sequence_detail, "shots": len(shots)}, ensure_ascii=False, default=str))

        regenerate = await storyboard_service.generate_storyboard(
            session,
            project_id=project.id,
            tenant=tenant,
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id=sequence_id,
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            style_preset="moody_noir",
            shots_per_scene=2,
            overwrite=True,
        )
        print("5. regenerate_sequence", json.dumps(regenerate, ensure_ascii=False, default=str))

        full_list, full_version = await storyboard_service.list_storyboard_shots(
            session,
            project_id=project.id,
            tenant=tenant,
        )
        sequence_list, sequence_version = await storyboard_service.list_storyboard_shots(
            session,
            project_id=project.id,
            tenant=tenant,
            sequence_id=sequence_id,
        )
        print("6. lists", json.dumps({"full_shots": len(full_list), "full_version": full_version, "sequence_shots": len(sequence_list), "sequence_version": sequence_version}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
