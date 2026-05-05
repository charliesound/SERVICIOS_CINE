from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Organization, Project, ProjectJob, User as DBUser
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.internal_admin_schema import (
    InternalDashboardSummary,
    InternalOrganizationDetail,
    InternalOrganizationReference,
    InternalOrganizationSummary,
    InternalRecentOrganization,
    InternalRecentProject,
    InternalRecentUser,
    InternalUsageSummary,
    InternalUserDetail,
    InternalUserSummary,
    PaginatedInternalOrganizations,
    PaginatedInternalUsers,
)
from services.account_service import resolve_effective_plan
from services.instance_registry import registry
from services.job_scheduler import scheduler
from services.queue_service import queue_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminOrganizationStats(BaseModel):
    id: str
    name: str
    project_count: int
    job_count: int


def require_admin(tenant: TenantContext) -> None:
    if not tenant.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")


async def _scalar_count(db: AsyncSession, statement) -> int:
    return int(await db.scalar(statement) or 0)


async def _load_organizations_map(
    db: AsyncSession,
    organization_ids: set[str],
) -> dict[str, Organization]:
    if not organization_ids:
        return {}

    result = await db.execute(
        select(Organization).where(Organization.id.in_(organization_ids))
    )
    organizations = result.scalars().all()
    return {str(org.id): org for org in organizations}


async def _group_count_by_org(
    db: AsyncSession,
    model,
    organization_ids: set[str],
) -> dict[str, int]:
    if not organization_ids:
        return {}

    result = await db.execute(
        select(model.organization_id, func.count())
        .where(model.organization_id.in_(organization_ids))
        .group_by(model.organization_id)
    )
    return {str(org_id): int(count) for org_id, count in result.all()}


async def _serialize_user_summary(
    db: AsyncSession,
    user: DBUser,
    organization: Optional[Organization],
) -> InternalUserSummary:
    effective_plan = await resolve_effective_plan(db, user, organization)
    # Read-only admin responses intentionally expose only non-secret profile fields.
    return InternalUserSummary(
        id=str(user.id),
        email=str(user.email),
        organization_id=str(user.organization_id),
        organization_name=(str(organization.name) if organization else None),
        role=str(user.role),
        billing_plan=(getattr(user, "billing_plan", None) or "free"),
        effective_plan=effective_plan,
        program=(getattr(user, "program", None) or "demo"),
        signup_type=(getattr(user, "signup_type", None) or "cid_user"),
        account_status=(getattr(user, "account_status", None) or "active"),
        access_level=(getattr(user, "access_level", None) or "standard"),
        cid_enabled=bool(getattr(user, "cid_enabled", True)),
        onboarding_completed=bool(getattr(user, "onboarding_completed", False)),
        created_at=user.created_at,
    )


def _serialize_org_reference(org: Optional[Organization]) -> Optional[InternalOrganizationReference]:
    if org is None:
        return None

    return InternalOrganizationReference(
        id=str(org.id),
        name=str(org.name),
        billing_plan=(getattr(org, "billing_plan", None) or "free"),
        is_active=bool(getattr(org, "is_active", True)),
        created_at=org.created_at,
    )


def _serialize_recent_user(user: DBUser, organization: Optional[Organization]) -> InternalRecentUser:
    return InternalRecentUser(
        id=str(user.id),
        email=str(user.email),
        organization_id=str(user.organization_id),
        organization_name=(str(organization.name) if organization else None),
        created_at=user.created_at,
    )


def _serialize_recent_organization(org: Organization) -> InternalRecentOrganization:
    return InternalRecentOrganization(
        id=str(org.id),
        name=str(org.name),
        billing_plan=(getattr(org, "billing_plan", None) or "free"),
        is_active=bool(getattr(org, "is_active", True)),
        created_at=org.created_at,
    )


def _serialize_recent_project(project: Project) -> InternalRecentProject:
    return InternalRecentProject(
        id=str(project.id),
        name=str(project.name),
        organization_id=str(project.organization_id),
        status=(getattr(project, "status", None) or "active"),
        created_at=project.created_at,
    )


