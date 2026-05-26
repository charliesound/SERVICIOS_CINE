from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PromptTrace(BaseModel):
    original_narrative: str | None = None
    source_scene_heading: str | None = None
    source_action_summary: str | None = None
    source_dialogue_summary: str | None = None
    positive_prompt_enriched: str | None = None
    negative_prompt_enriched: str | None = None
    prompt_summary: str | None = None
    display_description_es: str | None = None


class WorkflowTrace(BaseModel):
    workflow_key: str | None = None
    workflow_profile: str | None = None
    workflow_profile_requested: str | None = None
    workflow_profile_executed: str | None = None
    fallback_applied: bool = False
    fallback_reason: str | None = None
    missing_nodes: list[str] = Field(default_factory=list)
    missing_models: list[str] = Field(default_factory=list)


class ModelTrace(BaseModel):
    model_family: str | None = None
    checkpoint: str | None = None
    loras: list[dict[str, Any]] = Field(default_factory=list)
    sampler: str | None = None
    scheduler: str | None = None
    steps: int | None = None
    cfg: float | None = None
    seed: int | None = None
    width: int | None = None
    height: int | None = None


class AssetTrace(BaseModel):
    media_asset_id: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    thumbnail_url: str | None = None
    image_url: str | None = None
    association_method: str | None = None
    association_confidence: float | None = None
    association_reason: str | None = None
    repaired_at: datetime | None = None


class VersionHistoryItem(BaseModel):
    version: int
    shot_id: str
    created_at: datetime | None = None
    prompt: str | None = None
    is_active: bool = False


class VersionTrace(BaseModel):
    current_version: int = 1
    total_versions: int = 1
    has_previous_versions: bool = False
    previous_versions: list[VersionHistoryItem] = Field(default_factory=list)


class StoryboardTraceRecord(BaseModel):
    project_id: str
    organization_id: str
    shot_id: str | None = None
    sequence_id: str | None = None
    sequence_order: int | None = None
    scene_number: int | None = None
    shot_type: str | None = None
    visual_mode: str | None = None
    generation_mode: str | None = None
    generation_job_id: str | None = None
    render_job_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    prompt_trace: PromptTrace = Field(default_factory=PromptTrace)
    workflow_trace: WorkflowTrace = Field(default_factory=WorkflowTrace)
    model_trace: ModelTrace = Field(default_factory=ModelTrace)
    asset_trace: AssetTrace = Field(default_factory=AssetTrace)
    version_trace: VersionTrace = Field(default_factory=VersionTrace)
    available_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class StoryboardTraceSummary(BaseModel):
    project_id: str
    organization_id: str
    total_shots: int = 0
    traced_shots: int = 0
    shots_with_prompt: int = 0
    shots_with_workflow: int = 0
    shots_with_model: int = 0
    shots_with_asset: int = 0
    shots_with_render_job: int = 0
    shots_with_previous_versions: int = 0
    workflow_fallback_count: int = 0
    workflow_keys: list[str] = Field(default_factory=list)
    workflow_profiles: list[str] = Field(default_factory=list)
    model_families: list[str] = Field(default_factory=list)
    checkpoints: list[str] = Field(default_factory=list)
    missing_field_counts: dict[str, int] = Field(default_factory=dict)
