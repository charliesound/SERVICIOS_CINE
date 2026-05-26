from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import ProjectJob
from models.storage import MediaAsset
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from schemas.storyboard_trace_schema import (
    AssetTrace,
    ModelTrace,
    PromptTrace,
    StoryboardTraceRecord,
    StoryboardTraceSummary,
    VersionHistoryItem,
    VersionTrace,
    WorkflowTrace,
)
from services.storyboard_service import storyboard_service


_WINDOWS_DRIVE_RE = re.compile(r"(^|\s)[A-Za-z]:[\\/]")
_UNSAFE_PATH_RE = re.compile(r"(^|\s)(/opt/|/mnt/|/home/|/var/|/tmp/|\\\\)")


class StoryboardTraceService:
    async def get_shot_trace(
        self,
        db: AsyncSession,
        project_id: str,
        shot_id: str,
        tenant: TenantContext,
    ) -> StoryboardTraceRecord:
        project = await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        shot = await self._get_shot(db, project_id, shot_id, tenant.organization_id)
        asset = await self._get_asset_for_shot(db, project_id, shot, tenant.organization_id)
        job = await self._get_best_job(db, project_id, tenant.organization_id, shot, asset)
        versions = await self._get_version_siblings(db, project_id, tenant.organization_id, shot)
        return self._build_record(
            project_id=project_id,
            organization_id=str(project.organization_id),
            shot=shot,
            asset=asset,
            job=job,
            versions=versions,
        )

    async def get_project_trace_summary(
        self,
        db: AsyncSession,
        project_id: str,
        tenant: TenantContext,
    ) -> StoryboardTraceSummary:
        project = await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == tenant.organization_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        shots = list(result.scalars().all())
        asset_ids = [str(shot.asset_id) for shot in shots if getattr(shot, "asset_id", None)]
        assets_by_id: dict[str, MediaAsset] = {}
        if asset_ids:
            asset_result = await db.execute(
                select(MediaAsset).where(
                    MediaAsset.id.in_(asset_ids),
                    MediaAsset.project_id == project_id,
                    MediaAsset.organization_id == tenant.organization_id,
                )
            )
            assets_by_id = {str(asset.id): asset for asset in asset_result.scalars().all()}

        records = [
            self._build_record(
                project_id=project_id,
                organization_id=str(project.organization_id),
                shot=shot,
                asset=assets_by_id.get(str(getattr(shot, "asset_id", ""))),
                job=None,
                versions=[],
            )
            for shot in shots
        ]
        missing_field_counts: dict[str, int] = {}
        for record in records:
            for field in record.missing_fields:
                missing_field_counts[field] = missing_field_counts.get(field, 0) + 1

        return StoryboardTraceSummary(
            project_id=project_id,
            organization_id=str(project.organization_id),
            total_shots=len(shots),
            traced_shots=sum(1 for record in records if record.available_fields),
            shots_with_prompt=sum(1 for record in records if "prompt" in record.available_fields),
            shots_with_workflow=sum(1 for record in records if "workflow" in record.available_fields),
            shots_with_model=sum(1 for record in records if "model" in record.available_fields),
            shots_with_asset=sum(1 for record in records if "asset" in record.available_fields),
            shots_with_render_job=sum(1 for record in records if record.render_job_id),
            shots_with_previous_versions=sum(1 for record in records if record.version_trace.has_previous_versions),
            workflow_fallback_count=sum(1 for record in records if record.workflow_trace.fallback_applied),
            workflow_keys=self._dedupe(record.workflow_trace.workflow_key for record in records),
            workflow_profiles=self._dedupe(
                record.workflow_trace.workflow_profile_executed or record.workflow_trace.workflow_profile
                for record in records
            ),
            model_families=self._dedupe(record.model_trace.model_family for record in records),
            checkpoints=self._dedupe(record.model_trace.checkpoint for record in records),
            missing_field_counts=missing_field_counts,
        )

    async def get_asset_trace(
        self,
        db: AsyncSession,
        project_id: str,
        asset_id: str,
        tenant: TenantContext,
    ) -> StoryboardTraceRecord:
        project = await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        asset = await self._get_asset(db, project_id, asset_id, tenant.organization_id)
        shot = await self._get_shot_for_asset(db, project_id, asset, tenant.organization_id)
        job = await self._get_best_job(db, project_id, tenant.organization_id, shot, asset)
        versions = await self._get_version_siblings(db, project_id, tenant.organization_id, shot)
        return self._build_record(
            project_id=project_id,
            organization_id=str(project.organization_id),
            shot=shot,
            asset=asset,
            job=job,
            versions=versions,
        )

    async def _get_shot(
        self,
        db: AsyncSession,
        project_id: str,
        shot_id: str,
        organization_id: str,
    ) -> StoryboardShot:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.id == shot_id,
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
            )
        )
        shot = result.scalar_one_or_none()
        if shot is None:
            raise HTTPException(status_code=404, detail="Storyboard shot trace not found")
        return shot

    async def _get_asset(
        self,
        db: AsyncSession,
        project_id: str,
        asset_id: str,
        organization_id: str,
    ) -> MediaAsset:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.project_id == project_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        asset = result.scalar_one_or_none()
        if asset is None:
            raise HTTPException(status_code=404, detail="Storyboard asset trace not found")
        return asset

    async def _get_asset_for_shot(
        self,
        db: AsyncSession,
        project_id: str,
        shot: StoryboardShot,
        organization_id: str,
    ) -> MediaAsset | None:
        if not getattr(shot, "asset_id", None):
            return None
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == shot.asset_id,
                MediaAsset.project_id == project_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_shot_for_asset(
        self,
        db: AsyncSession,
        project_id: str,
        asset: MediaAsset,
        organization_id: str,
    ) -> StoryboardShot:
        asset_meta = self._decode_json(getattr(asset, "metadata_json", None))
        linked_shot_id = asset_meta.get("storyboard_shot_id") or asset_meta.get("source_shot_id")
        query = select(StoryboardShot).where(
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == organization_id,
        )
        if linked_shot_id:
            query = query.where(StoryboardShot.id == str(linked_shot_id))
        else:
            query = query.where(StoryboardShot.asset_id == str(asset.id))
        result = await db.execute(query)
        shot = result.scalar_one_or_none()
        if shot is None:
            raise HTTPException(status_code=404, detail="No storyboard shot linked to asset")
        return shot

    async def _get_best_job(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        shot: StoryboardShot,
        asset: MediaAsset | None,
    ) -> ProjectJob | None:
        shot_meta = self._decode_json(getattr(shot, "metadata_json", None))
        job_id = (
            shot_meta.get("render_job_id")
            or getattr(shot, "generation_job_id", None)
            or (getattr(asset, "job_id", None) if asset is not None else None)
        )
        if not job_id:
            return None
        result = await db.execute(
            select(ProjectJob).where(
                ProjectJob.id == str(job_id),
                ProjectJob.project_id == project_id,
                ProjectJob.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_version_siblings(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        shot: StoryboardShot,
    ) -> list[StoryboardShot]:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
                StoryboardShot.sequence_id == getattr(shot, "sequence_id", None),
                StoryboardShot.sequence_order == getattr(shot, "sequence_order", None),
                StoryboardShot.scene_number == getattr(shot, "scene_number", None),
            )
        )
        versions = list(result.scalars().all())
        return sorted(versions, key=lambda item: int(getattr(item, "version", 1) or 1))

    def _build_record(
        self,
        *,
        project_id: str,
        organization_id: str,
        shot: StoryboardShot,
        asset: MediaAsset | None,
        job: ProjectJob | None,
        versions: list[StoryboardShot],
    ) -> StoryboardTraceRecord:
        shot_meta = self._decode_json(getattr(shot, "metadata_json", None))
        asset_meta = self._decode_json(getattr(asset, "metadata_json", None)) if asset is not None else {}
        job_meta = self._decode_json(getattr(job, "result_data", None)) if job is not None else {}

        prompt_trace = self._build_prompt_trace(shot, shot_meta, asset_meta, job_meta)
        workflow_trace = self._build_workflow_trace(shot_meta, asset_meta, job_meta)
        model_trace = self._build_model_trace(shot_meta, asset_meta, job_meta)
        asset_trace = self._build_asset_trace(project_id, shot, asset, shot_meta, asset_meta)
        version_trace = self._build_version_trace(shot, versions)
        render_job_id = self._safe_text(shot_meta.get("render_job_id") or getattr(job, "id", None))

        available_fields = []
        if prompt_trace.positive_prompt_enriched or prompt_trace.original_narrative:
            available_fields.append("prompt")
        if workflow_trace.workflow_key or workflow_trace.workflow_profile or workflow_trace.workflow_profile_executed:
            available_fields.append("workflow")
        if model_trace.model_family or model_trace.checkpoint:
            available_fields.append("model")
        if asset_trace.media_asset_id:
            available_fields.append("asset")
        if render_job_id:
            available_fields.append("render_job")
        available_fields.append("version")

        expected_fields = ["prompt", "workflow", "model", "render_job", "asset", "version"]
        missing_fields = [field for field in expected_fields if field not in available_fields]

        return StoryboardTraceRecord(
            project_id=project_id,
            organization_id=organization_id,
            shot_id=str(getattr(shot, "id", "")),
            sequence_id=self._safe_text(getattr(shot, "sequence_id", None)),
            sequence_order=int(getattr(shot, "sequence_order", 0) or 0),
            scene_number=getattr(shot, "scene_number", None),
            shot_type=self._safe_text(getattr(shot, "shot_type", None)),
            visual_mode=self._safe_text(getattr(shot, "visual_mode", None)),
            generation_mode=self._safe_text(getattr(shot, "generation_mode", None)),
            generation_job_id=self._safe_text(getattr(shot, "generation_job_id", None)),
            render_job_id=render_job_id,
            created_at=getattr(shot, "created_at", None),
            updated_at=getattr(shot, "updated_at", None),
            prompt_trace=prompt_trace,
            workflow_trace=workflow_trace,
            model_trace=model_trace,
            asset_trace=asset_trace,
            version_trace=version_trace,
            available_fields=available_fields,
            missing_fields=missing_fields,
        )

    def _build_prompt_trace(
        self,
        shot: StoryboardShot,
        shot_meta: dict[str, Any],
        asset_meta: dict[str, Any],
        job_meta: dict[str, Any],
    ) -> PromptTrace:
        prompt_spec = self._first_dict(
            shot_meta.get("revised_prompt_spec"),
            shot_meta.get("prompt_spec"),
            asset_meta.get("prompt_spec"),
            job_meta.get("prompt_spec"),
        )
        return PromptTrace(
            original_narrative=self._safe_text(getattr(shot, "narrative_text", None)),
            positive_prompt_enriched=self._safe_text(
                prompt_spec.get("positive_prompt")
                or shot_meta.get("positive_prompt")
                or shot_meta.get("prompt_safe_description_en")
                or asset_meta.get("positive_prompt")
                or job_meta.get("prompt")
            ),
            negative_prompt_enriched=self._safe_text(
                prompt_spec.get("negative_prompt")
                or shot_meta.get("negative_prompt")
                or asset_meta.get("negative_prompt")
            ),
            prompt_summary=self._safe_text(shot_meta.get("prompt_summary") or asset_meta.get("prompt_summary")),
            display_description_es=self._safe_text(shot_meta.get("display_description_es")),
        )

    def _build_workflow_trace(
        self,
        shot_meta: dict[str, Any],
        asset_meta: dict[str, Any],
        job_meta: dict[str, Any],
    ) -> WorkflowTrace:
        workflow_profile = self._first_dict(
            asset_meta.get("workflow_profile"),
            shot_meta.get("workflow_profile"),
            job_meta.get("workflow_profile"),
        )
        fallback = self._first_dict(
            asset_meta.get("workflow_fallback_report"),
            shot_meta.get("workflow_fallback_report"),
            job_meta.get("workflow_fallback_report"),
        )
        requested = workflow_profile.get("requested") or shot_meta.get("workflow_profile_requested")
        executed = workflow_profile.get("executed") or shot_meta.get("workflow_profile_executed")
        fallback_applied = bool(fallback.get("fallback_applied", False))
        return WorkflowTrace(
            workflow_key=self._safe_text(asset_meta.get("workflow_key") or shot_meta.get("workflow_key") or job_meta.get("workflow_key")),
            workflow_profile=self._safe_text(executed or requested),
            workflow_profile_requested=self._safe_text(requested),
            workflow_profile_executed=self._safe_text(executed),
            fallback_applied=fallback_applied,
            fallback_reason=self._safe_text(fallback.get("reason")),
            missing_nodes=self._safe_text_list(fallback.get("missing_nodes") or asset_meta.get("missing_nodes")),
            missing_models=self._safe_text_list(fallback.get("missing_models") or asset_meta.get("missing_models")),
        )

    def _build_model_trace(
        self,
        shot_meta: dict[str, Any],
        asset_meta: dict[str, Any],
        job_meta: dict[str, Any],
    ) -> ModelTrace:
        prompt_spec = self._first_dict(shot_meta.get("prompt_spec"), asset_meta.get("prompt_spec"), job_meta.get("prompt_spec"))
        return ModelTrace(
            model_family=self._safe_text(shot_meta.get("model_family") or asset_meta.get("model_family") or job_meta.get("model_family")),
            checkpoint=self._safe_text(prompt_spec.get("checkpoint") or shot_meta.get("checkpoint") or asset_meta.get("checkpoint") or job_meta.get("checkpoint")),
            loras=self._safe_dict_list(prompt_spec.get("loras") or shot_meta.get("loras") or asset_meta.get("loras")),
            sampler=self._safe_text(prompt_spec.get("sampler_name") or prompt_spec.get("sampler") or asset_meta.get("sampler_name") or shot_meta.get("sampler_name")),
            scheduler=self._safe_text(prompt_spec.get("scheduler") or asset_meta.get("scheduler") or shot_meta.get("scheduler")),
            steps=self._safe_int(prompt_spec.get("steps") or asset_meta.get("steps") or shot_meta.get("steps")),
            cfg=self._safe_float(prompt_spec.get("cfg") or prompt_spec.get("cfg_scale") or asset_meta.get("cfg") or shot_meta.get("cfg")),
            seed=self._safe_int(prompt_spec.get("seed") or asset_meta.get("seed") or shot_meta.get("seed")),
        )

    def _build_asset_trace(
        self,
        project_id: str,
        shot: StoryboardShot,
        asset: MediaAsset | None,
        shot_meta: dict[str, Any],
        asset_meta: dict[str, Any],
    ) -> AssetTrace:
        association_meta = self._first_dict(shot_meta.get("asset_association"), asset_meta.get("asset_association"))
        media_asset_id = self._safe_text(getattr(asset, "id", None) if asset is not None else getattr(shot, "asset_id", None))
        return AssetTrace(
            media_asset_id=media_asset_id,
            file_name=self._safe_text(getattr(asset, "file_name", None) if asset is not None else None),
            file_size=self._safe_int(getattr(asset, "file_size", None) if asset is not None else None),
            mime_type=self._safe_text(getattr(asset, "mime_type", None) if asset is not None else None),
            thumbnail_url=f"/api/projects/{project_id}/storyboard/shots/{shot.id}/thumbnail" if media_asset_id else None,
            image_url=f"/api/projects/{project_id}/storyboard/shots/{shot.id}/image" if media_asset_id else None,
            association_method=self._safe_text(association_meta.get("association_method")),
            association_confidence=self._safe_float(association_meta.get("association_confidence")),
            association_reason=self._safe_text(association_meta.get("association_reason")),
            repaired_at=self._safe_datetime(association_meta.get("repaired_at")),
        )

    def _build_version_trace(self, shot: StoryboardShot, versions: list[StoryboardShot]) -> VersionTrace:
        current_version = int(getattr(shot, "version", 1) or 1)
        previous = [item for item in versions if str(getattr(item, "id", "")) != str(getattr(shot, "id", ""))]
        previous_items = [
            VersionHistoryItem(
                version=int(getattr(item, "version", 1) or 1),
                shot_id=str(getattr(item, "id", "")),
                created_at=getattr(item, "created_at", None),
                prompt=self._safe_text(getattr(item, "narrative_text", None)),
                is_active=bool(getattr(item, "is_active", False)),
            )
            for item in previous
        ]
        total_versions = max(len(versions), current_version, 1)
        return VersionTrace(
            current_version=current_version,
            total_versions=total_versions,
            has_previous_versions=bool(previous_items) or current_version > 1,
            previous_versions=previous_items,
        )

    def _decode_json(self, value: Any) -> dict[str, Any]:
        if not value:
            return {}
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return {}
            return decoded if isinstance(decoded, dict) else {}
        return {}

    def _first_dict(self, *values: Any) -> dict[str, Any]:
        for value in values:
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, str):
                try:
                    decoded = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(decoded, dict):
                    return decoded
        return {}

    def _safe_text(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        if text.startswith("/api/"):
            return text
        if _WINDOWS_DRIVE_RE.search(text) or _UNSAFE_PATH_RE.search(text):
            parts = [part for part in re.split(r"[\\/]", text) if part]
            return parts[-1] if len(parts) > 1 and " " not in text else "[server-path-redacted]"
        return text

    def _safe_text_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in (self._safe_text(raw) for raw in value) if item]

    def _safe_dict_list(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        safe: list[dict[str, Any]] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            safe.append({str(key): self._safe_text(val) or val for key, val in item.items() if key not in {"path", "storage_path", "canonical_path"}})
        return safe

    def _safe_int(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _safe_float(self, value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _safe_datetime(self, value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value.strip():
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def _dedupe(self, values: Any) -> list[str]:
        seen: set[str] = set()
        items: list[str] = []
        for value in values:
            safe = self._safe_text(value)
            key = safe.lower() if safe else ""
            if not key or key in seen:
                continue
            seen.add(key)
            items.append(safe)
        return items


storyboard_trace_service = StoryboardTraceService()
