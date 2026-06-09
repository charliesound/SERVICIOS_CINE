from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.credit_gate_service import (
    DEFAULT_OPERATION_CREDIT_COSTS,
    CreditAvailabilityCheckResult,
    CreditCostEstimationError,
    CreditGateEstimateResult,
    CreditGateService,
)
from services.credit_ledger_service import (
    CreditAvailabilityResult,
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditReservationResult,
    DuplicateIdempotencyKeyError,
    InsufficientCreditsError,
)


class DummySession:
    pass


class FakeLedgerService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.available_by_organization: dict[str, int] = {}
        self.duplicate_keys: dict[str, str] = {}

    async def get_available_credits(self, session, organization_id: str) -> CreditAvailabilityResult:
        self.calls.append(
            ("get_available_credits", {"session": session, "organization_id": organization_id})
        )
        available = self.available_by_organization.get(organization_id, 0)
        return CreditAvailabilityResult(
            organization_id=organization_id,
            balance_id="bal-{0}".format(organization_id),
            available_before=available,
            available_after=available,
            amount=available,
            status="ok",
            message="Available credits computed",
        )

    async def reserve_credits(
        self,
        session,
        organization_id: str,
        amount: int,
        project_id: str | None = None,
        user_id: str | None = None,
        job_id: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
        idempotency_key: str | None = None,
    ) -> CreditReservationResult:
        self.calls.append(
            (
                "reserve_credits",
                {
                    "session": session,
                    "organization_id": organization_id,
                    "amount": amount,
                    "project_id": project_id,
                    "user_id": user_id,
                    "job_id": job_id,
                    "reason": reason,
                    "metadata": metadata,
                    "idempotency_key": idempotency_key,
                },
            )
        )
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        available = self.available_by_organization.get(organization_id, 0)
        if available < amount:
            raise InsufficientCreditsError(requested=amount, available=available)
        return CreditReservationResult(
            organization_id=organization_id,
            balance_id="bal-{0}".format(organization_id),
            available_before=available,
            available_after=available - amount,
            amount=amount,
            ledger_entry_id="reserve-{0}".format(organization_id),
            message="reserved",
        )

    async def consume_reserved_credits(
        self,
        session,
        organization_id: str,
        amount: int,
        project_id: str | None = None,
        user_id: str | None = None,
        job_id: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
        idempotency_key: str | None = None,
    ) -> CreditConsumptionResult:
        self.calls.append(
            (
                "consume_reserved_credits",
                {
                    "session": session,
                    "organization_id": organization_id,
                    "amount": amount,
                    "project_id": project_id,
                    "user_id": user_id,
                    "job_id": job_id,
                    "reason": reason,
                    "metadata": metadata,
                    "idempotency_key": idempotency_key,
                },
            )
        )
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        return CreditConsumptionResult(
            organization_id=organization_id,
            balance_id="bal-{0}".format(organization_id),
            amount=amount,
            ledger_entry_id="consume-{0}".format(organization_id),
            bucket_debits={"purchased_balance": amount},
            message="consumed",
        )

    async def release_reserved_credits(
        self,
        session,
        organization_id: str,
        amount: int,
        job_id: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
        idempotency_key: str | None = None,
    ) -> CreditReleaseResult:
        self.calls.append(
            (
                "release_reserved_credits",
                {
                    "session": session,
                    "organization_id": organization_id,
                    "amount": amount,
                    "job_id": job_id,
                    "reason": reason,
                    "metadata": metadata,
                    "idempotency_key": idempotency_key,
                },
            )
        )
        if idempotency_key in self.duplicate_keys:
            raise DuplicateIdempotencyKeyError(idempotency_key or "", self.duplicate_keys[idempotency_key])
        return CreditReleaseResult(
            organization_id=organization_id,
            balance_id="bal-{0}".format(organization_id),
            amount=amount,
            ledger_entry_id="release-{0}".format(organization_id),
            message="released",
        )


@pytest.fixture
def session() -> DummySession:
    return DummySession()


@pytest.fixture
def fake_ledger() -> FakeLedgerService:
    return FakeLedgerService()


@pytest.fixture
def service(fake_ledger: FakeLedgerService) -> CreditGateService:
    return CreditGateService(ledger_service=fake_ledger)


