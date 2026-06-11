from __future__ import annotations

import inspect
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)

from models.ai_job_execution_attempt import (  # noqa: E402
    AIJobExecutionAttempt,
    ATTEMPT_STATUS_CANCELLED,
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_SUCCEEDED,
)
from services.ai_job_worker_mock_execution_service import (  # noqa: E402
    FINGERPRINT_VERSION,
    UNIQUE_ATTEMPT_CONSTRAINT,
    AIJobWorkerMockExecutionFingerprintMismatchError,
    AIJobWorkerMockExecutionInProgressError,
    AIJobWorkerMockExecutionInvalidStateError,
    AIJobWorkerMockExecutionReplayError,
    AIJobWorkerMockExecutionService,
    compute_execution_attempt_fingerprint,
)
from services.ai_job_worker_mock_service import (  # noqa: E402
    AIJobWorkerMockCancelledJobError,
    AIJobWorkerMockCommand,
    AIJobWorkerMockResult,
)


class DummySession:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    @asynccontextmanager
    async def begin_nested(self) -> DummySession:  # type: ignore[misc]
        yield self


class UniqueOrig(Exception):
    pgcode = "23505"

    def __init__(self) -> None:
        super().__init__(UNIQUE_ATTEMPT_CONSTRAINT)
        self.diag = type("Diag", (), {"constraint_name": UNIQUE_ATTEMPT_CONSTRAINT})()


class UnexpectedOrig(Exception):
    pgcode = "23505"

    def __init__(self) -> None:
        super().__init__("other_constraint")
        self.diag = type("Diag", (), {"constraint_name": "other_constraint"})()


def _unique_error() -> IntegrityError:
    return IntegrityError("insert", {}, UniqueOrig())


def _unexpected_error() -> IntegrityError:
    return IntegrityError("insert", {}, UnexpectedOrig())


def _command(**overrides: Any) -> AIJobWorkerMockCommand:
    values: dict[str, Any] = {
        "organization_id": "org-1",
        "job_id": "job-1",
        "requested_by": "tester",
        "execution_attempt_id": "attempt-1",
        "mode": "success",
        "simulated_duration_ms": None,
        "mock_output_metadata": None,
        "mock_error_code": None,
        "mock_error_message": None,
        "actual_credits": None,
        "release_credits": None,
    }
    values.update(overrides)
    return AIJobWorkerMockCommand(**values)


def _attempt(
    *,
    status: str,
    mode: str = "success",
    result_status: str | None = "consumed",
    fingerprint: str | None = None,
) -> AIJobExecutionAttempt:
    command = _command(mode=mode)
    return AIJobExecutionAttempt(
        organization_id=command.organization_id,
        job_id=command.job_id,
        execution_attempt_id=command.execution_attempt_id,
        mode=mode,
        status=status,
        fingerprint=fingerprint or compute_execution_attempt_fingerprint(command),
        fingerprint_version=FINGERPRINT_VERSION,
        result_status=result_status,
        consume_entry_id="consume-entry" if mode == "success" else None,
        release_entry_id="release-entry" if mode != "success" else None,
        consumed_credits=5 if mode == "success" else None,
        released_credits=5 if mode != "success" else None,
    )


