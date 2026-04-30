from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class DistributionPack(Base):
    __tablename__ = "distribution_packs"
    __table_args__ = (
        Index("ix_dist_pack_project", "project_id"),
        Index("ix_dist_pack_org", "organization_id"),
        Index("ix_dist_pack_type", "pack_type"),
        Index("ix_dist_pack_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_producer_pitch_id: Mapped[Optional[str]] = mapped_column(String(36))
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    pack_type: Mapped[str] = mapped_column(String(20), default="general_sales")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    logline: Mapped[Optional[str]] = mapped_column(Text)
    short_synopsis: Mapped[Optional[str]] = mapped_column(Text)
    commercial_positioning: Mapped[Optional[str]] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(String(100))
    comparable_titles_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    release_strategy_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    exploitation_windows_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    territory_strategy_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    marketing_hooks_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    available_materials_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    technical_specs_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    sales_arguments_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    risks_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    generated_sections_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DistributionPackSection(Base):
    __tablename__ = "distribution_pack_sections"
    __table_args__ = (
        Index("ix_dist_section_pack", "distribution_pack_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    distribution_pack_id: Mapped[str] = mapped_column(String(36), ForeignKey("distribution_packs.id", ondelete="CASCADE"), nullable=False)
    section_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    metadata_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SalesTarget(Base):
    __tablename__ = "sales_targets"
    __table_args__ = (
        Index("ix_sales_target_org", "organization_id"),
        Index("ix_sales_target_type", "target_type"),
        Index("ix_sales_target_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), default="distributor")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(50))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    genres_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    formats_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(20), default="manual")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectSalesOpportunity(Base):
    __tablename__ = "project_sales_opportunities"
    __table_args__ = (
        Index("ix_sales_opp_project", "project_id"),
        Index("ix_sales_opp_target", "sales_target_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sales_target_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("sales_targets.id"))
    distribution_pack_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("distribution_packs.id"))
    target_type: Mapped[str] = mapped_column(String(20), default="distributor")
    status: Mapped[str] = mapped_column(String(20), default="suggested")
    fit_score: Mapped[int] = mapped_column(Integer, default=0)
    fit_summary: Mapped[Optional[str]] = mapped_column(Text)
    recommended_pitch_angle: Mapped[Optional[str]] = mapped_column(Text)
    next_action: Mapped[Optional[str]] = mapped_column(String(100))
    last_contact_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


PACK_TYPE = ["distributor", "sales_agent", "festival", "cinema", "platform", "general_sales"]

PACK_STATUS = ["draft", "generated", "approved", "archived", "needs_review"]

SALES_TARGET_TYPES = ["distributor", "sales_agent", "cinema", "platform", "festival", "market"]

SALES_OPPORTUNITY_STATUS = ["suggested", "saved", "contacted", "follow_up", "interested", "rejected", "closed"]

DISTRIBUTION_SECTION_TYPES = [
    "logline",
    "short_synopsis",
    "commercial_positioning",
    "target_audience",
    "comparables",
    "release_strategy",
    "exploitation_windows",
    "territory_strategy",
    "marketing_hooks",
    "available_materials",
    "technical_specs",
    "sales_arguments",
    "risks",
]