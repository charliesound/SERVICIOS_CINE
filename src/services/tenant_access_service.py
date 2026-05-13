from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project, ProjectJob

logger = logging.getLogger("servicios_cine.tenant_access")


async def get_project_for_tenant(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> Optional[Project]:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()


async def assert_project_access(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
) -> Project:
    project = await get_project_for_tenant(db, project_id, organization_id)
    if project is None:
        raise PermissionError("Project not found or access denied")
    return project


def apply_tenant_filter(query, model, organization_id: str):
    return query.where(model.organization_id == organization_id)


def can_write_project(tenant) -> bool:
    if tenant.is_global_admin:
        return True
    if tenant.is_admin:
        return True
    if hasattr(tenant, "role") and tenant.role in ("admin", "owner", "producer", "operator"):
        return True
    return False


def can_read_project(tenant) -> bool:
    return True


async def get_project_job_for_tenant(
    db: AsyncSession,
    job_id: str,
    organization_id: str,
) -> Optional[ProjectJob]:
    result = await db.execute(
        select(ProjectJob).where(
            ProjectJob.id == job_id,
            ProjectJob.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()
