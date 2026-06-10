from __future__ import annotations

import asyncio
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Iterable, Sequence, TypeVar
from urllib.parse import urlparse

import pytest
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


TEST_DATABASE_ENV = "TEST_" + "DATABASE_" + "URL"
T = TypeVar("T")
BLOCKED_DATABASE_MARKERS = ("prod", "production", "live", "real", "main")
MINIMUM_BILLING_TABLES = (
    "credit_balances",
    "credit_ledger_entries",
)
SAFE_DB_NAME_SEQUENCES = (
    ("cid", "test"),
    ("cid", "testing"),
    ("test", "cid"),
    ("local", "test"),
    ("cid", "ci"),
)


class PostgresTestHarnessError(RuntimeError):
    """Base error for the PostgreSQL test harness."""


class PostgresTestConfigError(PostgresTestHarnessError):
    """Raised when the PostgreSQL test DSN env var is missing or unsafe."""


@dataclass(frozen=True)
class ValidatedPostgresTestDsn:
    raw_dsn: str
    database_name: str
    hostname: str | None


@dataclass
class PostgresTestHarness:
    validated_dsn: ValidatedPostgresTestDsn
    schema_name: str
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    async def schema_exists(self) -> bool:
        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.schemata "
                    "WHERE schema_name = :schema_name)"
                ),
                {"schema_name": self.schema_name},
            )
            return bool(result.scalar_one())

    async def table_exists(self, table_name: str) -> bool:
        async with self.engine.connect() as connection:
            result = await connection.execute(
                text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = :schema_name "
                    "AND table_name = :table_name)"
                ),
                {"schema_name": self.schema_name, "table_name": table_name},
            )
            return bool(result.scalar_one())


def get_test_db_dsn() -> str | None:
    return os.getenv(TEST_DATABASE_ENV)


def is_postgres_test_configured() -> bool:
    raw_dsn = get_test_db_dsn()
    return bool(raw_dsn and raw_dsn.strip())


def require_postgres_test_dsn() -> str:
    raw_dsn = get_test_db_dsn()
    if raw_dsn is None or not raw_dsn.strip():
        raise PostgresTestConfigError(
            "PostgreSQL test DSN env var is not configured. "
            "Set it to a dedicated PostgreSQL test database such as "
            "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test. "
            "There is no SQLite fallback."
        )
    return raw_dsn.strip()


def skip_if_postgres_test_unconfigured() -> None:
    if not is_postgres_test_configured():
        pytest.skip(
            "PostgreSQL test DSN env var is not configured for the test harness. "
            "Real PostgreSQL integration checks are skipped. There is no SQLite fallback."
        )


def _tokenize_database_name(database_name: str) -> tuple[str, ...]:
    return tuple(token for token in re.split(r"[._-]+", database_name.lower()) if token)


def _has_safe_name_sequence(name_parts: Sequence[str]) -> bool:
    for safe_sequence in SAFE_DB_NAME_SEQUENCES:
        sequence_len = len(safe_sequence)
        for index in range(len(name_parts) - sequence_len + 1):
            if tuple(name_parts[index : index + sequence_len]) == safe_sequence:
                return True
    return False


def validate_test_db_dsn(raw_dsn: str) -> ValidatedPostgresTestDsn:
    normalized = raw_dsn.strip()
    if not normalized:
        raise PostgresTestConfigError("PostgreSQL test DSN env var must not be empty")
    if normalized.startswith("sqlite://") or normalized.startswith("sqlite+aiosqlite://"):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN must point to postgresql+asyncpg://. "
            "SQLite URLs are forbidden."
        )
    if normalized.endswith((".db", ".sqlite", ".sqlite3")):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN must not point to a file-based database artifact."
        )
    if not normalized.startswith("postgresql+asyncpg://"):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN must use the asyncpg driver: postgresql+asyncpg://..."
        )

    parsed = urlparse(normalized)
    database_name = parsed.path.lstrip("/").strip()
    if not database_name:
        raise PostgresTestConfigError("PostgreSQL test DSN must include a database name")
    if any(database_name.endswith(suffix) for suffix in (".db", ".sqlite", ".sqlite3")):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN must not reference .db/.sqlite/.sqlite3 database names"
        )

    inspection_text = " ".join(
        part
        for part in (
            parsed.hostname or "",
            database_name,
        )
    ).lower()
    if any(marker in inspection_text for marker in BLOCKED_DATABASE_MARKERS):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN looks unsafe because it contains a "
            "production-like marker (prod/production/live/real/main)."
        )
    database_tokens = _tokenize_database_name(database_name)
    if not _has_safe_name_sequence(database_tokens):
        raise PostgresTestConfigError(
            "PostgreSQL test DSN must target an explicitly test-safe database name "
            "using clear test markers such as cid_test, cid-testing, local_test, "
            "test_cid, or cid_ci."
        )

    return ValidatedPostgresTestDsn(
        raw_dsn=normalized,
        database_name=database_name,
        hostname=parsed.hostname,
    )


