from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.helpers.postgres_test_harness import (
    MINIMUM_BILLING_TABLES,
    PostgresTestConfigError,
    build_billing_test_metadata,
    cleanup_concurrent_tasks,
    is_postgres_test_configured,
    open_independent_sessions,
    postgres_session_with_timeouts,
    require_postgres_test_dsn,
    require_validated_test_db_dsn,
    run_with_async_timeout,
    set_local_postgres_timeouts,
    skip_if_postgres_test_unconfigured,
    temporary_postgres_billing_harness,
    validate_test_db_dsn,
)


class FakeAsyncSession:
    def __init__(self) -> None:
        self.executed_sql: list[str] = []
        self.rollbacks = 0
        self.closes = 0

    async def execute(self, statement) -> None:
        self.executed_sql.append(str(statement))

    async def rollback(self) -> None:
        self.rollbacks += 1

    async def close(self) -> None:
        self.closes += 1


class FakeSessionFactory:
    def __init__(self) -> None:
        self.sessions: list[FakeAsyncSession] = []

    def __call__(self) -> FakeAsyncSession:
        session = FakeAsyncSession()
        self.sessions.append(session)
        return session


class DummyAwaitable:
    def __await__(self):
        async def complete() -> str:
            return "ok"

        return complete().__await__()


