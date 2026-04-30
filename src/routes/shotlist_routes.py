"""
Shotlist routes.
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from services.shotlist_service import (
    generate_planned_shots_from_project,
    get_planned_shots,
    approve_planned_shot,
    reject_planned_shot,
    get_shot_coverage_summary,
)


router = APIRouter(prefix="/api/projects/{project_id}/planned-shots", tags=["shotlist"])


class ApproveShotPayload(BaseModel):
    notes: Optional[str] = None


class RejectShotPayload(BaseModel):
    notes: Optional[str] = None


@router.get("")
async def list_planned_shots(
    project_id: str,
    sequence_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """List planned shots."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
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
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Generate planned shots from script."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from models.core import Project, User
    from sqlalchemy import select
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Approve a planned shot."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    shot = await approve_planned_shot(db, shot_id, current_user.user_id)
    
    return {"id": shot.id, "status": shot.status}


@router.post("/{shot_id}/reject")
async def reject_shot(
    project_id: str,
    shot_id: str,
    payload: RejectShotPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Reject a planned shot."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    shot = await reject_planned_shot(
        db, shot_id, current_user.user_id, payload.notes
    )
    
    return {"id": shot.id, "status": shot.status}


@router.get("/coverage")
async def get_shot_coverage(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get shot coverage summary."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    coverage = await get_shot_coverage_summary(db, project_id)
    
    return coverage