def require_validated_test_db_dsn() -> ValidatedPostgresTestDsn:
    return validate_test_db_dsn(require_postgres_test_dsn())


def build_billing_test_metadata(table_names: Sequence[str] | None = None) -> MetaData:
    from database import Base
    import models.billing  # noqa: F401

    requested_tables = tuple(table_names or MINIMUM_BILLING_TABLES)
    metadata = MetaData()
    for table_name in requested_tables:
        source_table = Base.metadata.tables.get(table_name)
        if source_table is None:
            raise PostgresTestHarnessError(
                f"Table {table_name!r} is not registered in Base.metadata"
            )
        source_table.to_metadata(metadata)
    return metadata


def generate_temporary_schema_name() -> str:
    return f"cid_test_{uuid.uuid4().hex}"


def _require_positive_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _require_positive_timeout_seconds(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return float(value)


async def set_local_postgres_timeouts(
    session: AsyncSession,
    *,
    statement_timeout_ms: int,
    lock_timeout_ms: int,
) -> None:
    statement_timeout_ms = _require_positive_int(
        statement_timeout_ms,
        "statement_timeout_ms",
    )
    lock_timeout_ms = _require_positive_int(lock_timeout_ms, "lock_timeout_ms")
    await session.execute(
        text("SET LOCAL statement_timeout = '{0}ms'".format(statement_timeout_ms))
    )
    await session.execute(text("SET LOCAL lock_timeout = '{0}ms'".format(lock_timeout_ms)))


@asynccontextmanager
async def postgres_session_with_timeouts(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    statement_timeout_ms: int,
    lock_timeout_ms: int,
) -> AsyncIterator[AsyncSession]:
    session = session_factory()
    try:
        await set_local_postgres_timeouts(
            session,
            statement_timeout_ms=statement_timeout_ms,
            lock_timeout_ms=lock_timeout_ms,
        )
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def run_with_async_timeout(
    awaitable: Awaitable[T],
    *,
    timeout_seconds: float,
    label: str,
) -> T:
    timeout_seconds = _require_positive_timeout_seconds(
        timeout_seconds,
        "timeout_seconds",
    )
    if not isinstance(label, str) or not label.strip():
        raise ValueError("label must be a non-empty string")
    try:
        return await asyncio.wait_for(awaitable, timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        raise AssertionError(
            "Timed out while waiting for {0} after {1:g}s".format(
                label,
                timeout_seconds,
            )
        ) from exc


@asynccontextmanager
async def open_independent_sessions(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    count: int = 2,
) -> AsyncIterator[tuple[AsyncSession, ...]]:
    count = _require_positive_int(count, "count")
    if count < 2:
        raise ValueError("count must be at least 2")
    sessions = tuple(session_factory() for _ in range(count))
    try:
        yield sessions
    finally:
        for session in sessions:
            try:
                await session.rollback()
            finally:
                await session.close()


async def cleanup_concurrent_tasks(
    tasks: Iterable[asyncio.Task[Any]],
    *,
    timeout_seconds: float,
) -> None:
    timeout_seconds = _require_positive_timeout_seconds(
        timeout_seconds,
        "timeout_seconds",
    )
    task_list = list(tasks)
    for task in task_list:
        if task.done() and not task.cancelled():
            task.result()

    pending = [task for task in task_list if not task.done()]
    if not pending:
        return
    for task in pending:
        task.cancel()
    results = await asyncio.wait_for(
        asyncio.gather(*pending, return_exceptions=True),
        timeout=timeout_seconds,
    )
    for result in results:
        if isinstance(result, asyncio.CancelledError):
            continue
        if isinstance(result, BaseException):
            raise result


@asynccontextmanager
async def temporary_postgres_billing_harness(
    table_names: Sequence[str] | None = None,
) -> AsyncIterator[PostgresTestHarness]:
    """Provision a temporary PostgreSQL schema for billing tests.

    The PostgreSQL test DSN env var must point to a dedicated test database such as
    postgresql+asyncpg://cid_test_user@localhost:5432/cid_test.
    It must never target development, staging, production, or any real database.
    There is no SQLite fallback in this helper.
    """

    validated = require_validated_test_db_dsn()
    schema_name = generate_temporary_schema_name()
    engine = create_async_engine(
        validated.raw_dsn,
        poolclass=NullPool,
        future=True,
        pool_pre_ping=True,
        connect_args={"server_settings": {"search_path": f"{schema_name},public"}},
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    harness = PostgresTestHarness(
        validated_dsn=validated,
        schema_name=schema_name,
        engine=engine,
        session_factory=session_factory,
    )

    try:
        async with engine.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))
            metadata = build_billing_test_metadata(table_names)
            await connection.run_sync(metadata.create_all)
        yield harness
    finally:
        try:
            async with engine.begin() as connection:
                await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
        finally:
            await engine.dispose()
