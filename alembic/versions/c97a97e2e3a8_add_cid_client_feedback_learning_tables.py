"""add_cid_client_feedback_learning_tables

Revision ID: c97a97e2e3a8
Revises: 7c72fdc1a074
Create Date: 2026-06-01 10:50:26.136846
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = 'c97a97e2e3a8'
down_revision = '7c72fdc1a074'
branch_labels = None
depends_on = None


CID_FEEDBACK_TYPES = [
    "answer_helpful",
    "answer_wrong",
    "answer_partially_wrong",
    "approved_correction",
    "rejected_answer",
    "style_preference",
    "tone_preference",
    "project_rule",
    "character_correction",
    "location_correction",
    "raccord_correction",
    "storyboard_correction",
    "production_decision",
    "prompt_success_case",
    "prompt_failure_case",
    "source_blacklist",
    "source_preference",
]

CID_FEEDBACK_SCOPES = ["project_feedback", "organization_feedback", "answer_feedback"]

CID_FEEDBACK_STATUSES = ["pending", "approved", "rejected", "archived"]

CID_FEEDBACK_AUDIT_ACTIONS = [
    "created",
    "approved",
    "rejected",
    "edited",
    "archived",
    "indexed",
    "deindexed",
]

CID_LEARNING_RULE_TYPES = [
    "style_preference",
    "tone_preference",
    "project_rule",
    "character_correction",
    "location_correction",
    "raccord_correction",
    "source_blacklist",
    "source_preference",
]


def _enum_ck(values: list[str]) -> str:
    vals = ", ".join(repr(v) for v in values)
    return f"value IN ({vals})"


def upgrade() -> None:
    # ### cid_client_feedback ###
    op.create_table(
        "cid_client_feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("feedback_type", sa.String(30), nullable=False),
        sa.Column("feedback_scope", sa.String(30), server_default="project_feedback", nullable=False),
        sa.Column("original_question", sa.Text, nullable=True),
        sa.Column("original_answer", sa.Text, nullable=True),
        sa.Column("corrected_answer", sa.Text, nullable=True),
        sa.Column("feedback_text", sa.Text, nullable=True),
        sa.Column("source_ids", sa.JSON, nullable=True),
        sa.Column("source_types", sa.JSON, nullable=True),
        sa.Column("approved_for_memory", sa.Boolean, server_default="0", nullable=False),
        sa.Column("approved_by_user_id", sa.String(36), nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("answer_version", sa.String(50), nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint(_enum_ck(CID_FEEDBACK_TYPES), name="ck_cf_feedback_type"),
        sa.CheckConstraint(_enum_ck(CID_FEEDBACK_SCOPES), name="ck_cf_feedback_scope"),
        sa.CheckConstraint(_enum_ck(CID_FEEDBACK_STATUSES), name="ck_cf_status"),
    )
    op.create_index("ix_cf_org_project", "cid_client_feedback", ["organization_id", "project_id"])
    op.create_index("ix_cf_org_project_type", "cid_client_feedback", ["organization_id", "project_id", "feedback_type"])
    op.create_index("ix_cf_org_project_status", "cid_client_feedback", ["organization_id", "project_id", "status"])
    op.create_index("ix_cf_user_id", "cid_client_feedback", ["user_id"])
    op.create_index("ix_cf_created_at", "cid_client_feedback", ["created_at"])

    # ### cid_feedback_memory_entries ###
    op.create_table(
        "cid_feedback_memory_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("feedback_id", sa.String(36), sa.ForeignKey("cid_client_feedback.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("source_text", sa.Text, nullable=True),
        sa.Column("approved_for_memory", sa.Boolean, server_default="0", nullable=False),
        sa.Column("approved_by_user_id", sa.String(36), nullable=True),
        sa.Column("qdrant_point_id", sa.String(100), nullable=True),
        sa.Column("indexed_at", sa.DateTime, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_cfme_org_project", "cid_feedback_memory_entries", ["organization_id", "project_id"])
    op.create_index("ix_cfme_feedback_id", "cid_feedback_memory_entries", ["feedback_id"])
    op.create_index("ix_cfme_source", "cid_feedback_memory_entries", ["source_type", "source_id"])
    op.create_index("ix_cfme_approved", "cid_feedback_memory_entries", ["approved_for_memory"])
    op.create_index("ix_cfme_qdrant_point", "cid_feedback_memory_entries", ["qdrant_point_id"])
    op.create_index("ix_cfme_created_at", "cid_feedback_memory_entries", ["created_at"])

    # ### cid_answer_feedback_events ###
    op.create_table(
        "cid_answer_feedback_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("feedback_id", sa.String(36), sa.ForeignKey("cid_client_feedback.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("answer_id", sa.String(36), nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("prompt_version", sa.String(50), nullable=True),
        sa.Column("answer_version", sa.String(50), nullable=True),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_cafe_org_project", "cid_answer_feedback_events", ["organization_id", "project_id"])
    op.create_index("ix_cafe_feedback_id", "cid_answer_feedback_events", ["feedback_id"])
    op.create_index("ix_cafe_answer_id", "cid_answer_feedback_events", ["answer_id"])
    op.create_index("ix_cafe_action", "cid_answer_feedback_events", ["action"])
    op.create_index("ix_cafe_created_at", "cid_answer_feedback_events", ["created_at"])

    # ### cid_project_learning_rules ###
    op.create_table(
        "cid_project_learning_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("rule_type", sa.String(30), nullable=False),
        sa.Column("rule_value", sa.Text, nullable=False),
        sa.Column("priority", sa.Integer, server_default="0", nullable=False),
        sa.Column("active", sa.Boolean, server_default="1", nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint(_enum_ck(CID_LEARNING_RULE_TYPES), name="ck_cplr_rule_type"),
    )
    op.create_index("ix_cplr_org_project", "cid_project_learning_rules", ["organization_id", "project_id"])
    op.create_index("ix_cplr_rule_type", "cid_project_learning_rules", ["rule_type"])
    op.create_index("ix_cplr_active", "cid_project_learning_rules", ["active"])
    op.create_index("ix_cplr_created_at", "cid_project_learning_rules", ["created_at"])

    # ### cid_organization_learning_preferences ###
    op.create_table(
        "cid_organization_learning_preferences",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("preference_type", sa.String(30), nullable=False),
        sa.Column("preference_value", sa.Text, nullable=False),
        sa.Column("priority", sa.Integer, server_default="0", nullable=False),
        sa.Column("active", sa.Boolean, server_default="1", nullable=False),
        sa.Column("created_by_user_id", sa.String(36), nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_colp_org", "cid_organization_learning_preferences", ["organization_id"])
    op.create_index("ix_colp_preference_type", "cid_organization_learning_preferences", ["preference_type"])
    op.create_index("ix_colp_active", "cid_organization_learning_preferences", ["active"])
    op.create_index("ix_colp_created_at", "cid_organization_learning_preferences", ["created_at"])

    # ### cid_feedback_audit ###
    op.create_table(
        "cid_feedback_audit",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("feedback_id", sa.String(36), sa.ForeignKey("cid_client_feedback.id", ondelete="SET NULL"), nullable=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("previous_status", sa.String(20), nullable=True),
        sa.Column("new_status", sa.String(20), nullable=True),
        sa.Column("previous_metadata_json", sa.JSON, nullable=True),
        sa.Column("new_metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.CheckConstraint(_enum_ck(CID_FEEDBACK_AUDIT_ACTIONS), name="ck_cfa_action"),
    )
    op.create_index("ix_cfa_org_project", "cid_feedback_audit", ["organization_id", "project_id"])
    op.create_index("ix_cfa_feedback_id", "cid_feedback_audit", ["feedback_id"])
    op.create_index("ix_cfa_user_id", "cid_feedback_audit", ["user_id"])
    op.create_index("ix_cfa_action", "cid_feedback_audit", ["action"])
    op.create_index("ix_cfa_created_at", "cid_feedback_audit", ["created_at"])


def downgrade() -> None:
    op.drop_table("cid_feedback_audit")
    op.drop_table("cid_organization_learning_preferences")
    op.drop_table("cid_project_learning_rules")
    op.drop_table("cid_answer_feedback_events")
    op.drop_table("cid_feedback_memory_entries")
    op.drop_table("cid_client_feedback")
