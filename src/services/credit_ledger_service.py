from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.billing import (
    CREDIT_LEDGER_ENTRY_TYPES,
    CREDIT_ENTRY_STATUSES,
    CreditBalance,
    CreditLedgerEntry,
)


CREDIT_CONSUMPTION_BUCKET_ORDER = [
    "trial_balance",
    "promotional_balance",
    "included_monthly_remaining",
    "purchased_balance",
    "enterprise_balance",
]

GRANT_ALLOWED_BUCKETS = set(CREDIT_CONSUMPTION_BUCKET_ORDER)

LEDGER_ENTRY_TYPE_GRANT = "credit_grant"
LEDGER_ENTRY_TYPE_RESERVE = "credit_reserve"
LEDGER_ENTRY_TYPE_RELEASE = "credit_release"
LEDGER_ENTRY_TYPE_CONSUME = "credit_consume"

LEDGER_STATUS_AVAILABLE = "available"
LEDGER_STATUS_RESERVED = "reserved"
LEDGER_STATUS_RELEASED = "available"
LEDGER_STATUS_CONSUMED = "consumed"

__all__ = [
    "CREDIT_CONSUMPTION_BUCKET_ORDER",
    "GRANT_ALLOWED_BUCKETS",
    "LEDGER_ENTRY_TYPE_GRANT",
    "LEDGER_ENTRY_TYPE_RESERVE",
    "LEDGER_ENTRY_TYPE_RELEASE",
    "LEDGER_ENTRY_TYPE_CONSUME",
    "LEDGER_STATUS_AVAILABLE",
    "LEDGER_STATUS_RESERVED",
    "LEDGER_STATUS_RELEASED",
    "LEDGER_STATUS_CONSUMED",
    "CreditLedgerError",
    "CreditBalanceNotFoundError",
    "InsufficientCreditsError",
    "CreditReservationNotFoundError",
    "DuplicateIdempotencyKeyError",
    "InvalidCreditAmountError",
    "CreditLedgerStateError",
    "CreditAvailabilityResult",
    "CreditReservationResult",
    "CreditConsumptionResult",
    "CreditReleaseResult",
    "CreditGrantResult",
    "calculate_available_credits",
    "validate_positive_amount",
    "allocate_credit_buckets",
    "apply_bucket_debit",
    "apply_bucket_credit",
    "CreditLedgerService",
]


class CreditLedgerError(Exception):
    """Base error for credit ledger operations."""


class CreditBalanceNotFoundError(CreditLedgerError):
    """Raised when a CreditBalance row cannot be located."""


class InsufficientCreditsError(CreditLedgerError):
    """Raised when available credits are insufficient for a reservation/consumption."""

    def __init__(self, requested: int, available: int) -> None:
        super().__init__(
            "Insufficient credits: requested {0}, available {1}".format(requested, available)
        )
        self.requested = requested
        self.available = available


class CreditReservationNotFoundError(CreditLedgerError):
    """Raised when a referenced reservation cannot be located."""


class DuplicateIdempotencyKeyError(CreditLedgerError):
    """Raised when an idempotency_key has already been used."""

    def __init__(self, idempotency_key: str, existing_entry_id: Optional[str] = None) -> None:
        super().__init__(
            "Duplicate idempotency_key: {0}".format(idempotency_key)
        )
        self.idempotency_key = idempotency_key
        self.existing_entry_id = existing_entry_id


class InvalidCreditAmountError(CreditLedgerError):
    """Raised when amount is not a strictly positive integer."""


class CreditLedgerStateError(CreditLedgerError):
    """Raised when the ledger state does not allow the requested operation."""


@dataclass
class CreditAvailabilityResult:
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = ""
    message: str = ""


@dataclass
class CreditReservationResult:
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = LEDGER_STATUS_RESERVED
    message: str = ""


@dataclass
class CreditConsumptionResult:
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = LEDGER_STATUS_CONSUMED
    message: str = ""
    bucket_debits: dict[str, int] = field(default_factory=dict)


@dataclass
class CreditReleaseResult:
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = LEDGER_STATUS_RELEASED
    message: str = ""


