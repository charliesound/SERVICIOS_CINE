from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.ai_job_orchestration import get_ai_job_orchestration_service
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.ai_job_api_schema import (
    AIJobConsumeRequest,
    AIJobCreateRequest,
    AIJobCreditCheckRequest,
    AIJobEstimateRequest,
    AIJobHistoryResponse,
    AIJobListResponse,
    AIJobMutationResponse,
    AIJobReadResponse,
    AIJobReleaseRequest,
    AIJobReserveRequest,
)
from schemas.auth_schema import TenantContext
from services.ai_job_async_orchestration_service import (
    AIJobAsyncAccountingError,
    AIJobAsyncConsumeRequest,
    AIJobAsyncCreateRequest,
    AIJobAsyncCreditCheckRequest,
    AIJobAsyncEstimateRequest,
    AIJobAsyncIdempotencyConflictError,
    AIJobAsyncInvalidStateError,
    AIJobAsyncNotFoundError,
    AIJobAsyncOrchestrationError,
    AIJobAsyncOrchestrationService,
    AIJobAsyncReleaseRequest,
    AIJobAsyncReserveRequest,
)


router = APIRouter(prefix="/api/v1/ai-jobs", tags=["ai-jobs"])


def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize(v) for v in value]
    if is_dataclass(value):
        return _serialize(asdict(value))
    if hasattr(value, "model_dump"):
        return _serialize(value.model_dump())
    if hasattr(value, "__dict__"):
        return {
            key: _serialize(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return value


def _job_response(job: Any) -> dict[str, Any]:
    data = _serialize(job)
    if isinstance(data, dict):
        if "job_metadata" in data and "metadata" not in data:
            data["metadata"] = data.pop("job_metadata")
        return data
    return {"value": data}


def _result_response(result: Any) -> AIJobMutationResponse:
    transition = _serialize(getattr(result, "transition_plan", None))
    accounting = _serialize(getattr(result, "accounting_result", None))
    return AIJobMutationResponse(
        job=_job_response(getattr(result, "job", None)),
        message=str(getattr(result, "message", "") or ""),
        transition=transition if isinstance(transition, dict) else None,
        accounting=accounting if isinstance(accounting, dict) else None,
    )


def _is_insufficient_credits(exc: Exception) -> bool:
    return exc.__class__.__name__ == "InsufficientCreditsError"


def _raise_http_from_error(exc: Exception) -> None:
    if isinstance(exc, AIJobAsyncNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, (AIJobAsyncInvalidStateError, AIJobAsyncIdempotencyConflictError)):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if _is_insufficient_credits(exc):
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncAccountingError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, AIJobAsyncOrchestrationError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise exc


def _ensure_internal_caller(tenant: TenantContext) -> None:
    if getattr(tenant, "auth_method", "") != "internal_api_key":
        raise HTTPException(
            status_code=403,
            detail="AI job consume/release endpoints are internal only",
        )


def _ensure_credit_override_allowed(
    tenant: TenantContext,
    value: int | None,
    field_name: str,
) -> None:
    if value is None:
        return
    if getattr(tenant, "auth_method", "") == "internal_api_key":
        return
    if getattr(tenant, "is_admin", False) or getattr(tenant, "is_global_admin", False):
        return
    raise HTTPException(
        status_code=403,
        detail=f"{field_name} override is internal/admin only",
    )


def _raise_not_implemented(endpoint_name: str) -> None:
    raise HTTPException(
        status_code=501,
        detail=f"{endpoint_name} requires future AIJobAsyncOrchestrationService surface",
    )


@router.post("", response_model=AIJobMutationResponse)
async def create_ai_job_endpoint(
    payload: AIJobCreateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    try:
        result = await service.create_ai_job(
            db,
            AIJobAsyncCreateRequest(
                organization_id=tenant.organization_id,
                user_id=tenant.user_id,
                operation_type=payload.operation_type,
                project_id=payload.project_id,
                idempotency_key=payload.idempotency_key,
                metadata=payload.metadata,
                provider_type=payload.provider_type,
                provider_name=payload.provider_name,
                workflow_id=payload.workflow_id,
                workflow_version=payload.workflow_version,
                workflow_hash=payload.workflow_hash,
                model_name=payload.model_name,
                input_asset_ids=payload.input_asset_ids,
                output_asset_ids=payload.output_asset_ids,
            ),
        )
        return _result_response(result)
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.post("/{job_id}/estimate", response_model=AIJobMutationResponse)
async def estimate_ai_job_endpoint(
    job_id: str,
    payload: AIJobEstimateRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    payload = payload or AIJobEstimateRequest()
    _ensure_credit_override_allowed(tenant, payload.estimated_credits, "estimated_credits")
    try:
        result = await service.estimate_ai_job(
            db,
            AIJobAsyncEstimateRequest(
                organization_id=tenant.organization_id,
                job_id=job_id,
                estimated_credits=payload.estimated_credits,
            ),
        )
        return _result_response(result)
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.post("/{job_id}/check-credits", response_model=AIJobMutationResponse)
async def check_ai_job_credits_endpoint(
    job_id: str,
    payload: AIJobCreditCheckRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    payload = payload or AIJobCreditCheckRequest()
    _ensure_credit_override_allowed(tenant, payload.estimated_credits, "estimated_credits")
    try:
        result = await service.check_ai_job_credits(
            db,
            AIJobAsyncCreditCheckRequest(
                organization_id=tenant.organization_id,
                job_id=job_id,
                estimated_credits=payload.estimated_credits,
            ),
        )
        response = _result_response(result)
        accounting = response.accounting or {}
        if accounting.get("sufficient") is False:
            raise HTTPException(status_code=402, detail="Insufficient credits")
        return response
    except HTTPException:
        raise
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.post("/{job_id}/reserve", response_model=AIJobMutationResponse)
async def reserve_ai_job_credits_endpoint(
    job_id: str,
    payload: AIJobReserveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    payload = payload or AIJobReserveRequest()
    _ensure_credit_override_allowed(tenant, payload.estimated_credits, "estimated_credits")
    try:
        result = await service.reserve_ai_job_credits(
            db,
            AIJobAsyncReserveRequest(
                organization_id=tenant.organization_id,
                job_id=job_id,
                estimated_credits=payload.estimated_credits,
                caller_key=payload.caller_key,
            ),
        )
        return _result_response(result)
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.post("/{job_id}/consume", response_model=AIJobMutationResponse)
async def consume_ai_job_credits_endpoint(
    job_id: str,
    payload: AIJobConsumeRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    _ensure_internal_caller(tenant)
    payload = payload or AIJobConsumeRequest()
    try:
        result = await service.consume_ai_job_credits(
            db,
            AIJobAsyncConsumeRequest(
                organization_id=tenant.organization_id,
                job_id=job_id,
                actual_credits=payload.actual_credits,
                caller_key=payload.caller_key,
            ),
        )
        return _result_response(result)
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.post("/{job_id}/release", response_model=AIJobMutationResponse)
async def release_ai_job_credits_endpoint(
    job_id: str,
    payload: AIJobReleaseRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    service: AIJobAsyncOrchestrationService = Depends(get_ai_job_orchestration_service),
) -> AIJobMutationResponse:
    _ensure_internal_caller(tenant)
    payload = payload or AIJobReleaseRequest()
    try:
        result = await service.release_ai_job_credits(
            db,
            AIJobAsyncReleaseRequest(
                organization_id=tenant.organization_id,
                job_id=job_id,
                release_credits=payload.release_credits,
                caller_key=payload.caller_key,
            ),
        )
        return _result_response(result)
    except Exception as exc:
        _raise_http_from_error(exc)
        raise


@router.get("/{job_id}", response_model=AIJobReadResponse)
async def get_ai_job_endpoint(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
) -> AIJobReadResponse:
    del job_id, tenant
    _raise_not_implemented("GET /api/v1/ai-jobs/{job_id}")


@router.get("", response_model=AIJobListResponse)
async def list_ai_jobs_endpoint(
    tenant: TenantContext = Depends(get_tenant_context),
) -> AIJobListResponse:
    del tenant
    _raise_not_implemented("GET /api/v1/ai-jobs")


@router.get("/{job_id}/history", response_model=AIJobHistoryResponse)
async def get_ai_job_history_endpoint(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
) -> AIJobHistoryResponse:
    del job_id, tenant
    _raise_not_implemented("GET /api/v1/ai-jobs/{job_id}/history")
