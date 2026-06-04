from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.project_access import validate_project_access, require_write_permission
from models.core import Project
from dependencies.tenant_context import get_tenant_context, TenantContext
from schemas.project_visual_bible_schema import (
    ProjectVisualBibleResponse,
    ProjectVisualBibleUpdate,
    VisualBiblePreviewRequest,
    VisualBiblePreviewResponse,
)
from services.project_visual_bible_service import (
    get_visual_bible,
    get_or_create_visual_bible,
    preview_enriched_prompt,
    reset_visual_bible,
    update_visual_bible,
)

router = APIRouter(
    prefix="/api/projects/{project_id}/visual-bible",
    tags=["project-visual-bible"],
)


def _to_response(vb) -> ProjectVisualBibleResponse:
    return ProjectVisualBibleResponse(
        id=vb.id,
        project_id=vb.project_id,
        organization_id=vb.organization_id,
        active_preset_id=vb.active_preset_id,
        selected_elements_json=vb.selected_elements_json or {},
        custom_prompt_tags_json=vb.custom_prompt_tags_json or [],
        negative_prompt_tags_json=vb.negative_prompt_tags_json or [],
        director_notes=vb.director_notes,
        prompt_mode=vb.prompt_mode or "tag_soup",
        target_model=vb.target_model or "SDXL",
        is_active=vb.is_active if vb.is_active is not None else True,
        created_by=vb.created_by,
        created_at=vb.created_at,
        updated_at=vb.updated_at,
    )


@router.get("", response_model=ProjectVisualBibleResponse)
async def api_get_visual_bible(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    validated_project_id = str(project.id)
    vb = await get_or_create_visual_bible(db, validated_project_id, tenant)
    return _to_response(vb)


@router.put("", response_model=ProjectVisualBibleResponse)
async def api_update_visual_bible(
    project_id: str,
    payload: ProjectVisualBibleUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
    _write: Any = Depends(require_write_permission),
):
    validated_project_id = str(project.id)
    vb = await update_visual_bible(db, validated_project_id, payload, tenant)
    return _to_response(vb)


@router.post("/preview-prompt", response_model=VisualBiblePreviewResponse)
async def api_preview_prompt(
    project_id: str,
    payload: VisualBiblePreviewRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    validated_project_id = str(project.id)
    return await preview_enriched_prompt(db, validated_project_id, payload, tenant)


@router.post("/reset", response_model=ProjectVisualBibleResponse)
async def api_reset_visual_bible(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
    _write: Any = Depends(require_write_permission),
):
    validated_project_id = str(project.id)
    vb = await reset_visual_bible(db, validated_project_id, tenant)
    return _to_response(vb)
