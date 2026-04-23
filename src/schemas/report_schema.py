from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class ReportBaseCreate(BaseModel):
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None

    @field_validator(
        "organization_id",
        "project_id",
        "shooting_day_id",
        "sequence_id",
        "scene_id",
        "shot_id",
        "document_asset_id",
        "media_asset_id",
    )
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class ReportBaseUpdate(BaseModel):
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None

    @field_validator(
        "shooting_day_id",
        "sequence_id",
        "scene_id",
        "shot_id",
        "document_asset_id",
        "media_asset_id",
    )
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class ReportBaseResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    shooting_day_id: Optional[str]
    sequence_id: Optional[str]
    scene_id: Optional[str]
    shot_id: Optional[str]
    report_date: date
    document_asset_id: Optional[str]
    media_asset_id: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime


class CameraReportCreate(ReportBaseCreate):
    camera_label: Optional[str] = None
    operator_name: Optional[str] = None
    card_or_mag: Optional[str] = None
    take_reference: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None

    @field_validator(
        "camera_label",
        "operator_name",
        "card_or_mag",
        "take_reference",
        "notes",
        "incidents",
    )
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CameraReportUpdate(ReportBaseUpdate):
    camera_label: Optional[str] = None
    operator_name: Optional[str] = None
    card_or_mag: Optional[str] = None
    take_reference: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None

    @field_validator(
        "camera_label",
        "operator_name",
        "card_or_mag",
        "take_reference",
        "notes",
        "incidents",
    )
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CameraReportResponse(ReportBaseResponse):
    camera_label: str
    operator_name: Optional[str]
    card_or_mag: str
    take_reference: Optional[str]
    notes: str
    incidents: str


class CameraReportListResponse(BaseModel):
    reports: List[CameraReportResponse] = Field(default_factory=list)


class SoundReportCreate(ReportBaseCreate):
    sound_roll: Optional[str] = None
    mixer_name: Optional[str] = None
    boom_operator: Optional[str] = None
    sample_rate: Optional[str] = None
    bit_depth: Optional[str] = None
    timecode_notes: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None

    @field_validator(
        "sound_roll",
        "mixer_name",
        "boom_operator",
        "sample_rate",
        "bit_depth",
        "timecode_notes",
        "notes",
        "incidents",
    )
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class SoundReportUpdate(ReportBaseUpdate):
    sound_roll: Optional[str] = None
    mixer_name: Optional[str] = None
    boom_operator: Optional[str] = None
    sample_rate: Optional[str] = None
    bit_depth: Optional[str] = None
    timecode_notes: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None

    @field_validator(
        "sound_roll",
        "mixer_name",
        "boom_operator",
        "sample_rate",
        "bit_depth",
        "timecode_notes",
        "notes",
        "incidents",
    )
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class SoundReportResponse(ReportBaseResponse):
    sound_roll: str
    mixer_name: Optional[str]
    boom_operator: Optional[str]
    sample_rate: Optional[str]
    bit_depth: Optional[str]
    timecode_notes: Optional[str]
    notes: str
    incidents: str


class SoundReportListResponse(BaseModel):
    reports: List[SoundReportResponse] = Field(default_factory=list)


class ScriptNoteCreate(ReportBaseCreate):
    best_take: Optional[str] = None
    continuity_notes: Optional[str] = None
    editor_note: Optional[str] = None

    @field_validator("best_take", "continuity_notes", "editor_note")
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class ScriptNoteUpdate(ReportBaseUpdate):
    best_take: Optional[str] = None
    continuity_notes: Optional[str] = None
    editor_note: Optional[str] = None

    @field_validator("best_take", "continuity_notes", "editor_note")
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class ScriptNoteResponse(ReportBaseResponse):
    best_take: Optional[str]
    continuity_notes: str
    editor_note: Optional[str]


class ScriptNoteListResponse(BaseModel):
    reports: List[ScriptNoteResponse] = Field(default_factory=list)


class DirectorNoteCreate(ReportBaseCreate):
    preferred_take: Optional[str] = None
    intention_note: Optional[str] = None
    pacing_note: Optional[str] = None
    coverage_note: Optional[str] = None

    @field_validator("preferred_take", "intention_note", "pacing_note", "coverage_note")
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DirectorNoteUpdate(ReportBaseUpdate):
    preferred_take: Optional[str] = None
    intention_note: Optional[str] = None
    pacing_note: Optional[str] = None
    coverage_note: Optional[str] = None

    @field_validator("preferred_take", "intention_note", "pacing_note", "coverage_note")
    @classmethod
    def validate_text_fields(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DirectorNoteResponse(ReportBaseResponse):
    preferred_take: Optional[str]
    intention_note: str
    pacing_note: Optional[str]
    coverage_note: Optional[str]


class DirectorNoteListResponse(BaseModel):
    reports: List[DirectorNoteResponse] = Field(default_factory=list)
