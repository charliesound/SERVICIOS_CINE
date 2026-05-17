from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


def _build_test_app(
    module_key: str,
    plan: str,
    *,
    is_admin: bool = True,
    is_global_admin: bool = False,
) -> FastAPI:
    from dependencies.module_access import require_module_access
    from dependencies.tenant_context import get_tenant_context
    from schemas.auth_schema import TenantContext

    app = FastAPI()

    @app.get("/protected/test")
    async def protected_test(
        _tenant: TenantContext = Depends(require_module_access(module_key)),
    ) -> dict[str, bool]:
        return {"ok": True}

    app.dependency_overrides[get_tenant_context] = lambda: TenantContext(
        user_id="user-1",
        organization_id="org-1",
        plan=plan,
        role="admin",
        is_admin=is_admin,
        is_global_admin=is_global_admin,
    )
    return app


def _build_stateless_test_app() -> FastAPI:
    from routes.cid_script_to_prompt_routes import router as cid_router

    app = FastAPI()
    app.include_router(cid_router)
    return app


def test_module_access_blocks_plan_without_feature() -> None:
    app = _build_test_app("funding_grants", "free", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["code"] == "MODULE_ACCESS_BLOCKED"
    assert detail["module"] == "funding_grants"


def test_module_access_allows_plan_with_feature() -> None:
    app = _build_test_app("funding_grants", "producer", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_module_access_bypasses_for_admin_roles() -> None:
    app = _build_test_app("funding_grants", "free", is_admin=True)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


# --- pitch_deck enforcement (presentation_routes.py) ---

def test_pitch_deck_blocks_plan_without_feature() -> None:
    app = _build_test_app("pitch_deck", "free", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["code"] == "MODULE_ACCESS_BLOCKED"
    assert detail["module"] == "pitch_deck"


def test_pitch_deck_allows_plan_with_feature() -> None:
    app = _build_test_app("pitch_deck", "producer", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_pitch_deck_bypasses_for_admin() -> None:
    app = _build_test_app("pitch_deck", "free", is_admin=True)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


# --- pipeline_builder enforcement (cid_script_to_prompt /analyze-full) ---

def test_pipeline_builder_blocks_plan_without_feature() -> None:
    app = _build_test_app("pipeline_builder", "free", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["code"] == "MODULE_ACCESS_BLOCKED"
    assert detail["module"] == "pipeline_builder"


def test_pipeline_builder_allows_plan_with_feature() -> None:
    app = _build_test_app("pipeline_builder", "studio", is_admin=False)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_pipeline_builder_bypasses_for_admin() -> None:
    app = _build_test_app("pipeline_builder", "free", is_admin=True)
    client = TestClient(app)

    response = client.get("/protected/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


# --- stateless cid_script_to_prompt endpoints remain accessible ---

def test_cid_stateless_endpoint_remains_accessible() -> None:
    from fastapi.testclient import TestClient as TC

    app = _build_stateless_test_app()
    client = TC(app)

    response = client.get("/api/cid/script-to-prompt/director-lenses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
