from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.billing import (
    CreditBalance,
    CreditLedgerEntry,
    CREDIT_LEDGER_ENTRY_TYPES,
    CREDIT_ENTRY_STATUSES,
)
from services.credit_ledger_service import (
    CREDIT_CONSUMPTION_BUCKET_ORDER,
    GRANT_ALLOWED_BUCKETS,
    LEDGER_ENTRY_TYPE_GRANT,
    LEDGER_ENTRY_TYPE_RESERVE,
    LEDGER_ENTRY_TYPE_RELEASE,
    LEDGER_ENTRY_TYPE_CONSUME,
    LEDGER_STATUS_AVAILABLE,
    LEDGER_STATUS_RESERVED,
    LEDGER_STATUS_RELEASED,
    LEDGER_STATUS_CONSUMED,
    calculate_available_credits,
    validate_positive_amount,
    allocate_credit_buckets,
    apply_bucket_debit,
    apply_bucket_credit,
    CreditLedgerService,
    CreditLedgerError,
    CreditBalanceNotFoundError,
    InsufficientCreditsError,
    CreditReservationNotFoundError,
    DuplicateIdempotencyKeyError,
    InvalidCreditAmountError,
    CreditLedgerStateError,
    CreditAvailabilityResult,
    CreditReservationResult,
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditGrantResult,
)
from schemas.credit_ledger_schema import (
    CreditAvailabilityRead,
    CreditGrantRequest,
    CreditReserveRequest,
    CreditReleaseRequest,
    CreditConsumeRequest,
    CreditLedgerOperationResult,
    CREDIT_GRANT_BUCKETS,
)


# --- Fake session helpers (no real DB) ------------------------------------


class FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class FakeAsyncSession:
    """Minimal fake AsyncSession for ledger unit tests.

    - Stores added ORM objects in self.added.
    - Holds an in-memory dict of (model, id) -> instance for _get_balance.
    - Tracks idempotency_key lookups separately for the ledger entries table.
    - Implements execute() returning a FakeScalarResult.
    - flush() is a no-op but is awaited.
    """

    def __init__(self) -> None:
        self.added: list = []
        self.balances: dict[str, CreditBalance] = {}
        self.idempotency_index: dict[str, CreditLedgerEntry] = {}
        self.commits: int = 0
        self.flushes: int = 0

    async def execute(self, stmt):
        # The service builds Select statements via SQLModel/SQLAlchemy; we
        # detect them by class name to avoid re-importing the same class.
        cls_name = type(stmt).__name__
        if cls_name == "Select":
            model = None
            if stmt.column_descriptions:
                model = stmt.column_descriptions[0].get("entity")
            if model is CreditBalance:
                for col, val in _filters_from_stmt(stmt):
                    if col == "organization_id":
                        return FakeScalarResult(self.balances.get(val))
            if model is CreditLedgerEntry:
                for col, val in _filters_from_stmt(stmt):
                    if col == "idempotency_key":
                        return FakeScalarResult(self.idempotency_index.get(val))
        return FakeScalarResult(None)

    async def flush(self) -> None:
        self.flushes += 1
        # index newly added entries by idempotency_key for later lookups
        for obj in self.added:
            if isinstance(obj, CreditLedgerEntry) and obj.idempotency_key:
                self.idempotency_index[obj.idempotency_key] = obj

    async def commit(self) -> None:
        self.commits += 1

    def add(self, obj) -> None:
        self.added.append(obj)
        if isinstance(obj, CreditBalance):
            if not getattr(obj, "id", None):
                obj.id = uuid.uuid4().hex
            self.balances[obj.organization_id] = obj


def _filters_from_stmt(stmt) -> list[tuple[str, Any]]:
    """Very small helper to extract (column_name, value) equality filters.

    Only supports the simple `Model.col == value` clauses used by the service.
    """
    pairs: list[tuple[str, Any]] = []
    try:
        where = stmt.whereclause
    except Exception:
        return pairs
    if where is None:
        return pairs
    # Walk a single And conjunction if needed
    clauses = []
    if hasattr(where, "clauses"):
        clauses = list(where.clauses)
    else:
        clauses = [where]
    for clause in clauses:
        left = getattr(clause, "left", None)
        right = getattr(clause, "right", None)
        op = getattr(clause, "operator", None)
        if op is not None and getattr(op, "__name__", "") == "eq" and left is not None and right is not None:
            col_name = getattr(left, "name", None) or getattr(left, "key", None)
            if col_name:
                pairs.append((col_name, right.value if hasattr(right, "value") else right))
    return pairs


