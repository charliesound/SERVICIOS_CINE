from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_orchestration_service import (
    AIJobAccountingError,
    AIJobCancelRequest,
    AIJobCreateRequest,
    AIJobEstimateRequest,
    AIJobFailureRequest,
    AIJobIdempotencyConflictError,
    AIJobInvalidOperationError,
    AIJobOrchestrationService,
    AIJobReserveRequest,
)


@dataclass
class FakeEstimateResult:
    operation_type: str
    estimated_credits: int
    cost_source: str = "fake"


@dataclass
class FakeAvailabilityResult:
    organization_id: str
    operation_type: str
    required_credits: int
    available_credits: int
    sufficient: bool
    balance_id: str | None = "balance-1"
    status: str = "ok"
    message: str = ""


@dataclass
class FakeLedgerResult:
    organization_id: str
    amount: int
    ledger_entry_id: str
    status: str = "ok"
    message: str = ""


class FakeAIJobRepository:
    def __init__(self) -> None:
        self.jobs: dict[str, Any] = {}

    def create(self, job: Any) -> Any:
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Any | None:
        return self.jobs.get(job_id)

    def save(self, job: Any) -> Any:
        self.jobs[job.id] = job
        return job

    def find_by_idempotency_key(self, organization_id: str, idempotency_key: str) -> Any | None:
        for job in self.jobs.values():
            if job.organization_id == organization_id and job.idempotency_key == idempotency_key:
                return job
        return None


class FakeCreditGateway:
    def __init__(self) -> None:
        self.reserve_calls = 0
        self.consume_calls = 0
        self.release_calls = 0

    def estimate_credit_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> FakeEstimateResult:
        return FakeEstimateResult(
            operation_type=operation_type.strip(),
            estimated_credits=estimated_credits or 8,
        )

    def check_credit_availability(
        self,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> FakeAvailabilityResult:
        required = estimated_credits or 8
        return FakeAvailabilityResult(
            organization_id=organization_id,
            operation_type=operation_type,
            required_credits=required,
            available_credits=999,
            sufficient=True,
        )

    def reserve_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.reserve_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="reservation-entry-{0}".format(self.reserve_calls),
        )

    def consume_reserved_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.consume_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="consume-entry-{0}".format(self.consume_calls),
        )

    def release_reserved_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.release_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="release-entry-{0}".format(self.release_calls),
        )


class FakeCreditGatewayMissingReserveEntry(FakeCreditGateway):
    def reserve_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.reserve_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="",
        )


class FakeCreditGatewayMissingConsumeEntry(FakeCreditGateway):
    def consume_reserved_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.consume_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="",
        )


class FakeCreditGatewayMissingReleaseEntry(FakeCreditGateway):
    def release_reserved_credits_for_operation(self, **kwargs: Any) -> FakeLedgerResult:
        self.release_calls += 1
        return FakeLedgerResult(
            organization_id=kwargs["organization_id"],
            amount=int(kwargs["estimated_credits"] or 0),
            ledger_entry_id="",
        )


@pytest.fixture
def now_values() -> list[datetime]:
    base = datetime(2026, 6, 9, 12, 0, 0)
    return [base.replace(minute=minute) for minute in range(0, 30)]


@pytest.fixture
def service(now_values: list[datetime]) -> AIJobOrchestrationService:
    repository = FakeAIJobRepository()
    gateway = FakeCreditGateway()

    def now_fn() -> datetime:
        return now_values.pop(0)

    return AIJobOrchestrationService(
        repository=repository,
        credit_gateway=gateway,
        now_fn=now_fn,
    )


def _build_service_with_gateway(
    gateway: Any,
    *,
    base_minute: int = 0,
) -> AIJobOrchestrationService:
    repository = FakeAIJobRepository()
    now_values = [datetime(2026, 6, 9, 12, base_minute + minute, 0) for minute in range(0, 30)]

    def now_fn() -> datetime:
        return now_values.pop(0)

    return AIJobOrchestrationService(
        repository=repository,
        credit_gateway=gateway,
        now_fn=now_fn,
    )