class TestEstimateCreditCost:
    def test_estimates_known_operation_cost(self, service: CreditGateService) -> None:
        result = service.estimate_credit_cost(operation_type="script_analysis")

        assert isinstance(result, CreditGateEstimateResult)
        assert result.estimated_credits == DEFAULT_OPERATION_CREDIT_COSTS["script_analysis"]
        assert result.cost_source == "table"

    def test_accepts_valid_explicit_cost(self, service: CreditGateService) -> None:
        result = service.estimate_credit_cost(
            operation_type="unknown_future_operation",
            estimated_credits=17,
        )

        assert result.estimated_credits == 17
        assert result.cost_source == "explicit"

    def test_rejects_empty_operation_type(self, service: CreditGateService) -> None:
        with pytest.raises(CreditCostEstimationError, match="operation_type must be a non-empty string"):
            service.estimate_credit_cost(operation_type="")

    def test_rejects_whitespace_only_operation_type(self, service: CreditGateService) -> None:
        with pytest.raises(CreditCostEstimationError, match="operation_type must be a non-empty string"):
            service.estimate_credit_cost(operation_type="   ")

    def test_rejects_non_string_operation_type(self, service: CreditGateService) -> None:
        with pytest.raises(CreditCostEstimationError, match="operation_type must be a non-empty string"):
            service.estimate_credit_cost(operation_type=123)  # type: ignore[arg-type]

    def test_normalizes_operation_type_with_strip(self, service: CreditGateService) -> None:
        result = service.estimate_credit_cost(operation_type="  script_analysis  ")

        assert result.operation_type == "script_analysis"
        assert result.estimated_credits == DEFAULT_OPERATION_CREDIT_COSTS["script_analysis"]

    @pytest.mark.parametrize("invalid_cost", [0, -1, True])
    def test_rejects_zero_or_negative_or_bool_explicit_cost(
        self, service: CreditGateService, invalid_cost: int
    ) -> None:
        with pytest.raises(CreditCostEstimationError):
            service.estimate_credit_cost(
                operation_type="script_analysis",
                estimated_credits=invalid_cost,
            )

    def test_rejects_unknown_operation_without_explicit_cost(
        self, service: CreditGateService
    ) -> None:
        with pytest.raises(CreditCostEstimationError, match="Unknown operation_type"):
            service.estimate_credit_cost(operation_type="unknown_future_operation")


