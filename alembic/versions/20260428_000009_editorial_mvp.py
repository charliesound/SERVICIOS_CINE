"""add editorial mvp tables and storyboard scope fields

Revision ID: 20260428_000009
Revises: 20260423_000008
Create Date: 2026-04-28 11:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260428_000009"
down_revision = "20260423_000008"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if _table_exists("storyboard_shots"):
        columns = _column_names("storyboard_shots")
        if "scene_number" not in columns:
            op.add_column("storyboard_shots", sa.Column("scene_number", sa.Integer(), nullable=True))
        if "scene_heading" not in columns:
            op.add_column("storyboard_shots", sa.Column("scene_heading", sa.String(length=500), nullable=True))
        if "generation_mode" not in columns:
            op.add_column("storyboard_shots", sa.Column("generation_mode", sa.String(length=50), nullable=True))
        if "generation_job_id" not in columns:
            op.add_column("storyboard_shots", sa.Column("generation_job_id", sa.String(length=36), nullable=True))
        if "version" not in columns:
            op.add_column("storyboard_shots", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
        if "is_active" not in columns:
            op.add_column("storyboard_shots", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        indexes = _index_names("storyboard_shots")
        if "ix_storyboard_shots_scene_number" not in indexes:
            op.create_index("ix_storyboard_shots_scene_number", "storyboard_shots", ["scene_number"], unique=False)
        if "ix_storyboard_shots_generation_job_id" not in indexes:
            op.create_index("ix_storyboard_shots_generation_job_id", "storyboard_shots", ["generation_job_id"], unique=False)
        if "ix_storyboard_shots_project_active_sequence" not in indexes:
            op.create_index(
                "ix_storyboard_shots_project_active_sequence",
                "storyboard_shots",
                ["project_id", "is_active", "sequence_id"],
                unique=False,
            )

    if _table_exists("assembly_cuts"):
        columns = _column_names("assembly_cuts")
        if "organization_id" not in columns:
            op.add_column("assembly_cuts", sa.Column("organization_id", sa.String(length=36), nullable=True))
        if "source_scope" not in columns:
            op.add_column("assembly_cuts", sa.Column("source_scope", sa.String(length=50), nullable=True))
        if "source_version" not in columns:
            op.add_column("assembly_cuts", sa.Column("source_version", sa.Integer(), nullable=True))
        if "metadata_json" not in columns:
            op.add_column("assembly_cuts", sa.Column("metadata_json", sa.Text(), nullable=True))
        if "created_by" not in columns:
            op.add_column("assembly_cuts", sa.Column("created_by", sa.String(length=36), nullable=True))
        if "updated_at" not in columns:
            op.add_column(
                "assembly_cuts",
                sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
            )
        indexes = _index_names("assembly_cuts")
        if "ix_assembly_cuts_org_project" not in indexes:
            op.create_index("ix_assembly_cuts_org_project", "assembly_cuts", ["organization_id", "project_id"], unique=False)

    if not _table_exists("takes"):
        op.create_table(
            "takes",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("scene_number", sa.Integer(), nullable=True),
            sa.Column("shot_number", sa.Integer(), nullable=True),
            sa.Column("take_number", sa.Integer(), nullable=True),
            sa.Column("camera_roll", sa.String(length=255), nullable=True),
            sa.Column("sound_roll", sa.String(length=255), nullable=True),
            sa.Column("camera_media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("sound_media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("camera_report_id", sa.String(length=36), nullable=True),
            sa.Column("sound_report_id", sa.String(length=36), nullable=True),
            sa.Column("script_note_id", sa.String(length=36), nullable=True),
            sa.Column("director_note_id", sa.String(length=36), nullable=True),
            sa.Column("video_filename", sa.String(length=255), nullable=True),
            sa.Column("audio_filename", sa.String(length=255), nullable=True),
            sa.Column("start_timecode", sa.String(length=64), nullable=True),
            sa.Column("end_timecode", sa.String(length=64), nullable=True),
            sa.Column("duration_frames", sa.Integer(), nullable=True),
            sa.Column("fps", sa.Float(), nullable=True),
            sa.Column("slate", sa.String(length=255), nullable=True),
            sa.Column("script_status", sa.String(length=50), nullable=True),
            sa.Column("director_status", sa.String(length=50), nullable=True),
            sa.Column("camera_status", sa.String(length=50), nullable=True),
            sa.Column("sound_status", sa.String(length=50), nullable=True),
            sa.Column("reconciliation_status", sa.String(length=50), nullable=True, server_default="partial"),
            sa.Column("is_circled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_best", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_recommended", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("score", sa.Float(), nullable=False, server_default="0"),
            sa.Column("recommended_reason", sa.Text(), nullable=True),
            sa.Column("conflict_flags_json", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["camera_media_asset_id"], ["media_assets.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["sound_media_asset_id"], ["media_assets.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["camera_report_id"], ["camera_reports.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["sound_report_id"], ["sound_reports.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["script_note_id"], ["script_notes.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["director_note_id"], ["director_notes.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
    if _table_exists("takes"):
        indexes = _index_names("takes")
        for index_name, columns in (
            ("ix_takes_org_project", ["organization_id", "project_id"]),
            ("ix_takes_scene_shot_take", ["project_id", "scene_number", "shot_number", "take_number"]),
            ("ix_takes_camera_asset", ["camera_media_asset_id"]),
            ("ix_takes_sound_asset", ["sound_media_asset_id"]),
            ("ix_takes_project_id", ["project_id"]),
            ("ix_takes_organization_id", ["organization_id"]),
        ):
            if index_name not in indexes:
                op.create_index(index_name, "takes", columns, unique=False)

    if not _table_exists("assembly_cut_items"):
        op.create_table(
            "assembly_cut_items",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("assembly_cut_id", sa.String(length=36), nullable=False),
            sa.Column("take_id", sa.String(length=36), nullable=True),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("scene_number", sa.Integer(), nullable=True),
            sa.Column("shot_number", sa.Integer(), nullable=True),
            sa.Column("take_number", sa.Integer(), nullable=True),
            sa.Column("source_media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("audio_media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("start_tc", sa.String(length=64), nullable=True),
            sa.Column("end_tc", sa.String(length=64), nullable=True),
            sa.Column("timeline_in", sa.Integer(), nullable=True),
            sa.Column("timeline_out", sa.Integer(), nullable=True),
            sa.Column("duration_frames", sa.Integer(), nullable=True),
            sa.Column("fps", sa.Float(), nullable=True),
            sa.Column("recommended_reason", sa.Text(), nullable=True),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["assembly_cut_id"], ["assembly_cuts.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["take_id"], ["takes.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
    if _table_exists("assembly_cut_items"):
        indexes = _index_names("assembly_cut_items")
        for index_name, columns in (
            ("ix_assembly_cut_items_cut_order", ["assembly_cut_id", "order_index"]),
            ("ix_assembly_cut_items_project_scene_shot_take", ["project_id", "scene_number", "shot_number", "take_number"]),
            ("ix_assembly_cut_items_assembly_cut_id", ["assembly_cut_id"]),
            ("ix_assembly_cut_items_take_id", ["take_id"]),
        ):
            if index_name not in indexes:
                op.create_index(index_name, "assembly_cut_items", columns, unique=False)


def downgrade() -> None:
    if _table_exists("assembly_cut_items"):
        for index_name in (
            "ix_assembly_cut_items_take_id",
            "ix_assembly_cut_items_assembly_cut_id",
            "ix_assembly_cut_items_project_scene_shot_take",
            "ix_assembly_cut_items_cut_order",
        ):
            if index_name in _index_names("assembly_cut_items"):
                op.drop_index(index_name, table_name="assembly_cut_items")
        op.drop_table("assembly_cut_items")

    if _table_exists("takes"):
        for index_name in (
            "ix_takes_organization_id",
            "ix_takes_project_id",
            "ix_takes_sound_asset",
            "ix_takes_camera_asset",
            "ix_takes_scene_shot_take",
            "ix_takes_org_project",
        ):
            if index_name in _index_names("takes"):
                op.drop_index(index_name, table_name="takes")
        op.drop_table("takes")
