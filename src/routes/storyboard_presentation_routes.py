from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from dependencies.module_access import require_module_access
from models.core import Project
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.storyboard_presentation_schema import StoryboardSheetRequest, StoryboardSheetResponse
from services.storyboard_export_service import storyboard_export_service
from services.storyboard_frame_service import storyboard_frame_service
from services.storyboard_layout_engine import storyboard_layout_engine


router = APIRouter(
    prefix="/api/projects",
    tags=["storyboard-presentation"],
    dependencies=[Depends(require_module_access("storyboard_ai"))],
)


async def _ensure_project_access(db: AsyncSession, project_id: str, tenant: TenantContext) -> None:
    result = await db.execute(
        select(Project.id).where(
            Project.id == project_id,
            Project.organization_id == str(tenant.organization_id),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)
async def generate_storyboard_sheet(
    project_id: str,
    payload: StoryboardSheetRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardSheetResponse:
    if payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_id in body must match route project_id")

    await _ensure_project_access(db, project_id, tenant)

    try:
        if payload.asset_ids:
            frames = await storyboard_frame_service.collect_by_asset_ids(
                db,
                payload.asset_ids,
                organization_id=tenant.organization_id,
                override_shot_info=payload.override_shot_info,
            )
        elif payload.render_job_id:
            frames = await storyboard_frame_service.collect_by_render_job(
                db,
                payload.render_job_id,
                organization_id=tenant.organization_id,
                override_shot_info=payload.override_shot_info,
            )
        else:
            frames = await storyboard_frame_service.collect_by_project(
                db,
                project_id,
                organization_id=tenant.organization_id,
                override_shot_info=payload.override_shot_info,
            )

        frames = storyboard_frame_service.limit_frames(
            frames,
            max_frames=payload.max_frames,
            frame_selection_mode=payload.frame_selection_mode,
        )

        pages = storyboard_layout_engine.render_pages(frames, payload.layout)
        base_name = f"storyboard_sheet_{project_id[:8]}_{payload.layout.layout.value}"
        if payload.output_format == "png":
            export_payload = storyboard_export_service.export_png(project_id=project_id, pages=pages, base_name=base_name)
        else:
            export_payload = storyboard_export_service.export_pdf(project_id=project_id, pages=pages, base_name=base_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StoryboardSheetResponse(
        artifact_path=str(export_payload["artifact_path"]),
        artifact_url=None,
        output_format=payload.output_format,
        frame_count=len(frames),
        layout=payload.layout.layout,
        preset=payload.layout.preset,
        metadata={
            "page_count": int(export_payload["page_count"]),
            "page_paths": list(export_payload["page_paths"]),
            "render_job_id": payload.render_job_id,
            "asset_ids": payload.asset_ids or [],
            "credit_estimate": storyboard_export_service.build_credit_estimate(len(frames)),
        },
    )
