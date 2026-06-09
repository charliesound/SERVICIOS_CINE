from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_job_status_service import (
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RESERVED,
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
    "AIJobAsyncReserveRequest",
    "AIJobAsyncConsumeRequest",
    "AIJobAsyncReleaseRequest",
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