@dataclass
class CreditGrantResult:
    organization_id: str
    balance_id: Optional[str] = None
    available_before: int = 0
    available_after: int = 0
    amount: int = 0
    ledger_entry_id: Optional[str] = None
    status: str = LEDGER_STATUS_AVAILABLE
    message: str = ""
    bucket: str = ""


def calculate_available_credits(balance: CreditBalance) -> int:
    """Compute available credits as the sum of consumption buckets minus reservations."""
    if balance is None:
        return 0
    consumable = (
        int(getattr(balance, "trial_balance", 0) or 0)
        + int(getattr(balance, "promotional_balance", 0) or 0)
        + int(getattr(balance, "included_monthly_remaining", 0) or 0)
        + int(getattr(balance, "purchased_balance", 0) or 0)
        + int(getattr(balance, "enterprise_balance", 0) or 0)
    )
    reserved = int(getattr(balance, "reserved_active", 0) or 0)
    return consumable - reserved


def validate_positive_amount(amount: int) -> None:
    """Reject zero or negative amounts; integer must be strictly positive."""
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise InvalidCreditAmountError("amount must be an integer")
    if amount <= 0:
        raise InvalidCreditAmountError(
            "amount must be > 0 (got {0})".format(amount)
        )


def allocate_credit_buckets(balance: CreditBalance, amount: int) -> dict[str, int]:
    """Plan how much to debit each bucket to cover `amount`, in canonical order.

    Returns a dict {bucket: amount} with non-negative integers that sum to
    exactly `amount` (or less if not enough balance). Does NOT mutate balance.

    Raises InsufficientCreditsError if available balance is below `amount`.
    """
    validate_positive_amount(amount)
    available_total = (
        int(getattr(balance, "trial_balance", 0) or 0)
        + int(getattr(balance, "promotional_balance", 0) or 0)
        + int(getattr(balance, "included_monthly_remaining", 0) or 0)
        + int(getattr(balance, "purchased_balance", 0) or 0)
        + int(getattr(balance, "enterprise_balance", 0) or 0)
    )
    if available_total < amount:
        raise InsufficientCreditsError(
            requested=amount, available=available_total
        )

    remaining = amount
    allocation: dict[str, int] = {}
    for bucket in CREDIT_CONSUMPTION_BUCKET_ORDER:
        if remaining <= 0:
            break
        bucket_value = int(getattr(balance, bucket, 0) or 0)
        if bucket_value <= 0:
            continue
        take = bucket_value if bucket_value < remaining else remaining
        allocation[bucket] = take
        remaining -= take
    if remaining > 0:
        raise InsufficientCreditsError(
            requested=amount, available=available_total - remaining
        )
    return allocation


def apply_bucket_debit(balance: CreditBalance, allocation: dict[str, int]) -> None:
    """Apply pre-computed debits to each bucket. Mutates balance in-place."""
    if not allocation:
        return
    for bucket, value in allocation.items():
        if bucket not in CREDIT_CONSUMPTION_BUCKET_ORDER:
            raise CreditLedgerStateError(
                "Cannot debit unknown bucket: {0}".format(bucket)
            )
        if value < 0:
            raise InvalidCreditAmountError(
                "debit amount must be >= 0 (got {0} for {1})".format(value, bucket)
            )
        current = int(getattr(balance, bucket, 0) or 0)
        if value > current:
            raise CreditLedgerStateError(
                "Cannot debit {0} from bucket {1}: current {2}".format(
                    value, bucket, current
                )
            )
        setattr(balance, bucket, current - value)


def apply_bucket_credit(balance: CreditBalance, bucket: str, amount: int) -> None:
    """Credit a single bucket by `amount`. Mutates balance in-place."""
    validate_positive_amount(amount)
    if bucket not in GRANT_ALLOWED_BUCKETS:
        raise CreditLedgerStateError("Unknown grant bucket: {0}".format(bucket))
    current = int(getattr(balance, bucket, 0) or 0)
    setattr(balance, bucket, current + amount)


