from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.billing import BillingAccount, CreditBalance, CreditLedgerEntry
from services.credit_ledger_service import (
    DuplicateIdempotencyKeyError,
    InsufficientCreditsError,
    CreditLedgerService,
    calculate_available_credits,
)
from tests.helpers.postgres_test_harness import (
    PostgresTestConfigError,
    require_validated_test_db_dsn,
    skip_if_postgres_test_unconfigured,
    temporary_postgres_billing_harness,
)


SKIP_INTEGRATION_BACKEND_CONTEXT = True

BILLING_LEDGER_TABLES = (
    "billing_accounts",
    "credit_balances",
    "credit_ledger_entries",
)


def _new_id() -> str:
    return uuid.uuid4().hex


def _skip_if_postgres_test_dsn_is_unavailable_or_unsafe() -> None:
    skip_if_postgres_test_unconfigured()
    try:
        require_validated_test_db_dsn()
    except PostgresTestConfigError as exc:
        pytest.skip(str(exc))


async def _create_billing_account(session, organization_id: str) -> BillingAccount:
    account = BillingAccount(
        id=_new_id(),
        organization_id=organization_id,
        legal_name=f"CID Test {organization_id[:8]}",
        billing_email=f"{organization_id[:8]}@example.test",
        country="ES",
    )
    session.add(account)
    await session.flush()
    return account


@pytest.mark.asyncio
async def test_credit_ledger_postgres_persists_grant_reserve_release_and_consume() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    organization_id = _new_id()
    project_id = _new_id()
    user_id = _new_id()
    job_for_release = _new_id()
    job_for_consume = _new_id()
    service = CreditLedgerService()

    async with temporary_postgres_billing_harness(BILLING_LEDGER_TABLES) as harness:
        async with harness.session_factory() as session:
            billing_account = await _create_billing_account(session, organization_id)

            grant = await service.grant_credits(
                session,
                organization_id,
                amount=100,
                bucket="purchased_balance",
                reason="integration.grant",
                idempotency_key=f"grant:{organization_id}",
            )
            reserve_for_release = await service.reserve_credits(
                session,
                organization_id,
                amount=30,
                project_id=project_id,
                user_id=user_id,
                job_id=job_for_release,
                reason="integration.reserve.release",
                idempotency_key=f"reserve-release:{organization_id}",
            )
            release = await service.release_reserved_credits(
                session,
                organization_id,
                amount=30,
                job_id=job_for_release,
                reason="integration.release",
                idempotency_key=f"release:{organization_id}",
            )
            reserve_for_consume = await service.reserve_credits(
                session,
                organization_id,
                amount=40,
                project_id=project_id,
                user_id=user_id,
                job_id=job_for_consume,
                reason="integration.reserve.consume",
                idempotency_key=f"reserve-consume:{organization_id}",
            )
            consume = await service.consume_reserved_credits(
                session,
                organization_id,
                amount=40,
                project_id=project_id,
                user_id=user_id,
                job_id=job_for_consume,
                reason="integration.consume",
                idempotency_key=f"consume:{organization_id}",
            )

            assert billing_account.organization_id == organization_id
            assert grant.available_after == 100
            assert reserve_for_release.available_after == 70
            assert release.available_after == 100
            assert reserve_for_consume.available_after == 60
            assert consume.available_after == 60
            assert consume.bucket_debits == {"purchased_balance": 40}

            await session.commit()

        async with harness.session_factory() as session:
            balance = (
                await session.execute(
                    select(CreditBalance).where(
                        CreditBalance.organization_id == organization_id
                    )
                )
            ).scalar_one()
            entries = (
                await session.execute(
                    select(CreditLedgerEntry)
                    .where(CreditLedgerEntry.organization_id == organization_id)
                )
            ).scalars().all()
            entries_by_key = {entry.idempotency_key: entry for entry in entries}

            assert balance.purchased_balance == 60
            assert balance.reserved_active == 0
            assert balance.consumed_period == 40
            assert calculate_available_credits(balance) == 60
            assert sorted(entry.entry_type for entry in entries) == sorted(
                [
                    "credit_grant",
                    "credit_reserve",
                    "credit_release",
                    "credit_reserve",
                    "credit_consume",
                ]
            )
            assert sorted(entry.amount for entry in entries) == [30, 30, 40, 40, 100]

            release_reservation = entries_by_key[f"reserve-release:{organization_id}"]
            consume_entry = entries_by_key[f"consume:{organization_id}"]
            assert release_reservation.project_id == project_id
            assert release_reservation.user_id == user_id
            assert release_reservation.job_id == job_for_release
            assert consume_entry.project_id == project_id
            assert consume_entry.job_id == job_for_consume
            assert consume_entry.status == "consumed"
            assert consume_entry.balance_after == 60


