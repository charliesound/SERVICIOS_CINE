from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class EditorialMediaAsset(BaseModel):
    id: str
    file_name: str
    file_path: str
    asset_type: Literal["video", "audio", "other"] = "other"
    duration_frames: int = 0
    fps: float = 24.0
    start_timecode: str = "00:00:00:00"
    end_timecode: Optional[str] = None
    channels: Optional[int] = None
    sample_rate: Optional[int] = None
    camera_roll: Optional[str] = None
    sound_roll: Optional[str] = None


class CameraReportEntry(BaseModel):
    card_or_mag: str
    clip_name: str
    scene: int
    shot: int
    take: int
    fps: float = 24.0
    lens: Optional[str] = None
    aperture: Optional[str] = None
    notes: Optional[str] = None


class SoundReportEntry(BaseModel):
    sound_roll: str
    file_name: str
    scene: int
    shot: Optional[int] = None
    take: int
    timecode_start: str = "00:00:00:00"
    tracks_count: int = 1
    notes: Optional[str] = None


class ScriptSupervisorNote(BaseModel):
    scene_number: int
    shot_number: int
    take_number: int
    is_circled: bool = False
    continuity_notes: Optional[str] = None
    editor_note: Optional[str] = None


class DirectorNote(BaseModel):
    scene_number: int
    shot_number: int
    take_number: int
    is_preferred: bool = False
    intention_note: Optional[str] = None
    pacing_note: Optional[str] = None


class SlateMatch(BaseModel):
    scene_number: int
    shot_number: int
    take_number: int
    confidence: float = Field(ge=0.0, le=1.0)
    matching_method: str
    warnings: list[str] = Field(default_factory=list)


class SyncCandidate(BaseModel):
    audio_asset_id: str
    audio_filename: str
    timecode_offset_frames: int = 0
    sync_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    sync_method: str = "unresolved"


class TakeDecision(BaseModel):
    take_id: str
    scene_number: int
    shot_number: int
    take_number: int
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_recommended: bool = False
    recommended_reason: str = "not_scored"
    camera_asset_id: Optional[str] = None
    sound_asset_id: Optional[str] = None


class AssemblyClip(BaseModel):
    id: str
    take_id: str
    clip_name: str
    source_media_asset_id: str
    audio_media_asset_id: Optional[str] = None
    timeline_in: int = 0
    timeline_out: int = 0
    duration_frames: int = 0
    fps: float = 24.0
    start_tc: str = "00:00:00:00"
    timecode_offset_frames: int = 0
    assigned_tracks: list[str] = Field(default_factory=lambda: ["V1", "A1"])


class AssemblySequence(BaseModel):
    id: str
    name: str
    scene_number: int
    clips: list[AssemblyClip] = Field(default_factory=list)


class AssemblyTimeline(BaseModel):
    id: str
    project_id: str
    name: str
    fps: float = 24.0
    total_duration_frames: int = 0
    sequences: list[AssemblySequence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RelinkReport(BaseModel):
    resolved_media_count: int = 0
    offline_media_count: int = 0
    missing_media_count: int = 0
    path_mappings: dict[str, str] = Field(default_factory=dict)


class MissingMediaReport(BaseModel):
    clip_name: str
    role: Literal["video", "audio"]
    expected_filename: str
    scene: int
    shot: int
    take: int


class NLEExportRequest(BaseModel):
    nle_type: Literal["resolve", "premiere", "avid"]
    audio_mode: Literal["conservative", "linked_multitrack"] = "conservative"
    target_platform: Literal["windows", "mac", "linux", "offline"] = "windows"
    destination_root_path: Optional[str] = None
    include_relink_report: bool = True
    timeline: Optional[AssemblyTimeline] = None
    media_assets: list[EditorialMediaAsset] = Field(default_factory=list)


class NLEExportResult(BaseModel):
    nle_type: str
    export_format: str
    file_name: str
    file_bytes_b64: str
    artifact_path: Optional[str] = None
    artifact_url: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    manifest: dict[str, Any] = Field(default_factory=dict)


class ScanMediaRequest(BaseModel):
    root_directory_path: Optional[str] = None
    root_paths: list[str] = Field(default_factory=list)
    recursive: bool = True
    max_files: int = Field(default=1000, ge=1, le=10000)

    def all_roots(self) -> list[str]:
        roots = list(self.root_paths)
        if self.root_directory_path:
            roots.insert(0, self.root_directory_path)
        return roots


class ScanMediaResponse(BaseModel):
    project_id: str
    scanned_roots: list[str] = Field(default_factory=list)
    assets: list[EditorialMediaAsset] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ImportReportsRequest(BaseModel):
    camera_reports: list[CameraReportEntry] = Field(default_factory=list)
    sound_reports: list[SoundReportEntry] = Field(default_factory=list)
    script_notes: list[ScriptSupervisorNote] = Field(default_factory=list)
    director_notes: list[DirectorNote] = Field(default_factory=list)


class ImportReportsResponse(BaseModel):
    project_id: str
    report_id: str
    imported_counts: dict[str, int]
    warnings: list[str] = Field(default_factory=list)


class MatchTakesRequest(ImportReportsRequest):
    media_assets: list[EditorialMediaAsset] = Field(default_factory=list)


class MatchTakesResponse(BaseModel):
    project_id: str
    slate_matches: list[SlateMatch] = Field(default_factory=list)
    take_decisions: list[TakeDecision] = Field(default_factory=list)
    sync_candidates: list[SyncCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BuildAssemblyRequest(BaseModel):
    take_decisions: list[TakeDecision] = Field(default_factory=list)
    media_assets: list[EditorialMediaAsset] = Field(default_factory=list)
    name: str = "CID Neutral Assembly"
    fps: float = 24.0
    allow_missing_audio: bool = True


class ReportLookupResponse(BaseModel):
    project_id: str
    report_id: str
    status: str
    relink_report: Optional[RelinkReport] = None
    missing_media: list[MissingMediaReport] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
