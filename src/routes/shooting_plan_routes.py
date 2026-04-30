"""
Shooting plan routes.
"""

import json
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from services.shotlist_service import (
    create_shooting_plan,
    get_shooting_plans,
    get_shooting_plan_items,
    approve_shooting_plan,
)
from services.shooting_plan_coverage_service import (
    get_shot_coverage,
    get_pickup_recommendations,
)


router = APIRouter(prefix="/api/projects/{project_id}/shooting-plans", tags=["shooting-plans"])


class CreatePlanPayload(BaseModel):
    title: str


class AddShotPayload(BaseModel):
    shot_id: str
    shooting_day: int = 1


@router.get("")
async def list_shooting_plans(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """List shooting plans."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    plans = await get_shooting_plans(db, project_id)
    
    return {
        "plans": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "approved_by": p.approved_by,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in plans
        ]
    }


@router.post("")
async def create_shooting_plan_endpoint(
    project_id: str,
    payload: CreatePlanPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Create a new shooting plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from models.core import Project
    from sqlalchemy import select
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    plan = await create_shooting_plan(
        db, project_id, project.organization_id, payload.title, current_user.user_id
    )
    
    return {
        "id": plan.id,
        "status": plan.status,
    }


@router.get("/{plan_id}")
async def get_shooting_plan(
    project_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get shooting plan details."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from services.shotlist_service import ShootingPlanItem
    from sqlalchemy import select
    from models.change_governance import ShootingPlan
    
    result = await db.execute(
        select(ShootingPlan).where(ShootingPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan or plan.project_id != project_id:
        raise HTTPException(status_code=404, detail="Shooting plan not found")
    
    items = await get_shooting_plan_items(db, plan_id)
    
    shots = {}
    for item in items:
        key = f"d{item.shooting_day}"
        if key not in shots:
            shots[key] = {"day": item.shooting_day, "shots": []}
        shots[key]["shots"].append({
            "id": item.id,
            "sequence": item.sequence_number,
            "scene": item.scene_number,
            "shot": item.shot_number,
            "location": item.location,
            "status": item.status,
        })
    
    return {
        "id": plan.id,
        "title": plan.title,
        "status": plan.status,
        "approved_by": plan.approved_by,
        "days": list(shots.values()),
    }


@router.post("/{plan_id}/approve")
async def approve_shooting_plan_endpoint(
    project_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Approve a shooting plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    plan = await approve_shooting_plan(db, plan_id, current_user.user_id)
    
    return {
        "id": plan.id,
        "status": plan.status,
    }


@router.get("/{plan_id}/coverage")
async def get_plan_coverage(
    project_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get coverage report for a shooting plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    coverage = await get_shot_coverage(db, project_id, plan_id)
    pickups = await get_pickup_recommendations(db, project_id)
    
    return {
        "coverage": coverage,
        "pickup_recommendations": pickups,
    }


@router.get("/coverage")
async def get_all_coverage(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get overall coverage across all planned shots."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    coverage = await get_shot_coverage(db, project_id, None)
    pickups = await get_pickup_recommendations(db, project_id)
    
    return {
        "coverage": coverage,
        "pickup_recommendations": pickups,
    }