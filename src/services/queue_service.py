from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    from models.core import ProjectJob


logger = logging.getLogger(__name__)

QUEUE_RUNTIME_ORGANIZATION_ID = "__queue_runtime__"
QUEUE_RUNTIME_PROJECT_ID = "__queue_runtime__"


class QueueStatus(Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELED = "canceled"
    REJECTED = "rejected"


TERMINAL_STATUSES = {
    QueueStatus.SUCCEEDED.value,
    QueueStatus.FAILED.value,
    QueueStatus.TIMEOUT.value,
    QueueStatus.CANCELED.value,
    QueueStatus.REJECTED.value,
}


@dataclass
class QueueItem:
    job_id: str
    task_type: str
    backend: str
    priority: int
    user_plan: str
    user_id: Optional[str]
    created_at: datetime
    status: QueueStatus = QueueStatus.QUEUED
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class QueueConfig:
    MAX_CONCURRENT = {
        "still": 2,
        "video": 1,
        "dubbing": 2,
        "lab": 1,
        "matcher": 2,  # Allow up to 2 concurrent matcher jobs
    }
    PLAN_LAB_ACCESS = ["pro", "enterprise"]


class QueueService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._persistence_mode = (
            os.getenv("QUEUE_PERSISTENCE_MODE", "memory").strip().lower() or "memory"
        )
        if self._persistence_mode not in {"memory", "db"}:
            logger.warning(
                "Unsupported queue persistence mode '%s'; falling back to memory-only queue",
                self._persistence_mode,
            )
            self._persistence_mode = "memory"
        self._queue: Dict[str, List[QueueItem]] = defaultdict(list)
        self._running: Dict[str, List[str]] = defaultdict(list)
        self._completed: Dict[str, QueueItem] = {}
        self._job_map: Dict[str, QueueItem] = {}
        self._config = QueueConfig()
        self._state_lock = threading.RLock()
        if self._persistence_mode == "db":
            logger.info(
                "QueueService running in db mode with durable ProjectJob persistence"
            )
        else:
            logger.warning(
                "QueueService running in memory mode. Jobs are not durable across process restarts."
            )

    def _is_db_mode(self) -> bool:
        return self._persistence_mode == "db"

    def _reset_runtime_state(self) -> None:
        self._queue = defaultdict(list)
        self._running = defaultdict(list)
        self._completed = {}
        self._job_map = {}

    def _queue_job_type(self, item: QueueItem) -> str:
        return f"render:{item.task_type}"

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _serialize_item(
        self,
        item: QueueItem,
        event: Optional[str] = None,
        recovery_reason: Optional[str] = None,
    ) -> str:
        payload = {
            "job_id": item.job_id,
            "task_type": item.task_type,
            "backend": item.backend,
            "priority": item.priority,
            "user_plan": item.user_plan,
            "user_id": item.user_id,
            "status": item.status.value,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "scheduled_at": item.scheduled_at.isoformat()
            if item.scheduled_at
            else None,
            "started_at": item.started_at.isoformat() if item.started_at else None,
            "completed_at": item.completed_at.isoformat()
            if item.completed_at
            else None,
            "error": item.error,
            "retry_count": item.retry_count,
            "max_retries": item.max_retries,
            "event": event,
            "recovery_reason": recovery_reason,
        }
        return json.dumps(payload, ensure_ascii=True)

    def _deserialize_payload(self, value: Optional[str]) -> Dict[str, Any]:
        if not value:
            return {}
        try:
            payload = json.loads(value)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            logger.warning("Invalid queue payload JSON ignored")
        return {}

    def _item_from_record(self, record: ProjectJob) -> QueueItem:
        payload = self._deserialize_payload(record.result_data)
        status_value = (
            record.status or payload.get("status") or QueueStatus.QUEUED.value
        )
        try:
            status = QueueStatus(status_value)
        except ValueError:
            status = QueueStatus.QUEUED

        task_type = payload.get("task_type") or (record.job_type or "render:still")
        if isinstance(task_type, str) and task_type.startswith("render:"):
            task_type = task_type.split(":", 1)[1]

        return QueueItem(
            job_id=record.id,
            task_type=task_type,
            backend=payload.get("backend") or "still",
            priority=int(payload.get("priority") or 0),
            user_plan=payload.get("user_plan") or "free",
            user_id=payload.get("user_id") or record.created_by,
            created_at=record.created_at
            or self._parse_datetime(payload.get("created_at"))
            or datetime.utcnow(),
            status=status,
            scheduled_at=self._parse_datetime(payload.get("scheduled_at")),
            started_at=self._parse_datetime(payload.get("started_at")),
            completed_at=record.completed_at
            or self._parse_datetime(payload.get("completed_at")),
            error=record.error_message or payload.get("error"),
            retry_count=int(payload.get("retry_count") or 0),
            max_retries=int(payload.get("max_retries") or 3),
        )

    def _get_db_types(self):
        from database import AsyncSessionLocal
        from models.core import ProjectJob

        return AsyncSessionLocal, ProjectJob

    def _run_db(self, coroutine):
        result: Dict[str, Any] = {}
        error: Dict[str, BaseException] = {}

        def runner() -> None:
            try:
                result["value"] = asyncio.run(coroutine)
            except BaseException as exc:  # pragma: no cover - surfaced to caller
                error["value"] = exc

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join()

        if "value" in error:
            raise error["value"]
        return result.get("value")

    async def _persist_transition_async(
        self,
        item: QueueItem,
        event: Optional[str],
        recovery_reason: Optional[str] = None,
    ) -> None:
        AsyncSessionLocal, ProjectJob = self._get_db_types()
        from services.job_tracking_service import job_tracking_service

        async with AsyncSessionLocal() as session:
            record = await session.get(ProjectJob, item.job_id)
            created_record = record is None
            previous_status = record.status if record is not None else None
            payload = self._serialize_item(
                item,
                event=event,
                recovery_reason=recovery_reason,
            )
            if record is None:
                record = ProjectJob(
                    id=item.job_id,
                    organization_id=QUEUE_RUNTIME_ORGANIZATION_ID,
                    project_id=QUEUE_RUNTIME_PROJECT_ID,
                    job_type=self._queue_job_type(item),
                    status=item.status.value,
                    result_data=payload,
                    error_message=item.error,
                    created_by=item.user_id,
                    created_at=item.created_at,
                    updated_at=datetime.utcnow(),
                    completed_at=item.completed_at,
                )
                session.add(record)
                await session.flush()
            else:
                if (
                    record.organization_id != QUEUE_RUNTIME_ORGANIZATION_ID
                    or record.project_id != QUEUE_RUNTIME_PROJECT_ID
                ):
                    logger.warning(
                        "Skipping durable queue write for non-queue ProjectJob id=%s",
                        item.job_id,
                    )
                    return
                record.job_type = self._queue_job_type(item)
                record.status = item.status.value
                record.result_data = payload
                record.error_message = item.error
                record.created_by = item.user_id
                record.updated_at = datetime.utcnow()
                record.completed_at = item.completed_at

            if event:
                await job_tracking_service.record_queue_transition(
                    session,
                    job_id=item.job_id,
                    organization_id=record.organization_id,
                    project_id=record.project_id,
                    created_by=item.user_id,
                    current_status=item.status.value,
                    previous_status=previous_status,
                    event=event,
                    task_type=item.task_type,
                    backend=item.backend,
                    priority=item.priority,
                    user_plan=item.user_plan,
                    retry_count=item.retry_count,
                    error=item.error,
                    recovery_reason=recovery_reason,
                    created_record=created_record,
                )

            await session.commit()

    async def _load_persisted_jobs_async(self) -> List[ProjectJob]:
        AsyncSessionLocal, ProjectJob = self._get_db_types()
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProjectJob)
                .where(
                    ProjectJob.organization_id == QUEUE_RUNTIME_ORGANIZATION_ID,
                    ProjectJob.project_id == QUEUE_RUNTIME_PROJECT_ID,
                )
                .order_by(ProjectJob.created_at.asc(), ProjectJob.id.asc())
            )
            return list(result.scalars().all())

    async def _get_persisted_job_async(self, job_id: str) -> Optional[ProjectJob]:
        AsyncSessionLocal, ProjectJob = self._get_db_types()
        async with AsyncSessionLocal() as session:
            record = await session.get(ProjectJob, job_id)
            if record is None:
                return None
            if (
                record.organization_id != QUEUE_RUNTIME_ORGANIZATION_ID
                or record.project_id != QUEUE_RUNTIME_PROJECT_ID
            ):
                return None
            return record

    def _record_transition(
        self,
        item: QueueItem,
        event: str,
        recovery_reason: Optional[str] = None,
    ) -> None:
        if not self._is_db_mode():
            return
        self._run_db(
            self._persist_transition_async(
                item,
                event=event,
                recovery_reason=recovery_reason,
            )
        )

    def recover_on_startup(self) -> Dict[str, Any]:
        summary = {
            "mode": self._persistence_mode,
            "requeued": 0,
            "failed": 0,
            "untouched_terminal": 0,
            "loaded": 0,
        }
        with self._state_lock:
            self._reset_runtime_state()
            if not self._is_db_mode():
                return summary

            records: List[ProjectJob] = list(
                self._run_db(self._load_persisted_jobs_async()) or []
            )
            for record in records:
                item = self._item_from_record(record)
                self._job_map[item.job_id] = item
                summary["loaded"] += 1

                if item.status in {QueueStatus.QUEUED, QueueStatus.SCHEDULED}:
                    recovery_tag = "startup_requeue"
                    if item.status == QueueStatus.SCHEDULED:
                        item.status = QueueStatus.QUEUED
                        item.scheduled_at = None
                    self._record_transition(
                        item,
                        recovery_tag,
                        recovery_reason="startup_requeue",
                    )
                    self._queue[item.backend].append(item)
                    summary["requeued"] += 1
                    continue

                if item.status == QueueStatus.RUNNING:
                    item.status = QueueStatus.FAILED
                    item.error = "backend_restart"
                    item.completed_at = datetime.utcnow()
                    self._completed[item.job_id] = item
                    self._record_transition(
                        item,
                        "startup_failed",
                        recovery_reason="backend_restart",
                    )
                    summary["failed"] += 1
                    continue

                if item.status.value in TERMINAL_STATUSES:
                    self._completed[item.job_id] = item
                    summary["untouched_terminal"] += 1

            for backend in list(self._queue.keys()):
                self._queue[backend].sort(key=lambda x: (-x.priority, x.created_at))

        return summary

    def get_runtime_mode(self) -> Dict[str, Any]:
        return {
            "persistence_mode": self._persistence_mode,
            "durable": self._is_db_mode(),
            "production_ready": self._is_db_mode(),
        }

    def enqueue(
        self,
        job_id: str,
        task_type: str,
        backend: str,
        priority: int,
        user_plan: str,
        user_id: Optional[str] = None,
    ) -> Optional[QueueItem]:
        if backend == "lab" and user_plan not in self._config.PLAN_LAB_ACCESS:
            item = QueueItem(
                job_id=job_id,
                task_type=task_type,
                backend=backend,
                priority=priority,
                user_plan=user_plan,
                user_id=user_id,
                created_at=datetime.utcnow(),
                status=QueueStatus.REJECTED,
                error="Plan does not have lab access",
            )
            self._job_map[job_id] = item
            self._record_transition(item, "rejected")
            return None

        item = QueueItem(
            job_id=job_id,
            task_type=task_type,
            backend=backend,
            priority=priority,
            user_plan=user_plan,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )

        with self._state_lock:
            self._queue[backend].append(item)
            self._queue[backend].sort(key=lambda x: (-x.priority, x.created_at))
            self._job_map[job_id] = item
            self._record_transition(item, "enqueue")
        return item

    def get_status(self, job_id: str) -> Optional[QueueItem]:
        item = self._job_map.get(job_id)
        if item or not self._is_db_mode():
            return item

        record = self._run_db(self._get_persisted_job_async(job_id))
        if not record:
            return None

        item = self._item_from_record(record)
        self._job_map[job_id] = item
        if item.status.value in TERMINAL_STATUSES:
            self._completed[job_id] = item
        return item

    def get_all_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        backends = set(self._config.MAX_CONCURRENT.keys())
        backends.update(self._queue.keys())
        backends.update(self._running.keys())
        return {
            backend: {
                "queue_size": len(filtered_queue),
                "running": len(filtered_running),
                "max_concurrent": self._config.MAX_CONCURRENT.get(backend, 1),
                "items": [
                    {
                        "job_id": i.job_id,
                        "status": i.status.value,
                        "priority": i.priority,
                    }
                    for i in filtered_queue
                ],
            }
            for backend in sorted(backends)
            for queue in [self._queue.get(backend, [])]
            for filtered_queue in [
                queue
                if user_id is None
                else [item for item in queue if item.user_id == user_id]
            ]
            for filtered_running in [
                self._running.get(backend, [])
                if user_id is None
                else [
                    job_id
                    for job_id in self._running.get(backend, [])
                    if self._job_map.get(job_id) is not None
                    and self._job_map[job_id].user_id == user_id
                ]
            ]
        }

    def get_next_for_backend(self, backend: str) -> Optional[QueueItem]:
        max_concurrent = self._config.MAX_CONCURRENT.get(backend, 1)
        current_running = len(self._running.get(backend, []))

        if current_running >= max_concurrent:
            return None

        if not self._queue[backend]:
            return None

        with self._state_lock:
            item = self._queue[backend].pop(0)
            item.status = QueueStatus.SCHEDULED
            item.scheduled_at = datetime.utcnow()
            self._record_transition(item, "scheduled")
            return item

    def mark_running(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item or item.status not in {QueueStatus.QUEUED, QueueStatus.SCHEDULED}:
            return False

        item.status = QueueStatus.RUNNING
        item.started_at = datetime.utcnow()
        if job_id not in self._running[item.backend]:
            self._running[item.backend].append(job_id)
        self._record_transition(item, "running")
        return True

    def mark_succeeded(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False

        item.status = QueueStatus.SUCCEEDED
        item.completed_at = datetime.utcnow()
        self._release_slot(job_id)
        self._completed[job_id] = item
        self._record_transition(item, "succeeded")
        return True

    def mark_failed(self, job_id: str, error: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False

        if item.retry_count < item.max_retries:
            item.retry_count += 1
            item.status = QueueStatus.QUEUED
            item.error = error
            item.scheduled_at = None
            item.started_at = None
            item.completed_at = None
            self._queue[item.backend].insert(0, item)
            self._record_transition(item, "retry_queued")
        else:
            item.status = QueueStatus.FAILED
            item.error = error
            item.completed_at = datetime.utcnow()
            self._completed[job_id] = item
            self._record_transition(item, "failed")

        self._release_slot(job_id)
        return True

    def mark_timeout(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False

        item.status = QueueStatus.TIMEOUT
        item.completed_at = datetime.utcnow()
        self._release_slot(job_id)
        self._completed[job_id] = item
        self._record_transition(item, "timeout")
        return True

    def cancel(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False

        if item.status == QueueStatus.RUNNING:
            item.status = QueueStatus.CANCELED
            item.completed_at = datetime.utcnow()
            self._release_slot(job_id)
        elif item.status == QueueStatus.QUEUED:
            item.status = QueueStatus.CANCELED
            item.completed_at = datetime.utcnow()
            self._queue[item.backend] = [
                i for i in self._queue[item.backend] if i.job_id != job_id
            ]
        elif item.status == QueueStatus.SCHEDULED:
            item.status = QueueStatus.CANCELED
            item.completed_at = datetime.utcnow()

        self._completed[job_id] = item
        self._record_transition(item, "canceled")
        return True

    def retry(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False

        if item.status not in [QueueStatus.FAILED, QueueStatus.TIMEOUT]:
            return False

        item.status = QueueStatus.QUEUED
        item.retry_count = 0
        item.error = None
        item.completed_at = None
        item.started_at = None
        item.scheduled_at = None
        self._queue[item.backend].insert(0, item)
        self._record_transition(item, "manual_retry")
        return True

    def _release_slot(self, job_id: str):
        item = self._job_map.get(job_id)
        if item and job_id in self._running.get(item.backend, []):
            self._running[item.backend].remove(job_id)

    def get_running_count(self, backend: str) -> int:
        return len(self._running.get(backend, []))

    def can_accept_job(self, backend: str) -> bool:
        max_concurrent = self._config.MAX_CONCURRENT.get(backend, 1)
        return self.get_running_count(backend) < max_concurrent

    def get_queue_position(self, job_id: str) -> Optional[int]:
        item = self._job_map.get(job_id)
        if not item:
            return None

        if item.status != QueueStatus.QUEUED:
            return None

        queue = self._queue.get(item.backend, [])
        for i, q_item in enumerate(queue):
            if q_item.job_id == job_id:
                return i + 1
        return None

    def count_user_jobs(self, user_id: str) -> Dict[str, int]:
        queued = 0
        running = 0
        for item in self._job_map.values():
            if item.user_id != user_id:
                continue
            if item.status == QueueStatus.QUEUED:
                queued += 1
            elif item.status == QueueStatus.RUNNING:
                running += 1
        return {"queued": queued, "running": running}


queue_service = QueueService()
