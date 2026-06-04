"""
Shooting plan routes.
"""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import (
    get_tenant_context,
    require_write_permission,
    validate_project_access,
)
from models.change_governance import ShootingPlan
from models.core import Project
from schemas.auth_schema import TenantContext
from services.shooting_plan_coverage_service import (
    get_pickup_recommendations,
    get_shot_coverage,
)
from services.shotlist_service import (
    ShootingPlanItem,
    approve_shooting_plan,
    create_shooting_plan,
    get_shooting_plan_items,
    get_shooting_plans,
)


router = APIRouter(prefix="/api/projects/{project_id}/shooting-plans", tags=["shooting-plans"], dependencies=[Depends(get_tenant_context)])


class CreatePlanPayload(BaseModel):
    title: str


class AddShotPayload(BaseModel):
    shot_id: str
    shooting_day: int = 1


@router.get("")
async def list_shooting_plans(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
):
    """List shooting plans."""
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
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Create a new shooting plan."""
    plan = await create_shooting_plan(
        db, project_id, project.organization_id, payload.title, _tenant.user_id
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
    project: Project = Depends(validate_project_access),
):
    """Get shooting plan details."""
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
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Approve a shooting plan."""
    result = await db.execute(
        select(ShootingPlan).where(ShootingPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan or plan.project_id != project_id:
        raise HTTPException(status_code=404, detail="Shooting plan not found")
    plan = await approve_shooting_plan(db, plan_id, _tenant.user_id)
    
    return {
        "id": plan.id,
        "status": plan.status,
    }


@router.get("/{plan_id}/coverage")
async def get_plan_coverage(
    project_id: str,
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
):
    """Get coverage report for a shooting plan."""
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
    project: Project = Depends(validate_project_access),
):
    """Get overall coverage across all planned shots."""
    coverage = await get_shot_coverage(db, project_id, None)
    pickups = await get_pickup_recommendations(db, project_id)
    
    return {
        "coverage": coverage,
        "pickup_recommendations": pickups,
    }