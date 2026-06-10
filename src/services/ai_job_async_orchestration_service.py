from __future__ import annotations

import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models.ai_job import AIJob
from services.ai_job_status_service import (
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_CREATED,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_ESTIMATED,
)
from services.ai_job_transition_service import (
    AIJobTransitionError,
    AIJobTransitionPlan,
    build_ai_job_transition_plan,
)

__all__ = [
    "AIJobAsyncOrchestrationError",
    "AIJobAsyncNotFoundError",
    "AIJobAsyncAccountingError",
    "AIJobAsyncInvalidStateError",
    "AIJobAsyncIdempotencyConflictError",
    "AIJobAsyncCreateRequest",
    "AIJobAsyncEstimateRequest",
    "AIJobAsyncCreditCheckRequest",
    "AIJobAsyncReserveRequest",
    "AIJobAsyncConsumeRequest",
    "AIJobAsyncReleaseRequest",
    "AIJobAsyncListRequest",
    "AIJobAsyncHistoryResult",
    "AIJobAsyncOrchestrationResult",
    "AIJobAsyncOrchestrationService",
]


class AIJobAsyncOrchestrationError(Exception):
    """Base error for async AI job orchestration."""


class AIJobAsyncNotFoundError(AIJobAsyncOrchestrationError):
    """Raised when a tenant-scoped AI job lookup returns no row."""


class AIJobAsyncAccountingError(AIJobAsyncOrchestrationError):
    """Raised when accounting results or inputs are unsafe."""


class AIJobAsyncInvalidStateError(AIJobAsyncOrchestrationError):
    """Raised when the requested lifecycle transition is invalid."""


class AIJobAsyncIdempotencyConflictError(AIJobAsyncOrchestrationError):
    """Raised when a create idempotency key replays with a different payload."""


@dataclass(frozen=True)
class AIJobAsyncCreateRequest:
    organization_id: str
    operation_type: str
    user_id: str | None = None
    project_id: str | None = None
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None
    provider_type: str | None = None
    provider_name: str | None = None
    workflow_id: str | None = None
    workflow_version: str | None = None
    workflow_hash: str | None = None
    model_name: str | None = None
    input_asset_ids: Iterable[str] | None = None
    output_asset_ids: Iterable[str] | None = None


@dataclass(frozen=True)
class AIJobAsyncEstimateRequest:
    organization_id: str
    job_id: str
    estimated_credits: int | None = None


@dataclass(frozen=True)
class AIJobAsyncCreditCheckRequest:
    organization_id: str
    job_id: str
    estimated_credits: int | None = None


@dataclass(frozen=True)
class AIJobAsyncReserveRequest:
    organization_id: str
    job_id: str
    estimated_credits: int | None = None
    caller_key: str | None = None


@dataclass(frozen=True)
class AIJobAsyncConsumeRequest:
    organization_id: str
    job_id: str
    actual_credits: int | None = None
    caller_key: str | None = None


@dataclass(frozen=True)
class AIJobAsyncReleaseRequest:
    organization_id: str
    job_id: str
    release_credits: int | None = None
    caller_key: str | None = None


@dataclass(frozen=True)
class AIJobAsyncListRequest:
    organization_id: str
    status: str | None = None
    project_id: str | None = None
    operation_type: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    limit: int = 50
    cursor: str | None = None


@dataclass(frozen=True)
class AIJobAsyncHistoryResult:
    job_id: str
    events: list[dict[str, Any]]


@dataclass(frozen=True)
class AIJobAsyncOrchestrationResult:
    job: Any
    transition_plan: AIJobTransitionPlan | None = None
    accounting_result: Any = None
    message: str = ""


