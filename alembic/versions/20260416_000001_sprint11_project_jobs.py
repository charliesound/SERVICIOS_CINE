"""sprint11 project jobs and asset tracking

Revision ID: 20260416_000001
Revises: 20260414_000001
Create Date: 2026-04-16 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260416_000001"
down_revision = "20260414_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("project_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("result_data", sa.String(length=16777215), nullable=True),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_project_jobs_org_project_created",
        "project_jobs",
        ["organization_id", "project_id", "created_at"],
        unique=False,
    )

    op.add_column(
        "media_assets",
        sa.Column("job_id", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "media_assets",
        sa.Column("asset_source", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "media_assets",
        sa.Column("content_ref", sa.String(length=2000), nullable=True),
    )
    op.add_column(
        "media_assets",
        sa.Column("metadata_json", sa.Text(), nullable=True),
    )
    op.add_column(
        "media_assets",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_media_assets_job_id",
        "media_assets",
        ["job_id"],
        unique=False,
    )
    op.alter_column(
        "media_assets",
        "storage_source_id",
        existing_type=sa.String(length=36),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "media_assets",
        "storage_source_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.drop_index("ix_media_assets_job_id", table_name="media_assets")
    op.drop_column("media_assets", "created_at")
    op.drop_column("media_assets", "metadata_json")
    op.drop_column("media_assets", "content_ref")
    op.drop_column("media_assets", "asset_source")
    op.drop_column("media_assets", "job_id")
    op.drop_index("ix_project_jobs_org_project_created", table_name="project_jobs")
    op.drop_table("project_jobs")
