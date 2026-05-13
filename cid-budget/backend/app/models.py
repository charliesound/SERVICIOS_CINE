import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BudgetEstimate(Base):
    __tablename__ = "budget_estimates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(64), index=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    budget_level: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total_min: Mapped[float] = mapped_column(Float, default=0)
    total_estimated: Mapped[float] = mapped_column(Float, default=0)
    total_max: Mapped[float] = mapped_column(Float, default=0)
    contingency_percent: Mapped[float] = mapped_column(Float, default=10)
    assumptions_json: Mapped[dict] = mapped_column(JSON, default=list)
    role_summaries_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class BudgetLineItem(Base):
    __tablename__ = "budget_line_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    budget_estimate_id: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(50))
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[float] = mapped_column(Float, default=1)
    unit_cost_min: Mapped[float] = mapped_column(Float, default=0)
    unit_cost_estimated: Mapped[float] = mapped_column(Float, default=0)
    unit_cost_max: Mapped[float] = mapped_column(Float, default=0)
    total_min: Mapped[float] = mapped_column(Float, default=0)
    total_estimated: Mapped[float] = mapped_column(Float, default=0)
    total_max: Mapped[float] = mapped_column(Float, default=0)
    source: Mapped[str] = mapped_column(String(50), default="default_rule")
    confidence: Mapped[str] = mapped_column(String(20), default="medium")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