def make_balance(
    *,
    organization_id: str = "org-1",
    trial_balance: int = 0,
    promotional_balance: int = 0,
    included_monthly_remaining: int = 0,
    purchased_balance: int = 0,
    enterprise_balance: int = 0,
    reserved_active: int = 0,
    consumed_period: int = 0,
    expired_total: int = 0,
    refunded_total: int = 0,
    adjusted_total: int = 0,
    version: int = 1,
) -> CreditBalance:
    balance = CreditBalance(
        id=uuid.uuid4().hex,
        organization_id=organization_id,
        trial_balance=trial_balance,
        promotional_balance=promotional_balance,
        included_monthly_remaining=included_monthly_remaining,
        purchased_balance=purchased_balance,
        enterprise_balance=enterprise_balance,
        reserved_active=reserved_active,
        consumed_period=consumed_period,
        expired_total=expired_total,
        refunded_total=refunded_total,
        adjusted_total=adjusted_total,
        version=version,
        last_updated_at=datetime.utcnow(),
    )
    return balance


# --- Pure function tests --------------------------------------------------


class TestCalculateAvailableCredits:
    def test_subtracts_reserved(self) -> None:
        b = make_balance(
            trial_balance=100,
            promotional_balance=200,
            included_monthly_remaining=300,
            purchased_balance=400,
            enterprise_balance=500,
            reserved_active=50,
        )
        # (100 + 200 + 300 + 400 + 500) - 50 = 1450
        assert calculate_available_credits(b) == 1450

    def test_zero_when_none(self) -> None:
        # Defensive: passing None must not crash; the function is annotated
        # to take a CreditBalance but we guard against None.
        assert calculate_available_credits(None) == 0  # type: ignore[arg-type]

    def test_zero_when_all_zero(self) -> None:
        b = make_balance()
        assert calculate_available_credits(b) == 0


class TestValidatePositiveAmount:
    def test_accepts_positive(self) -> None:
        validate_positive_amount(1)
        validate_positive_amount(1_000_000)

    def test_rejects_zero(self) -> None:
        with pytest.raises(InvalidCreditAmountError):
            validate_positive_amount(0)

    def test_rejects_negative(self) -> None:
        with pytest.raises(InvalidCreditAmountError):
            validate_positive_amount(-1)

    def test_rejects_non_int(self) -> None:
        with pytest.raises(InvalidCreditAmountError):
            validate_positive_amount(1.5)  # type: ignore[arg-type]

    def test_rejects_bool(self) -> None:
        with pytest.raises(InvalidCreditAmountError):
            validate_positive_amount(True)  # type: ignore[arg-type]


class TestAllocateCreditBuckets:
    def test_uses_canonical_order(self) -> None:
        b = make_balance(
            trial_balance=10,
            promotional_balance=20,
            included_monthly_remaining=30,
            purchased_balance=40,
            enterprise_balance=50,
        )
        alloc = allocate_credit_buckets(b, 25)
        # Canonical order: trial first (10), then promotional (15 of 20)
        assert alloc == {"trial_balance": 10, "promotional_balance": 15}
        # Order of keys must follow the canonical order
        assert list(alloc.keys()) == ["trial_balance", "promotional_balance"]

    def test_full_consumption(self) -> None:
        b = make_balance(
            trial_balance=1, promotional_balance=2,
            included_monthly_remaining=3, purchased_balance=4,
            enterprise_balance=5,
        )
        alloc = allocate_credit_buckets(b, 15)
        assert alloc == {
            "trial_balance": 1,
            "promotional_balance": 2,
            "included_monthly_remaining": 3,
            "purchased_balance": 4,
            "enterprise_balance": 5,
        }
        assert sum(alloc.values()) == 15

    def test_partial_first_bucket(self) -> None:
        b = make_balance(trial_balance=100, purchased_balance=10)
        alloc = allocate_credit_buckets(b, 50)
        assert alloc == {"trial_balance": 50}
        assert sum(alloc.values()) == 50

    def test_rejects_insufficient(self) -> None:
        b = make_balance(trial_balance=10, purchased_balance=5)
        with pytest.raises(InsufficientCreditsError) as exc:
            allocate_credit_buckets(b, 100)
        assert exc.value.requested == 100
        assert exc.value.available == 15

    def test_rejects_zero(self) -> None:
        b = make_balance()
        with pytest.raises(InvalidCreditAmountError):
            allocate_credit_buckets(b, 0)

    def test_does_not_mutate_balance(self) -> None:
        b = make_balance(
            trial_balance=10, promotional_balance=10,
            included_monthly_remaining=10, purchased_balance=10,
        )
        snapshot = (
            b.trial_balance, b.promotional_balance,
            b.included_monthly_remaining, b.purchased_balance,
            b.enterprise_balance, b.reserved_active,
        )
        allocate_credit_buckets(b, 7)
        assert (
            b.trial_balance, b.promotional_balance,
            b.included_monthly_remaining, b.purchased_balance,
            b.enterprise_balance, b.reserved_active,
        ) == snapshot

    def test_skips_empty_buckets(self) -> None:
        b = make_balance(trial_balance=0, promotional_balance=5)
        alloc = allocate_credit_buckets(b, 5)
        assert alloc == {"promotional_balance": 5}


