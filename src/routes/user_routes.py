from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import (
    TenantContext,
    get_tenant_context,
    require_write_permission,
)
from models.core import User as DBUser
from routes.auth_routes import hash_password
from schemas.auth_schema import UserResponse
from schemas.user_schema import UserCreate
from services.account_service import (
    apply_internal_plan_change,
    build_user_response_from_db,
    create_user_account,
    get_user_by_email,
    get_user_by_id,
)

router = APIRouter(prefix="/api/users", tags=["users"])


def _is_admin_tenant(tenant: TenantContext) -> bool:
    return bool(
        getattr(tenant, "is_global_admin", False)
        or getattr(tenant, "role", None) == "admin"
    )


def _can_access_user(tenant: TenantContext, user_id: str) -> bool:
    return str(tenant.user_id) == str(user_id) or _is_admin_tenant(tenant)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await create_user_account(
        db,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        plan=user_data.plan,
        full_name=user_data.username,
        organization_name=f"{user_data.username} Studio",
    )

    return await build_user_response_from_db(db, user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    if not _can_access_user(tenant, user_id):
        raise HTTPException(status_code=403, detail="Not allowed to access this user")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await build_user_response_from_db(db, user)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    if not _is_admin_tenant(tenant):
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(
        select(DBUser).order_by(DBUser.created_at.desc(), DBUser.id.desc())
    )
    users = result.scalars().all()
    return [await build_user_response_from_db(db, user) for user in users]


@router.patch("/{user_id}/plan")
async def update_user_plan(
    user_id: str,
    new_plan: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    if not _can_access_user(tenant, user_id):
        raise HTTPException(
            status_code=403, detail="Not allowed to change this user plan"
        )

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        previous_plan, current_plan = await apply_internal_plan_change(
            db, user, new_plan
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "message": f"Plan activado internamente: {previous_plan} -> {current_plan}",
        "previous_plan": previous_plan,
        "current_plan": current_plan,
        "activation_mode": "internal_manual",
        "effective_immediately": True,
    }
