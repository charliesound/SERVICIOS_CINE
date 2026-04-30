from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AssemblyCut(Base):
    __tablename__ = "assembly_cuts"
    __table_args__ = (
        Index("ix_assembly_cuts_org_project", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="draft")
    source_scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    items: Mapped[list["AssemblyCutItem"]] = relationship(
        "AssemblyCutItem",
        back_populates="assembly_cut",
        cascade="all, delete-orphan",
        order_by="AssemblyCutItem.order_index",
    )


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    scene_id: Mapped[Optional[str]] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500))
    duration_seconds: Mapped[Optional[float]] = mapped_column(String(20))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class Take(Base):
    __tablename__ = "takes"
    __table_args__ = (
        Index("ix_takes_org_project", "organization_id", "project_id"),
        Index("ix_takes_scene_shot_take", "project_id", "scene_number", "shot_number", "take_number"),
        Index("ix_takes_camera_asset", "camera_media_asset_id"),
        Index("ix_takes_sound_asset", "sound_media_asset_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scene_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shot_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    take_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    camera_roll: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sound_roll: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    camera_media_asset_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True
    )
    sound_media_asset_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True
    )
    camera_report_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("camera_reports.id", ondelete="SET NULL"), nullable=True
    )
    sound_report_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("sound_reports.id", ondelete="SET NULL"), nullable=True
    )
    script_note_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("script_notes.id", ondelete="SET NULL"), nullable=True
    )
    director_note_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("director_notes.id", ondelete="SET NULL"), nullable=True
    )
    video_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    audio_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_timecode: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    end_timecode: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    audio_timecode_start: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    audio_time_reference_samples: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    audio_sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    audio_channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    audio_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_scene: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    audio_take: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    audio_circled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    audio_metadata_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audio_metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dual_system_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sync_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sync_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sync_warning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_frames: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    slate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    script_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    director_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    camera_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sound_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reconciliation_status: Mapped[Optional[str]] = mapped_column(String(50), default="partial")
    is_circled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_best: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recommended_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conflict_flags_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    assembly_items: Mapped[list["AssemblyCutItem"]] = relationship(
        "AssemblyCutItem",
        back_populates="take",
    )


class AssemblyCutItem(Base):
    __tablename__ = "assembly_cut_items"
    __table_args__ = (
        Index("ix_assembly_cut_items_cut_order", "assembly_cut_id", "order_index"),
        Index("ix_assembly_cut_items_project_scene_shot_take", "project_id", "scene_number", "shot_number", "take_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    assembly_cut_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assembly_cuts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    take_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("takes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scene_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shot_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    take_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_media_asset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    audio_media_asset_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    start_tc: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    end_tc: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timeline_in: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timeline_out: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_frames: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recommended_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), nullable=False
    )

    assembly_cut: Mapped[AssemblyCut] = relationship("AssemblyCut", back_populates="items")
    take: Mapped[Optional[Take]] = relationship("Take", back_populates="assembly_items")