class TestApplyBucketDebit:
    def test_updates_expected_fields(self) -> None:
        b = make_balance(trial_balance=10, promotional_balance=20)
        apply_bucket_debit(b, {"trial_balance": 5, "promotional_balance": 10})
        assert b.trial_balance == 5
        assert b.promotional_balance == 10

    def test_noop_with_empty_allocation(self) -> None:
        b = make_balance(trial_balance=10)
        apply_bucket_debit(b, {})
        assert b.trial_balance == 10

    def test_rejects_unknown_bucket(self) -> None:
        b = make_balance()
        with pytest.raises(CreditLedgerStateError):
            apply_bucket_debit(b, {"unknown_bucket": 1})

    def test_rejects_overdebit(self) -> None:
        b = make_balance(trial_balance=3)
        with pytest.raises(CreditLedgerStateError):
            apply_bucket_debit(b, {"trial_balance": 5})

    def test_rejects_negative_value(self) -> None:
        b = make_balance(trial_balance=10)
        with pytest.raises(InvalidCreditAmountError):
            apply_bucket_debit(b, {"trial_balance": -1})


class TestApplyBucketCredit:
    def test_updates_expected_field(self) -> None:
        b = make_balance(purchased_balance=10)
        apply_bucket_credit(b, "purchased_balance", 25)
        assert b.purchased_balance == 35

    def test_rejects_unknown_bucket(self) -> None:
        b = make_balance()
        with pytest.raises(CreditLedgerStateError):
            apply_bucket_credit(b, "bogus", 5)

    def test_rejects_zero(self) -> None:
        b = make_balance()
        with pytest.raises(InvalidCreditAmountError):
            apply_bucket_credit(b, "trial_balance", 0)


# --- Service-level async tests with FakeAsyncSession ----------------------


@pytest.fixture
def service() -> CreditLedgerService:
    return CreditLedgerService()


@pytest.fixture
def session() -> FakeAsyncSession:
    return FakeAsyncSession()