@router.get("/system/overview")
async def admin_system_overview(
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Legacy admin overview payload kept for frontend compatibility."""
    require_admin(tenant)

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
    require_admin(tenant)
    return await scheduler.get_status()


@router.get("/projects")
async def admin_list_all_projects(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List all projects across all tenants. Restricted to global admins."""
    require_admin(tenant)

    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()

    return [
        {
            "id": str(project.id),
            "name": project.name,
            "organization_id": str(project.organization_id),
            "created_at": project.created_at,
        }
        for project in projects
    ]


@router.get("/jobs")
async def admin_list_all_jobs(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List all jobs across all tenants. Restricted to global admins."""
    require_admin(tenant)

    result = await db.execute(select(ProjectJob).order_by(ProjectJob.created_at.desc()))
    jobs = result.scalars().all()

    return [
        {
            "id": str(job.id),
            "project_id": str(job.project_id),
            "job_type": job.job_type,
            "status": job.status,
            "created_at": job.created_at,
        }
        for job in jobs
    ]


@router.get("/organizations")
async def admin_list_organizations(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[AdminOrganizationStats]:
    """Overview of all organizations and their usage. Restricted to global admins."""
    require_admin(tenant)

    result = await db.execute(select(Organization))
    organizations = result.scalars().all()

    stats = []
    for org in organizations:
        project_count = await db.scalar(
            select(func.count(Project.id)).where(Project.organization_id == org.id)
        )
        stats.append(
            AdminOrganizationStats(
                id=str(org.id),
                name=str(org.name),
                project_count=int(project_count or 0),
                job_count=0,
            )
        )

    return stats


@router.get("/internal/dashboard", response_model=InternalDashboardSummary)
async def admin_internal_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> InternalDashboardSummary:
    require_admin(tenant)

    total_users = await _scalar_count(db, select(func.count(DBUser.id)))
    total_organizations = await _scalar_count(db, select(func.count(Organization.id)))
    active_users = await _scalar_count(
        db,
        select(func.count(DBUser.id)).where(DBUser.account_status == "active"),
    )
    pending_demo_requests = await _scalar_count(
        db,
        select(func.count(DBUser.id)).where(
            DBUser.signup_type == "demo_request",
            DBUser.account_status == "pending",
        ),
    )
    pending_partner_interests = await _scalar_count(
        db,
        select(func.count(DBUser.id)).where(
            DBUser.signup_type == "partner_interest",
            DBUser.account_status == "pending",
        ),
    )
    active_organizations = await _scalar_count(
        db,
        select(func.count(Organization.id)).where(Organization.is_active.is_(True)),
    )
    total_projects = await _scalar_count(db, select(func.count(Project.id)))

    recent_users_result = await db.execute(
        select(DBUser).order_by(DBUser.created_at.desc()).limit(10)
    )
    recent_users = recent_users_result.scalars().all()
    user_org_map = await _load_organizations_map(
        db,
        {str(user.organization_id) for user in recent_users},
    )

    recent_orgs_result = await db.execute(
        select(Organization).order_by(Organization.created_at.desc()).limit(10)
    )
    recent_organizations = recent_orgs_result.scalars().all()

    recent_projects_result = await db.execute(
        select(Project).order_by(Project.created_at.desc()).limit(10)
    )
    recent_projects = recent_projects_result.scalars().all()

    return InternalDashboardSummary(
        total_users=total_users,
        total_organizations=total_organizations,
        active_users=active_users,
        pending_demo_requests=pending_demo_requests,
        pending_partner_interests=pending_partner_interests,
        active_organizations=active_organizations,
        total_projects=total_projects,
        recent_users=[
            _serialize_recent_user(user, user_org_map.get(str(user.organization_id)))
            for user in recent_users
        ],
        recent_organizations=[
            _serialize_recent_organization(org) for org in recent_organizations
        ],
        recent_projects=[_serialize_recent_project(project) for project in recent_projects],
    )


@router.get("/internal/users", response_model=PaginatedInternalUsers)
async def admin_internal_users(
    q: Optional[str] = Query(default=None),
    signup_type: Optional[str] = Query(default=None),
    account_status: Optional[str] = Query(default=None),
    billing_plan: Optional[str] = Query(default=None),
    access_level: Optional[str] = Query(default=None),
    cid_enabled: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PaginatedInternalUsers:
    require_admin(tenant)

    filters = []
    if q:
        search = f"%{q.strip()}%"
        filters.append(
            or_(
                DBUser.email.ilike(search),
                DBUser.username.ilike(search),
                DBUser.full_name.ilike(search),
                DBUser.company.ilike(search),
                Organization.name.ilike(search),
            )
        )
    if signup_type:
        filters.append(DBUser.signup_type == signup_type)
    if account_status:
        filters.append(DBUser.account_status == account_status)
    if billing_plan:
        filters.append(DBUser.billing_plan == billing_plan)
    if access_level:
        filters.append(DBUser.access_level == access_level)
    if cid_enabled is not None:
        filters.append(DBUser.cid_enabled.is_(cid_enabled))

    base_query = select(DBUser).outerjoin(
        Organization, Organization.id == DBUser.organization_id
    )
    count_query = select(func.count(DBUser.id)).select_from(DBUser).outerjoin(
        Organization, Organization.id == DBUser.organization_id
    )

    if filters:
        base_query = base_query.where(*filters)
        count_query = count_query.where(*filters)

    total = await _scalar_count(db, count_query)
    result = await db.execute(
        base_query.order_by(DBUser.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    organizations_map = await _load_organizations_map(
        db,
        {str(user.organization_id) for user in users},
    )

    items = [
        await _serialize_user_summary(
            db,
            user,
            organizations_map.get(str(user.organization_id)),
        )
        for user in users
    ]

    return PaginatedInternalUsers(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/internal/users/{user_id}", response_model=InternalUserDetail)
async def admin_internal_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> InternalUserDetail:
    require_admin(tenant)

    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    organization = None
    if user.organization_id:
        org_result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = org_result.scalar_one_or_none()

    project_count = await _scalar_count(
        db,
        select(func.count(Project.id)).where(Project.organization_id == user.organization_id),
    )
    job_count = await _scalar_count(
        db,
        select(func.count(ProjectJob.id)).where(
            ProjectJob.organization_id == user.organization_id
        ),
    )

    summary = await _serialize_user_summary(db, user, organization)
    return InternalUserDetail(
        id=summary.id,
        email=summary.email,
        organization_id=summary.organization_id,
        organization_name=summary.organization_name,
        role=summary.role,
        billing_plan=summary.billing_plan,
        effective_plan=summary.effective_plan,
        program=summary.program,
        signup_type=summary.signup_type,
        account_status=summary.account_status,
        access_level=summary.access_level,
        cid_enabled=summary.cid_enabled,
        onboarding_completed=summary.onboarding_completed,
        created_at=summary.created_at,
        organization=_serialize_org_reference(organization),
        usage=InternalUsageSummary(project_count=project_count, job_count=job_count),
    )


@router.get("/internal/organizations", response_model=PaginatedInternalOrganizations)
async def admin_internal_organizations(
    q: Optional[str] = Query(default=None),
    billing_plan: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PaginatedInternalOrganizations:
    require_admin(tenant)

    filters = []
    if q:
        search = f"%{q.strip()}%"
        filters.append(or_(Organization.name.ilike(search), Organization.id.ilike(search)))
    if billing_plan:
        filters.append(Organization.billing_plan == billing_plan)
    if is_active is not None:
        filters.append(Organization.is_active.is_(is_active))

    query = select(Organization)
    count_query = select(func.count(Organization.id))
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    total = await _scalar_count(db, count_query)
    result = await db.execute(
        query.order_by(Organization.created_at.desc()).offset(offset).limit(limit)
    )
    organizations = result.scalars().all()
    organization_ids = {str(org.id) for org in organizations}
    user_counts = await _group_count_by_org(db, DBUser, organization_ids)
    project_counts = await _group_count_by_org(db, Project, organization_ids)

    items = [
        InternalOrganizationSummary(
            id=str(org.id),
            name=str(org.name),
            billing_plan=(getattr(org, "billing_plan", None) or "free"),
            is_active=bool(getattr(org, "is_active", True)),
            created_at=org.created_at,
            user_count=user_counts.get(str(org.id), 0),
            project_count=project_counts.get(str(org.id), 0),
        )
        for org in organizations
    ]

    return PaginatedInternalOrganizations(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/internal/organizations/{organization_id}", response_model=InternalOrganizationDetail)
async def admin_internal_organization_detail(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> InternalOrganizationDetail:
    require_admin(tenant)

    org_result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = org_result.scalar_one_or_none()
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    users_result = await db.execute(
        select(DBUser)
        .where(DBUser.organization_id == organization_id)
        .order_by(DBUser.created_at.desc())
    )
    users = users_result.scalars().all()

    projects_result = await db.execute(
        select(Project)
        .where(Project.organization_id == organization_id)
        .order_by(Project.created_at.desc())
        .limit(10)
    )
    recent_projects = projects_result.scalars().all()

    project_count = await _scalar_count(
        db,
        select(func.count(Project.id)).where(Project.organization_id == organization_id),
    )

    effective_plan_summary: dict[str, int] = {}
    user_items: list[InternalUserSummary] = []
    for user in users:
        user_summary = await _serialize_user_summary(db, user, organization)
        user_items.append(user_summary)
        effective_plan_summary[user_summary.effective_plan] = (
            effective_plan_summary.get(user_summary.effective_plan, 0) + 1
        )

    organization_summary = InternalOrganizationSummary(
        id=str(organization.id),
        name=str(organization.name),
        billing_plan=(getattr(organization, "billing_plan", None) or "free"),
        is_active=bool(getattr(organization, "is_active", True)),
        created_at=organization.created_at,
        user_count=len(user_items),
        project_count=project_count,
    )

    return InternalOrganizationDetail(
        organization=organization_summary,
        users=user_items,
        project_count=project_count,
        recent_projects=[_serialize_recent_project(project) for project in recent_projects],
        effective_plan_summary=effective_plan_summary,
    )


@router.get("/internal/demo-requests", response_model=PaginatedInternalUsers)
async def admin_internal_demo_requests(
    account_status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PaginatedInternalUsers:
    require_admin(tenant)

    filters = [DBUser.signup_type == "demo_request"]
    if account_status:
        filters.append(DBUser.account_status == account_status)

    total = await _scalar_count(
        db,
        select(func.count(DBUser.id)).where(*filters),
    )
    result = await db.execute(
        select(DBUser)
        .where(*filters)
        .order_by(DBUser.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()
    organizations_map = await _load_organizations_map(
        db,
        {str(user.organization_id) for user in users},
    )

    items = [
        await _serialize_user_summary(
            db,
            user,
            organizations_map.get(str(user.organization_id)),
        )
        for user in users
    ]

    return PaginatedInternalUsers(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/internal/partner-interests", response_model=PaginatedInternalUsers)
async def admin_internal_partner_interests(
    account_status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PaginatedInternalUsers:
    require_admin(tenant)

    filters = [DBUser.signup_type == "partner_interest"]
    if account_status:
        filters.append(DBUser.account_status == account_status)

    total = await _scalar_count(
        db,
        select(func.count(DBUser.id)).where(*filters),
    )
    result = await db.execute(
        select(DBUser)
        .where(*filters)
        .order_by(DBUser.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()
    organizations_map = await _load_organizations_map(
        db,
        {str(user.organization_id) for user in users},
    )

    items = [
        await _serialize_user_summary(
            db,
            user,
            organizations_map.get(str(user.organization_id)),
        )
        for user in users
    ]

    return PaginatedInternalUsers(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
