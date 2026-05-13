from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext
from schemas.queue_schema import QueueItemResponse, FullQueueStatus
from services.queue_service import queue_service, QueueStatus
from services.plan_limits_service import plan_limits_service

router = APIRouter(prefix="/api/queue", tags=["queue"])


def _resolve_owned_queue_item(job_id: str, tenant: TenantContext):
    item = queue_service.get_status(job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Job not found")
    if not tenant.is_global_admin and item.user_id != tenant.user_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return item


@router.get("/status", response_model=FullQueueStatus)
async def get_queue_status(tenant: TenantContext = Depends(get_tenant_context)):
    raw_status = queue_service.get_all_status(
        None if tenant.is_global_admin else tenant.user_id
    )
    status = {
        backend: {"backend": backend, **details}
        for backend, details in raw_status.items()
    }

    return {
        "backends": status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status/{job_id}", response_model=QueueItemResponse)
async def get_job_queue_status(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
):
    item = _resolve_owned_queue_item(job_id, tenant)

    position = queue_service.get_queue_position(job_id)

    return QueueItemResponse(
        job_id=item.job_id,
        status=item.status.value,
        backend=item.backend,
        priority=item.priority,
        created_at=item.created_at.isoformat(),
        queue_position=position,
    )


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    _: None = Depends(require_write_permission),
):
    item = _resolve_owned_queue_item(job_id, tenant)

    if item.status == QueueStatus.RUNNING:
        raise HTTPException(
            status_code=409,
            detail="Running jobs cannot be cancelled safely in this demo",
        )
    if item.status not in {QueueStatus.QUEUED, QueueStatus.SCHEDULED}:
        raise HTTPException(status_code=400, detail="Cannot cancel job")

    success = queue_service.cancel(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    return {"message": "Job cancelled", "job_id": job_id}


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    _: None = Depends(require_write_permission),
):
    item = _resolve_owned_queue_item(job_id, tenant)

    plan = plan_limits_service.get_plan(tenant.plan)
    if not plan:
        raise HTTPException(status_code=403, detail="Plan not available for this account")

    if not plan_limits_service.can_run_task(tenant.plan, item.task_type):
        raise HTTPException(
            status_code=403,
            detail="Current plan does not allow this render task",
        )

    counts = queue_service.count_user_jobs(tenant.user_id)
    can_submit_active = (
        plan.max_active_jobs == -1 or counts["running"] < plan.max_active_jobs
    )
    can_submit_queued = (
        plan.max_queued_jobs == -1 or counts["queued"] < plan.max_queued_jobs
    )
    if not can_submit_active and not can_submit_queued:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Has alcanzado la capacidad operativa de tu plan {plan.display_name}. "
                f"Libera jobs en curso o activa un plan superior para seguir enviando trabajo."
            ),
        )

    success = queue_service.retry(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot retry job")
    return {"message": "Job requeued", "job_id": job_id}
