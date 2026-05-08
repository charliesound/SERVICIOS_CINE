from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _clean_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = (value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)
    return cleaned


class FeedbackTargetType(str, Enum):
    storyboard = "storyboard"
    sequence = "sequence"
    shot = "shot"
    prompt = "prompt"
    visual_reference = "visual_reference"


class FeedbackCategory(str, Enum):
    composition = "composition"
    lighting = "lighting"
    character = "character"
    camera = "camera"
    continuity = "continuity"
    tone = "tone"
    production = "production"
    other = "other"


class FeedbackSeverity(str, Enum):
    minor = "minor"
    medium = "medium"
    major = "major"


class FeedbackRole(str, Enum):
    director = "director"
    producer = "producer"
    cinematographer = "cinematographer"
    operator = "operator"


class RegenerationStrategy(str, Enum):
    single_shot = "single_shot"
    selected_shots = "selected_shots"
    sequence = "sequence"
    full_storyboard_not_allowed = "full_storyboard_not_allowed"


class DirectorFeedbackNote(BaseModel):
    note_id: str = ""
    target_type: FeedbackTargetType = FeedbackTargetType.shot
    target_id: str = ""
    note_text: str = ""
    category: FeedbackCategory = FeedbackCategory.other
    severity: FeedbackSeverity = FeedbackSeverity.minor
    created_by_role: FeedbackRole = FeedbackRole.director
    preserve_original_logic: bool = True

    @field_validator("note_id", "target_id", "note_text")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _clean(value)


class DirectorFeedbackInterpretation(BaseModel):
    requested_changes: list[str] = Field(default_factory=list)
    protected_story_elements: list[str] = Field(default_factory=list)
    protected_visual_elements: list[str] = Field(default_factory=list)
    conflict_with_script: bool = False
    conflict_with_script_details: str = ""
    conflict_with_reference: bool = False
    conflict_with_reference_details: str = ""
    conflict_with_initial_prompt: bool = False
    conflict_with_initial_prompt_details: str = ""
    recommended_action: str = ""
    risk_level: str = "low"
    explanation: str = ""

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, value: str | None) -> str | None:
        return _clean(value)


class PromptRevisionPatch(BaseModel):
    original_prompt: str = ""
    revised_prompt: str = ""
    original_negative_prompt: str = ""
    revised_negative_prompt: str = ""
    preserved_elements: list[str] = Field(default_factory=list)
    changed_elements: list[str] = Field(default_factory=list)
    rejected_changes: list[str] = Field(default_factory=list)
    revision_reason: str = ""
    director_note_applied: str = ""
    version_number: int = 1

    @field_validator("original_prompt", "revised_prompt", "original_negative_prompt", "revised_negative_prompt", "revision_reason", "director_note_applied")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _clean(value)

    @field_validator("preserved_elements", "changed_elements", "rejected_changes")
    @classmethod
    def validate_lists(cls, values: list[str]) -> list[str]:
        return _clean_list(values)


class StoryboardRevisionPlan(BaseModel):
    project_id: str = ""
    sequence_id: str = ""
    shot_id: str | None = None
    original_story_logic: str = ""
    director_feedback: DirectorFeedbackNote | None = None
    interpretation: DirectorFeedbackInterpretation | None = None
    prompt_revision: PromptRevisionPatch | None = None
    regeneration_strategy: RegenerationStrategy = RegenerationStrategy.single_shot
    requires_director_confirmation: bool = False
    qa_checklist: list[str] = Field(default_factory=list)

    @field_validator("project_id", "sequence_id", "shot_id", "original_story_logic")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _clean(value)

    @field_validator("qa_checklist")
    @classmethod
    def validate_qa(cls, values: list[str]) -> list[str]:
        return _clean_list(values)


class StoryboardRevisionResult(BaseModel):
    status: str = ""
    revision_id: str = ""
    revision_plan: StoryboardRevisionPlan | None = None
    revised_prompt_spec: dict[str, Any] = Field(default_factory=dict)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    message: str = ""

    @field_validator("status", "revision_id", "message")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        return _clean(value)


class ShotFeedbackRequest(BaseModel):
    note_text: str = ""
    category: FeedbackCategory = FeedbackCategory.other
    severity: FeedbackSeverity = FeedbackSeverity.minor
    created_by_role: FeedbackRole = FeedbackRole.director
    preserve_original_logic: bool = True


class SequenceFeedbackRequest(BaseModel):
    note_text: str = ""
    apply_to: str = "selected_shots"
    shot_ids: list[str] = Field(default_factory=list)
    preserve_original_logic: bool = True
