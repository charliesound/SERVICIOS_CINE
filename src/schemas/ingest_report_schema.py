from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class _ReportBase(BaseModel):
    organization_id: Optional[str] = None
    project_id: str
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    report_date: date
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None


class _ReportMeta(BaseModel):
    id: str
    organization_id: str
    project_id: str
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    report_date: date
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CameraReportCreate(_ReportBase):
    camera_label: str
    operator_name: Optional[str] = None
    card_or_mag: str
    take_reference: Optional[str] = None
    notes: str = ""
    incidents: str = ""


class CameraReportUpdate(BaseModel):
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    camera_label: Optional[str] = None
    operator_name: Optional[str] = None
    card_or_mag: Optional[str] = None
    take_reference: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None


class CameraReportResponse(_ReportMeta):
    camera_label: str
    operator_name: Optional[str] = None
    card_or_mag: str
    take_reference: Optional[str] = None
    notes: str
    incidents: str


class CameraReportListResponse(BaseModel):
    items: List[CameraReportResponse]


class SoundReportCreate(_ReportBase):
    sound_roll: str
    mixer_name: Optional[str] = None
    boom_operator: Optional[str] = None
    sample_rate: Optional[str] = None
    bit_depth: Optional[str] = None
    timecode_notes: Optional[str] = None
    notes: str = ""
    incidents: str = ""


class SoundReportUpdate(BaseModel):
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    sound_roll: Optional[str] = None
    mixer_name: Optional[str] = None
    boom_operator: Optional[str] = None
    sample_rate: Optional[str] = None
    bit_depth: Optional[str] = None
    timecode_notes: Optional[str] = None
    notes: Optional[str] = None
    incidents: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None


class SoundReportResponse(_ReportMeta):
    sound_roll: str
    mixer_name: Optional[str] = None
    boom_operator: Optional[str] = None
    sample_rate: Optional[str] = None
    bit_depth: Optional[str] = None
    timecode_notes: Optional[str] = None
    notes: str
    incidents: str


class SoundReportListResponse(BaseModel):
    items: List[SoundReportResponse]


class ScriptNoteCreate(_ReportBase):
    best_take: Optional[str] = None
    continuity_notes: str
    editor_note: Optional[str] = None


class ScriptNoteUpdate(BaseModel):
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    best_take: Optional[str] = None
    continuity_notes: Optional[str] = None
    editor_note: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None


class ScriptNoteResponse(_ReportMeta):
    best_take: Optional[str] = None
    continuity_notes: str
    editor_note: Optional[str] = None


class ScriptNoteListResponse(BaseModel):
    items: List[ScriptNoteResponse]


class DirectorNoteCreate(_ReportBase):
    preferred_take: Optional[str] = None
    intention_note: str
    pacing_note: Optional[str] = None
    coverage_note: Optional[str] = None


class DirectorNoteUpdate(BaseModel):
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    preferred_take: Optional[str] = None
    intention_note: Optional[str] = None
    pacing_note: Optional[str] = None
    coverage_note: Optional[str] = None
    report_date: Optional[date] = None
    document_asset_id: Optional[str] = None
    media_asset_id: Optional[str] = None


class DirectorNoteResponse(_ReportMeta):
    preferred_take: Optional[str] = None
    intention_note: str
    pacing_note: Optional[str] = None
    coverage_note: Optional[str] = None


class DirectorNoteListResponse(BaseModel):
    items: List[DirectorNoteResponse]
