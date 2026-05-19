from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture(autouse=True)
def _reset_taxonomy_service():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    CinematicTaxonomyService._instance = None


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:////tmp/ailinkcinema.db")
    session_local = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_local() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _ensure_project_exists(db, project_id="proj-vb-1", org_id="org-vb-test"):
    from sqlalchemy import text as sa_text

    async def _inner():
        r = await db.execute(
            sa_text(
                "SELECT id FROM projects WHERE id = :pid"
            ).bindparams(pid=project_id)
        )
        if not r.scalar_one_or_none():
            await db.execute(
                sa_text(
                    "INSERT INTO projects (id, organization_id, name, status) "
                    "VALUES (:pid, :oid, :name, :status)"
                ).bindparams(pid=project_id, oid=org_id, name="VB Test Project", status="active")
            )
            await db.commit()

    return _inner


class TestGetOrCreateVisualBible:
    async def test_creates_default_when_not_exists(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        vb = await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        assert vb is not None
        assert vb.project_id == "proj-vb-1"
        assert vb.organization_id == "org-vb-test"
        assert vb.active_preset_id is None
        assert vb.prompt_mode == "tag_soup"
        assert vb.target_model == "SDXL"

    async def test_returns_existing(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        vb1 = await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        vb2 = await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        assert vb1.id == vb2.id


class TestGetVisualBible:
    async def test_returns_existing(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible, get_visual_bible
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        vb1 = await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        vb2 = await get_visual_bible(db_session, "proj-vb-1", tenant)
        assert vb1.id == vb2.id

    async def test_raises_404_when_not_found(self, db_session):
        from services.project_visual_bible_service import get_visual_bible
        from dependencies.tenant_context import TenantContext
        from fastapi import HTTPException

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-other", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        with pytest.raises(HTTPException) as exc:
            await get_visual_bible(db_session, "proj-vb-1", tenant)
        assert exc.value.status_code == 404


class TestUpdateVisualBible:
    async def test_updates_active_preset_valid(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible, update_visual_bible
        from schemas.project_visual_bible_schema import ProjectVisualBibleUpdate
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        payload = ProjectVisualBibleUpdate(active_preset_id="noir_classic")
        vb = await update_visual_bible(db_session, "proj-vb-1", payload, tenant)
        assert vb.active_preset_id == "noir_classic"

    async def test_rejects_fake_preset(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible, update_visual_bible
        from schemas.project_visual_bible_schema import ProjectVisualBibleUpdate
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        payload = ProjectVisualBibleUpdate(active_preset_id="fake_preset_999")
        with pytest.raises(Exception) as exc:
            await update_visual_bible(db_session, "proj-vb-1", payload, tenant)
        assert "not found" in str(exc.value).lower()


class TestResetVisualBible:
    async def test_clears_configuration(self, db_session):
        from services.project_visual_bible_service import get_or_create_visual_bible, update_visual_bible, reset_visual_bible
        from schemas.project_visual_bible_schema import ProjectVisualBibleUpdate
        from dependencies.tenant_context import TenantContext

        tenant = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session)()
        await get_or_create_visual_bible(db_session, "proj-vb-1", tenant)
        await update_visual_bible(
            db_session, "proj-vb-1",
            ProjectVisualBibleUpdate(
                active_preset_id="noir_classic",
                director_notes="Some notes",
                prompt_mode="semantic_t5",
                target_model="Flux",
            ),
            tenant,
        )
        vb = await reset_visual_bible(db_session, "proj-vb-1", tenant)
        assert vb.active_preset_id is None
        assert vb.selected_elements_json == {}
        assert vb.custom_prompt_tags_json == []
        assert vb.negative_prompt_tags_json == []
        assert vb.director_notes is None
        assert vb.prompt_mode == "tag_soup"
        assert vb.target_model == "SDXL"


class TestTenantIsolation:
    async def test_other_org_returns_404(self, db_session):
        from services.project_visual_bible_service import get_visual_bible
        from dependencies.tenant_context import TenantContext
        from fastapi import HTTPException

        tenant_a = TenantContext(
            user_id="u1", organization_id="org-vb-test", role="admin", plan="free"
        )
        tenant_b = TenantContext(
            user_id="u2", organization_id="org-vb-other", role="admin", plan="free"
        )
        await _ensure_project_exists(db_session, org_id="org-vb-test")()

        with pytest.raises(HTTPException) as exc:
            await get_visual_bible(db_session, "proj-vb-1", tenant_b)
        assert exc.value.status_code == 404
