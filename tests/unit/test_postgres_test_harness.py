from __future__ import annotations

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
    is_postgres_test_configured,
    require_postgres_test_dsn,
    require_validated_test_db_dsn,
    skip_if_postgres_test_unconfigured,
    temporary_postgres_billing_harness,
    validate_test_db_dsn,
)


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

    def test_builds_minimum_billing_metadata_without_connecting(self) -> None:
        metadata = build_billing_test_metadata()

        assert set(metadata.tables) == set(MINIMUM_BILLING_TABLES)

    def test_skip_helper_is_explicit_when_unconfigured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TEST_" + "DATABASE_" + "URL", raising=False)

        with pytest.raises(pytest.skip.Exception, match="There is no SQLite fallback"):
            skip_if_postgres_test_unconfigured()


@pytest.mark.asyncio
async def test_temporary_postgres_billing_harness_creates_and_drops_schema() -> None:
    skip_if_postgres_test_unconfigured()
    validated = require_validated_test_db_dsn()

    async with temporary_postgres_billing_harness() as harness:
        assert harness.validated_dsn.database_name == validated.database_name
        assert await harness.schema_exists() is True
        assert await harness.table_exists("credit_balances") is True
        assert await harness.table_exists("credit_ledger_entries") is True
