"""add storyboard shots editable core

Revision ID: 20260421_000003
Revises: 20260418_000002
Create Date: 2026-04-21 18:55:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260421_000003"
down_revision = "20260418_000002"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("storyboard_shots"):
        op.create_table(
            "storyboard_shots",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("sequence_id", sa.String(length=255), nullable=True),
            sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("narrative_text", sa.Text(), nullable=True),
            sa.Column("asset_id", sa.String(length=36), nullable=True),
            sa.Column("shot_type", sa.String(length=100), nullable=True),
            sa.Column("visual_mode", sa.String(length=100), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = _index_names("storyboard_shots")
    if "ix_storyboard_shots_project_id" not in indexes:
        op.create_index(
            "ix_storyboard_shots_project_id",
            "storyboard_shots",
            ["project_id"],
            unique=False,
        )
    if "ix_storyboard_shots_organization_id" not in indexes:
        op.create_index(
            "ix_storyboard_shots_organization_id",
            "storyboard_shots",
            ["organization_id"],
            unique=False,
        )
    if "ix_storyboard_shots_asset_id" not in indexes:
        op.create_index(
            "ix_storyboard_shots_asset_id",
            "storyboard_shots",
            ["asset_id"],
            unique=False,
        )
    if "ix_storyboard_shots_org_project_sequence" not in indexes:
        op.create_index(
            "ix_storyboard_shots_org_project_sequence",
            "storyboard_shots",
            ["organization_id", "project_id", "sequence_id"],
            unique=False,
        )
    if "ix_storyboard_shots_project_sequence_order" not in indexes:
        op.create_index(
            "ix_storyboard_shots_project_sequence_order",
            "storyboard_shots",
            ["project_id", "sequence_id", "sequence_order"],
            unique=False,
        )


def downgrade() -> None:
    if not _table_exists("storyboard_shots"):
        return

    indexes = _index_names("storyboard_shots")
    for index_name in (
        "ix_storyboard_shots_project_sequence_order",
        "ix_storyboard_shots_org_project_sequence",
        "ix_storyboard_shots_asset_id",
        "ix_storyboard_shots_organization_id",
        "ix_storyboard_shots_project_id",
    ):
        if index_name in indexes:
            op.drop_index(index_name, table_name="storyboard_shots")
    op.drop_table("storyboard_shots")
