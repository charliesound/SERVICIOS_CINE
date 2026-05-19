"""add project visual bible table

Revision ID: 20260519_000001
Revises: 20260517_000003
Create Date: 2026-05-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260519_000001"
down_revision: Union[str, None] = "20260517_000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return index_name in {i["name"] for i in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "project_visual_bibles"):
        op.create_table(
            "project_visual_bibles",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("active_preset_id", sa.String(length=100), nullable=True),
            sa.Column("selected_elements_json", sa.JSON(), nullable=True, server_default=sa.text("'{}'")),
            sa.Column("custom_prompt_tags_json", sa.JSON(), nullable=True, server_default=sa.text("'[]'")),
            sa.Column("negative_prompt_tags_json", sa.JSON(), nullable=True, server_default=sa.text("'[]'")),
            sa.Column("director_notes", sa.Text(), nullable=True),
            sa.Column("prompt_mode", sa.String(length=50), nullable=True, server_default="tag_soup"),
            sa.Column("target_model", sa.String(length=50), nullable=True, server_default="SDXL"),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("created_by", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                ["project_id"],
                ["projects.id"],
                ondelete="CASCADE",
            ),
        )

    if not _index_exists(bind, "project_visual_bibles", "ix_project_visual_bibles_project_id"):
        op.create_index(
            "ix_project_visual_bibles_project_id",
            "project_visual_bibles",
            ["project_id"],
            unique=True,
        )
    if not _index_exists(bind, "project_visual_bibles", "ix_project_visual_bibles_organization_id"):
        op.create_index(
            "ix_project_visual_bibles_organization_id",
            "project_visual_bibles",
            ["organization_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "project_visual_bibles"):
        if _index_exists(bind, "project_visual_bibles", "ix_project_visual_bibles_organization_id"):
            op.drop_index("ix_project_visual_bibles_organization_id", table_name="project_visual_bibles")
        if _index_exists(bind, "project_visual_bibles", "ix_project_visual_bibles_project_id"):
            op.drop_index("ix_project_visual_bibles_project_id", table_name="project_visual_bibles")
        op.drop_table("project_visual_bibles")
