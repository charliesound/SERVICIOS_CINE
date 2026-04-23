from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from schemas.job_schema import JobSubmit, JobResponse, JobDetail
from services.job_router import router as job_router, JobRequest
from services.queue_service import queue_service
from services.plan_limits_service import plan_limits_service
from services.instance_registry import registry

router = APIRouter(prefix="/api/render", tags=["render"])


@router.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobSubmit):
    plan = plan_limits_service.get_plan(job_data.user_plan)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    counts = queue_service.count_user_jobs(job_data.user_id)
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
        job_data.user_plan, job_data.task_type
    ):
        raise HTTPException(
            status_code=403,
            detail=f"Plan '{job_data.user_plan}' does not allow task type '{job_data.task_type}'",
        )

    job_request = JobRequest(
        task_type=job_data.task_type,
        workflow_key=job_data.workflow_key,
        prompt=job_data.prompt,
        priority=job_data.priority,
        target_instance=job_data.target_instance,
        user_id=job_data.user_id,
        user_plan=job_data.user_plan,
    )

    response = await job_router.route_job(job_request)

    if response.status.value == "failed":
        raise HTTPException(status_code=400, detail=response.error)

    if response.status.value == "queued":
        queue_service.enqueue(
            job_id=response.job_id,
            task_type=job_data.task_type,
            backend=response.backend,
            priority=job_data.priority + plan.priority_score
            if plan
            else job_data.priority,
            user_plan=job_data.user_plan,
            user_id=job_data.user_id,
        )

    return response


@router.get("/jobs/{job_id}", response_model=JobDetail)
async def get_job(job_id: str):
    job = await job_router.get_job_status(job_id)
    if not job:
        queue_item = queue_service.get_status(job_id)
        if not queue_item:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobDetail(
            job_id=queue_item.job_id,
            task_type=queue_item.task_type,
            workflow_key="",
            status=queue_item.status.value,
            backend=queue_item.backend,
            created_at=queue_item.created_at.isoformat(),
            queue_position=queue_service.get_queue_position(job_id),
        )

    return JobDetail(
        job_id=job.job_id,
        task_type=job.task_type,
        workflow_key=job.workflow_key,
        status=job.status.value,
        backend=job.target_backend,
        created_at=job.created_at.isoformat() if job.created_at else "",
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=job.error,
    )


@router.get("/jobs", response_model=list)
async def list_jobs(user_id: Optional[str] = None, backend: Optional[str] = None):
    all_jobs = await job_router.get_all_jobs()

    if user_id:
        all_jobs = [j for j in all_jobs if j.user_id == user_id]
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
            error=j.error,
        )
        for j in all_jobs
    ]


@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: str):
    success = queue_service.retry(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot retry job")

    job = await job_router.get_job_status(job_id)
    if job:
        backend = registry.get_backend(job.target_backend)
        return JobResponse(
            job_id=job_id,
            status="queued",
            backend=job.target_backend,
            backend_url=backend.base_url if backend else "",
            queue_position=1,
        )

    return JobResponse(job_id=job_id, status="queued", backend="", backend_url="")
