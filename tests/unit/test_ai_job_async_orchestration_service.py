from __future__ import annotations

import inspect
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://placeholder:placeholder@localhost:5432/placeholder",
)
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_async_orchestration_service import (
    AIJobAsyncAccountingError,
    AIJobAsyncConsumeRequest,
    AIJobAsyncNotFoundError,
    AIJobAsyncOrchestrationService,
    AIJobAsyncReleaseRequest,
    AIJobAsyncReserveRequest,
)


class DummySession:
    pass


@dataclass
class FakeAccountingResult:
    ledger_entry_id: str | None
    amount: int = 8


class FakeJob:
    def __init__(
        self,
        *,
        organization_id: str = "org-1",
        job_id: str = "job-1",
        status: str = "credit_checked",
        estimated_credits: int = 8,
        reserved_credits: int = 8,
        reservation_entry_id: str | None = "reservation-entry-1",
    ) -> None:
        self.id = job_id
        self.organization_id = organization_id
        self.project_id = "project-1"
        self.user_id = "user-1"
        self.operation_type = "image_generation"
        self.status = status
        self.estimated_credits = estimated_credits
        self.reserved_credits = reserved_credits
        self.consumed_credits = 0
        self.released_credits = 0
        self.reservation_entry_id = reservation_entry_id
        self.consume_entry_id = None
        self.release_entry_id = None
        self.provider_type = "provider-type"
        self.provider_name = "provider-name"
        self.workflow_id = "workflow-1"
        self.workflow_version = "v1"
        self.workflow_hash = "hash-1"
        self.model_name = "model-a"
        self.input_asset_ids = ["asset-1"]
        self.reserved_at = None
        self.consumed_at = None
        self.released_at = None


class FakeRepository:
    def __init__(self, job: FakeJob | None) -> None:
        self.job = job
        self.calls: list[tuple[str, tuple]] = []
        self.saved_jobs: list[FakeJob] = []

    async def get_for_update(self, organization_id: str, job_id: str) -> FakeJob | None:
        self.calls.append(("get_for_update", (organization_id, job_id)))
        if self.job is None:
            return None
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def get(self, *args):  # pragma: no cover - fails loudly if used.
        self.calls.append(("get", args))
        raise AssertionError("unexpected non-locking repository read")

    async def save(self, job: FakeJob) -> FakeJob:
        self.calls.append(("save", (job,)))
        self.saved_jobs.append(job)
        return job


class FakeAccountingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.reserve_result = FakeAccountingResult("reservation-entry-1")
        self.consume_result = FakeAccountingResult("consume-entry-1")
        self.release_result = FakeAccountingResult("release-entry-1")
        self.estimate_result = object()
        self.availability_result = object()

    async def estimate_credit_cost(self, session, **kwargs):
        self.calls.append(("estimate_credit_cost", {"session": session, **kwargs}))
        return self.estimate_result

    async def check_credit_availability(self, session, **kwargs):
        self.calls.append(("check_credit_availability", {"session": session, **kwargs}))
        return self.availability_result

    async def reserve_credits_for_job(self, session, **kwargs):
        self.calls.append(("reserve_credits_for_job", {"session": session, **kwargs}))
        return self.reserve_result

    async def consume_reserved_credits_for_job(self, session, **kwargs):
        self.calls.append(("consume_reserved_credits_for_job", {"session": session, **kwargs}))
        return self.consume_result

    async def release_reserved_credits_for_job(self, session, **kwargs):
        self.calls.append(("release_reserved_credits_for_job", {"session": session, **kwargs}))
        return self.release_result


@pytest.fixture
def session() -> DummySession:
    return DummySession()


def _service(
    job: FakeJob | None,
    gateway: FakeAccountingGateway | None = None,
) -> tuple[AIJobAsyncOrchestrationService, FakeRepository, FakeAccountingGateway]:
    repository = FakeRepository(job)
    accounting_gateway = gateway or FakeAccountingGateway()
    service = AIJobAsyncOrchestrationService(
        repository=repository,
        accounting_gateway=accounting_gateway,
        now_fn=lambda: datetime(2026, 6, 9, 12, 0, 0),
    )
    return service, repository, accounting_gateway


