from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import AuditLog, User
from app.schemas import AuditLogOut

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/project/{project_id}", response_model=list[AuditLogOut])
async def get_project_audit(project_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(AuditLog).where(AuditLog.project_id == project_id).order_by(AuditLog.created_at.desc())
    )
    return result.scalars().all()


@router.get("/job/{job_id}", response_model=list[AuditLogOut])
async def get_job_audit(job_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(AuditLog).where(AuditLog.dubbing_job_id == job_id).order_by(AuditLog.created_at.desc())
    )
    return result.scalars().all()