def _create_minimal_job(service: AIJobOrchestrationService, *, organization_id: str = "org-1"):
    result = service.create_ai_job(
        AIJobCreateRequest(
            organization_id=organization_id,
            operation_type="image_generation",
            user_id="user-1",
            project_id="project-1",
            metadata={"client_ref": "abc"},
        )
    )
    return result.job


class TestAIJobOrchestrationService:
    def test_creates_minimal_job(self, service: AIJobOrchestrationService) -> None:
        result = service.create_ai_job(
            AIJobCreateRequest(
                organization_id="org-1",
                operation_type="image_generation",
                user_id="user-1",
                project_id="project-1",
            )
        )

        assert result.job.organization_id == "org-1"
        assert result.job.operation_type == "image_generation"
        assert result.job.user_id == "user-1"
        assert result.job.project_id == "project-1"
        assert result.job.status == "created"

    def test_create_with_idempotency_key_returns_same_job_on_repeat(self, service: AIJobOrchestrationService) -> None:
        request = AIJobCreateRequest(
            organization_id="org-1",
            operation_type="image_generation",
            user_id="user-1",
            project_id="project-1",
            idempotency_key="idem-1",
            metadata={"client_ref": "abc"},
        )

        first = service.create_ai_job(request)
        second = service.create_ai_job(request)

        assert first.job.id == second.job.id

    def test_estimate_moves_created_to_estimated(self, service: AIJobOrchestrationService) -> None:
        job = _create_minimal_job(service)

        result = service.estimate_ai_job(
            AIJobEstimateRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "estimated"
        assert result.job.estimated_credits == 8
        assert result.job.estimated_at == datetime(2026, 6, 9, 12, 1, 0)

    def test_check_credits_moves_estimated_to_credit_checked(self, service: AIJobOrchestrationService) -> None:
        job = _create_minimal_job(service)
        service.estimate_ai_job(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))

        result = service.check_ai_job_credits(
            AIJobEstimateRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "credit_checked"
        assert result.job.credit_checked_at == datetime(2026, 6, 9, 12, 2, 0)

    def test_reserve_moves_credit_checked_to_reserved(self, service: AIJobOrchestrationService) -> None:
        job = _create_minimal_job(service)
        service.estimate_ai_job(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))
        service.check_ai_job_credits(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))

        result = service.reserve_ai_job_credits(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "reserved"
        assert result.job.reservation_entry_id == "reservation-entry-1"
        assert result.job.reserved_credits == 8
        assert result.job.reserved_at == datetime(2026, 6, 9, 12, 3, 0)

    def test_reserve_from_created_fails_without_gateway_call(self, service: AIJobOrchestrationService) -> None:
        job = _create_minimal_job(service)

        with pytest.raises(AIJobInvalidOperationError, match="Invalid AI job transition plan"):
            service.reserve_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert service.credit_gateway.reserve_calls == 0

    def test_reserve_missing_ledger_entry_keeps_job_in_credit_checked(self) -> None:
        service = _build_service_with_gateway(FakeCreditGatewayMissingReserveEntry())
        job = _create_minimal_job(service)
        service.estimate_ai_job(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))
        service.check_ai_job_credits(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))

        with pytest.raises(AIJobAccountingError, match="Reservation result missing ledger_entry_id"):
            service.reserve_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert job.status == "credit_checked"
        assert job.reservation_entry_id is None

    def test_queue_moves_reserved_to_queued(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_reserved_job(service)

        result = service.queue_ai_job(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        assert result.job.status == "queued"

    def test_running_moves_queued_to_running(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_reserved_job(service)
        service.queue_ai_job(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        result = service.mark_ai_job_running(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "running"

    def test_succeeded_moves_running_to_succeeded(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_running_job(service)

        result = service.mark_ai_job_succeeded(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "succeeded"

    def test_prepare_consumption_moves_succeeded_to_consume_pending(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_succeeded_job(service)

        result = service.prepare_ai_job_credit_consumption(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "consume_pending"
        assert result.job.consume_entry_id is None

    def test_consume_moves_consume_pending_to_consumed(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_succeeded_job(service)
        service.prepare_ai_job_credit_consumption(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        result = service.consume_ai_job_credits(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "consumed"
        assert result.job.consume_entry_id == "consume-entry-1"
        assert result.job.consumed_credits == 8

    def test_consume_from_succeeded_fails_without_gateway_call(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_succeeded_job(service)

        with pytest.raises(AIJobInvalidOperationError, match="Invalid AI job transition plan"):
            service.consume_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert service.credit_gateway.consume_calls == 0

    def test_consume_missing_ledger_entry_keeps_job_in_consume_pending(self) -> None:
        service = _build_service_with_gateway(FakeCreditGatewayMissingConsumeEntry())
        job = _prepare_succeeded_job(service)
        service.prepare_ai_job_credit_consumption(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        with pytest.raises(AIJobAccountingError, match="Consumption result missing ledger_entry_id"):
            service.consume_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert job.status == "consume_pending"
        assert job.consume_entry_id is None

    def test_failed_moves_running_to_failed(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_running_job(service)

        result = service.mark_ai_job_failed(
            AIJobFailureRequest(
                organization_id="org-1",
                job_id=job.id,
                error_code="provider_error",
                failure_reason="boom",
            )
        )

        assert result.job.status == "failed"
        assert result.job.error_code == "provider_error"
        assert result.job.failure_reason == "boom"

    def test_prepare_release_moves_failed_to_release_pending(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_failed_job(service)

        result = service.prepare_ai_job_credit_release(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "release_pending"
        assert result.job.release_entry_id is None

    def test_release_moves_release_pending_to_released(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_failed_job(service)
        service.prepare_ai_job_credit_release(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        result = service.release_ai_job_credits(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        assert result.job.status == "released"
        assert result.job.release_entry_id == "release-entry-1"
        assert result.job.released_credits == 8

    def test_release_from_failed_fails_without_gateway_call(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_failed_job(service)

        with pytest.raises(AIJobInvalidOperationError, match="Invalid AI job transition plan"):
            service.release_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert service.credit_gateway.release_calls == 0

    def test_release_missing_ledger_entry_keeps_job_in_release_pending(self) -> None:
        service = _build_service_with_gateway(FakeCreditGatewayMissingReleaseEntry())
        job = _prepare_failed_job(service)
        service.prepare_ai_job_credit_release(
            AIJobReserveRequest(organization_id="org-1", job_id=job.id)
        )

        with pytest.raises(AIJobAccountingError, match="Release result missing ledger_entry_id"):
            service.release_ai_job_credits(
                AIJobReserveRequest(organization_id="org-1", job_id=job.id)
            )

        assert job.status == "release_pending"
        assert job.release_entry_id is None

    def test_reserved_cancel_release_path(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_reserved_job(service)

        service.request_ai_job_cancel(AIJobCancelRequest(organization_id="org-1", job_id=job.id))
        service.mark_ai_job_cancelled(AIJobCancelRequest(organization_id="org-1", job_id=job.id))
        service.prepare_ai_job_credit_release(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
        result = service.release_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        assert result.job.status == "released"

    def test_queued_cancel_release_path(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_reserved_job(service)
        service.queue_ai_job(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        service.request_ai_job_cancel(AIJobCancelRequest(organization_id="org-1", job_id=job.id))
        service.mark_ai_job_cancelled(AIJobCancelRequest(organization_id="org-1", job_id=job.id))
        service.prepare_ai_job_credit_release(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
        result = service.release_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        assert result.job.status == "released"

    def test_rejects_invalid_transition_created_to_running(self, service: AIJobOrchestrationService) -> None:
        job = _create_minimal_job(service)

        with pytest.raises(AIJobInvalidOperationError, match="Invalid AI job transition plan"):
            service.mark_ai_job_running(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

    def test_rejects_double_consume(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_succeeded_job(service)
        service.prepare_ai_job_credit_consumption(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
        service.consume_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        with pytest.raises(AIJobAccountingError, match="already consumed"):
            service.consume_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

    def test_rejects_double_release(self, service: AIJobOrchestrationService) -> None:
        job = _prepare_failed_job(service)
        service.prepare_ai_job_credit_release(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
        service.release_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

        with pytest.raises(AIJobAccountingError, match="already released"):
            service.release_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))

    def test_same_idempotency_key_different_tenant_does_not_conflict(self, service: AIJobOrchestrationService) -> None:
        first = service.create_ai_job(
            AIJobCreateRequest(
                organization_id="org-1",
                operation_type="image_generation",
                idempotency_key="same-key",
            )
        )
        second = service.create_ai_job(
            AIJobCreateRequest(
                organization_id="org-2",
                operation_type="image_generation",
                idempotency_key="same-key",
            )
        )

        assert first.job.id != second.job.id

    def test_idempotency_conflict_on_different_payload_same_tenant(self, service: AIJobOrchestrationService) -> None:
        service.create_ai_job(
            AIJobCreateRequest(
                organization_id="org-1",
                operation_type="image_generation",
                idempotency_key="idem-2",
                metadata={"client_ref": "a"},
            )
        )

        with pytest.raises(AIJobIdempotencyConflictError, match="Conflicting AI job create request"):
            service.create_ai_job(
                AIJobCreateRequest(
                    organization_id="org-1",
                    operation_type="image_generation",
                    idempotency_key="idem-2",
                    metadata={"client_ref": "b"},
                )
            )

    def test_idempotency_conflict_on_different_workflow_or_input_assets(self, service: AIJobOrchestrationService) -> None:
        service.create_ai_job(
            AIJobCreateRequest(
                organization_id="org-1",
                operation_type="image_generation",
                idempotency_key="idem-3",
                workflow_id="workflow-a",
                input_asset_ids=["asset-a"],
            )
        )

        with pytest.raises(AIJobIdempotencyConflictError, match="Conflicting AI job create request"):
            service.create_ai_job(
                AIJobCreateRequest(
                    organization_id="org-1",
                    operation_type="image_generation",
                    idempotency_key="idem-3",
                    workflow_id="workflow-b",
                    input_asset_ids=["asset-a"],
                )
            )

        with pytest.raises(AIJobIdempotencyConflictError, match="Conflicting AI job create request"):
            service.create_ai_job(
                AIJobCreateRequest(
                    organization_id="org-1",
                    operation_type="image_generation",
                    idempotency_key="idem-3",
                    workflow_id="workflow-a",
                    input_asset_ids=["asset-b"],
                )
            )

    def test_module_does_not_import_db_sessions_workers_routes_or_real_providers(self) -> None:
        module_source = (
            ROOT / "src" / "services" / "ai_job_orchestration_service.py"
        ).read_text(encoding="utf-8")

        forbidden_markers = (
            "AsyncSession",
            "database import",
            "sqlalchemy.ext.asyncio",
            "routes",
            "worker",
            "comfyui",
            "provider adapter",
        )
        for marker in forbidden_markers:
            assert marker not in module_source


def _prepare_reserved_job(service: AIJobOrchestrationService):
    job = _create_minimal_job(service)
    service.estimate_ai_job(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))
    service.check_ai_job_credits(AIJobEstimateRequest(organization_id="org-1", job_id=job.id))
    service.reserve_ai_job_credits(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
    return job


def _prepare_running_job(service: AIJobOrchestrationService):
    job = _prepare_reserved_job(service)
    service.queue_ai_job(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
    service.mark_ai_job_running(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
    return job


def _prepare_succeeded_job(service: AIJobOrchestrationService):
    job = _prepare_running_job(service)
    service.mark_ai_job_succeeded(AIJobReserveRequest(organization_id="org-1", job_id=job.id))
    return job


def _prepare_failed_job(service: AIJobOrchestrationService):
    job = _prepare_running_job(service)
    service.mark_ai_job_failed(
        AIJobFailureRequest(
            organization_id="org-1",
            job_id=job.id,
            error_code="provider_error",
            failure_reason="boom",
        )
    )
    return job
