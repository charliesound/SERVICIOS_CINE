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
    AIJobAsyncCreditCheckRequest,
    AIJobAsyncCreateRequest,
    AIJobAsyncIdempotencyConflictError,
    AIJobAsyncEstimateRequest,
    AIJobAsyncNotFoundError,
    AIJobAsyncListRequest,
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


@dataclass
class FakeEstimateResult:
    operation_type: str
    estimated_credits: int


@dataclass
class FakeAvailabilityResult:
    organization_id: str
    operation_type: str
    estimated_credits: int
    sufficient: bool


class FakeJob:
    def __init__(
        self,
        *,
        organization_id: str = "org-1",
        job_id: str = "job-1",
        status: str = "credit_checked",
        operation_type: str = "image_generation",
        estimated_credits: int = 8,
        reserved_credits: int = 8,
        reservation_entry_id: str | None = "reservation-entry-1",
        idempotency_key: str | None = None,
        project_id: str | None = "project-1",
        user_id: str | None = "user-1",
        provider_type: str | None = "provider-type",
        provider_name: str | None = "provider-name",
        workflow_id: str | None = "workflow-1",
        workflow_version: str | None = "v1",
        workflow_hash: str | None = "hash-1",
        model_name: str | None = "model-a",
        input_asset_ids: list[str] | None = None,
        output_asset_ids: list[str] | None = None,
        job_metadata: dict | None = None,
    ) -> None:
        self.id = job_id
        self.organization_id = organization_id
        self.project_id = project_id
        self.user_id = user_id
        self.operation_type = operation_type
        self.status = status
        self.estimated_credits = estimated_credits
        self.reserved_credits = reserved_credits
        self.consumed_credits = 0
        self.released_credits = 0
        self.reservation_entry_id = reservation_entry_id
        self.consume_entry_id = None
        self.release_entry_id = None
        self.idempotency_key = idempotency_key
        self.provider_type = provider_type
        self.provider_name = provider_name
        self.workflow_id = workflow_id
        self.workflow_version = workflow_version
        self.workflow_hash = workflow_hash
        self.model_name = model_name
        self.input_asset_ids = input_asset_ids if input_asset_ids is not None else ["asset-1"]
        self.output_asset_ids = output_asset_ids if output_asset_ids is not None else []
        self.attempt_number = 1
        self.created_at = datetime(2026, 6, 9, 10, 0, 0)
        self.reserved_at = None
        self.estimated_at = None
        self.credit_checked_at = None
        self.consumed_at = None
        self.released_at = None
        self.job_metadata = job_metadata if job_metadata is not None else {
            "client_ref": "abc",
            "operation_type": operation_type,
            "estimated_credits": 0,
            "job_status": status,
        }


