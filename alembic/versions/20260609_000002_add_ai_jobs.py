"""add ai_jobs table

Revision ID: 20260609_000002_ai_jobs
Revises: 20260605_000001_billing
Create Date: 2026-06-09 00:00:02.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260609_000002_ai_jobs"
down_revision: Union[str, None] = "20260605_000001_billing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AI_JOB_STATUSES = (
    "created",
    "estimated",
    "credit_checked",
    "reserved",
    "queued",
    "running",
    "succeeded",
    "partial_succeeded",
    "failed",
    "cancel_requested",
    "cancelled",
    "consume_pending",
    "consumed",
    "release_pending",
    "released",
    "retry_pending",
    "expired",
)


def _enum_ck(column_name: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(repr(value) for value in values)
    return f"{column_name} IN ({quoted})"


def upgrade() -> None:
    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("operation_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), server_default="created", nullable=False),
        sa.Column("estimated_credits", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reserved_credits", sa.Integer(), server_default="0", nullable=False),
        sa.Column("consumed_credits", sa.Integer(), server_default="0", nullable=False),
        sa.Column("released_credits", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reservation_entry_id", sa.String(length=36), nullable=True),
        sa.Column("consume_entry_id", sa.String(length=36), nullable=True),
        sa.Column("release_entry_id", sa.String(length=36), nullable=True),
        sa.Column("idempotency_key", sa.String(length=120), nullable=True),
        sa.Column("provider_type", sa.String(length=50), nullable=True),
        sa.Column("provider_name", sa.String(length=100), nullable=True),
        sa.Column("provider_job_id", sa.String(length=255), nullable=True),
        sa.Column("workflow_id", sa.String(length=100), nullable=True),
        sa.Column("workflow_version", sa.String(length=100), nullable=True),
        sa.Column("workflow_hash", sa.String(length=255), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=True),
        sa.Column("input_asset_ids", sa.JSON(), nullable=True),
        sa.Column("output_asset_ids", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("parent_job_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("estimated_at", sa.DateTime(), nullable=True),
        sa.Column("credit_checked_at", sa.DateTime(), nullable=True),
        sa.Column("reserved_at", sa.DateTime(), nullable=True),
        sa.Column("queued_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("cancel_requested_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("consume_pending_at", sa.DateTime(), nullable=True),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("release_pending_at", sa.DateTime(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.CheckConstraint(
            _enum_ck("status", AI_JOB_STATUSES),
            name="ck_ai_jobs_status",
        ),
        sa.CheckConstraint(
            "estimated_credits >= 0 AND reserved_credits >= 0 AND "
            "consumed_credits >= 0 AND released_credits >= 0",
            name="ck_ai_jobs_non_negative_credits",
        ),
        sa.CheckConstraint(
            "attempt_number >= 1",
            name="ck_ai_jobs_attempt_number_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_ai_jobs_organization_id_created_at",
        "ai_jobs",
        ["organization_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_organization_id_status",
        "ai_jobs",
        ["organization_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_organization_id_project_id_created_at",
        "ai_jobs",
        ["organization_id", "project_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_organization_id_operation_type_created_at",
        "ai_jobs",
        ["organization_id", "operation_type", "created_at"],
        unique=False,
    )
    op.create_index("ix_ai_jobs_parent_job_id", "ai_jobs", ["parent_job_id"], unique=False)
    op.create_index(
        "ix_ai_jobs_reservation_entry_id",
        "ai_jobs",
        ["reservation_entry_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_consume_entry_id",
        "ai_jobs",
        ["consume_entry_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_release_entry_id",
        "ai_jobs",
        ["release_entry_id"],
        unique=False,
    )
    op.create_index(
        "ix_ai_jobs_provider_job_id",
        "ai_jobs",
        ["provider_job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_jobs_provider_job_id", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_release_entry_id", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_consume_entry_id", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_reservation_entry_id", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_parent_job_id", table_name="ai_jobs")
    op.drop_index(
        "ix_ai_jobs_organization_id_operation_type_created_at",
        table_name="ai_jobs",
    )
    op.drop_index(
        "ix_ai_jobs_organization_id_project_id_created_at",
        table_name="ai_jobs",
    )
    op.drop_index("ix_ai_jobs_organization_id_status", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_organization_id_created_at", table_name="ai_jobs")
    op.drop_table("ai_jobs")
