from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Protocol

from models.ai_job import AIJob
from services.ai_job_transition_service import (
    AIJobTransitionError,
    AIJobTransitionPlan,
    build_ai_job_transition_plan,
)


__all__ = [
    "AIJobOrchestrationError",
    "AIJobNotFoundError",
    "AIJobIdempotencyConflictError",
    "AIJobAccountingError",
    "AIJobInvalidOperationError",
    "AIJobCreateRequest",
    "AIJobEstimateRequest",
    "AIJobReserveRequest",
    "AIJobQueueRequest",
    "AIJobCompletionRequest",
    "AIJobFailureRequest",
    "AIJobCancelRequest",
    "AIJobRetryRequest",
    "AIJobOrchestrationResult",
    "AIJobRepositoryProtocol",
    "AIJobCreditGatewayProtocol",
    "AIJobOrchestrationService",
]


class AIJobOrchestrationError(Exception):
    """Base error for AI job orchestration helpers."""


class AIJobNotFoundError(AIJobOrchestrationError):
    """Raised when the requested job does not exist in the repository."""


class AIJobIdempotencyConflictError(AIJobOrchestrationError):
    """Raised when an idempotent create request conflicts with existing payload."""


class AIJobAccountingError(AIJobOrchestrationError):
    """Raised when accounting preconditions or results are inconsistent."""


class AIJobInvalidOperationError(AIJobOrchestrationError):
    """Raised when the requested orchestration operation is invalid."""


@dataclass(frozen=True)
class AIJobCreateRequest:
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
    input_asset_ids: list[str] | None = None
    output_asset_ids: list[str] | None = None


@dataclass(frozen=True)
class AIJobEstimateRequest:
    organization_id: str
    job_id: str
    estimated_credits: int | None = None


@dataclass(frozen=True)
class AIJobReserveRequest:
    organization_id: str
    job_id: str
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIJobQueueRequest:
    organization_id: str
    job_id: str


@dataclass(frozen=True)
class AIJobCompletionRequest:
    organization_id: str
    job_id: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIJobFailureRequest:
    organization_id: str
    job_id: str
    error_code: str | None = None
    failure_reason: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIJobCancelRequest:
    organization_id: str
    job_id: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIJobRetryRequest:
    organization_id: str
    job_id: str
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class AIJobOrchestrationResult:
    job: AIJob
    transition_plan: AIJobTransitionPlan | None = None
    message: str = ""
    accounting_result: Any | None = None
    availability_result: Any | None = None


class AIJobRepositoryProtocol(Protocol):
    def create(self, job: AIJob) -> AIJob: ...

    def get(self, job_id: str) -> AIJob | None: ...

    def save(self, job: AIJob) -> AIJob: ...

    def find_by_idempotency_key(
        self,
        organization_id: str,
        idempotency_key: str,
    ) -> AIJob | None: ...


