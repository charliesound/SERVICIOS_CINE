import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Callable, Awaitable, Optional

from .queue_service import queue_service, QueueStatus, QueueItem
from .instance_registry import registry
from .comfyui_client_factory import factory, ComfyUIClient
from .workflow_builder import builder as workflow_builder

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

            success, error = await self._execute_job(item)
            if not success:
                queue_service.mark_failed(item.job_id, error or "Execution failed")

    async def _execute_job(self, item: QueueItem) -> tuple[bool, Optional[str]]:
        backend = registry.get_backend(item.backend)
        if not backend or not backend.is_available:
            logger.error(f"Backend {item.backend} not available")
            return False, f"Backend {item.backend} not available"

        client = factory.get_client(item.backend)
        if not client:
            logger.error(f"Could not create client for {item.backend}")
            return False, f"Could not create client for {item.backend}"

        prompt_inputs = item.prompt or {}
        if not item.workflow_key or not prompt_inputs:
            missing_parts = []
            if not prompt_inputs:
                missing_parts.append("prompt")
            if not item.workflow_key:
                missing_parts.append("workflow_key")
            error = f"Missing render payload: {'/'.join(missing_parts)} not found"
            logger.error(
                "Render payload missing for job_id=%s backend=%s task_type=%s missing=%s",
                item.job_id,
                item.backend,
                item.task_type,
                ",".join(missing_parts),
            )
            return False, error

        runtime_prompt = workflow_builder.build_runtime_prompt(
            item.workflow_key,
            prompt_inputs,
        )
        if not runtime_prompt:
            error = f"Missing render payload: runtime prompt builder not found for workflow_key={item.workflow_key}"
            logger.error(
                "Runtime prompt builder missing for job_id=%s backend=%s task_type=%s workflow_key=%s prompt_keys=%s",
                item.job_id,
                item.backend,
                item.task_type,
                item.workflow_key,
                sorted(prompt_inputs.keys()),
            )
            return False, error

        queue_service.mark_running(item.job_id)
        logger.info(
            "Starting render job_id=%s task_type=%s backend=%s workflow_key=%s prompt_keys=%s",
            item.job_id,
            item.task_type,
            item.backend,
            item.workflow_key,
            sorted(prompt_inputs.keys()),
        )

        try:
            async with client:
                result = await client.post_prompt(runtime_prompt, item.workflow_key)
                item.prompt_id = result.get("prompt_id") if isinstance(result, dict) else None
                logger.info(
                    "ComfyUI accepted job_id=%s backend=%s workflow_key=%s status=%s prompt_id=%s",
                    item.job_id,
                    item.backend,
                    item.workflow_key,
                    result.get("_http_status") if isinstance(result, dict) else None,
                    item.prompt_id,
                )

                if "prompt_id" in result:
                    prompt_id = result["prompt_id"]
                    await self._wait_for_completion(item, client, prompt_id)
                    return True, None
                return False, "ComfyUI prompt submission did not return prompt_id"
        except Exception as e:
            logger.error(
                "Render execution failed for job_id=%s backend=%s workflow_key=%s error=%s",
                item.job_id,
                item.backend,
                item.workflow_key,
                str(e),
            )
            return False, str(e)

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
                    await self._persist_success_assets(
                        item=item,
                        client=client,
                        prompt_id=prompt_id,
                        history_entry=history[prompt_id],
                    )
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

    async def _persist_success_assets(
        self,
        *,
        item: QueueItem,
        client: ComfyUIClient,
        prompt_id: str,
        history_entry: dict,
    ) -> None:
        from database import AsyncSessionLocal
        from models.storyboard import StoryboardShot
        from .job_tracking_service import job_tracking_service

        async with AsyncSessionLocal() as session:
            created_assets = await job_tracking_service.persist_scheduler_success_assets(
                session,
                job_id=item.job_id,
                prompt_id=prompt_id,
                backend_base_url=client.base_url,
                history_entry=history_entry,
            )
            storyboard_shot_id = (item.metadata or {}).get("storyboard_shot_id")
            image_asset = next(
                (asset for asset in created_assets if str(getattr(asset, "asset_type", "")) == "image"),
                None,
            )
            if storyboard_shot_id and image_asset is not None:
                shot = await session.get(StoryboardShot, storyboard_shot_id)
                if shot is not None:
                    shot.asset_id = str(image_asset.id)
            await session.commit()

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
