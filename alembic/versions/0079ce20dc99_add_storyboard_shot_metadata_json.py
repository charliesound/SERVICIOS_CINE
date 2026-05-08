"""add storyboard_shot metadata_json column

Revision ID: 0079ce20dc99
Revises: 20260428_000010
Create Date: 2026-05-08

Adds nullable Text column metadata_json to storyboard_shots table
for storing CID cinematic intelligence metadata (directorial_intent,
montage_intent, shot_editorial_purpose, prompt_spec, etc.).
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0079ce20dc99"
down_revision = "20260428_000010"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _column_exists("storyboard_shots", "metadata_json"):
        op.add_column(
            "storyboard_shots",
            sa.Column("metadata_json", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    if _column_exists("storyboard_shots", "metadata_json"):
        op.drop_column("storyboard_shots", "metadata_json")
