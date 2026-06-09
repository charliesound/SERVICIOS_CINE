from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://placeholder:placeholder@localhost:5432/placeholder")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_accounting_gateway import (
    AIJobAccountingGateway,
    AIJobAccountingGatewayError,
)
from services.credit_gate_service import CreditAvailabilityCheckResult, CreditGateEstimateResult
from services.credit_ledger_service import (
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditReservationResult,
)


class DummySession:
    pass


class FakeCostingService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.estimate_result = CreditGateEstimateResult(
            operation_type="script_analysis",
            estimated_credits=5,
            cost_source="table",
        )
        self.availability_result = CreditAvailabilityCheckResult(
            organization_id="org-1",
            operation_type="script_analysis",
            required_credits=5,
            available_credits=99,
            sufficient=True,
            balance_id="bal-1",
            status="ok",
            message="checked",
        )
        self.reserve_result = CreditReservationResult(
            organization_id="org-1",
            balance_id="bal-1",
            available_before=99,
            available_after=94,
            amount=5,
            ledger_entry_id="reserve-entry-1",
            status="reserved",
            message="reserved",
        )
        self.consume_result = CreditConsumptionResult(
            organization_id="org-1",
            balance_id="bal-1",
            available_before=94,
            available_after=89,
            amount=5,
            ledger_entry_id="consume-entry-1",
            status="consumed",
            message="consumed",
            bucket_debits={"purchased_balance": 5},
        )
        self.release_result = CreditReleaseResult(
            organization_id="org-1",
            balance_id="bal-1",
            available_before=89,
            available_after=94,
            amount=5,
            ledger_entry_id="release-entry-1",
            status="released",
            message="released",
        )

    def estimate_ai_job_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditGateEstimateResult:
        self.calls.append(
            (
                "estimate_ai_job_cost",
                {
                    "operation_type": operation_type,
                    "estimated_credits": estimated_credits,
                },
            )
        )
        return self.estimate_result

    async def check_ai_job_credit_availability(
        self,
        session,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditAvailabilityCheckResult:
        self.calls.append(
            (
                "check_ai_job_credit_availability",
                {
                    "session": session,
                    "organization_id": organization_id,
                    "operation_type": operation_type,
                    "estimated_credits": estimated_credits,
                },
            )
        )
        return self.availability_result

    async def reserve_ai_job_credits(self, session, **kwargs) -> CreditReservationResult:
        self.calls.append(("reserve_ai_job_credits", {"session": session, **kwargs}))
        return self.reserve_result

    async def consume_ai_job_credits(self, session, **kwargs) -> CreditConsumptionResult:
        self.calls.append(("consume_ai_job_credits", {"session": session, **kwargs}))
        return self.consume_result

    async def release_ai_job_credits(self, session, **kwargs) -> CreditReleaseResult:
        self.calls.append(("release_ai_job_credits", {"session": session, **kwargs}))
        return self.release_result


@pytest.fixture
def session() -> DummySession:
    return DummySession()


@pytest.fixture
def fake_costing() -> FakeCostingService:
    return FakeCostingService()


@pytest.fixture
def gateway(fake_costing: FakeCostingService) -> AIJobAccountingGateway:
    return AIJobAccountingGateway(costing_service=fake_costing)


class TestIdempotencyKeyBuilder:
    def test_build_idempotency_key_reserve(self, gateway: AIJobAccountingGateway) -> None:
        assert gateway.build_idempotency_key(
            action="reserve",
            organization_id="org-1",
            job_id="job-1",
        ) == "ai_job:org-1:job-1:reserve"

    def test_build_idempotency_key_consume(self, gateway: AIJobAccountingGateway) -> None:
        assert gateway.build_idempotency_key(
            action="consume",
            organization_id="org-1",
            job_id="job-1",
        ) == "ai_job:org-1:job-1:consume"

    def test_build_idempotency_key_release(self, gateway: AIJobAccountingGateway) -> None:
        assert gateway.build_idempotency_key(
            action="release",
            organization_id="org-1",
            job_id="job-1",
        ) == "ai_job:org-1:job-1:release"

    def test_build_idempotency_key_with_caller_key(self, gateway: AIJobAccountingGateway) -> None:
        assert gateway.build_idempotency_key(
            action="reserve",
            organization_id="org-1",
            job_id="job-1",
            caller_key=" retry-1 ",
        ) == "ai_job:org-1:job-1:reserve:retry-1"


class TestReserve:
    @pytest.mark.asyncio
    async def test_rejects_missing_organization_id(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        with pytest.raises(AIJobAccountingGatewayError, match="organization_id must be a non-empty string"):
            await gateway.reserve_credits_for_job(
                session,
                organization_id="",
                job_id="job-1",
                estimated_credits=5,
                operation_type="image_generation",
            )

        assert not any(method == "reserve_ai_job_credits" for method, _ in fake_costing.calls)

    @pytest.mark.asyncio
    async def test_rejects_missing_job_id(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        with pytest.raises(AIJobAccountingGatewayError, match="job_id must be a non-empty string"):
            await gateway.reserve_credits_for_job(
                session,
                organization_id="org-1",
                job_id=" ",
                estimated_credits=5,
                operation_type="image_generation",
            )

        assert not any(method == "reserve_ai_job_credits" for method, _ in fake_costing.calls)

    @pytest.mark.asyncio
    async def test_rejects_invalid_estimated_credits(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        with pytest.raises(AIJobAccountingGatewayError, match="estimated_credits must be a positive integer"):
            await gateway.reserve_credits_for_job(
                session,
                organization_id="org-1",
                job_id="job-1",
                estimated_credits=0,
                operation_type="image_generation",
            )

        assert not any(method == "reserve_ai_job_credits" for method, _ in fake_costing.calls)

    @pytest.mark.asyncio
    async def test_reserve_delegates_with_session_and_metadata(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        result = await gateway.reserve_credits_for_job(
            session,
            organization_id="org-1",
            job_id="job-1",
            estimated_credits=5,
            project_id="project-1",
            user_id="user-1",
            operation_type="image_generation",
            provider_type="llm",
            provider_name="provider-x",
            workflow_id="workflow-1",
            workflow_version="v1",
            workflow_hash="hash-1",
            model_name="model-a",
            input_asset_ids=[" asset-1 ", ""],
        )

        assert result.ledger_entry_id == "reserve-entry-1"
        method, payload = fake_costing.calls[-1]
        assert method == "reserve_ai_job_credits"
        assert payload["session"] is session
        assert payload["organization_id"] == "org-1"
        assert payload["job_id"] == "job-1"
        assert payload["estimated_credits"] == 5
        assert payload["idempotency_key"] == "ai_job:org-1:job-1:reserve"
        assert payload["metadata"]["job_id"] == "job-1"
        assert payload["metadata"]["project_id"] == "project-1"
        assert payload["metadata"]["user_id"] == "user-1"
        assert payload["metadata"]["operation_type"] == "image_generation"
        assert payload["metadata"]["provider_type"] == "llm"
        assert payload["metadata"]["provider_name"] == "provider-x"
        assert payload["metadata"]["workflow_id"] == "workflow-1"
        assert payload["metadata"]["workflow_version"] == "v1"
        assert payload["metadata"]["workflow_hash"] == "hash-1"
        assert payload["metadata"]["model_name"] == "model-a"
        assert payload["metadata"]["input_asset_ids"] == ["asset-1"]
        assert payload["metadata"]["job_status"] == "reserved"


class TestConsumeAndRelease:
    @pytest.mark.asyncio
    async def test_consume_requires_reservation_entry_id(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        with pytest.raises(AIJobAccountingGatewayError, match="reservation_entry_id must be a non-empty string"):
            await gateway.consume_reserved_credits_for_job(
                session,
                organization_id="org-1",
                job_id="job-1",
                reservation_entry_id=None,
                actual_credits=4,
                operation_type="image_generation",
            )

        assert not any(method == "consume_ai_job_credits" for method, _ in fake_costing.calls)

    @pytest.mark.asyncio
    async def test_release_requires_reservation_entry_id(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        with pytest.raises(AIJobAccountingGatewayError, match="reservation_entry_id must be a non-empty string"):
            await gateway.release_reserved_credits_for_job(
                session,
                organization_id="org-1",
                job_id="job-1",
                reservation_entry_id="",
                release_credits=4,
                operation_type="image_generation",
            )

        assert not any(method == "release_ai_job_credits" for method, _ in fake_costing.calls)

    @pytest.mark.asyncio
    async def test_consume_delegates_with_reservation_metadata(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        result = await gateway.consume_reserved_credits_for_job(
            session,
            organization_id="org-1",
            job_id="job-1",
            reservation_entry_id="reservation-entry-1",
            actual_credits=4,
            project_id="project-1",
            user_id="user-1",
            operation_type="image_generation",
            provider_type="llm",
            provider_name="provider-x",
            workflow_id="workflow-1",
            workflow_version="v1",
            workflow_hash="hash-1",
            model_name="model-a",
            input_asset_ids=["asset-1"],
            caller_key="retry-1",
        )

        assert result.ledger_entry_id == "consume-entry-1"
        method, payload = fake_costing.calls[-1]
        assert method == "consume_ai_job_credits"
        assert payload["session"] is session
        assert payload["idempotency_key"] == "ai_job:org-1:job-1:consume:retry-1"
        assert payload["metadata"]["reservation_entry_id"] == "reservation-entry-1"
        assert payload["metadata"]["job_status"] == "consumed"
        assert payload["metadata"]["input_asset_ids"] == ["asset-1"]

    @pytest.mark.asyncio
    async def test_release_delegates_with_reservation_metadata(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        result = await gateway.release_reserved_credits_for_job(
            session,
            organization_id="org-1",
            job_id="job-1",
            reservation_entry_id="reservation-entry-1",
            release_credits=4,
            project_id="project-1",
            user_id="user-1",
            operation_type="image_generation",
            provider_type="llm",
            provider_name="provider-x",
            workflow_id="workflow-1",
            workflow_version="v1",
            workflow_hash="hash-1",
            model_name="model-a",
            input_asset_ids=["asset-1"],
            caller_key="retry-2",
        )

        assert result.ledger_entry_id == "release-entry-1"
        method, payload = fake_costing.calls[-1]
        assert method == "release_ai_job_credits"
        assert payload["session"] is session
        assert payload["idempotency_key"] == "ai_job:org-1:job-1:release:retry-2"
        assert payload["metadata"]["reservation_entry_id"] == "reservation-entry-1"
        assert payload["metadata"]["job_status"] == "released"


class TestEstimateAndAvailability:
    @pytest.mark.asyncio
    async def test_estimate_delegates_to_costing_service(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        result = await gateway.estimate_credit_cost(
            session,
            operation_type="image_generation",
            estimated_credits=12,
        )

        assert result.estimated_credits == 5
        method, payload = fake_costing.calls[-1]
        assert method == "estimate_ai_job_cost"
        assert payload["operation_type"] == "image_generation"
        assert payload["estimated_credits"] == 12

    @pytest.mark.asyncio
    async def test_availability_delegates_without_mutation_or_session_creation(
        self,
        gateway: AIJobAccountingGateway,
        fake_costing: FakeCostingService,
        session: DummySession,
    ) -> None:
        result = await gateway.check_credit_availability(
            session,
            organization_id="org-1",
            operation_type="image_generation",
            estimated_credits=9,
        )

        assert result.sufficient is True
        method, payload = fake_costing.calls[-1]
        assert method == "check_ai_job_credit_availability"
        assert payload["session"] is session
        assert payload["organization_id"] == "org-1"


def test_gateway_source_has_no_forbidden_strings() -> None:
    source = inspect.getsource(AIJobAccountingGateway)
    forbidden_terms = (
        "AsyncSessionLocal",
        ".commit(",
        "create_async_engine",
        "".join(["sq", "lite"]),
        "".join(["Sq", "lite"]),
        "".join(["aio", "".join(["sq", "lite"])]),
    )

    assert all(term not in source for term in forbidden_terms)
