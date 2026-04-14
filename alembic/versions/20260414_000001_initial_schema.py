"""initial schema

Revision ID: 20260414_000001
Revises:
Create Date: 2026-04-14 00:00:01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260414_000001"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum(
    "ADMIN",
    "PRODUCER",
    "CREATOR",
    "EDITOR",
    "CLIENT",
    name="userrole",
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("billing_plan", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "funding_opportunities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("amount_range", sa.String(length=100), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lead_gen_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("org_id", sa.String(length=36), nullable=True),
        sa.Column("trigger_source", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_gen_events_org_id", "lead_gen_events", ["org_id"], unique=False
    )
    op.create_index(
        "ix_lead_gen_events_user_id", "lead_gen_events", ["user_id"], unique=False
    )

    op.create_table(
        "producer_demo_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("org_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("organization_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column(
            "source", sa.String(length=100), server_default="website", nullable=True
        ),
        sa.Column("status", sa.String(length=50), server_default="new", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_producer_demo_requests_created_at",
        "producer_demo_requests",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_producer_demo_requests_email",
        "producer_demo_requests",
        ["email"],
        unique=False,
    )
    op.create_index(
        "ix_producer_demo_requests_org_id",
        "producer_demo_requests",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        "ix_producer_demo_requests_status_created_at",
        "producer_demo_requests",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_producer_demo_requests_user_id",
        "producer_demo_requests",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "saved_opportunities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("funding_opportunity_id", sa.String(length=36), nullable=False),
        sa.Column(
            "status", sa.String(length=50), server_default="bookmarked", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["funding_opportunity_id"],
            ["funding_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "funding_opportunity_id",
            name="uq_saved_opportunities_project_funding",
        ),
    )
    op.create_index(
        "ix_saved_opportunities_created_at",
        "saved_opportunities",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_saved_opportunities_funding_opportunity_id",
        "saved_opportunities",
        ["funding_opportunity_id"],
        unique=False,
    )
    op.create_index(
        "ix_saved_opportunities_project_id",
        "saved_opportunities",
        ["project_id"],
        unique=False,
    )

    op.create_table(
        "sequences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sequences_project_id", "sequences", ["project_id"], unique=False
    )

    op.create_table(
        "characters",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("line_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_characters_project_id", "characters", ["project_id"], unique=False
    )

    op.create_table(
        "scenes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_id", sa.String(length=36), nullable=True),
        sa.Column("scene_number", sa.String(length=10), nullable=True),
        sa.Column("setting", sa.String(length=10), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("time_of_day", sa.String(length=50), nullable=True),
        sa.Column("action_text", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sequence_id"], ["sequences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scenes_project_id", "scenes", ["project_id"], unique=False)
    op.create_index("ix_scenes_sequence_id", "scenes", ["sequence_id"], unique=False)

    op.create_table(
        "scene_character_link",
        sa.Column("scene_id", sa.String(length=36), nullable=False),
        sa.Column("character_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["character_id"], ["characters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("scene_id", "character_id"),
    )

    op.create_table(
        "assembly_cuts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("sequence_ledger", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assembly_cuts_project_id", "assembly_cuts", ["project_id"], unique=False
    )

    op.create_table(
        "clips",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("scene_id", sa.String(length=36), nullable=True),
        sa.Column("file_path_or_url", sa.String(), nullable=False),
        sa.Column("proxy_filename", sa.String(length=255), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=255), nullable=True),
        sa.Column("duration_seconds", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clips_project_id", "clips", ["project_id"], unique=False)
    op.create_index("ix_clips_scene_id", "clips", ["scene_id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column(
            "status", sa.String(length=50), server_default="pending", nullable=False
        ),
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
        sa.CheckConstraint(
            "length(trim(target_id)) > 0", name="ck_reviews_target_id_not_blank"
        ),
        sa.CheckConstraint(
            "length(trim(target_type)) > 0", name="ck_reviews_target_type_not_blank"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'needs_work', 'approved', 'rejected')",
            name="ck_reviews_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_project_id", "reviews", ["project_id"], unique=False)
    op.create_index(
        "ix_reviews_project_status_created_at",
        "reviews",
        ["project_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_reviews_project_target_created_at",
        "reviews",
        ["project_id", "target_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_reviews_project_target_id_created_at",
        "reviews",
        ["project_id", "target_type", "target_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "approval_decisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("review_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=36), nullable=True),
        sa.Column("author_name", sa.String(length=100), nullable=True),
        sa.Column("status_applied", sa.String(length=50), nullable=False),
        sa.Column("rationale_note", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status_applied IN ('pending', 'needs_work', 'approved', 'rejected')",
            name="ck_approval_decisions_status_applied",
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_approval_decisions_review_created_at",
        "approval_decisions",
        ["review_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_approval_decisions_review_id",
        "approval_decisions",
        ["review_id"],
        unique=False,
    )
    op.create_index(
        "ix_approval_decisions_review_status_created_at",
        "approval_decisions",
        ["review_id", "status_applied", "created_at"],
        unique=False,
    )

    op.create_table(
        "review_comments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("review_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=36), nullable=True),
        sa.Column("author_name", sa.String(length=100), nullable=True),
        sa.Column("body", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(body)) > 0", name="ck_review_comments_body_not_blank"
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_review_comments_review_created_at",
        "review_comments",
        ["review_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_review_comments_review_id", "review_comments", ["review_id"], unique=False
    )

    op.create_table(
        "shots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("scene_id", sa.String(length=36), nullable=False),
        sa.Column("shot_number", sa.Integer(), nullable=True),
        sa.Column("shot_size", sa.String(length=50), nullable=True),
        sa.Column("camera_angle", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shots_project_id", "shots", ["project_id"], unique=False)
    op.create_index("ix_shots_scene_id", "shots", ["scene_id"], unique=False)

    op.create_table(
        "deliverables",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("source_review_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("format_type", sa.String(length=50), nullable=False),
        sa.Column("delivery_payload", sa.JSON(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), server_default="draft", nullable=False
        ),
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
        sa.CheckConstraint(
            "length(trim(name)) > 0", name="ck_deliverables_name_not_blank"
        ),
        sa.CheckConstraint(
            "length(trim(format_type)) > 0",
            name="ck_deliverables_format_type_not_blank",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'ready', 'delivered')",
            name="ck_deliverables_status",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_review_id"], ["reviews.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_review_id", name="uq_deliverables_source_review_id"
        ),
    )
    op.create_index(
        "ix_deliverables_project_id", "deliverables", ["project_id"], unique=False
    )
    op.create_index(
        "ix_deliverables_project_source_review_created_at",
        "deliverables",
        ["project_id", "source_review_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_deliverables_project_status_created_at",
        "deliverables",
        ["project_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_deliverables_source_review_id",
        "deliverables",
        ["source_review_id"],
        unique=False,
    )

    op.create_table(
        "visual_assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("shot_id", sa.String(length=36), nullable=False),
        sa.Column("file_path_or_url", sa.String(), nullable=False),
        sa.Column("thumbnail_url", sa.String(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("generation_metadata", sa.JSON(), nullable=True),
        sa.Column("is_reference_approved", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shot_id"], ["shots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_visual_assets_project_id", "visual_assets", ["project_id"], unique=False
    )
    op.create_index(
        "ix_visual_assets_shot_id", "visual_assets", ["shot_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_visual_assets_shot_id", table_name="visual_assets")
    op.drop_index("ix_visual_assets_project_id", table_name="visual_assets")
    op.drop_table("visual_assets")

    op.drop_index("ix_deliverables_source_review_id", table_name="deliverables")
    op.drop_index(
        "ix_deliverables_project_status_created_at", table_name="deliverables"
    )
    op.drop_index(
        "ix_deliverables_project_source_review_created_at", table_name="deliverables"
    )
    op.drop_index("ix_deliverables_project_id", table_name="deliverables")
    op.drop_table("deliverables")

    op.drop_index("ix_shots_scene_id", table_name="shots")
    op.drop_index("ix_shots_project_id", table_name="shots")
    op.drop_table("shots")

    op.drop_index("ix_review_comments_review_id", table_name="review_comments")
    op.drop_index("ix_review_comments_review_created_at", table_name="review_comments")
    op.drop_table("review_comments")

    op.drop_index(
        "ix_approval_decisions_review_status_created_at",
        table_name="approval_decisions",
    )
    op.drop_index("ix_approval_decisions_review_id", table_name="approval_decisions")
    op.drop_index(
        "ix_approval_decisions_review_created_at", table_name="approval_decisions"
    )
    op.drop_table("approval_decisions")

    op.drop_index("ix_reviews_project_target_id_created_at", table_name="reviews")
    op.drop_index("ix_reviews_project_target_created_at", table_name="reviews")
    op.drop_index("ix_reviews_project_status_created_at", table_name="reviews")
    op.drop_index("ix_reviews_project_id", table_name="reviews")
    op.drop_table("reviews")

    op.drop_index("ix_clips_scene_id", table_name="clips")
    op.drop_index("ix_clips_project_id", table_name="clips")
    op.drop_table("clips")

    op.drop_index("ix_assembly_cuts_project_id", table_name="assembly_cuts")
    op.drop_table("assembly_cuts")

    op.drop_table("scene_character_link")

    op.drop_index("ix_scenes_sequence_id", table_name="scenes")
    op.drop_index("ix_scenes_project_id", table_name="scenes")
    op.drop_table("scenes")

    op.drop_index("ix_characters_project_id", table_name="characters")
    op.drop_table("characters")

    op.drop_index("ix_sequences_project_id", table_name="sequences")
    op.drop_table("sequences")

    op.drop_index("ix_saved_opportunities_project_id", table_name="saved_opportunities")
    op.drop_index(
        "ix_saved_opportunities_funding_opportunity_id",
        table_name="saved_opportunities",
    )
    op.drop_index("ix_saved_opportunities_created_at", table_name="saved_opportunities")
    op.drop_table("saved_opportunities")

    op.drop_index(
        "ix_producer_demo_requests_user_id", table_name="producer_demo_requests"
    )
    op.drop_index(
        "ix_producer_demo_requests_status_created_at",
        table_name="producer_demo_requests",
    )
    op.drop_index(
        "ix_producer_demo_requests_org_id", table_name="producer_demo_requests"
    )
    op.drop_index(
        "ix_producer_demo_requests_email", table_name="producer_demo_requests"
    )
    op.drop_index(
        "ix_producer_demo_requests_created_at", table_name="producer_demo_requests"
    )
    op.drop_table("producer_demo_requests")

    op.drop_index("ix_lead_gen_events_user_id", table_name="lead_gen_events")
    op.drop_index("ix_lead_gen_events_org_id", table_name="lead_gen_events")
    op.drop_table("lead_gen_events")

    op.drop_table("projects")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table("funding_opportunities")
    op.drop_table("organizations")

    bind = op.get_bind()
    user_role_enum.drop(bind, checkfirst=True)