class TestPostgresHarnessValidation:
    def test_missing_postgres_test_dsn_reports_unconfigured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TEST_" + "DATABASE_" + "URL", raising=False)

        assert is_postgres_test_configured() is False
        with pytest.raises(PostgresTestConfigError, match="test DSN env var is not configured"):
            require_postgres_test_dsn()

    def test_rejects_sqlite_url(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="SQLite URLs are forbidden"):
            validate_test_db_dsn("sqlite:///tmp/test.db")

    def test_rejects_sqlite_aiosqlite_url(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="SQLite URLs are forbidden"):
            validate_test_db_dsn("sqlite+aiosqlite:///tmp/test.db")

    def test_rejects_postgresql_without_asyncpg(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="must use the asyncpg driver"):
            validate_test_db_dsn("postgresql://cid_test_user@localhost:5432/cid_test")

    def test_rejects_suspicious_production_name(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="production-like marker"):
            validate_test_db_dsn(
                "postgresql+asyncpg://cid_test_user@localhost:5432/cid_production"
            )

    def test_rejects_ailinkcinema_database_name(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="explicitly test-safe"):
            validate_test_db_dsn(
                "postgresql+asyncpg://cid_test_user@localhost:5432/ailinkcinema"
            )

    def test_rejects_cinema_database_name(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="explicitly test-safe"):
            validate_test_db_dsn(
                "postgresql+asyncpg://cid_test_user@localhost:5432/cinema"
            )

    def test_accepts_explicit_test_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test"
        )

        assert validated.database_name == "cid_test"
        assert validated.hostname == "localhost"

    def test_accepts_cid_test_ledger_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test_ledger"
        )

        assert validated.database_name == "cid_test_ledger"

    def test_accepts_cid_ci_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid_ci"
        )

        assert validated.database_name == "cid_ci"

    def test_accepts_cid_testing_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid-testing"
        )

        assert validated.database_name == "cid-testing"

    def test_accepts_cid_testing_underscore_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid_testing"
        )

        assert validated.database_name == "cid_testing"

    def test_accepts_local_test_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/local_test"
        )

        assert validated.database_name == "local_test"

    def test_accepts_test_cid_database_name(self) -> None:
        validated = validate_test_db_dsn(
            "postgresql+asyncpg://cid_test_user@localhost:5432/test_cid"
        )

        assert validated.database_name == "test_cid"

    def test_rejects_cidproduction_database_name(self) -> None:
        with pytest.raises(PostgresTestConfigError, match="production-like marker"):
            validate_test_db_dsn(
                "postgresql+asyncpg://cid_test_user@localhost:5432/cidproduction"
            )

    def test_builds_minimum_billing_metadata_without_connecting(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test")
        metadata = build_billing_test_metadata()

        assert set(metadata.tables) == set(MINIMUM_BILLING_TABLES)

    def test_skip_helper_is_explicit_when_unconfigured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TEST_" + "DATABASE_" + "URL", raising=False)

        with pytest.raises(pytest.skip.Exception, match="Real PostgreSQL integration checks are skipped"):
            skip_if_postgres_test_unconfigured()


class TestPostgresConcurrencyTimeoutHelpers:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("statement_timeout_ms", "lock_timeout_ms"),
        [(0, 100), (100, 0), (-1, 100), (100, -1), (True, 100), (100, False)],
    )
    async def test_set_local_postgres_timeouts_validates_positive_ints(
        self,
        statement_timeout_ms: int,
        lock_timeout_ms: int,
    ) -> None:
        with pytest.raises(ValueError, match="must be a positive integer"):
            await set_local_postgres_timeouts(
                FakeAsyncSession(),  # type: ignore[arg-type]
                statement_timeout_ms=statement_timeout_ms,
                lock_timeout_ms=lock_timeout_ms,
            )

    @pytest.mark.asyncio
    async def test_set_local_postgres_timeouts_emits_expected_sql(self) -> None:
        session = FakeAsyncSession()

        await set_local_postgres_timeouts(
            session,  # type: ignore[arg-type]
            statement_timeout_ms=1200,
            lock_timeout_ms=300,
        )

        assert session.executed_sql == [
            "SET LOCAL statement_timeout = '1200ms'",
            "SET LOCAL lock_timeout = '300ms'",
        ]
        assert session.rollbacks == 0
        assert session.closes == 0

    @pytest.mark.asyncio
    async def test_postgres_session_with_timeouts_closes_without_commit(self) -> None:
        factory = FakeSessionFactory()

        async with postgres_session_with_timeouts(
            factory,  # type: ignore[arg-type]
            statement_timeout_ms=1000,
            lock_timeout_ms=250,
        ) as session:
            assert session is factory.sessions[0]

        assert len(factory.sessions) == 1
        assert factory.sessions[0].rollbacks == 0
        assert factory.sessions[0].closes == 1

    @pytest.mark.asyncio
    async def test_postgres_session_with_timeouts_rolls_back_on_error(self) -> None:
        factory = FakeSessionFactory()

        with pytest.raises(RuntimeError, match="boom"):
            async with postgres_session_with_timeouts(
                factory,  # type: ignore[arg-type]
                statement_timeout_ms=1000,
                lock_timeout_ms=250,
            ):
                raise RuntimeError("boom")

        assert factory.sessions[0].rollbacks == 1
        assert factory.sessions[0].closes == 1

    @pytest.mark.asyncio
    async def test_run_with_async_timeout_returns_result(self) -> None:
        async def complete() -> str:
            return "ok"

        assert await run_with_async_timeout(
            complete(),
            timeout_seconds=1,
            label="fast operation",
        ) == "ok"

    @pytest.mark.asyncio
    async def test_run_with_async_timeout_raises_assertion_with_label(self) -> None:
        async def wait_forever() -> None:
            await asyncio.sleep(60)

        with pytest.raises(AssertionError, match="slow operation"):
            await run_with_async_timeout(
                wait_forever(),
                timeout_seconds=0.01,
                label="slow operation",
            )

    @pytest.mark.asyncio
    async def test_run_with_async_timeout_preserves_original_exception(self) -> None:
        async def fail() -> None:
            raise RuntimeError("original")

        with pytest.raises(RuntimeError, match="original"):
            await run_with_async_timeout(
                fail(),
                timeout_seconds=1,
                label="failing operation",
            )

    @pytest.mark.asyncio
    async def test_run_with_async_timeout_validates_arguments(self) -> None:
        with pytest.raises(ValueError, match="timeout_seconds"):
            await run_with_async_timeout(DummyAwaitable(), timeout_seconds=0, label="x")
        with pytest.raises(ValueError, match="label"):
            await run_with_async_timeout(DummyAwaitable(), timeout_seconds=1, label="")

    @pytest.mark.asyncio
    async def test_open_independent_sessions_validates_count(self) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            async with open_independent_sessions(
                FakeSessionFactory(),  # type: ignore[arg-type]
                count=1,
            ):
                pass

    @pytest.mark.asyncio
    async def test_open_independent_sessions_opens_requested_count(self) -> None:
        factory = FakeSessionFactory()

        async with open_independent_sessions(
            factory,  # type: ignore[arg-type]
            count=3,
        ) as sessions:
            assert len(sessions) == 3
            assert len({id(session) for session in sessions}) == 3

        assert len(factory.sessions) == 3
        assert [session.rollbacks for session in factory.sessions] == [1, 1, 1]
        assert [session.closes for session in factory.sessions] == [1, 1, 1]

    @pytest.mark.asyncio
    async def test_open_independent_sessions_cleans_up_after_error(self) -> None:
        factory = FakeSessionFactory()

        with pytest.raises(RuntimeError, match="task failed"):
            async with open_independent_sessions(
                factory,  # type: ignore[arg-type]
                count=2,
            ):
                raise RuntimeError("task failed")

        assert [session.rollbacks for session in factory.sessions] == [1, 1]
        assert [session.closes for session in factory.sessions] == [1, 1]

    @pytest.mark.asyncio
    async def test_cleanup_concurrent_tasks_cancels_pending_tasks(self) -> None:
        cancelled = asyncio.Event()

        async def pending() -> None:
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                cancelled.set()
                raise

        task = asyncio.create_task(pending())
        await asyncio.sleep(0)

        await cleanup_concurrent_tasks([task], timeout_seconds=1)

        assert task.cancelled()
        assert cancelled.is_set()

    @pytest.mark.asyncio
    async def test_cleanup_concurrent_tasks_allows_empty_list(self) -> None:
        await cleanup_concurrent_tasks([], timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_cleanup_concurrent_tasks_does_not_hide_completed_exception(self) -> None:
        async def fail() -> None:
            raise RuntimeError("task error")

        task = asyncio.create_task(fail())
        await asyncio.sleep(0)

        with pytest.raises(RuntimeError, match="task error"):
            await cleanup_concurrent_tasks([task], timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_cleanup_concurrent_tasks_validates_timeout(self) -> None:
        with pytest.raises(ValueError, match="timeout_seconds"):
            await cleanup_concurrent_tasks([], timeout_seconds=0)


@pytest.mark.asyncio
async def test_temporary_postgres_billing_harness_creates_and_drops_schema() -> None:
    skip_if_postgres_test_unconfigured()
    validated = require_validated_test_db_dsn()

    async with temporary_postgres_billing_harness() as harness:
        assert harness.validated_dsn.database_name == validated.database_name
        assert await harness.schema_exists() is True
        assert await harness.table_exists("credit_balances") is True
        assert await harness.table_exists("credit_ledger_entries") is True
