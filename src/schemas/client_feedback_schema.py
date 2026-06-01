from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class CIDClientFeedbackCreate(BaseModel):
    project_id: str
    feedback_type: str
    feedback_scope: str = "project_feedback"
    original_question: str | None = None
    original_answer: str | None = None
    corrected_answer: str | None = None
    feedback_text: str | None = None
    source_ids: list[str] | None = None
    source_types: list[str] | None = None
    approved_for_memory: bool = False
    confidence: float | None = None
    model_used: str | None = None
    prompt_version: str | None = None
    answer_version: str | None = None
    metadata_json: dict[str, Any] | None = None


class CIDClientFeedbackUpdate(BaseModel):
    feedback_text: str | None = None
    corrected_answer: str | None = None
    approved_for_memory: bool | None = None
    status: str | None = None
    confidence: float | None = None
    metadata_json: dict[str, Any] | None = None


class CIDClientFeedbackResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    user_id: str
    feedback_type: str
    feedback_scope: str
    original_question: str | None = None
    original_answer: str | None = None
    corrected_answer: str | None = None
    feedback_text: str | None = None
    source_ids: dict[str, Any] | list[Any] | None = None
    source_types: list[str] | None = None
    approved_for_memory: bool = False
    approved_by_user_id: str | None = None
    confidence: float | None = None
    status: str = "pending"
    model_used: str | None = None
    prompt_version: str | None = None
    answer_version: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CIDFeedbackListResponse(BaseModel):
    feedbacks: list[CIDClientFeedbackResponse]
    total_count: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)


class CIDFeedbackMemoryEntryCreate(BaseModel):
    feedback_id: str
    project_id: str
    source_type: str
    source_id: str
    source_text: str | None = None
    approved_for_memory: bool = False
    confidence: float | None = None
    metadata_json: dict[str, Any] | None = None


class CIDFeedbackMemoryEntryResponse(BaseModel):
    id: str
    feedback_id: str
    organization_id: str
    project_id: str
    source_type: str
    source_id: str
    source_text: str | None = None
    approved_for_memory: bool = False
    approved_by_user_id: str | None = None
    qdrant_point_id: str | None = None
    indexed_at: datetime | None = None
    confidence: float | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CIDAnswerFeedbackEventCreate(BaseModel):
    feedback_id: str
    project_id: str
    answer_id: str
    action: str
    model_used: str | None = None
    prompt_version: str | None = None
    answer_version: str | None = None
    metadata_json: dict[str, Any] | None = None


class CIDAnswerFeedbackEventResponse(BaseModel):
    id: str
    feedback_id: str
    organization_id: str
    project_id: str
    answer_id: str
    model_used: str | None = None
    prompt_version: str | None = None
    answer_version: str | None = None
    action: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CIDProjectLearningRuleCreate(BaseModel):
    project_id: str
    rule_type: str
    rule_value: str
    priority: int = 0
    active: bool = True
    metadata_json: dict[str, Any] | None = None


class CIDProjectLearningRuleUpdate(BaseModel):
    rule_value: str | None = None
    priority: int | None = None
    active: bool | None = None
    metadata_json: dict[str, Any] | None = None


class CIDProjectLearningRuleResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    rule_type: str
    rule_value: str
    priority: int = 0
    active: bool = True
    created_by_user_id: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CIDOrganizationLearningPreferenceCreate(BaseModel):
    preference_type: str
    preference_value: str
    priority: int = 0
    active: bool = True
    metadata_json: dict[str, Any] | None = None


class CIDOrganizationLearningPreferenceUpdate(BaseModel):
    preference_value: str | None = None
    priority: int | None = None
    active: bool | None = None
    metadata_json: dict[str, Any] | None = None


class CIDOrganizationLearningPreferenceResponse(BaseModel):
    id: str
    organization_id: str
    preference_type: str
    preference_value: str
    priority: int = 0
    active: bool = True
    created_by_user_id: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CIDFeedbackAuditResponse(BaseModel):
    id: str
    feedback_id: str | None = None
    organization_id: str
    project_id: str
    user_id: str
    action: str
    previous_status: str | None = None
    new_status: str | None = None
    previous_metadata_json: dict[str, Any] | None = None
    new_metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
