from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.comfyui_model_inventory_service import ComfyUIInventoryError
from services.comfyui_storyboard_render_service import comfyui_storyboard_render_service
from services.storyboard_service import storyboard_service


router = APIRouter(prefix="/api", tags=["comfyui-storyboard"])


@router.get("/ops/comfyui/storyboard/status")
async def get_comfyui_storyboard_status() -> dict[str, Any]:
    return await comfyui_storyboard_render_service.healthcheck()


@router.post("/projects/{project_id}/storyboard/render")
async def render_storyboard_scenes(
    project_id: str,
    payload: dict[str, Any],
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    try:
        await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        return comfyui_storyboard_render_service.render_storyboard_with_plan(
            project_id=project_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
