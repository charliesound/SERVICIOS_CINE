from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class StoryboardShot(Base):
    __tablename__ = "storyboard_shots"
    __table_args__ = (
        Index(
            "ix_storyboard_shots_org_project_sequence",
            "organization_id",
            "project_id",
            "sequence_id",
        ),
        Index(
            "ix_storyboard_shots_project_sequence_order",
            "project_id",
            "sequence_id",
            "sequence_order",
        ),
        Index(
            "ix_storyboard_shots_project_active_sequence",
            "project_id",
            "is_active",
            "sequence_id",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sequence_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scene_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    scene_heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    narrative_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    shot_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    visual_mode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    generation_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    generation_job_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="storyboard_shots",
        primaryjoin="foreign(StoryboardShot.project_id) == Project.id",
    )
    media_asset = relationship(
        "MediaAsset",
        primaryjoin="foreign(StoryboardShot.asset_id) == MediaAsset.id",
        viewonly=True,
    )
