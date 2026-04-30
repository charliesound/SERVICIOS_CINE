from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class BudgetEstimate(Base):
    __tablename__ = "budget_estimates"
    __table_args__ = (
        Index("ix_budget_estimate_project_id", "project_id"),
        Index("ix_budget_estimate_org_project", "organization_id", "project_id"),
        Index("ix_budget_estimate_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    source_breakdown_id: Mapped[Optional[str]] = mapped_column(String(36))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    budget_level: Mapped[str] = mapped_column(
        String(20), default="medium"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft"
    )
    total_min: Mapped[float] = mapped_column(Float, default=0.0)
    total_estimated: Mapped[float] = mapped_column(Float, default=0.0)
    total_max: Mapped[float] = mapped_column(Float, default=0.0)
    contingency_percent: Mapped[float] = mapped_column(Float, default=0.0)
    assumptions_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    role_summaries_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"
    __table_args__ = (
        Index("ix_budget_line_item_estimate_id", "budget_estimate_id"),
        Index("ix_budget_line_item_category", "category"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    budget_estimate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("budget_estimates.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost_min: Mapped[float] = mapped_column(Float, default=0.0)
    unit_cost_estimated: Mapped[float] = mapped_column(Float, default=0.0)
    unit_cost_max: Mapped[float] = mapped_column(Float, default=0.0)
    total_min: Mapped[float] = mapped_column(Float, default=0.0)
    total_estimated: Mapped[float] = mapped_column(Float, default=0.0)
    total_max: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(
        String(20), default="default_rule"
    )
    confidence: Mapped[str] = mapped_column(
        String(20), default="medium"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


BUDGET_LEVELS = ["low", "medium", "high", "custom"]

BUDGET_STATUSES = ["draft", "active", "archived", "needs_review"]

BUDGET_SOURCES = ["script", "breakdown", "manual", "default_rule"]

CONFIDENCE_LEVELS = ["low", "medium", "high"]