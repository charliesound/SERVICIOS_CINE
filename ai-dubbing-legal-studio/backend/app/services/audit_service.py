from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog
import json


async def log_audit(
    db: AsyncSession,
    user_id: int = None,
    organization_id: int = None,
    project_id: int = None,
    dubbing_job_id: int = None,
    action: str = None,
    entity_type: str = None,
    entity_id: int = None,
    details: dict = None,
    ip_address: str = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        organization_id=organization_id,
        project_id=project_id,
        dubbing_job_id=dubbing_job_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details, ensure_ascii=False) if details else None,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
