from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from schemas.shot_schema import StoryboardShotResponse


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class StoryboardGenerateRequest(BaseModel):
    mode: str = "SEQUENCE"
    generation_mode: Optional[str] = None
    sequence_id: Optional[str] = None
    sequence_ids: list[str] = Field(default_factory=list)
    scene_start: Optional[int] = None
    scene_end: Optional[int] = None
    selected_scene_ids: list[str] = Field(default_factory=list)
    scene_numbers: list[int] = Field(default_factory=list)
    style_preset: str = "cinematic_realistic"
    visual_mode: Optional[str] = None
    shots_per_scene: int = 3
    max_scenes: Optional[int] = None
    overwrite: bool = False
    director_lens_id: Optional[str] = None
    montage_profile_id: Optional[str] = None
    use_cinematic_intelligence: bool = False
    use_montage_intelligence: bool = False
    validate_prompts: bool = False


class StoryboardSequencePlanRequest(BaseModel):
    style_preset: str = "cinematic_realistic"
    shots_per_scene: int = 5


class StoryboardSequencePlanResponse(BaseModel):
    sequence_id: str
    sequence_title: str = ""
    estimated_shot_count: int = 0
    shots: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("sequence_id", "sequence_title")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class StoryboardSequenceResponse(BaseModel):
    sequence_id: str
    sequence_number: int
    title: str
    summary: str
    included_scenes: list[int] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    location: Optional[str] = None
    emotional_arc: Optional[str] = None
    estimated_duration: Optional[int] = None
    estimated_shots: int = 0
    storyboard_status: str = "not_generated"
    current_version: int = 0


class StoryboardOptionsResponse(BaseModel):
    modes: list[str] = Field(default_factory=list)
    sequences: list[StoryboardSequenceResponse] = Field(default_factory=list)
    scenes_detected: list[dict[str, Any]] = Field(default_factory=list)
    styles_available: list[str] = Field(default_factory=list)
    storyboard_status: dict[str, Any] = Field(default_factory=dict)


class StoryboardJobResponse(BaseModel):
    job_id: str
    status: str
    mode: str
    generation_mode: Optional[str] = None
    version: int
    sequence_id: Optional[str] = None
    sequence_ids: list[str] = Field(default_factory=list)
    scene_start: Optional[int] = None
    scene_end: Optional[int] = None
    selected_scene_numbers: list[int] = Field(default_factory=list)
    total_selected: int = 0
    total_scenes: int = 0
    total_shots: int = 0


class StoryboardListResponse(BaseModel):
    project_id: str
    mode: str
    sequence_id: Optional[str] = None
    scene_number: Optional[int] = None
    version: Optional[int] = None
    shots: list[StoryboardShotResponse] = Field(default_factory=list)


class StoryboardSequenceDetailResponse(BaseModel):
    sequence: StoryboardSequenceResponse
    shots: list[StoryboardShotResponse] = Field(default_factory=list)


class StoryboardGenerationAuditResponse(BaseModel):
    job_id: str
    mode: str
    sequence_id: Optional[str] = None
    scene_start: Optional[int] = None
    scene_end: Optional[int] = None
    style_preset: str
    shots_per_scene: int
    overwrite: bool
    version: int
    generated_assets: list[str] = Field(default_factory=list)
    created_at: datetime
