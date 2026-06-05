from __future__ import annotations

import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Sequence
from urllib.parse import urlparse

import pytest
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


TEST_DATABASE_ENV = "TEST_DATABASE_URL"
BLOCKED_DATABASE_MARKERS = ("prod", "production", "live", "real", "main")
MINIMUM_BILLING_TABLES = (
    "credit_balances",
    "credit_ledger_entries",
)
SAFE_TOKEN_SEQUENCES = (
    ("cid", "test"),
    ("cid", "testing"),
    ("test", "cid"),
    ("local", "test"),
    ("cid", "ci"),
)


class PostgresTestHarnessError(RuntimeError):
    """Base error for the PostgreSQL test harness."""


class PostgresTestConfigError(PostgresTestHarnessError):
    """Raised when TEST_DATABASE_URL is missing or unsafe."""


@dataclass(frozen=True)
class ValidatedPostgresTestUrl:
    raw_url: str
    database_name: str
    hostname: str | None


@dataclass
class PostgresTestHarness:
    validated_url: ValidatedPostgresTestUrl
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


def get_test_database_url() -> str | None:
    return os.getenv(TEST_DATABASE_ENV)


def is_postgres_test_configured() -> bool:
    raw_url = get_test_database_url()
    return bool(raw_url and raw_url.strip())


def require_postgres_test_configuration() -> str:
    raw_url = get_test_database_url()
    if raw_url is None or not raw_url.strip():
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL is not configured. "
            "Set it to a dedicated PostgreSQL test database such as "
            "postgresql+asyncpg://user:password@localhost:5432/cid_test. "
            "There is no SQLite fallback."
        )
    return raw_url.strip()


def skip_if_postgres_test_unconfigured() -> None:
    if not is_postgres_test_configured():
        pytest.skip(
            "TEST_DATABASE_URL is not configured for PostgreSQL test harness. "
            "Real PostgreSQL integration checks are skipped. There is no SQLite fallback."
        )


def _tokenize_database_name(database_name: str) -> tuple[str, ...]:
    return tuple(token for token in re.split(r"[._-]+", database_name.lower()) if token)


def _has_safe_token_sequence(tokens: Sequence[str]) -> bool:
    for safe_sequence in SAFE_TOKEN_SEQUENCES:
        sequence_len = len(safe_sequence)
        for index in range(len(tokens) - sequence_len + 1):
            if tuple(tokens[index : index + sequence_len]) == safe_sequence:
                return True
    return False


def validate_test_database_url(raw_url: str) -> ValidatedPostgresTestUrl:
    normalized = raw_url.strip()
    if not normalized:
        raise PostgresTestConfigError("TEST_DATABASE_URL must not be empty")
    if normalized.startswith("sqlite://") or normalized.startswith("sqlite+aiosqlite://"):
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL must point to PostgreSQL via postgresql+asyncpg://. "
            "SQLite URLs are forbidden."
        )
    if normalized.endswith((".db", ".sqlite", ".sqlite3")):
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL must not point to a file-based database artifact."
        )
    if not normalized.startswith("postgresql+asyncpg://"):
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL must use the asyncpg driver: postgresql+asyncpg://..."
        )

    parsed = urlparse(normalized)
    database_name = parsed.path.lstrip("/").strip()
    if not database_name:
        raise PostgresTestConfigError("TEST_DATABASE_URL must include a database name")
    if any(database_name.endswith(suffix) for suffix in (".db", ".sqlite", ".sqlite3")):
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL must not reference .db/.sqlite/.sqlite3 database names"
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
            "TEST_DATABASE_URL looks unsafe for tests because it contains a "
            "production-like marker (prod/production/live/real/main)."
        )
    database_tokens = _tokenize_database_name(database_name)
    if not _has_safe_token_sequence(database_tokens):
        raise PostgresTestConfigError(
            "TEST_DATABASE_URL must target an explicitly test-safe database name "
            "using clear test tokens such as cid_test, cid-testing, local_test, "
            "test_cid, or cid_ci."
        )

    return ValidatedPostgresTestUrl(
        raw_url=normalized,
        database_name=database_name,
        hostname=parsed.hostname,
    )


def require_validated_test_database_url() -> ValidatedPostgresTestUrl:
    return validate_test_database_url(require_postgres_test_configuration())


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


@asynccontextmanager
async def temporary_postgres_billing_harness(
    table_names: Sequence[str] | None = None,
) -> AsyncIterator[PostgresTestHarness]:
    """Provision a temporary PostgreSQL schema for billing tests.

    TEST_DATABASE_URL must point to a dedicated PostgreSQL test database such as
    postgresql+asyncpg://user:password@localhost:5432/cid_test.
    It must never target development, staging, production, or any real database.
    There is no SQLite fallback in this helper.
    """

    validated = require_validated_test_database_url()
    schema_name = generate_temporary_schema_name()
    engine = create_async_engine(
        validated.raw_url,
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
        validated_url=validated,
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
