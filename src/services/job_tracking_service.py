from __future__ import annotations

import json
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Organization, Project, ProjectJob, User
from models.history import JobHistory
from models.storage import MediaAsset, MediaAssetStatus, MediaAssetType
from services.ingest_service import ingest_service


QUEUE_RUNTIME_ORGANIZATION_ID = "__queue_runtime__"
QUEUE_RUNTIME_PROJECT_ID = "__queue_runtime__"


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

    def _is_queue_runtime_context(self, organization_id: str, project_id: str) -> bool:
        return (
            organization_id == QUEUE_RUNTIME_ORGANIZATION_ID
            and project_id == QUEUE_RUNTIME_PROJECT_ID
        )

    async def _ensure_queue_runtime_context(self, db: AsyncSession) -> None:
        organization = await db.get(Organization, QUEUE_RUNTIME_ORGANIZATION_ID)
        if organization is None:
            organization = Organization(
                id=QUEUE_RUNTIME_ORGANIZATION_ID,
                name="Queue Runtime",
                billing_plan="system",
                is_active=True,
            )
            db.add(organization)

        project = await db.get(Project, QUEUE_RUNTIME_PROJECT_ID)
        if project is None:
            project = Project(
                id=QUEUE_RUNTIME_PROJECT_ID,
                organization_id=QUEUE_RUNTIME_ORGANIZATION_ID,
                name="Queue Runtime",
                description="Internal runtime project for durable queue tracking",
                status="system",
            )
            db.add(project)

        await db.flush()

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
        if self._is_queue_runtime_context(organization_id, project_id):
            await self._ensure_queue_runtime_context(db)

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
    ) -> MediaAsset:
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
                relative_path=content_ref,
                canonical_path=content_ref,
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
            )
            db.add(asset)
        else:
            asset.file_name = file_name
            asset.relative_path = content_ref
            asset.canonical_path = content_ref
            asset.content_ref = content_ref
            asset.metadata_json = self._encode_json(metadata_json)
            asset.status = status

        await db.flush()
        return asset

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

    async def persist_scheduler_success_assets(
        self,
        db: AsyncSession,
        *,
        job_id: str,
        prompt_id: str,
        backend_base_url: str,
        history_entry: Any,
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
                    content_ref = self._build_backend_content_ref(
                        backend_base_url=backend_base_url,
                        filename=normalized_filename,
                        subfolder=subfolder if isinstance(subfolder, str) else None,
                        output_type=output_type
                        if isinstance(output_type, str)
                        else None,
                    )

                    asset = await self.upsert_job_asset(
                        db,
                        organization_id=str(job.organization_id),
                        project_id=str(job.project_id),
                        job_id=str(job.id),
                        file_name=normalized_filename,
                        content_ref=content_ref,
                        asset_source=f"queue_{output_kind}_{node_id}_{index}",
                        metadata_json={
                            "prompt_id": prompt_id,
                            "node_id": str(node_id),
                            "output_kind": output_kind,
                            "backend_base_url": backend_base_url,
                            "output": entry,
                        },
                        created_by=job.created_by,
                        asset_type=asset_type,
                        status=MediaAssetStatus.INDEXED,
                        file_extension=extension,
                        mime_type=mime_type or "application/octet-stream",
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