class AIJobAsyncOrchestrationService:
    """Async coordinator for AI job persistence and accounting boundaries."""

    def __init__(
        self,
        *,
        repository: Any,
        accounting_gateway: Any,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.accounting_gateway = accounting_gateway
        self._now = now_fn or datetime.utcnow

    async def get_ai_job(
        self,
        session: AsyncSession,
        organization_id: str,
        job_id: str,
    ) -> Any:
        _ = session
        normalized_organization_id = self._require_text(organization_id, "organization_id")
        normalized_job_id = self._require_text(job_id, "job_id")
        job = await self.repository.get(normalized_organization_id, normalized_job_id)
        if job is None:
            raise AIJobAsyncNotFoundError(
                "AI job not found for organization {0}: {1}".format(
                    normalized_organization_id,
                    normalized_job_id,
                )
            )
        return job

    async def list_ai_jobs(
        self,
        session: AsyncSession,
        request: AIJobAsyncListRequest,
    ) -> tuple[list[Any], str | None]:
        _ = session
        organization_id = self._require_text(request.organization_id, "organization_id")
        return await self.repository.list_for_organization(
            organization_id,
            status=self._normalize_optional_text(request.status),
            project_id=self._normalize_optional_text(request.project_id),
            operation_type=self._normalize_optional_text(request.operation_type),
            created_after=request.created_after,
            created_before=request.created_before,
            limit=request.limit,
            cursor=self._normalize_optional_text(request.cursor),
        )

    async def get_ai_job_history(
        self,
        session: AsyncSession,
        organization_id: str,
        job_id: str,
    ) -> AIJobAsyncHistoryResult:
        job = await self.get_ai_job(session, organization_id, job_id)
        return AIJobAsyncHistoryResult(
            job_id=str(getattr(job, "id", job_id)),
            events=self._derive_history_events(job),
        )

    async def create_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncCreateRequest,
    ) -> AIJobAsyncOrchestrationResult:
        _ = session
        organization_id = self._require_text(request.organization_id, "organization_id")
        operation_type = self._require_text(request.operation_type, "operation_type")
        project_id = self._normalize_optional_text(request.project_id)
        user_id = self._normalize_optional_text(request.user_id)
        provider_type = self._normalize_optional_text(request.provider_type)
        provider_name = self._normalize_optional_text(request.provider_name)
        workflow_id = self._normalize_optional_text(request.workflow_id)
        workflow_version = self._normalize_optional_text(request.workflow_version)
        workflow_hash = self._normalize_optional_text(request.workflow_hash)
        model_name = self._normalize_optional_text(request.model_name)
        idempotency_key = self._normalize_optional_text(request.idempotency_key)
        input_asset_ids = self._normalize_asset_ids(request.input_asset_ids)
        output_asset_ids = self._normalize_asset_ids(request.output_asset_ids)
        request_metadata = self._normalize_metadata(request.metadata)

        create_payload = self._build_create_payload(
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            operation_type=operation_type,
            idempotency_key=idempotency_key,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            job_metadata=request_metadata,
        )

        if idempotency_key is not None:
            existing_job = await self.repository.find_by_idempotency_key(
                organization_id,
                idempotency_key,
            )
            if existing_job is not None:
                existing_payload = self._build_existing_create_payload(existing_job)
                if existing_payload == self._build_create_payload_from_request(create_payload):
                    return AIJobAsyncOrchestrationResult(
                        job=existing_job,
                        message="AI job already exists",
                    )
                raise AIJobAsyncIdempotencyConflictError(
                    "Conflicting AI job create request"
                )

        job = AIJob(
            id=uuid.uuid4().hex,
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            operation_type=operation_type,
            status=AI_JOB_STATUS_CREATED,
            estimated_credits=0,
            reserved_credits=0,
            consumed_credits=0,
            released_credits=0,
            idempotency_key=idempotency_key,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            attempt_number=1,
            created_at=self._now(),
            job_metadata=self._build_job_metadata(
                existing_metadata=request_metadata,
                operation_type=operation_type,
                estimated_credits=0,
                job_status=AI_JOB_STATUS_CREATED,
            ),
        )
        saved_job = await self.repository.create(job)
        return AIJobAsyncOrchestrationResult(job=saved_job, message="AI job created")

    async def estimate_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncEstimateRequest,
    ) -> AIJobAsyncOrchestrationResult:
        job = await self._load_job_for_mutation(request.organization_id, request.job_id)
        plan = self._build_transition_plan(job.status, AI_JOB_STATUS_ESTIMATED)
        estimate_result = await self.accounting_gateway.estimate_credit_cost(
            session,
            operation_type=job.operation_type,
            estimated_credits=request.estimated_credits,
        )
        estimated_credits = self._coerce_result_credits(
            getattr(estimate_result, "estimated_credits", None),
            field_name="estimated_credits",
        )
        job.operation_type = self._normalize_optional_text(
            getattr(estimate_result, "operation_type", job.operation_type)
        ) or job.operation_type
        job.estimated_credits = estimated_credits
        self._apply_transition(job, plan)
        job.job_metadata = self._build_job_metadata(
            existing_metadata=getattr(job, "job_metadata", None),
            operation_type=job.operation_type,
            estimated_credits=job.estimated_credits,
            job_status=job.status,
        )
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            accounting_result=estimate_result,
            message="AI job estimated",
        )

    async def check_ai_job_credits(
        self,
        session: AsyncSession,
        request: AIJobAsyncCreditCheckRequest,
    ) -> AIJobAsyncOrchestrationResult:
        job = await self._load_job_for_mutation(request.organization_id, request.job_id)
        plan = self._build_transition_plan(job.status, AI_JOB_STATUS_CREDIT_CHECKED)
        estimated_credits = self._resolve_positive_credits(
            request.estimated_credits,
            getattr(job, "estimated_credits", None),
            field_name="estimated_credits",
        )
        availability_result = await self.accounting_gateway.check_credit_availability(
            session,
            organization_id=job.organization_id,
            operation_type=job.operation_type,
            estimated_credits=estimated_credits,
        )
        job.estimated_credits = estimated_credits
        self._apply_transition(job, plan)
        job.job_metadata = self._build_job_metadata(
            existing_metadata=getattr(job, "job_metadata", None),
            operation_type=job.operation_type,
            estimated_credits=job.estimated_credits,
            job_status=job.status,
        )
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            accounting_result=availability_result,
            message="AI job credit checked",
        )

    async def estimate_credit_cost(
        self,
        session: AsyncSession,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> Any:
        return await self.accounting_gateway.estimate_credit_cost(
            session,
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    async def check_credit_availability(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> Any:
        return await self.accounting_gateway.check_credit_availability(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    async def reserve_ai_job_credits(
        self,
        session: AsyncSession,
        request: AIJobAsyncReserveRequest,
    ) -> AIJobAsyncOrchestrationResult:
        job = await self._load_job_for_mutation(request.organization_id, request.job_id)
        plan = self._build_transition_plan(job.status, AI_JOB_STATUS_RESERVED)
        credits = self._resolve_positive_credits(
            request.estimated_credits,
            getattr(job, "estimated_credits", None),
            field_name="estimated_credits",
        )
        accounting_result = await self.accounting_gateway.reserve_credits_for_job(
            session,
            organization_id=request.organization_id,
            job_id=request.job_id,
            estimated_credits=credits,
            project_id=getattr(job, "project_id", None),
            user_id=getattr(job, "user_id", None),
            operation_type=getattr(job, "operation_type", None),
            provider_type=getattr(job, "provider_type", None),
            provider_name=getattr(job, "provider_name", None),
            workflow_id=getattr(job, "workflow_id", None),
            workflow_version=getattr(job, "workflow_version", None),
            workflow_hash=getattr(job, "workflow_hash", None),
            model_name=getattr(job, "model_name", None),
            input_asset_ids=getattr(job, "input_asset_ids", None),
            caller_key=request.caller_key,
        )
        ledger_entry_id = self._require_ledger_entry_id(
            accounting_result,
            "Reservation result missing ledger_entry_id",
        )
        job.reservation_entry_id = ledger_entry_id
        job.reserved_credits = credits
        self._apply_transition(job, plan)
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            accounting_result=accounting_result,
            message="reserved",
        )

    async def consume_ai_job_credits(
        self,
        session: AsyncSession,
        request: AIJobAsyncConsumeRequest,
    ) -> AIJobAsyncOrchestrationResult:
        job = await self._load_job_for_mutation(request.organization_id, request.job_id)
        reservation_entry_id = self._require_reservation_entry_id(job)
        plan = self._build_transition_plan(job.status, AI_JOB_STATUS_CONSUMED)
        credits = self._resolve_positive_credits(
            request.actual_credits,
            getattr(job, "estimated_credits", None),
            getattr(job, "reserved_credits", None),
            field_name="actual_credits",
        )
        accounting_result = await self.accounting_gateway.consume_reserved_credits_for_job(
            session,
            organization_id=request.organization_id,
            job_id=request.job_id,
            reservation_entry_id=reservation_entry_id,
            actual_credits=credits,
            project_id=getattr(job, "project_id", None),
            user_id=getattr(job, "user_id", None),
            operation_type=getattr(job, "operation_type", None),
            provider_type=getattr(job, "provider_type", None),
            provider_name=getattr(job, "provider_name", None),
            workflow_id=getattr(job, "workflow_id", None),
            workflow_version=getattr(job, "workflow_version", None),
            workflow_hash=getattr(job, "workflow_hash", None),
            model_name=getattr(job, "model_name", None),
            input_asset_ids=getattr(job, "input_asset_ids", None),
            caller_key=request.caller_key,
        )
        ledger_entry_id = self._require_ledger_entry_id(
            accounting_result,
            "Consumption result missing ledger_entry_id",
        )
        job.consume_entry_id = ledger_entry_id
        job.consumed_credits = credits
        self._apply_transition(job, plan)
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            accounting_result=accounting_result,
            message="consumed",
        )

    async def release_ai_job_credits(
        self,
        session: AsyncSession,
        request: AIJobAsyncReleaseRequest,
    ) -> AIJobAsyncOrchestrationResult:
        job = await self._load_job_for_mutation(request.organization_id, request.job_id)
        reservation_entry_id = self._require_reservation_entry_id(job)
        plan = self._build_transition_plan(job.status, AI_JOB_STATUS_RELEASED)
        credits = self._resolve_positive_credits(
            request.release_credits,
            getattr(job, "reserved_credits", None),
            field_name="release_credits",
        )
        accounting_result = await self.accounting_gateway.release_reserved_credits_for_job(
            session,
            organization_id=request.organization_id,
            job_id=request.job_id,
            reservation_entry_id=reservation_entry_id,
            release_credits=credits,
            project_id=getattr(job, "project_id", None),
            user_id=getattr(job, "user_id", None),
            operation_type=getattr(job, "operation_type", None),
            provider_type=getattr(job, "provider_type", None),
            provider_name=getattr(job, "provider_name", None),
            workflow_id=getattr(job, "workflow_id", None),
            workflow_version=getattr(job, "workflow_version", None),
            workflow_hash=getattr(job, "workflow_hash", None),
            model_name=getattr(job, "model_name", None),
            input_asset_ids=getattr(job, "input_asset_ids", None),
            caller_key=request.caller_key,
        )
        ledger_entry_id = self._require_ledger_entry_id(
            accounting_result,
            "Release result missing ledger_entry_id",
        )
        job.release_entry_id = ledger_entry_id
        job.released_credits = credits
        self._apply_transition(job, plan)
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            accounting_result=accounting_result,
            message="released",
        )

    async def _load_job_for_mutation(self, organization_id: str, job_id: str) -> Any:
        job = await self.repository.get_for_update(organization_id, job_id)
        if job is None:
            raise AIJobAsyncNotFoundError(
                "AI job not found for organization {0}: {1}".format(
                    organization_id,
                    job_id,
                )
            )
        return job

    def _build_transition_plan(self, from_status: str, to_status: str) -> AIJobTransitionPlan:
        try:
            return build_ai_job_transition_plan(from_status, to_status)
        except AIJobTransitionError as exc:
            raise AIJobAsyncInvalidStateError(str(exc)) from exc

    def _apply_transition(self, job: Any, plan: AIJobTransitionPlan) -> None:
        job.status = plan.to_status
        if plan.timestamp_field:
            setattr(job, plan.timestamp_field, self._now())

    def _derive_history_events(self, job: Any) -> list[dict[str, Any]]:
        event_fields = (
            ("created", "created_at"),
            ("estimated", "estimated_at"),
            ("credit_checked", "credit_checked_at"),
            ("reserved", "reserved_at"),
            ("queued", "queued_at"),
            ("running", "started_at"),
            ("finished", "finished_at"),
            ("cancel_requested", "cancel_requested_at"),
            ("cancelled", "cancelled_at"),
            ("consume_pending", "consume_pending_at"),
            ("consumed", "consumed_at"),
            ("release_pending", "release_pending_at"),
            ("released", "released_at"),
        )
        events: list[dict[str, Any]] = []
        for status, field_name in event_fields:
            timestamp = getattr(job, field_name, None)
            if timestamp is None:
                continue
            events.append(
                {
                    "status": status,
                    "timestamp": timestamp,
                    "actor_type": "system",
                    "message": "AI job {0}".format(status),
                    "job_id": getattr(job, "id", None),
                }
            )
        events.sort(key=lambda item: item["timestamp"])
        return events

    def _require_ledger_entry_id(self, result: Any, message: str) -> str:
        ledger_entry_id = getattr(result, "ledger_entry_id", None)
        if not isinstance(ledger_entry_id, str) or not ledger_entry_id.strip():
            raise AIJobAsyncAccountingError(message)
        return ledger_entry_id.strip()

    def _require_reservation_entry_id(self, job: Any) -> str:
        reservation_entry_id = getattr(job, "reservation_entry_id", None)
        if not isinstance(reservation_entry_id, str) or not reservation_entry_id.strip():
            raise AIJobAsyncAccountingError("AI job missing reservation_entry_id")
        return reservation_entry_id.strip()

    def _resolve_positive_credits(
        self,
        *candidates: int | None,
        field_name: str,
    ) -> int:
        for candidate in candidates:
            if candidate is None:
                continue
            if isinstance(candidate, bool) or not isinstance(candidate, int):
                raise AIJobAsyncAccountingError(
                    "{0} must be a positive integer".format(field_name)
                )
            if candidate > 0:
                return candidate
        raise AIJobAsyncAccountingError(
            "{0} must be a positive integer".format(field_name)
        )

    def _normalize_text(self, value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise AIJobAsyncOrchestrationError(f"{field_name} must be a non-empty string")
        normalized = value.strip()
        if not normalized:
            raise AIJobAsyncOrchestrationError(f"{field_name} must be a non-empty string")
        return normalized

    def _require_text(self, value: str, field_name: str) -> str:
        return self._normalize_text(value, field_name)

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = self._normalize_text(value, "optional text field")
        return normalized or None

    def _normalize_asset_ids(self, asset_ids: Iterable[str] | None) -> list[str]:
        if asset_ids is None:
            return []
        if isinstance(asset_ids, str):
            raise AIJobAsyncOrchestrationError(
                "asset_ids must be a list or tuple of strings"
            )
        normalized: list[str] = []
        for asset_id in asset_ids:
            if not isinstance(asset_id, str):
                raise AIJobAsyncOrchestrationError("asset_ids entries must be strings")
            cleaned = asset_id.strip()
            if cleaned:
                normalized.append(cleaned)
        return normalized

    def _normalize_metadata(self, metadata: dict[str, Any] | None) -> dict[str, Any]:
        if metadata is None:
            return {}
        if not isinstance(metadata, dict):
            raise AIJobAsyncOrchestrationError("metadata must be a mapping")
        return dict(metadata)

    def _build_job_metadata(
        self,
        *,
        existing_metadata: dict[str, Any] | None,
        operation_type: str,
        estimated_credits: int,
        job_status: str,
    ) -> dict[str, Any]:
        payload = self._normalize_metadata(existing_metadata)
        payload["operation_type"] = self._normalize_text(
            operation_type,
            "operation_type",
        )
        payload["estimated_credits"] = estimated_credits
        payload["job_status"] = job_status
        return payload

    def _build_create_payload(
        self,
        *,
        organization_id: str,
        project_id: str | None,
        user_id: str | None,
        operation_type: str,
        idempotency_key: str | None,
        provider_type: str | None,
        provider_name: str | None,
        workflow_id: str | None,
        workflow_version: str | None,
        workflow_hash: str | None,
        model_name: str | None,
        input_asset_ids: Iterable[str] | None,
        output_asset_ids: Iterable[str] | None,
        job_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "organization_id": organization_id,
            "project_id": project_id,
            "user_id": user_id,
            "operation_type": operation_type,
            "status": AI_JOB_STATUS_CREATED,
            "estimated_credits": 0,
            "reserved_credits": 0,
            "consumed_credits": 0,
            "released_credits": 0,
            "idempotency_key": idempotency_key,
            "provider_type": provider_type,
            "provider_name": provider_name,
            "workflow_id": workflow_id,
            "workflow_version": workflow_version,
            "workflow_hash": workflow_hash,
            "model_name": model_name,
            "input_asset_ids": list(input_asset_ids or []),
            "output_asset_ids": list(output_asset_ids or []),
            "attempt_number": 1,
            "job_metadata": self._build_job_metadata(
                existing_metadata=job_metadata,
                operation_type=operation_type,
                estimated_credits=0,
                job_status=AI_JOB_STATUS_CREATED,
            ),
        }

    def _build_create_payload_from_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        return dict(payload)

    def _build_existing_create_payload(self, job: AIJob) -> dict[str, Any]:
        return {
            "organization_id": job.organization_id,
            "project_id": job.project_id,
            "user_id": job.user_id,
            "operation_type": self._normalize_text(job.operation_type, "operation_type"),
            "status": self._normalize_text(job.status, "status"),
            "estimated_credits": int(job.estimated_credits or 0),
            "reserved_credits": int(job.reserved_credits or 0),
            "consumed_credits": int(job.consumed_credits or 0),
            "released_credits": int(job.released_credits or 0),
            "idempotency_key": job.idempotency_key,
            "provider_type": job.provider_type,
            "provider_name": job.provider_name,
            "workflow_id": job.workflow_id,
            "workflow_version": job.workflow_version,
            "workflow_hash": job.workflow_hash,
            "model_name": job.model_name,
            "input_asset_ids": list(job.input_asset_ids or []),
            "output_asset_ids": list(job.output_asset_ids or []),
            "attempt_number": int(job.attempt_number or 0),
            "job_metadata": self._normalize_metadata(getattr(job, "job_metadata", None)),
        }

    def _coerce_result_credits(self, value: Any, *, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise AIJobAsyncAccountingError(
                "{0} must be a positive integer".format(field_name)
            )
        if value <= 0:
            raise AIJobAsyncAccountingError(
                "{0} must be a positive integer".format(field_name)
            )
        return value