@pytest.mark.asyncio
async def test_credit_ledger_postgres_rejects_insufficient_duplicate_and_keeps_tenants_separate() -> None:
    _skip_if_postgres_test_dsn_is_unavailable_or_unsafe()
    org_a = _new_id()
    org_b = _new_id()
    project_a = _new_id()
    project_b = _new_id()
    service = CreditLedgerService()

    async with temporary_postgres_billing_harness(BILLING_LEDGER_TABLES) as harness:
        async with harness.session_factory() as session:
            account_a = await _create_billing_account(session, org_a)
            account_b = await _create_billing_account(session, org_b)

            await service.grant_credits(
                session,
                org_a,
                amount=25,
                bucket="trial_balance",
                reason="integration.org_a.grant",
                idempotency_key=f"grant:{org_a}",
            )
            await service.grant_credits(
                session,
                org_b,
                amount=90,
                bucket="enterprise_balance",
                reason="integration.org_b.grant",
                idempotency_key=f"grant:{org_b}",
            )
            await service.reserve_credits(
                session,
                org_b,
                amount=40,
                project_id=project_b,
                reason="integration.org_b.reserve",
                idempotency_key=f"reserve:{org_b}",
            )

            with pytest.raises(InsufficientCreditsError) as insufficient:
                await service.reserve_credits(
                    session,
                    org_a,
                    amount=30,
                    project_id=project_a,
                    reason="integration.org_a.insufficient",
                    idempotency_key=f"reserve-too-much:{org_a}",
                )
            assert insufficient.value.requested == 30
            assert insufficient.value.available == 25

            with pytest.raises(DuplicateIdempotencyKeyError) as duplicate:
                await service.grant_credits(
                    session,
                    org_b,
                    amount=5,
                    bucket="trial_balance",
                    reason="integration.duplicate",
                    idempotency_key=f"grant:{org_a}",
                )
            assert duplicate.value.idempotency_key == f"grant:{org_a}"

            await session.commit()

        async with harness.session_factory() as session:
            balance_a = (
                await session.execute(
                    select(CreditBalance).where(CreditBalance.organization_id == org_a)
                )
            ).scalar_one()
            balance_b = (
                await session.execute(
                    select(CreditBalance).where(CreditBalance.organization_id == org_b)
                )
            ).scalar_one()
            org_a_entry_count = (
                await session.execute(
                    select(func.count())
                    .select_from(CreditLedgerEntry)
                    .where(CreditLedgerEntry.organization_id == org_a)
                )
            ).scalar_one()
            org_b_entries = (
                await session.execute(
                    select(CreditLedgerEntry).where(
                        CreditLedgerEntry.organization_id == org_b
                    )
                )
            ).scalars().all()

            assert account_a.organization_id == org_a
            assert account_b.organization_id == org_b
            assert balance_a.trial_balance == 25
            assert balance_a.reserved_active == 0
            assert calculate_available_credits(balance_a) == 25
            assert balance_b.enterprise_balance == 90
            assert balance_b.reserved_active == 40
            assert calculate_available_credits(balance_b) == 50
            assert org_a_entry_count == 1
            assert len(org_b_entries) == 2
            assert {entry.project_id for entry in org_b_entries} == {None, project_b}
            assert all(entry.organization_id == org_b for entry in org_b_entries)
