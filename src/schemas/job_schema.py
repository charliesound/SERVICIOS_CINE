from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class JobCreate(BaseModel):
    task_type: str
    workflow_key: str
    prompt: Dict[str, Any]
    priority: int = 5
    target_instance: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class JobSubmit(BaseModel):
    task_type: str
    workflow_key: str
    prompt: Dict[str, Any]
    user_id: str
    user_plan: str
    priority: int = 5
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
