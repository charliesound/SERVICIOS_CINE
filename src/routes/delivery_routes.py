import os
import json
from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from models.delivery import Deliverable, DeliverableStatus
from schemas.delivery_schema import (
    DeliverableCreate,
    DeliverableListResponse,
    DeliverableResponse,
    DeliverableUpdate,
)
from services.delivery_service import delivery_service
from routes.auth_routes import (
    get_current_user_optional,
    check_project_ownership,
    get_tenant_context,
)
from schemas.auth_schema import UserResponse, TenantContext
from services.logging_service import logger
from services.export_service import export_service
from services.plan_limits_service import plan_limits_service
from routes.project_routes import _enforce_export_permission


router = APIRouter(prefix="/api/delivery", tags=["delivery"])


async def _get_project_for_tenant_or_admin(
    db: AsyncSession, project_id: str, tenant: TenantContext
) -> Project | None:
    query = select(Project).where(Project.id == project_id)
    if not tenant.is_admin:
        query = query.where(Project.organization_id == tenant.organization_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def _get_deliverable_for_tenant_or_admin(
    db: AsyncSession, deliverable_id: str, tenant: TenantContext
) -> Deliverable | None:
    query = select(Deliverable).where(Deliverable.id == deliverable_id)
    if not tenant.is_admin:
        query = query.where(Deliverable.organization_id == tenant.organization_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


def _deliverable_response(deliverable: Deliverable) -> DeliverableResponse:
    source_review_id = cast(
        Optional[str], getattr(deliverable, "source_review_id", None)
    )
    updated_at = cast(Optional[datetime], getattr(deliverable, "updated_at", None))
    created_at = cast(datetime, deliverable.created_at)
    payload = getattr(deliverable, "delivery_payload", None)
    return DeliverableResponse(
        id=str(deliverable.id),
        project_id=str(deliverable.project_id),
        source_review_id=str(source_review_id)
        if source_review_id is not None
        else None,
        name=cast(str, deliverable.name),
        format_type=cast(str, deliverable.format_type),
        delivery_payload=payload if isinstance(payload, dict) else {},
        status=str(deliverable.status),
        created_at=created_at,
        updated_at=updated_at or created_at,
    )


@router.get(
    "/projects/{project_id}/deliverables", response_model=DeliverableListResponse
)
async def list_deliverables(
    project_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableListResponse:
    project = await _get_project_for_tenant_or_admin(db, project_id, tenant)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    deliverables = await delivery_service.list_deliverables(
        db,
        project_id,
        str(project.organization_id),
        status,
    )
    return DeliverableListResponse(
        deliverables=[
            _deliverable_response(deliverable) for deliverable in deliverables
        ]
    )


@router.get("/deliverables/{deliverable_id}", response_model=DeliverableResponse)
async def get_deliverable_detail(
    deliverable_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableResponse:
    deliverable = await _get_deliverable_for_tenant_or_admin(db, deliverable_id, tenant)

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    return _deliverable_response(deliverable)


@router.get("/reviews/{review_id}/deliverable", response_model=DeliverableResponse)
async def get_deliverable_from_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableResponse:
    deliverable = await delivery_service.get_deliverable_by_review(
        db,
        review_id,
        tenant.organization_id,
    )

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found for review")

    return _deliverable_response(deliverable)


@router.post("/projects/{project_id}/deliverables", response_model=DeliverableResponse)
async def create_deliverable(
    project_id: str,
    deliverable: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableResponse:
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id, Project.organization_id == tenant.organization_id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_deliverable = await delivery_service.create_deliverable(
        db,
        project_id=project_id,
        organization_id=tenant.organization_id,
        source_review_id=deliverable.source_review_id,
        name=deliverable.name,
        format_type=deliverable.format_type,
        delivery_payload=deliverable.delivery_payload,
    )

    return _deliverable_response(db_deliverable)


@router.patch("/deliverables/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: str,
    update: DeliverableUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableResponse:
    deliverable = await delivery_service.get_deliverable(
        db, deliverable_id, tenant.organization_id
    )

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if update.status is not None:
        deliverable = await delivery_service.update_status(
            db, deliverable, update.status
        )

    return _deliverable_response(deliverable)


@router.get("/deliverables/{deliverable_id}/download")
async def download_deliverable(
    deliverable_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
): 
    deliverable = await _get_deliverable_for_tenant_or_admin(db, deliverable_id, tenant)
    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if str(deliverable.status).lower() != DeliverableStatus.READY:
        raise HTTPException(
            status_code=400,
            detail=f"Deliverable is not ready (status: {deliverable.status})",
        )

    payload = deliverable.delivery_payload or {}
    file_path_str = payload.get("file_path")
    file_name = payload.get("file_name", "export.zip")

    if not file_path_str or not os.path.exists(file_path_str):
        raise HTTPException(status_code=404, detail="Physical file not found on server")

    return FileResponse(
        path=file_path_str, filename=file_name, media_type="application/zip"
    )


@router.post("/projects/{project_id}/export")
async def trigger_project_export(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
): 
    project = await _get_project_for_tenant_or_admin(db, project_id, tenant)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Enforce plan permissions for ZIP export
    await _enforce_export_permission(tenant.plan, export_format="zip")

    job = await export_service.trigger_project_export(
        project_id=project_id,
        organization_id=str(project.organization_id),
        user_id=tenant.user_id,
    )

    return {"job_id": str(job.id), "status": job.status}
