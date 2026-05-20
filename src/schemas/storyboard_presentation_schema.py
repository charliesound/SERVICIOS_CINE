from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class StoryboardSheetPreset(str, Enum):
    clean_corporate = "clean_corporate"
    cinematic_pitch = "cinematic_pitch"
    production_sheet = "production_sheet"
    realistic_client_review = "realistic_client_review"


class StoryboardLayoutName(str, Enum):
    grid_2x2 = "grid_2x2"
    grid_2x3 = "grid_2x3"
    grid_2x4 = "grid_2x4"
    grid_3x3 = "grid_3x3"


class StoryboardFrameMetadata(BaseModel):
    visual_bible: dict[str, Any] | None = None
    workflow_profile: dict[str, Any] | None = None
    workflow_fallback_report: dict[str, Any] | None = None
    render_job_id: str | None = None
    media_asset_id: str | None = None


class StoryboardShotInfo(BaseModel):
    scene: str | None = None
    shot_size: str | None = None
    camera_angle: str | None = None
    movement: str | None = None
    description: str | None = None
    dialogue: str | None = None
    notes: str | None = None
    status: str | None = None


class StoryboardFrame(BaseModel):
    shot_number: int
    scene_number: str | None = None
    image_path: str
    info: StoryboardShotInfo = Field(default_factory=StoryboardShotInfo)
    metadata: StoryboardFrameMetadata = Field(default_factory=StoryboardFrameMetadata)


class StoryboardLayoutConfig(BaseModel):
    layout: StoryboardLayoutName
    preset: StoryboardSheetPreset
    page_width_px: int = 1920
    page_height_px: int = 1080
    gutter_px: int = 24
    margin_px: int = 48
    caption_height_px: int = 130
    title: str | None = None

    @field_validator("page_width_px", "page_height_px", "gutter_px", "margin_px", "caption_height_px")
    @classmethod
    def _validate_positive_dimensions(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("layout dimensions must be positive")
        return value


class StoryboardSheetRequest(BaseModel):
    project_id: str
    render_job_id: str | None = None
    asset_ids: list[str] | None = None
    layout: StoryboardLayoutConfig
    output_format: Literal["png", "pdf"]
    override_shot_info: dict[str, StoryboardShotInfo] | None = None


class StoryboardSheetResponse(BaseModel):
    artifact_path: str
    artifact_url: str | None = None
    output_format: Literal["png", "pdf"]
    frame_count: int
    layout: StoryboardLayoutName
    preset: StoryboardSheetPreset
    metadata: dict[str, Any] = Field(default_factory=dict)