class AIJobCreditGatewayProtocol(Protocol):
    def estimate_credit_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> Any: ...

    def check_credit_availability(
        self,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> Any: ...

    def reserve_credits_for_operation(
        self,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...

    def consume_reserved_credits_for_operation(
        self,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...

    def release_reserved_credits_for_operation(
        self,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any: ...


class AIJobOrchestrationService:
    """Pure in-memory orchestration helper for future AI job lifecycle flows."""

    def __init__(
        self,
        *,
        repository: AIJobRepositoryProtocol,
        credit_gateway: AIJobCreditGatewayProtocol,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.credit_gateway = credit_gateway
        self.now_fn = now_fn or datetime.utcnow

    def create_ai_job(self, request: AIJobCreateRequest) -> AIJobOrchestrationResult:
        if request.idempotency_key:
            existing = self.repository.find_by_idempotency_key(
                request.organization_id,
                request.idempotency_key,
            )
            if existing is not None:
                if self._is_equivalent_create_request(existing, request):
                    return AIJobOrchestrationResult(
                        job=existing,
                        message="existing idempotent AI job returned",
                    )
                raise AIJobIdempotencyConflictError(
                    "Conflicting AI job create request for idempotency_key {0}".format(
                        request.idempotency_key
                    )
                )

        now = self.now_fn()
        job = AIJob(
            id=uuid.uuid4().hex,
            organization_id=request.organization_id,
            project_id=request.project_id,
            user_id=request.user_id,
            operation_type=request.operation_type.strip(),
            status="created",
            estimated_credits=0,
            reserved_credits=0,
            consumed_credits=0,
            released_credits=0,
            idempotency_key=request.idempotency_key,
            provider_type=request.provider_type,
            provider_name=request.provider_name,
            workflow_id=request.workflow_id,
            workflow_version=request.workflow_version,
            workflow_hash=request.workflow_hash,
            model_name=request.model_name,
            input_asset_ids=list(request.input_asset_ids or []),
            output_asset_ids=list(request.output_asset_ids or []),
            attempt_number=1,
            created_at=now,
        )
        self._merge_job_metadata(job, request.metadata)
        self.repository.create(job)
        return AIJobOrchestrationResult(job=job, message="AI job created")

    def estimate_ai_job(self, request: AIJobEstimateRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        estimate = self.credit_gateway.estimate_credit_cost(
            operation_type=job.operation_type,
            estimated_credits=request.estimated_credits,
        )
        job.operation_type = estimate.operation_type
        job.estimated_credits = int(estimate.estimated_credits)
        plan = self._apply_transition(job, "estimated")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job estimated",
        )

    def check_ai_job_credits(self, request: AIJobEstimateRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        availability = self.credit_gateway.check_credit_availability(
            organization_id=job.organization_id,
            operation_type=job.operation_type,
            estimated_credits=job.estimated_credits,
        )
        plan = self._apply_transition(job, "credit_checked")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            availability_result=availability,
            message="AI job credit availability checked",
        )

    def reserve_ai_job_credits(self, request: AIJobReserveRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._preview_transition(job, "reserved")
        reservation = self.credit_gateway.reserve_credits_for_operation(
            organization_id=job.organization_id,
            operation_type=job.operation_type,
            job_id=job.id,
            estimated_credits=job.estimated_credits,
            project_id=job.project_id,
            user_id=job.user_id,
            idempotency_key=request.idempotency_key,
            metadata=self._build_canonical_metadata(job, request.metadata),
        )
        if not getattr(reservation, "ledger_entry_id", None):
            raise AIJobAccountingError("Reservation result missing ledger_entry_id")
        plan = self._apply_transition(job, "reserved")
        job.reservation_entry_id = reservation.ledger_entry_id
        job.reserved_credits = int(getattr(reservation, "amount", 0) or 0)
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            accounting_result=reservation,
            message="AI job credits reserved",
        )

    def queue_ai_job(self, request: AIJobQueueRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._require_reservation(job)
        plan = self._apply_transition(job, "queued")
        self.repository.save(job)
        return AIJobOrchestrationResult(job=job, transition_plan=plan, message="AI job queued")

    def mark_ai_job_running(self, request: AIJobQueueRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._preview_transition(job, "running")
        self._require_reservation(job)
        plan = self._apply_transition(job, "running")
        self.repository.save(job)
        return AIJobOrchestrationResult(job=job, transition_plan=plan, message="AI job running")

    def mark_ai_job_succeeded(self, request: AIJobCompletionRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "succeeded")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job marked succeeded",
        )

    def mark_ai_job_failed(self, request: AIJobFailureRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        job.error_code = request.error_code
        job.failure_reason = request.failure_reason
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "failed")
        self.repository.save(job)
        return AIJobOrchestrationResult(job=job, transition_plan=plan, message="AI job failed")

    def request_ai_job_cancel(self, request: AIJobCancelRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "cancel_requested")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job cancellation requested",
        )

    def mark_ai_job_cancelled(self, request: AIJobCancelRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "cancelled")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job cancelled",
        )

    def prepare_ai_job_credit_consumption(
        self,
        request: AIJobCompletionRequest,
    ) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        if job.consume_entry_id:
            raise AIJobAccountingError("AI job credits were already consumed")
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "consume_pending")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job prepared for credit consumption",
        )

    def consume_ai_job_credits(self, request: AIJobReserveRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        if job.consume_entry_id:
            raise AIJobAccountingError("AI job credits were already consumed")
        self._preview_transition(job, "consumed")
        consumption = self.credit_gateway.consume_reserved_credits_for_operation(
            organization_id=job.organization_id,
            operation_type=job.operation_type,
            job_id=job.id,
            estimated_credits=job.estimated_credits,
            project_id=job.project_id,
            user_id=job.user_id,
            idempotency_key=request.idempotency_key,
            metadata=self._build_canonical_metadata(job, request.metadata),
        )
        if not getattr(consumption, "ledger_entry_id", None):
            raise AIJobAccountingError("Consumption result missing ledger_entry_id")
        plan = self._apply_transition(job, "consumed")
        job.consume_entry_id = consumption.ledger_entry_id
        job.consumed_credits = int(getattr(consumption, "amount", 0) or 0)
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            accounting_result=consumption,
            message="AI job credits consumed",
        )

    def prepare_ai_job_credit_release(
        self,
        request: AIJobCancelRequest,
    ) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        if job.release_entry_id:
            raise AIJobAccountingError("AI job credits were already released")
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "release_pending")
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            message="AI job prepared for credit release",
        )

    def release_ai_job_credits(self, request: AIJobReserveRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        if job.release_entry_id:
            raise AIJobAccountingError("AI job credits were already released")
        self._preview_transition(job, "released")
        release = self.credit_gateway.release_reserved_credits_for_operation(
            organization_id=job.organization_id,
            operation_type=job.operation_type,
            job_id=job.id,
            estimated_credits=job.estimated_credits,
            idempotency_key=request.idempotency_key,
            metadata=self._build_canonical_metadata(job, request.metadata),
        )
        if not getattr(release, "ledger_entry_id", None):
            raise AIJobAccountingError("Release result missing ledger_entry_id")
        plan = self._apply_transition(job, "released")
        job.release_entry_id = release.ledger_entry_id
        job.released_credits = int(getattr(release, "amount", 0) or 0)
        self.repository.save(job)
        return AIJobOrchestrationResult(
            job=job,
            transition_plan=plan,
            accounting_result=release,
            message="AI job credits released",
        )

    def expire_ai_job(self, request: AIJobCancelRequest) -> AIJobOrchestrationResult:
        job = self._get_job(request.organization_id, request.job_id)
        self._merge_job_metadata(job, request.metadata)
        plan = self._apply_transition(job, "expired")
        self.repository.save(job)
        return AIJobOrchestrationResult(job=job, transition_plan=plan, message="AI job expired")

    def retry_ai_job(self, request: AIJobRetryRequest) -> AIJobOrchestrationResult:
        raise AIJobInvalidOperationError("retry_ai_job is not implemented in this microphase")

    def _get_job(self, organization_id: str, job_id: str) -> AIJob:
        job = self.repository.get(job_id)
        if job is None or job.organization_id != organization_id:
            raise AIJobNotFoundError(
                "AI job {0} not found for organization {1}".format(job_id, organization_id)
            )
        return job

    def _apply_transition(self, job: AIJob, to_status: str) -> AIJobTransitionPlan:
        plan = self._preview_transition(job, to_status)
        job.status = plan.to_status
        if plan.timestamp_field:
            setattr(job, plan.timestamp_field, self.now_fn())
        self._merge_job_metadata(job, None)
        return plan

    def _preview_transition(self, job: AIJob, to_status: str) -> AIJobTransitionPlan:
        try:
            return build_ai_job_transition_plan(job.status, to_status)
        except AIJobTransitionError as exc:
            raise AIJobInvalidOperationError(str(exc)) from exc

    def _require_reservation(self, job: AIJob) -> None:
        if not job.reservation_entry_id or int(job.reserved_credits or 0) <= 0:
            raise AIJobAccountingError("AI job requires a valid reservation before execution")

    def _merge_job_metadata(self, job: AIJob, metadata: dict[str, Any] | None) -> None:
        payload: dict[str, Any] = {}
        if getattr(job, "job_metadata", None):
            payload.update(job.job_metadata or {})
        if metadata:
            payload.update(metadata)
        payload["operation_type"] = job.operation_type
        payload["estimated_credits"] = int(job.estimated_credits or 0)
        payload["job_status"] = job.status
        job.job_metadata = payload

    def _build_canonical_metadata(
        self,
        job: AIJob,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        self._merge_job_metadata(job, metadata)
        return dict(job.job_metadata or {})

    def _is_equivalent_create_request(self, job: AIJob, request: AIJobCreateRequest) -> bool:
        return (
            job.organization_id == request.organization_id
            and job.operation_type == request.operation_type.strip()
            and job.user_id == request.user_id
            and job.project_id == request.project_id
            and job.provider_type == request.provider_type
            and job.provider_name == request.provider_name
            and job.workflow_id == request.workflow_id
            and job.workflow_version == request.workflow_version
            and job.workflow_hash == request.workflow_hash
            and job.model_name == request.model_name
            and list(job.input_asset_ids or []) == list(request.input_asset_ids or [])
            and list(job.output_asset_ids or []) == list(request.output_asset_ids or [])
            and (job.job_metadata or {}) == self._build_expected_create_metadata(request)
        )

    def _build_expected_create_metadata(
        self,
        request: AIJobCreateRequest,
    ) -> dict[str, Any]:
        payload = dict(request.metadata or {})
        payload["operation_type"] = request.operation_type.strip()
        payload["estimated_credits"] = 0
        payload["job_status"] = "created"
        return payload
