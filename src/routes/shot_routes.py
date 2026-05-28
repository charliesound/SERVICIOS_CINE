import json
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.storage import MediaAsset
from models.storyboard import StoryboardShot
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.shot_schema import (
    StoryboardShotBulkReorderRequest,
    StoryboardShotCreate,
    StoryboardShotListResponse,
    StoryboardShotResponse,
    StoryboardShotUpdate,
)
from services.shot_service import shot_service


router = APIRouter(prefix="/api/projects", tags=["shots"])


def _safe_metadata_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _derive_render_state(*, asset_id: str | None, metadata: dict[str, Any]) -> tuple[str, str, bool, str | None]:
    metadata_status = metadata.get("render_status")
    render_job_id = metadata.get("render_job_id")

    if metadata_status == "render_pending":
        return "render_pending", "render_pending", False, render_job_id
    if metadata_status == "render_failed":
        return "render_failed", "render_failed", False, render_job_id
    if metadata_status == "render_succeeded":
        return "render_succeeded", "render_succeeded", bool(asset_id), render_job_id
    if asset_id:
        return "render_succeeded", "render_succeeded", True, render_job_id
    return "no_asset", "planned", False, render_job_id


async def _serialize_shot(
    db: AsyncSession,
    project_id: str,
    shot: StoryboardShot,
) -> StoryboardShotResponse:
    metadata = _safe_metadata_dict(getattr(shot, "metadata_json", None))
    asset = None
    if shot.asset_id:
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == shot.asset_id))
        asset = result.scalar_one_or_none()
    render_status, image_state, has_image, render_job_id = _derive_render_state(
        asset_id=shot.asset_id,
        metadata=metadata,
    )
    thumbnail_url = f"/api/projects/{project_id}/storyboard/shots/{shot.id}/thumbnail"
    image_url = f"/api/projects/{project_id}/storyboard/shots/{shot.id}/image"
    return StoryboardShotResponse(
        id=str(shot.id),
        project_id=str(shot.project_id),
        organization_id=str(shot.organization_id),
        sequence_id=shot.sequence_id,
        sequence_order=int(shot.sequence_order),
        scene_number=getattr(shot, "scene_number", None),
        scene_heading=getattr(shot, "scene_heading", None),
        narrative_text=shot.narrative_text,
        asset_id=shot.asset_id,
        shot_type=shot.shot_type,
        visual_mode=shot.visual_mode,
        generation_mode=getattr(shot, "generation_mode", None),
        generation_job_id=getattr(shot, "generation_job_id", None),
        metadata_json=getattr(shot, "metadata_json", None),
        version=int(getattr(shot, "version", 1) or 1),
        is_active=bool(getattr(shot, "is_active", True)),
        asset_file_name=getattr(asset, "file_name", None),
        asset_mime_type=getattr(asset, "mime_type", None),
        thumbnail_url=thumbnail_url,
        image_url=image_url,
        preview_url=image_url,
        render_job_id=render_job_id,
        render_status=render_status,
        has_image=has_image,
        image_state=image_state,
        created_at=shot.created_at,
        updated_at=shot.updated_at,
    )


@router.get("/{project_id}/shots", response_model=StoryboardShotListResponse)
async def list_project_shots(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardShotListResponse:
    shots = await shot_service.list_project_shots(db, project_id=project_id, tenant=tenant)
    return StoryboardShotListResponse(
        shots=[await _serialize_shot(db, project_id, shot) for shot in shots]
    )


@router.post("/{project_id}/shots", response_model=StoryboardShotResponse, status_code=status.HTTP_201_CREATED)
async def create_project_shot(
    project_id: str,
    payload: StoryboardShotCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardShotResponse:
    shot = await shot_service.create_shot(
        db,
        project_id=project_id,
        payload=payload,
        tenant=tenant,
    )
    return await _serialize_shot(db, project_id, shot)


@router.put("/{project_id}/shots/bulk-reorder", response_model=StoryboardShotListResponse)
async def bulk_reorder_project_shots(
    project_id: str,
    payload: StoryboardShotBulkReorderRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardShotListResponse:
    shots = await shot_service.bulk_reorder(
        db,
        project_id=project_id,
        payload=payload,
        tenant=tenant,
    )
    return StoryboardShotListResponse(
        shots=[await _serialize_shot(db, project_id, shot) for shot in shots]
    )


@router.put("/{project_id}/shots/{shot_id}", response_model=StoryboardShotResponse)
async def update_project_shot(
    project_id: str,
    shot_id: str,
    payload: StoryboardShotUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardShotResponse:
    shot = await shot_service.update_shot(
        db,
        project_id=project_id,
        shot_id=shot_id,
        payload=payload,
        tenant=tenant,
    )
    return await _serialize_shot(db, project_id, shot)


@router.delete("/{project_id}/shots/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_shot(
    project_id: str,
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> Response:
    await shot_service.delete_shot(
        db,
        project_id=project_id,
        shot_id=shot_id,
        tenant=tenant,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
