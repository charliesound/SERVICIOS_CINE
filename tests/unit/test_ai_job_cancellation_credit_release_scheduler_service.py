from __future__ import annotations

import contextlib
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from services.ai_job_cancellation_credit_release_scheduler_service import (
    AIJobCancellationCreditReleaseSchedulerService,
    AIJobCancellationCreditReleaseSchedulerTenantConfig,
    AIJobCancellationCreditReleaseSchedulerTickRequest,
    DANGEROUS_ORG_IDS,
    MAX_ITEMS_CAP,
    MAX_ITEMS_DEFAULT,
    REQUESTED_BY_DEFAULT,
)


@pytest.fixture
def mock_session() -> MagicMock:
    s = MagicMock()
    s.commit = AsyncMock()
    return s


@pytest.fixture
def mock_session_provider(mock_session: MagicMock) -> Any:
    @contextlib.asynccontextmanager
    async def _provider() -> Any:
        yield mock_session

    return _provider


@pytest.fixture
def mock_orchestration_service() -> MagicMock:
    svc = MagicMock()
    svc.process_cancelled_ai_job_credit_releases = AsyncMock()
    return svc


@pytest.fixture
def scheduler_service(
    mock_orchestration_service: MagicMock,
    mock_session_provider: AsyncIterator[MagicMock],
) -> AIJobCancellationCreditReleaseSchedulerService:
    return AIJobCancellationCreditReleaseSchedulerService(
        orchestration_service=mock_orchestration_service,
        session_provider=mock_session_provider,
    )


def _make_result(
    scanned: int = 10,
    processed: int = 8,
    released: int = 6,
    skipped: int = 2,
    failed: int = 0,
    **kwargs: Any,
) -> MagicMock:
    m = MagicMock()
    m.scanned_count = scanned
    m.processed_count = processed
    m.released_count = released
    m.skipped_count = skipped
    m.failed_count = failed
    for k, v in kwargs.items():
        setattr(m, k, v)
    type(m).scanned_count = PropertyMock(return_value=scanned)
    return m


