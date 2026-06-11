from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AIJobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_type: str
    project_id: str | None = None
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None
    provider_type: str | None = None
    provider_name: str | None = None
    workflow_id: str | None = None
    workflow_version: str | None = None
    workflow_hash: str | None = None
    model_name: str | None = None
    input_asset_ids: list[str] | None = None
    output_asset_ids: list[str] | None = None


class AIJobEstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_credits: int | None = Field(default=None, gt=0)


class AIJobCreditCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_credits: int | None = Field(default=None, gt=0)


class AIJobReserveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_credits: int | None = Field(default=None, gt=0)
    caller_key: str | None = None


class AIJobCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(default=None, min_length=1, max_length=500)
    metadata: dict[str, Any] | None = None


class AIJobConsumeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actual_credits: int | None = Field(default=None, gt=0)
    caller_key: str | None = None


class AIJobReleaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    release_credits: int | None = Field(default=None, gt=0)
    caller_key: str | None = None


class AIJobMutationResponse(BaseModel):
    job: dict[str, Any]
    message: str = ""
    transition: dict[str, Any] | None = None
    accounting: dict[str, Any] | None = None


class AIJobCancelResponse(BaseModel):
    job_id: str
    organization_id: str
    status: str
    cancel_requested: bool
    idempotent: bool = False
    message: str = ""
    reason: str | None = None
    metadata: dict[str, Any] | None = None


class AIJobReadResponse(BaseModel):
    job: dict[str, Any]


class AIJobListResponse(BaseModel):
    items: list[dict[str, Any]]
    next_cursor: str | None = None


class AIJobHistoryResponse(BaseModel):
    job_id: str
    events: list[dict[str, Any]]