@pytest.mark.asyncio
async def test_reserve_uses_get_for_update(session: DummySession) -> None:
    service, repository, _gateway = _service(FakeJob(reservation_entry_id=None))

    await service.reserve_ai_job_credits(
        session,
        AIJobAsyncReserveRequest(organization_id="org-1", job_id="job-1"),
    )

    assert repository.calls[0] == ("get_for_update", ("org-1", "job-1"))
    assert not any(method == "get" for method, _ in repository.calls)


@pytest.mark.asyncio
async def test_reserve_fails_when_job_not_found(session: DummySession) -> None:
    service, _repository, gateway = _service(None)

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.reserve_ai_job_credits(
            session,
            AIJobAsyncReserveRequest(organization_id="org-1", job_id="missing"),
        )

    assert gateway.calls == []


@pytest.mark.asyncio
async def test_reserve_calls_gateway_with_session_and_saves_job(session: DummySession) -> None:
    job = FakeJob(reservation_entry_id=None)
    service, repository, gateway = _service(job)

    result = await service.reserve_ai_job_credits(
        session,
        AIJobAsyncReserveRequest(
            organization_id="org-1",
            job_id="job-1",
            caller_key="attempt-1",
        ),
    )

    method, payload = gateway.calls[-1]
    assert method == "reserve_credits_for_job"
    assert payload["session"] is session
    assert payload["organization_id"] == "org-1"
    assert payload["job_id"] == "job-1"
    assert payload["estimated_credits"] == 8
    assert payload["project_id"] == "project-1"
    assert payload["user_id"] == "user-1"
    assert payload["operation_type"] == "image_generation"
    assert payload["provider_type"] == "provider-type"
    assert payload["provider_name"] == "provider-name"
    assert payload["workflow_id"] == "workflow-1"
    assert payload["workflow_version"] == "v1"
    assert payload["workflow_hash"] == "hash-1"
    assert payload["model_name"] == "model-a"
    assert payload["input_asset_ids"] == ["asset-1"]
    assert payload["caller_key"] == "attempt-1"
    assert result.job.reservation_entry_id == "reservation-entry-1"
    assert result.job.reserved_credits == 8
    assert result.job.status == "reserved"
    assert result.job.reserved_at == datetime(2026, 6, 9, 12, 0, 0)
    assert repository.saved_jobs == [job]


