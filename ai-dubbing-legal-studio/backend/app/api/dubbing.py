from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import DubbingJob, JobStep, Approval, User, Actor, VoiceContract
from app.schemas import DubbingJobCreate, DubbingJobOut, ApprovalCreate
from app.services.audit_service import log_audit
from app.services.contract_validation_service import validate_contract

router = APIRouter(prefix="/api/dubbing-jobs", tags=["dubbing"])


@router.post("/project/{project_id}", response_model=DubbingJobOut)
async def create_dubbing_job(project_id: int, data: DubbingJobCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    job = DubbingJob(
        project_id=project_id,
        media_asset_id=data.media_asset_id,
        actor_id=data.actor_id,
        contract_id=data.contract_id,
        mode=data.mode.value,
        source_language=data.source_language,
        target_language=data.target_language,
        territory=data.territory,
        usage_type=data.usage_type,
        created_by=user.id,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/project/{project_id}", response_model=list[DubbingJobOut])
async def list_dubbing_jobs(project_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.project_id == project_id))
    return result.scalars().all()


@router.get("/{job_id}", response_model=DubbingJobOut)
async def get_dubbing_job(job_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return job


@router.post("/{job_id}/start")
async def start_job(job_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    if job.mode.value == "voz_original_ia_autorizada" and job.contract_id:
        validation = await validate_contract(
            db, contract_id=job.contract_id,
            mode=job.mode.value, language=job.target_language,
            territory=job.territory, usage_type=job.usage_type,
        )
        if validation["blocked"]:
            job.legal_blocked = True
            job.legal_block_reason = validation["reason"]
            job.status = "blocked_legal"
            await db.commit()
            await log_audit(db, user_id=user.id, dubbing_job_id=job.id,
                            action="job.blocked_legal", details=validation)
            return {"status": "blocked_legal", "reason": validation["reason"]}

    job.status = "pending_legal_check"
    await db.commit()
    await log_audit(db, user_id=user.id, dubbing_job_id=job.id, action="job.started")
    return {"status": "started"}


@router.post("/{job_id}/approve")
async def approve_job(job_id: int, data: ApprovalCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    approval = Approval(dubbing_job_id=job_id, approved_by=user.id, decision=data.decision, comments=data.comments)
    db.add(approval)
    job.status = "approved" if data.decision == "approved" else "rejected"
    await db.commit()
    await log_audit(db, user_id=user.id, dubbing_job_id=job_id,
                    action=f"job.{data.decision}", details={"decision": data.decision, "comments": data.comments})
    return {"status": job.status}


@router.post("/{job_id}/reject")
async def reject_job(job_id: int, data: ApprovalCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    approval = Approval(dubbing_job_id=job_id, approved_by=user.id, decision="rejected", comments=data.comments)
    db.add(approval)
    job.status = "rejected"
    await db.commit()
    return {"status": "rejected"}


@router.get("/{job_id}/export")
async def export_job(job_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return {"job_id": job.id, "output_path": job.output_path, "status": job.status.value}