class TestAKillSwitch:
    async def test_enabled_false_does_not_call_orchestration(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            enabled=False,
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(
                    organization_id="org-1",
                ),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.enabled is False
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.assert_not_called()

    async def test_disabled_result_indicates_disabled(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(enabled=False)
        result = await scheduler_service.run_tick(request)
        assert result.enabled is False
        assert result.processed_tenant_count == 0
        assert result.tenant_count == 0


class TestBTenantIteration:
    async def test_two_tenants_both_called(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-a"),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-b"),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.processed_tenant_count == 2
        assert scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_count == 2

    async def test_correct_organization_id_passed_per_call(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-alpha"),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-beta"),
            ),
        )
        await scheduler_service.run_tick(request)
        calls = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list
        assert len(calls) == 2
        for i, expected_org in enumerate(["org-alpha", "org-beta"]):
            args, _ = calls[i]
            req_obj = args[1]
            assert req_obj.organization_id == expected_org
        assert req_obj.organization_id == "org-beta"

    async def test_no_tenants_returns_empty(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest()
        result = await scheduler_service.run_tick(request)
        assert result.tenant_count == 0
        assert result.processed_tenant_count == 0
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.assert_not_called()


class TestCMaxItems:
    async def test_default_max_items(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.max_items == MAX_ITEMS_DEFAULT

    async def test_max_items_per_tenant_respected(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1", max_items=77),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.max_items == 77

    async def test_max_items_capped_at_100(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1", max_items=999),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.max_items == MAX_ITEMS_CAP

    async def test_max_items_zero_raises(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1", max_items=0),
            ),
        )
        with pytest.raises(ValueError, match="max_items must be >= 1"):
            await scheduler_service.run_tick(request)


class TestDDryRunRequestedBy:
    async def test_dry_run_propagated(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            dry_run=True,
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.dry_run is True

    async def test_requested_by_default(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.requested_by == REQUESTED_BY_DEFAULT

    async def test_requested_by_custom(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            requested_by="ops-manual-test",
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        await scheduler_service.run_tick(request)
        call = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_args_list[0]
        req_obj = call[0][1]
        assert req_obj.requested_by == "ops-manual-test"


class TestETenantsDisabled:
    async def test_disabled_tenant_skipped_no_call(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1", enabled=False),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.skipped_tenant_count == 1
        assert result.processed_tenant_count == 0
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.assert_not_called()

    async def test_disabled_and_enabled_tenants(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-a", enabled=False),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-b", enabled=True),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.skipped_tenant_count == 1
        assert result.processed_tenant_count == 1
        assert scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.call_count == 1

    async def test_disabled_tenant_marked_in_per_tenant(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.return_value = _make_result()
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1", enabled=False),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert len(result.per_tenant_results) == 1
        assert result.per_tenant_results[0].status == "disabled"
        assert result.per_tenant_results[0].organization_id == "org-1"


class TestFAllTenantsPeligroso:
    @pytest.mark.parametrize("bad_id", sorted(DANGEROUS_ORG_IDS))
    async def test_dangerous_org_ids_rejected(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService, bad_id: str
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id=bad_id),
            ),
        )
        with pytest.raises(ValueError, match="Rejected dangerous organization_id"):
            await scheduler_service.run_tick(request)

    @pytest.mark.parametrize("bad_id", ["", "   ", "ALL", "All-Tenants", "GLOBAL"])
    async def test_empty_and_case_insensitive_dangerous_org_ids_rejected(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService, bad_id: str
    ) -> None:
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id=bad_id),
            ),
        )
        with pytest.raises(ValueError):
            await scheduler_service.run_tick(request)

    async def test_no_all_tenants_flag(
        self,
    ) -> None:
        assert not hasattr(AIJobCancellationCreditReleaseSchedulerTickRequest, "all_tenants")


class TestGFailurePorTenant:
    async def test_exception_does_not_tumb_all_tenants(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        mock = scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases
        mock.side_effect = [
            _make_result(),
            Exception("tenant-b-exploded"),
            _make_result(),
        ]
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-a"),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-b"),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-c"),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.processed_tenant_count == 2
        assert result.failed_tenant_count == 1

    async def test_failed_tenant_has_error_message(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.side_effect = Exception(
            "db timeout"
        )
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert len(result.per_tenant_results) == 1
        tenant_result = result.per_tenant_results[0]
        assert tenant_result.status == "failed"
        assert tenant_result.error_message is not None

    async def test_error_message_no_secrets(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.side_effect = Exception(
            "DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cid_test"
        )
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-1"),
            ),
        )
        result = await scheduler_service.run_tick(request)
        err = result.per_tenant_results[0].error_message or ""
        assert "postgresql" not in err.lower()
        assert "asyncpg" not in err.lower()
        assert "DATABASE_URL" not in err
        assert "password" not in err.lower()
        assert "localhost" not in err.lower()

    async def test_counters_aggregated_correctly(
        self, scheduler_service: AIJobCancellationCreditReleaseSchedulerService
    ) -> None:
        scheduler_service._orchestration_service.process_cancelled_ai_job_credit_releases.side_effect = [
            _make_result(scanned=10, processed=8, released=6, skipped=2, failed=0),
            _make_result(scanned=5, processed=4, released=3, skipped=1, failed=1),
        ]
        request = AIJobCancellationCreditReleaseSchedulerTickRequest(
            tenants=(
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-a"),
                AIJobCancellationCreditReleaseSchedulerTenantConfig(organization_id="org-b"),
            ),
        )
        result = await scheduler_service.run_tick(request)
        assert result.total_scanned_count == 15
        assert result.total_processed_count == 12
        assert result.total_released_count == 9
        assert result.total_skipped_count == 3
        assert result.total_failed_count == 1


class TestHBoundarySeguridadCodigo:

    SERVICE_PATH = "src/services/ai_job_cancellation_credit_release_scheduler_service.py"

    @pytest.fixture(scope="class")
    def source(self) -> str:
        with open(self.SERVICE_PATH) as f:
            return f.read()

    def test_no_credit_ledger_service(self, source: str) -> None:
        assert "CreditLedgerService" not in source

    def test_no_direct_release_call(self, source: str) -> None:
        assert "release_cancelled_ai_job_reserved_credits(" not in source

    def test_contains_process_cancelled_ai_job_credit_releases(self, source: str) -> None:
        assert "process_cancelled_ai_job_credit_releases" in source

    def test_no_route_imports(self, source: str) -> None:
        assert "src.routes" not in source and "routes." not in source

    def test_no_database_url(self, source: str) -> None:
        assert "DATABASE_URL" not in source

    def test_no_async_session_local(self, source: str) -> None:
        assert "AsyncSessionLocal" not in source

    def test_no_create_async_engine(self, source: str) -> None:
        assert "create_async_engine" not in source

    def test_no_fastapi_or_router(self, source: str) -> None:
        assert "FastAPI" not in source and "APIRouter" not in source and "@router" not in source

    def test_no_scheduler_activation_keywords(self, source: str) -> None:
        lower = source.lower()
        assert "import schedule" not in lower
        assert "from schedule" not in lower
        assert "cron(" not in lower
        assert "cron " not in lower
        assert "backgroundtasks" not in lower
        assert "@repeat" not in lower


class TestINoRuntimeActivation:
    def test_no_app_import(self) -> None:
        import sys

        assert "app" not in sys.modules or "main" not in sys.modules
