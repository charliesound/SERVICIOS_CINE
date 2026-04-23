from datetime import datetime
import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String

from database import Base


class CameraReport(Base):
    __tablename__ = "camera_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    shooting_day_id = Column(String, nullable=True)
    sequence_id = Column(String, nullable=True)
    scene_id = Column(String, nullable=True)
    shot_id = Column(String, nullable=True)
    camera_label = Column(String, nullable=False)
    operator_name = Column(String, nullable=True)
    card_or_mag = Column(String, nullable=False)
    take_reference = Column(String, nullable=True)
    notes = Column(String, nullable=False, default="")
    incidents = Column(String, nullable=False, default="")
    report_date = Column(Date, nullable=False)
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=True, index=True
    )
    media_asset_id = Column(
        String, ForeignKey("media_assets.id"), nullable=True, index=True
    )
    created_by = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SoundReport(Base):
    __tablename__ = "sound_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    shooting_day_id = Column(String, nullable=True)
    sequence_id = Column(String, nullable=True)
    scene_id = Column(String, nullable=True)
    shot_id = Column(String, nullable=True)
    sound_roll = Column(String, nullable=False)
    mixer_name = Column(String, nullable=True)
    boom_operator = Column(String, nullable=True)
    sample_rate = Column(String, nullable=True)
    bit_depth = Column(String, nullable=True)
    timecode_notes = Column(String, nullable=True)
    notes = Column(String, nullable=False, default="")
    incidents = Column(String, nullable=False, default="")
    report_date = Column(Date, nullable=False)
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=True, index=True
    )
    media_asset_id = Column(
        String, ForeignKey("media_assets.id"), nullable=True, index=True
    )
    created_by = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScriptNote(Base):
    __tablename__ = "script_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    shooting_day_id = Column(String, nullable=True)
    sequence_id = Column(String, nullable=True)
    scene_id = Column(String, nullable=True)
    shot_id = Column(String, nullable=True)
    best_take = Column(String, nullable=True)
    continuity_notes = Column(String, nullable=False)
    editor_note = Column(String, nullable=True)
    report_date = Column(Date, nullable=False)
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=True, index=True
    )
    media_asset_id = Column(
        String, ForeignKey("media_assets.id"), nullable=True, index=True
    )
    created_by = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DirectorNote(Base):
    __tablename__ = "director_notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    shooting_day_id = Column(String, nullable=True)
    sequence_id = Column(String, nullable=True)
    scene_id = Column(String, nullable=True)
    shot_id = Column(String, nullable=True)
    preferred_take = Column(String, nullable=True)
    intention_note = Column(String, nullable=False)
    pacing_note = Column(String, nullable=True)
    coverage_note = Column(String, nullable=True)
    report_date = Column(Date, nullable=False)
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=True, index=True
    )
    media_asset_id = Column(
        String, ForeignKey("media_assets.id"), nullable=True, index=True
    )
    created_by = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
