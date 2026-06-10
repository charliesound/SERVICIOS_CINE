from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://placeholder:placeholder@localhost:5432/placeholder",
)
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_worker_mock_service import (
    AIJobWorkerMockCommand,
    AIJobWorkerMockError,
    AIJobWorkerMockInvalidModeError,
    AIJobWorkerMockService,
    AIJobWorkerMockSettlementError,
)


class DummySession:
    pass


class FakeJob:
    def __init__(
        self,
        *,
        organization_id: str = "org-1",
        job_id: str = "job-1",
        status: str = "reserved",
        reserved_credits: int | None = 8,
    ) -> None:
        self.organization_id = organization_id
        self.id = job_id
        self.status = status
        self.reserved_credits = reserved_credits
        self.consumed_credits = 0
        self.released_credits = 0
        self.consume_entry_id = None
        self.release_entry_id = None
        self.job_metadata = {}


class FakeOrchestrationService:
    def __init__(self, job: FakeJob) -> None:
        self.job = job
        self.calls: list[tuple[str, object]] = []

    async def get_ai_job(self, session, organization_id: str, job_id: str):
        del session
        self.calls.append(("get", (organization_id, job_id)))
        if self.job.organization_id != organization_id or self.job.id != job_id:
            return None
        return self.job

    async def enqueue_ai_job(self, session, request):
        del session
        self.calls.append(("enqueue", request))
        self.job.status = "queued"
        return SimpleNamespace(job=self.job)

    async def start_ai_job(self, session, request):
        del session
        self.calls.append(("start", request))
        self.job.status = "running"
        return SimpleNamespace(job=self.job)

    async def succeed_ai_job(self, session, request):
        del session
        self.calls.append(("succeed", request))
        self.job.status = "succeeded"
        self.job.job_metadata.setdefault("mock_worker", {})["output"] = request.output_metadata
        return SimpleNamespace(job=self.job)

    async def fail_ai_job(self, session, request):
        del session
        self.calls.append(("fail", request))
        self.job.status = "failed"
        self.job.job_metadata.setdefault("mock_worker", {})["error"] = request.error_metadata
        return SimpleNamespace(job=self.job)

    async def cancel_ai_job(self, session, request):
        del session
        self.calls.append(("cancel", request))
        self.job.status = "cancelled"
        self.job.job_metadata.setdefault("mock_worker", {})["error"] = request.error_metadata
        return SimpleNamespace(job=self.job)

    async def mark_consume_pending(self, session, request):
        del session
        self.calls.append(("mark_consume_pending", request))
        self.job.status = "consume_pending"
        return SimpleNamespace(job=self.job)

    async def mark_release_pending(self, session, request):
        del session
        self.calls.append(("mark_release_pending", request))
        self.job.status = "release_pending"
        return SimpleNamespace(job=self.job)

    async def consume_ai_job_credits(self, session, request):
        del session
        self.calls.append(("consume", request))
        self.job.status = "consumed"
        self.job.consumed_credits = request.actual_credits
        self.job.consume_entry_id = "consume-entry-1"
        return SimpleNamespace(job=self.job)

    async def release_ai_job_credits(self, session, request):
        del session
        self.calls.append(("release", request))
        self.job.status = "released"
        self.job.released_credits = request.release_credits
        self.job.release_entry_id = "release-entry-1"
        return SimpleNamespace(job=self.job)


@pytest.fixture
def session() -> DummySession:
    return DummySession()


def _command(**overrides) -> AIJobWorkerMockCommand:
    values = {
        "organization_id": "org-1",
        "job_id": "job-1",
        "requested_by": "worker-test",
        "execution_attempt_id": "attempt-1",
        "mode": "success",
    }
    values.update(overrides)
    return AIJobWorkerMockCommand(**values)


def _service(job: FakeJob) -> tuple[AIJobWorkerMockService, FakeOrchestrationService]:
    orchestration = FakeOrchestrationService(job)
    return AIJobWorkerMockService(orchestration), orchestration


@pytest.mark.asyncio
async def test_success_path_calls_orchestration_in_order(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(reserved_credits=9))

    result = await service.execute(
        session,
        _command(mode="success", mock_output_metadata={"asset_id": "asset-1"}),
    )

    assert [name for name, _payload in orchestration.calls] == [
        "get",
        "enqueue",
        "start",
        "succeed",
        "mark_consume_pending",
        "consume",
    ]
    consume_request = orchestration.calls[-1][1]
    assert consume_request.actual_credits == 9
    assert consume_request.caller_key == "attempt-1"
    assert result.status == "consumed"
    assert result.consume_entry_id == "consume-entry-1"
    assert result.consumed_credits == 9
    assert result.output_metadata == {"asset_id": "asset-1"}


@pytest.mark.asyncio
async def test_failure_path_calls_orchestration_in_order(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(reserved_credits=7))

    result = await service.execute(
        session,
        _command(
            mode="failure",
            mock_error_code="mock_failed",
            mock_error_message="safe message",
        ),
    )

    assert [name for name, _payload in orchestration.calls] == [
        "get",
        "enqueue",
        "start",
        "fail",
        "mark_release_pending",
        "release",
    ]
    release_request = orchestration.calls[-1][1]
    assert release_request.release_credits == 7
    assert release_request.caller_key == "attempt-1"
    assert result.status == "released"
    assert result.release_entry_id == "release-entry-1"
    assert result.released_credits == 7
    assert result.error_metadata == {"code": "mock_failed", "message": "safe message"}


