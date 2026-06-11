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
    AIJobAsyncAccountingError,
    AIJobAsyncCancelRequest,
    AIJobAsyncCancelCreditReleaseRequest,
    AIJobAsyncCancelCreditReleaseReconciliationRequest,
    AIJobAsyncInvalidStateError,
    AIJobAsyncNotFoundError,
    AIJobAsyncOrchestrationError,
    AIJobAsyncOrchestrationService,
)
from services.credit_ledger_service import DuplicateIdempotencyKeyError


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
    def __init__(
        self,
        job: FakeJob | None,
        candidates: list[FakeJob] | None = None,
    ) -> None:
        self.job = job
        self.candidates = candidates
        self.calls: list[tuple[str, tuple]] = []
        self.saved_jobs: list[FakeJob] = []

    async def get_for_update(self, organization_id: str, job_id: str) -> FakeJob | None:
        self.calls.append(("get_for_update", (organization_id, job_id)))
        if self.candidates is not None:
            for job in self.candidates:
                if job.organization_id == organization_id and job.id == job_id:
                    return job
            return None
        if self.job is None:
            return None
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def get(self, organization_id: str, job_id: str) -> FakeJob | None:
        self.calls.append(("get", (organization_id, job_id)))
        if self.candidates is not None:
            for job in self.candidates:
                if job.organization_id == organization_id and job.id == job_id:
                    return job
            return None
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

    async def list_cancelled_credit_release_candidates(
        self,
        organization_id: str,
        *,
        limit: int,
    ) -> list[FakeJob]:
        self.calls.append(
            ("list_cancelled_credit_release_candidates", (organization_id, limit))
        )
        source = self.candidates if self.candidates is not None else []
        return [
            job
            for job in source
            if job.organization_id == organization_id
            and job.status in {"cancel_requested", "cancelled", "release_pending"}
            and job.reservation_entry_id is not None
            and job.consume_entry_id is None
            and job.release_entry_id is None
            and job.consumed_credits == 0
            and job.reserved_credits > 0
        ][:limit]


class FakeAccountingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.release_entry_id = "release-entry-1"
        self.release_error: Exception | None = None
        self.release_errors_by_job_id: dict[str, Exception] = {}

    async def release_reserved_credits_for_job(self, _session, **kwargs):
        self.calls.append(("release_reserved_credits_for_job", kwargs))
        job_error = self.release_errors_by_job_id.get(str(kwargs.get("job_id", "")))
        if job_error is not None:
            raise job_error
        if self.release_error is not None:
            raise self.release_error
        return FakeAccountingResult(ledger_entry_id=self.release_entry_id)


@dataclass
class FakeAccountingResult:
    ledger_entry_id: str


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


