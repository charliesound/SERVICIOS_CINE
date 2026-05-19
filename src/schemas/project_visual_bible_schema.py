from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_PROMPT_MODES = {"tag_soup", "semantic_t5"}
ALLOWED_TARGET_MODELS = {"SDXL", "Flux", "Wan"}


class ProjectVisualBibleBase(BaseModel):
    active_preset_id: Optional[str] = None
    selected_elements_json: dict[str, Any] = Field(default_factory=dict)
    custom_prompt_tags_json: list[str] = Field(default_factory=list)
    negative_prompt_tags_json: list[str] = Field(default_factory=list)
    director_notes: Optional[str] = None
    prompt_mode: str = "tag_soup"
    target_model: str = "SDXL"
    is_active: bool = True

    @field_validator("prompt_mode")
    @classmethod
    def validate_prompt_mode(cls, v: str) -> str:
        if v not in ALLOWED_PROMPT_MODES:
            raise ValueError(
                f"prompt_mode must be one of {sorted(ALLOWED_PROMPT_MODES)}, got '{v}'"
            )
        return v

    @field_validator("target_model")
    @classmethod
    def validate_target_model(cls, v: str) -> str:
        if v not in ALLOWED_TARGET_MODELS:
            raise ValueError(
                f"target_model must be one of {sorted(ALLOWED_TARGET_MODELS)}, got '{v}'"
            )
        return v

    @field_validator("selected_elements_json")
    @classmethod
    def validate_selected_elements_is_dict(cls, v: Any) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("selected_elements_json must be a dict")
        return v

    @field_validator("custom_prompt_tags_json")
    @classmethod
    def validate_custom_tags_is_list(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("custom_prompt_tags_json must be a list")
        return v

    @field_validator("negative_prompt_tags_json")
    @classmethod
    def validate_negative_tags_is_list(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            raise ValueError("negative_prompt_tags_json must be a list")
        return v


class ProjectVisualBibleCreate(ProjectVisualBibleBase):
    pass


class ProjectVisualBibleUpdate(BaseModel):
    active_preset_id: Optional[str] = None
    selected_elements_json: Optional[dict[str, Any]] = None
    custom_prompt_tags_json: Optional[list[str]] = None
    negative_prompt_tags_json: Optional[list[str]] = None
    director_notes: Optional[str] = None
    prompt_mode: Optional[str] = None
    target_model: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("prompt_mode")
    @classmethod
    def validate_prompt_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_PROMPT_MODES:
            raise ValueError(
                f"prompt_mode must be one of {sorted(ALLOWED_PROMPT_MODES)}, got '{v}'"
            )
        return v

    @field_validator("target_model")
    @classmethod
    def validate_target_model(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_TARGET_MODELS:
            raise ValueError(
                f"target_model must be one of {sorted(ALLOWED_TARGET_MODELS)}, got '{v}'"
            )
        return v

    @field_validator("selected_elements_json")
    @classmethod
    def validate_selected_elements_is_dict(cls, v: Optional[Any]) -> Optional[dict[str, Any]]:
        if v is not None and not isinstance(v, dict):
            raise ValueError("selected_elements_json must be a dict")
        return v

    @field_validator("custom_prompt_tags_json")
    @classmethod
    def validate_custom_tags_is_list(cls, v: Optional[Any]) -> Optional[list[str]]:
        if v is not None and not isinstance(v, list):
            raise ValueError("custom_prompt_tags_json must be a list")
        return v

    @field_validator("negative_prompt_tags_json")
    @classmethod
    def validate_negative_tags_is_list(cls, v: Optional[Any]) -> Optional[list[str]]:
        if v is not None and not isinstance(v, list):
            raise ValueError("negative_prompt_tags_json must be a list")
        return v


class ProjectVisualBibleResponse(ProjectVisualBibleBase):
    id: str
    project_id: str
    organization_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class VisualBiblePreviewRequest(BaseModel):
    base_prompt: str = Field(..., min_length=1)
    selected_tags: Optional[list[str]] = None


class VisualBiblePreviewResponse(BaseModel):
    base_prompt: str
    enriched_prompt: str
    negative_prompt: str
    applied_preset: Optional[dict[str, Any]] = None
    applied_tags: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    visual_bible_id: str
