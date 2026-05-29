from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class WorkflowProfile(str, Enum):
    smoke_light = "smoke_light"
    storyboard_safe = "storyboard_safe"
    storyboard_fast = "storyboard_fast"
    production_quality = "production_quality"
    production_storyboard_cinematic = "production_storyboard_cinematic"
    production_storyboard_cinematic_controlnet = "production_storyboard_cinematic_controlnet"
    production_storyboard_cinematic_reference = "production_storyboard_cinematic_reference"


FALLBACK_CHAIN: dict[WorkflowProfile, WorkflowProfile | None] = {
    WorkflowProfile.production_storyboard_cinematic_reference: WorkflowProfile.production_storyboard_cinematic,
    WorkflowProfile.production_storyboard_cinematic_controlnet: WorkflowProfile.production_storyboard_cinematic,
    WorkflowProfile.production_quality: WorkflowProfile.production_storyboard_cinematic,
    WorkflowProfile.production_storyboard_cinematic: WorkflowProfile.storyboard_safe,
    WorkflowProfile.storyboard_fast: WorkflowProfile.storyboard_safe,
    WorkflowProfile.storyboard_safe: WorkflowProfile.smoke_light,
    WorkflowProfile.smoke_light: None,
}


class WorkflowFallbackReport(BaseModel):
    requested_profile: str
    executed_profile: str
    fallback_applied: bool
    reason: str
    missing_nodes: list[str] = Field(default_factory=list)
    missing_models: list[str] = Field(default_factory=list)


class WorkflowCapabilitySnapshot(BaseModel):
    backend: str
    base_url: str
    total_nodes: int
    available_nodes: list[str] = Field(default_factory=list)
    missing_nodes: list[str] = Field(default_factory=list)
    failed_nodes: list[str] = Field(default_factory=list)
    object_info_snapshot_at: str | None = None
    source: str = "object_info_api"


class WorkflowBuildResult(BaseModel):
    prompt_payload: dict[str, Any] = Field(default_factory=dict)
    workflow_key: str
    requested_profile: str
    executed_profile: str
    fallback_report: WorkflowFallbackReport | None = None
    metadata_injected: bool = False
