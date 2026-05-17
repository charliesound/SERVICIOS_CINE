"""add missing account and funding columns

Revision ID: 20260517_000001
Revises: ec2e3eaf1271
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260517_000001"
down_revision: Union[str, None] = "ec2e3eaf1271"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _has_column(table_name, column.name):
        op.add_column(table_name, column)


def upgrade() -> None:
    # Align users table with current DBUser model.
    _add_column_if_missing("users", sa.Column("username", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("billing_plan", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("program", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("signup_type", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("account_status", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("access_level", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("cid_enabled", sa.Boolean(), nullable=True))
    _add_column_if_missing("users", sa.Column("onboarding_completed", sa.Boolean(), nullable=True))
    _add_column_if_missing("users", sa.Column("company", sa.String(), nullable=True))
    _add_column_if_missing("users", sa.Column("country", sa.String(), nullable=True))

    # Align funding_sources with current FundingSource model.
    _add_column_if_missing("funding_sources", sa.Column("organization_id", sa.String(), nullable=True))

    # Align projects table with current Project model.
    _add_column_if_missing("projects", sa.Column("script_text", sa.Text(), nullable=True))

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("funding_sources")}

    if "ix_funding_sources_organization_id" not in indexes:
        op.create_index(
            "ix_funding_sources_organization_id",
            "funding_sources",
            ["organization_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    indexes = {index["name"] for index in inspector.get_indexes("funding_sources")}
    if "ix_funding_sources_organization_id" in indexes:
        op.drop_index("ix_funding_sources_organization_id", table_name="funding_sources")

    for table_name, column_name in [
        ("projects", "script_text"),
        ("funding_sources", "organization_id"),
        ("users", "country"),
        ("users", "company"),
        ("users", "onboarding_completed"),
        ("users", "cid_enabled"),
        ("users", "access_level"),
        ("users", "account_status"),
        ("users", "signup_type"),
        ("users", "program"),
        ("users", "billing_plan"),
        ("users", "username"),
    ]:
        if _has_column(table_name, column_name):
            op.drop_column(table_name, column_name)
