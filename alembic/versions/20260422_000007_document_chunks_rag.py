"""add document chunks for project rag

Revision ID: 20260422_000007
Revises: 20260422_000006
Create Date: 2026-04-22 20:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_000007"
down_revision = "20260422_000006"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("document_chunks"):
        op.create_table(
            "document_chunks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column("chunk_text", sa.Text(), nullable=False),
            sa.Column("chunk_tokens_estimate", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("embedding_payload", sa.Text(), nullable=False),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_id"], ["project_documents.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = _index_names("document_chunks")
    for index_name, columns in (
        ("ix_document_chunks_doc_chunk", ["document_id", "chunk_index"]),
        ("ix_document_chunks_org_project", ["organization_id", "project_id"]),
        ("ix_document_chunks_created_at", ["created_at"]),
    ):
        if index_name not in indexes:
            op.create_index(index_name, "document_chunks", columns, unique=False)


def downgrade() -> None:
    if _table_exists("document_chunks"):
        for index_name in (
            "ix_document_chunks_created_at",
            "ix_document_chunks_org_project",
            "ix_document_chunks_doc_chunk",
        ):
            if index_name in _index_names("document_chunks"):
                op.drop_index(index_name, table_name="document_chunks")
        op.drop_table("document_chunks")
