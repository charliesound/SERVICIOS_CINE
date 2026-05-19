from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.tenant_context import TenantContext
from models.core import Project
from models.project_visual_bible import ProjectVisualBible
from schemas.project_visual_bible_schema import (
    ProjectVisualBibleCreate,
    ProjectVisualBibleUpdate,
    VisualBiblePreviewRequest,
    VisualBiblePreviewResponse,
)
from services.cinematic_taxonomy_service import (
    CategoryNotFoundError,
    CinematicTaxonomyError,
    CinematicTaxonomyService,
    PresetNotFoundError,
)

cinematic_taxonomy_service = CinematicTaxonomyService()


async def _get_project_for_tenant_or_404(
    db: AsyncSession, project_id: str, tenant: TenantContext
) -> Project:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == str(tenant.organization_id),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _collect_all_taxonomy_element_ids() -> set[str]:
    ids: set[str] = set()
    for el in cinematic_taxonomy_service._elements.values():
        for e in el:
            ids.add(e.id)
    return ids


async def get_visual_bible(
    db: AsyncSession, project_id: str, tenant: TenantContext
) -> ProjectVisualBible:
    await _get_project_for_tenant_or_404(db, project_id, tenant)
    result = await db.execute(
        select(ProjectVisualBible).where(
            ProjectVisualBible.project_id == project_id,
            ProjectVisualBible.organization_id == str(tenant.organization_id),
        )
    )
    vb = result.scalar_one_or_none()
    if not vb:
        raise HTTPException(status_code=404, detail="Visual Bible not found for this project")
    return vb


async def get_or_create_visual_bible(
    db: AsyncSession, project_id: str, tenant: TenantContext
) -> ProjectVisualBible:
    await _get_project_for_tenant_or_404(db, project_id, tenant)
    result = await db.execute(
        select(ProjectVisualBible).where(
            ProjectVisualBible.project_id == project_id,
            ProjectVisualBible.organization_id == str(tenant.organization_id),
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    vb = ProjectVisualBible(
        project_id=project_id,
        organization_id=str(tenant.organization_id),
    )
    db.add(vb)
    await db.commit()
    await db.refresh(vb)
    return vb


async def update_visual_bible(
    db: AsyncSession,
    project_id: str,
    payload: ProjectVisualBibleUpdate,
    tenant: TenantContext,
) -> ProjectVisualBible:
    vb = await get_visual_bible(db, project_id, tenant)

    if payload.active_preset_id is not None:
        try:
            cinematic_taxonomy_service.get_preset(payload.active_preset_id)
        except PresetNotFoundError:
            raise HTTPException(
                status_code=400,
                detail=f"Preset '{payload.active_preset_id}' not found in cinematic taxonomy",
            )

    if payload.selected_elements_json is not None:
        valid_ids = _collect_all_taxonomy_element_ids()
        for key, value in payload.selected_elements_json.items():
            if isinstance(value, list):
                for el_id in value:
                    if isinstance(el_id, str) and el_id not in valid_ids:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Element '{el_id}' in selected_elements_json.{key} not found in taxonomy",
                        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vb, field, value)

    await db.commit()
    await db.refresh(vb)
    return vb


async def reset_visual_bible(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
) -> ProjectVisualBible:
    vb = await get_visual_bible(db, project_id, tenant)
    vb.active_preset_id = None
    vb.selected_elements_json = {}
    vb.custom_prompt_tags_json = []
    vb.negative_prompt_tags_json = []
    vb.director_notes = None
    vb.prompt_mode = "tag_soup"
    vb.target_model = "SDXL"
    await db.commit()
    await db.refresh(vb)
    return vb


async def preview_enriched_prompt(
    db: AsyncSession,
    project_id: str,
    payload: VisualBiblePreviewRequest,
    tenant: TenantContext,
) -> VisualBiblePreviewResponse:
    vb = await get_or_create_visual_bible(db, project_id, tenant)

    preset_id = vb.active_preset_id
    selected_tags: list[str] = list(vb.custom_prompt_tags_json or [])
    if payload.selected_tags:
        for tag in payload.selected_tags:
            if tag not in selected_tags:
                selected_tags.append(tag)

    try:
        result = cinematic_taxonomy_service.enrich_prompt(
            base_prompt=payload.base_prompt,
            preset_id=preset_id,
            selected_tags=selected_tags if selected_tags else None,
        )
    except (PresetNotFoundError, CategoryNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CinematicTaxonomyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return VisualBiblePreviewResponse(
        base_prompt=result.base_prompt,
        enriched_prompt=result.enriched_prompt,
        negative_prompt=result.negative_prompt,
        applied_preset=result.applied_preset.model_dump() if result.applied_preset else None,
        applied_tags=[t.model_dump() for t in result.applied_tags],
        warnings=result.warnings,
        visual_bible_id=vb.id,
    )


async def resolve_active_preset(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
) -> Optional[dict[str, Any]]:
    vb = await get_or_create_visual_bible(db, project_id, tenant)
    if not vb.active_preset_id:
        return None
    try:
        preset = cinematic_taxonomy_service.get_preset(vb.active_preset_id)
        return preset.model_dump()
    except PresetNotFoundError:
        return None


def validate_selected_elements_against_taxonomy(payload: ProjectVisualBibleUpdate) -> None:
    if payload.selected_elements_json is None:
        return
    valid_ids = _collect_all_taxonomy_element_ids()
    for key, value in payload.selected_elements_json.items():
        if isinstance(value, list):
            for el_id in value:
                if isinstance(el_id, str) and el_id not in valid_ids:
                    raise ValueError(
                        f"Element '{el_id}' in selected_elements_json.{key} not found in taxonomy"
                    )