@pytest.mark.asyncio
async def test_reserve_fails_when_gateway_has_no_ledger_entry(session: DummySession) -> None:
    gateway = FakeAccountingGateway()
    gateway.reserve_result = FakeAccountingResult(None)
    service, repository, _gateway = _service(FakeJob(reservation_entry_id=None), gateway)

    with pytest.raises(AIJobAsyncAccountingError, match="Reservation result missing ledger_entry_id"):
        await service.reserve_ai_job_credits(
            session,
            AIJobAsyncReserveRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.saved_jobs == []


@pytest.mark.asyncio
async def test_consume_requires_reservation_entry_id(session: DummySession) -> None:
    service, repository, gateway = _service(
        FakeJob(status="consume_pending", reservation_entry_id=None)
    )

    with pytest.raises(AIJobAsyncAccountingError, match="reservation_entry_id"):
        await service.consume_ai_job_credits(
            session,
            AIJobAsyncConsumeRequest(organization_id="org-1", job_id="job-1"),
        )

    assert gateway.calls == []
    assert repository.saved_jobs == []


@pytest.mark.asyncio
async def test_consume_passes_reservation_and_saves_job(session: DummySession) -> None:
    job = FakeJob(status="consume_pending", reservation_entry_id="reservation-entry-1")
    service, repository, gateway = _service(job)

    result = await service.consume_ai_job_credits(
        session,
        AIJobAsyncConsumeRequest(
            organization_id="org-1",
            job_id="job-1",
            actual_credits=6,
            caller_key="attempt-1",
        ),
    )

    method, payload = gateway.calls[-1]
    assert method == "consume_reserved_credits_for_job"
    assert payload["session"] is session
    assert payload["reservation_entry_id"] == "reservation-entry-1"
    assert payload["actual_credits"] == 6
    assert payload["caller_key"] == "attempt-1"
    assert result.job.consume_entry_id == "consume-entry-1"
    assert result.job.consumed_credits == 6
    assert result.job.status == "consumed"
    assert result.job.consumed_at == datetime(2026, 6, 9, 12, 0, 0)
    assert repository.saved_jobs == [job]


@pytest.mark.asyncio
async def test_release_requires_reservation_entry_id(session: DummySession) -> None:
    service, repository, gateway = _service(
        FakeJob(status="release_pending", reservation_entry_id=None)
    )

    with pytest.raises(AIJobAsyncAccountingError, match="reservation_entry_id"):
        await service.release_ai_job_credits(
            session,
            AIJobAsyncReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert gateway.calls == []
    assert repository.saved_jobs == []


@pytest.mark.asyncio
async def test_release_passes_reservation_and_saves_job(session: DummySession) -> None:
    job = FakeJob(status="release_pending", reservation_entry_id="reservation-entry-1")
    service, repository, gateway = _service(job)

    result = await service.release_ai_job_credits(
        session,
        AIJobAsyncReleaseRequest(
            organization_id="org-1",
            job_id="job-1",
            release_credits=5,
            caller_key="attempt-2",
        ),
    )

    method, payload = gateway.calls[-1]
    assert method == "release_reserved_credits_for_job"
    assert payload["session"] is session
    assert payload["reservation_entry_id"] == "reservation-entry-1"
    assert payload["release_credits"] == 5
    assert payload["caller_key"] == "attempt-2"
    assert result.job.release_entry_id == "release-entry-1"
    assert result.job.released_credits == 5
    assert result.job.status == "released"
    assert result.job.released_at == datetime(2026, 6, 9, 12, 0, 0)
    assert repository.saved_jobs == [job]


@pytest.mark.asyncio
async def test_estimate_delegates_to_gateway(session: DummySession) -> None:
    service, _repository, gateway = _service(FakeJob())

    result = await service.estimate_credit_cost(
        session,
        operation_type="image_generation",
        estimated_credits=7,
    )

    assert result is gateway.estimate_result
    assert gateway.calls[-1] == (
        "estimate_credit_cost",
        {
            "session": session,
            "operation_type": "image_generation",
            "estimated_credits": 7,
        },
    )


@pytest.mark.asyncio
async def test_availability_delegates_to_gateway(session: DummySession) -> None:
    service, _repository, gateway = _service(FakeJob())

    result = await service.check_credit_availability(
        session,
        organization_id="org-1",
        operation_type="image_generation",
        estimated_credits=7,
    )

    assert result is gateway.availability_result
    assert gateway.calls[-1] == (
        "check_credit_availability",
        {
            "session": session,
            "organization_id": "org-1",
            "operation_type": "image_generation",
            "estimated_credits": 7,
        },
    )


def test_source_has_no_forbidden_integration_patterns() -> None:
    source = inspect.getsource(AIJobAsyncOrchestrationService)
    forbidden_terms = (
        "".join(["Async", "Session", "Local"]),
        "".join([".", "commit", "("]),
        "".join(["create", "_async", "_engine"]),
        "".join(["Credit", "Ledger", "Service", "("]),
        "".join(["Credit", "Gate", "Service", "("]),
        "".join(["sq", "lite"]),
        "".join(["Sq", "lite"]),
        "".join(["aio", "".join(["sq", "lite"])]),
        "".join(["sq", "lite", "3"]),
        "".join(["get", "(", "job_id", ")"]),
    )

    assert all(term not in source for term in forbidden_terms)
