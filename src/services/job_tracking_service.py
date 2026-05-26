from __future__ import annotations

import json
import logging
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from models.core import ProjectJob, User
from models.history import JobHistory
from models.storage import MediaAsset, MediaAssetStatus, MediaAssetType
from services.ingest_service import ingest_service


logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[2]


class JobTrackingService:
    def _encode_json(self, payload: Optional[Any]) -> Optional[str]:
        if payload is None:
            return None
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, ensure_ascii=False, default=str)

    def _decode_json(self, payload: Optional[str]) -> Optional[Any]:
        if not payload:
            return None
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload

    async def record_job_event(
        self,
        db: AsyncSession,
        *,
        organization_id: str,
        project_id: str,
        job_id: str,
        event_type: str,
        status_from: Optional[str] = None,
        status_to: Optional[str] = None,
        message: Optional[str] = None,
        detail: Optional[str] = None,
        metadata_json: Optional[Any] = None,
        created_by: Optional[str] = None,
    ) -> JobHistory:
        if created_by is not None and await db.get(User, created_by) is None:
            created_by = None

        entry = JobHistory(
            organization_id=organization_id,
            project_id=project_id,
            job_id=job_id,
            event_type=event_type,
            status_from=status_from,
            status_to=status_to,
            message=message,
            detail=detail,
            metadata_json=self._encode_json(metadata_json),
            created_by=created_by,
        )
        db.add(entry)
        await db.flush()
        return entry

    async def record_project_job_event(
        self,
        db: AsyncSession,
        *,
        job: ProjectJob,
        event_type: str,
        status_from: Optional[str] = None,
        status_to: Optional[str] = None,
        message: Optional[str] = None,
        detail: Optional[str] = None,
        metadata_json: Optional[Any] = None,
    ) -> JobHistory:
        return await self.record_job_event(
            db,
            organization_id=str(job.organization_id),
            project_id=str(job.project_id),
            job_id=str(job.id),
            event_type=event_type,
            status_from=status_from,
            status_to=status_to,
            message=message,
            detail=detail,
            metadata_json=metadata_json,
            created_by=job.created_by,
        )

    async def update_progress(
        self,
        db: AsyncSession,
        *,
        job: ProjectJob,
        percent: int,
        stage: str,
        code: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        job.progress_percent = max(0, min(100, percent))
        job.progress_stage = stage
        job.progress_code = code

        existing = self._decode_json(job.result_data) or {}
        if isinstance(existing, dict):
            existing["progress"] = {
                "percent": job.progress_percent,
                "stage": stage,
                "code": code,
                "updated_at": datetime.utcnow().isoformat(),
            }
            if metadata:
                existing.setdefault("progress_history", []).append({
                    "percent": job.progress_percent,
                    "stage": stage,
                    "code": code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": metadata,
                })
            job.result_data = self._encode_json(existing)

        await self.record_project_job_event(
            db,
            job=job,
            event_type="progress_update",
            status_from=job.status,
            status_to=job.status,
            message=f"[{percent}%] {stage}",
            metadata_json={
                "progress_percent": job.progress_percent,
                "progress_stage": stage,
                "progress_code": code,
                **(metadata or {}),
            },
        )
        await db.flush()

    async def upsert_job_asset(
        self,
        db: AsyncSession,
        *,
        organization_id: str,
        project_id: str,
        job_id: str,
        file_name: str,
        content_ref: str,
        asset_source: str,
        metadata_json: dict[str, Any],
        created_by: Optional[str],
        asset_type: str = MediaAssetType.DOCUMENT,
        status: str = MediaAssetStatus.INDEXED,
        file_extension: str = "json",
        mime_type: str = "application/json",
        relative_path: Optional[str] = None,
        canonical_path: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> MediaAsset:
        stored_relative_path = relative_path or content_ref
        stored_canonical_path = canonical_path or content_ref
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.organization_id == organization_id,
                MediaAsset.project_id == project_id,
                MediaAsset.job_id == job_id,
                MediaAsset.asset_source == asset_source,
            )
        )
        asset = result.scalar_one_or_none()

        if asset is None:
            asset = MediaAsset(
                organization_id=organization_id,
                project_id=project_id,
                storage_source_id=None,
                file_name=file_name,
                relative_path=stored_relative_path,
                canonical_path=stored_canonical_path,
                content_ref=content_ref,
                file_extension=file_extension,
                mime_type=mime_type,
                asset_type=asset_type,
                metadata_json=self._encode_json(metadata_json),
                asset_source=asset_source,
                job_id=str(job_id),
                status=status,
                created_by=created_by,
                created_at=datetime.utcnow(),
                file_size=max(0, int(file_size or 0)),
            )
            db.add(asset)
        else:
            asset.file_name = file_name
            asset.relative_path = stored_relative_path
            asset.canonical_path = stored_canonical_path
            asset.content_ref = content_ref
            asset.metadata_json = self._encode_json(metadata_json)
            asset.status = status
            asset.file_size = max(0, int(file_size or 0))

        await db.flush()
        return asset

    def _storage_output_root(self) -> Path:
        output_root = Path(get_settings().storage_output_dir)
        if not output_root.is_absolute():
            output_root = (REPO_ROOT / output_root).resolve()
        return output_root

    def _safe_path_component(self, value: str, fallback: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", (value or "").strip())
        normalized = normalized.strip("._")
        return normalized[:120] or fallback

    def _build_local_asset_paths(
        self,
        *,
        job: ProjectJob,
        file_name: str,
        node_id: str,
        index: int,
    ) -> tuple[Path, str]:
        output_root = self._storage_output_root()
        relative_dir = Path("renders") / str(job.organization_id) / str(job.project_id) / str(job.id)
        safe_stem = self._safe_path_component(Path(file_name).stem, "asset")
        safe_suffix = Path(file_name).suffix.lower() or ".bin"
        safe_node = self._safe_path_component(node_id, "node")
        stored_name = f"{safe_node}_{index:02d}_{safe_stem}{safe_suffix}"
        relative_path = relative_dir / stored_name
        return output_root / relative_path, relative_path.as_posix()

    async def _download_backend_asset(
        self,
        *,
        backend_base_url: str,
        filename: str,
        subfolder: Optional[str],
        output_type: Optional[str],
    ) -> tuple[bytes, str]:
        content_ref = self._build_backend_content_ref(
            backend_base_url=backend_base_url,
            filename=filename,
            subfolder=subfolder,
            output_type=output_type,
        )
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(content_ref)
            response.raise_for_status()
            return response.content, content_ref

    def _create_thumbnail_webp(
        self,
        *,
        file_path: Path,
        relative_path: str,
        mime_type: Optional[str],
    ) -> Optional[dict[str, str]]:
        if not (mime_type or "").startswith("image/"):
            return None

        try:
            from PIL import Image as PILImage
        except Exception:
            return None

        thumb_path = file_path.with_name(f"{file_path.stem}_thumb.webp")
        thumb_relative = str(Path(relative_path).with_name(thumb_path.name).as_posix())

        try:
            with PILImage.open(file_path) as img:
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                width = min(256, img.width)
                if width <= 0:
                    return None
                ratio = width / img.width
                height = max(1, int(img.height * ratio))
                img.resize((width, height), PILImage.LANCZOS).save(
                    thumb_path,
                    format="WEBP",
                    quality=80,
                    method=6,
                )
        except Exception as exc:
            logger.warning("Thumbnail generation failed for %s: %s", file_path, exc)
            return None

        return {
            "thumbnail_path": str(thumb_path),
            "thumbnail_relative_path": thumb_relative,
            "thumbnail_content_ref": f"file://{thumb_path}",
        }

    async def list_job_history(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> list[JobHistory]:
        query = select(JobHistory).where(JobHistory.job_id == job_id)
        if organization_id is not None:
            query = query.where(JobHistory.organization_id == organization_id)
        if project_id is not None:
            query = query.where(JobHistory.project_id == project_id)
        result = await db.execute(
            query.order_by(JobHistory.created_at.asc(), JobHistory.id.asc())
        )
        return list(result.scalars().all())

    async def list_job_assets(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> list[MediaAsset]:
        query = select(MediaAsset).where(MediaAsset.job_id == job_id)
        if organization_id is not None:
            query = query.where(MediaAsset.organization_id == organization_id)
        if project_id is not None:
            query = query.where(MediaAsset.project_id == project_id)
        result = await db.execute(
            query.order_by(MediaAsset.created_at.desc(), MediaAsset.id.desc())
        )
        return list(result.scalars().all())

    def serialize_history_entry(self, entry: JobHistory) -> dict[str, Any]:
        return {
            "id": str(entry.id),
            "event_type": str(entry.event_type),
            "status_from": entry.status_from,
            "status_to": entry.status_to,
            "message": entry.message,
            "detail": entry.detail,
            "metadata_json": self._decode_json(entry.metadata_json),
            "created_by": entry.created_by,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    def serialize_asset(self, asset: MediaAsset) -> dict[str, Any]:
        return {
            "id": str(asset.id),
            "job_id": asset.job_id,
            "file_name": str(asset.file_name),
            "file_extension": str(asset.file_extension),
            "asset_type": str(asset.asset_type),
            "asset_source": asset.asset_source,
            "content_ref": asset.content_ref,
            "mime_type": asset.mime_type,
            "status": str(asset.status),
            "metadata_json": self._decode_json(asset.metadata_json),
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
        }

    async def build_job_tracking_payload(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> dict[str, list[dict[str, Any]]]:
        history = await self.list_job_history(
            db,
            job_id=job_id,
            organization_id=organization_id,
            project_id=project_id,
        )
        assets = await self.list_job_assets(
            db,
            job_id=job_id,
            organization_id=organization_id,
            project_id=project_id,
        )
        return {
            "history": [self.serialize_history_entry(entry) for entry in history],
            "assets": [self.serialize_asset(asset) for asset in assets],
        }

    def _fallback_mime_type(self, output_kind: str) -> Optional[str]:
        if output_kind == "images":
            return "image/png"
        if output_kind == "audio":
            return "audio/wav"
        if output_kind == "videos":
            return "video/mp4"
        return None

    def _build_backend_content_ref(
        self,
        *,
        backend_base_url: str,
        filename: str,
        subfolder: Optional[str],
        output_type: Optional[str],
    ) -> str:
        query = {"filename": filename}
        if subfolder:
            query["subfolder"] = subfolder
        if output_type:
            query["type"] = output_type
        return f"{backend_base_url.rstrip('/')}/view?{urlencode(query)}"

    @staticmethod
    def _extract_visual_bible_metadata(source_metadata: Any) -> dict[str, Any]:
        if not source_metadata:
            return {}
        if isinstance(source_metadata, str):
            try:
                source_metadata = json.loads(source_metadata)
            except (json.JSONDecodeError, TypeError):
                return {}
        if not isinstance(source_metadata, dict):
            return {}
        vb_enabled = source_metadata.get("visual_bible_enabled")
        vb_applied = source_metadata.get("visual_bible_applied")
        vb_id = source_metadata.get("visual_bible_id")
        vb_preset = source_metadata.get("visual_bible_preset")
        if vb_enabled is None and vb_applied is None and vb_id is None and vb_preset is None:
            return {}
        return {
            "visual_bible": {
                "enabled": bool(vb_enabled) if vb_enabled is not None else False,
                "applied": bool(vb_applied) if vb_applied is not None else False,
                "visual_bible_id": vb_id,
                "visual_bible_preset": vb_preset,
                "source": "render_job_metadata",
            }
        }

    @staticmethod
    def _extract_workflow_profile_metadata(source_metadata: Any) -> dict[str, Any]:
        if not source_metadata or not isinstance(source_metadata, dict):
            return {}
        requested = source_metadata.get("workflow_profile_requested")
        executed = source_metadata.get("workflow_profile_executed")
        fallback_str = source_metadata.get("workflow_fallback_report")
        available_node_count = source_metadata.get("available_node_count")
        missing_nodes = source_metadata.get("missing_nodes")
        workflow_key = source_metadata.get("workflow_key")
        storyboard_style_preset = source_metadata.get("storyboard_style_preset")
        if requested is None and executed is None:
            return {}
        meta: dict[str, Any] = {}
        if requested is not None or executed is not None:
            meta["workflow_profile"] = {
                "requested": str(requested) if requested is not None else "",
                "executed": str(executed) if executed is not None else "",
            }
            if storyboard_style_preset is not None:
                meta["workflow_profile"]["style_preset"] = str(storyboard_style_preset)
        if available_node_count is not None:
            meta["available_node_count"] = int(available_node_count)
        if isinstance(missing_nodes, list):
            meta["missing_nodes"] = [str(node) for node in missing_nodes]
        if workflow_key is not None:
            meta["workflow_key"] = str(workflow_key)
        if fallback_str is not None:
            if isinstance(fallback_str, str):
                try:
                    fallback_str = json.loads(fallback_str)
                except (json.JSONDecodeError, TypeError):
                    pass
            if isinstance(fallback_str, dict):
                meta["workflow_fallback_report"] = fallback_str
        return meta

    @staticmethod
    def _extract_render_prompt_metadata(source_metadata: Any) -> dict[str, Any]:
        if not source_metadata or not isinstance(source_metadata, dict):
            return {}
        keys = (
            "prompt",
            "negative_prompt",
            "checkpoint",
            "width",
            "height",
            "steps",
            "cfg",
            "sampler_name",
            "scheduler",
            "seed",
            "model_family",
            "style_preset",
            "storyboard_style_preset",
            "scene_heading",
            "source_scene_heading",
            "source_action_summary",
            "source_dialogue_summary",
            "shot_objective",
            "atmosphere",
            "location",
            "time_of_day",
            "int_ext",
        )
        meta: dict[str, Any] = {}
        for key in keys:
            if source_metadata.get(key) is not None:
                meta[key] = source_metadata.get(key)
        return meta

    async def persist_scheduler_success_assets(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        prompt_id: str,
        backend_base_url: str,
        history_entry: Any,
        source_metadata: Optional[dict] = None,
    ) -> list[MediaAsset]:
        if not isinstance(history_entry, dict):
            return []

        job = await db.get(ProjectJob, job_id)
        if job is None:
            return []

        outputs = history_entry.get("outputs")
        if not isinstance(outputs, dict):
            return []

        created_assets: list[MediaAsset] = []

        for node_id, node_output in outputs.items():
            if not isinstance(node_output, dict):
                continue

            for output_kind in ("images", "audio", "videos", "files"):
                entries = node_output.get(output_kind)
                if not isinstance(entries, list):
                    continue

                for index, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        continue

                    filename = entry.get("filename")
                    if not isinstance(filename, str) or not filename.strip():
                        continue

                    normalized_filename = filename.strip()
                    subfolder = entry.get("subfolder")
                    output_type = entry.get("type")
                    mime_type, _encoding = mimetypes.guess_type(normalized_filename)
                    mime_type = mime_type or self._fallback_mime_type(output_kind)
                    asset_type = ingest_service.infer_asset_type(
                        normalized_filename,
                        mime_type,
                    )

                    if asset_type == MediaAssetType.OTHER and mime_type is None:
                        continue

                    extension = (
                        Path(normalized_filename).suffix.lower().lstrip(".") or "bin"
                    )
                    file_bytes, backend_content_ref = await self._download_backend_asset(
                        backend_base_url=backend_base_url,
                        filename=normalized_filename,
                        subfolder=subfolder if isinstance(subfolder, str) else None,
                        output_type=output_type if isinstance(output_type, str) else None,
                    )
                    stored_path, relative_path = self._build_local_asset_paths(
                        job=job,
                        file_name=normalized_filename,
                        node_id=str(node_id),
                        index=index,
                    )
                    stored_path.parent.mkdir(parents=True, exist_ok=True)
                    stored_path.write_bytes(file_bytes)
                    thumbnail_metadata = self._create_thumbnail_webp(
                        file_path=stored_path,
                        relative_path=relative_path,
                        mime_type=mime_type,
                    ) or {}
                    content_ref = f"file://{stored_path}"

                    metadata_json: dict[str, Any] = {
                        "prompt_id": prompt_id,
                        "node_id": str(node_id),
                        "output_kind": output_kind,
                        "backend_base_url": backend_base_url,
                        "backend_content_ref": backend_content_ref,
                        "storage_path": str(stored_path),
                        "canonical_path": str(stored_path),
                        "relative_path": relative_path,
                        "output": entry,
                        **thumbnail_metadata,
                    }
                    vb_meta = self._extract_visual_bible_metadata(source_metadata)
                    if vb_meta:
                        metadata_json.update(vb_meta)
                    wp_meta = self._extract_workflow_profile_metadata(source_metadata)
                    if wp_meta:
                        metadata_json.update(wp_meta)
                    render_meta = self._extract_render_prompt_metadata(source_metadata)
                    if render_meta:
                        metadata_json.update(render_meta)

                    asset = await self.upsert_job_asset(
                        db,
                        organization_id=str(job.organization_id),
                        project_id=str(job.project_id),
                        job_id=str(job.id),
                        file_name=normalized_filename,
                        content_ref=content_ref,
                        asset_source=f"queue_{output_kind}_{node_id}_{index}",
                        metadata_json=metadata_json,
                        created_by=job.created_by,
                        asset_type=asset_type,
                        status=MediaAssetStatus.INDEXED,
                        file_extension=extension,
                        mime_type=mime_type or "application/octet-stream",
                        relative_path=relative_path,
                        canonical_path=str(stored_path),
                        file_size=len(file_bytes),
                    )
                    created_assets.append(asset)

        return created_assets

    async def record_queue_transition(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        organization_id: str,
        project_id: str,
        created_by: Optional[str],
        current_status: str,
        previous_status: Optional[str],
        event: str,
        task_type: str,
        backend: str,
        workflow_key: Optional[str],
        prompt_keys: Optional[list[str]],
        priority: int,
        user_plan: str,
        retry_count: int,
        error: Optional[str] = None,
        payload_metadata: Optional[dict[str, Any]] = None,
        recovery_reason: Optional[str] = None,
        created_record: bool = False,
    ) -> None:
        metadata = {
            "task_type": task_type,
            "backend": backend,
            "priority": priority,
            "user_plan": user_plan,
            "retry_count": retry_count,
        }
        if workflow_key:
            metadata["workflow_key"] = workflow_key
        if prompt_keys:
            metadata["prompt_keys"] = prompt_keys
        if payload_metadata:
            metadata["payload_metadata"] = payload_metadata
        if error:
            metadata["error"] = error
        if recovery_reason:
            metadata["recovery_reason"] = recovery_reason

        if created_record:
            await self.record_job_event(
                db,
                organization_id=organization_id,
                project_id=project_id,
                job_id=job_id,
                event_type="job_created",
                status_from=None,
                status_to=current_status,
                message="Queue job record created",
                metadata_json=metadata,
                created_by=created_by,
            )

        event_map = {
            "enqueue": ("job_queued", "Job queued for backend dispatch", None),
            "scheduled": ("job_scheduled", "Job scheduled on backend", None),
            "running": ("job_running", "Job started on backend", None),
            "succeeded": (
                "job_succeeded",
                "Job completed successfully",
                None,
            ),
            "failed": ("job_failed", "Job failed", error),
            "timeout": ("job_failed", "Job timed out", error or "timeout"),
            "canceled": ("job_cancelled", "Job cancelled", error),
            "manual_retry": (
                "job_retry_requested",
                "Manual retry requested",
                error,
            ),
            "retry_queued": (
                "job_retry_requested",
                "Automatic retry queued",
                error,
            ),
            "rejected": ("job_failed", "Job rejected", error),
            "startup_requeue": (
                "job_queued",
                "Job requeued during startup recovery",
                error,
            ),
            "startup_failed": (
                "job_failed",
                "Job failed during startup recovery",
                error,
            ),
        }
        mapped = event_map.get(event)
        if mapped:
            event_type, message, detail = mapped
            await self.record_job_event(
                db,
                organization_id=organization_id,
                project_id=project_id,
                job_id=job_id,
                event_type=event_type,
                status_from=previous_status,
                status_to=current_status,
                message=message,
                detail=detail,
                metadata_json=metadata,
                created_by=created_by,
            )

        if event in {"startup_requeue", "startup_failed"} or recovery_reason:
            await self.record_job_event(
                db,
                organization_id=organization_id,
                project_id=project_id,
                job_id=job_id,
                event_type="recovery_applied",
                status_from=previous_status,
                status_to=current_status,
                message="Startup recovery applied",
                detail=error,
                metadata_json=metadata,
                created_by=created_by,
            )


job_tracking_service = JobTrackingService()
