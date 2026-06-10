from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)

from models.ai_job import AIJob
from models.ai_job_execution_attempt import (
    AIJobExecutionAttempt,
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_SUCCEEDED,
)
from repositories.ai_job_execution_attempt_repository import AIJobExecutionAttemptRepository
from services.ai_job_worker_mock_execution_service import (
    FINGERPRINT_VERSION,
    AIJobWorkerMockExecutionConflictError,
    AIJobWorkerMockExecutionFingerprintMismatchError,
    AIJobWorkerMockExecutionInProgressError,
    AIJobWorkerMockExecutionResult,
    AIJobWorkerMockExecutionService,
    compute_execution_attempt_fingerprint,
)
from services.ai_job_worker_mock_service import (
    AIJobWorkerMockCommand,
    AIJobWorkerMockResult,
)
from tests.helpers.postgres_test_harness import (
    PostgresTestConfigError,
    cleanup_concurrent_tasks,
    open_independent_sessions,
    postgres_session_with_timeouts,
    require_validated_test_db_dsn,
    run_with_async_timeout,
    skip_if_postgres_test_unconfigured,
    temporary_postgres_billing_harness,
)


AI_JOB_ATTEMPT_TABLES = (
    "ai_jobs",
    "ai_job_execution_attempts",
)
SKIP_INTEGRATION_BACKEND_CONTEXT = True


def _unique_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _skip_if_postgres_test_dsn_is_unavailable_or_unsafe() -> None:
    skip_if_postgres_test_unconfigured()
    try:
        require_validated_test_db_dsn()
    except PostgresTestConfigError as exc:
        pytest.skip(str(exc))


def _command(
    *,
    organization_id: str | None = None,
    job_id: str | None = None,
    execution_attempt_id: str | None = None,
    actual_credits: int | None = None,
    mock_output_metadata: dict[str, object] | None = None,
) -> AIJobWorkerMockCommand:
    return AIJobWorkerMockCommand(
        organization_id=organization_id or _unique_id("org"),
        job_id=job_id or _unique_id("job"),
        requested_by="postgres-integration-test",
        execution_attempt_id=execution_attempt_id or _unique_id("attempt"),
        mode="success",
        mock_output_metadata=mock_output_metadata,
        actual_credits=actual_credits,
    )


async def _create_ai_job(session, command: AIJobWorkerMockCommand) -> AIJob:
    job = AIJob(
        id=command.job_id,
        organization_id=command.organization_id,
        operation_type="mock_worker_postgres_integration",
        status="reserved",
        estimated_credits=10,
        reserved_credits=10,
    )
    session.add(job)
    await session.flush()
    return job


async def _count_attempts(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(AIJobExecutionAttempt)
        .where(AIJobExecutionAttempt.organization_id == organization_id)
        .where(AIJobExecutionAttempt.job_id == job_id)
        .where(AIJobExecutionAttempt.execution_attempt_id == execution_attempt_id)
    )
    return int(result.scalar_one())


async def _load_attempt(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
) -> AIJobExecutionAttempt | None:
    return await AIJobExecutionAttemptRepository(session).get(
        organization_id,
        job_id,
        execution_attempt_id,
    )


async def _cleanup_attempt_key(session, command: AIJobWorkerMockCommand) -> None:
    await session.execute(
        delete(AIJobExecutionAttempt)
        .where(AIJobExecutionAttempt.organization_id == command.organization_id)
        .where(AIJobExecutionAttempt.job_id == command.job_id)
        .where(AIJobExecutionAttempt.execution_attempt_id == command.execution_attempt_id)
    )
    await session.execute(
        delete(AIJob)
        .where(AIJob.organization_id == command.organization_id)
        .where(AIJob.id == command.job_id)
    )
    # Integration visibility across independent sessions requires test-level commits.
    await session.commit()


class FakeWorkerService:
    def __init__(
        self,
        *,
        worker_entered: asyncio.Event | None = None,
        release_worker: asyncio.Event | None = None,
    ) -> None:
        self.calls: list[AIJobWorkerMockCommand] = []
        self.worker_entered = worker_entered
        self.release_worker = release_worker

    async def execute(self, session, command: AIJobWorkerMockCommand) -> AIJobWorkerMockResult:
        del session
        self.calls.append(command)
        if self.worker_entered is not None:
            self.worker_entered.set()
        if self.release_worker is not None:
            await asyncio.wait_for(self.release_worker.wait(), timeout=5)
        return AIJobWorkerMockResult(
            organization_id=command.organization_id,
            job_id=command.job_id,
            mode=command.mode,
            status="consumed",
            consumed_credits=command.actual_credits or 7,
            consume_entry_id=f"consume-{command.execution_attempt_id}",
            output_metadata=command.mock_output_metadata or {},
        )


