from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


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


class CIDClientFeedback(Base):
    __tablename__ = "cid_client_feedback"
    __table_args__ = (
        CheckConstraint(
            f"feedback_type IN ({', '.join(repr(t) for t in CID_FEEDBACK_TYPES)})",
            name="ck_cf_feedback_type",
        ),
        CheckConstraint(
            f"feedback_scope IN ({', '.join(repr(s) for s in CID_FEEDBACK_SCOPES)})",
            name="ck_cf_feedback_scope",
        ),
        CheckConstraint(
            f"status IN ({', '.join(repr(s) for s in CID_FEEDBACK_STATUSES)})",
            name="ck_cf_status",
        ),
        Index("ix_cf_org_project", "organization_id", "project_id"),
        Index("ix_cf_org_project_type", "organization_id", "project_id", "feedback_type"),
        Index("ix_cf_org_project_status", "organization_id", "project_id", "status"),
        Index("ix_cf_user_id", "user_id"),
        Index("ix_cf_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(30), nullable=False)
    feedback_scope: Mapped[str] = mapped_column(
        String(30), default="project_feedback"
    )
    original_question: Mapped[str | None] = mapped_column(Text)
    original_answer: Mapped[str | None] = mapped_column(Text)
    corrected_answer: Mapped[str | None] = mapped_column(Text)
    feedback_text: Mapped[str | None] = mapped_column(Text)
    source_ids: Mapped[str | None] = mapped_column(JSON)
    source_types: Mapped[str | None] = mapped_column(JSON)
    approved_for_memory: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(String(36))
    confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    model_used: Mapped[str | None] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    answer_version: Mapped[str | None] = mapped_column(String(50))
    metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CIDFeedbackMemoryEntry(Base):
    __tablename__ = "cid_feedback_memory_entries"
    __table_args__ = (
        CheckConstraint(
            f"status IN ({', '.join(repr(s) for s in CID_FEEDBACK_STATUSES)})",
            name="ck_cfme_status",
        ),
        Index("ix_cfme_org_project", "organization_id", "project_id"),
        Index("ix_cfme_feedback_id", "feedback_id"),
        Index("ix_cfme_source", "source_type", "source_id"),
        Index("ix_cfme_approved", "approved_for_memory"),
        Index("ix_cfme_qdrant_point", "qdrant_point_id"),
        Index("ix_cfme_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    feedback_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cid_client_feedback.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text)
    approved_for_memory: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(String(36))
    qdrant_point_id: Mapped[str | None] = mapped_column(String(100))
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime)
    confidence: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CIDAnswerFeedbackEvent(Base):
    __tablename__ = "cid_answer_feedback_events"
    __table_args__ = (
        Index("ix_cafe_org_project", "organization_id", "project_id"),
        Index("ix_cafe_feedback_id", "feedback_id"),
        Index("ix_cafe_answer_id", "answer_id"),
        Index("ix_cafe_action", "action"),
        Index("ix_cafe_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    feedback_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cid_client_feedback.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    answer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    answer_version: Mapped[str | None] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class CIDProjectLearningRule(Base):
    __tablename__ = "cid_project_learning_rules"
    __table_args__ = (
        CheckConstraint(
            f"rule_type IN ({', '.join(repr(t) for t in CID_LEARNING_RULE_TYPES)})",
            name="ck_cplr_rule_type",
        ),
        Index("ix_cplr_org_project", "organization_id", "project_id"),
        Index("ix_cplr_rule_type", "rule_type"),
        Index("ix_cplr_active", "active"),
        Index("ix_cplr_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)
    rule_value: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36))
    metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CIDOrganizationLearningPreference(Base):
    __tablename__ = "cid_organization_learning_preferences"
    __table_args__ = (
        Index("ix_colp_org", "organization_id"),
        Index("ix_colp_preference_type", "preference_type"),
        Index("ix_colp_active", "active"),
        Index("ix_colp_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    preference_type: Mapped[str] = mapped_column(String(30), nullable=False)
    preference_value: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36))
    metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CIDFeedbackAudit(Base):
    __tablename__ = "cid_feedback_audit"
    __table_args__ = (
        CheckConstraint(
            f"action IN ({', '.join(repr(a) for a in CID_FEEDBACK_AUDIT_ACTIONS)})",
            name="ck_cfa_action",
        ),
        Index("ix_cfa_org_project", "organization_id", "project_id"),
        Index("ix_cfa_feedback_id", "feedback_id"),
        Index("ix_cfa_user_id", "user_id"),
        Index("ix_cfa_action", "action"),
        Index("ix_cfa_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    feedback_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cid_client_feedback.id", ondelete="SET NULL"), nullable=True
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    previous_status: Mapped[str | None] = mapped_column(String(20))
    new_status: Mapped[str | None] = mapped_column(String(20))
    previous_metadata_json: Mapped[str | None] = mapped_column(JSON)
    new_metadata_json: Mapped[str | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
