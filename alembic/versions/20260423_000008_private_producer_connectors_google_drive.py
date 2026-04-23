"""add google drive integration connector tables

Revision ID: 20260423_000008
Revises: 20260422_000007
Create Date: 2026-04-23 09:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260423_000008"
down_revision = "20260422_000007"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("integration_connections"):
        op.create_table(
            "integration_connections",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_account_email", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="connected"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
    if "ix_integration_connections_org_provider" not in _index_names("integration_connections"):
        op.create_index(
            "ix_integration_connections_org_provider",
            "integration_connections",
            ["organization_id", "provider"],
            unique=False,
        )

    if not _table_exists("integration_tokens"):
        op.create_table(
            "integration_tokens",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("connection_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("access_token_encrypted", sa.Text(), nullable=False),
            sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
            sa.Column("token_expiry_at", sa.DateTime(), nullable=True),
            sa.Column("scope", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["connection_id"], ["integration_connections.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("connection_id", name="uq_integration_tokens_connection_id"),
        )
    for index_name, columns in (
        ("ix_integration_tokens_org_connection", ["organization_id", "connection_id"]),
    ):
        if index_name not in _index_names("integration_tokens"):
            op.create_index(index_name, "integration_tokens", columns, unique=False)

    if not _table_exists("project_external_folder_links"):
        op.create_table(
            "project_external_folder_links",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("connection_id", sa.String(length=36), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_folder_id", sa.String(length=255), nullable=False),
            sa.Column("external_folder_name", sa.String(length=255), nullable=False),
            sa.Column("sync_mode", sa.String(length=30), nullable=False, server_default="import_only"),
            sa.Column("last_sync_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["connection_id"], ["integration_connections.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "project_id",
                "provider",
                "external_folder_id",
                name="uq_project_external_folder_links_project_provider_folder",
            ),
        )
    for index_name, columns in (
        ("ix_project_external_folder_links_org_project", ["organization_id", "project_id"]),
    ):
        if index_name not in _index_names("project_external_folder_links"):
            op.create_index(index_name, "project_external_folder_links", columns, unique=False)

    if not _table_exists("external_document_sync_state"):
        op.create_table(
            "external_document_sync_state",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_file_id", sa.String(length=255), nullable=False),
            sa.Column("external_modified_time", sa.DateTime(), nullable=True),
            sa.Column("external_checksum", sa.String(length=255), nullable=True),
            sa.Column("linked_project_document_id", sa.String(length=36), nullable=True),
            sa.Column("sync_status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("last_seen_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["linked_project_document_id"], ["project_documents.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "project_id",
                "provider",
                "external_file_id",
                name="uq_external_document_sync_state_project_provider_file",
            ),
        )
    for index_name, columns in (
        ("ix_external_document_sync_state_org_project", ["organization_id", "project_id"]),
    ):
        if index_name not in _index_names("external_document_sync_state"):
            op.create_index(index_name, "external_document_sync_state", columns, unique=False)


def downgrade() -> None:
    for table_name, index_names in (
        ("external_document_sync_state", ["ix_external_document_sync_state_org_project"]),
        ("project_external_folder_links", ["ix_project_external_folder_links_org_project"]),
        ("integration_tokens", ["ix_integration_tokens_org_connection"]),
        ("integration_connections", ["ix_integration_connections_org_provider"]),
    ):
        if _table_exists(table_name):
            existing_indexes = _index_names(table_name)
            for index_name in index_names:
                if index_name in existing_indexes:
                    op.drop_index(index_name, table_name=table_name)
            op.drop_table(table_name)