def _service_with_candidates(
    candidates: list[FakeJob],
) -> tuple[AIJobAsyncOrchestrationService, FakeRepository, FakeAccountingGateway]:
    repository = FakeRepository(None, candidates=candidates)
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


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_from_cancel_requested_once(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancel_requested",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.job_id == "job-1"
    assert result.organization_id == "org-1"
    assert result.status == "released"
    assert result.release_required is True
    assert result.release_performed is True
    assert result.idempotent is False
    assert result.release_entry_id == "release-entry-1"
    assert result.message == "released cancelled AI job reserved credits"
    assert job.status == "released"
    assert job.cancelled_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.release_pending_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.released_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.released_credits == 8
    assert job.release_entry_id == "release-entry-1"
    assert repository.calls[0] == ("get_for_update", ("org-1", "job-1"))
    assert repository.saved_jobs == [job]
    assert gateway.calls == [
        (
            "release_reserved_credits_for_job",
            {
                "organization_id": "org-1",
                "job_id": "job-1",
                "reservation_entry_id": "reservation-entry-1",
                "release_credits": 8,
                "project_id": None,
                "user_id": None,
                "operation_type": "image_generation",
                "provider_type": None,
                "provider_name": None,
                "workflow_id": None,
                "workflow_version": None,
                "workflow_hash": None,
                "model_name": None,
                "input_asset_ids": None,
                "caller_key": "cancel:reservation-entry-1",
            },
        )
    ]


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_from_cancelled_status(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancelled",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
        consume_entry_id=None,
    )
    service, repository, gateway = _service(job)

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.status == "released"
    assert result.release_performed is True
    assert job.cancelled_at is None
    assert job.release_pending_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.released_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.release_entry_id == "release-entry-1"
    assert job.released_credits == 8
    assert job.reserved_credits == 8
    assert job.consume_entry_id is None
    assert repository.saved_jobs == [job]
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_from_release_pending_status(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="release_pending",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
        release_pending_at=datetime(2026, 6, 9, 11, 0, 0),
    )
    service, repository, gateway = _service(job)

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.status == "released"
    assert result.release_performed is True
    assert job.release_pending_at == datetime(2026, 6, 9, 11, 0, 0)
    assert job.released_at == datetime(2026, 6, 9, 12, 0, 0)
    assert job.release_entry_id == "release-entry-1"
    assert job.released_credits == 8
    assert repository.saved_jobs == [job]
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_with_release_entry_is_idempotent(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="released",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
        release_entry_id="release-entry-1",
        released_credits=8,
    )
    service, repository, gateway = _service(job)

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.status == "released"
    assert result.release_required is False
    assert result.release_performed is False
    assert result.idempotent is True
    assert result.release_entry_id == "release-entry-1"
    assert repository.saved_jobs == [job]
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_sequential_rerun_does_not_call_ledger_twice(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancelled",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)

    first = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )
    second = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert first.release_performed is True
    assert first.idempotent is False
    assert second.release_performed is False
    assert second.idempotent is True
    assert second.release_entry_id == "release-entry-1"
    assert job.release_entry_id == "release-entry-1"
    assert job.released_credits == 8
    assert job.reserved_credits == 8
    assert job.consume_entry_id is None
    assert [call for call, _kwargs in gateway.calls] == ["release_reserved_credits_for_job"]
    assert repository.saved_jobs == [job, job]


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_without_reservation_is_noop(
    session: DummySession,
) -> None:
    job = FakeJob(status="cancelled", reserved_credits=0, reservation_entry_id=None)
    service, repository, gateway = _service(job)

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.status == "cancelled"
    assert result.release_required is False
    assert result.release_performed is False
    assert result.idempotent is True
    assert result.release_entry_id is None
    assert result.message == "AI job has no reserved credits to release"
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_with_consume_entry_rejects(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancelled",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
        consume_entry_id="consume-entry-1",
    )
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError, match="after consumption"):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_with_consumed_credits_rejects(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancelled",
        reserved_credits=8,
        consumed_credits=1,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError, match="after consumption"):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_wrong_tenant_is_not_found(
    session: DummySession,
) -> None:
    service, repository, gateway = _service(
        FakeJob(
            organization_id="org-2",
            status="cancelled",
            reserved_credits=8,
            reservation_entry_id="reservation-entry-1",
        )
    )

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.calls == [("get_for_update", ("org-1", "job-1"))]
    assert repository.saved_jobs == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_reconciles_duplicate_idempotency(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="release_pending",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)
    gateway.release_error = DuplicateIdempotencyKeyError(
        "ai_job:org-1:job-1:release:cancel:reservation-entry-1",
        existing_entry_id="release-entry-1",
    )

    result = await service.release_cancelled_ai_job_reserved_credits(
        session,
        AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
    )

    assert result.status == "released"
    assert result.release_required is True
    assert result.release_performed is False
    assert result.idempotent is True
    assert result.release_entry_id == "release-entry-1"
    assert job.release_entry_id == "release-entry-1"
    assert job.released_credits == 8
    assert repository.saved_jobs == [job]
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_duplicate_without_existing_id_rejects(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="release_pending",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)
    gateway.release_error = DuplicateIdempotencyKeyError(
        "ai_job:org-1:job-1:release:cancel:reservation-entry-1",
        existing_entry_id=None,
    )

    with pytest.raises(AIJobAsyncAccountingError, match="without existing entry id"):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert job.status == "release_pending"
    assert job.release_entry_id is None
    assert job.released_credits == 0
    assert repository.saved_jobs == []
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_gateway_error_does_not_mark_released(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="cancelled",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)
    gateway.release_error = RuntimeError("ledger unavailable")

    with pytest.raises(RuntimeError, match="ledger unavailable"):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert job.status == "cancelled"
    assert job.release_entry_id is None
    assert job.released_credits == 0
    assert job.release_pending_at is None
    assert job.released_at is None
    assert repository.saved_jobs == []
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_release_cancelled_reserved_credits_non_eligible_status_rejects(
    session: DummySession,
) -> None:
    job = FakeJob(
        status="succeeded",
        reserved_credits=8,
        reservation_entry_id="reservation-entry-1",
    )
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncInvalidStateError, match="cannot be released"):
        await service.release_cancelled_ai_job_reserved_credits(
            session,
            AIJobAsyncCancelCreditReleaseRequest(organization_id="org-1", job_id="job-1"),
        )

    assert repository.saved_jobs == []
    assert gateway.calls == []


