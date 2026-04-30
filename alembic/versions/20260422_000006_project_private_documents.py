"""add tenant safe project private documents

Revision ID: 20260422_000006
Revises: 20260422_000005
Create Date: 2026-04-22 18:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_000006"
down_revision = "20260422_000005"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("project_documents"):
        op.create_table(
            "project_documents",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("uploaded_by_user_id", sa.String(length=36), nullable=True),
            sa.Column("document_type", sa.String(length=50), nullable=False, server_default="other"),
            sa.Column("upload_status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("file_name", sa.String(length=255), nullable=False),
            sa.Column("mime_type", sa.String(length=255), nullable=False),
            sa.Column("file_size", sa.Float(), nullable=False, server_default="0"),
            sa.Column("storage_path", sa.String(length=2000), nullable=False),
            sa.Column("checksum", sa.String(length=64), nullable=False),
            sa.Column("extracted_text", sa.Text(), nullable=True),
            sa.Column("visibility_scope", sa.String(length=30), nullable=False, server_default="project"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = _index_names("project_documents")
    for index_name, columns in (
        ("ix_project_documents_org_project", ["organization_id", "project_id"]),
        ("ix_project_documents_status_created_at", ["upload_status", "created_at"]),
        ("ix_project_documents_checksum", ["checksum"]),
    ):
        if index_name not in indexes:
            op.create_index(index_name, "project_documents", columns, unique=False)


def downgrade() -> None:
    if _table_exists("project_documents"):
        for index_name in (
            "ix_project_documents_checksum",
            "ix_project_documents_status_created_at",
            "ix_project_documents_org_project",
        ):
            if index_name in _index_names("project_documents"):
                op.drop_index(index_name, table_name="project_documents")
        op.drop_table("project_documents")
