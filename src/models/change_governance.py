from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ProjectChangeRequest(Base):
    __tablename__ = "project_change_requests"
    __table_args__ = (
        Index("ix_change_request_project_id", "project_id"),
        Index("ix_change_request_source", "source_type", "source_id"),
        Index("ix_change_request_target", "target_module"),
        Index("ix_change_request_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    source_id: Mapped[Optional[str]] = mapped_column(String(36))
    target_module: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    change_type: Mapped[str] = mapped_column(
        String(20),
        default="updated",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default="medium",
    )
    title: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    before_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    after_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    recommended_action: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20),
        default="proposed",
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    approved_by: Mapped[Optional[str]] = mapped_column(String(36))
    rejected_by: Mapped[Optional[str]] = mapped_column(String(36))
    approval_comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class ProjectApproval(Base):
    __tablename__ = "project_approvals"
    __table_args__ = (
        Index("ix_approval_project_id", "project_id"),
        Index("ix_approval_change_request_id", "change_request_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    change_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("project_change_requests.id", ondelete="CASCADE"), nullable=False
    )
    approver_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    approver_role: Mapped[Optional[str]] = mapped_column(String(30))
    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class ApprovedProjectBaseline(Base):
    __tablename__ = "approved_project_baselines"
    __table_args__ = (
        Index("ix_baseline_project_id", "project_id"),
        Index("ix_baseline_type", "baseline_type"),
        Index("ix_baseline_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    baseline_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_label: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
    )
    approved_by: Mapped[Optional[str]] = mapped_column(String(36))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class PlannedShot(Base):
    __tablename__ = "planned_shots"
    __table_args__ = (
        Index("ix_planned_shot_project_id", "project_id"),
        Index("ix_planned_shot_sequence", "project_id", "sequence_number"),
        Index("ix_planned_shot_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)
    scene_number: Mapped[Optional[int]] = mapped_column(Integer)
    shot_number: Mapped[int] = mapped_column(Integer, default=1)
    shot_code: Mapped[Optional[str]] = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    shot_type: Mapped[Optional[str]] = mapped_column(
        String(30), default="general"
    )
    camera_movement: Mapped[Optional[str]] = mapped_column(String(50))
    lens_suggestion: Mapped[Optional[str]] = mapped_column(String(100))
    characters_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    location: Mapped[Optional[str]] = mapped_column(String(100))
    day_night: Mapped[str] = mapped_column(String(10), default="day")
    estimated_duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    priority: Mapped[str] = mapped_column(
        String(20), default="recommended"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="proposed"
    )
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    source_storyboard_shot_id: Mapped[Optional[str]] = mapped_column(String(36))
    approved_by: Mapped[Optional[str]] = mapped_column(String(36))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class ShootingPlan(Base):
    __tablename__ = "shooting_plans"
    __table_args__ = (
        Index("ix_shooting_plan_project_id", "project_id"),
        Index("ix_shooting_plan_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(
        String(20), default="draft"
    )
    approved_by: Mapped[Optional[str]] = mapped_column(String(36))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ShootingPlanItem(Base):
    __tablename__ = "shooting_plan_items"
    __table_args__ = (
        Index("ix_plan_item_plan_id", "shooting_plan_id"),
        Index("ix_plan_item_day", "shooting_day"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    shooting_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shooting_plans.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    shooting_day: Mapped[int] = mapped_column(Integer, default=1)
    date_planned: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sequence_number: Mapped[int] = mapped_column(Integer)
    scene_number: Mapped[Optional[int]] = mapped_column(Integer)
    shot_number: Mapped[Optional[int]] = mapped_column(Integer)
    planned_shot_id: Mapped[Optional[str]] = mapped_column(String(36))
    location: Mapped[Optional[str]] = mapped_column(String(100))
    day_night: Mapped[str] = mapped_column(String(10))
    characters_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    estimated_time_minutes: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(
        String(20), default="planned"
    )
    linked_take_ids_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)


CHANGE_REQUEST_SOURCE_TYPES = [
    "script_version",
    "breakdown",
    "budget",
    "storyboard",
    "shotlist",
    "shooting_plan",
    "reports",
]

CHANGE_REQUEST_TARGET_MODULES = [
    "script",
    "breakdown",
    "budget",
    "storyboard",
    "shotlist",
    "shooting_plan",
    "editorial",
    "funding",
    "producer_pack",
    "distribution",
]

CHANGE_REQUEST_STATUSES = [
    "proposed",
    "pending_approval",
    "approved",
    "rejected",
    "applied",
    "cancelled",
]

CHANGE_REQUEST_SEVERITIES = ["low", "medium", "high", "critical"]

CHANGE_REQUEST_TYPES = ["created", "updated", "deleted", "recalculated", "regenerated", "invalidated"]

BASELINE_TYPES = [
    "script",
    "breakdown",
    "budget",
    "storyboard",
    "shotlist",
    "shooting_plan",
]

BASELINE_STATUSES = ["active", "archived", "superseded"]

SHOT_STATUSES = [
    "proposed",
    "approved",
    "rejected",
    "shot",
    "pending_pickup",
    "not_shot",
    "cancelled",
]

SHOT_PRIORITIES = ["essential", "recommended", "optional"]

SHOT_TYPES = [
    "general",
    "plano_medio",
    "primer_plano",
    "detalle",
    "recurso",
    "contrap_plano",
    "insert",
]

PLANNING_ITEM_STATUSES = [
    "planned",
    "shot",
    "partially_shot",
    "not_shot",
    "cancelled",
    "rescheduled",
]