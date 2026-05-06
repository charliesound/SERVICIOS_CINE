from __future__ import annotations

from typing import Any, Optional

from schemas.auth_schema import TenantContext
from services.comfyui_client_factory import JobRequest
from services.job_router import router as job_router
from services.plan_limits_service import plan_limits_service
from services.queue_service import queue_service


class RenderJobService:
    async def submit_job(
        self,
        *,
        tenant: TenantContext,
        task_type: str,
        workflow_key: str,
        prompt: dict[str, Any],
        priority: int = 5,
        target_instance: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        job_request = JobRequest(
            task_type=task_type,
            workflow_key=workflow_key,
            prompt=prompt,
            priority=priority,
            target_instance=target_instance,
            user_id=tenant.user_id,
            user_plan=tenant.plan,
            parameters=metadata or {},
        )

        response = await job_router.route_job(job_request)
        if response.status.value == "failed":
            return response, None

        queue_item = queue_service.enqueue(
            job_id=response.job_id,
            task_type=task_type,
            backend=response.backend,
            priority=priority + plan_limits_service.get_priority_score(tenant.plan),
            user_plan=tenant.plan,
            user_id=tenant.user_id,
            workflow_key=workflow_key,
            prompt=prompt,
            metadata=metadata or {},
            project_id=project_id,
            organization_id=tenant.organization_id,
            created_by=tenant.user_id,
            target_instance=target_instance,
        )
        return response, queue_item


render_job_service = RenderJobService()
