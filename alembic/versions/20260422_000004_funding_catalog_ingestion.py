"""add institutional funding catalog ingestion

Revision ID: 20260422_000004
Revises: 20260421_000003
Create Date: 2026-04-22 10:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_000004"
down_revision = "20260421_000003"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("funding_sources"):
        op.create_table(
            "funding_sources",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("code", sa.String(length=20), nullable=False),
            sa.Column("agency_name", sa.String(length=255), nullable=True),
            sa.Column("official_url", sa.String(length=500), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("region_scope", sa.String(length=32), nullable=False, server_default="spain"),
            sa.Column("country_or_program", sa.String(length=100), nullable=True),
            sa.Column("region", sa.String(length=20), nullable=False, server_default="spain"),
            sa.Column("territory", sa.String(length=50), nullable=False, server_default="Espana"),
            sa.Column("source_type", sa.String(length=30), nullable=False, server_default="institutional"),
            sa.Column("verification_status", sa.String(length=20), nullable=False, server_default="official"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("last_synced_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        for name, column in (
            ("agency_name", sa.Column("agency_name", sa.String(length=255), nullable=True)),
            ("description", sa.Column("description", sa.Text(), nullable=True)),
            ("region_scope", sa.Column("region_scope", sa.String(length=32), nullable=False, server_default="spain")),
            ("country_or_program", sa.Column("country_or_program", sa.String(length=100), nullable=True)),
            ("source_type", sa.Column("source_type", sa.String(length=30), nullable=False, server_default="institutional")),
            ("verification_status", sa.Column("verification_status", sa.String(length=20), nullable=False, server_default="official")),
            ("updated_at", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
        ):
            if not _column_exists("funding_sources", name):
                op.add_column("funding_sources", column)

    funding_source_indexes = _index_names("funding_sources")
    if "ix_funding_source_name" not in funding_source_indexes:
        op.create_index("ix_funding_source_name", "funding_sources", ["name"], unique=False)
    if "ix_funding_source_code" not in funding_source_indexes:
        op.create_index("ix_funding_source_code", "funding_sources", ["code"], unique=False)

    if not _table_exists("funding_calls"):
        op.create_table(
            "funding_calls",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("source_id", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("region_scope", sa.String(length=32), nullable=False, server_default="spain"),
            sa.Column("country_or_program", sa.String(length=100), nullable=False, server_default="Espana"),
            sa.Column("agency_name", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("official_url", sa.String(length=500), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("open_date", sa.DateTime(), nullable=True),
            sa.Column("close_date", sa.DateTime(), nullable=True),
            sa.Column("amount_range", sa.String(length=100), nullable=True),
            sa.Column("amount_min", sa.Float(), nullable=True),
            sa.Column("amount_max", sa.Float(), nullable=True),
            sa.Column("opportunity_type", sa.String(length=50), nullable=True),
            sa.Column("phase", sa.String(length=30), nullable=True),
            sa.Column("collaboration_mode", sa.String(length=30), nullable=True),
            sa.Column("max_award_per_project", sa.Float(), nullable=True),
            sa.Column("total_budget_pool", sa.Float(), nullable=True),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
            sa.Column("region", sa.String(length=20), nullable=False, server_default="spain"),
            sa.Column("territory", sa.String(length=50), nullable=False, server_default="Espana"),
            sa.Column("eligibility_summary", sa.Text(), nullable=True),
            sa.Column("eligibility_json", sa.Text(), nullable=True),
            sa.Column("requirements_json", sa.Text(), nullable=True),
            sa.Column("collaboration_rules_json", sa.Text(), nullable=True),
            sa.Column("point_system_json", sa.Text(), nullable=True),
            sa.Column("eligible_formats_json", sa.Text(), nullable=True),
            sa.Column("notes_json", sa.Text(), nullable=True),
            sa.Column("deadline", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
            sa.Column("verification_status", sa.String(length=20), nullable=False, server_default="official"),
            sa.Column("ingested_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["source_id"], ["funding_sources.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        for name, column in (
            ("region_scope", sa.Column("region_scope", sa.String(length=32), nullable=False, server_default="spain")),
            ("country_or_program", sa.Column("country_or_program", sa.String(length=100), nullable=False, server_default="Espana")),
            ("agency_name", sa.Column("agency_name", sa.String(length=255), nullable=False, server_default="")),
            ("open_date", sa.Column("open_date", sa.DateTime(), nullable=True)),
            ("close_date", sa.Column("close_date", sa.DateTime(), nullable=True)),
            ("max_award_per_project", sa.Column("max_award_per_project", sa.Float(), nullable=True)),
            ("total_budget_pool", sa.Column("total_budget_pool", sa.Float(), nullable=True)),
            ("currency", sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR")),
            ("eligibility_json", sa.Column("eligibility_json", sa.Text(), nullable=True)),
            ("requirements_json", sa.Column("requirements_json", sa.Text(), nullable=True)),
            ("collaboration_rules_json", sa.Column("collaboration_rules_json", sa.Text(), nullable=True)),
            ("point_system_json", sa.Column("point_system_json", sa.Text(), nullable=True)),
            ("eligible_formats_json", sa.Column("eligible_formats_json", sa.Text(), nullable=True)),
            ("notes_json", sa.Column("notes_json", sa.Text(), nullable=True)),
            ("created_at", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
            ("updated_at", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
        ):
            if not _column_exists("funding_calls", name):
                op.add_column("funding_calls", column)

    funding_call_indexes = _index_names("funding_calls")
    for index_name, columns in (
        ("ix_funding_call_source_id", ["source_id"]),
        ("ix_funding_call_status", ["status"]),
        ("ix_funding_call_deadline", ["deadline"]),
        ("ix_funding_call_region_scope", ["region_scope"]),
    ):
        if index_name not in funding_call_indexes:
            op.create_index(index_name, "funding_calls", columns, unique=False)

    if not _table_exists("funding_requirements"):
        op.create_table(
            "funding_requirements",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("call_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False, server_default="general"),
            sa.Column("requirement_text", sa.Text(), nullable=False),
            sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("notes_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["call_id"], ["funding_calls.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    funding_requirement_indexes = _index_names("funding_requirements")
    if "ix_funding_requirement_call_id" not in funding_requirement_indexes:
        op.create_index("ix_funding_requirement_call_id", "funding_requirements", ["call_id"], unique=False)
    if "ix_funding_requirement_category" not in funding_requirement_indexes:
        op.create_index("ix_funding_requirement_category", "funding_requirements", ["category"], unique=False)


def downgrade() -> None:
    if _table_exists("funding_requirements"):
        for index_name in ("ix_funding_requirement_category", "ix_funding_requirement_call_id"):
            if index_name in _index_names("funding_requirements"):
                op.drop_index(index_name, table_name="funding_requirements")
        op.drop_table("funding_requirements")

    if _table_exists("funding_calls"):
        for index_name in (
            "ix_funding_call_region_scope",
            "ix_funding_call_deadline",
            "ix_funding_call_status",
            "ix_funding_call_source_id",
        ):
            if index_name in _index_names("funding_calls"):
                op.drop_index(index_name, table_name="funding_calls")
        op.drop_table("funding_calls")

    if _table_exists("funding_sources"):
        for index_name in ("ix_funding_source_code", "ix_funding_source_name"):
            if index_name in _index_names("funding_sources"):
                op.drop_index(index_name, table_name="funding_sources")
        op.drop_table("funding_sources")
