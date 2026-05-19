from __future__ import annotations

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ProjectVisualBible(Base):
    __tablename__ = "project_visual_bibles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True, unique=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    active_preset_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    selected_elements_json: Mapped[Optional[dict]] = mapped_column(
        JSON, default=dict
    )
    custom_prompt_tags_json: Mapped[Optional[list]] = mapped_column(
        JSON, default=list
    )
    negative_prompt_tags_json: Mapped[Optional[list]] = mapped_column(
        JSON, default=list
    )
    director_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    prompt_mode: Mapped[Optional[str]] = mapped_column(
        String(50), default="tag_soup"
    )
    target_model: Mapped[Optional[str]] = mapped_column(
        String(50), default="SDXL"
    )
    is_active: Mapped[Optional[bool]] = mapped_column(
        Boolean, default=True
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
