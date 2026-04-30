"""add bwf ixml and dual system take fields

Revision ID: 20260428_000010
Revises: 20260428_000009
Create Date: 2026-04-28 12:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260428_000010"
down_revision = "20260428_000009"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _table_exists("takes"):
        return

    columns = _column_names("takes")
    additions = (
        ("audio_timecode_start", sa.Column("audio_timecode_start", sa.String(length=64), nullable=True)),
        ("audio_time_reference_samples", sa.Column("audio_time_reference_samples", sa.Integer(), nullable=True)),
        ("audio_sample_rate", sa.Column("audio_sample_rate", sa.Integer(), nullable=True)),
        ("audio_channels", sa.Column("audio_channels", sa.Integer(), nullable=True)),
        ("audio_duration_seconds", sa.Column("audio_duration_seconds", sa.Float(), nullable=True)),
        ("audio_fps", sa.Column("audio_fps", sa.Float(), nullable=True)),
        ("audio_scene", sa.Column("audio_scene", sa.String(length=255), nullable=True)),
        ("audio_take", sa.Column("audio_take", sa.String(length=255), nullable=True)),
        ("audio_circled", sa.Column("audio_circled", sa.Boolean(), nullable=True)),
        ("audio_metadata_status", sa.Column("audio_metadata_status", sa.String(length=50), nullable=True)),
        ("audio_metadata_json", sa.Column("audio_metadata_json", sa.Text(), nullable=True)),
        ("dual_system_status", sa.Column("dual_system_status", sa.String(length=50), nullable=True)),
        ("sync_confidence", sa.Column("sync_confidence", sa.Float(), nullable=True)),
        ("sync_method", sa.Column("sync_method", sa.String(length=50), nullable=True)),
        ("sync_warning", sa.Column("sync_warning", sa.Text(), nullable=True)),
    )
    for column_name, column in additions:
        if column_name not in columns:
            op.add_column("takes", column)


def downgrade() -> None:
    if not _table_exists("takes"):
        return

    columns = _column_names("takes")
    for column_name in (
        "sync_warning",
        "sync_method",
        "sync_confidence",
        "dual_system_status",
        "audio_metadata_json",
        "audio_metadata_status",
        "audio_circled",
        "audio_take",
        "audio_scene",
        "audio_fps",
        "audio_duration_seconds",
        "audio_channels",
        "audio_sample_rate",
        "audio_time_reference_samples",
        "audio_timecode_start",
    ):
        if column_name in columns:
            op.drop_column("takes", column_name)
