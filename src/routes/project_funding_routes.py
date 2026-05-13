from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext
from services.project_funding_service import project_funding_service
from services.budget_estimator_service import budget_estimator_service
from schemas.opportunity_tracking_schema import (
    OpportunityTrackingCreate,
    OpportunityTrackingUpdate,
    OpportunityTrackingResponse,
)
from schemas.requirement_checklist_item_schema import (
    RequirementChecklistItemResponse,
    RequirementChecklistItemUpdate,
)


router = APIRouter(prefix="/api/projects", tags=["project-funding"])


class ProjectFundingSourceCreate(BaseModel):
    source_name: str
    source_type: str
    amount: float
    currency: str = "EUR"
    status: str = "projected"
    notes: Optional[str] = None


class ProjectFundingSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("/{project_id}/funding/private-sources")
async def list_private_funding_sources(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    sources = await project_funding_service.list_sources(
        db, project_id, str(project.organization_id)
    )

    return JSONResponse(content={
        "project_id": project_id,
        "count": len(sources),
        "sources": sources,
    })


@router.post("/{project_id}/funding/private-sources")
async def create_private_funding_source(
    project_id: str,
    payload: ProjectFundingSourceCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    source = await project_funding_service.create_source(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        source_name=payload.source_name,
        source_type=payload.source_type,
        amount=payload.amount,
        currency=payload.currency,
        status=payload.status,
        notes=payload.notes,
    )

    return JSONResponse(content={
        "project_id": project_id,
        "source": source,
    })


@router.patch("/{project_id}/funding/private-sources/{source_id}")
async def update_private_funding_source(
    project_id: str,
    source_id: str,
    payload: ProjectFundingSourceUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    source = await project_funding_service.update_source(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        source_id=source_id,
        source_name=payload.source_name,
        source_type=payload.source_type,
        amount=payload.amount,
        currency=payload.currency,
        status=payload.status,
        notes=payload.notes,
    )

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return JSONResponse(content={
        "project_id": project_id,
        "source": source,
    })


@router.delete("/{project_id}/funding/private-sources/{source_id}")
async def delete_private_funding_source(
    project_id: str,
    source_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    deleted = await project_funding_service.delete_source(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        source_id=source_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")

    return JSONResponse(content={
        "project_id": project_id,
        "status": "deleted",
    })


@router.get("/{project_id}/funding/private-summary")
async def get_private_funding_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    summary = await project_funding_service.get_summary(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
    )

    return JSONResponse(content={
        "project_id": project_id,
        **summary,
    })


# Opportunity Tracking Endpoints
@router.post("/{project_id}/funding/tracking")
async def create_opportunity_tracking(
    project_id: str,
    funding_call_id: str,
    project_funding_match_id: Optional[str] = None,
    status: Optional[str] = "interested",
    priority: Optional[str] = None,
    owner_user_id: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    tracking = await project_funding_service.create_tracking(
        db=db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        funding_call_id=funding_call_id,
        project_funding_match_id=project_funding_match_id,
        status=status,
        priority=priority,
        owner_user_id=owner_user_id,
        notes=notes,
    )

    return JSONResponse(content={
        "project_id": project_id,
        "tracking": tracking,
    })


@router.get("/{project_id}/funding/tracking")
async def list_opportunity_trackings(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    trackings = await project_funding_service.get_trackings_for_project(
        db=db,
        project_id=project_id,
        organization_id=str(project.organization_id),
    )

    return JSONResponse(content={
        "project_id": project_id,
        "trackings": trackings,
    })


@router.get("/{project_id}/funding/tracking/{tracking_id}")
async def get_opportunity_tracking(
    project_id: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    tracking = await project_funding_service.get_tracking(
        db=db,
        tracking_id=tracking_id,
        organization_id=str(project.organization_id),
    )
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    return JSONResponse(content={
        "project_id": project_id,
        "tracking": tracking,
    })


@router.patch("/{project_id}/funding/tracking/{tracking_id}")
async def update_opportunity_tracking(
    project_id: str,
    tracking_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    owner_user_id: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    tracking = await project_funding_service.update_tracking(
        db=db,
        tracking_id=tracking_id,
        organization_id=str(project.organization_id),
        status=status,
        priority=priority,
        owner_user_id=owner_user_id,
        notes=notes,
    )
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    return JSONResponse(content={
        "project_id": project_id,
        "tracking": tracking,
    })


@router.delete("/{project_id}/funding/tracking/{tracking_id}")
async def delete_opportunity_tracking(
    project_id: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    deleted = await project_funding_service.delete_tracking(
        db=db,
        tracking_id=tracking_id,
        organization_id=str(project.organization_id),
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Tracking not found")

    return JSONResponse(content={
        "project_id": project_id,
        "status": "deleted",
    })


# Checklist Endpoints
@router.get("/{project_id}/funding/tracking/{tracking_id}/checklist")
async def get_tracking_checklist(
    project_id: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    checklist_items = await project_funding_service.get_checklist_for_tracking(
        db=db,
        tracking_id=tracking_id,
        organization_id=str(project.organization_id),
    )

    return JSONResponse(content={
        "project_id": project_id,
        "tracking_id": tracking_id,
        "checklist_items": checklist_items,
    })


@router.patch("/{project_id}/funding/tracking/{tracking_id}/checklist/{item_id}")
async def update_tracking_checklist_item(
    project_id: str,
    tracking_id: str,
    item_id: str,
    label: Optional[str] = None,
    requirement_type: Optional[str] = None,
    is_fulfilled: Optional[bool] = None,
    auto_detected: Optional[bool] = None,
    linked_project_document_id: Optional[str] = None,
    evidence_excerpt: Optional[str] = None,
    due_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    item = await project_funding_service.update_checklist_item(
        db=db,
        item_id=item_id,
        organization_id=str(project.organization_id),
        label=label,
        requirement_type=requirement_type,
        is_fulfilled=is_fulfilled,
        auto_detected=auto_detected,
        linked_project_document_id=linked_project_document_id,
        evidence_excerpt=evidence_excerpt,
        due_date=due_date,
        notes=notes,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    return JSONResponse(content={
        "project_id": project_id,
        "tracking_id": tracking_id,
        "checklist_item": item,
    })


# Notification Endpoints
@router.get("/{project_id}/funding/notifications")
async def get_project_notifications(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    notifications = await project_funding_service.get_notifications_for_project(
        db=db,
        project_id=project_id,
        organization_id=str(project.organization_id),
    )

    return JSONResponse(content={
        "project_id": project_id,
        "notifications": notifications,
    })


@router.patch("/{project_id}/funding/notifications/{notification_id}/read")
async def mark_notification_as_read(
    project_id: str,
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write_check: TenantContext = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    notification = await project_funding_service.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        organization_id=str(project.organization_id),
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return JSONResponse(content={
        "project_id": project_id,
        "notification": notification,
    })