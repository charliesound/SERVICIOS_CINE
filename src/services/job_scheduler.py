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
from .comfyui_node_capability_service import get_instance_capability_snapshot
from .comfyui_workflow_selector_service import build_metadata_workflow_profile, get_template_filename
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


def _merge_storyboard_runtime_metadata(
    metadata: dict,
    runtime_metadata: Optional[dict],
    *,
    render_status: str,
    error_message: Optional[str] = None,
) -> dict:
    merged = dict(metadata or {})
    for key in (
        "workflow_key",
        "workflow_template",
        "workflow_profile_requested",
        "workflow_profile_executed",
        "workflow_fallback_report",
        "fallback_applied",
        "fallback_reason",
        "missing_nodes",
        "checkpoint",
        "prompt",
        "negative_prompt",
        "width",
        "height",
        "steps",
        "cfg",
        "sampler_name",
        "scheduler",
        "seed",
        "model_family",
        "continuity_seed",
        "character_reference_images",
        "environment_reference_images",
        "style_reference_images",
        "visual_bible_reference_pack",
        "controlnet_hints",
        "reference_mode",
        "references_used",
        "controlnet_model",
        "controlnet_preprocessor",
        "controlnet_strength",
    ):
        if runtime_metadata and runtime_metadata.get(key) is not None:
            merged[key] = runtime_metadata.get(key)
    merged["render_status"] = render_status
    if error_message:
        merged["render_error"] = str(error_message)
    else:
        merged.pop("render_error", None)
    return merged


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
                updated_item = queue_service.get_status(item.job_id)
                if updated_item and updated_item.status == QueueStatus.FAILED:
                    await self._persist_failure(item, "render_failed", error or "Execution failed")

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

        capability_snapshot = get_instance_capability_snapshot(
            item.backend,
            client.base_url,
            fetch_live=item.backend == "still",
        )
        available_nodes = set(capability_snapshot.available_nodes) if capability_snapshot.available_nodes else None
        requested_profile = str(
            prompt_inputs.get("workflow_profile_requested")
            or (item.metadata or {}).get("workflow_profile_requested")
            or "storyboard_safe"
        )

        runtime_prompt, executed_workflow_key, fallback_report, executed_profile = (
            workflow_builder.build_runtime_prompt_with_profile(
                item.workflow_key,
                prompt_inputs,
                requested_profile=requested_profile,
                available_nodes=available_nodes,
                skip_node_validation=available_nodes is None,
            )
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

        item.workflow_key = executed_workflow_key or item.workflow_key
        item.metadata = {
            **(item.metadata or {}),
            **build_metadata_workflow_profile(
                requested_profile=requested_profile,
                executed_profile=executed_profile,
                fallback_report=fallback_report,
                available_node_count=capability_snapshot.total_nodes,
            ),
            "workflow_key": item.workflow_key,
            "object_info_snapshot_at": capability_snapshot.object_info_snapshot_at,
            "backend": capability_snapshot.backend,
            "backend_base_url": capability_snapshot.base_url,
            "workflow_template": (
                get_template_filename(executed_profile)
                if executed_profile not in {"hardcoded_safety_net", "none"}
                else "hardcoded_still_storyboard_frame"
            ),
        }
        item.metadata.update(workflow_builder.extract_runtime_prompt_metadata(runtime_prompt))
        references_used = {
            "pose_reference_image": bool(prompt_inputs.get("pose_reference_image")),
            "controlnet_hints": bool(prompt_inputs.get("controlnet_hints")),
        }
        if requested_profile == "production_storyboard_cinematic_controlnet" or executed_profile == "production_storyboard_cinematic_controlnet":
            item.metadata["reference_mode"] = "controlnet"
            item.metadata["references_used"] = references_used
            item.metadata["controlnet_model"] = prompt_inputs.get("controlnet_model")
            item.metadata["controlnet_preprocessor"] = prompt_inputs.get("controlnet_preprocessor")
            item.metadata["controlnet_strength"] = prompt_inputs.get("controlnet_strength")

        self._dump_runtime_prompt_if_needed(
            job_id=item.job_id,
            runtime_prompt=runtime_prompt,
            requested_profile=requested_profile,
            executed_profile=executed_profile,
        )

        final_checkpoint = (
            (item.metadata or {}).get("checkpoint")
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

    def _dump_runtime_prompt_if_needed(
        self,
        *,
        job_id: str,
        runtime_prompt: Dict[str, object],
        requested_profile: str,
        executed_profile: str,
    ) -> None:
        is_controlnet_profile = (
            requested_profile == "production_storyboard_cinematic_controlnet"
            or executed_profile == "production_storyboard_cinematic_controlnet"
        )
        if not is_controlnet_profile:
            return
        dump_path = Path(f"/tmp/cid_controlnet_runtime_prompt_{job_id}.json")
        try:
            dump_path.write_text(
                json.dumps(runtime_prompt, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            logger.info("Dumped controlnet runtime prompt for job_id=%s at %s", job_id, str(dump_path))
        except Exception as exc:
            logger.warning("Could not dump controlnet runtime prompt for job_id=%s: %s", job_id, exc)

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
        await self._persist_failure(item, "render_failed", "Job timed out")

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
                    meta = {}
                    if shot.metadata_json:
                        try:
                            meta = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
                        except Exception:
                            meta = {}
                    meta = _merge_storyboard_runtime_metadata(
                        meta,
                        item.metadata,
                        render_status="render_succeeded",
                    )
                    shot.metadata_json = json.dumps(meta, ensure_ascii=False, default=str)
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

    async def _persist_failure(
        self,
        item: QueueItem,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        from database import AsyncSessionLocal
        from models.storyboard import StoryboardShot

        storyboard_shot_id = (item.metadata or {}).get("storyboard_shot_id")
        if not storyboard_shot_id:
            return

        async with AsyncSessionLocal() as session:
            shot = await session.get(StoryboardShot, storyboard_shot_id)
            if shot is not None:
                meta = {}
                if shot.metadata_json:
                    try:
                        meta = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
                    except Exception:
                        meta = {}
                meta = _merge_storyboard_runtime_metadata(
                    meta,
                    item.metadata,
                    render_status=status,
                    error_message=error_message,
                )
                shot.metadata_json = json.dumps(meta, ensure_ascii=False, default=str)
                await session.commit()
                logger.info(
                    "Persisted render failure for shot_id=%s job_id=%s status=%s error=%s",
                    storyboard_shot_id,
                    item.job_id,
                    status,
                    error_message,
                )

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
                    await self._persist_failure(item, "render_failed", "Job timed out")

    async def get_status(self) -> Dict:
        return {
            "running": self._running,
            "poll_interval": self._poll_interval,
            "job_timeout": self._job_timeout,
            "queue_status": queue_service.get_all_status(),
        }


scheduler = JobScheduler()