class FakeRepository:
    def __init__(self, job: FakeJob | None) -> None:
        self.job = job
        self.calls: list[tuple[str, tuple]] = []
        self.saved_jobs: list[FakeJob] = []
        self.created_jobs: list[FakeJob] = []
        self._idempotency_index: dict[tuple[str, str], FakeJob] = {}
        if job is not None and job.idempotency_key:
            self._idempotency_index[(job.organization_id, job.idempotency_key)] = job

    async def find_by_idempotency_key(self, organization_id: str, idempotency_key: str) -> FakeJob | None:
        self.calls.append(("find_by_idempotency_key", (organization_id, idempotency_key)))
        return self._idempotency_index.get((organization_id, idempotency_key))

    async def create(self, job: FakeJob) -> FakeJob:
        self.calls.append(("create", (job,)))
        self.created_jobs.append(job)
        self.job = job
        if job.idempotency_key:
            self._idempotency_index[(job.organization_id, job.idempotency_key)] = job
        return job

    async def get_for_update(self, organization_id: str, job_id: str) -> FakeJob | None:
        self.calls.append(("get_for_update", (organization_id, job_id)))
        if self.job is None:
            return None
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def get(self, *args):
        self.calls.append(("get", args))
        organization_id, job_id = args
        if self.job is None:
            return None
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def list_for_organization(self, organization_id: str, **kwargs):
        self.calls.append(("list_for_organization", (organization_id, kwargs)))
        if self.job is None or self.job.organization_id != organization_id:
            return [], None
        return [self.job], None

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
        self.estimate_result = FakeEstimateResult("image_generation", 11)
        self.availability_result = FakeAvailabilityResult("org-1", "image_generation", 11, True)

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
async def test_create_creates_ai_job(session: DummySession) -> None:
    service, repository, _gateway = _service(None)

    result = await service.create_ai_job(
        session,
        AIJobAsyncCreateRequest(
            organization_id="org-1",
            operation_type=" image_generation ",
            user_id="user-1",
            project_id="project-1",
            metadata={"client_ref": "abc"},
            provider_type="provider-type",
            provider_name="provider-name",
            workflow_id="workflow-1",
            workflow_version="v1",
            workflow_hash="hash-1",
            model_name="model-a",
            input_asset_ids=["asset-1", ""],
            output_asset_ids=[" output-1 "],
        ),
    )

    assert result.message == "AI job created"
    assert result.job.organization_id == "org-1"
    assert result.job.operation_type == "image_generation"
    assert result.job.status == "created"
    assert result.job.estimated_credits == 0
    assert result.job.reserved_credits == 0
    assert result.job.consumed_credits == 0
    assert result.job.released_credits == 0
    assert result.job.created_at == datetime(2026, 6, 9, 12, 0, 0)
    assert result.job.input_asset_ids == ["asset-1"]
    assert result.job.output_asset_ids == ["output-1"]
    assert result.job.job_metadata["operation_type"] == "image_generation"
    assert result.job.job_metadata["estimated_credits"] == 0
    assert result.job.job_metadata["job_status"] == "created"
    assert result.job.job_metadata["client_ref"] == "abc"
    assert repository.created_jobs == [result.job]


@pytest.mark.asyncio
async def test_create_normalizes_operation_type(session: DummySession) -> None:
    service, _repository, _gateway = _service(None)

    result = await service.create_ai_job(
        session,
        AIJobAsyncCreateRequest(
            organization_id="org-1",
            operation_type="  image_generation  ",
        ),
    )

    assert result.job.operation_type == "image_generation"
    assert result.job.job_metadata["operation_type"] == "image_generation"


@pytest.mark.asyncio
async def test_create_returns_existing_job_when_idempotent_and_equivalent(session: DummySession) -> None:
    existing = FakeJob(
        organization_id="org-1",
        status="created",
        operation_type="image_generation",
        idempotency_key="idem-1",
        job_metadata={"client_ref": "abc", "operation_type": "image_generation", "estimated_credits": 0, "job_status": "created"},
        reservation_entry_id=None,
        reserved_credits=0,
        estimated_credits=0,
        project_id=None,
        user_id=None,
        provider_type=None,
        provider_name=None,
        workflow_id=None,
        workflow_version=None,
        workflow_hash=None,
        model_name=None,
        input_asset_ids=[],
    )
    service, repository, _gateway = _service(existing)

    result = await service.create_ai_job(
        session,
        AIJobAsyncCreateRequest(
            organization_id="org-1",
            operation_type="image_generation",
            idempotency_key="idem-1",
            metadata={"client_ref": "abc"},
        ),
    )

    assert result.job is existing
    assert result.message == "AI job already exists"
    assert not repository.created_jobs


@pytest.mark.asyncio
async def test_create_raises_conflict_for_same_idempotency_key_different_payload(session: DummySession) -> None:
    existing = FakeJob(
        organization_id="org-1",
        status="created",
        operation_type="image_generation",
        idempotency_key="idem-1",
        job_metadata={"client_ref": "abc", "operation_type": "image_generation", "estimated_credits": 0, "job_status": "created"},
        reservation_entry_id=None,
        reserved_credits=0,
        estimated_credits=0,
        project_id=None,
        user_id=None,
        provider_type=None,
        provider_name=None,
        workflow_id=None,
        workflow_version=None,
        workflow_hash=None,
        model_name=None,
        input_asset_ids=[],
    )
    service, repository, _gateway = _service(existing)

    with pytest.raises(AIJobAsyncIdempotencyConflictError, match="Conflicting AI job create request"):
        await service.create_ai_job(
            session,
            AIJobAsyncCreateRequest(
                organization_id="org-1",
                operation_type="image_generation",
                idempotency_key="idem-1",
                metadata={"client_ref": "different"},
            ),
        )

    assert not repository.created_jobs


