from __future__ import annotations

import threading
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Optional

from schemas.cid_pipeline_schema import (
    CIDPipelineDefinition,
    CIDPipelineJobHistoryEvent,
    CIDPipelineJobResponse,
    CIDPipelineValidationResponse,
)


class CIDPipelineSimulatedJobService:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._jobs: dict[str, CIDPipelineJobResponse] = {}
        self._lock = threading.RLock()

    def create_job(
        self,
        *,
        organization_id: str,
        user_id: str,
        project_id: Optional[str],
        pipeline: CIDPipelineDefinition,
        validation: CIDPipelineValidationResponse,
    ) -> CIDPipelineJobResponse:
        now = datetime.utcnow()
        job_id = uuid.uuid4().hex
        history = [
            self._event("created", "created", "Simulated job created", now),
            self._event("validated", "validated", "Pipeline validation completed", now),
            self._event("queued", "simulated/queued", "Simulated job queued", now),
        ]
        job = CIDPipelineJobResponse(
            job_id=job_id,
            mode="simulated",
            status="simulated/queued",
            organization_id=organization_id,
            user_id=user_id,
            project_id=project_id,
            pipeline_id=pipeline.pipeline_id,
            task_type=pipeline.task_type,
            preset_key=pipeline.preset_key,
            created_at=now,
            updated_at=now,
            validation=validation,
            history=history,
            pipeline=deepcopy(pipeline),
        )
        with self._lock:
            self._jobs[job_id] = job
        return deepcopy(job)

    def list_jobs(
        self,
        *,
        organization_id: str,
        user_id: str,
        project_id: Optional[str] = None,
        is_global_admin: bool = False,
    ) -> list[CIDPipelineJobResponse]:
        with self._lock:
            jobs = list(self._jobs.values())
        
        filtered = []
        for job in jobs:
            # Global Admin bypasses user/org filters
            # If a project_id is provided, we still filter by it for precision
            if is_global_admin:
                if project_id is None or job.project_id == project_id:
                    filtered.append(deepcopy(job))
                continue
            
            # Normal user filter
            if (job.organization_id == organization_id and 
                job.user_id == user_id and 
                (project_id is None or job.project_id == project_id)):
                filtered.append(deepcopy(job))
                
        filtered.sort(key=lambda item: (item.created_at, item.job_id), reverse=True)
        return filtered

    def get_job(
        self,
        *,
        job_id: str,
        organization_id: str,
        user_id: str,
        is_global_admin: bool = False,
    ) -> Optional[CIDPipelineJobResponse]:
        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            return None
        
        if is_global_admin:
            return deepcopy(job)
            
        if job.organization_id != organization_id or job.user_id != user_id:
            return None
        return deepcopy(job)

    def _event(self, event_type: str, status: str, message: str, created_at: datetime) -> CIDPipelineJobHistoryEvent:
        return CIDPipelineJobHistoryEvent(
            id=uuid.uuid4().hex,
            event_type=event_type,
            status=status,
            message=message,
            created_at=created_at,
        )


cid_pipeline_simulated_job_service = CIDPipelineSimulatedJobService()
