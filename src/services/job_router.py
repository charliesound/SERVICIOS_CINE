from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import asyncio

from .instance_registry import InstanceRegistry, registry
from .plan_limits_service import plan_limits_service
from .comfyui_client_factory import (
    ComfyUIFactory,
    factory as comfyui_factory,
    JobRequest,
    JobResponse,
    JobStatus,
)


@dataclass
class Job:
    job_id: str
    task_type: str
    workflow_key: str
    prompt: Dict[str, Any]
    priority: int
    target_backend: str
    user_id: Optional[str] = None
    user_plan: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    outputs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "task_type": self.task_type,
            "workflow_key": self.workflow_key,
            "prompt": self.prompt,
            "priority": self.priority,
            "target_backend": self.target_backend,
            "user_id": self.user_id,
            "user_plan": self.user_plan,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error": self.error,
            "outputs": self.outputs,
        }


class JobRouter:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.registry = registry
        self.factory = comfyui_factory
        self._jobs: Dict[str, Job] = {}
        self._job_lock = asyncio.Lock()

    def _resolve_backend(self, job_request: JobRequest) -> Optional[str]:
        if job_request.target_instance:
            if self.registry.get_backend(job_request.target_instance):
                return job_request.target_instance
            return None

        backend = self.registry.get_backend_for_workflow(job_request.workflow_key)
        if backend:
            return backend.type.value

        backend = self.registry.resolve_backend_for_task(job_request.task_type)
        if backend:
            return backend.type.value

        return None

    def _validate_plan_access(self, plan: str, task_type: str) -> bool:
        return plan_limits_service.can_run_task(plan, task_type)

    async def route_job(self, job_request: JobRequest) -> JobResponse:
        job_id = str(uuid.uuid4())[:8]

        backend_key = self._resolve_backend(job_request)
        if not backend_key:
            return JobResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                backend="",
                backend_url="",
                error=f"No backend found for task_type={job_request.task_type}, workflow={job_request.workflow_key}",
            )

        if job_request.user_plan and not self._validate_plan_access(
            job_request.user_plan, job_request.task_type
        ):
            return JobResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                backend=backend_key,
                backend_url=self.registry.get_backend(backend_key).base_url
                if self.registry.get_backend(backend_key)
                else "",
                error=f"Plan '{job_request.user_plan}' does not allow task type '{job_request.task_type}'",
            )

        backend = self.registry.get_backend(backend_key)
        if not backend or not backend.is_available:
            return JobResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                backend=backend_key,
                backend_url=backend.base_url if backend else "",
                error=f"Backend '{backend_key}' is not available",
            )

        job = Job(
            job_id=job_id,
            task_type=job_request.task_type,
            workflow_key=job_request.workflow_key,
            prompt=job_request.prompt,
            priority=job_request.priority,
            target_backend=backend_key,
            user_id=job_request.user_id,
            user_plan=job_request.user_plan,
        )

        async with self._job_lock:
            self._jobs[job_id] = job

        self.registry.increment_jobs(backend_key)

        return JobResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            backend=backend_key,
            backend_url=backend.base_url,
            queue_position=backend.current_jobs,
            estimated_time=self._estimate_time(backend, job_request.priority),
        )

    def _estimate_time(self, backend, priority: int) -> int:
        base_time = 60
        queue_factor = backend.current_jobs * 30
        priority_factor = (10 - priority) * 5
        return base_time + queue_factor + priority_factor

    async def submit_to_backend(self, job: Job) -> bool:
        client = self.factory.get_client(job.target_backend)
        if not client:
            return False

        async with client:
            try:
                result = await client.post_prompt(job.prompt, job.workflow_key)
                job.started_at = datetime.utcnow()
                return "prompt_id" in result
            except Exception as e:
                job.error = str(e)
                return False

    async def get_job_status(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    async def get_all_jobs(self) -> List[Job]:
        return list(self._jobs.values())

    async def get_jobs_by_backend(self, backend_key: str) -> List[Job]:
        return [j for j in self._jobs.values() if j.target_backend == backend_key]

    async def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False

        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            return False

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        self.registry.decrement_jobs(job.target_backend)
        return True


router = JobRouter()