@pytest.mark.asyncio
async def test_create_idempotency_key_is_tenant_scoped(session: DummySession) -> None:
    existing = FakeJob(
        organization_id="org-2",
        status="created",
        operation_type="image_generation",
        idempotency_key="idem-1",
        job_metadata={"client_ref": "abc", "operation_type": "image_generation", "estimated_credits": 0, "job_status": "created"},
        reservation_entry_id=None,
        reserved_credits=0,
        estimated_credits=0,
        project_id=None,
        user_id=None,
        provider_type=None,
        provider_name=None,
        workflow_id=None,
        workflow_version=None,
        workflow_hash=None,
        model_name=None,
        input_asset_ids=[],
    )
    service, repository, _gateway = _service(existing)

    result = await service.create_ai_job(
        session,
        AIJobAsyncCreateRequest(
            organization_id="org-1",
            operation_type="image_generation",
            idempotency_key="idem-1",
            metadata={"client_ref": "abc"},
        ),
    )

    assert result.job.organization_id == "org-1"
    assert result.job is not existing
    assert repository.created_jobs


@pytest.mark.asyncio
async def test_get_ai_job_uses_tenant_scoped_repository_read(session: DummySession) -> None:
    service, repository, _gateway = _service(FakeJob())

    result = await service.get_ai_job(session, "org-1", "job-1")

    assert result.id == "job-1"
    assert repository.calls[-1] == ("get", ("org-1", "job-1"))


@pytest.mark.asyncio
async def test_get_ai_job_raises_not_found_for_wrong_tenant(session: DummySession) -> None:
    service, _repository, _gateway = _service(FakeJob(organization_id="org-2"))

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.get_ai_job(session, "org-1", "job-1")


@pytest.mark.asyncio
async def test_list_ai_jobs_delegates_with_tenant_and_filters(session: DummySession) -> None:
    service, repository, _gateway = _service(FakeJob())

    jobs, next_cursor = await service.list_ai_jobs(
        session,
        AIJobAsyncListRequest(
            organization_id="org-1",
            status=" created ",
            project_id="project-1",
            operation_type=" image_generation ",
            limit=25,
            cursor="job-0",
        ),
    )

    assert [job.id for job in jobs] == ["job-1"]
    assert next_cursor is None
    method, args = repository.calls[-1]
    organization_id, kwargs = args
    assert method == "list_for_organization"
    assert organization_id == "org-1"
    assert kwargs["status"] == "created"
    assert kwargs["operation_type"] == "image_generation"
    assert kwargs["limit"] == 25
    assert kwargs["cursor"] == "job-0"


@pytest.mark.asyncio
async def test_get_ai_job_history_derives_timestamped_events(session: DummySession) -> None:
    job = FakeJob(status="reserved")
    job.estimated_at = datetime(2026, 6, 9, 11, 0, 0)
    job.reserved_at = datetime(2026, 6, 9, 12, 0, 0)
    service, _repository, _gateway = _service(job)

    result = await service.get_ai_job_history(session, "org-1", "job-1")

    assert result.job_id == "job-1"
    assert [event["status"] for event in result.events] == [
        "created",
        "estimated",
        "reserved",
    ]


@pytest.mark.asyncio
async def test_estimate_uses_get_for_update(session: DummySession) -> None:
    service, repository, _gateway = _service(FakeJob(status="created", reservation_entry_id=None, reserved_credits=0))

    await service.estimate_ai_job(
        session,
        AIJobAsyncEstimateRequest(organization_id="org-1", job_id="job-1"),
    )

    assert repository.calls[0] == ("get_for_update", ("org-1", "job-1"))
    assert not any(method == "get" for method, _ in repository.calls)


