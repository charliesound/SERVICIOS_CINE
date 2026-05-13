from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from services.account_service import get_user_by_id, resolve_effective_plan
from services.cid_test_mode import (
    get_internal_test_plan,
    require_test_mode_enabled,
    resolve_test_access,
)

router = APIRouter(prefix="/api/dev/cid-test", tags=["cid-internal-test"])


DEMO_SCRIPT_SHORT = (
    "INT. CAFE - NIGHT\n\n"
    "MARIA, early 30s, watches rain through the window.\n"
    "A cup of coffee cools on the table.\n\n"
    "MARIA\n"
    "(quietly)\n"
    "Not again.\n\n"
    "EXT. STREET - NIGHT\n\n"
    "A car passes fast and disappears into the fog.\n"
)

SIMULATED_OUTPUT = {
    "script_analysis": {
        "status": "simulated",
        "scenes": 3,
        "estimated_duration_min": 5,
        "genre": "drama",
        "summary": "Short dramatic scene in a cafe at night.",
    },
    "breakdown": {
        "status": "simulated",
        "sequences": [
            {"id": "seq_01", "location": "INT. CAFE - NIGHT", "shots": 4},
            {"id": "seq_02", "location": "EXT. STREET - NIGHT", "shots": 2},
        ],
    },
    "characters": {
        "status": "simulated",
        "characters": [
            {"name": "MARIA", "role": "protagonist", "age": "30s", "lines": 1},
        ],
    },
    "locations": {
        "status": "simulated",
        "locations": [
            {"name": "CAFE", "type": "interior", "lighting": "night"},
            {"name": "STREET", "type": "exterior", "lighting": "night"},
        ],
    },
    "storyboard": {
        "status": "simulated",
        "shots_planned": 6,
        "sequences": 2,
    },
    "production_plan": {
        "status": "simulated",
        "estimated_days": 1,
        "crew_size": 5,
        "budget_category": "low",
    },
    "cid_pipeline": {
        "status": "simulated",
        "pipeline_id": "pipe_demo_001",
        "stages": ["ingest", "analysis", "breakdown", "planning"],
    },
}


class SimulateAccessPayload(BaseModel):
    requested_plan: str | None = None


class SimulateDemoProjectPayload(BaseModel):
    title: str = "Demo CID Project"
    script_text: str | None = None
    demo_type: str = Field(default="short_film")


class RunFullPipelinePayload(BaseModel):
    project_id: str | None = None
    execution_mode: str = "simulated"
    modules: list[str] = Field(default_factory=lambda: list(SIMULATED_OUTPUT.keys()))


async def _get_request_context(tenant: TenantContext, db: AsyncSession) -> dict:
    user = await get_user_by_id(db, tenant.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access = resolve_test_access(user.email, tenant.is_global_admin)
    if not access["can_access_as_test_user"]:
        raise HTTPException(status_code=403, detail="Internal tester access required")

    return {"tenant": tenant, "user": user, "access": access}


async def require_internal_tester(
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> dict:
    require_test_mode_enabled()
    return await _get_request_context(tenant, db)


@router.get("/status")
async def cid_test_status(
    context: dict = Depends(require_internal_tester),
):
    user = context["user"]
    tenant = context["tenant"]
    access = context["access"]

    return {
        "enabled": access["enabled"],
        "user_email": user.email,
        "is_admin": tenant.is_global_admin,
        "is_internal_tester": access["is_internal_tester"],
        "test_plan": access["test_plan"],
        "warning": "CID internal test mode is isolated to /api/dev/cid-test/*",
    }


@router.post("/simulate-access")
async def simulate_access(
    payload: SimulateAccessPayload,
    context: dict = Depends(require_internal_tester),
    db: AsyncSession = Depends(get_db),
):
    del payload
    user = context["user"]
    tenant = context["tenant"]
    access = context["access"]
    original_plan = await resolve_effective_plan(db, user)

    return {
        "original_plan": original_plan,
        "simulated_plan": access["test_plan"],
        "can_access_as_test_user": access["can_access_as_test_user"],
        "is_real_admin": tenant.is_global_admin,
        "is_email_whitelisted": access["is_email_whitelisted"],
        "note": "Simulation only. This endpoint does not change the real plan, role, or tenant context.",
    }


@router.post("/simulate-demo-project")
async def simulate_demo_project(
    payload: SimulateDemoProjectPayload,
    context: dict = Depends(require_internal_tester),
):
    del context
    title = payload.title.strip() or "Demo CID Project"
    script_text = (payload.script_text or "").strip() or DEMO_SCRIPT_SHORT

    return {
        "simulated": True,
        "project_id": f"sim_{uuid.uuid4().hex[:12]}",
        "title": title,
        "demo_type": payload.demo_type,
        "script_text": script_text,
        "persisted": False,
        "created_assets": [],
        "note": "Simulation only. No project, job, or asset is persisted.",
    }


@router.post("/run-full-pipeline")
async def run_full_pipeline(
    payload: RunFullPipelinePayload,
    context: dict = Depends(require_internal_tester),
):
    del context
    modules = payload.modules or list(SIMULATED_OUTPUT.keys())
    pipeline_result = {}
    warnings = []

    for module_name in modules:
        if module_name in SIMULATED_OUTPUT:
            pipeline_result[module_name] = SIMULATED_OUTPUT[module_name]
        else:
            pipeline_result[module_name] = {
                "status": "simulated",
                "note": "Module not yet implemented; no real service was called.",
            }
            warnings.append(f"Module '{module_name}' is simulated only")

    if payload.execution_mode == "available_real":
        warnings.append(
            "Real mode requested but forced to simulated; no external service or real job execution is enabled here."
        )

    return {
        "simulated": True,
        "project_id": payload.project_id or f"sim_{uuid.uuid4().hex[:12]}",
        "run_id": f"sim_run_{uuid.uuid4().hex[:12]}",
        "status": "completed_simulated",
        "test_plan": get_internal_test_plan(),
        "pipeline_result": pipeline_result,
        "warnings": warnings,
        "next_steps": ["Review simulated output before enabling any real pipeline integration."],
    }
