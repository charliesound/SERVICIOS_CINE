from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.ai_job_worker_mock import get_ai_job_worker_mock_service
from dependencies.tenant_context import get_tenant_context
from schemas.ai_job_worker_mock_api_schema import (
    AIJobWorkerMockExecuteRequest,
    AIJobWorkerMockExecuteResponse,
)
from schemas.auth_schema import TenantContext
from services.ai_job_async_orchestration_service import (
    AIJobAsyncAccountingError,
    AIJobAsyncInvalidStateError,
    AIJobAsyncNotFoundError,
    AIJobAsyncOrchestrationError,
)
from services.ai_job_worker_mock_service import (
    AIJobWorkerMockCommand,
    AIJobWorkerMockError,
    AIJobWorkerMockInvalidModeError,
    AIJobWorkerMockService,
    AIJobWorkerMockSettlementError,
)

logger = logging.getLogger("servicios_cine.routes.internal_ai_job_worker_mock")

router = APIRouter(
    prefix="/api/v1/internal/ai-jobs",
    tags=["ai-jobs-internal"],
    include_in_schema=False,
)


def _ensure_internal_caller(tenant: TenantContext) -> None:
    if getattr(tenant, "auth_method", "") != "internal_api_key":
        raise HTTPException(
            status_code=403,
            detail="Mock worker trigger is internal only",
        )


def _reject_forged_organization_query(request: Request) -> None:
    if "organization_id" in request.query_params:
        raise HTTPException(
            status_code=422,
            detail="organization_id query is not allowed",
        )


def _resolve_requested_by(tenant: TenantContext) -> str:
    user_id = getattr(tenant, "user_id", None)
    if user_id:
        return str(user_id)
    return "internal_trigger"


def _map_worker_error(exc: Exception) -> None:
    if isinstance(exc, AIJobWorkerMockInvalidModeError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, AIJobWorkerMockSettlementError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, AIJobWorkerMockError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncInvalidStateError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncAccountingError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncOrchestrationError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, HTTPException):
        raise exc
    raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post(
    "/{job_id}/mock-worker/execute",
    response_model=AIJobWorkerMockExecuteResponse,
)
async def execute_mock_worker_endpoint(
    job_id: str,
    payload: AIJobWorkerMockExecuteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    worker: AIJobWorkerMockService = Depends(get_ai_job_worker_mock_service),
) -> AIJobWorkerMockExecuteResponse:
    _ensure_internal_caller(tenant)
    _reject_forged_organization_query(request)

    command = AIJobWorkerMockCommand(
        organization_id=tenant.organization_id,
        job_id=job_id,
        requested_by=_resolve_requested_by(tenant),
        execution_attempt_id=payload.execution_attempt_id,
        mode=payload.mode,
        simulated_duration_ms=payload.simulated_duration_ms,
        mock_output_metadata=payload.mock_output_metadata,
        mock_error_code=payload.mock_error_code,
        mock_error_message=payload.mock_error_message,
        actual_credits=payload.actual_credits,
        release_credits=payload.release_credits,
    )

    try:
        result = await worker.execute(db, command)
    except Exception as exc:
        _map_worker_error(exc)
        raise  # unreachable but satisfies type checker

    return AIJobWorkerMockExecuteResponse(
        organization_id=result.organization_id,
        job_id=result.job_id,
        mode=str(result.mode),
        status=result.status,
        consumed_credits=result.consumed_credits,
        released_credits=result.released_credits,
        consume_entry_id=result.consume_entry_id,
        release_entry_id=result.release_entry_id,
        output_metadata=result.output_metadata,
        error_metadata=result.error_metadata,
    )
