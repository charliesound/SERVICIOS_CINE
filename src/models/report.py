from datetime import date, datetime, timezone
import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def current_date() -> date:
    return datetime.now(timezone.utc).date()


class ReportBaseMixin:
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    shooting_day_id = Column(String(36), nullable=True)
    sequence_id = Column(String(36), nullable=True)
    scene_id = Column(String(36), nullable=True)
    shot_id = Column(String(36), nullable=True)
    report_date = Column(Date, default=current_date, nullable=False)
    document_asset_id = Column(
        String(36),
        ForeignKey("document_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    media_asset_id = Column(
        String(36),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by = Column(String(36), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )


class CameraReport(Base, ReportBaseMixin):
    __tablename__ = "camera_reports"
    __table_args__ = (
        Index("ix_camera_reports_org_project", "organization_id", "project_id"),
        Index("ix_camera_reports_report_date", "report_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    camera_label = Column(String(255), default="", nullable=False)
    operator_name = Column(String(255), nullable=True)
    card_or_mag = Column(String(255), default="", nullable=False)
    take_reference = Column(String(255), nullable=True)
    notes = Column(Text, default="", nullable=False)
    incidents = Column(Text, default="", nullable=False)

    document_asset = relationship("DocumentAsset")


class SoundReport(Base, ReportBaseMixin):
    __tablename__ = "sound_reports"
    __table_args__ = (
        Index("ix_sound_reports_org_project", "organization_id", "project_id"),
        Index("ix_sound_reports_report_date", "report_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sound_roll = Column(String(255), default="", nullable=False)
    mixer_name = Column(String(255), nullable=True)
    boom_operator = Column(String(255), nullable=True)
    sample_rate = Column(String(100), nullable=True)
    bit_depth = Column(String(100), nullable=True)
    timecode_notes = Column(Text, nullable=True)
    notes = Column(Text, default="", nullable=False)
    incidents = Column(Text, default="", nullable=False)

    document_asset = relationship("DocumentAsset")


class ScriptNote(Base, ReportBaseMixin):
    __tablename__ = "script_notes"
    __table_args__ = (
        Index("ix_script_notes_org_project", "organization_id", "project_id"),
        Index("ix_script_notes_report_date", "report_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    best_take = Column(String(255), nullable=True)
    continuity_notes = Column(Text, default="", nullable=False)
    editor_note = Column(Text, nullable=True)

    document_asset = relationship("DocumentAsset")


class DirectorNote(Base, ReportBaseMixin):
    __tablename__ = "director_notes"
    __table_args__ = (
        Index("ix_director_notes_org_project", "organization_id", "project_id"),
        Index("ix_director_notes_report_date", "report_date"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    preferred_take = Column(String(255), nullable=True)
    intention_note = Column(Text, default="", nullable=False)
    pacing_note = Column(Text, nullable=True)
    coverage_note = Column(Text, nullable=True)

    document_asset = relationship("DocumentAsset")
