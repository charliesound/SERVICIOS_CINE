from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.postgres_advisory_lock_manager import (
    DANGEROUS_ORG_IDS,
    PostgresAdvisoryLockManager,
    PostgresAdvisoryLockRequest,
    PostgresAdvisoryLockResult,
    _derive_lock_key,
)

LOCK_NAME = "scheduler:cancelled-credit-release"
ORG_A = "org-a"
ORG_B = "org-b"


@pytest.fixture
def manager() -> PostgresAdvisoryLockManager:
    return PostgresAdvisoryLockManager()


@pytest.fixture
def mock_session() -> MagicMock:
    s = MagicMock()
    s.execute = AsyncMock()
    return s


class TestAKeyDerivation:
    def test_same_request_same_lock_key(self) -> None:
        key1 = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        key2 = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        assert key1 == key2

    def test_different_org_generates_different_key(self) -> None:
        key_a = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        key_b = _derive_lock_key(LOCK_NAME, "tenant", ORG_B)
        assert key_a != key_b

    def test_different_scope_generates_different_key(self) -> None:
        tenant_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        global_key = _derive_lock_key(LOCK_NAME, "global", None)
        assert tenant_key != global_key

    def test_lock_key_is_int(self) -> None:
        key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        assert isinstance(key, int)

    def test_lock_key_is_stable_across_calls(self) -> None:
        keys = [_derive_lock_key(LOCK_NAME, "tenant", ORG_A) for _ in range(10)]
        assert all(k == keys[0] for k in keys)

    def test_lock_key_is_signed_64bit(self) -> None:
        key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        assert -(2**63) <= key <= (2**63 - 1)


