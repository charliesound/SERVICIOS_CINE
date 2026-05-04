from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class CIDPipelineLegalContext(BaseModel):
    voice_cloning: bool = False
    consent: bool = False
    rights_declared: bool = False
    rights_notes: Optional[str] = None

    @field_validator("rights_notes")
    @classmethod
    def validate_rights_notes(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CIDPipelineStage(BaseModel):
    id: str
    name: str
    type: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name", "type")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Stage fields must not be blank")
        return normalized


class CIDPipelineDefinition(BaseModel):
    pipeline_id: str
    mode: str = "simulated"
    title: str
    summary: Optional[str] = None
    preset_key: str
    preset_name: str
    task_type: str
    project_id: Optional[str] = None
    intent: Optional[str] = None
    workflow_key: Optional[str] = None
    backend: Optional[str] = None
    stages: list[CIDPipelineStage] = Field(default_factory=list)
    legal: CIDPipelineLegalContext = Field(default_factory=CIDPipelineLegalContext)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("pipeline_id", "title", "preset_key", "preset_name", "task_type")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pipeline fields must not be blank")
        return normalized

    @field_validator("summary", "project_id", "intent", "workflow_key", "backend")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CIDPipelinePresetResponse(BaseModel):
    key: str
    name: str
    description: str
    task_type: str
    mode: str = "simulated"
    requires_legal_gate: bool = False
    default_workflow_key: Optional[str] = None
    default_backend: Optional[str] = None
    stage_count: int = 0


class CIDPipelinePresetListResponse(BaseModel):
    count: int
    presets: list[CIDPipelinePresetResponse] = Field(default_factory=list)


class CIDPipelineGenerateRequest(BaseModel):
    intent: Optional[str] = None
    preset_key: Optional[str] = None
    title: Optional[str] = None
    project_id: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    legal: CIDPipelineLegalContext = Field(default_factory=CIDPipelineLegalContext)

    @field_validator("intent", "preset_key", "title", "project_id")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CIDPipelineValidateRequest(BaseModel):
    pipeline: CIDPipelineDefinition
    project_id: Optional[str] = None

    @field_validator("project_id")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CIDPipelineExecuteRequest(BaseModel):
    pipeline: CIDPipelineDefinition
    project_id: Optional[str] = None

    @field_validator("project_id")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CIDPipelineValidationIssue(BaseModel):
    code: str
    message: str
    severity: str
    field: Optional[str] = None


class CIDPipelineValidationResponse(BaseModel):
    valid: bool
    blocked: bool = False
    errors: list[CIDPipelineValidationIssue] = Field(default_factory=list)
    warnings: list[CIDPipelineValidationIssue] = Field(default_factory=list)


class CIDPipelineGenerateResponse(BaseModel):
    mode: str = "simulated"
    pipeline: CIDPipelineDefinition
    validation: CIDPipelineValidationResponse


class CIDPipelineJobHistoryEvent(BaseModel):
    id: str
    event_type: str
    status: str
    message: str
    created_at: datetime


class CIDPipelineJobResponse(BaseModel):
    job_id: str
    mode: str = "simulated"
    status: str
    organization_id: str
    user_id: str
    project_id: Optional[str] = None
    pipeline_id: str
    task_type: str
    preset_key: str
    created_at: datetime
    updated_at: datetime
    validation: CIDPipelineValidationResponse
    history: list[CIDPipelineJobHistoryEvent] = Field(default_factory=list)
    pipeline: CIDPipelineDefinition


class CIDPipelineExecuteResponse(BaseModel):
    mode: str = "simulated"
    job: CIDPipelineJobResponse


class CIDPipelineJobListResponse(BaseModel):
    count: int
    jobs: list[CIDPipelineJobResponse] = Field(default_factory=list)