def _service(worker: FakeWorkerService) -> AIJobWorkerMockExecutionService:
    return AIJobWorkerMockExecutionService(
        worker_service=worker,  # type: ignore[arg-type]
        attempt_repository_factory=AIJobExecutionAttemptRepository,
    )


@pytest.mark.asyncio
async def test_first_execution_persists_attempt() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    command = _command(actual_credits=9)
    worker = FakeWorkerService()

    async with temporary_postgres_billing_harness(AI_JOB_ATTEMPT_TABLES) as harness:
        async with harness.session_factory() as session:
            await _create_ai_job(session, command)
            result = await _service(worker).execute(session, command)

            assert result.replay is False
            assert result.attempt_status == ATTEMPT_STATUS_SUCCEEDED
            assert len(worker.calls) == 1
            assert await _count_attempts(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            ) == 1

            attempt = await _load_attempt(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            assert attempt is not None
            assert attempt.status == ATTEMPT_STATUS_SUCCEEDED
            assert attempt.fingerprint_version == FINGERPRINT_VERSION
            assert attempt.result_status == "consumed"
            assert attempt.consume_entry_id == f"consume-{command.execution_attempt_id}"
            assert attempt.consumed_credits == 9
            assert attempt.started_at is not None
            assert attempt.finished_at is not None

        async with harness.session_factory() as cleanup_session:
            await _cleanup_attempt_key(cleanup_session, command)


@pytest.mark.asyncio
async def test_terminal_replay_same_fingerprint_does_not_call_worker_again() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    command = _command(actual_credits=8)
    first_worker = FakeWorkerService()
    replay_worker = FakeWorkerService()

    async with temporary_postgres_billing_harness(AI_JOB_ATTEMPT_TABLES) as harness:
        async with harness.session_factory() as session:
            await _create_ai_job(session, command)
            first_result = await _service(first_worker).execute(session, command)
            assert first_result.replay is False
            # Commit makes the terminal attempt visible to an independent replay session.
            await session.commit()

        async with harness.session_factory() as session:
            replay_result = await _service(replay_worker).execute(session, command)

            assert replay_result.replay is True
            assert replay_result.attempt_status == ATTEMPT_STATUS_SUCCEEDED
            assert replay_result.result.status == "consumed"
            assert replay_result.result.consume_entry_id == f"consume-{command.execution_attempt_id}"
            assert replay_result.result.consumed_credits == 8
            assert first_worker.calls == [command]
            assert replay_worker.calls == []
            assert await _count_attempts(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            ) == 1

        async with harness.session_factory() as cleanup_session:
            await _cleanup_attempt_key(cleanup_session, command)


@pytest.mark.asyncio
async def test_fingerprint_mismatch_does_not_call_worker_again_or_mutate_row() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    command = _command(actual_credits=7)
    conflicting = _command(
        organization_id=command.organization_id,
        job_id=command.job_id,
        execution_attempt_id=command.execution_attempt_id,
        actual_credits=11,
    )
    first_worker = FakeWorkerService()
    conflicting_worker = FakeWorkerService()

    async with temporary_postgres_billing_harness(AI_JOB_ATTEMPT_TABLES) as harness:
        async with harness.session_factory() as session:
            await _create_ai_job(session, command)
            await _service(first_worker).execute(session, command)
            original = await _load_attempt(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            assert original is not None
            original_fingerprint = original.fingerprint
            original_consumed_credits = original.consumed_credits
            await session.commit()

        async with harness.session_factory() as session:
            with pytest.raises(AIJobWorkerMockExecutionFingerprintMismatchError):
                await _service(conflicting_worker).execute(session, conflicting)

            attempt = await _load_attempt(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            assert attempt is not None
            assert attempt.fingerprint == original_fingerprint
            assert attempt.consumed_credits == original_consumed_credits
            assert attempt.status == ATTEMPT_STATUS_SUCCEEDED
            assert conflicting_worker.calls == []
            assert await _count_attempts(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            ) == 1

        async with harness.session_factory() as cleanup_session:
            await _cleanup_attempt_key(cleanup_session, command)


@pytest.mark.asyncio
async def test_in_progress_conflict_baseline_does_not_call_worker() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    command = _command(actual_credits=7)
    worker = FakeWorkerService()

    async with temporary_postgres_billing_harness(AI_JOB_ATTEMPT_TABLES) as harness:
        async with harness.session_factory() as session:
            await _create_ai_job(session, command)
            session.add(
                AIJobExecutionAttempt(
                    organization_id=command.organization_id,
                    job_id=command.job_id,
                    execution_attempt_id=command.execution_attempt_id,
                    mode=command.mode,
                    status=ATTEMPT_STATUS_IN_PROGRESS,
                    fingerprint=compute_execution_attempt_fingerprint(command),
                    fingerprint_version=FINGERPRINT_VERSION,
                    requested_by=command.requested_by,
                )
            )
            # Commit makes the in-progress row visible to the wrapper session.
            await session.commit()

        async with harness.session_factory() as session:
            with pytest.raises(AIJobWorkerMockExecutionInProgressError):
                await _service(worker).execute(session, command)

            attempt = await _load_attempt(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            assert attempt is not None
            assert attempt.status == ATTEMPT_STATUS_IN_PROGRESS
            assert worker.calls == []
            assert await _count_attempts(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            ) == 1

        async with harness.session_factory() as cleanup_session:
            await _cleanup_attempt_key(cleanup_session, command)


@pytest.mark.asyncio
async def test_concurrent_same_key_same_payload_calls_worker_at_most_once() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    command = _command(actual_credits=6)
    worker_entered = asyncio.Event()
    release_worker = asyncio.Event()
    worker = FakeWorkerService(
        worker_entered=worker_entered,
        release_worker=release_worker,
    )
    tasks: list[asyncio.Task[AIJobWorkerMockExecutionResult]] = []

    async with temporary_postgres_billing_harness(AI_JOB_ATTEMPT_TABLES) as harness:
        async with harness.session_factory() as setup_session:
            await _create_ai_job(setup_session, command)
            # Test-level commit makes the job visible to independent sessions.
            await setup_session.commit()

        try:
            async with open_independent_sessions(harness.session_factory, count=2) as (
                session_a,
                session_b,
            ):

                async def execute_first() -> AIJobWorkerMockExecutionResult:
                    async with postgres_session_with_timeouts(
                        lambda: session_a,  # type: ignore[arg-type]
                        statement_timeout_ms=4_000,
                        lock_timeout_ms=2_000,
                    ) as session:
                        result = await _service(worker).execute(session, command)
                        # Test-level commit releases the unique-key wait for session B.
                        await session.commit()
                        return result

                async def execute_second() -> AIJobWorkerMockExecutionResult:
                    async with postgres_session_with_timeouts(
                        lambda: session_b,  # type: ignore[arg-type]
                        statement_timeout_ms=4_000,
                        lock_timeout_ms=2_000,
                    ) as session:
                        result = await _service(worker).execute(session, command)
                        await session.commit()
                        return result

                task_a = asyncio.create_task(execute_first())
                tasks.append(task_a)
                await run_with_async_timeout(
                    worker_entered.wait(),
                    timeout_seconds=2,
                    label="first worker entry",
                )

                task_b = asyncio.create_task(execute_second())
                tasks.append(task_b)
                release_worker.set()
                gathered = await run_with_async_timeout(
                    asyncio.gather(task_a, task_b, return_exceptions=True),
                    timeout_seconds=8,
                    label="same-key concurrent wrapper executions",
                )
        finally:
            await cleanup_concurrent_tasks(
                [task for task in tasks if not task.done()],
                timeout_seconds=2,
            )

        successes = [item for item in gathered if isinstance(item, AIJobWorkerMockExecutionResult)]
        failures = [item for item in gathered if isinstance(item, BaseException)]

        assert len(worker.calls) == 1
        assert any(result.replay is False for result in successes)
        replay_results = [result for result in successes if result.replay is True]
        assert len(replay_results) <= 1
        assert all(
            isinstance(
                failure,
                (
                    AIJobWorkerMockExecutionConflictError,
                    SQLAlchemyError,
                ),
            )
            for failure in failures
        )
        assert len(successes) + len(failures) == 2
        assert all(task.done() for task in tasks)

        async with harness.session_factory() as session:
            assert await _count_attempts(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            ) == 1
            attempt = await _load_attempt(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            assert attempt is not None
            assert attempt.status == ATTEMPT_STATUS_SUCCEEDED

        async with harness.session_factory() as cleanup_session:
            await _cleanup_attempt_key(cleanup_session, command)
