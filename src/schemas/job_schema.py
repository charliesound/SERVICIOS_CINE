from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class JobHistoryEntry(BaseModel):
    id: str
    event_type: str
    status_from: Optional[str] = None
    status_to: Optional[str] = None
    message: Optional[str] = None
    detail: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None


class JobAssetEntry(BaseModel):
    id: str
    job_id: Optional[str] = None
    file_name: str
    file_extension: str
    asset_type: str
    asset_source: Optional[str] = None
    content_ref: Optional[str] = None
    mime_type: Optional[str] = None
    status: str
    metadata_json: Optional[Any] = None
    created_at: Optional[str] = None


class JobCreate(BaseModel):
    task_type: str = Field(..., min_length=1, max_length=64)
    workflow_key: str = Field(..., min_length=1, max_length=128)
    prompt: Dict[str, Any]
    priority: int = Field(default=5, ge=0, le=10)
    target_instance: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class JobSubmit(BaseModel):
    task_type: str = Field(..., min_length=1, max_length=64)
    workflow_key: str = Field(..., min_length=1, max_length=128)
    prompt: Dict[str, Any]
    user_id: str
    user_plan: str
    priority: int = Field(default=5, ge=0, le=10)
    target_instance: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    backend: str
    backend_url: str
    queue_position: Optional[int] = None
    estimated_time: Optional[int] = None
    error: Optional[str] = None


class JobDetail(BaseModel):
    job_id: str
    task_type: str
    workflow_key: str
    status: str
    backend: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    queue_position: Optional[int] = None
    history: List[JobHistoryEntry] = Field(default_factory=list)
    assets: List[JobAssetEntry] = Field(default_factory=list)