class TestReserveCredits:
    @pytest.mark.asyncio
    async def test_increases_reserved_active(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(
            trial_balance=100, promotional_balance=200,
            included_monthly_remaining=300, purchased_balance=400,
            enterprise_balance=500,
        )
        session.balances[balance.organization_id] = balance

        result = await service.reserve_credits(
            session, balance.organization_id, amount=150, job_id="job-1"
        )
        assert isinstance(result, CreditReservationResult)
        assert result.amount == 150
        assert result.status == LEDGER_STATUS_RESERVED
        assert balance.reserved_active == 150
        # available should drop from 1500 to 1350
        assert result.available_before == 1500
        assert result.available_after == 1350
        assert result.ledger_entry_id is not None
        # ledger entry was added
        ledger_entries = [o for o in session.added if isinstance(o, CreditLedgerEntry)]
        assert len(ledger_entries) == 1
        assert ledger_entries[0].entry_type == LEDGER_ENTRY_TYPE_RESERVE
        assert ledger_entries[0].status == LEDGER_STATUS_RESERVED
        assert ledger_entries[0].job_id == "job-1"
        assert ledger_entries[0].amount == 150
        # version was bumped
        assert balance.version == 2

    @pytest.mark.asyncio
    async def test_rejects_insufficient(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(trial_balance=10)
        session.balances[balance.organization_id] = balance
        with pytest.raises(InsufficientCreditsError):
            await service.reserve_credits(session, balance.organization_id, amount=100)
        # balance untouched
        assert balance.reserved_active == 0

    @pytest.mark.asyncio
    async def test_rejects_zero_amount(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        with pytest.raises(InvalidCreditAmountError):
            await service.reserve_credits(session, "org-1", amount=0)


class TestReleaseReservedCredits:
    @pytest.mark.asyncio
    async def test_decreases_reserved_active(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(
            trial_balance=1000, reserved_active=200,
        )
        session.balances[balance.organization_id] = balance

        result = await service.release_reserved_credits(
            session, balance.organization_id, amount=50, job_id="job-1"
        )
        assert isinstance(result, CreditReleaseResult)
        assert result.amount == 50
        assert result.status == LEDGER_STATUS_RELEASED
        assert balance.reserved_active == 150
        # available goes from 800 (1000-200) up to 850
        assert result.available_before == 800
        assert result.available_after == 850

    @pytest.mark.asyncio
    async def test_state_error_when_release_exceeds_reserved(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(trial_balance=1000, reserved_active=10)
        session.balances[balance.organization_id] = balance
        with pytest.raises(CreditLedgerStateError):
            await service.release_reserved_credits(
                session, balance.organization_id, amount=20
            )
        # unchanged
        assert balance.reserved_active == 10

    @pytest.mark.asyncio
    async def test_balance_not_found(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        with pytest.raises(CreditBalanceNotFoundError):
            await service.release_reserved_credits(
                session, "missing-org", amount=5
            )


class TestConsumeReservedCredits:
    @pytest.mark.asyncio
    async def test_debits_buckets_and_reserved(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(
            trial_balance=10,
            promotional_balance=20,
            included_monthly_remaining=30,
            purchased_balance=40,
            enterprise_balance=5000,
            reserved_active=200,
        )
        session.balances[balance.organization_id] = balance

        result = await service.consume_reserved_credits(
            session,
            balance.organization_id,
            amount=25,
            job_id="job-1",
            reason="ai.inference",
        )
        assert isinstance(result, CreditConsumptionResult)
        assert result.amount == 25
        assert result.status == LEDGER_STATUS_CONSUMED
        # Buckets debited in canonical order
        assert balance.trial_balance == 0
        assert balance.promotional_balance == 5
        assert balance.included_monthly_remaining == 30
        # reserved_active decremented and consumed_period incremented
        assert balance.reserved_active == 175
        assert balance.consumed_period == 25
        # bucket_debits recorded
        assert result.bucket_debits == {"trial_balance": 10, "promotional_balance": 15}

    @pytest.mark.asyncio
    async def test_state_error_when_consume_exceeds_reserved(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(trial_balance=100, reserved_active=5)
        session.balances[balance.organization_id] = balance
        with pytest.raises(CreditLedgerStateError):
            await service.consume_reserved_credits(
                session, balance.organization_id, amount=10
            )
        # unchanged
        assert balance.reserved_active == 5
        assert balance.consumed_period == 0


class TestGrantCredits:
    @pytest.mark.asyncio
    async def test_adds_to_requested_bucket(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        balance = make_balance(purchased_balance=10)
        session.balances[balance.organization_id] = balance

        result = await service.grant_credits(
            session,
            balance.organization_id,
            amount=50,
            bucket="purchased_balance",
            reason="manual.topup",
        )
        assert isinstance(result, CreditGrantResult)
        assert result.amount == 50
        assert result.bucket == "purchased_balance"
        assert result.status == LEDGER_STATUS_AVAILABLE
        assert balance.purchased_balance == 60
        # entry created
        ledger_entries = [o for o in session.added if isinstance(o, CreditLedgerEntry)]
        assert len(ledger_entries) == 1
        assert ledger_entries[0].entry_type == LEDGER_ENTRY_TYPE_GRANT
        assert ledger_entries[0].status == LEDGER_STATUS_AVAILABLE

    @pytest.mark.asyncio
    async def test_creates_balance_if_missing(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        result = await service.grant_credits(
            session, "new-org", amount=10, bucket="trial_balance"
        )
        assert result.bucket == "trial_balance"
        assert "new-org" in session.balances
        assert session.balances["new-org"].trial_balance == 10
        # version was bumped from None/0 baseline to at least 1 by _touch
        assert session.balances["new-org"].version is not None
        assert session.balances["new-org"].version >= 1
        # flush was called at least once (get_or_create + after add(entry))
        assert session.flushes >= 1

    @pytest.mark.asyncio
    async def test_rejects_unknown_bucket(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        with pytest.raises(CreditLedgerStateError):
            await service.grant_credits(
                session, "org-1", amount=10, bucket="not_a_real_bucket"
            )


class TestIdempotency:
    @pytest.mark.asyncio
    async def test_duplicate_idempotency_key_is_rejected_grant(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        # Prime the session with a pre-existing ledger entry that has the key.
        existing = CreditLedgerEntry(
            id=uuid.uuid4().hex,
            organization_id="org-1",
            entry_type=LEDGER_ENTRY_TYPE_GRANT,
            status=LEDGER_STATUS_AVAILABLE,
            amount=42,
            idempotency_key="dup-key",
            created_at=datetime.utcnow(),
        )
        session.idempotency_index["dup-key"] = existing

        with pytest.raises(DuplicateIdempotencyKeyError) as exc:
            await service.grant_credits(
                session, "org-1", amount=5, bucket="trial_balance",
                idempotency_key="dup-key",
            )
        assert exc.value.idempotency_key == "dup-key"
        assert exc.value.existing_entry_id == existing.id

    @pytest.mark.asyncio
    async def test_duplicate_idempotency_key_is_rejected_reserve(
        self, service: CreditLedgerService, session: FakeAsyncSession
    ) -> None:
        existing = CreditLedgerEntry(
            id=uuid.uuid4().hex,
            organization_id="org-1",
            entry_type=LEDGER_ENTRY_TYPE_RESERVE,
            status=LEDGER_STATUS_RESERVED,
            amount=10,
            idempotency_key="dup-key-2",
            created_at=datetime.utcnow(),
        )
        session.idempotency_index["dup-key-2"] = existing
        # Need a real balance for the reserve to be possible; create one
        balance = make_balance(trial_balance=100)
        session.balances[balance.organization_id] = balance
        with pytest.raises(DuplicateIdempotencyKeyError):
            await service.reserve_credits(
                session, "org-1", amount=5, idempotency_key="dup-key-2"
            )
        # balance untouched
        assert balance.reserved_active == 0


class TestNoStripeDependency:
    def test_module_does_not_import_stripe(self) -> None:
        # The service module must not depend on stripe at import time.
        import importlib
        mod = importlib.import_module("services.credit_ledger_service")
        src_path = Path(mod.__file__).read_text()
        assert "stripe" not in src_path.lower(), (
            "credit_ledger_service.py must not reference Stripe"
        )

    def test_schema_does_not_import_stripe(self) -> None:
        import importlib
        mod = importlib.import_module("schemas.credit_ledger_schema")
        src_path = Path(mod.__file__).read_text()
        assert "stripe" not in src_path.lower()


class TestConstants:
    def test_bucket_order_canonical(self) -> None:
        assert CREDIT_CONSUMPTION_BUCKET_ORDER == [
            "trial_balance",
            "promotional_balance",
            "included_monthly_remaining",
            "purchased_balance",
            "enterprise_balance",
        ]

    def test_grant_allowed_buckets_match_canonical(self) -> None:
        assert GRANT_ALLOWED_BUCKETS == set(CREDIT_CONSUMPTION_BUCKET_ORDER)

    def test_ledger_entry_types_constant_values(self) -> None:
        assert LEDGER_ENTRY_TYPE_GRANT in CREDIT_LEDGER_ENTRY_TYPES
        assert LEDGER_ENTRY_TYPE_RESERVE in CREDIT_LEDGER_ENTRY_TYPES
        assert LEDGER_ENTRY_TYPE_RELEASE in CREDIT_LEDGER_ENTRY_TYPES
        assert LEDGER_ENTRY_TYPE_CONSUME in CREDIT_LEDGER_ENTRY_TYPES

    def test_ledger_status_constants(self) -> None:
        assert LEDGER_STATUS_AVAILABLE in CREDIT_ENTRY_STATUSES
        assert LEDGER_STATUS_RESERVED in CREDIT_ENTRY_STATUSES
        assert LEDGER_STATUS_RELEASED in CREDIT_ENTRY_STATUSES
        assert LEDGER_STATUS_CONSUMED in CREDIT_ENTRY_STATUSES


class TestSchemas:
    def test_credit_grant_request_rejects_zero(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreditGrantRequest(organization_id="o", amount=0)

    def test_credit_reserve_request_minimal(self) -> None:
        r = CreditReserveRequest(organization_id="o", amount=10)
        assert r.amount == 10
        assert r.idempotency_key is None
        assert r.project_id is None

    def test_credit_consume_request_minimal(self) -> None:
        r = CreditConsumeRequest(organization_id="o", amount=3)
        assert r.amount == 3

    def test_credit_release_request_minimal(self) -> None:
        r = CreditReleaseRequest(organization_id="o", amount=4)
        assert r.amount == 4

    def test_credit_availability_read_defaults(self) -> None:
        r = CreditAvailabilityRead(organization_id="o")
        assert r.organization_id == "o"
        assert r.available_before == 0
        assert r.amount == 0

    def test_credit_ledger_operation_result_from_attrs(self) -> None:
        r = CreditLedgerOperationResult(
            organization_id="o",
            amount=10,
            status="ok",
        )
        assert r.organization_id == "o"
        assert r.bucket_debits is None

    def test_grant_buckets_tuple_matches_canonical(self) -> None:
        assert list(CREDIT_GRANT_BUCKETS) == CREDIT_CONSUMPTION_BUCKET_ORDER
