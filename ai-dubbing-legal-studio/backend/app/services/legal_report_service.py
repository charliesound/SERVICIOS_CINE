import json
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import DubbingJob, AuditLog, JobStep, Approval, VoiceContract, Actor


async def generate_legal_report(db: AsyncSession, job_id: int, output_format: str = "json") -> dict:
    job_result = await db.execute(select(DubbingJob).where(DubbingJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise ValueError("Job no encontrado")

    audit_result = await db.execute(
        select(AuditLog).where(AuditLog.dubbing_job_id == job_id).order_by(AuditLog.created_at)
    )
    audit_logs = audit_result.scalars().all()

    steps_result = await db.execute(select(JobStep).where(JobStep.dubbing_job_id == job_id))
    steps = steps_result.scalars().all()

    approvals_result = await db.execute(select(Approval).where(Approval.dubbing_job_id == job_id))
    approvals = approvals_result.scalars().all()

    contract_data = None
    actor_data = None
    if job.contract_id:
        contract_result = await db.execute(select(VoiceContract).where(VoiceContract.id == job.contract_id))
        contract = contract_result.scalar_one_or_none()
        if contract:
            contract_data = {
                "id": contract.id,
                "contract_ref": contract.contract_ref,
                "signed_date": contract.signed_date.isoformat() if contract.signed_date else None,
                "expiry_date": contract.expiry_date.isoformat() if contract.expiry_date else None,
                "is_active": contract.is_active,
                "ia_consent": contract.ia_consent,
                "allowed_languages": json.loads(contract.allowed_languages) if isinstance(contract.allowed_languages, str) else contract.allowed_languages,
                "allowed_territories": json.loads(contract.allowed_territories) if isinstance(contract.allowed_territories, str) else contract.allowed_territories,
                "allowed_usage_types": json.loads(contract.allowed_usage_types) if isinstance(contract.allowed_usage_types, str) else contract.allowed_usage_types,
            }
            if contract.actor_id:
                actor_result = await db.execute(select(Actor).where(Actor.id == contract.actor_id))
                actor = actor_result.scalar_one_or_none()
                if actor:
                    actor_data = {"id": actor.id, "name": actor.name}

    report = {
        "report_generated_at": datetime.now().isoformat(),
        "project_id": job.project_id,
        "dubbing_job": {
            "id": job.id,
            "mode": job.mode.value,
            "source_language": job.source_language,
            "target_language": job.target_language,
            "territory": job.territory,
            "usage_type": job.usage_type,
            "status": job.status.value,
            "legal_blocked": job.legal_blocked,
            "legal_block_reason": job.legal_block_reason,
            "tts_provider": job.tts_provider_used,
            "lipsync_provider": job.lipsync_provider_used,
            "model_version": job.model_version,
        },
        "actor": actor_data,
        "contract": contract_data,
        "steps": [
            {
                "step_name": s.step_name,
                "status": s.status,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "duration_ms": s.duration_ms,
                "error_message": s.error_message,
            }
            for s in steps
        ],
        "approvals": [
            {
                "decision": a.decision,
                "comments": a.comments,
                "approved_by": a.approved_by,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in approvals
        ],
        "audit_logs": [
            {
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ],
    }

    return report
