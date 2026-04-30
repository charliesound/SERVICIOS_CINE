import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Callable, Awaitable, Optional

from .queue_service import queue_service, QueueStatus, QueueItem
from .instance_registry import registry
from .comfyui_client_factory import factory, ComfyUIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEDULER_POLL_INTERVAL = int(os.getenv("SCHEDULER_POLL_INTERVAL", "5"))
SCHEDULER_JOB_TIMEOUT = int(os.getenv("SCHEDULER_JOB_TIMEOUT", "3600"))
SCHEDULER_MAX_ERRORS = int(os.getenv("SCHEDULER_MAX_CONSECUTIVE_ERRORS", "5"))
SCHEDULER_INITIAL_BACKOFF = int(os.getenv("SCHEDULER_INITIAL_BACKOFF", "2"))
SCHEDULER_MAX_BACKOFF = int(os.getenv("SCHEDULER_MAX_BACKOFF", "30"))


class JobScheduler:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._poll_interval = 5
        self._job_timeout = 3600

    async def start(self):
        async with self._lock:
            if self._running:
                logger.warning("Scheduler already running")
                return
            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Job scheduler started")

    async def stop(self):
        async with self._lock:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("Job scheduler stopped")

    async def _run_loop(self):
        while self._running:
            try:
                await self._process_queues()
                await self._check_timeouts()
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(self._poll_interval)

    async def _process_queues(self):
        backends = ["still", "video", "dubbing", "lab"]

        for backend_key in backends:
            if not queue_service.can_accept_job(backend_key):
                continue

            item = queue_service.get_next_for_backend(backend_key)
            if not item:
                continue

            success = await self._execute_job(item)
            if not success:
                queue_service.mark_failed(item.job_id, "Execution failed")

    async def _execute_job(self, item: QueueItem) -> bool:
        backend = registry.get_backend(item.backend)
        if not backend or not backend.is_available:
            logger.error(f"Backend {item.backend} not available")
            return False

        client = factory.get_client(item.backend)
        if not client:
            logger.error(f"Could not create client for {item.backend}")
            return False

        queue_service.mark_running(item.job_id)
        logger.info(f"Starting job {item.job_id} on {item.backend}")

        try:
            async with client:
                result = await client.post_prompt({}, item.task_type)

                if "prompt_id" in result:
                    prompt_id = result["prompt_id"]
                    await self._wait_for_completion(item, client, prompt_id)
                    return True
                return False
        except Exception as e:
            logger.error(f"Job {item.job_id} failed: {e}")
            return False

    async def _wait_for_completion(
        self, item: QueueItem, client: ComfyUIClient, prompt_id: str
    ):
        max_wait = self._job_timeout
        elapsed = 0
        poll_interval = 2

        while elapsed < max_wait:
            try:
                history = await client.get_history(prompt_id)
                if prompt_id in history:
                    queue_service.mark_succeeded(item.job_id)
                    logger.info(f"Job {item.job_id} succeeded")
                    return
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            except Exception as e:
                logger.error(f"Error checking job status: {e}")
                break

        queue_service.mark_timeout(item.job_id)
        logger.warning(f"Job {item.job_id} timed out")

    async def _check_timeouts(self):
        running_jobs = [
            item
            for item in queue_service._job_map.values()
            if item.status == QueueStatus.RUNNING
        ]

        for item in running_jobs:
            if item.started_at:
                elapsed = (datetime.utcnow() - item.started_at).total_seconds()
                if elapsed > self._job_timeout:
                    logger.warning(f"Job {item.job_id} exceeded timeout")
                    queue_service.mark_timeout(item.job_id)

    async def get_status(self) -> Dict:
        return {
            "running": self._running,
            "poll_interval": self._poll_interval,
            "job_timeout": self._job_timeout,
            "queue_status": queue_service.get_all_status(),
        }


scheduler = JobScheduler()