@pytest.mark.asyncio
async def test_estimate_fails_if_job_not_found(session: DummySession) -> None:
    service, _repository, gateway = _service(None)

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.estimate_ai_job(
            session,
            AIJobAsyncEstimateRequest(organization_id="org-1", job_id="missing"),
        )

    assert gateway.calls == []


@pytest.mark.asyncio
async def test_estimate_delegates_to_gateway_and_saves_job(session: DummySession) -> None:
    job = FakeJob(status="created", reservation_entry_id=None, reserved_credits=0, estimated_credits=0)
    service, repository, gateway = _service(job)

    result = await service.estimate_ai_job(
        session,
        AIJobAsyncEstimateRequest(
            organization_id="org-1",
            job_id="job-1",
            estimated_credits=7,
        ),
    )

    method, payload = gateway.calls[-1]
    assert method == "estimate_credit_cost"
    assert payload["session"] is session
    assert payload["operation_type"] == "image_generation"
    assert payload["estimated_credits"] == 7
    assert result.job.operation_type == "image_generation"
    assert result.job.estimated_credits == 11
    assert result.job.status == "estimated"
    assert result.job.estimated_at == datetime(2026, 6, 9, 12, 0, 0)
    assert result.job.job_metadata["job_status"] == "estimated"
    assert result.job.job_metadata["estimated_credits"] == 11
    assert repository.saved_jobs == [job]


@pytest.mark.asyncio
async def test_check_uses_get_for_update(session: DummySession) -> None:
    service, repository, _gateway = _service(FakeJob(status="estimated", reservation_entry_id=None, reserved_credits=0, estimated_credits=11))

    await service.check_ai_job_credits(
        session,
        AIJobAsyncCreditCheckRequest(organization_id="org-1", job_id="job-1"),
    )

    assert repository.calls[0] == ("get_for_update", ("org-1", "job-1"))
    assert not any(method == "get" for method, _ in repository.calls)


@pytest.mark.asyncio
async def test_check_fails_if_job_not_found(session: DummySession) -> None:
    service, _repository, gateway = _service(None)

    with pytest.raises(AIJobAsyncNotFoundError):
        await service.check_ai_job_credits(
            session,
            AIJobAsyncCreditCheckRequest(organization_id="org-1", job_id="missing"),
        )

    assert gateway.calls == []


@pytest.mark.asyncio
async def test_check_requires_positive_credits_when_job_has_no_estimate(session: DummySession) -> None:
    job = FakeJob(status="estimated", reservation_entry_id=None, estimated_credits=0, reserved_credits=0)
    service, repository, gateway = _service(job)

    with pytest.raises(AIJobAsyncAccountingError, match="estimated_credits must be a positive integer"):
        await service.check_ai_job_credits(
            session,
            AIJobAsyncCreditCheckRequest(organization_id="org-1", job_id="job-1"),
        )

    assert gateway.calls == []
    assert repository.saved_jobs == []


@pytest.mark.asyncio
async def test_check_delegates_to_gateway_and_saves_job(session: DummySession) -> None:
    job = FakeJob(status="estimated", reservation_entry_id=None, estimated_credits=11, reserved_credits=0)
    service, repository, gateway = _service(job)

    result = await service.check_ai_job_credits(
        session,
        AIJobAsyncCreditCheckRequest(
            organization_id="org-1",
            job_id="job-1",
            estimated_credits=9,
        ),
    )

    method, payload = gateway.calls[-1]
    assert method == "check_credit_availability"
    assert payload["session"] is session
    assert payload["organization_id"] == "org-1"
    assert payload["operation_type"] == "image_generation"
    assert payload["estimated_credits"] == 9
    assert result.job.status == "credit_checked"
    assert result.job.credit_checked_at == datetime(2026, 6, 9, 12, 0, 0)
    assert result.job.job_metadata["job_status"] == "credit_checked"
    assert result.job.job_metadata["estimated_credits"] == 9
    assert repository.saved_jobs == [job]


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
