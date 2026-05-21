from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.storage import MediaAsset, MediaAssetType
from models.storyboard import StoryboardShot
from schemas.storyboard_presentation_schema import (
    StoryboardFrame,
    StoryboardFrameMetadata,
    StoryboardShotInfo,
)


class StoryboardFrameService:
    _HOST_OUTPUT_PREFIX = "/opt/SERVICIOS_CINE/data/output/"
    _HOST_DATA_PREFIX = "/opt/SERVICIOS_CINE/data/"
    _DOCKER_OUTPUT_ROOT = Path("/app/data/output")
    _DOCKER_DATA_ROOT = Path("/app/data")

    async def collect_by_project(
        self,
        db: AsyncSession,
        project_id: str,
        *,
        organization_id: str | None = None,
        override_shot_info: dict[str, StoryboardShotInfo] | None = None,
    ) -> list[StoryboardFrame]:
        query = select(MediaAsset).where(
            MediaAsset.project_id == project_id,
            MediaAsset.asset_type == MediaAssetType.IMAGE,
        )
        if organization_id:
            query = query.where(MediaAsset.organization_id == organization_id)
        result = await db.execute(query)
        assets = list(result.scalars().all())
        return await self._build_frames(
            db,
            assets,
            render_job_id=None,
            organization_id=organization_id,
            override_shot_info=override_shot_info,
        )

    async def collect_by_render_job(
        self,
        db: AsyncSession,
        render_job_id: str,
        *,
        organization_id: str | None = None,
        override_shot_info: dict[str, StoryboardShotInfo] | None = None,
    ) -> list[StoryboardFrame]:
        query = select(MediaAsset).where(
            MediaAsset.job_id == render_job_id,
            MediaAsset.asset_type == MediaAssetType.IMAGE,
        )
        if organization_id:
            query = query.where(MediaAsset.organization_id == organization_id)
        result = await db.execute(query)
        assets = list(result.scalars().all())
        return await self._build_frames(
            db,
            assets,
            render_job_id=render_job_id,
            organization_id=organization_id,
            override_shot_info=override_shot_info,
        )

    async def collect_by_asset_ids(
        self,
        db: AsyncSession,
        asset_ids: list[str],
        *,
        organization_id: str | None = None,
        override_shot_info: dict[str, StoryboardShotInfo] | None = None,
    ) -> list[StoryboardFrame]:
        if not asset_ids:
            raise ValueError("asset_ids is required")
        query = select(MediaAsset).where(
            MediaAsset.id.in_(asset_ids),
            MediaAsset.asset_type == MediaAssetType.IMAGE,
        )
        if organization_id:
            query = query.where(MediaAsset.organization_id == organization_id)
        result = await db.execute(query)
        assets = list(result.scalars().all())
        return await self._build_frames(
            db,
            assets,
            render_job_id=None,
            organization_id=organization_id,
            override_shot_info=override_shot_info,
        )

    async def _build_frames(
        self,
        db: AsyncSession,
        assets: list[MediaAsset],
        *,
        render_job_id: str | None,
        organization_id: str | None,
        override_shot_info: dict[str, StoryboardShotInfo] | None,
    ) -> list[StoryboardFrame]:
        if not assets:
            raise ValueError("No storyboard image assets found")

        shot_map = await self._load_storyboard_shots(
            db,
            assets=assets,
            render_job_id=render_job_id,
            organization_id=organization_id,
        )

        frames: list[tuple[tuple[int, int, str], StoryboardFrame]] = []
        for index, asset in enumerate(assets, start=1):
            asset_meta = self._decode_json(getattr(asset, "metadata_json", None))
            image_path, attempted_paths = self._resolve_image_path(asset, asset_meta)
            if image_path is None:
                logger.debug(
                    "Skipping storyboard frame asset %s: no existing image file found across candidates",
                    getattr(asset, "id", ""),
                    extra={
                        "asset_id": str(getattr(asset, "id", "") or ""),
                        "job_id": str(getattr(asset, "job_id", "") or ""),
                        "attempted_paths": attempted_paths,
                    },
                )
                continue

            shot = shot_map.get(str(asset.id)) or shot_map.get(str(getattr(asset, "job_id", "") or ""))
            shot_meta = self._decode_json(getattr(shot, "metadata_json", None) if shot is not None else None)
            frame = self._build_frame(
                asset=asset,
                asset_meta=asset_meta,
                shot=shot,
                shot_meta=shot_meta,
                image_path=image_path,
                fallback_shot_number=index,
                override_shot_info=override_shot_info or {},
            )
            sort_key = (
                int(getattr(shot, "scene_number", 0) or 0),
                int(getattr(shot, "sequence_order", frame.shot_number) or frame.shot_number),
                str(getattr(asset, "created_at", "") or ""),
            )
            frames.append((sort_key, frame))

        if not frames:
            raise ValueError("No storyboard frames with existing image files were found")

        frames.sort(key=lambda item: item[0])
        return [frame for _key, frame in frames]

    def limit_frames(
        self,
        frames: list[StoryboardFrame],
        *,
        max_frames: int | None,
        frame_selection_mode: str = "first",
    ) -> list[StoryboardFrame]:
        if frame_selection_mode != "first":
            raise ValueError(f"Unsupported frame_selection_mode: {frame_selection_mode}")
        if max_frames is None or max_frames >= len(frames):
            return list(frames)
        return list(frames[:max_frames])

    async def _load_storyboard_shots(
        self,
        db: AsyncSession,
        *,
        assets: list[MediaAsset],
        render_job_id: str | None,
        organization_id: str | None,
    ) -> dict[str, StoryboardShot]:
        asset_ids = [str(asset.id) for asset in assets]
        query = select(StoryboardShot).where(StoryboardShot.asset_id.in_(asset_ids))
        if organization_id:
            query = query.where(StoryboardShot.organization_id == organization_id)
        result = await db.execute(query)
        shots = list(result.scalars().all())

        shot_map = {str(shot.asset_id): shot for shot in shots if getattr(shot, "asset_id", None)}
        if shot_map or not render_job_id:
            return shot_map

        regen_query = select(StoryboardShot).where(StoryboardShot.generation_job_id == render_job_id)
        if organization_id:
            regen_query = regen_query.where(StoryboardShot.organization_id == organization_id)
        regen_result = await db.execute(regen_query)
        regen_shots = list(regen_result.scalars().all())
        for shot in regen_shots:
            shot_map[str(render_job_id)] = shot
        return shot_map

    def _build_frame(
        self,
        *,
        asset: MediaAsset,
        asset_meta: dict[str, Any],
        shot: StoryboardShot | None,
        shot_meta: dict[str, Any],
        image_path: str,
        fallback_shot_number: int,
        override_shot_info: dict[str, StoryboardShotInfo],
    ) -> StoryboardFrame:
        shot_number = int(getattr(shot, "sequence_order", 0) or 0) or fallback_shot_number
        scene_number = getattr(shot, "scene_number", None)
        scene_heading = getattr(shot, "scene_heading", None)

        info = StoryboardShotInfo(
            scene=scene_heading,
            shot_size=getattr(shot, "shot_type", None),
            camera_angle=self._first_text(shot_meta, "camera_angle", "camera_type"),
            movement=self._first_text(shot_meta, "camera_motion", "movement"),
            description=self._first_text(
                shot_meta,
                "description",
                "positive_prompt",
                fallback=getattr(shot, "narrative_text", None),
            ),
            dialogue=self._first_text(shot_meta, "dialogue"),
            notes=self._first_text(shot_meta, "notes", "prompt_summary"),
            status=self._first_text(asset_meta, "status", fallback=str(getattr(asset, "status", "") or "")),
        )

        override = override_shot_info.get(str(getattr(asset, "id", ""))) or override_shot_info.get(str(getattr(shot, "id", "")))
        if override is not None:
            info = override

        metadata = StoryboardFrameMetadata(
            visual_bible=(asset_meta.get("visual_bible") or shot_meta.get("visual_bible")) if isinstance(asset_meta, dict) else None,
            workflow_profile=asset_meta.get("workflow_profile") if isinstance(asset_meta, dict) else None,
            workflow_fallback_report=asset_meta.get("workflow_fallback_report") if isinstance(asset_meta, dict) else None,
            render_job_id=str(getattr(asset, "job_id", "") or "") or None,
            media_asset_id=str(getattr(asset, "id", "") or "") or None,
        )

        return StoryboardFrame(
            shot_number=shot_number,
            scene_number=str(scene_number) if scene_number is not None else None,
            image_path=image_path,
            info=info,
            metadata=metadata,
        )

    def _resolve_image_path(self, asset: MediaAsset, metadata: dict[str, Any]) -> tuple[str | None, list[str]]:
        raw_candidates = self._raw_path_candidates(asset, metadata)
        relative_candidates = self._relative_path_candidates(asset, metadata, raw_candidates)

        candidate_paths: list[str] = []
        for raw_path in raw_candidates:
            candidate_paths.append(raw_path)
            converted_path = self._map_host_path_to_docker(raw_path)
            if converted_path is not None:
                candidate_paths.append(converted_path)

        for relative_path in relative_candidates:
            output_relative = relative_path.removeprefix("output/")
            candidate_paths.append(str(self._DOCKER_OUTPUT_ROOT / output_relative))
            candidate_paths.append(str(self._DOCKER_DATA_ROOT / relative_path))

        attempted_paths: list[str] = []
        for candidate in self._dedupe_paths(candidate_paths):
            candidate_path = Path(candidate)
            attempted_paths.append(candidate)
            if candidate_path.is_file():
                return str(candidate_path), attempted_paths

        return None, attempted_paths

    def _raw_path_candidates(self, asset: MediaAsset, metadata: dict[str, Any]) -> list[str]:
        raw_values = [
            getattr(asset, "canonical_path", None),
            metadata.get("storage_path"),
            getattr(asset, "content_ref", None),
        ]

        candidates: list[str] = []
        for raw in raw_values:
            parsed_path = self._parse_candidate_path(raw)
            if parsed_path is not None:
                candidates.append(parsed_path)
        return self._dedupe_paths(candidates)

    def _relative_path_candidates(self, asset: MediaAsset, metadata: dict[str, Any], raw_candidates: list[str]) -> list[str]:
        candidates: list[str] = []

        asset_relative_path = self._normalize_relative_path(getattr(asset, "relative_path", None))
        if asset_relative_path is not None:
            candidates.append(asset_relative_path)

        metadata_relative_path = self._normalize_relative_path(metadata.get("relative_path"))
        if metadata_relative_path is not None:
            candidates.append(metadata_relative_path)

        for raw_path in raw_candidates:
            extracted = self._extract_relative_path(raw_path)
            if extracted is not None:
                candidates.append(extracted)

        return self._dedupe_paths(candidates)

    def _parse_candidate_path(self, raw_value: Any) -> str | None:
        if not isinstance(raw_value, str) or not raw_value.strip():
            return None

        value = raw_value.strip()
        if value.startswith("file://"):
            parsed = urlparse(value)
            if parsed.scheme != "file":
                return None

            path_value = parsed.path or ""
            if parsed.netloc not in ("", "localhost"):
                if path_value:
                    if parsed.netloc.endswith(":"):
                        path_value = f"{parsed.netloc}{path_value}"
                    else:
                        path_value = f"//{parsed.netloc}{path_value}"
                else:
                    path_value = parsed.netloc

            file_path = unquote(path_value)
            if parsed.netloc == "" and file_path.startswith("//"):
                file_path = f"/{file_path.lstrip('/')}"
            if file_path.startswith("/") and len(file_path) > 2 and file_path[2] == ":":
                file_path = file_path[1:]
            return file_path or None

        return value

    def _map_host_path_to_docker(self, path_value: str) -> str | None:
        if path_value.startswith(self._HOST_OUTPUT_PREFIX):
            suffix = path_value[len(self._HOST_OUTPUT_PREFIX) :].lstrip("/")
            return str(self._DOCKER_OUTPUT_ROOT / suffix)
        if path_value.startswith(self._HOST_DATA_PREFIX):
            suffix = path_value[len(self._HOST_DATA_PREFIX) :].lstrip("/")
            return str(self._DOCKER_DATA_ROOT / suffix)
        return None

    def _extract_relative_path(self, path_value: str) -> str | None:
        prefixes = (
            self._HOST_OUTPUT_PREFIX,
            f"{self._DOCKER_OUTPUT_ROOT.as_posix().rstrip('/')}/",
            self._HOST_DATA_PREFIX,
            f"{self._DOCKER_DATA_ROOT.as_posix().rstrip('/')}/",
        )
        for prefix in prefixes:
            if path_value.startswith(prefix):
                suffix = path_value[len(prefix) :]
                normalized = self._normalize_relative_path(suffix)
                if normalized is not None:
                    return normalized
        return None

    def _normalize_relative_path(self, raw_value: Any) -> str | None:
        if not isinstance(raw_value, str) or not raw_value.strip():
            return None

        normalized = raw_value.strip().replace("\\", "/").lstrip("/")
        if not normalized or normalized in (".", ".."):
            return None
        if ".." in normalized.split("/"):
            return None
        return normalized

    def _dedupe_paths(self, values: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for value in values:
            cleaned = value.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            deduped.append(cleaned)
        return deduped

    def _decode_json(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return dict(payload)
        if isinstance(payload, str) and payload.strip():
            try:
                decoded = json.loads(payload)
            except json.JSONDecodeError:
                return {}
            return decoded if isinstance(decoded, dict) else {}
        return {}

    def _first_text(self, payload: dict[str, Any], *keys: str, fallback: str | None = None) -> str | None:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return fallback.strip() if isinstance(fallback, str) and fallback.strip() else None


storyboard_frame_service = StoryboardFrameService()


logger = logging.getLogger(__name__)
