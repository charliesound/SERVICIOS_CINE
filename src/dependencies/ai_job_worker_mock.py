from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.ai_job_orchestration import get_ai_job_orchestration_service
from repositories.ai_job_execution_attempt_repository import AIJobExecutionAttemptRepository
from services.ai_job_async_orchestration_service import AIJobAsyncOrchestrationService
from services.ai_job_worker_mock_execution_service import AIJobWorkerMockExecutionService
from services.ai_job_worker_mock_service import AIJobWorkerMockService


def get_ai_job_worker_mock_service(
    db: AsyncSession = Depends(get_db),
    orchestration_service: AIJobAsyncOrchestrationService = Depends(
        get_ai_job_orchestration_service
    ),
) -> AIJobWorkerMockService:
    return AIJobWorkerMockService(orchestration_service=orchestration_service)


def get_ai_job_worker_mock_execution_service(
    db: AsyncSession = Depends(get_db),
    worker_service: AIJobWorkerMockService = Depends(get_ai_job_worker_mock_service),
) -> AIJobWorkerMockExecutionService:
    del db
    return AIJobWorkerMockExecutionService(
        worker_service=worker_service,
        attempt_repository_factory=AIJobExecutionAttemptRepository,
    )
