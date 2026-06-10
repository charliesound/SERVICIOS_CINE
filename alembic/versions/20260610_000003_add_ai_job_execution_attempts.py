"""add ai_job_execution_attempts table

Revision ID: 20260610_000003_ai_job_execution_attempts
Revises: 20260609_000002_ai_jobs
Create Date: 2026-06-10 00:00:03.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260610_000003_ai_job_execution_attempts"
down_revision: Union[str, None] = "20260609_000002_ai_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ATTEMPT_STATUSES = (
    "in_progress",
    "succeeded",
    "failed",
    "cancelled",
    "conflicted",
)

ATTEMPT_MODES = (
    "success",
    "failure",
    "cancel",
)


def _enum_ck(column_name: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(repr(value) for value in values)
    return f"{column_name} IN ({quoted})"


def upgrade() -> None:
    op.create_table(
        "ai_job_execution_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("execution_attempt_id", sa.String(length=255), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="in_progress", nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("fingerprint_version", sa.String(length=10), server_default="v1", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("requested_by", sa.String(length=100), nullable=True),
        sa.Column("result_status", sa.String(length=40), nullable=True),
        sa.Column("consume_entry_id", sa.String(length=36), nullable=True),
        sa.Column("release_entry_id", sa.String(length=36), nullable=True),
        sa.Column("consumed_credits", sa.Integer(), nullable=True),
        sa.Column("released_credits", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message_safe", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            _enum_ck("mode", ATTEMPT_MODES),
            name="ck_ai_job_execution_attempts_mode",
        ),
        sa.CheckConstraint(
            _enum_ck("status", ATTEMPT_STATUSES),
            name="ck_ai_job_execution_attempts_status",
        ),
        sa.CheckConstraint(
            "consumed_credits IS NULL OR consumed_credits > 0",
            name="ck_ai_job_execution_attempts_consumed_credits_positive",
        ),
        sa.CheckConstraint(
            "released_credits IS NULL OR released_credits > 0",
            name="ck_ai_job_execution_attempts_released_credits_positive",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_ai_job_execution_attempts_finished_after_started",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["ai_jobs.id"],
            name="fk_ai_job_execution_attempts_job_id_ai_jobs",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "job_id",
            "execution_attempt_id",
            name="uq_ai_job_execution_attempts_org_job_attempt",
        ),
    )

    op.create_index(
        "ix_ai_job_execution_attempts_org_job",
        "ai_job_execution_attempts",
        ["organization_id", "job_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_job_execution_attempts_org_job_created_at",
        "ai_job_execution_attempts",
        ["organization_id", "job_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_job_execution_attempts_org_status_created_at",
        "ai_job_execution_attempts",
        ["organization_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_job_execution_attempts_org_attempt",
        "ai_job_execution_attempts",
        ["organization_id", "execution_attempt_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_job_execution_attempts_org_attempt", table_name="ai_job_execution_attempts")
    op.drop_index(
        "ix_ai_job_execution_attempts_org_status_created_at",
        table_name="ai_job_execution_attempts",
    )
    op.drop_index(
        "ix_ai_job_execution_attempts_org_job_created_at",
        table_name="ai_job_execution_attempts",
    )
    op.drop_index("ix_ai_job_execution_attempts_org_job", table_name="ai_job_execution_attempts")
    op.drop_table("ai_job_execution_attempts")
