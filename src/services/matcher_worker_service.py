from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .queue_service import queue_service, QueueStatus, QueueItem
from routes.matcher_routes import process_matcher_job
from database import AsyncSessionLocal
from models.matcher import MatcherJob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MATCHER_WORKER_POLL_INTERVAL = int("5")
MATCHER_WORKER_BATCH_SIZE = int("1")


class MatcherWorkerService:
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
        self._poll_interval = MATCHER_WORKER_POLL_INTERVAL
        self._batch_size = MATCHER_WORKER_BATCH_SIZE

    async def start(self):
        async with self._lock:
            if self._running:
                logger.warning("Matcher worker already running")
                return
            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Matcher worker started")

    async def stop(self):
        async with self._lock:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("Matcher worker stopped")

    async def _run_loop(self):
        while self._running:
            try:
                await self._process_matcher_queue()
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Matcher worker error: {e}")
                await asyncio.sleep(self._poll_interval)

    async def _process_matcher_queue(self):
        # Check if we can accept a matcher job
        if not queue_service.can_accept_job("matcher"):
            return

        # Get next job from the matcher queue
        item = queue_service.get_next_for_backend("matcher")
        if not item:
            return

        # Process the matcher job
        success = await self._execute_matcher_job(item)
        if not success:
            queue_service.mark_failed(item.job_id, "Matcher execution failed")

    async def _execute_matcher_job(self, item: QueueItem) -> bool:
        # Extract job data
        job_data = {}
        if hasattr(item, 'task_type') and item.task_type == "matcher":
            # In our current implementation, we're storing job data differently
            # Let's extract from the item or fetch from database
            pass
        
        # For now, we'll get the job ID from the item and fetch details from DB
        job_id = item.job_id
        
        # Get database session
        async with AsyncSessionLocal() as db:
            # Get the matcher job details
            from sqlalchemy import select
            result = await db.execute(select(MatcherJob).where(MatcherJob.id == job_id))
            matcher_job = result.scalar_one_or_none()
            
            if not matcher_job:
                logger.error(f"Matcher job {job_id} not found")
                return False
                
            # Verify this is actually a matcher job (tenant safety)
            project_id = matcher_job.project_id
            organization_id = matcher_job.organization_id
            
            logger.info(f"Processing matcher job {job_id} for project {project_id}, organization {organization_id}")
            
            # Mark as running in queue service
            queue_service.mark_running(job_id)
            
            try:
                # Process the matcher job using our function
                await process_matcher_job(job_id, project_id, organization_id, db)
                return True
            except Exception as e:
                logger.error(f"Matcher job {job_id} failed: {e}")
                return False


matcher_worker_service = MatcherWorkerService()
