from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ProducerPitchPack(Base):
    __tablename__ = "producer_pitch_packs"
    __table_args__ = (
        Index("ix_pitch_pack_project", "project_id"),
        Index("ix_pitch_pack_org", "organization_id"),
        Index("ix_pitch_pack_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    source_budget_id: Mapped[Optional[str]] = mapped_column(String(36))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    logline: Mapped[Optional[str]] = mapped_column(Text)
    short_synopsis: Mapped[Optional[str]] = mapped_column(Text)
    long_synopsis: Mapped[Optional[str]] = mapped_column(Text)
    intention_note: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(50))
    format: Mapped[Optional[str]] = mapped_column(String(30))
    tone: Mapped[Optional[str]] = mapped_column(String(50))
    target_audience: Mapped[Optional[str]] = mapped_column(String(100))
    commercial_strengths_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    production_needs_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    budget_summary_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    funding_summary_json: Mapped[Optional[str]] =mapped_column(JSON, default=dict)
    storyboard_selection_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    risks_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    generated_sections_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProducerPitchSection(Base):
    __tablename__ = "producer_pitch_sections"
    __table_args__ = (
        Index("ix_pitch_section_pack", "pitch_pack_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    pitch_pack_id: Mapped[str] = mapped_column(String(36), ForeignKey("producer_pitch_packs.id", ondelete="CASCADE"), nullable=False)
    section_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    metadata_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


PITCH_PACK_STATUSES = ["draft", "generated", "approved", "archived", "needs_review"]

PITCH_SECTION_TYPES = [
    "logline",
    "short_synopsis",
    "long_synopsis",
    "intention_note",
    "genre_format",
    "target_audience",
    "commercial_strengths",
    "production_needs",
    "budget_summary",
    "funding_summary",
    "storyboard_selection",
    "risks",
]

SECTION_ORDER = {
    "logline": 1,
    "short_synopsis": 2,
    "long_synopsis": 3,
    "intention_note": 4,
    "genre_format": 5,
    "target_audience": 6,
    "commercial_strengths": 7,
    "production_needs": 8,
    "budget_summary": 9,
    "funding_summary": 10,
    "storyboard_selection": 11,
    "risks": 12,
}