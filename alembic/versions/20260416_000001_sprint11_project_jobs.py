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
    # Ensure media_assets table exists before adding columns (missing from initial schema)
    # Note: index=True on columns creates indexes automatically, so we don't duplicate
    op.create_table(
        "media_assets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("project_id", sa.String(length=36), nullable=False, index=True),
        sa.Column("storage_source_id", sa.String(length=36), nullable=True),
        sa.Column("watch_path_id", sa.String(length=36), nullable=True),
        sa.Column("ingest_scan_id", sa.String(length=36), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("relative_path", sa.String(length=1000), nullable=True),
        sa.Column("canonical_path", sa.String(length=2000), nullable=True),
        sa.Column("file_extension", sa.String(length=10), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("asset_type", sa.String(length=20), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("created_by", sa.String(length=36), nullable=True),
    )
    # Indexes created automatically by index=True on columns above

    # Create project_jobs table
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


def downgrade() -> None:
    # Drop project_jobs first
    op.drop_index("ix_project_jobs_org_project_created", table_name="project_jobs")
    op.drop_table("project_jobs")

    # Drop media_assets table (indexes auto-dropped with table)
    op.drop_table("media_assets")
