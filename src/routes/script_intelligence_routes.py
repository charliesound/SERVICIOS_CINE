from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.module_access import require_module_access
from dependencies.tenant_context import TenantContext, get_tenant_context
from schemas.cid_script_intelligence_schema import (
    ScriptIntelligenceAnalyzeRequest,
    ScriptIntelligenceResponse,
)
from services.cid_script_intelligence_service import cid_script_intelligence_service


router = APIRouter(prefix="/api/projects", tags=["script-intelligence"])


@router.post("/{project_id}/script-intelligence/analyze", response_model=ScriptIntelligenceResponse)
async def analyze_script_intelligence(
    project_id: str,
    payload: ScriptIntelligenceAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _module_access: TenantContext = Depends(require_module_access("script_analysis")),
) -> ScriptIntelligenceResponse:
    try:
        result = await cid_script_intelligence_service.analyze_project(
            db,
            project_id=project_id,
            organization_id=str(tenant.organization_id),
            sequence_ids=payload.sequence_ids,
            theory_focus=payload.theory_focus,
            include_storyboard_actionables=payload.include_storyboard_actionables,
        )
    except ValueError as exc:
        if str(exc) == "project_not_found":
            raise HTTPException(status_code=404, detail="Project not found") from exc
        if str(exc) == "project_script_missing":
            raise HTTPException(status_code=400, detail="Project has no script text") from exc
        raise HTTPException(status_code=500, detail="Script intelligence failed") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Script intelligence failed") from exc

    return ScriptIntelligenceResponse(**result)
