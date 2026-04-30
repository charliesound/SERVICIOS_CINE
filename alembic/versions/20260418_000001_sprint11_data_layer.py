"""sprint11 data layer job history

Revision ID: 20260418_000001
Revises: 20260416_000001
Create Date: 2026-04-18 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260418_000001"
down_revision = "20260416_000001"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("job_history"):
        op.create_table(
            "job_history",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("job_id", sa.String(length=36), nullable=False),
            sa.Column("event_type", sa.String(length=100), nullable=False),
            sa.Column("status_from", sa.String(length=50), nullable=True),
            sa.Column("status_to", sa.String(length=50), nullable=True),
            sa.Column("message", sa.String(length=500), nullable=True),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(length=36), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(
                ["job_id"], ["project_jobs.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["project_id"], ["projects.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = _index_names("job_history")

    if "ix_job_history_organization_id" not in indexes:
        op.create_index(
            "ix_job_history_organization_id",
            "job_history",
            ["organization_id"],
            unique=False,
        )
    if "ix_job_history_project_id" not in indexes:
        op.create_index(
            "ix_job_history_project_id",
            "job_history",
            ["project_id"],
            unique=False,
        )
    if "ix_job_history_job_id" not in indexes:
        op.create_index(
            "ix_job_history_job_id",
            "job_history",
            ["job_id"],
            unique=False,
        )
    if "ix_job_history_created_by" not in indexes:
        op.create_index(
            "ix_job_history_created_by",
            "job_history",
            ["created_by"],
            unique=False,
        )
    if "ix_job_history_org_project_created" not in indexes:
        op.create_index(
            "ix_job_history_org_project_created",
            "job_history",
            ["organization_id", "project_id", "created_at"],
            unique=False,
        )
    if "ix_job_history_job_created" not in indexes:
        op.create_index(
            "ix_job_history_job_created",
            "job_history",
            ["job_id", "created_at"],
            unique=False,
        )
    if "ix_job_history_event_type_created" not in indexes:
        op.create_index(
            "ix_job_history_event_type_created",
            "job_history",
            ["event_type", "created_at"],
            unique=False,
        )


def downgrade() -> None:
    if not _table_exists("job_history"):
        return

    indexes = _index_names("job_history")
    for index_name in (
        "ix_job_history_event_type_created",
        "ix_job_history_job_created",
        "ix_job_history_org_project_created",
        "ix_job_history_created_by",
        "ix_job_history_job_id",
        "ix_job_history_project_id",
        "ix_job_history_organization_id",
    ):
        if index_name in indexes:
            op.drop_index(index_name, table_name="job_history")

    op.drop_table("job_history")
