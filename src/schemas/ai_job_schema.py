from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class AIJobBase(BaseModel):
    organization_id: str
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    operation_type: str
    status: str = "created"
    estimated_credits: int = 0
    reserved_credits: int = 0
    consumed_credits: int = 0
    released_credits: int = 0
    reservation_entry_id: Optional[str] = None
    consume_entry_id: Optional[str] = None
    release_entry_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    provider_type: Optional[str] = None
    provider_name: Optional[str] = None
    provider_job_id: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_version: Optional[str] = None
    workflow_hash: Optional[str] = None
    model_name: Optional[str] = None
    input_asset_ids: list[str] | None = None
    output_asset_ids: list[str] | None = None
    error_code: Optional[str] = None
    failure_reason: Optional[str] = None
    attempt_number: int = 1
    parent_job_id: Optional[str] = None
    estimated_at: datetime | None = None
    credit_checked_at: datetime | None = None
    reserved_at: datetime | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancel_requested_at: datetime | None = None
    cancelled_at: datetime | None = None
    consume_pending_at: datetime | None = None
    consumed_at: datetime | None = None
    release_pending_at: datetime | None = None
    released_at: datetime | None = None
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("metadata", "job_metadata"),
        serialization_alias="metadata",
    )


class AIJobCreate(AIJobBase):
    pass


class AIJobUpdate(BaseModel):
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    operation_type: Optional[str] = None
    status: Optional[str] = None
    estimated_credits: Optional[int] = None
    reserved_credits: Optional[int] = None
    consumed_credits: Optional[int] = None
    released_credits: Optional[int] = None
    reservation_entry_id: Optional[str] = None
    consume_entry_id: Optional[str] = None
    release_entry_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    provider_type: Optional[str] = None
    provider_name: Optional[str] = None
    provider_job_id: Optional[str] = None
    workflow_id: Optional[str] = None
    workflow_version: Optional[str] = None
    workflow_hash: Optional[str] = None
    model_name: Optional[str] = None
    input_asset_ids: list[str] | None = None
    output_asset_ids: list[str] | None = None
    error_code: Optional[str] = None
    failure_reason: Optional[str] = None
    attempt_number: Optional[int] = None
    parent_job_id: Optional[str] = None
    estimated_at: datetime | None = None
    credit_checked_at: datetime | None = None
    reserved_at: datetime | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancel_requested_at: datetime | None = None
    cancelled_at: datetime | None = None
    consume_pending_at: datetime | None = None
    consumed_at: datetime | None = None
    release_pending_at: datetime | None = None
    released_at: datetime | None = None
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("metadata", "job_metadata"),
        serialization_alias="metadata",
    )


class AIJobResponse(AIJobBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


__all__ = [
    "AIJobBase",
    "AIJobCreate",
    "AIJobUpdate",
    "AIJobResponse",
]
