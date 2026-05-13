from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.security import TokenData, get_token_data, optional_internal_api_key
from models.core import Project
from schemas.auth_schema import TenantContext
from services.account_service import get_user_by_id, resolve_effective_plan
from services.tenant_access_service import can_write_project, get_project_for_tenant

logger = logging.getLogger("servicios_cine.tenant_context")


async def get_tenant_context(
    request: Request,
    token: Optional[TokenData] = Depends(get_token_data),
    db: AsyncSession = Depends(get_db),
    internal_key: Optional[str] = Depends(optional_internal_api_key),
) -> TenantContext:
    if token is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    auth_method = "jwt"
    org_id = token.organization_id

    if internal_key:
        auth_method = "internal_api_key"

    if not org_id:
        raise HTTPException(
            status_code=403,
            detail="Account is not associated with any organization",
        )

    is_admin = "admin" in token.roles
    is_global_admin = "global_admin" in token.roles

    user_id = token.sub
    role = token.roles[0] if token.roles else "viewer"

    plan = "free"
    if user_id and user_id != "dev-bypass":
        user_record = await get_user_by_id(db, str(user_id))
        if user_record:
            plan = await resolve_effective_plan(db, user_record)
            role = user_record.access_level or role

    return TenantContext(
        user_id=user_id or "",
        organization_id=org_id,
        plan=plan,
        role=role,
        is_admin=is_admin,
        is_global_admin=is_global_admin,
        auth_method=auth_method,
    )


async def require_organization(
    tenant: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    if not tenant.organization_id:
        raise HTTPException(
            status_code=403,
            detail="Account is not associated with any organization",
        )
    return tenant


async def validate_project_access(
    project_id: str,
    tenant: TenantContext = Depends(require_organization),
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = await get_project_for_tenant(db, project_id, tenant.organization_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    return project


def require_project_scope(scope: str):
    async def _validator(
        project: Project = Depends(validate_project_access),
        tenant: TenantContext = Depends(require_organization),
    ) -> Project:
        if tenant.is_global_admin:
            return project
        if scope not in getattr(tenant, "scopes", []) and scope not in tenant.role:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient scope: {scope}",
            )
        return project

    return _validator


async def require_write_permission(
    tenant: TenantContext = Depends(require_organization),
) -> TenantContext:
    if not can_write_project(tenant):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions: write access required",
        )
    return tenant
