from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from schemas.queue_schema import QueueItemResponse, FullQueueStatus
from services.queue_service import queue_service, QueueStatus

router = APIRouter(prefix="/api/queue", tags=["queue"])


@router.get("/status", response_model=FullQueueStatus)
async def get_queue_status():
    status = queue_service.get_all_status()
    
    return {
        "backends": status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status/{job_id}", response_model=QueueItemResponse)
async def get_job_queue_status(job_id: str):
    item = queue_service.get_status(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    
    position = queue_service.get_queue_position(job_id)
    
    return QueueItemResponse(
        job_id=item.job_id,
        status=item.status.value,
        backend=item.backend,
        priority=item.priority,
        created_at=item.created_at.isoformat(),
        queue_position=position
    )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    success = queue_service.cancel(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    return {"message": "Job cancelled", "job_id": job_id}


@router.post("/{job_id}/retry")
async def retry_job(job_id: str):
    success = queue_service.retry(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot retry job")
    return {"message": "Job requeued", "job_id": job_id}
