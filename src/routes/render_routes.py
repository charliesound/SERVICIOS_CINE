import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.job_schema import JobSubmit, JobResponse, JobDetail
from services.render_job_service import render_job_service
from services.job_router import router as job_router, JobRequest
from services.queue_service import queue_service
from services.job_tracking_service import job_tracking_service
from services.plan_limits_service import plan_limits_service
from database import AsyncSessionLocal

router = APIRouter(prefix="/api/render", tags=["render"])

MAX_PROMPT_BYTES = 50_000


def _serialized_prompt_size(prompt: dict) -> int:
    return len(json.dumps(prompt, ensure_ascii=False).encode("utf-8"))


def _sanitize_job_error(status: str, error: Optional[str]) -> Optional[str]:
    if not error:
        return None
    normalized_status = (status or "").lower()
    if normalized_status == "timeout":
        return "Render job timed out"
    if normalized_status == "canceled":
        return "Render job cancelled"
    if normalized_status in {"failed", "rejected"}:
        return "Render job failed"
    return error


async def _get_owned_job_resources(job_id: str, user_id: str):
    queue_item = queue_service.get_status(job_id)
    if queue_item and queue_item.user_id == user_id:
        return None, queue_item

    job = await job_router.get_job_status(job_id)
    if job and job.user_id == user_id:
        return job, None

    return None, None


def _public_job_response(response: JobResponse) -> JobResponse:
    return JobResponse(
        job_id=response.job_id,
        status=response.status,
        backend=response.backend,
        backend_url="",
        queue_position=response.queue_position,
        estimated_time=response.estimated_time,
        error=None,
    )


async def _get_tracking_payload(job_id: str) -> dict[str, list[dict]]:
    async with AsyncSessionLocal() as session:
        return await job_tracking_service.build_job_tracking_payload(
            session,
            job_id=job_id,
        )


@router.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobSubmit,
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        prompt_size = _serialized_prompt_size(job_data.prompt)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid render prompt payload")

    if prompt_size > MAX_PROMPT_BYTES:
        raise HTTPException(status_code=413, detail="Prompt payload too large")

    plan = plan_limits_service.get_plan(tenant.plan)
    if not plan:
        raise HTTPException(status_code=403, detail="Plan not available for this account")

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

    if plan and not plan_limits_service.can_run_task(
        tenant.plan, job_data.task_type
    ):
        raise HTTPException(
            status_code=403,
            detail="Current plan does not allow this render task",
        )

    try:
        response, queue_item = await render_job_service.submit_job(
            tenant=tenant,
            task_type=job_data.task_type,
            workflow_key=job_data.workflow_key,
            prompt=job_data.prompt,
            priority=job_data.priority,
            target_instance=job_data.target_instance,
            project_id=job_data.project_id,
            metadata=job_data.parameters,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Render service unavailable")

    if response.status.value == "failed":
        error_text = (response.error or "").lower()
        if "plan" in error_text or "not allowed" in error_text:
            raise HTTPException(
                status_code=403,
                detail=response.error or "Current plan does not allow this render task",
            )
        if "backend" in error_text or "no backend" in error_text or "unavailable" in error_text or "not reachable" in error_text:
            raise HTTPException(
                status_code=503,
                detail=response.error or "Render backend unavailable",
            )
        raise HTTPException(status_code=422, detail=response.error or "Render job failed")

    if queue_item is None and response.status.value != "failed":
        raise HTTPException(status_code=503, detail="Render queue unavailable")

    return _public_job_response(response)


@router.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
):
    job, queue_item = await _get_owned_job_resources(job_id, tenant.user_id)
    if not job:
        if not queue_item:
            raise HTTPException(status_code=404, detail="Job not found")

        tracking_payload = await _get_tracking_payload(job_id)

        return JobDetail(
            job_id=queue_item.job_id,
            task_type=queue_item.task_type,
            workflow_key=queue_item.workflow_key or "",
            status=queue_item.status.value,
            backend=queue_item.backend,
            created_at=queue_item.created_at.isoformat(),
            started_at=queue_item.started_at.isoformat()
            if queue_item.started_at
            else None,
            completed_at=(
                queue_item.completed_at.isoformat() if queue_item.completed_at else None
            ),
            error=_sanitize_job_error(queue_item.status.value, queue_item.error),
            queue_position=queue_service.get_queue_position(job_id),
            history=tracking_payload["history"],
            assets=tracking_payload["assets"],
        )

    tracking_payload = await _get_tracking_payload(job_id)

    return JobDetail(
        job_id=job.job_id,
        task_type=job.task_type,
        workflow_key=job.workflow_key,
        status=job.status.value,
        backend=job.target_backend,
        created_at=job.created_at.isoformat() if job.created_at else "",
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=_sanitize_job_error(job.status.value, job.error),
        history=tracking_payload["history"],
        assets=tracking_payload["assets"],
    )


@router.get("/jobs", response_model=list)
async def list_jobs(
    user_id: Optional[str] = None,
    backend: Optional[str] = None,
    tenant: TenantContext = Depends(get_tenant_context),
):
    all_jobs = await job_router.get_all_jobs()
    _ = user_id

    all_jobs = [j for j in all_jobs if j.user_id == tenant.user_id]
    if backend:
        all_jobs = [j for j in all_jobs if j.target_backend == backend]

    return [
        JobDetail(
            job_id=j.job_id,
            task_type=j.task_type,
            workflow_key=j.workflow_key,
            status=j.status.value,
            backend=j.target_backend,
            created_at=j.created_at.isoformat() if j.created_at else "",
            started_at=j.started_at.isoformat() if j.started_at else None,
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
            error=_sanitize_job_error(j.status.value, j.error),
        )
        for j in all_jobs
    ]


@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
):
    job, queue_item = await _get_owned_job_resources(job_id, tenant.user_id)
    if not job and not queue_item:
        raise HTTPException(status_code=404, detail="Job not found")

    success = queue_service.retry(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot retry job")

    job = await job_router.get_job_status(job_id)
    if job:
        return JobResponse(
            job_id=job_id,
            status="queued",
            backend=job.target_backend,
            backend_url="",
            queue_position=1,
        )

    return JobResponse(job_id=job_id, status="queued", backend="", backend_url="")
