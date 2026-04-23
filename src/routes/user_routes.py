from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import User as DBUser
from routes.auth_routes import get_current_user_optional, hash_password
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
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await build_user_response_from_db(db, user)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
):
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
    current_user: UserResponse | None = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if current_user.user_id != user_id and current_user.role != "admin":
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