class TestCheckCreditAvailability:
    @pytest.mark.asyncio
    async def test_returns_sufficient_when_credits_cover_requirement(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 20

        result = await service.check_credit_availability(
            session,
            organization_id="org-1",
            operation_type="  image_generation  ",
        )

        assert isinstance(result, CreditAvailabilityCheckResult)
        assert result.sufficient is True
        assert result.operation_type == "image_generation"
        assert result.required_credits == DEFAULT_OPERATION_CREDIT_COSTS["image_generation"]
        assert result.available_credits == 20

    @pytest.mark.asyncio
    async def test_returns_insufficient_when_balance_is_too_low(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 2

        result = await service.check_credit_availability(
            session,
            organization_id="org-1",
            operation_type="video_generation",
        )

        assert result.sufficient is False
        assert result.required_credits == DEFAULT_OPERATION_CREDIT_COSTS["video_generation"]
        assert result.available_credits == 2


class TestReserveConsumeRelease:
    @pytest.mark.asyncio
    async def test_reserve_calls_credit_ledger_with_expected_fields(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 50

        result = await service.reserve_credits_for_operation(
            session,
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            operation_type="  storyboard_generation  ",
            job_id="job-1",
            reason="storyboard reserve",
            idempotency_key="idem-1",
            metadata={
                "phase": "preflight",
                "operation_type": "tampered",
                "estimated_credits": 999,
            },
        )

        assert result.amount == DEFAULT_OPERATION_CREDIT_COSTS["storyboard_generation"]
        method, payload = fake_ledger.calls[-1]
        assert method == "reserve_credits"
        assert payload["organization_id"] == "org-1"
        assert payload["project_id"] == "proj-1"
        assert payload["user_id"] == "user-1"
        assert payload["job_id"] == "job-1"
        assert payload["reason"] == "storyboard reserve"
        assert payload["idempotency_key"] == "idem-1"
        assert payload["metadata"] == {
            "operation_type": "storyboard_generation",
            "estimated_credits": DEFAULT_OPERATION_CREDIT_COSTS["storyboard_generation"],
            "phase": "preflight",
        }

    @pytest.mark.asyncio
    async def test_consume_calls_credit_ledger_with_expected_fields(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        result = await service.consume_reserved_credits_for_operation(
            session,
            organization_id="org-1",
            project_id="proj-1",
            user_id="user-1",
            operation_type="  transcription  ",
            job_id="job-2",
            reason="transcription consume",
            idempotency_key="idem-2",
            metadata={"provider": "internal"},
        )

        assert result.amount == DEFAULT_OPERATION_CREDIT_COSTS["transcription"]
        method, payload = fake_ledger.calls[-1]
        assert method == "consume_reserved_credits"
        assert payload["organization_id"] == "org-1"
        assert payload["project_id"] == "proj-1"
        assert payload["user_id"] == "user-1"
        assert payload["job_id"] == "job-2"
        assert payload["reason"] == "transcription consume"
        assert payload["idempotency_key"] == "idem-2"
        assert payload["metadata"] == {
            "operation_type": "transcription",
            "estimated_credits": DEFAULT_OPERATION_CREDIT_COSTS["transcription"],
            "provider": "internal",
        }

    @pytest.mark.asyncio
    async def test_release_calls_credit_ledger_with_expected_fields(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        result = await service.release_reserved_credits_for_operation(
            session,
            organization_id="org-1",
            operation_type="  sound_sync  ",
            job_id="job-3",
            reason="sound sync release",
            idempotency_key="idem-3",
            metadata={"cleanup": True},
        )

        assert result.amount == DEFAULT_OPERATION_CREDIT_COSTS["sound_sync"]
        method, payload = fake_ledger.calls[-1]
        assert method == "release_reserved_credits"
        assert payload["organization_id"] == "org-1"
        assert payload["job_id"] == "job-3"
        assert payload["reason"] == "sound sync release"
        assert payload["idempotency_key"] == "idem-3"
        assert payload["metadata"] == {
            "operation_type": "sound_sync",
            "estimated_credits": DEFAULT_OPERATION_CREDIT_COSTS["sound_sync"],
            "cleanup": True,
        }

    @pytest.mark.asyncio
    async def test_default_reason_is_derived_from_operation(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 10

        await service.reserve_credits_for_operation(
            session,
            organization_id="org-1",
            operation_type="script_analysis",
            job_id="job-4",
        )

        _, payload = fake_ledger.calls[-1]
        assert payload["reason"] == "credit_gate.reserve.script_analysis"


class TestErrorPropagationAndTenantIsolation:
    @pytest.mark.asyncio
    async def test_propagates_insufficient_credits_error(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 0

        with pytest.raises(InsufficientCreditsError):
            await service.reserve_credits_for_operation(
                session,
                organization_id="org-1",
                operation_type="script_analysis",
                job_id="job-5",
                estimated_credits=2,
            )

    @pytest.mark.asyncio
    async def test_propagates_duplicate_idempotency_key(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-1"] = 10
        fake_ledger.duplicate_keys["dup-key"] = "existing-entry-1"

        with pytest.raises(DuplicateIdempotencyKeyError) as exc:
            await service.reserve_credits_for_operation(
                session,
                organization_id="org-1",
                operation_type="script_analysis",
                job_id="job-6",
                idempotency_key="dup-key",
            )

        assert exc.value.idempotency_key == "dup-key"
        assert exc.value.existing_entry_id == "existing-entry-1"

    @pytest.mark.asyncio
    async def test_keeps_organizations_separate_in_calls(
        self,
        service: CreditGateService,
        fake_ledger: FakeLedgerService,
        session: DummySession,
    ) -> None:
        fake_ledger.available_by_organization["org-a"] = 15
        fake_ledger.available_by_organization["org-b"] = 30

        await service.reserve_credits_for_operation(
            session,
            organization_id="org-a",
            operation_type="script_analysis",
            job_id="job-a",
        )
        await service.reserve_credits_for_operation(
            session,
            organization_id="org-b",
            operation_type="image_generation",
            job_id="job-b",
        )

        reserve_calls = [
            payload
            for method, payload in fake_ledger.calls
            if method == "reserve_credits"
        ]
        assert reserve_calls[0]["organization_id"] == "org-a"
        assert reserve_calls[0]["job_id"] == "job-a"
        assert reserve_calls[1]["organization_id"] == "org-b"
        assert reserve_calls[1]["job_id"] == "job-b"
