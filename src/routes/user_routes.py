from fastapi import APIRouter, HTTPException
from typing import List

from schemas.user_schema import UserCreate, UserUpdate, UserInDB
from schemas.auth_schema import UserResponse
from services.user_service import user_store

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    existing = user_store.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = user_store.create_user(
        username=user_data.username,
        email=user_data.email,
        password=pwd_context.hash(user_data.password),
        plan=user_data.plan,
    )

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        plan=user.plan,
        role=user.role,
        is_active=user.is_active,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = user_store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        plan=user.plan,
        role=user.role,
        is_active=user.is_active,
    )


@router.get("/", response_model=List[UserResponse])
async def list_users():
    users = user_store.get_all_users()
    return [
        UserResponse(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            plan=u.plan,
            role=u.role,
            is_active=u.is_active,
        )
        for u in users
    ]


@router.patch("/{user_id}/plan")
async def update_user_plan(user_id: str, new_plan: str):
    success = user_store.update_user_plan(user_id, new_plan)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Plan updated", "new_plan": new_plan}
