from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Organization, Project, ProjectJob
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from pydantic import BaseModel
from services.instance_registry import registry
from services.job_scheduler import scheduler
from services.queue_service import queue_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

class AdminOrganizationStats(BaseModel):
    id: str
    name: str
    project_count: int
    job_count: int


def _require_admin(tenant: TenantContext) -> None:
    if not tenant.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")


@router.get("/system/overview")
async def admin_system_overview(
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Legacy admin overview payload kept for frontend compatibility."""
    _require_admin(tenant)

    instances_status = registry.get_status_summary()
    queue_status = queue_service.get_all_status()
    scheduler_status = await scheduler.get_status()

    total_running = sum(status.get("running", 0) for status in queue_status.values())
    total_queued = sum(status.get("queue_size", 0) for status in queue_status.values())

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "scheduler": {
            "running": scheduler_status.get("running", False),
            "poll_interval": scheduler_status.get("poll_interval", 0),
            "job_timeout": scheduler_status.get("job_timeout", 0),
        },
        "queue": queue_status,
        "backends": instances_status.get("backends", {}),
        "summary": {
            "total_backends": instances_status.get("total_backends", 0),
            "available_backends": instances_status.get("available_backends", 0),
            "total_running": total_running,
            "total_queued": total_queued,
        },
    }


@router.get("/scheduler/status")
async def admin_scheduler_status(
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Legacy scheduler status payload kept for frontend compatibility."""
    _require_admin(tenant)
    return await scheduler.get_status()

@router.get("/projects")
async def admin_list_all_projects(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List all projects across all tenants. Restricted to global admins."""
    _require_admin(tenant)
    
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "organization_id": str(p.organization_id),
            "created_at": p.created_at
        } for p in projects
    ]

@router.get("/jobs")
async def admin_list_all_jobs(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List all jobs across all tenants. Restricted to global admins."""
    _require_admin(tenant)
    
    result = await db.execute(select(ProjectJob).order_by(ProjectJob.created_at.desc()))
    jobs = result.scalars().all()
    
    return [
        {
            "id": str(j.id),
            "project_id": str(j.project_id),
            "job_type": j.job_type,
            "status": j.status,
            "created_at": j.created_at
        } for j in jobs
    ]

@router.get("/organizations")
async def admin_list_organizations(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> List[AdminOrganizationStats]:
    """Overview of all organizations and their usage. Restricted to global admins."""
    _require_admin(tenant)
    
    # Simple join to get counts
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    
    stats = []
    for org in orgs:
        p_count = await db.scalar(select(func.count(Project.id)).where(Project.organization_id == org.id))
        # ProjectJob doesn't have org_id yet, but we could join via project or add it later
        # For now, let's keep it simple
        stats.append(AdminOrganizationStats(
            id=str(org.id),
            name=str(org.name),
            project_count=p_count or 0,
            job_count=0 # Placeholder for now
        ))
    
    return stats