@pytest.mark.asyncio
async def test_cancel_path_for_cancel_requested_job_releases(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(status="cancel_requested", reserved_credits=5))

    result = await service.execute(
        session,
        _command(mode="cancel", mock_error_code="cancelled"),
    )

    assert [name for name, _payload in orchestration.calls] == [
        "get",
        "cancel",
        "mark_release_pending",
        "release",
    ]
    release_request = orchestration.calls[-1][1]
    assert release_request.release_credits == 5
    assert release_request.caller_key == "attempt-1"
    assert result.status == "released"
    assert result.release_entry_id == "release-entry-1"


@pytest.mark.asyncio
async def test_cancel_path_requires_existing_cancel_requested_status(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(status="reserved"))

    with pytest.raises(AIJobWorkerMockError, match="cancel_requested"):
        await service.execute(session, _command(mode="cancel"))

    assert [name for name, _payload in orchestration.calls] == ["get"]


@pytest.mark.parametrize(
    "field",
    ["organization_id", "job_id", "requested_by", "execution_attempt_id"],
)
@pytest.mark.asyncio
async def test_required_text_fields_are_validated(session: DummySession, field: str) -> None:
    service, orchestration = _service(FakeJob())

    with pytest.raises(AIJobWorkerMockError, match=field):
        await service.execute(session, _command(**{field: " "}))

    assert orchestration.calls == []


@pytest.mark.asyncio
async def test_get_ai_job_returns_none_fails_before_any_transition(session: DummySession) -> None:
    class NotFoundOrchestration(FakeOrchestrationService):
        async def get_ai_job(self, session, organization_id, job_id):
            self.calls.append(("get", (organization_id, job_id)))
            return None

    orchestration = NotFoundOrchestration(FakeJob())
    service = AIJobWorkerMockService(orchestration)

    for mode in ("success", "failure", "cancel"):
        orchestration.calls.clear()

        with pytest.raises(AIJobWorkerMockError, match="AI job not found for mock worker execution"):
            await service.execute(session, _command(mode=mode))

        assert [name for name, _ in orchestration.calls] == ["get"]


@pytest.mark.asyncio
async def test_invalid_mode_fails(session: DummySession) -> None:
    service, orchestration = _service(FakeJob())

    with pytest.raises(AIJobWorkerMockInvalidModeError):
        await service.execute(session, _command(mode="other"))

    assert orchestration.calls == []


@pytest.mark.asyncio
async def test_explicit_success_credits_are_validated_and_used(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(reserved_credits=9))

    result = await service.execute(session, _command(mode="success", actual_credits=3))

    assert orchestration.calls[-1][1].actual_credits == 3
    assert result.consumed_credits == 3


@pytest.mark.asyncio
async def test_explicit_release_credits_are_validated_and_used(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(reserved_credits=9))

    result = await service.execute(session, _command(mode="failure", release_credits=4))

    assert orchestration.calls[-1][1].release_credits == 4
    assert result.released_credits == 4


@pytest.mark.asyncio
async def test_missing_reserved_credits_fails(session: DummySession) -> None:
    service, orchestration = _service(FakeJob(reserved_credits=None))

    with pytest.raises(AIJobWorkerMockSettlementError, match="reserved_credits"):
        await service.execute(session, _command(mode="success"))

    assert [name for name, _payload in orchestration.calls] == ["get"]


@pytest.mark.parametrize("duration", [-1, 60_001])
@pytest.mark.asyncio
async def test_invalid_simulated_duration_fails(session: DummySession, duration: int) -> None:
    service, orchestration = _service(FakeJob())

    with pytest.raises(AIJobWorkerMockError, match="simulated_duration_ms"):
        await service.execute(session, _command(simulated_duration_ms=duration))

    assert orchestration.calls == []


@pytest.mark.asyncio
async def test_metadata_is_json_safe(session: DummySession) -> None:
    service, orchestration = _service(FakeJob())

    with pytest.raises(AIJobWorkerMockError, match="JSON-safe"):
        await service.execute(
            session,
            _command(mode="success", mock_output_metadata={"bad": object()}),
        )

    assert orchestration.calls == []


@pytest.mark.asyncio
async def test_orchestration_errors_propagate(session: DummySession) -> None:
    class FailingOrchestration(FakeOrchestrationService):
        async def enqueue_ai_job(self, session, request):
            del session, request
            raise RuntimeError("boom")

    orchestration = FailingOrchestration(FakeJob())
    service = AIJobWorkerMockService(orchestration)

    with pytest.raises(RuntimeError, match="boom"):
        await service.execute(session, _command(mode="success"))


def test_worker_source_has_no_forbidden_direct_dependencies() -> None:
    source = (SRC_DIR / "services" / "ai_job_worker_mock_service.py").read_text(
        encoding="utf-8"
    )
    forbidden_terms = (
        "".join(["Async", "Session", "Local"]),
        "".join(["session", ".", "commit"]),
        "".join(["Credit", "Ledger", "Service"]),
        "".join(["Credit", "Gate", "Service"]),
        "".join(["AI", "Job", "Accounting", "Gateway"]),
        "".join(["Com", "fy", "UI"]),
        "".join(["op", "enai"]),
        "".join(["anth", "ropic"]),
        "".join(["ol", "lama"]),
    )

    assert all(term not in source for term in forbidden_terms)


def test_worker_mock_service_has_no_route_or_api_imports() -> None:
    source = (SRC_DIR / "services" / "ai_job_worker_mock_service.py").read_text()
    forbidden_terms = (
        "routes.",
        "internal_ai_job_worker_mock_routes",
        "dependencies.ai_job_worker_mock",
        "schemas.ai_job_worker_mock_api_schema",
        "FastAPI",
        "APIRouter",
        "HTTPException",
    )
    for term in forbidden_terms:
        assert term not in source, f"forbidden route/API dependency found: {term}"