class FakeRepository:
    def __init__(
        self,
        *,
        events: list[str],
        create_error: IntegrityError | None = None,
        existing_attempt: AIJobExecutionAttempt | None = None,
    ) -> None:
        self.events = events
        self.create_error = create_error
        self.existing_attempt = existing_attempt
        self.created_attempt: AIJobExecutionAttempt | None = None
        self.saved_attempt: AIJobExecutionAttempt | None = None
        self.get_for_update_calls: list[tuple[str, str, str]] = []

    async def create(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
        self.events.append("repo.create")
        self.created_attempt = attempt
        if self.create_error is not None:
            raise self.create_error
        return attempt

    async def get_for_update(
        self,
        organization_id: str,
        job_id: str,
        execution_attempt_id: str,
    ) -> AIJobExecutionAttempt | None:
        self.events.append("repo.get_for_update")
        self.get_for_update_calls.append((organization_id, job_id, execution_attempt_id))
        return self.existing_attempt

    async def save(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
        self.events.append("repo.save")
        self.saved_attempt = attempt
        return attempt


class FakeWorker:
    def __init__(self, events: list[str], result: AIJobWorkerMockResult | None = None) -> None:
        self.events = events
        self.calls: list[tuple[DummySession, AIJobWorkerMockCommand]] = []
        self.result = result or AIJobWorkerMockResult(
            organization_id="org-1",
            job_id="job-1",
            mode="success",
            status="consumed",
            consumed_credits=5,
            consume_entry_id="consume-entry",
        )

    async def execute(
        self,
        session: DummySession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockResult:
        self.events.append("worker.execute")
        self.calls.append((session, command))
        return self.result


def _service(
    *,
    repository: FakeRepository,
    worker: FakeWorker,
    now_values: list[datetime] | None = None,
) -> AIJobWorkerMockExecutionService:
    values = now_values or [datetime(2026, 6, 10, 10, 0, 0)]
    last_value = values[-1]
    iterator = iter(values)

    def now_fn() -> datetime:
        return next(iterator, last_value)

    return AIJobWorkerMockExecutionService(
        worker_service=worker,  # type: ignore[arg-type]
        attempt_repository_factory=lambda session: repository,  # type: ignore[return-value]
        now_fn=now_fn,
    )


def test_fingerprint_returns_64_hex_chars() -> None:
    fingerprint = compute_execution_attempt_fingerprint(_command())

    assert len(fingerprint) == 64
    assert all(char in "0123456789abcdef" for char in fingerprint)


def test_fingerprint_is_stable_for_unordered_metadata() -> None:
    first = compute_execution_attempt_fingerprint(
        _command(mock_output_metadata={"b": 2, "a": {"d": 4, "c": 3}})
    )
    second = compute_execution_attempt_fingerprint(
        _command(mock_output_metadata={"a": {"c": 3, "d": 4}, "b": 2})
    )

    assert first == second


def test_fingerprint_changes_if_mode_changes() -> None:
    assert compute_execution_attempt_fingerprint(
        _command(mode="success")
    ) != compute_execution_attempt_fingerprint(_command(mode="failure"))


def test_fingerprint_ignores_identity_and_requested_by() -> None:
    first = compute_execution_attempt_fingerprint(_command())
    second = compute_execution_attempt_fingerprint(
        _command(
            organization_id="org-2",
            job_id="job-2",
            execution_attempt_id="attempt-2",
            requested_by="other",
        )
    )

    assert first == second


@pytest.mark.asyncio
async def test_first_execution_creates_attempt_before_worker_call() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    await service.execute(DummySession(), _command())

    assert events == ["repo.create", "worker.execute", "repo.save"]
    assert len(worker.calls) == 1


@pytest.mark.asyncio
async def test_worker_guard_error_does_not_save_success_attempt() -> None:
    class GuardedWorker(FakeWorker):
        async def execute(
            self,
            session: DummySession,
            command: AIJobWorkerMockCommand,
        ) -> AIJobWorkerMockResult:
            self.events.append("worker.execute")
            self.calls.append((session, command))
            raise AIJobWorkerMockCancelledJobError(
                "Mock worker execution is blocked for AI job status: cancel_requested"
            )

    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = GuardedWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockCancelledJobError, match="cancel_requested"):
        await service.execute(DummySession(), _command())

    assert events == ["repo.create", "worker.execute"]
    assert repository.saved_attempt is None
    assert repository.created_attempt is not None
    assert repository.created_attempt.status == ATTEMPT_STATUS_IN_PROGRESS
    assert len(worker.calls) == 1


@pytest.mark.asyncio
async def test_success_marks_attempt_succeeded_and_stores_result_fields() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = FakeWorker(events=events)
    now_start = datetime(2026, 6, 10, 10, 0, 0)
    now_finish = now_start + timedelta(seconds=5)
    service = _service(
        repository=repository,
        worker=worker,
        now_values=[now_start, now_finish],
    )

    result = await service.execute(DummySession(), _command(mode="success"))

    assert result.replay is False
    assert result.attempt_status == ATTEMPT_STATUS_SUCCEEDED
    assert repository.saved_attempt is repository.created_attempt
    assert repository.saved_attempt is not None
    assert repository.saved_attempt.status == ATTEMPT_STATUS_SUCCEEDED
    assert repository.saved_attempt.result_status == "consumed"
    assert repository.saved_attempt.consume_entry_id == "consume-entry"
    assert repository.saved_attempt.consumed_credits == 5
    assert repository.saved_attempt.started_at == now_start
    assert repository.saved_attempt.finished_at == now_finish


@pytest.mark.asyncio
async def test_failure_marks_attempt_failed() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = FakeWorker(
        events=events,
        result=AIJobWorkerMockResult(
            organization_id="org-1",
            job_id="job-1",
            mode="failure",
            status="released",
            released_credits=7,
            release_entry_id="release-entry",
        ),
    )
    service = _service(repository=repository, worker=worker)

    result = await service.execute(DummySession(), _command(mode="failure"))

    assert result.attempt_status == ATTEMPT_STATUS_FAILED
    assert repository.saved_attempt is not None
    assert repository.saved_attempt.status == ATTEMPT_STATUS_FAILED
    assert repository.saved_attempt.result_status == "released"
    assert repository.saved_attempt.release_entry_id == "release-entry"
    assert repository.saved_attempt.released_credits == 7


@pytest.mark.asyncio
async def test_cancel_marks_attempt_cancelled() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = FakeWorker(
        events=events,
        result=AIJobWorkerMockResult(
            organization_id="org-1",
            job_id="job-1",
            mode="cancel",
            status="released",
            released_credits=3,
            release_entry_id="release-entry",
        ),
    )
    service = _service(repository=repository, worker=worker)

    result = await service.execute(DummySession(), _command(mode="cancel"))

    assert result.attempt_status == ATTEMPT_STATUS_CANCELLED
    assert repository.saved_attempt is not None
    assert repository.saved_attempt.status == ATTEMPT_STATUS_CANCELLED
    assert repository.saved_attempt.release_entry_id == "release-entry"
    assert repository.saved_attempt.released_credits == 3


@pytest.mark.asyncio
async def test_terminal_replay_returns_stored_result_and_does_not_call_worker() -> None:
    events: list[str] = []
    existing = _attempt(status=ATTEMPT_STATUS_SUCCEEDED, mode="success")
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=existing,
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    result = await service.execute(DummySession(), _command(mode="success"))

    assert result.replay is True
    assert result.attempt_status == ATTEMPT_STATUS_SUCCEEDED
    assert result.result.status == "consumed"
    assert result.result.consume_entry_id == "consume-entry"
    assert worker.calls == []
    assert events == ["repo.create", "repo.get_for_update"]


@pytest.mark.asyncio
async def test_fingerprint_mismatch_raises_conflict_without_worker_call() -> None:
    events: list[str] = []
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=_attempt(status=ATTEMPT_STATUS_SUCCEEDED, fingerprint="b" * 64),
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockExecutionFingerprintMismatchError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_in_progress_raises_conflict_without_worker_call() -> None:
    events: list[str] = []
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=_attempt(status=ATTEMPT_STATUS_IN_PROGRESS),
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockExecutionInProgressError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_expected_unique_integrity_error_triggers_replay_path() -> None:
    events: list[str] = []
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=_attempt(status=ATTEMPT_STATUS_SUCCEEDED),
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    await service.execute(DummySession(), _command())

    assert repository.get_for_update_calls == [("org-1", "job-1", "attempt-1")]
    assert worker.calls == []


@pytest.mark.asyncio
async def test_unexpected_integrity_error_is_propagated_without_worker_call() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events, create_error=_unexpected_error())
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(IntegrityError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_replay_without_loaded_attempt_raises_replay_error() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events, create_error=_unique_error())
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockExecutionReplayError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_invalid_stored_status_raises_invalid_state() -> None:
    events: list[str] = []
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=_attempt(status="unknown"),
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockExecutionInvalidStateError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_conflicted_status_is_not_replayed_in_v1() -> None:
    events: list[str] = []
    repository = FakeRepository(
        events=events,
        create_error=_unique_error(),
        existing_attempt=_attempt(status="conflicted", result_status=None),
    )
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)

    with pytest.raises(AIJobWorkerMockExecutionInvalidStateError):
        await service.execute(DummySession(), _command())

    assert worker.calls == []


@pytest.mark.asyncio
async def test_wrapper_does_not_commit() -> None:
    events: list[str] = []
    repository = FakeRepository(events=events)
    worker = FakeWorker(events=events)
    service = _service(repository=repository, worker=worker)
    session = DummySession()

    await service.execute(session, _command())

    assert session.commits == 0


def test_service_source_has_no_forbidden_session_or_accounting_dependencies() -> None:
    import services.ai_job_worker_mock_execution_service as module

    source = inspect.getsource(module)
    assert "AsyncSessionLocal" not in source
    assert ".commit(" not in source
    assert "CreditLedgerService" not in source
    assert "CreditGateService" not in source
    assert "AIJobAccountingGateway" not in source
    assert "AIJobCostingService" not in source
