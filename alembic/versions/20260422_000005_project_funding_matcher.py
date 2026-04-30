"""harden project funding matcher persistence

Revision ID: 20260422_000005
Revises: 20260422_000004
Create Date: 2026-04-22 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_000005"
down_revision = "20260422_000004"
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
    if not _table_exists("project_funding_matches"):
        op.create_table(
            "project_funding_matches",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("funding_call_id", sa.String(length=36), nullable=False),
            sa.Column("match_score", sa.Float(), nullable=False, server_default="0"),
            sa.Column("fit_level", sa.String(length=20), nullable=True),
            sa.Column("fit_summary", sa.Text(), nullable=True),
            sa.Column("blocking_reasons", sa.Text(), nullable=True),
            sa.Column("missing_documents", sa.Text(), nullable=True),
            sa.Column("recommended_actions", sa.Text(), nullable=True),
            sa.Column("confidence_level", sa.String(length=20), nullable=True),
            sa.Column("evaluation_version", sa.String(length=20), nullable=True),
            sa.Column("computed_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["funding_call_id"], ["funding_calls.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        for name, column in (
            ("organization_id", sa.Column("organization_id", sa.String(length=36), nullable=False, server_default="")),
            ("fit_level", sa.Column("fit_level", sa.String(length=20), nullable=True)),
            ("confidence_level", sa.Column("confidence_level", sa.String(length=20), nullable=True)),
            ("evaluation_version", sa.Column("evaluation_version", sa.String(length=20), nullable=True)),
        ):
            if not _column_exists("project_funding_matches", name):
                op.add_column("project_funding_matches", column)

    matcher_indexes = _index_names("project_funding_matches")
    for index_name, columns in (
        ("ix_match_project_id", ["project_id"]),
        ("ix_match_project_org", ["project_id", "organization_id"]),
        ("ix_match_funding_call_id", ["funding_call_id"]),
    ):
        if index_name not in matcher_indexes:
            op.create_index(index_name, "project_funding_matches", columns, unique=False)


def downgrade() -> None:
    if _table_exists("project_funding_matches"):
        for index_name in (
            "ix_match_funding_call_id",
            "ix_match_project_org",
            "ix_match_project_id",
        ):
            if index_name in _index_names("project_funding_matches"):
                op.drop_index(index_name, table_name="project_funding_matches")
        op.drop_table("project_funding_matches")
