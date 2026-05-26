from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.storage import MediaAsset, MediaAssetType
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from services.storyboard_frame_service import storyboard_frame_service


class StoryboardAssetRepairService:

    async def repair_storyboard_shot_asset_links(
        self,
        db: AsyncSession,
        project_id: str,
        tenant: TenantContext,
    ) -> dict[str, Any]:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == tenant.organization_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        shots = list(result.scalars().all())

        repaired: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        not_found: list[dict[str, Any]] = []

        for shot in shots:
            shot_id = str(shot.id)
            if getattr(shot, "asset_id", None):
                asset_result = await db.execute(
                    select(MediaAsset).where(MediaAsset.id == shot.asset_id)
                )
                existing_asset = asset_result.scalar_one_or_none()
                if existing_asset is not None:
                    skipped.append({"shot_id": shot_id, "reason": "already_has_valid_asset"})
                    continue

            meta = storyboard_frame_service.decode_metadata(
                getattr(shot, "metadata_json", None)
            )

            candidates = await self._find_matching_assets(
                db, project_id, shot_id, meta, tenant
            )

            if not candidates:
                not_found.append({"shot_id": shot_id, "reason": "no_matching_asset_found"})
                continue

            best_match = candidates[0]
            matched_by = str(getattr(best_match, "_matched_by", "unknown") or "unknown")
            match_score = int(getattr(best_match, "_match_score", 0) or 0)
            association_method = (
                "direct_metadata_link"
                if matched_by == "metadata_json.storyboard_shot_id"
                else "repair_service"
            )
            meta["asset_association"] = {
                "association_method": association_method,
                "association_confidence": min(1.0, match_score / 100.0),
                "association_reason": matched_by,
                "repaired_at": datetime.now(timezone.utc).isoformat(),
            }
            shot.asset_id = best_match.id
            shot.metadata_json = json.dumps(meta, ensure_ascii=False, default=str)
            db.add(shot)
            repaired.append({
                "shot_id": shot_id,
                "asset_id": str(best_match.id),
                "matched_by": matched_by,
                "association_method": association_method,
                "association_confidence": min(1.0, match_score / 100.0),
            })

        await db.commit()

        return {
            "project_id": project_id,
            "total_shots": len(shots),
            "repaired_count": len(repaired),
            "skipped_count": len(skipped),
            "not_found_count": len(not_found),
            "repaired": repaired,
            "skipped": skipped,
            "not_found": not_found,
        }

    async def _find_matching_assets(
        self,
        db: AsyncSession,
        project_id: str,
        shot_id: str,
        shot_meta: dict[str, Any],
        tenant: TenantContext,
    ) -> list[MediaAsset]:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.project_id == project_id,
                MediaAsset.organization_id == tenant.organization_id,
                MediaAsset.asset_type == MediaAssetType.IMAGE,
            )
        )
        all_assets = list(result.scalars().all())

        scored: list[tuple[int, MediaAsset, str]] = []

        for asset in all_assets:
            score, reason = self._score_asset_match(asset, shot_id, shot_meta)
            if score > 0:
                asset._matched_by = reason  # type: ignore[attr-defined]
                asset._match_score = score  # type: ignore[attr-defined]
                scored.append((score, asset, reason))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [asset for _score, asset, _reason in scored]

    def _score_asset_match(
        self,
        asset: MediaAsset,
        shot_id: str,
        shot_meta: dict[str, Any],
    ) -> tuple[int, str]:
        score = 0
        reason = ""

        asset_meta_raw = getattr(asset, "metadata_json", None)
        asset_meta: dict[str, Any] = {}
        if isinstance(asset_meta_raw, dict):
            asset_meta = asset_meta_raw
        elif isinstance(asset_meta_raw, str):
            import json
            try:
                asset_meta = json.loads(asset_meta_raw)
            except (json.JSONDecodeError, TypeError):
                asset_meta = {}

        meta_storyboard_shot_id = asset_meta.get("storyboard_shot_id") or asset_meta.get("source_shot_id")
        if meta_storyboard_shot_id and str(meta_storyboard_shot_id) == shot_id:
            score += 100
            reason = "metadata_json.storyboard_shot_id"

        meta_job_id = asset_meta.get("generation_job_id") or asset_meta.get("render_job_id")
        shot_job_id = shot_meta.get("generation_job_id") or shot_meta.get("render_job_id")
        if meta_job_id and shot_job_id and str(meta_job_id) == str(shot_job_id):
            score += 50
            if not reason:
                reason = "shared_job_id"

        asset_job_id = getattr(asset, "job_id", None)
        shot_render_job = shot_meta.get("render_job_id") or shot_meta.get("generation_job_id")
        if asset_job_id and shot_render_job and str(asset_job_id) == str(shot_render_job):
            score += 40
            if not reason:
                reason = "asset.job_id_matches_shot_meta"

        segment = shot_id[:8] if len(shot_id) >= 8 else shot_id
        file_name = getattr(asset, "file_name", "") or ""
        canonical_path = getattr(asset, "canonical_path", "") or ""
        relative_path = getattr(asset, "relative_path", "") or ""
        if segment in file_name or segment in canonical_path or segment in relative_path:
            score += 30
            if not reason:
                reason = "shot_id_segment_in_path"

        if not reason:
            reason = "fallback_other"

        return score, reason


storyboard_asset_repair_service = StoryboardAssetRepairService()
logger = logging.getLogger(__name__)
