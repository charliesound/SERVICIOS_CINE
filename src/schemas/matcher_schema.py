from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MatcherJobResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    trigger_type: str
    trigger_ref_id: Optional[str] = None
    input_hash: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_summary_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatcherJobListResponse(BaseModel):
    project_id: str
    organization_id: str
    jobs: List[MatcherJobResponse]
    total_count: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)


class MatcherTriggerRequest(BaseModel):
    evaluation_version: Optional[str] = None


class MatcherStatusResponse(BaseModel):
    project_id: str
    organization_id: str
    latest_job_id: Optional[str] = None
    latest_job_status: Optional[str] = None
    latest_job_created_at: Optional[datetime] = None
    latest_job_finished_at: Optional[datetime] = None
    total_jobs_count: int

    model_config = ConfigDict(from_attributes=True)