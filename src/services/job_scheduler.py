import asyncio
import logging
import os
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, Callable, Awaitable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .queue_service import queue_service, QueueStatus, QueueItem
from .instance_registry import registry
from .comfyui_client_factory import factory, ComfyUIClient
from .workflow_builder import builder as workflow_builder
from .job_tracking_service import job_tracking_service
from database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NON_REALISTIC_STORYBOARD_STYLES = {
    "hand_drawn_storyboard",
    "rough_pencil_storyboard",
    "ink_storyboard",
    "charcoal_storyboard",
    "graphic_novel_storyboard",
}


def _should_force_sketch(style_preset: Optional[str]) -> bool:
    normalized = (style_preset or "").strip().lower()
    return normalized in NON_REALISTIC_STORYBOARD_STYLES


def _extract_image_asset_path(asset: object) -> Optional[Path]:
    path_value = getattr(asset, "canonical_path", None)
    if isinstance(path_value, str) and path_value.strip():
        return Path(path_value)
    metadata_raw = getattr(asset, "metadata_json", None)
    metadata: dict = {}
    if isinstance(metadata_raw, str):
        try:
            parsed = json.loads(metadata_raw)
            if isinstance(parsed, dict):
                metadata = parsed
        except Exception:
            metadata = {}
    elif isinstance(metadata_raw, dict):
        metadata = metadata_raw
    storage_path = metadata.get("storage_path")
    if isinstance(storage_path, str) and storage_path.strip():
        return Path(storage_path)
    return None


def _apply_storyboard_sketch_postprocess(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    except Exception:
        logger.warning("Pillow unavailable; skipping sketch postprocess for %s", path)
        return False

    try:
        with Image.open(path) as img:
            gray = ImageOps.grayscale(img)
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edges = ImageOps.invert(edges)
            edges = ImageOps.autocontrast(edges)
            edges = ImageEnhance.Contrast(edges).enhance(2.2)
            base = ImageOps.autocontrast(gray).quantize(colors=6).convert("L")
            blended = Image.blend(base, edges, alpha=0.78)
            thresholded = blended.point(lambda p: 245 if p > 220 else p)
            final = ImageOps.autocontrast(thresholded)
            final.save(path)
        return True
    except Exception as exc:
        logger.warning("Sketch postprocess failed for %s: %s", path, exc)
        return False

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

        final_checkpoint = (
            runtime_prompt.get("1", {})
            .get("inputs", {})
            .get("ckpt_name")
            if isinstance(runtime_prompt, dict)
            else None
        )
        logger.info(
            "Storyboard runtime mapping job_id=%s workflow_key=%s style_preset=%s preset_key=%s checkpoint=%s",
            item.job_id,
            item.workflow_key,
            prompt_inputs.get("style_preset"),
            prompt_inputs.get("preset_key"),
            final_checkpoint,
        )
        logger.info(
            "Storyboard prompt payload job_id=%s positive=%s negative=%s",
            item.job_id,
            str(prompt_inputs.get("prompt") or "")[:240],
            str(prompt_inputs.get("negative_prompt") or "")[:240],
        )

        queue_service.mark_running(item.job_id)
        # Update progress: scheduled -> running (15%)
        async with AsyncSessionLocal() as _db:
            from models.core import ProjectJob as PJ
            _job = await _db.get(PJ, item.job_id)
            if _job:
                await job_tracking_service.update_progress(
                    _db, job=_job, percent=15, stage="Programado en scheduler", code="scheduled"
                )
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
                # Update progress: preparing workflow (30%)
                async with AsyncSessionLocal() as _db:
                    from models.core import ProjectJob as PJ
                    _job = await _db.get(PJ, item.job_id)
                    if _job:
                        await job_tracking_service.update_progress(
                            _db, job=_job, percent=30, stage="Preparando workflow", code="preparing_workflow"
                        )
                result = await client.post_prompt(runtime_prompt, item.workflow_key)
                item.prompt_id = result.get("prompt_id") if isinstance(result, dict) else None
                # Update progress: submitted to ComfyUI (45%)
                async with AsyncSessionLocal() as _db:
                    from models.core import ProjectJob as PJ
                    _job = await _db.get(PJ, item.job_id)
                    if _job:
                        await job_tracking_service.update_progress(
                            _db, job=_job, percent=45, stage="Enviando a ComfyUI", code="submitting_to_comfyui"
                        )
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

        # Update progress: ComfyUI accepted (60%)
        async with AsyncSessionLocal() as _db:
            from models.core import ProjectJob as PJ
            _job = await _db.get(PJ, item.job_id)
            if _job:
                await job_tracking_service.update_progress(
                    _db, job=_job, percent=60, stage="ComfyUI aceptó el prompt", code="comfyui_prompt_accepted"
                )

        while elapsed < max_wait:
            try:
                history = await client.get_history(prompt_id)
                if prompt_id in history:
                    # Update progress: persisting assets (90%)
                    async with AsyncSessionLocal() as _db:
                        from models.core import ProjectJob as PJ
                        _job = await _db.get(PJ, item.job_id)
                        if _job:
                            await job_tracking_service.update_progress(
                                _db, job=_job, percent=90, stage="Guardando assets generados", code="persisting_assets"
                            )
                    await self._persist_success_assets(
                        item=item,
                        client=client,
                        prompt_id=prompt_id,
                        history_entry=history[prompt_id],
                    )
                    # Update progress: completed (100%)
                    async with AsyncSessionLocal() as _db:
                        from models.core import ProjectJob as PJ
                        _job = await _db.get(PJ, item.job_id)
                        if _job:
                            await job_tracking_service.update_progress(
                                _db, job=_job, percent=100, stage="Render completado", code="completed"
                            )
                    queue_service.mark_succeeded(item.job_id)
                    logger.info(f"Job {item.job_id} succeeded")
                    return
                # Update progress: waiting for ComfyUI (75%)
                async with AsyncSessionLocal() as _db:
                    from models.core import ProjectJob as PJ
                    _job = await _db.get(PJ, item.job_id)
                    if _job:
                        await job_tracking_service.update_progress(
                            _db, job=_job, percent=75, stage="Esperando respuesta de ComfyUI", code="waiting_for_comfyui"
                        )
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
            except Exception as e:
                logger.warning(
                    "ComfyUI history polling failed for job_id=%s: %s; will retry until timeout",
                    item.job_id, e,
                )
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                continue

        # On timeout, leave progress where it was
        queue_service.mark_timeout(item.job_id)
        logger.warning(f"Job {item.job_id} timed out after {elapsed}s")

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
                source_metadata=item.metadata,
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
            style_preset = (item.prompt or {}).get("style_preset")
            if image_asset is not None and _should_force_sketch(style_preset):
                image_path = _extract_image_asset_path(image_asset)
                if image_path is not None:
                    applied = _apply_storyboard_sketch_postprocess(image_path)
                    logger.info(
                        "Storyboard sketch postprocess job_id=%s style_preset=%s applied=%s path=%s",
                        item.job_id,
                        style_preset,
                        applied,
                        str(image_path),
                    )
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
