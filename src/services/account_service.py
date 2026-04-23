from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Organization, User as DBUser
from schemas.auth_schema import UserResponse
from services.plan_limits_service import plan_limits_service


def normalize_plan_name(plan_name: Optional[str]) -> str:
    normalized = (plan_name or "free").strip().lower()
    return normalized if plan_limits_service.get_plan(normalized) else "free"


def plan_to_program(plan_name: Optional[str]) -> str:
    normalized = normalize_plan_name(plan_name)
    if normalized in {"creator", "producer", "studio", "enterprise"}:
        return normalized
    return "demo"


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[DBUser]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[DBUser]:
    result = await db.execute(select(DBUser).where(DBUser.email == email))
    return result.scalar_one_or_none()


async def get_organization(
    db: AsyncSession, organization_id: Optional[str]
) -> Optional[Organization]:
    if not organization_id:
        return None
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    return result.scalar_one_or_none()


async def resolve_effective_plan(
    db: AsyncSession,
    user: DBUser,
    organization: Optional[Organization] = None,
) -> str:
    org = organization or await get_organization(db, user.organization_id)
    return normalize_plan_name(
        getattr(user, "billing_plan", None) or getattr(org, "billing_plan", None)
    )


def build_user_response(
    user: DBUser,
    effective_plan: str,
) -> UserResponse:
    username = (
        getattr(user, "username", None)
        or getattr(user, "full_name", None)
        or str(user.email).split("@", 1)[0]
    )
    return UserResponse(
        user_id=str(user.id),
        username=username,
        email=str(user.email),
        plan=effective_plan,
        role=str(user.role),
        is_active=bool(user.is_active),
        program=getattr(user, "program", "demo") or "demo",
        signup_type=getattr(user, "signup_type", "cid_user") or "cid_user",
        account_status=getattr(user, "account_status", "active") or "active",
        access_level=getattr(user, "access_level", "standard") or "standard",
        cid_enabled=bool(getattr(user, "cid_enabled", True)),
        onboarding_completed=bool(getattr(user, "onboarding_completed", False)),
        full_name=getattr(user, "full_name", None),
        company=getattr(user, "company", None),
        country=getattr(user, "country", None),
    )


async def build_user_response_from_db(db: AsyncSession, user: DBUser) -> UserResponse:
    plan_name = await resolve_effective_plan(db, user)
    return build_user_response(user, plan_name)


async def create_user_account(
    db: AsyncSession,
    *,
    username: str,
    email: str,
    hashed_password: str,
    plan: str = "free",
    role: str = "user",
    is_active: bool = True,
    program: str = "demo",
    signup_type: str = "cid_user",
    account_status: str = "active",
    access_level: str = "standard",
    cid_enabled: bool = True,
    onboarding_completed: bool = False,
    full_name: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    organization_name: Optional[str] = None,
) -> DBUser:
    normalized_plan = normalize_plan_name(plan)
    organization = Organization(
        name=(organization_name or username or email.split("@", 1)[0]).strip(),
        billing_plan=normalized_plan,
        is_active=True,
    )
    db.add(organization)
    await db.flush()

    user = DBUser(
        organization_id=str(organization.id),
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=hashed_password,
        full_name=(full_name or username).strip(),
        role=role,
        is_active=is_active,
        billing_plan=normalized_plan,
        program=program or plan_to_program(normalized_plan),
        signup_type=signup_type,
        account_status=account_status,
        access_level=access_level,
        cid_enabled=cid_enabled,
        onboarding_completed=onboarding_completed,
        company=company.strip() if company else None,
        country=country.strip() if country else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def apply_internal_plan_change(
    db: AsyncSession,
    user: DBUser,
    target_plan: str,
) -> tuple[str, str]:
    requested_plan = (target_plan or "").strip().lower()
    if not plan_limits_service.get_plan(requested_plan):
        raise ValueError("Plan not found")
    normalized_plan = requested_plan

    previous_plan = await resolve_effective_plan(db, user)
    user.billing_plan = normalized_plan
    user.program = plan_to_program(normalized_plan)

    organization = await get_organization(db, user.organization_id)
    if organization is not None:
        organization.billing_plan = normalized_plan

    await db.commit()
    await db.refresh(user)
    return previous_plan, normalized_plan
