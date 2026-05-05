from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InternalRecentUser(BaseModel):
    id: str
    email: str
    organization_id: str
    organization_name: Optional[str] = None
    created_at: Optional[datetime] = None


class InternalRecentOrganization(BaseModel):
    id: str
    name: str
    billing_plan: str
    is_active: bool
    created_at: Optional[datetime] = None


class InternalRecentProject(BaseModel):
    id: str
    name: str
    organization_id: str
    status: str
    created_at: Optional[datetime] = None


class InternalDashboardSummary(BaseModel):
    total_users: int
    total_organizations: int
    active_users: int
    pending_demo_requests: int
    pending_partner_interests: int
    active_organizations: int
    total_projects: int
    recent_users: list[InternalRecentUser]
    recent_organizations: list[InternalRecentOrganization]
    recent_projects: list[InternalRecentProject]


class InternalUserSummary(BaseModel):
    id: str
    email: str
    organization_id: str
    organization_name: Optional[str] = None
    role: str
    billing_plan: str
    effective_plan: str
    program: str
    signup_type: str
    account_status: str
    access_level: str
    cid_enabled: bool
    onboarding_completed: bool
    created_at: Optional[datetime] = None


class InternalOrganizationReference(BaseModel):
    id: str
    name: str
    billing_plan: str
    is_active: bool
    created_at: Optional[datetime] = None


class InternalUsageSummary(BaseModel):
    project_count: int
    job_count: int


class InternalUserDetail(InternalUserSummary):
    organization: Optional[InternalOrganizationReference] = None
    usage: InternalUsageSummary


class PaginatedInternalUsers(BaseModel):
    items: list[InternalUserSummary]
    total: int
    limit: int
    offset: int


class InternalOrganizationSummary(BaseModel):
    id: str
    name: str
    billing_plan: str
    is_active: bool
    created_at: Optional[datetime] = None
    user_count: int
    project_count: int


class PaginatedInternalOrganizations(BaseModel):
    items: list[InternalOrganizationSummary]
    total: int
    limit: int
    offset: int


class InternalOrganizationDetail(BaseModel):
    organization: InternalOrganizationSummary
    users: list[InternalUserSummary]
    project_count: int
    recent_projects: list[InternalRecentProject]
    effective_plan_summary: dict[str, int]