class CreditLedgerService:
    """Async service that manages credit balances and the append-only ledger.

    The service does NOT commit sessions; the caller is responsible for the
    transactional boundary (commit/rollback).
    """

    def __init__(self) -> None:
        self._now = datetime.utcnow

    # ----- internal helpers -------------------------------------------------

    def _new_id(self) -> str:
        return uuid.uuid4().hex

    async def _get_existing_entry_by_idempotency_key(
        self, session: AsyncSession, idempotency_key: Optional[str]
    ) -> Optional[CreditLedgerEntry]:
        if not idempotency_key:
            return None
        stmt = select(CreditLedgerEntry).where(
            CreditLedgerEntry.idempotency_key == idempotency_key
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_balance(
        self, session: AsyncSession, organization_id: str
    ) -> Optional[CreditBalance]:
        stmt = select(CreditBalance).where(
            CreditBalance.organization_id == organization_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    def _extract_reservation_entry_id(
        self, metadata: Optional[dict[str, Any]]
    ) -> Optional[str]:
        if not metadata or "reservation_entry_id" not in metadata:
            return None
        reservation_entry_id = str(metadata.get("reservation_entry_id") or "").strip()
        if not reservation_entry_id:
            raise CreditReservationNotFoundError("reservation_entry_id is required")
        return reservation_entry_id

    async def _get_reservation_entry(
        self,
        session: AsyncSession,
        organization_id: str,
        reservation_entry_id: str,
    ) -> CreditLedgerEntry:
        stmt = select(CreditLedgerEntry).where(
            CreditLedgerEntry.id == reservation_entry_id,
            CreditLedgerEntry.organization_id == organization_id,
        )
        result = await session.execute(stmt)
        reservation = result.scalar_one_or_none()
        if reservation is None:
            raise CreditReservationNotFoundError(
                "Reservation {0} not found for organization {1}".format(
                    reservation_entry_id, organization_id
                )
            )
        return reservation

    async def _get_reservation_settlements(
        self,
        session: AsyncSession,
        organization_id: str,
        reservation_entry_id: str,
    ) -> list[CreditLedgerEntry]:
        stmt = select(CreditLedgerEntry).where(
            CreditLedgerEntry.organization_id == organization_id
        )
        result = await session.execute(stmt)
        entries = list(result.scalars().all())
        settlements: list[CreditLedgerEntry] = []
        for entry in entries:
            if entry.entry_type not in {
                LEDGER_ENTRY_TYPE_CONSUME,
                LEDGER_ENTRY_TYPE_RELEASE,
            }:
                continue
            metadata = getattr(entry, "metadata_json", None) or {}
            entry_reservation_id = str(metadata.get("reservation_entry_id") or "").strip()
            if entry_reservation_id == reservation_entry_id:
                settlements.append(entry)
        return settlements

    async def _validate_linked_reservation(
        self,
        session: AsyncSession,
        organization_id: str,
        reservation_entry_id: str,
        amount: int,
        *,
        job_id: Optional[str],
        settlement_action: str,
    ) -> CreditLedgerEntry:
        reservation = await self._get_reservation_entry(
            session=session,
            organization_id=organization_id,
            reservation_entry_id=reservation_entry_id,
        )
        if reservation.entry_type != LEDGER_ENTRY_TYPE_RESERVE:
            raise CreditLedgerStateError(
                "Reservation {0} is not a reserve entry".format(reservation_entry_id)
            )
        if reservation.status != LEDGER_STATUS_RESERVED:
            raise CreditLedgerStateError(
                "Reservation {0} is not in reserved status".format(
                    reservation_entry_id
                )
            )
        reservation_amount = int(reservation.amount or 0)
        if reservation_amount <= 0:
            raise CreditLedgerStateError(
                "Reservation {0} has invalid amount".format(reservation_entry_id)
            )
        reservation_job_id = getattr(reservation, "job_id", None)
        if job_id is not None and job_id != reservation_job_id:
            raise CreditLedgerStateError(
                "Reservation {0} does not match job_id {1}".format(
                    reservation_entry_id, job_id
                )
            )
        if amount > reservation_amount:
            raise CreditLedgerStateError(
                "Cannot {0} {1} credits: reservation amount is {2}".format(
                    settlement_action, amount, reservation_amount
                )
            )
        settlements = await self._get_reservation_settlements(
            session=session,
            organization_id=organization_id,
            reservation_entry_id=reservation_entry_id,
        )
        if settlements:
            raise CreditLedgerStateError(
                "Reservation {0} already has a settlement".format(
                    reservation_entry_id
                )
            )
        return reservation

    def _build_settlement_metadata(
        self,
        metadata: Optional[dict[str, Any]],
        reservation: CreditLedgerEntry,
        reservation_entry_id: str,
        amount: int,
        settlement_action: str,
        job_id: Optional[str],
    ) -> dict[str, Any]:
        settlement_metadata: dict[str, Any] = dict(metadata or {})
        settlement_job_id = job_id or getattr(reservation, "job_id", None)
        settlement_metadata.update(
            {
                "reservation_entry_id": reservation_entry_id,
                "reservation_amount": int(reservation.amount or 0),
                "settlement_amount": amount,
                "settlement_action": settlement_action,
            }
        )
        if settlement_job_id is not None:
            settlement_metadata["job_id"] = settlement_job_id
        return settlement_metadata

    def _touch(self, balance: CreditBalance) -> None:
        balance.last_updated_at = self._now()
        balance.version = int(balance.version or 0) + 1

    def _build_entry(
        self,
        organization_id: str,
        entry_type: str,
        status: str,
        amount: int,
        *,
        balance_after: Optional[int] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        credit_package_purchase_id: Optional[str] = None,
        reason: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        reserved_until: Optional[datetime] = None,
        released_at: Optional[datetime] = None,
        consumed_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> CreditLedgerEntry:
        if entry_type not in CREDIT_LEDGER_ENTRY_TYPES:
            raise CreditLedgerStateError(
                "Unknown entry_type: {0}".format(entry_type)
            )
        if status not in CREDIT_ENTRY_STATUSES:
            raise CreditLedgerStateError(
                "Unknown entry status: {0}".format(status)
            )
        entry = CreditLedgerEntry(
            id=self._new_id(),
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            job_id=job_id,
            subscription_id=subscription_id,
            credit_package_purchase_id=credit_package_purchase_id,
            entry_type=entry_type,
            status=status,
            amount=amount,
            balance_after=balance_after,
            reason=reason,
            idempotency_key=idempotency_key,
            expires_at=expires_at,
            reserved_until=reserved_until,
            released_at=released_at,
            consumed_at=consumed_at,
            metadata_json=metadata,
            created_at=self._now(),
        )
        return entry

    # ----- public service methods ------------------------------------------

    async def get_balance(
        self, session: AsyncSession, organization_id: str
    ) -> Optional[CreditBalance]:
        return await self._get_balance(session, organization_id)

    async def get_or_create_balance(
        self, session: AsyncSession, organization_id: str
    ) -> CreditBalance:
        balance = await self._get_balance(session, organization_id)
        if balance is not None:
            return balance
        balance = CreditBalance(
            id=self._new_id(),
            organization_id=organization_id,
            last_updated_at=self._now(),
        )
        session.add(balance)
        await session.flush()
        return balance

    async def get_available_credits(
        self, session: AsyncSession, organization_id: str
    ) -> CreditAvailabilityResult:
        balance = await self._get_balance(session, organization_id)
        if balance is None:
            return CreditAvailabilityResult(
                organization_id=organization_id,
                available_before=0,
                available_after=0,
                status="no_balance",
                message="No CreditBalance found for organization",
            )
        available = calculate_available_credits(balance)
        return CreditAvailabilityResult(
            organization_id=organization_id,
            balance_id=getattr(balance, "id", None),
            available_before=available,
            available_after=available,
            amount=available,
            status="ok",
            message="Available credits computed",
        )

    async def grant_credits(
        self,
        session: AsyncSession,
        organization_id: str,
        amount: int,
        bucket: str = "promotional_balance",
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreditGrantResult:
        validate_positive_amount(amount)
        if bucket not in GRANT_ALLOWED_BUCKETS:
            raise CreditLedgerStateError("Unknown grant bucket: {0}".format(bucket))

        existing = await self._get_existing_entry_by_idempotency_key(
            session, idempotency_key
        )
        if existing is not None:
            raise DuplicateIdempotencyKeyError(
                idempotency_key=idempotency_key or "",
                existing_entry_id=getattr(existing, "id", None),
            )

        balance = await self.get_or_create_balance(session, organization_id)
        available_before = calculate_available_credits(balance)
        apply_bucket_credit(balance, bucket, amount)
        available_after = calculate_available_credits(balance)
        self._touch(balance)

        entry = self._build_entry(
            organization_id=organization_id,
            entry_type=LEDGER_ENTRY_TYPE_GRANT,
            status=LEDGER_STATUS_AVAILABLE,
            amount=amount,
            balance_after=available_after,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=metadata,
        )
        session.add(entry)
        await session.flush()

        return CreditGrantResult(
            organization_id=organization_id,
            balance_id=balance.id,
            available_before=available_before,
            available_after=available_after,
            amount=amount,
            ledger_entry_id=entry.id,
            status=LEDGER_STATUS_AVAILABLE,
            message="Granted {0} credits to {1}".format(amount, bucket),
            bucket=bucket,
        )

    async def reserve_credits(
        self,
        session: AsyncSession,
        organization_id: str,
        amount: int,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreditReservationResult:
        validate_positive_amount(amount)

        existing = await self._get_existing_entry_by_idempotency_key(
            session, idempotency_key
        )
        if existing is not None:
            raise DuplicateIdempotencyKeyError(
                idempotency_key=idempotency_key or "",
                existing_entry_id=getattr(existing, "id", None),
            )

        balance = await self.get_or_create_balance(session, organization_id)
        available_before = calculate_available_credits(balance)
        if available_before < amount:
            raise InsufficientCreditsError(
                requested=amount, available=available_before
            )

        balance.reserved_active = int(balance.reserved_active or 0) + amount
        available_after = calculate_available_credits(balance)
        self._touch(balance)

        entry = self._build_entry(
            organization_id=organization_id,
            entry_type=LEDGER_ENTRY_TYPE_RESERVE,
            status=LEDGER_STATUS_RESERVED,
            amount=amount,
            balance_after=available_after,
            project_id=project_id,
            user_id=user_id,
            job_id=job_id,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=metadata,
        )
        session.add(entry)
        await session.flush()

        return CreditReservationResult(
            organization_id=organization_id,
            balance_id=balance.id,
            available_before=available_before,
            available_after=available_after,
            amount=amount,
            ledger_entry_id=entry.id,
            status=LEDGER_STATUS_RESERVED,
            message="Reserved {0} credits".format(amount),
        )

    async def release_reserved_credits(
        self,
        session: AsyncSession,
        organization_id: str,
        amount: int,
        job_id: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreditReleaseResult:
        validate_positive_amount(amount)

        existing = await self._get_existing_entry_by_idempotency_key(
            session, idempotency_key
        )
        if existing is not None:
            raise DuplicateIdempotencyKeyError(
                idempotency_key=idempotency_key or "",
                existing_entry_id=getattr(existing, "id", None),
            )

        reservation_entry_id = self._extract_reservation_entry_id(metadata)
        reservation: Optional[CreditLedgerEntry] = None
        if reservation_entry_id is not None:
            reservation = await self._validate_linked_reservation(
                session=session,
                organization_id=organization_id,
                reservation_entry_id=reservation_entry_id,
                amount=amount,
                job_id=job_id,
                settlement_action="release",
            )

        balance = await self._get_balance(session, organization_id)
        if balance is None:
            raise CreditBalanceNotFoundError(
                "No CreditBalance for organization {0}".format(organization_id)
            )
        reserved_active = int(balance.reserved_active or 0)
        if reserved_active < amount:
            raise CreditLedgerStateError(
                "Cannot release {0} credits: reserved_active is {1}".format(
                    amount, reserved_active
                )
            )

        entry_metadata = metadata
        entry_job_id = job_id
        if reservation_entry_id is not None and reservation is not None:
            entry_metadata = self._build_settlement_metadata(
                metadata=metadata,
                reservation=reservation,
                reservation_entry_id=reservation_entry_id,
                amount=amount,
                settlement_action="release",
                job_id=job_id,
            )
            entry_job_id = job_id or getattr(reservation, "job_id", None)

        available_before = calculate_available_credits(balance)
        balance.reserved_active = reserved_active - amount
        available_after = calculate_available_credits(balance)
        self._touch(balance)

        entry = self._build_entry(
            organization_id=organization_id,
            entry_type=LEDGER_ENTRY_TYPE_RELEASE,
            status=LEDGER_STATUS_RELEASED,
            amount=amount,
            balance_after=available_after,
            job_id=entry_job_id,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=entry_metadata,
            released_at=self._now(),
        )
        session.add(entry)
        await session.flush()

        return CreditReleaseResult(
            organization_id=organization_id,
            balance_id=balance.id,
            available_before=available_before,
            available_after=available_after,
            amount=amount,
            ledger_entry_id=entry.id,
            status=LEDGER_STATUS_RELEASED,
            message="Released {0} reserved credits".format(amount),
        )

    async def consume_reserved_credits(
        self,
        session: AsyncSession,
        organization_id: str,
        amount: int,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreditConsumptionResult:
        validate_positive_amount(amount)

        existing = await self._get_existing_entry_by_idempotency_key(
            session, idempotency_key
        )
        if existing is not None:
            raise DuplicateIdempotencyKeyError(
                idempotency_key=idempotency_key or "",
                existing_entry_id=getattr(existing, "id", None),
            )

        reservation_entry_id = self._extract_reservation_entry_id(metadata)
        reservation: Optional[CreditLedgerEntry] = None
        if reservation_entry_id is not None:
            reservation = await self._validate_linked_reservation(
                session=session,
                organization_id=organization_id,
                reservation_entry_id=reservation_entry_id,
                amount=amount,
                job_id=job_id,
                settlement_action="consume",
            )

        balance = await self._get_balance(session, organization_id)
        if balance is None:
            raise CreditBalanceNotFoundError(
                "No CreditBalance for organization {0}".format(organization_id)
            )
        reserved_active = int(balance.reserved_active or 0)
        if reserved_active < amount:
            raise CreditLedgerStateError(
                "Cannot consume {0} credits: reserved_active is {1}".format(
                    amount, reserved_active
                )
            )

        entry_metadata = metadata
        entry_job_id = job_id
        if reservation_entry_id is not None and reservation is not None:
            entry_metadata = self._build_settlement_metadata(
                metadata=metadata,
                reservation=reservation,
                reservation_entry_id=reservation_entry_id,
                amount=amount,
                settlement_action="consume",
                job_id=job_id,
            )
            entry_job_id = job_id or getattr(reservation, "job_id", None)

        available_before = calculate_available_credits(balance)
        allocation = allocate_credit_buckets(balance, amount)
        apply_bucket_debit(balance, allocation)
        balance.reserved_active = reserved_active - amount
        balance.consumed_period = int(balance.consumed_period or 0) + amount
        available_after = calculate_available_credits(balance)
        self._touch(balance)

        entry = self._build_entry(
            organization_id=organization_id,
            entry_type=LEDGER_ENTRY_TYPE_CONSUME,
            status=LEDGER_STATUS_CONSUMED,
            amount=amount,
            balance_after=available_after,
            project_id=project_id,
            user_id=user_id,
            job_id=entry_job_id,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=entry_metadata,
            consumed_at=self._now(),
        )
        session.add(entry)
        await session.flush()

        return CreditConsumptionResult(
            organization_id=organization_id,
            balance_id=balance.id,
            available_before=available_before,
            available_after=available_after,
            amount=amount,
            ledger_entry_id=entry.id,
            status=LEDGER_STATUS_CONSUMED,
            message="Consumed {0} reserved credits".format(amount),
            bucket_debits=allocation,
        )