def _candidate(job_id: str, **overrides) -> FakeJob:
    values = {
        "id": job_id,
        "status": "cancelled",
        "reserved_credits": 8,
        "reservation_entry_id": f"reservation-{job_id}",
    }
    values.update(overrides)
    return FakeJob(**values)


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_releases_eligible_jobs(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1"), _candidate("job-2", status="release_pending")]
    service, repository, gateway = _service_with_candidates(jobs)

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(
            organization_id="org-1",
            max_items=10,
        ),
    )

    assert result.organization_id == "org-1"
    assert result.scanned_count == 2
    assert result.processed_count == 2
    assert result.released_count == 2
    assert result.skipped_count == 0
    assert result.failed_count == 0
    assert [item.error_category for item in result.per_job_results] == [
        "released_now",
        "released_now",
    ]
    assert [job.status for job in jobs] == ["released", "released"]
    assert [job.release_entry_id for job in jobs] == ["release-entry-1", "release-entry-1"]
    assert [call for call, _ in gateway.calls] == [
        "release_reserved_credits_for_job",
        "release_reserved_credits_for_job",
    ]
    assert repository.calls[0] == (
        "list_cancelled_credit_release_candidates",
        ("org-1", 10),
    )


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_dry_run_does_not_release(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1"), _candidate("job-2")]
    service, repository, gateway = _service_with_candidates(jobs)

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(
            organization_id="org-1",
            max_items=10,
            dry_run=True,
        ),
    )

    assert result.dry_run is True
    assert result.scanned_count == 2
    assert result.processed_count == 2
    assert result.released_count == 0
    assert result.skipped_count == 2
    assert result.failed_count == 0
    assert [item.error_category for item in result.per_job_results] == [
        "dry_run_eligible",
        "dry_run_eligible",
    ]
    assert [job.status for job in jobs] == ["cancelled", "cancelled"]
    assert gateway.calls == []
    assert [call for call, _ in repository.calls] == [
        "list_cancelled_credit_release_candidates"
    ]


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_max_items_limits_candidates(
    session: DummySession,
) -> None:
    service, _repository, gateway = _service_with_candidates(
        [_candidate("job-1"), _candidate("job-2"), _candidate("job-3")]
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(
            organization_id="org-1",
            max_items=2,
        ),
    )

    assert result.scanned_count == 2
    assert [item.job_id for item in result.per_job_results] == ["job-1", "job-2"]
    assert len(gateway.calls) == 2


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_selector_excludes_ineligible_jobs(
    session: DummySession,
) -> None:
    service, _repository, gateway = _service_with_candidates(
        [
            _candidate("eligible"),
            _candidate("no-reservation", reservation_entry_id=None),
            _candidate("already-released", release_entry_id="release-entry"),
            _candidate("consumed-entry", consume_entry_id="consume-entry"),
            _candidate("consumed-credits", consumed_credits=1),
            _candidate("released-status", status="released"),
            _candidate("succeeded-status", status="succeeded"),
            _candidate("no-credits", reserved_credits=0),
            _candidate("wrong-org", organization_id="org-2"),
        ]
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.scanned_count == 1
    assert [item.job_id for item in result.per_job_results] == ["eligible"]
    assert len(gateway.calls) == 1


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_job_error_does_not_abort_batch(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1"), _candidate("job-2")]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = RuntimeError("gateway unavailable")

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.processed_count == 2
    assert result.released_count == 1
    assert result.failed_count == 1
    assert [item.error_category for item in result.per_job_results] == [
        "retryable_error",
        "released_now",
    ]
    assert jobs[0].release_entry_id is None
    assert jobs[1].release_entry_id == "release-entry-1"


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_counts_idempotent_replay(
    session: DummySession,
) -> None:
    service, _repository, gateway = _service_with_candidates([_candidate("job-1")])
    gateway.release_error = DuplicateIdempotencyKeyError(
        "ai_job:org-1:job-1:release:cancel:reservation-job-1",
        existing_entry_id="release-entry-1",
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.released_count == 1
    assert result.failed_count == 0
    assert result.per_job_results[0].error_category == "idempotent_replay"
    assert result.per_job_results[0].idempotent is True
    assert result.per_job_results[0].release_entry_id == "release-entry-1"


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_accounting_error_is_terminal(
    session: DummySession,
) -> None:
    service, _repository, gateway = _service_with_candidates([_candidate("job-1")])
    gateway.release_error = DuplicateIdempotencyKeyError(
        "ai_job:org-1:job-1:release:cancel:reservation-job-1",
        existing_entry_id=None,
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.released_count == 0
    assert result.failed_count == 1
    assert result.per_job_results[0].error_category == "terminal_error"
    assert "without existing entry id" in result.per_job_results[0].message


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_requires_organization_id(
    session: DummySession,
) -> None:
    service, repository, gateway = _service_with_candidates([_candidate("job-1")])

    with pytest.raises(AIJobAsyncOrchestrationError, match="organization_id"):
        await service.process_cancelled_ai_job_credit_releases(
            session,
            AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id=" "),
        )

    assert repository.calls == []
    assert gateway.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("max_items", [0, -1, True, "bad"])
async def test_process_cancelled_credit_releases_validates_max_items(
    session: DummySession,
    max_items,
) -> None:
    service, repository, gateway = _service_with_candidates([_candidate("job-1")])

    with pytest.raises(AIJobAsyncOrchestrationError, match="max_items"):
        await service.process_cancelled_ai_job_credit_releases(
            session,
            AIJobAsyncCancelCreditReleaseReconciliationRequest(
                organization_id="org-1",
                max_items=max_items,
            ),
        )

    assert repository.calls == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_caps_max_items_at_100(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1")]
    service, repository, gateway = _service_with_candidates(jobs)

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(
            organization_id="org-1",
            max_items=200,
        ),
    )

    assert result.scanned_count == 1
    assert repository.calls[0] == (
        "list_cancelled_credit_release_candidates",
        ("org-1", 100),
    )


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_not_found_does_not_abort(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1"), _candidate("job-2")]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = AIJobAsyncNotFoundError("job disappeared")

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.processed_count == 2
    assert result.released_count == 1
    assert result.failed_count == 1
    error_categories = [item.error_category for item in result.per_job_results]
    assert "terminal_error" in error_categories
    assert jobs[0].release_entry_id is None
    assert jobs[1].release_entry_id == "release-entry-1"


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_unexpected_error_does_not_abort(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1"), _candidate("job-2")]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = ValueError("weird error")

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.processed_count == 2
    assert result.released_count == 1
    assert result.failed_count == 1
    assert result.per_job_results[0].error_category == "unexpected_error"
    assert jobs[0].release_entry_id is None
    assert jobs[1].release_entry_id == "release-entry-1"


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_invalid_state_consumption_maps_to_skipped_consumed(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1")]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = AIJobAsyncInvalidStateError(
        "Cannot release after consumption"
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.failed_count == 0
    assert result.skipped_count == 1
    assert result.per_job_results[0].error_category == "skipped_consumed"
    assert result.per_job_results[0].idempotent is False


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_invalid_state_generic_maps_to_skipped_not_eligible(
    session: DummySession,
) -> None:
    jobs = [_candidate("job-1")]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = AIJobAsyncInvalidStateError(
        "Job cannot be released in current state"
    )

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.failed_count == 0
    assert result.skipped_count == 1
    assert result.per_job_results[0].error_category == "skipped_not_eligible"
    assert result.per_job_results[0].idempotent is False


@pytest.mark.asyncio
async def test_process_cancelled_credit_releases_skipped_count_matches_others(
    session: DummySession,
) -> None:
    jobs = [
        _candidate("job-1"),
        _candidate("job-2"),
        _candidate("job-3"),
        _candidate("job-4"),
    ]
    service, _repository, gateway = _service_with_candidates(jobs)
    gateway.release_errors_by_job_id["job-1"] = AIJobAsyncInvalidStateError(
        "Cannot release after consumption"
    )
    gateway.release_errors_by_job_id["job-3"] = RuntimeError("timeout")

    result = await service.process_cancelled_ai_job_credit_releases(
        session,
        AIJobAsyncCancelCreditReleaseReconciliationRequest(organization_id="org-1"),
    )

    assert result.processed_count == 4
    assert result.released_count == 2  # job-2, job-4
    assert result.failed_count == 1  # job-3 retryable_error
    assert result.skipped_count == 1  # job-1 skipped_consumed
    assert result.released_count + result.failed_count + result.skipped_count == 4
    error_categories = [item.error_category for item in result.per_job_results]
    assert error_categories == [
        "skipped_consumed",
        "released_now",
        "retryable_error",
        "released_now",
    ]