class TestBRequestValidation:
    @pytest.mark.parametrize("bad_name", ["", "   "])
    async def test_empty_lock_name_rejected(
        self, manager: PostgresAdvisoryLockManager, bad_name: str
    ) -> None:
        with pytest.raises(ValueError, match="lock_name must be non-empty"):
            await manager.try_acquire(
                MagicMock(),
                PostgresAdvisoryLockRequest(lock_name=bad_name),
            )

    @pytest.mark.parametrize("bad_scope", ["", "tenantt", "GLOBAL", "Tenant"])
    async def test_invalid_scope_rejected(
        self, manager: PostgresAdvisoryLockManager, bad_scope: str
    ) -> None:
        with pytest.raises(ValueError, match="Invalid scope"):
            await manager.try_acquire(
                MagicMock(),
                PostgresAdvisoryLockRequest(
                    lock_name=LOCK_NAME, scope=bad_scope
                ),
            )

    @pytest.mark.parametrize("missing_org", [None, "", "   "])
    async def test_tenant_scope_requires_organization_id(
        self, manager: PostgresAdvisoryLockManager, missing_org: Any
    ) -> None:
        with pytest.raises(ValueError, match="organization_id is required"):
            await manager.try_acquire(
                MagicMock(),
                PostgresAdvisoryLockRequest(
                    lock_name=LOCK_NAME,
                    scope="tenant",
                    organization_id=missing_org,
                ),
            )

    @pytest.mark.parametrize("bad_org", sorted(DANGEROUS_ORG_IDS))
    async def test_dangerous_org_ids_rejected(
        self, manager: PostgresAdvisoryLockManager, bad_org: str
    ) -> None:
        with pytest.raises(ValueError, match="Rejected dangerous organization_id"):
            await manager.try_acquire(
                MagicMock(),
                PostgresAdvisoryLockRequest(
                    lock_name=LOCK_NAME,
                    scope="tenant",
                    organization_id=bad_org,
                ),
            )

    async def test_global_scope_with_organization_id_rejected(
        self, manager: PostgresAdvisoryLockManager
    ) -> None:
        with pytest.raises(
            ValueError, match="organization_id must not be provided for global scope"
        ):
            await manager.try_acquire(
                MagicMock(),
                PostgresAdvisoryLockRequest(
                    lock_name=LOCK_NAME,
                    scope="global",
                    organization_id=ORG_A,
                ),
            )

    async def test_global_scope_without_organization_id_ok(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        result = await manager.try_acquire(
            mock_session,
            PostgresAdvisoryLockRequest(
                lock_name=LOCK_NAME, scope="global", organization_id=None
            ),
        )
        assert result.scope == "global"
        assert result.acquired is True


class TestCTryAcquire:
    async def test_calls_session_execute_with_pg_try_advisory_lock(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        await manager.try_acquire(mock_session, request)
        call_sql = mock_session.execute.call_args[0][0].text
        assert "pg_try_advisory_lock" in call_sql

    async def test_passes_lock_key_as_parameter(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        expected_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        await manager.try_acquire(mock_session, request)
        call_params = mock_session.execute.call_args[0][1]
        assert call_params["lock_key"] == expected_key

    async def test_acquired_true_when_scalar_true(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        result = await manager.try_acquire(mock_session, request)
        assert result.acquired is True

    async def test_acquired_false_when_scalar_false(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = False
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        result = await manager.try_acquire(mock_session, request)
        assert result.acquired is False

    async def test_does_not_call_commit(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        await manager.try_acquire(mock_session, request)
        mock_session.commit.assert_not_called()

    async def test_does_not_call_rollback(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        await manager.try_acquire(mock_session, request)
        mock_session.rollback.assert_not_called()

    async def test_does_not_close_session(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        await manager.try_acquire(mock_session, request)
        mock_session.close.assert_not_called()

    async def test_result_contains_expected_fields(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        request = PostgresAdvisoryLockRequest(
            lock_name=LOCK_NAME, scope="tenant", organization_id=ORG_A
        )
        result = await manager.try_acquire(mock_session, request)
        assert isinstance(result, PostgresAdvisoryLockResult)
        assert result.lock_name == LOCK_NAME
        assert result.scope == "tenant"
        assert isinstance(result.lock_key, int)


class TestDRelease:
    async def test_calls_session_execute_with_pg_advisory_unlock(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        await manager.release(mock_session, lock_key)
        call_sql = mock_session.execute.call_args[0][0].text
        assert "pg_advisory_unlock" in call_sql

    async def test_passes_lock_key_as_parameter(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        await manager.release(mock_session, lock_key)
        call_params = mock_session.execute.call_args[0][1]
        assert call_params["lock_key"] == lock_key

    async def test_returns_true_when_scalar_true(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        result = await manager.release(mock_session, lock_key)
        assert result is True

    async def test_returns_false_when_scalar_false(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = False
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        result = await manager.release(mock_session, lock_key)
        assert result is False

    async def test_does_not_call_commit(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        await manager.release(mock_session, lock_key)
        mock_session.commit.assert_not_called()

    async def test_does_not_call_rollback(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        await manager.release(mock_session, lock_key)
        mock_session.rollback.assert_not_called()

    async def test_does_not_close_session(
        self, manager: PostgresAdvisoryLockManager, mock_session: MagicMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar.return_value = True
        mock_session.execute.return_value = mock_result
        lock_key = _derive_lock_key(LOCK_NAME, "tenant", ORG_A)
        await manager.release(mock_session, lock_key)
        mock_session.close.assert_not_called()


class TestENoSecretsBoundary:
    SERVICE_PATH = "src/services/postgres_advisory_lock_manager.py"

    @pytest.fixture(scope="class")
    def source(self) -> str:
        with open(self.SERVICE_PATH) as f:
            return f.read()

    def test_no_database_url(self, source: str) -> None:
        assert "DATABASE_URL" not in source

    def test_no_async_session_local(self, source: str) -> None:
        assert "AsyncSessionLocal" not in source

    def test_no_create_async_engine(self, source: str) -> None:
        assert "create_async_engine" not in source

    def test_no_fastapi_or_router(self, source: str) -> None:
        assert "FastAPI" not in source and "APIRouter" not in source

    def test_no_at_router(self, source: str) -> None:
        assert "@router" not in source

    def test_no_background_tasks(self, source: str) -> None:
        assert "BackgroundTasks" not in source

    def test_no_startup(self, source: str) -> None:
        assert "startup" not in source

    def test_no_on_event(self, source: str) -> None:
        assert "on_event" not in source

    def test_no_lifespan(self, source: str) -> None:
        assert "lifespan" not in source

    def test_no_cron(self, source: str) -> None:
        assert "cron" not in source

    def test_no_schedule(self, source: str) -> None:
        assert "schedule" not in source

    def test_no_scripts(self, source: str) -> None:
        assert "scripts" not in source

    def test_no_routes(self, source: str) -> None:
        assert "routes" not in source

    def test_no_credit_ledger_service(self, source: str) -> None:
        assert "CreditLedgerService" not in source

    def test_no_release_cancelled_credits(self, source: str) -> None:
        assert "release_cancelled_ai_job_reserved_credits(" not in source

    def test_no_process_cancelled_releases(self, source: str) -> None:
        assert "process_cancelled_ai_job_credit_releases(" not in source

    def test_contains_pg_try_advisory_lock(self, source: str) -> None:
        assert "pg_try_advisory_lock" in source

    def test_contains_pg_advisory_unlock(self, source: str) -> None:
        assert "pg_advisory_unlock" in source
