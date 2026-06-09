from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_costing_service import AIJobCostingError, AIJobCostingService
from services.credit_gate_service import (
    CreditAvailabilityCheckResult,
    CreditGateEstimateResult,
)
from services.credit_ledger_service import (
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditReservationResult,
    DuplicateIdempotencyKeyError,
    InsufficientCreditsError,
)


class DummySession:
    pass


class FakeCreditGateService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.duplicate_keys: dict[str, str] = {}
        self.available_by_organization: dict[str, int] = {}
        self.costs: dict[str, int] = {
            "script_analysis": 1,
            "image_generation": 8,
            "transcription": 3,
            "sound_sync": 6,
        }

    def estimate_credit_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditGateEstimateResult:
        normalized = operation_type.strip()
        self.calls.append(
            (
                "estimate_credit_cost",
                {
                    "operation_type": operation_type,
                    "estimated_credits": estimated_credits,
                },
            )
        )
        if estimated_credits is not None:
            if estimated_credits <= 0:
                raise ValueError("estimated_credits must be positive")
            return CreditGateEstimateResult(
                operation_type=normalized,
                estimated_credits=estimated_credits,
                cost_source="explicit",
            )
        return CreditGateEstimateResult(
            operation_type=normalized,
            estimated_credits=self.costs[normalized],
            cost_source="table",
        )

    async def check_credit_availability(
        self,
        session,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditAvailabilityCheckResult:
        estimate = self.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        available = self.available_by_organization.get(organization_id, 0)
        self.calls.append(
            (
                "check_credit_availability",
                {
                    "session": session,
                    "organization_id": organization_id,
                    "operation_type": operation_type,
                    "estimated_credits": estimated_credits,
                },
            )
        )
        return CreditAvailabilityCheckResult(
            organization_id=organization_id,
            operation_type=estimate.operation_type,
            required_credits=estimate.estimated_credits,
            available_credits=available,
            sufficient=available >= estimate.estimated_credits,
            balance_id="bal-{0}".format(organization_id),
            status="ok",
            message="checked",
        )

    async def reserve_credits_for_operation(self, session, **kwargs) -> CreditReservationResult:
        self.calls.append(("reserve_credits_for_operation", {"session": session, **kwargs}))
        idempotency_key = kwargs.get("idempotency_key")
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        organization_id = kwargs["organization_id"]
        amount = kwargs["estimated_credits"] or self.costs[kwargs["operation_type"].strip()]
        available = self.available_by_organization.get(organization_id, 0)
        if available < amount:
            raise InsufficientCreditsError(requested=amount, available=available)
        return CreditReservationResult(
            organization_id=organization_id,
            balance_id="bal-{0}".format(organization_id),
            amount=amount,
            ledger_entry_id="reserve-{0}".format(kwargs["job_id"]),
            message="reserved",
        )

    async def consume_reserved_credits_for_operation(self, session, **kwargs) -> CreditConsumptionResult:
        self.calls.append(("consume_reserved_credits_for_operation", {"session": session, **kwargs}))
        idempotency_key = kwargs.get("idempotency_key")
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        amount = kwargs["estimated_credits"] or self.costs[kwargs["operation_type"].strip()]
        return CreditConsumptionResult(
            organization_id=kwargs["organization_id"],
            balance_id="bal-{0}".format(kwargs["organization_id"]),
            amount=amount,
            ledger_entry_id="consume-{0}".format(kwargs["job_id"]),
            message="consumed",
            bucket_debits={"purchased_balance": amount},
        )

    async def release_reserved_credits_for_operation(self, session, **kwargs) -> CreditReleaseResult:
        self.calls.append(("release_reserved_credits_for_operation", {"session": session, **kwargs}))
        idempotency_key = kwargs.get("idempotency_key")
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        amount = kwargs["estimated_credits"] or self.costs[kwargs["operation_type"].strip()]
        return CreditReleaseResult(
            organization_id=kwargs["organization_id"],
            balance_id="bal-{0}".format(kwargs["organization_id"]),
            amount=amount,
            ledger_entry_id="release-{0}".format(kwargs["job_id"]),
            message="released",
        )


@pytest.fixture
def session() -> DummySession:
    return DummySession()


@pytest.fixture
def fake_gate() -> FakeCreditGateService:
    return FakeCreditGateService()


@pytest.fixture
def service(fake_gate: FakeCreditGateService) -> AIJobCostingService:
    return AIJobCostingService(credit_gate_service=fake_gate)


class TestEstimateAndCheck:
    def test_estimate_ai_job_cost_uses_credit_gate_service(
        self,
        service: AIJobCostingService,
    ) -> None:
        result = service.estimate_ai_job_cost(operation_type="  script_analysis  ")

        assert result.operation_type == "script_analysis"
        assert result.estimated_credits == 1
        assert result.cost_source == "table"

    @pytest.mark.asyncio
    async def test_check_ai_job_credit_availability_delegates_correctly(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        fake_gate.available_by_organization["org-1"] = 10

        result = await service.check_ai_job_credit_availability(
            session,
            organization_id="org-1",
            operation_type=" image_generation ",
        )

        assert result.organization_id == "org-1"
        assert result.operation_type == "image_generation"
        assert result.required_credits == 8
        assert result.available_credits == 10
        assert result.sufficient is True


class TestCanonicalMetadata:
    def test_build_ai_job_costing_metadata_protects_canonical_fields(
        self,
        service: AIJobCostingService,
    ) -> None:
        metadata = service.build_ai_job_costing_metadata(
            operation_type=" image_generation ",
            provider_type=" api ",
            provider_name=" provider-x ",
            workflow_id=" wf-1 ",
            workflow_version=" v1 ",
            workflow_hash=" hash-1 ",
            model_name=" model-a ",
            input_asset_ids=[" in-1 ", "", "in-2"],
            output_asset_ids=[" out-1 "],
            job_status=" running ",
            failure_reason=" ignored ",
            metadata={
                "operation_type": "tampered",
                "estimated_credits": 999,
                "provider_type": "tampered",
                "provider_name": "tampered",
                "workflow_id": "tampered",
                "workflow_version": "tampered",
                "workflow_hash": "tampered",
                "model_name": "tampered",
                "input_asset_ids": ["tampered"],
                "output_asset_ids": ["tampered"],
                "job_status": "tampered",
                "failure_reason": "tampered",
                "extra_key": "kept",
            },
        )

        assert metadata == {
            "operation_type": "image_generation",
            "estimated_credits": 8,
            "provider_type": "api",
            "provider_name": "provider-x",
            "workflow_id": "wf-1",
            "workflow_version": "v1",
            "workflow_hash": "hash-1",
            "model_name": "model-a",
            "input_asset_ids": ["in-1", "in-2"],
            "output_asset_ids": ["out-1"],
            "job_status": "running",
            "failure_reason": "ignored",
            "extra_key": "kept",
        }

    def test_rejects_non_string_asset_entries(
        self,
        service: AIJobCostingService,
    ) -> None:
        with pytest.raises(AIJobCostingError, match="input_asset_ids entries must be strings"):
            service.build_ai_job_costing_metadata(
                operation_type="script_analysis",
                input_asset_ids=["ok", 123],  # type: ignore[list-item]
            )


class TestReserveConsumeRelease:
    @pytest.mark.asyncio
    async def test_reserve_ai_job_credits_uses_canonical_metadata(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        fake_gate.available_by_organization["org-1"] = 20

        result = await service.reserve_ai_job_credits(
            session,
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            job_id="job-1",
            operation_type=" script_analysis ",
            provider_type="llm",
            model_name="gpt-x",
            input_asset_ids=["script-1"],
            metadata={"extra": "value", "job_status": "tampered"},
            reason="reserve reason",
            idempotency_key="idem-1",
        )

        assert result.organization_id == "org-1"
        method, payload = fake_gate.calls[-1]
        assert method == "reserve_credits_for_operation"
        assert payload["organization_id"] == "org-1"
        assert payload["project_id"] == "proj-1"
        assert payload["user_id"] == "user-1"
        assert payload["job_id"] == "job-1"
        assert payload["operation_type"] == " script_analysis "
        assert payload["reason"] == "reserve reason"
        assert payload["idempotency_key"] == "idem-1"
        assert payload["metadata"]["operation_type"] == "script_analysis"
        assert payload["metadata"]["estimated_credits"] == 1
        assert payload["metadata"]["provider_type"] == "llm"
        assert payload["metadata"]["model_name"] == "gpt-x"
        assert payload["metadata"]["job_status"] == "reserved"
        assert payload["metadata"]["input_asset_ids"] == ["script-1"]
        assert payload["metadata"]["extra"] == "value"

    @pytest.mark.asyncio
    async def test_consume_ai_job_credits_uses_canonical_metadata(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        result = await service.consume_ai_job_credits(
            session,
            organization_id="org-1",
            project_id="proj-2",
            user_id="user-2",
            job_id="job-2",
            operation_type=" transcription ",
            output_asset_ids=[" transcript-1 "],
            provider_name="provider-y",
            reason="consume reason",
            idempotency_key="idem-2",
        )

        assert result.organization_id == "org-1"
        method, payload = fake_gate.calls[-1]
        assert method == "consume_reserved_credits_for_operation"
        assert payload["project_id"] == "proj-2"
        assert payload["user_id"] == "user-2"
        assert payload["job_id"] == "job-2"
        assert payload["reason"] == "consume reason"
        assert payload["idempotency_key"] == "idem-2"
        assert payload["metadata"]["operation_type"] == "transcription"
        assert payload["metadata"]["estimated_credits"] == 3
        assert payload["metadata"]["provider_name"] == "provider-y"
        assert payload["metadata"]["output_asset_ids"] == ["transcript-1"]
        assert payload["metadata"]["job_status"] == "consumed"

    @pytest.mark.asyncio
    async def test_release_ai_job_credits_uses_failure_reason(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        result = await service.release_ai_job_credits(
            session,
            organization_id="org-2",
            job_id="job-3",
            operation_type=" sound_sync ",
            failure_reason=" timeout ",
            provider_type="gpu_on_demand",
            reason="release reason",
            idempotency_key="idem-3",
        )

        assert result.organization_id == "org-2"
        method, payload = fake_gate.calls[-1]
        assert method == "release_reserved_credits_for_operation"
        assert payload["organization_id"] == "org-2"
        assert payload["job_id"] == "job-3"
        assert payload["reason"] == "release reason"
        assert payload["idempotency_key"] == "idem-3"
        assert payload["metadata"]["operation_type"] == "sound_sync"
        assert payload["metadata"]["estimated_credits"] == 6
        assert payload["metadata"]["provider_type"] == "gpu_on_demand"
        assert payload["metadata"]["job_status"] == "released"
        assert payload["metadata"]["failure_reason"] == "timeout"


class TestErrorPropagationAndIsolation:
    @pytest.mark.asyncio
    async def test_propagates_insufficient_credits_error(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        fake_gate.available_by_organization["org-1"] = 0

        with pytest.raises(InsufficientCreditsError):
            await service.reserve_ai_job_credits(
                session,
                organization_id="org-1",
                job_id="job-4",
                operation_type="script_analysis",
            )

    @pytest.mark.asyncio
    async def test_propagates_duplicate_idempotency_key_error(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        fake_gate.available_by_organization["org-1"] = 10
        fake_gate.duplicate_keys["dup-key"] = "entry-1"

        with pytest.raises(DuplicateIdempotencyKeyError) as exc:
            await service.reserve_ai_job_credits(
                session,
                organization_id="org-1",
                job_id="job-5",
                operation_type="script_analysis",
                idempotency_key="dup-key",
            )

        assert exc.value.idempotency_key == "dup-key"
        assert exc.value.existing_entry_id == "entry-1"

    @pytest.mark.asyncio
    async def test_does_not_mix_organizations_in_fake_gate_calls(
        self,
        service: AIJobCostingService,
        fake_gate: FakeCreditGateService,
        session: DummySession,
    ) -> None:
        fake_gate.available_by_organization["org-a"] = 20
        fake_gate.available_by_organization["org-b"] = 20

        await service.reserve_ai_job_credits(
            session,
            organization_id="org-a",
            job_id="job-a",
            operation_type="script_analysis",
        )
        await service.reserve_ai_job_credits(
            session,
            organization_id="org-b",
            job_id="job-b",
            operation_type="image_generation",
        )

        reserve_calls = [
            payload
            for method, payload in fake_gate.calls
            if method == "reserve_credits_for_operation"
        ]
        assert reserve_calls[0]["organization_id"] == "org-a"
        assert reserve_calls[0]["job_id"] == "job-a"
        assert reserve_calls[1]["organization_id"] == "org-b"
        assert reserve_calls[1]["job_id"] == "job-b"
