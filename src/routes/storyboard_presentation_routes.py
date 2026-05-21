from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from database import get_db
from dependencies.module_access import require_module_access
from models.core import Project
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.storyboard_presentation_schema import (
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
    StoryboardSheetRequest,
    StoryboardSheetResponse,
    StoryboardSheetTemplate,
)
from services.storyboard_export_service import storyboard_export_service
from services.storyboard_frame_service import storyboard_frame_service
from services.storyboard_layout_engine import storyboard_layout_engine


router = APIRouter(
    prefix="/api/projects",
    tags=["storyboard-presentation"],
    dependencies=[Depends(require_module_access("storyboard_ai"))],
)


@dataclass(frozen=True)
class ResolvedStoryboardSheetTemplate:
    sheet_template: StoryboardSheetTemplate | None
    layout_config: StoryboardLayoutConfig
    effective_max_frames: int | None
    orientation: Literal["portrait", "landscape"]


_TEMPLATE_CONFIG: dict[StoryboardSheetTemplate, dict[str, object]] = {
    StoryboardSheetTemplate.clean_4_panel_pitch: {
        "layout": StoryboardLayoutName.grid_2x2,
        "preset": StoryboardSheetPreset.cinematic_pitch,
        "default_max_frames": 4,
        "orientation": "portrait",
        "title": "Pitch Storyboard Sheet",
    },
    StoryboardSheetTemplate.clean_6_panel_review: {
        "layout": StoryboardLayoutName.grid_2x3,
        "preset": StoryboardSheetPreset.realistic_client_review,
        "default_max_frames": 6,
        "orientation": "portrait",
        "title": "Review Storyboard Sheet",
    },
    StoryboardSheetTemplate.grid_8_panel_vertical: {
        "layout": StoryboardLayoutName.grid_2x4,
        "preset": StoryboardSheetPreset.realistic_client_review,
        "default_max_frames": 8,
        "orientation": "portrait",
        "title": "8 Panel Vertical Sheet",
    },
    StoryboardSheetTemplate.grid_8_panel_landscape: {
        "layout": StoryboardLayoutName.grid_2x4,
        "preset": StoryboardSheetPreset.realistic_client_review,
        "default_max_frames": 8,
        "orientation": "landscape",
        "title": "8 Panel Landscape Sheet",
    },
    StoryboardSheetTemplate.production_12_panel_vertical: {
        "layout": StoryboardLayoutName.grid_3x3,
        "preset": StoryboardSheetPreset.production_sheet,
        "default_max_frames": 12,
        "orientation": "portrait",
        "title": "Production Storyboard Sheet",
    },
    StoryboardSheetTemplate.production_12_panel_landscape: {
        "layout": StoryboardLayoutName.grid_3x3,
        "preset": StoryboardSheetPreset.production_sheet,
        "default_max_frames": 12,
        "orientation": "landscape",
        "title": "Production Landscape Sheet",
    },
    StoryboardSheetTemplate.client_review_with_notes: {
        "layout": StoryboardLayoutName.grid_2x2,
        "preset": StoryboardSheetPreset.realistic_client_review,
        "default_max_frames": 4,
        "orientation": "portrait",
        "title": "Client Review With Notes",
        "caption_height_px": 180,
    },
    StoryboardSheetTemplate.technical_storyboard_sheet: {
        "layout": StoryboardLayoutName.grid_2x2,
        "preset": StoryboardSheetPreset.production_sheet,
        "default_max_frames": None,
        "orientation": "portrait",
        "title": "Technical Storyboard Sheet",
        "caption_height_px": 190,
    },
}


def _resolve_orientation_dimensions(orientation: Literal["portrait", "landscape"]) -> tuple[int, int]:
    if orientation == "portrait":
        return 1080, 1920
    return 1920, 1080


def resolve_storyboard_sheet_template(payload: StoryboardSheetRequest) -> ResolvedStoryboardSheetTemplate:
    if payload.sheet_template is None:
        orientation: Literal["portrait", "landscape"] = (
            "portrait" if payload.layout.page_height_px > payload.layout.page_width_px else "landscape"
        )
        return ResolvedStoryboardSheetTemplate(
            sheet_template=None,
            layout_config=payload.layout,
            effective_max_frames=payload.max_frames,
            orientation=orientation,
        )

    template_config = _TEMPLATE_CONFIG[payload.sheet_template]
    orientation = template_config["orientation"]
    page_width_px, page_height_px = _resolve_orientation_dimensions(orientation)
    layout_config = payload.layout.model_copy(
        update={
            "layout": template_config["layout"],
            "preset": template_config["preset"],
            "page_width_px": page_width_px,
            "page_height_px": page_height_px,
            "caption_height_px": template_config.get("caption_height_px", payload.layout.caption_height_px),
            "title": payload.layout.title or template_config.get("title"),
        }
    )
    effective_max_frames = payload.max_frames if payload.max_frames is not None else template_config["default_max_frames"]
    return ResolvedStoryboardSheetTemplate(
        sheet_template=payload.sheet_template,
        layout_config=layout_config,
        effective_max_frames=effective_max_frames,
        orientation=orientation,
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


@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")
async def download_storyboard_sheet_artifact(
    project_id: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    await _ensure_project_access(db, project_id, tenant)

    artifact_path = storyboard_export_service.resolve_artifact_path(project_id, filename)
    if artifact_path is None or not artifact_path.is_file():
        raise HTTPException(status_code=404, detail="Storyboard sheet artifact not found")

    media_type = mimetypes.guess_type(artifact_path.name)[0] or "application/octet-stream"
    return FileResponse(path=artifact_path, media_type=media_type, filename=artifact_path.name)


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
    resolved_template = resolve_storyboard_sheet_template(payload)

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
            max_frames=resolved_template.effective_max_frames,
            frame_selection_mode=payload.frame_selection_mode,
        )

        pages = storyboard_layout_engine.render_pages(frames, resolved_template.layout_config)
        base_name = storyboard_export_service.build_export_base_name(
            project_id=project_id,
            layout=resolved_template.layout_config.layout.value,
            frame_count=len(frames),
            output_format=payload.output_format,
            sheet_template=resolved_template.sheet_template.value if resolved_template.sheet_template else None,
        )
        if payload.output_format == "png":
            export_payload = storyboard_export_service.export_png(project_id=project_id, pages=pages, base_name=base_name)
        else:
            export_payload = storyboard_export_service.export_pdf(project_id=project_id, pages=pages, base_name=base_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    artifact_path = Path(str(export_payload["artifact_path"]))
    page_paths = list(export_payload["page_paths"])
    page_urls = storyboard_export_service.build_page_urls(project_id, page_paths)

    return StoryboardSheetResponse(
        artifact_path=str(artifact_path),
        artifact_url=storyboard_export_service.build_artifact_url(project_id, artifact_path.name),
        output_format=payload.output_format,
        frame_count=len(frames),
        layout=resolved_template.layout_config.layout,
        preset=resolved_template.layout_config.preset,
        metadata={
            "page_count": int(export_payload["page_count"]),
            "page_paths": page_paths,
            "page_urls": page_urls,
            "render_job_id": payload.render_job_id,
            "asset_ids": payload.asset_ids or [],
            "credit_estimate": storyboard_export_service.build_credit_estimate(len(frames)),
            "template": {
                "sheet_template": resolved_template.sheet_template.value if resolved_template.sheet_template else None,
                "effective_layout": resolved_template.layout_config.layout.value,
                "effective_preset": resolved_template.layout_config.preset.value,
                "effective_max_frames": resolved_template.effective_max_frames,
                "orientation": resolved_template.orientation,
            },
        },
    )
