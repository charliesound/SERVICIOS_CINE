from __future__ import annotations

import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from models.ai_job import AIJob
from services.credit_ledger_service import DuplicateIdempotencyKeyError
from services.ai_job_status_service import (
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_CONSUME_PENDING,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_CREATED,
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_QUEUED,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RELEASE_PENDING,
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_ESTIMATED,
    AI_JOB_STATUS_RUNNING,
    AI_JOB_STATUS_SUCCEEDED,
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
    "AIJobAsyncCancelRequest",
    "AIJobAsyncCancelCreditReleaseRequest",
    "AIJobAsyncCancelCreditReleaseReconciliationRequest",
    "AIJobAsyncConsumeRequest",
    "AIJobAsyncReleaseRequest",
    "AIJobAsyncListRequest",
    "AIJobAsyncExecutionTransitionRequest",
    "AIJobAsyncHistoryResult",
    "AIJobAsyncOrchestrationResult",
    "AIJobAsyncCancelCreditReleaseResult",
    "AIJobAsyncCancelCreditReleaseReconciliationJobResult",
    "AIJobAsyncCancelCreditReleaseReconciliationResult",
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
class AIJobAsyncCancelRequest:
    organization_id: str
    job_id: str
    metadata: dict[str, Any] | None = None
    requested_by: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class AIJobAsyncCancelCreditReleaseRequest:
    organization_id: str
    job_id: str
    requested_by: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class AIJobAsyncCancelCreditReleaseReconciliationRequest:
    organization_id: str
    max_items: int = 50
    dry_run: bool = False
    requested_by: str | None = None
    metadata: dict[str, Any] | None = None


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
class AIJobAsyncExecutionTransitionRequest:
    organization_id: str
    job_id: str
    execution_attempt_id: str | None = None
    metadata: dict[str, Any] | None = None
    output_metadata: dict[str, Any] | None = None
    error_metadata: dict[str, Any] | None = None
    requested_by: str | None = None
    reason: str | None = None


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


@dataclass(frozen=True)
class AIJobAsyncCancelCreditReleaseResult:
    job_id: str
    organization_id: str
    status: str
    release_required: bool
    release_performed: bool
    idempotent: bool
    release_entry_id: str | None
    message: str


@dataclass(frozen=True)
class AIJobAsyncCancelCreditReleaseReconciliationJobResult:
    job_id: str
    organization_id: str
    status_before: str | None
    status_after: str | None
    release_entry_id: str | None
    release_performed: bool
    idempotent: bool
    error_category: str
    message: str


@dataclass(frozen=True)
class AIJobAsyncCancelCreditReleaseReconciliationResult:
    organization_id: str
    scanned_count: int
    processed_count: int
    released_count: int
    skipped_count: int
    failed_count: int
    dry_run: bool
    per_job_results: list[AIJobAsyncCancelCreditReleaseReconciliationJobResult]


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

    async def enqueue_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_QUEUED,
            message="queued",
            require_execution_attempt=True,
        )

    async def start_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_RUNNING,
            message="running",
            require_execution_attempt=True,
        )

    async def succeed_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_SUCCEEDED,
            message="succeeded",
            require_execution_attempt=True,
        )

    async def fail_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_FAILED,
            message="failed",
            require_execution_attempt=True,
        )

    async def cancel_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_CANCELLED,
            message="cancelled",
            require_execution_attempt=True,
        )

    async def request_cancel_ai_job(
        self,
        session: AsyncSession,
        request: AIJobAsyncCancelRequest,
    ) -> AIJobAsyncOrchestrationResult:
        _ = session
        organization_id = self._require_text(request.organization_id, "organization_id")
        job_id = self._require_text(request.job_id, "job_id")
        job = await self._load_job_for_mutation(organization_id, job_id)

        if job.status == AI_JOB_STATUS_CANCEL_REQUESTED:
            return AIJobAsyncOrchestrationResult(
                job=job,
                message="AI job cancellation already requested",
            )
        if job.status == AI_JOB_STATUS_CANCELLED:
            return AIJobAsyncOrchestrationResult(
                job=job,
                message="AI job already cancelled",
            )

        if job.status in {
            AI_JOB_STATUS_CREATED,
            AI_JOB_STATUS_ESTIMATED,
            AI_JOB_STATUS_CREDIT_CHECKED,
        }:
            target_status = AI_JOB_STATUS_CANCELLED
            message = "cancelled"
        elif job.status in {
            AI_JOB_STATUS_RESERVED,
            AI_JOB_STATUS_QUEUED,
            AI_JOB_STATUS_RUNNING,
        }:
            target_status = AI_JOB_STATUS_CANCEL_REQUESTED
            message = "cancel requested"
        else:
            raise AIJobAsyncInvalidStateError(
                "AI job cannot be cancelled from status: {0}".format(job.status)
            )

        plan = self._build_transition_plan(job.status, target_status)
        self._apply_transition(job, plan)
        job.job_metadata = self._build_execution_metadata(
            existing_metadata=getattr(job, "job_metadata", None),
            job_status=job.status,
            execution_attempt_id=None,
            metadata=request.metadata,
            output_metadata=None,
            error_metadata=None,
            requested_by=request.requested_by,
            reason=request.reason,
        )
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            message=message,
        )

    async def mark_consume_pending(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_CONSUME_PENDING,
            message="consume pending",
            require_execution_attempt=False,
        )

    async def mark_release_pending(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
    ) -> AIJobAsyncOrchestrationResult:
        return await self._transition_ai_job_execution(
            session,
            request,
            to_status=AI_JOB_STATUS_RELEASE_PENDING,
            message="release pending",
            require_execution_attempt=False,
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

    async def release_cancelled_ai_job_reserved_credits(
        self,
        session: AsyncSession,
        request: AIJobAsyncCancelCreditReleaseRequest,
    ) -> AIJobAsyncCancelCreditReleaseResult:
        organization_id = self._require_text(request.organization_id, "organization_id")
        job_id = self._require_text(request.job_id, "job_id")
        job = await self._load_job_for_mutation(organization_id, job_id)

        release_entry_id = self._normalize_optional_text(
            getattr(job, "release_entry_id", None)
        )
        if release_entry_id is not None:
            self._finish_cancel_release_without_ledger_if_needed(job)
            saved_job = await self.repository.save(job)
            return self._build_cancel_credit_release_result(
                saved_job,
                release_required=False,
                release_performed=False,
                idempotent=True,
                message="AI job reserved credits already released",
            )

        reservation_entry_id = self._normalize_optional_text(
            getattr(job, "reservation_entry_id", None)
        )
        if reservation_entry_id is None:
            return self._build_cancel_credit_release_result(
                job,
                release_required=False,
                release_performed=False,
                idempotent=True,
                message="AI job has no reserved credits to release",
            )

        if self._normalize_optional_text(getattr(job, "consume_entry_id", None)) is not None:
            raise AIJobAsyncInvalidStateError(
                "AI job reserved credits cannot be released after consumption"
            )
        if int(getattr(job, "consumed_credits", 0) or 0) > 0:
            raise AIJobAsyncInvalidStateError(
                "AI job reserved credits cannot be released after consumption"
            )
        if job.status not in {
            AI_JOB_STATUS_CANCEL_REQUESTED,
            AI_JOB_STATUS_CANCELLED,
            AI_JOB_STATUS_RELEASE_PENDING,
        }:
            raise AIJobAsyncInvalidStateError(
                "AI job reserved credits cannot be released from status: {0}".format(
                    job.status
                )
            )

        credits = self._resolve_positive_credits(
            getattr(job, "reserved_credits", None),
            field_name="release_credits",
        )
        caller_key = "cancel:{0}".format(reservation_entry_id)
        try:
            accounting_result = await self.accounting_gateway.release_reserved_credits_for_job(
                session,
                organization_id=organization_id,
                job_id=job_id,
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
                caller_key=caller_key,
            )
            job.release_entry_id = self._require_ledger_entry_id(
                accounting_result,
                "Release result missing ledger_entry_id",
            )
            release_performed = True
            idempotent = False
            message = "released cancelled AI job reserved credits"
        except DuplicateIdempotencyKeyError as exc:
            existing_entry_id = self._normalize_optional_text(exc.existing_entry_id)
            if existing_entry_id is None:
                raise AIJobAsyncAccountingError(
                    "Duplicate release idempotency key without existing entry id"
                ) from exc
            job.release_entry_id = existing_entry_id
            release_performed = False
            idempotent = True
            message = "AI job reserved credits release already exists"

        job.released_credits = credits
        self._finish_cancel_release_without_ledger_if_needed(job)
        saved_job = await self.repository.save(job)
        return self._build_cancel_credit_release_result(
            saved_job,
            release_required=True,
            release_performed=release_performed,
            idempotent=idempotent,
            message=message,
        )

    async def process_cancelled_ai_job_credit_releases(
        self,
        session: AsyncSession,
        request: AIJobAsyncCancelCreditReleaseReconciliationRequest,
    ) -> AIJobAsyncCancelCreditReleaseReconciliationResult:
        organization_id = self._require_text(request.organization_id, "organization_id")
        max_items = self._resolve_reconciliation_max_items(request.max_items)
        candidates = await self.repository.list_cancelled_credit_release_candidates(
            organization_id,
            limit=max_items,
        )
        per_job_results: list[AIJobAsyncCancelCreditReleaseReconciliationJobResult] = []

        for job in candidates:
            status_before = self._normalize_optional_text(getattr(job, "status", None))
            job_id = str(getattr(job, "id", "") or "")
            if request.dry_run:
                per_job_results.append(
                    AIJobAsyncCancelCreditReleaseReconciliationJobResult(
                        job_id=job_id,
                        organization_id=organization_id,
                        status_before=status_before,
                        status_after=status_before,
                        release_entry_id=self._normalize_optional_text(
                            getattr(job, "release_entry_id", None)
                        ),
                        release_performed=False,
                        idempotent=False,
                        error_category="dry_run_eligible",
                        message="AI job eligible for cancelled credit release",
                    )
                )
                continue

            try:
                release_result = await self.release_cancelled_ai_job_reserved_credits(
                    session,
                    AIJobAsyncCancelCreditReleaseRequest(
                        organization_id=organization_id,
                        job_id=job_id,
                        requested_by=request.requested_by,
                    ),
                )
                per_job_results.append(
                    self._build_reconciliation_job_result(
                        job_id=job_id,
                        organization_id=organization_id,
                        status_before=status_before,
                        release_result=release_result,
                    )
                )
            except AIJobAsyncNotFoundError as exc:
                per_job_results.append(
                    self._build_reconciliation_error_result(
                        job=job,
                        organization_id=organization_id,
                        status_before=status_before,
                        error_category="terminal_error",
                        message=str(exc),
                    )
                )
            except AIJobAsyncInvalidStateError as exc:
                per_job_results.append(
                    self._build_reconciliation_error_result(
                        job=job,
                        organization_id=organization_id,
                        status_before=status_before,
                        error_category=self._map_invalid_state_reconciliation_category(str(exc)),
                        message=str(exc),
                    )
                )
            except AIJobAsyncAccountingError as exc:
                per_job_results.append(
                    self._build_reconciliation_error_result(
                        job=job,
                        organization_id=organization_id,
                        status_before=status_before,
                        error_category="terminal_error",
                        message=str(exc),
                    )
                )
            except RuntimeError as exc:
                per_job_results.append(
                    self._build_reconciliation_error_result(
                        job=job,
                        organization_id=organization_id,
                        status_before=status_before,
                        error_category="retryable_error",
                        message=str(exc),
                    )
                )
            except Exception as exc:
                per_job_results.append(
                    self._build_reconciliation_error_result(
                        job=job,
                        organization_id=organization_id,
                        status_before=status_before,
                        error_category="unexpected_error",
                        message=str(exc),
                    )
                )

        return self._build_reconciliation_result(
            organization_id=organization_id,
            dry_run=bool(request.dry_run),
            scanned_count=len(candidates),
            per_job_results=per_job_results,
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

    async def _transition_ai_job_execution(
        self,
        session: AsyncSession,
        request: AIJobAsyncExecutionTransitionRequest,
        *,
        to_status: str,
        message: str,
        require_execution_attempt: bool,
    ) -> AIJobAsyncOrchestrationResult:
        _ = session
        organization_id = self._require_text(request.organization_id, "organization_id")
        job_id = self._require_text(request.job_id, "job_id")
        execution_attempt_id = None
        if request.execution_attempt_id is not None:
            execution_attempt_id = self._normalize_text(
                request.execution_attempt_id,
                "execution_attempt_id",
            )
        if require_execution_attempt and execution_attempt_id is None:
            raise AIJobAsyncOrchestrationError(
                "execution_attempt_id must be a non-empty string"
            )
        job = await self._load_job_for_mutation(organization_id, job_id)
        plan = self._build_transition_plan(job.status, to_status)
        self._apply_transition(job, plan)
        job.job_metadata = self._build_execution_metadata(
            existing_metadata=getattr(job, "job_metadata", None),
            job_status=job.status,
            execution_attempt_id=execution_attempt_id,
            metadata=request.metadata,
            output_metadata=request.output_metadata,
            error_metadata=request.error_metadata,
            requested_by=request.requested_by,
            reason=request.reason,
        )
        saved_job = await self.repository.save(job)
        return AIJobAsyncOrchestrationResult(
            job=saved_job,
            transition_plan=plan,
            message=message,
        )

    def _build_transition_plan(self, from_status: str, to_status: str) -> AIJobTransitionPlan:
        try:
            return build_ai_job_transition_plan(from_status, to_status)
        except AIJobTransitionError as exc:
            raise AIJobAsyncInvalidStateError(str(exc)) from exc

    def _apply_transition(self, job: Any, plan: AIJobTransitionPlan) -> None:
        job.status = plan.to_status
        if plan.timestamp_field:
            setattr(job, plan.timestamp_field, self._now())

    def _finish_cancel_release_without_ledger_if_needed(self, job: Any) -> None:
        if job.status == AI_JOB_STATUS_CANCEL_REQUESTED:
            self._apply_transition(
                job,
                self._build_transition_plan(job.status, AI_JOB_STATUS_CANCELLED),
            )
        if job.status == AI_JOB_STATUS_CANCELLED:
            self._apply_transition(
                job,
                self._build_transition_plan(job.status, AI_JOB_STATUS_RELEASE_PENDING),
            )
        if job.status == AI_JOB_STATUS_RELEASE_PENDING:
            self._apply_transition(
                job,
                self._build_transition_plan(job.status, AI_JOB_STATUS_RELEASED),
            )

    def _build_cancel_credit_release_result(
        self,
        job: Any,
        *,
        release_required: bool,
        release_performed: bool,
        idempotent: bool,
        message: str,
    ) -> AIJobAsyncCancelCreditReleaseResult:
        return AIJobAsyncCancelCreditReleaseResult(
            job_id=str(getattr(job, "id", "")),
            organization_id=str(getattr(job, "organization_id", "")),
            status=str(getattr(job, "status", "")),
            release_required=release_required,
            release_performed=release_performed,
            idempotent=idempotent,
            release_entry_id=self._normalize_optional_text(
                getattr(job, "release_entry_id", None)
            ),
            message=message,
        )

    def _build_reconciliation_job_result(
        self,
        *,
        job_id: str,
        organization_id: str,
        status_before: str | None,
        release_result: AIJobAsyncCancelCreditReleaseResult,
    ) -> AIJobAsyncCancelCreditReleaseReconciliationJobResult:
        if release_result.release_performed:
            error_category = "released_now"
        elif release_result.idempotent and release_result.release_required:
            error_category = "idempotent_replay"
        elif release_result.release_entry_id is not None:
            error_category = "skipped_already_released"
        else:
            error_category = "skipped_no_reservation"
        return AIJobAsyncCancelCreditReleaseReconciliationJobResult(
            job_id=job_id,
            organization_id=organization_id,
            status_before=status_before,
            status_after=release_result.status,
            release_entry_id=release_result.release_entry_id,
            release_performed=release_result.release_performed,
            idempotent=release_result.idempotent,
            error_category=error_category,
            message=release_result.message,
        )

    def _build_reconciliation_error_result(
        self,
        *,
        job: Any,
        organization_id: str,
        status_before: str | None,
        error_category: str,
        message: str,
    ) -> AIJobAsyncCancelCreditReleaseReconciliationJobResult:
        return AIJobAsyncCancelCreditReleaseReconciliationJobResult(
            job_id=str(getattr(job, "id", "") or ""),
            organization_id=organization_id,
            status_before=status_before,
            status_after=self._normalize_optional_text(getattr(job, "status", None)),
            release_entry_id=self._normalize_optional_text(
                getattr(job, "release_entry_id", None)
            ),
            release_performed=False,
            idempotent=False,
            error_category=error_category,
            message=message,
        )

    def _build_reconciliation_result(
        self,
        *,
        organization_id: str,
        dry_run: bool,
        scanned_count: int,
        per_job_results: list[AIJobAsyncCancelCreditReleaseReconciliationJobResult],
    ) -> AIJobAsyncCancelCreditReleaseReconciliationResult:
        released_count = sum(
            1
            for item in per_job_results
            if item.error_category in {"released_now", "idempotent_replay"}
        )
        failed_count = sum(
            1
            for item in per_job_results
            if item.error_category
            in {"retryable_error", "terminal_error", "unexpected_error"}
        )
        skipped_count = len(per_job_results) - released_count - failed_count
        return AIJobAsyncCancelCreditReleaseReconciliationResult(
            organization_id=organization_id,
            scanned_count=scanned_count,
            processed_count=len(per_job_results),
            released_count=released_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            dry_run=dry_run,
            per_job_results=per_job_results,
        )

    def _map_invalid_state_reconciliation_category(self, message: str) -> str:
        lowered = message.lower()
        if "consumption" in lowered or "consumed" in lowered:
            return "skipped_consumed"
        return "skipped_not_eligible"

    def _resolve_reconciliation_max_items(self, value: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise AIJobAsyncOrchestrationError("max_items must be a positive integer")
        if value <= 0:
            raise AIJobAsyncOrchestrationError("max_items must be a positive integer")
        return min(value, 100)

    def _derive_history_events(self, job: Any) -> list[dict[str, Any]]:
        event_fields = (
            ("created", "created_at"),
            ("estimated", "estimated_at"),
            ("credit_checked", "credit_checked_at"),
            ("reserved", "reserved_at"),
            ("queued", "queued_at"),
            ("running", "started_at"),
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
        finished_status = self._resolve_finished_history_status(job)
        finished_at = getattr(job, "finished_at", None)
        if finished_status is not None and finished_at is not None:
            events.append(
                {
                    "status": finished_status,
                    "timestamp": finished_at,
                    "actor_type": "system",
                    "message": "AI job {0}".format(finished_status),
                    "job_id": getattr(job, "id", None),
                }
            )
        events.sort(key=lambda item: item["timestamp"])
        return events

    def _resolve_finished_history_status(self, job: Any) -> str | None:
        status = getattr(job, "status", None)
        if status in {
            AI_JOB_STATUS_SUCCEEDED,
            AI_JOB_STATUS_PARTIAL_SUCCEEDED,
            AI_JOB_STATUS_FAILED,
        }:
            return status
        metadata = self._normalize_metadata(getattr(job, "job_metadata", None))
        execution = metadata.get("execution")
        if isinstance(execution, dict):
            last_finished_status = execution.get("finished_status")
            if last_finished_status in {
                AI_JOB_STATUS_SUCCEEDED,
                AI_JOB_STATUS_PARTIAL_SUCCEEDED,
                AI_JOB_STATUS_FAILED,
            }:
                return last_finished_status
        return None

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

    def _build_execution_metadata(
        self,
        *,
        existing_metadata: dict[str, Any] | None,
        job_status: str,
        execution_attempt_id: str | None,
        metadata: dict[str, Any] | None,
        output_metadata: dict[str, Any] | None,
        error_metadata: dict[str, Any] | None,
        requested_by: str | None,
        reason: str | None,
    ) -> dict[str, Any]:
        payload = self._normalize_metadata(existing_metadata)
        payload["job_status"] = job_status
        execution = self._normalize_metadata(payload.get("execution"))
        if execution_attempt_id is not None:
            execution["execution_attempt_id"] = execution_attempt_id
        if metadata is not None:
            execution["metadata"] = self._normalize_metadata(metadata)
        normalized_requested_by = self._normalize_optional_text(requested_by)
        if normalized_requested_by is not None:
            execution["requested_by"] = normalized_requested_by
        normalized_reason = self._normalize_optional_text(reason)
        if normalized_reason is not None:
            execution["reason"] = normalized_reason
        if job_status in {
            AI_JOB_STATUS_SUCCEEDED,
            AI_JOB_STATUS_PARTIAL_SUCCEEDED,
            AI_JOB_STATUS_FAILED,
        }:
            execution["finished_status"] = job_status
        if execution:
            payload["execution"] = execution

        if output_metadata is not None or error_metadata is not None:
            mock_worker = self._normalize_metadata(payload.get("mock_worker"))
            if execution_attempt_id is not None:
                mock_worker["execution_attempt_id"] = execution_attempt_id
            if output_metadata is not None:
                mock_worker["output"] = self._normalize_metadata(output_metadata)
            if error_metadata is not None:
                mock_worker["error"] = self._normalize_metadata(error_metadata)
            payload["mock_worker"] = mock_worker
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
