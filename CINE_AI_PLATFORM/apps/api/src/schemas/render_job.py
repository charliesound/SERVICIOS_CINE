from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.render_context import RenderContextFlags


RenderJobStatus = Literal["queued", "running", "succeeded", "failed", "timeout"]


class RenderJobCreateRequest(BaseModel):
    request_payload: Dict[str, Any] = Field(default_factory=dict)
    render_context: Optional[RenderContextFlags] = None


class RenderJobOutputImage(BaseModel):
    """Normalized media reference for a single output image from a render job."""
    filename: str
    subfolder: str = ""
    image_type: str = "output"
    media_url: Optional[str] = None
    view_url: Optional[str] = None
    node_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class RenderJobResult(BaseModel):
    provider: str
    prompt_id: Optional[str] = None
    completion_source: Optional[str] = None
    submit_status_code: Optional[int] = None
    submit_latency_ms: Optional[int] = None
    poll_elapsed_ms: Optional[int] = None
    history_summary: Optional[Dict[str, Any]] = None
    provider_submit_response: Optional[Dict[str, Any]] = None
    output_images: Optional[List[RenderJobOutputImage]] = None


class RenderJobFailure(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class RenderJobData(BaseModel):
    job_id: str
    created_at: str
    updated_at: str
    status: RenderJobStatus
    request_payload: Dict[str, Any] = Field(default_factory=dict)
    parent_job_id: Optional[str] = None
    comfyui_prompt_id: Optional[str] = None
    result: Optional[RenderJobResult] = None
    error: Optional[RenderJobFailure] = None
    duration_ms: Optional[int] = None


class RenderJobItemResponse(BaseModel):
    ok: bool = True
    job: RenderJobData


class RenderJobListResponse(BaseModel):
    ok: bool = True
    jobs: List[RenderJobData] = Field(default_factory=list)
    count: int = 0


class RenderJobError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class RenderJobErrorResponse(BaseModel):
    ok: bool = False
    error: RenderJobError
