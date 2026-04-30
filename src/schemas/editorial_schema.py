from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EditorialTakeResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    scene_number: Optional[int] = None
    shot_number: Optional[int] = None
    take_number: Optional[int] = None
    camera_roll: Optional[str] = None
    sound_roll: Optional[str] = None
    camera_media_asset_id: Optional[str] = None
    sound_media_asset_id: Optional[str] = None
    camera_report_id: Optional[str] = None
    sound_report_id: Optional[str] = None
    script_note_id: Optional[str] = None
    director_note_id: Optional[str] = None
    video_filename: Optional[str] = None
    audio_filename: Optional[str] = None
    start_timecode: Optional[str] = None
    end_timecode: Optional[str] = None
    audio_timecode_start: Optional[str] = None
    audio_time_reference_samples: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    audio_duration_seconds: Optional[float] = None
    audio_fps: Optional[float] = None
    audio_scene: Optional[str] = None
    audio_take: Optional[str] = None
    audio_circled: Optional[bool] = None
    audio_metadata_status: Optional[str] = None
    audio_metadata: Optional[dict[str, Any]] = None
    dual_system_status: Optional[str] = None
    sync_confidence: Optional[float] = None
    sync_method: Optional[str] = None
    sync_warning: Optional[str] = None
    duration_frames: Optional[int] = None
    fps: Optional[float] = None
    slate: Optional[str] = None
    script_status: Optional[str] = None
    director_status: Optional[str] = None
    camera_status: Optional[str] = None
    sound_status: Optional[str] = None
    reconciliation_status: Optional[str] = None
    is_circled: bool = False
    is_best: bool = False
    is_recommended: bool = False
    score: float = 0.0
    recommended_reason: Optional[str] = None
    conflict_flags: list[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EditorialTakeListResponse(BaseModel):
    takes: list[EditorialTakeResponse] = Field(default_factory=list)


class EditorialReconcileResponse(BaseModel):
    project_id: str
    total_assets_considered: int
    total_reports_considered: int
    takes_created: int
    takes_updated: int
    total_takes: int
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EditorialScoreResponse(BaseModel):
    project_id: str
    takes_scored: int
    recommended_groups: int
    warnings: list[str] = Field(default_factory=list)


class EditorialRecommendedTakeResponse(BaseModel):
    scene_number: Optional[int] = None
    shot_number: Optional[int] = None
    take: EditorialTakeResponse


class EditorialRecommendedTakeListResponse(BaseModel):
    recommended_takes: list[EditorialRecommendedTakeResponse] = Field(default_factory=list)


class AssemblyCutItemResponse(BaseModel):
    id: str
    assembly_cut_id: str
    take_id: Optional[str] = None
    project_id: str
    scene_number: Optional[int] = None
    shot_number: Optional[int] = None
    take_number: Optional[int] = None
    source_media_asset_id: Optional[str] = None
    audio_media_asset_id: Optional[str] = None
    start_tc: Optional[str] = None
    end_tc: Optional[str] = None
    timeline_in: Optional[int] = None
    timeline_out: Optional[int] = None
    duration_frames: Optional[int] = None
    fps: Optional[float] = None
    recommended_reason: Optional[str] = None
    order_index: int
    created_at: datetime


class AssemblyCutResponse(BaseModel):
    id: str
    project_id: str
    organization_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    source_scope: Optional[str] = None
    source_version: Optional[int] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: list[AssemblyCutItemResponse] = Field(default_factory=list)


class AssemblyCutCreateResponse(BaseModel):
    assembly_cut: AssemblyCutResponse
    items_created: int


class EditorialFCPXMLExportResponse(BaseModel):
    deliverable_id: Optional[str] = None
    file_name: str
    file_path: str
    assembly_cut_id: str
    format_type: str = "FCPXML"


class MediaPathResolutionResponse(BaseModel):
    asset_id: str
    filename: str
    resolved_path: str
    fcpxml_uri: str
    status: str
    reason: str
    candidates: list[str] = Field(default_factory=list)


class EditorialMediaRelinkEntryResponse(BaseModel):
    clip_id: str
    clip_name: str
    role: str
    asset_id: Optional[str] = None
    filename: str
    resolved_path: str
    fcpxml_uri: str
    status: str
    reason: str
    duration_frames: Optional[int] = None
    start_timecode: Optional[str] = None
    scene: Optional[int | str] = None
    shot: Optional[int | str] = None
    take: Optional[int | str] = None
    video_asset_id: Optional[str] = None
    audio_asset_id: Optional[str] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_status: Optional[str] = None
    audio_status: Optional[str] = None
    sync_method: Optional[str] = None
    sync_confidence: Optional[float] = None
    dual_system_status: Optional[str] = None
    take_warnings: list[str] = Field(default_factory=list)
    audio_metadata: Optional[dict[str, Any]] = None


class EditorialMediaRelinkReportResponse(BaseModel):
    generated_at: datetime
    project_id: str
    assembly_cut_id: str
    clip_count: int
    resolved_media_count: int
    offline_media_count: int
    missing_media_count: int
    warnings: list[str] = Field(default_factory=list)
    entries: list[EditorialMediaRelinkEntryResponse] = Field(default_factory=list)


class EditorialFCPXMLValidationResponse(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    clip_count: int = 0
    asset_count: int = 0
    fps: Optional[float] = None


class EditorialFCPXMLStatusResponse(BaseModel):
    deliverable_id: Optional[str] = None
    file_name: str
    file_path: str
    assembly_cut_id: str
    format_type: str = "FCPXML"
    clip_count: int = 0
    route_status: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    validation: EditorialFCPXMLValidationResponse
    media_relink_report: EditorialMediaRelinkReportResponse


class EditorialPackageExportResponse(BaseModel):
    deliverable_id: Optional[str] = None
    file_name: str
    file_path: str
    assembly_cut_id: str
    format_type: str = "ZIP"


class DavinciPlatformExportRequest(BaseModel):
    platform: str = Field(default="windows", description="windows|mac|linux|offline|all")
    root_path: Optional[str] = Field(default=None, description="Root path for media files")
    include_media: bool = Field(default=False, description="Include media files in package")
    audio_mode: str = Field(default="conservative", description="conservative|experimental")


class DavinciPlatformExportResponse(BaseModel):
    deliverable_id: Optional[str] = None
    file_name: str
    file_path: str
    assembly_cut_id: str
    platform: str
    format_type: str = "FCPXML"
    root_path: Optional[str] = None


class EditorialAudioMetadataResponse(BaseModel):
    status: str
    asset_id: Optional[str] = None
    filename: str
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    duration_seconds: Optional[float] = None
    bit_depth: Optional[int] = None
    codec: Optional[str] = None
    file_size: Optional[int] = None
    timecode: Optional[str] = None
    time_reference_samples: Optional[int] = None
    time_reference_seconds: Optional[float] = None
    fps: Optional[float] = None
    scene: Optional[str] = None
    shot: Optional[str] = None
    take: Optional[str] = None
    sound_roll: Optional[str] = None
    circled: Optional[bool] = None
    notes: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    raw_bext: Optional[dict[str, Any]] = None
    raw_ixml: Optional[dict[str, Any]] = None
    reason: Optional[str] = None


class EditorialAudioMetadataListResponse(BaseModel):
    project_id: str
    audio_assets: list[EditorialAudioMetadataResponse] = Field(default_factory=list)


class EditorialAudioMetadataScanResponse(BaseModel):
    project_id: str
    scanned_count: int
    parsed_count: int
    partial_count: int
    unsupported_count: int
    error_count: int
    audio_assets: list[EditorialAudioMetadataResponse] = Field(default_factory=list)
