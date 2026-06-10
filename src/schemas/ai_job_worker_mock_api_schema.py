from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AIJobWorkerMockExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: Literal["success", "failure", "cancel"]
    execution_attempt_id: str = Field(..., min_length=1)
    simulated_duration_ms: int | None = Field(default=None, ge=0, le=60_000)
    mock_output_metadata: dict[str, Any] | None = None
    mock_error_code: str | None = Field(default=None, min_length=1)
    mock_error_message: str | None = Field(default=None, min_length=1)
    actual_credits: int | None = Field(default=None, gt=0)
    release_credits: int | None = Field(default=None, gt=0)


class AIJobWorkerMockExecuteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: str
    job_id: str
    mode: str
    status: str
    replay: bool = False
    attempt_status: str | None = None
    consumed_credits: int | None = None
    released_credits: int | None = None
    consume_entry_id: str | None = None
    release_entry_id: str | None = None
    output_metadata: dict[str, Any] | None = None
    error_metadata: dict[str, Any] | None = None
