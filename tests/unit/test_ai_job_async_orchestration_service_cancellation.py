from __future__ import annotations

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
    AIJobAsyncCancelRequest,
    AIJobAsyncInvalidStateError,
    AIJobAsyncNotFoundError,
    AIJobAsyncOrchestrationService,
)


class DummySession:
    pass


@dataclass
class FakeJob:
    organization_id: str = "org-1"
    id: str = "job-1"
    status: str = "created"
    operation_type: str = "image_generation"
    estimated_credits: int = 0
    reserved_credits: int = 0
    consumed_credits: int = 0
    released_credits: int = 0
    reservation_entry_id: str | None = None
    consume_entry_id: str | None = None
    release_entry_id: str | None = None
    job_metadata: dict | None = None
    created_at: datetime = datetime(2026, 6, 9, 10, 0, 0)
    estimated_at: datetime | None = None
    credit_checked_at: datetime | None = None
    reserved_at: datetime | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancel_requested_at: datetime | None = None
    cancelled_at: datetime | None = None
    consume_pending_at: datetime | None = None
    consumed_at: datetime | None = None
    release_pending_at: datetime | None = None
    released_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.job_metadata is None:
            self.job_metadata = {
                "operation_type": self.operation_type,
                "estimated_credits": self.estimated_credits,
                "job_status": self.status,
            }


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

    async def get(self, organization_id: str, job_id: str) -> FakeJob | None:
        self.calls.append(("get", (organization_id, job_id)))
        if self.job is None:
            return None
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def save(self, job: FakeJob) -> FakeJob:
        self.calls.append(("save", (job,)))
        self.saved_jobs.append(job)
        self.job = job
        return job


class FakeAccountingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []


@pytest.fixture
def session() -> DummySession:
    return DummySession()


def _service(
    job: FakeJob | None,
) -> tuple[AIJobAsyncOrchestrationService, FakeRepository, FakeAccountingGateway]:
    repository = FakeRepository(job)
    gateway = FakeAccountingGateway()
    service = AIJobAsyncOrchestrationService(
        repository=repository,
        accounting_gateway=gateway,
        now_fn=lambda: datetime(2026, 6, 9, 12, 0, 0),
    )
    return service, repository, gateway


@pytest.mark.asyncio
async def test_request_cancel_cancels_pending_pre_execution_job(
    session: DummySession,
) -> None:
    job = FakeJob(status="created")
    service, repository, gateway = _service(job)

    result = await service.request_cancel_ai_job(
        session,
        AIJobAsyncCancelRequest(
            organization_id="org-1",
            job_id="job-1",
            requested_by="user-1",
            reason="user requested",
        ),
    )

    assert result.message == "cancelled"
    assert result.job.status == "cancelled"
    assert result.job.cancelled_at == datetime(2026, 6, 9, 12, 0, 0)
    assert result.job.cancel_requested_at is None
    assert result.job.job_metadata["job_status"] == "cancelled"
    assert result.job.job_metadata["execution"]["requested_by"] == "user-1"
    assert result.job.job_metadata["execution"]["reason"] == "user requested"
    assert result.transition_plan is not None
    assert result.transition_plan.to_status == "cancelled"
    assert repository.calls[0] == ("get_for_update", ("org-1", "job-1"))
    assert repository.saved_jobs == [job]
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_repeated_cancel_is_idempotent(
    session: DummySession,
) -> None:
    job = FakeJob(status="created")
    service, repository, gateway = _service(job)

    first = await service.request_cancel_ai_job(
        session,
        AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
    )
    second = await service.request_cancel_ai_job(
        session,
        AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
    )

    assert first.job is second.job
    assert second.message == "AI job already cancelled"
    assert second.job.status == "cancelled"
    assert repository.saved_jobs == [job]
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_succeeded_job_is_not_cancelable(
    session: DummySession,
) -> None:
    job = FakeJob(status="succeeded")
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError, match="cannot be cancelled"):
        await service.request_cancel_ai_job(
            session,
            AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
        )

    assert job.status == "succeeded"
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_failed_job_is_not_cancelable(
    session: DummySession,
) -> None:
    job = FakeJob(status="failed")
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError, match="cannot be cancelled"):
        await service.request_cancel_ai_job(
            session,
            AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
        )

    assert job.status == "failed"
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_wrong_tenant_is_not_found(
    session: DummySession,
) -> None:
    service, repository, gateway = _service(FakeJob(organization_id="org-2"))

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.request_cancel_ai_job(
            session,
            AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.calls == [("get_for_update", ("org-1", "job-1"))]
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["reserved", "queued", "running"])
async def test_request_cancel_reserved_or_in_progress_job_marks_cancel_requested_only(
    session: DummySession,
    status: str,
) -> None:
    job = FakeJob(
        status=status,
        estimated_credits=8,
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)

    result = await service.request_cancel_ai_job(
        session,
        AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.message == "cancel requested"
    assert result.job.status == "cancel_requested"
    assert result.job.cancel_requested_at == datetime(2026, 6, 9, 12, 0, 0)
    assert result.job.cancelled_at is None
    assert result.job.release_pending_at is None
    assert result.job.released_at is None
    assert result.job.release_entry_id is None
    assert result.transition_plan is not None
    assert result.transition_plan.to_status == "cancel_requested"
    assert repository.saved_jobs == [job]
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_existing_cancel_requested_is_idempotent(
    session: DummySession,
) -> None:
    job = FakeJob(status="cancel_requested")
    service, repository, gateway = _service(job)

    result = await service.request_cancel_ai_job(
        session,
        AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.message == "AI job cancellation already requested"
    assert result.job is job
    assert result.job.status == "cancel_requested"
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_request_cancel_controlled_error_leaves_session_usable(
    session: DummySession,
) -> None:
    job = FakeJob(status="succeeded")
    service, repository, _gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError):
        await service.request_cancel_ai_job(
            session,
            AIJobAsyncCancelRequest(organization_id="org-1", job_id="job-1"),
        )

    loaded = await service.get_ai_job(session, "org-1", "job-1")

    assert loaded is job
    assert repository.calls[-1] == ("get", ("org-1", "job-1"))
    assert repository.saved_jobs == []
