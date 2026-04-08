from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QueueItemResponse(BaseModel):
    job_id: str
    status: str
    backend: str
    priority: int
    created_at: str
    queue_position: Optional[int] = None


class QueueStatusResponse(BaseModel):
    backend: str
    queue_size: int
    running: int
    max_concurrent: int
    items: List[Dict[str, Any]]


class FullQueueStatus(BaseModel):
    backends: Dict[str, QueueStatusResponse]
    timestamp: str
