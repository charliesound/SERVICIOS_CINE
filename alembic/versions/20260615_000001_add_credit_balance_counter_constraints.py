"""add credit balance counter constraints

Revision ID: 20260615_000001_credit_balance_counters
Revises: 20260610_000003_ai_job_execution_attempts
Create Date: 2026-06-15 00:00:01.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "20260615_000001_credit_balance_counters"
down_revision: Union[str, None] = "20260610_000003_ai_job_execution_attempts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONSTRAINT_NAME = "ck_credit_balances_non_negative_counters"


def upgrade() -> None:
    op.create_check_constraint(
        CONSTRAINT_NAME,
        "credit_balances",
        "consumed_period >= 0 AND expired_total >= 0 AND "
        "refunded_total >= 0 AND version >= 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        CONSTRAINT_NAME,
        "credit_balances",
        type_="check",
    )
