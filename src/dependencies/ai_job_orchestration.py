from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.ai_job_repository import AIJobRepository
from services.ai_job_accounting_gateway import AIJobAccountingGateway
from services.ai_job_async_orchestration_service import AIJobAsyncOrchestrationService
from services.ai_job_costing_service import AIJobCostingService


def get_ai_job_orchestration_service(
    db: AsyncSession = Depends(get_db),
) -> AIJobAsyncOrchestrationService:
    repository = AIJobRepository(db)
    accounting_gateway = AIJobAccountingGateway(AIJobCostingService())
    return AIJobAsyncOrchestrationService(
        repository=repository,
        accounting_gateway=accounting_gateway,
    )
