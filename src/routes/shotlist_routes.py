"""
Shotlist routes.
"""

from typing import Optional
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
from models.change_governance import PlannedShot
from models.core import Project
from schemas.auth_schema import TenantContext
from services.shotlist_service import (
    approve_planned_shot,
    generate_planned_shots_from_project,
    get_planned_shots,
    get_shot_coverage_summary,
    reject_planned_shot,
)


router = APIRouter(prefix="/api/projects/{project_id}/planned-shots", tags=["shotlist"], dependencies=[Depends(get_tenant_context)])


class ApproveShotPayload(BaseModel):
    notes: Optional[str] = None


class RejectShotPayload(BaseModel):
    notes: Optional[str] = None


@router.get("")
async def list_planned_shots(
    project_id: str,
    sequence_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
):
    """List planned shots."""
    shots = await get_planned_shots(db, project_id, sequence_number)
    
    return {
        "shots": [
            {
                "id": s.id,
                "sequence_number": s.sequence_number,
                "scene_number": s.scene_number,
                "shot_number": s.shot_number,
                "shot_code": s.shot_code,
                "description": s.description,
                "shot_type": s.shot_type,
                "camera_movement": s.camera_movement,
                "location": s.location,
                "day_night": s.day_night,
                "priority": s.priority,
                "status": s.status,
                "characters_json": s.characters_json,
            }
            for s in shots
        ]
    }


@router.post("/generate")
async def generate_planned_shots(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Generate planned shots from script."""
    shots = await generate_planned_shots_from_project(
        db, project_id, project.organization_id
    )
    
    return {
        "shots": len(shots),
        "message": f"Generated {len(shots)} planned shots",
    }


@router.post("/{shot_id}/approve")
async def approve_shot(
    project_id: str,
    shot_id: str,
    payload: ApproveShotPayload,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Approve a planned shot."""
    result = await db.execute(
        select(PlannedShot).where(PlannedShot.id == shot_id)
    )
    planned_shot = result.scalar_one_or_none()
    if not planned_shot or planned_shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Planned shot not found")
    shot = await approve_planned_shot(db, shot_id, _tenant.user_id)
    
    return {"id": shot.id, "status": shot.status}


@router.post("/{shot_id}/reject")
async def reject_shot(
    project_id: str,
    shot_id: str,
    payload: RejectShotPayload,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Reject a planned shot."""
    result = await db.execute(
        select(PlannedShot).where(PlannedShot.id == shot_id)
    )
    planned_shot = result.scalar_one_or_none()
    if not planned_shot or planned_shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Planned shot not found")
    shot = await reject_planned_shot(
        db, shot_id, _tenant.user_id, payload.notes
    )
    
    return {"id": shot.id, "status": shot.status}


@router.get("/coverage")
async def get_shot_coverage(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
):
    """Get shot coverage summary."""
    coverage = await get_shot_coverage_summary(db, project_id)
    
    return coverage