"""
Change governance routes.
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from dependencies.tenant_context import (
    get_tenant_context,
    require_organization,
    validate_project_access,
    require_write_permission,
)
from models.core import Project
from models.change_governance import ProjectChangeRequest, CHANGE_REQUEST_STATUSES
from schemas.auth_schema import TenantContext
from services.change_governance_service import (
    create_change_request,
    list_change_requests,
    approve_change_request,
    reject_change_request,
    apply_approved_change,
    create_change_requests_from_script_change,
    get_pending_changes_count,
    can_approve,
)


router = APIRouter(
    prefix="/api/projects/{project_id}/change-requests",
    tags=["change-requests"],
    dependencies=[Depends(get_tenant_context)],
)


class CreateChangeRequestPayload(BaseModel):
    source_type: str
    target_module: str
    title: str
    change_type: str = "updated"
    severity: str = "medium"
    summary: Optional[str] = None
    before_json: Optional[dict] = None
    after_json: Optional[dict] = None
    impact_json: Optional[dict] = None
    recommended_action: Optional[str] = None
    source_id: Optional[str] = None


class ApprovePayload(BaseModel):
    comment: Optional[str] = None


class RejectPayload(BaseModel):
    comment: Optional[str] = None


@router.get("")
async def list_change_requests_endpoint(
    project_id: str,
    status: Optional[str] = None,
    target_module: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
):
    """List change requests for a project."""
    requests = await list_change_requests(db, project_id, status, target_module)
    return {
        "change_requests": [
            {
                "id": r.id,
                "source_type": r.source_type,
                "target_module": r.target_module,
                "change_type": r.change_type,
                "severity": r.severity,
                "title": r.title,
                "summary": r.summary,
                "status": r.status,
                "impact_json": r.impact_json,
                "recommended_action": r.recommended_action,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            }
            for r in requests
        ]
    }


@router.post("")
async def create_change_request_endpoint(
    project_id: str,
    payload: CreateChangeRequestPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
    _: TenantContext = Depends(require_write_permission),
):
    """Create a new change request."""
    if not await can_approve(tenant.role, payload.target_module):
        raise HTTPException(status_code=403, detail="Cannot create change request")
    
    request = await create_change_request(
        db, project_id, project.organization_id,
        source_type=payload.source_type,
        target_module=payload.target_module,
        title=payload.title,
        change_type=payload.change_type,
        severity=payload.severity,
        summary=payload.summary,
        before_json=payload.before_json,
        after_json=payload.after_json,
        impact_json=payload.impact_json,
        recommended_action=payload.recommended_action,
        created_by=tenant.user_id,
        source_id=payload.source_id,
    )
    
    return {
        "id": request.id,
        "status": request.status,
    }


@router.get("/{change_request_id}")
async def get_change_request(
    project_id: str,
    change_request_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
):
    """Get a change request."""
    result = await db.execute(
        select(ProjectChangeRequest).where(ProjectChangeRequest.id == change_request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request or request.project_id != project_id:
        raise HTTPException(status_code=404, detail="Change request not found")
    
    return {
        "id": request.id,
        "source_type": request.source_type,
        "target_module": request.target_module,
        "change_type": request.change_type,
        "severity": request.severity,
        "title": request.title,
        "summary": request.summary,
        "before_json": request.before_json,
        "after_json": request.after_json,
        "impact_json": request.impact_json,
        "recommended_action": request.recommended_action,
        "status": request.status,
        "created_by": request.created_by,
        "approved_by": request.approved_by,
        "created_at": request.created_at.isoformat() if request.created_at else None,
    }


@router.post("/{change_request_id}/approve")
async def approve_change_request_endpoint(
    project_id: str,
    change_request_id: str,
    payload: ApprovePayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
    _: TenantContext = Depends(require_write_permission),
):
    """Approve a change request."""
    result = await db.execute(
        select(ProjectChangeRequest).where(ProjectChangeRequest.id == change_request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request or request.project_id != project_id:
        raise HTTPException(status_code=404, detail="Change request not found")
    
    if not await can_approve(tenant.role, request.target_module):
        raise HTTPException(status_code=403, detail="Cannot approve this module")
    
    request = await approve_change_request(
        db, change_request_id, tenant.user_id, tenant.role, payload.comment
    )
    
    return {
        "id": request.id,
        "status": request.status,
    }


@router.post("/{change_request_id}/reject")
async def reject_change_request_endpoint(
    project_id: str,
    change_request_id: str,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
    _: TenantContext = Depends(require_write_permission),
):
    """Reject a change request."""
    result = await db.execute(
        select(ProjectChangeRequest).where(ProjectChangeRequest.id == change_request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request or request.project_id != project_id:
        raise HTTPException(status_code=404, detail="Change request not found")
    
    if not await can_approve(tenant.role, request.target_module):
        raise HTTPException(status_code=403, detail="Cannot reject this module")
    
    request = await reject_change_request(
        db, change_request_id, tenant.user_id, tenant.role, payload.comment
    )
    
    return {
        "id": request.id,
        "status": request.status,
    }


@router.post("/{change_request_id}/apply")
async def apply_change(
    project_id: str,
    change_request_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_organization),
    project: Project = Depends(validate_project_access),
    _: TenantContext = Depends(require_write_permission),
):
    """Apply an approved change."""
    result = await db.execute(
        select(ProjectChangeRequest).where(ProjectChangeRequest.id == change_request_id)
    )
    cr = result.scalar_one_or_none()
    if not cr or cr.project_id != project_id:
        raise HTTPException(status_code=404, detail="Change request not found")
    
    request = await apply_approved_change(db, change_request_id)
    
    return {
        "id": request.id,
        "status": request.status,
    }