from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import threading


class QueueStatus(Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELED = "canceled"
    REJECTED = "rejected"


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
        self._queue: Dict[str, List[QueueItem]] = defaultdict(list)
        self._running: Dict[str, List[str]] = defaultdict(list)
        self._completed: Dict[str, QueueItem] = {}
        self._job_map: Dict[str, QueueItem] = {}
        self._config = QueueConfig()

    def enqueue(self, job_id: str, task_type: str, backend: str, 
                priority: int, user_plan: str, user_id: Optional[str] = None) -> Optional[QueueItem]:
        
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
                error="Plan does not have lab access"
            )
            self._job_map[job_id] = item
            return None

        item = QueueItem(
            job_id=job_id,
            task_type=task_type,
            backend=backend,
            priority=priority,
            user_plan=user_plan,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        self._queue[backend].append(item)
        self._queue[backend].sort(key=lambda x: (-x.priority, x.created_at))
        self._job_map[job_id] = item
        return item

    def get_status(self, job_id: str) -> Optional[QueueItem]:
        return self._job_map.get(job_id)

    def get_all_status(self) -> Dict[str, Any]:
        return {
            backend: {
                "queue_size": len(queue),
                "running": len(self._running.get(backend, [])),
                "max_concurrent": self._config.MAX_CONCURRENT.get(backend, 1),
                "items": [
                    {"job_id": i.job_id, "status": i.status.value, "priority": i.priority}
                    for i in queue
                ]
            }
            for backend, queue in self._queue.items()
        }

    def get_next_for_backend(self, backend: str) -> Optional[QueueItem]:
        max_concurrent = self._config.MAX_CONCURRENT.get(backend, 1)
        current_running = len(self._running.get(backend, []))
        
        if current_running >= max_concurrent:
            return None

        if not self._queue[backend]:
            return None

        return self._queue[backend].pop(0)

    def mark_running(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item or item.status != QueueStatus.QUEUED:
            return False
        
        item.status = QueueStatus.RUNNING
        item.started_at = datetime.utcnow()
        self._running[item.backend].append(job_id)
        return True

    def mark_succeeded(self, job_id: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False
        
        item.status = QueueStatus.SUCCEEDED
        item.completed_at = datetime.utcnow()
        self._release_slot(job_id)
        self._completed[job_id] = item
        return True

    def mark_failed(self, job_id: str, error: str) -> bool:
        item = self._job_map.get(job_id)
        if not item:
            return False
        
        if item.retry_count < item.max_retries:
            item.retry_count += 1
            item.status = QueueStatus.QUEUED
            self._queue[item.backend].insert(0, item)
        else:
            item.status = QueueStatus.FAILED
            item.error = error
            item.completed_at = datetime.utcnow()
            self._completed[job_id] = item
        
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
            self._queue[item.backend] = [i for i in self._queue[item.backend] if i.job_id != job_id]
        
        self._completed[job_id] = item
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
        self._queue[item.backend].insert(0, item)
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


queue_service = QueueService()
