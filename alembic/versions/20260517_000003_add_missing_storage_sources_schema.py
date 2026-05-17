"""add missing storage sources schema

Revision ID: 20260517_000003
Revises: 20260517_000002
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260517_000003"
down_revision: Union[str, None] = "20260517_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "storage_sources"):
        op.create_table(
            "storage_sources",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("source_type", sa.String(length=50), nullable=False, server_default="local"),
            sa.Column("mount_path", sa.String(length=1000), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("created_by", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "storage_sources", "ix_storage_sources_organization_id"):
        op.create_index("ix_storage_sources_organization_id", "storage_sources", ["organization_id"], unique=False)
    if not _index_exists(bind, "storage_sources", "ix_storage_sources_project_id"):
        op.create_index("ix_storage_sources_project_id", "storage_sources", ["project_id"], unique=False)
    if not _index_exists(bind, "storage_sources", "ix_storage_sources_source_type"):
        op.create_index("ix_storage_sources_source_type", "storage_sources", ["source_type"], unique=False)
    if not _index_exists(bind, "storage_sources", "ix_storage_sources_status"):
        op.create_index("ix_storage_sources_status", "storage_sources", ["status"], unique=False)
    if not _index_exists(bind, "storage_sources", "ix_storage_sources_organization_project"):
        op.create_index(
            "ix_storage_sources_organization_project",
            "storage_sources",
            ["organization_id", "project_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "storage_sources"):
        if _index_exists(bind, "storage_sources", "ix_storage_sources_organization_project"):
            op.drop_index("ix_storage_sources_organization_project", table_name="storage_sources")
        if _index_exists(bind, "storage_sources", "ix_storage_sources_status"):
            op.drop_index("ix_storage_sources_status", table_name="storage_sources")
        if _index_exists(bind, "storage_sources", "ix_storage_sources_source_type"):
            op.drop_index("ix_storage_sources_source_type", table_name="storage_sources")
        if _index_exists(bind, "storage_sources", "ix_storage_sources_project_id"):
            op.drop_index("ix_storage_sources_project_id", table_name="storage_sources")
        if _index_exists(bind, "storage_sources", "ix_storage_sources_organization_id"):
            op.drop_index("ix_storage_sources_organization_id", table_name="storage_sources")
        op.drop_table("storage_sources")
