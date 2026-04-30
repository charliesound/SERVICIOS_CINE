from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project, ProjectJob
from models.production import ProductionBreakdown
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from services.job_tracking_service import job_tracking_service
from services.script_intake_service import script_intake_service


class StoryboardGenerationMode:
    FULL_SCRIPT = "FULL_SCRIPT"
    SEQUENCE = "SEQUENCE"
    SCENE_RANGE = "SCENE_RANGE"
    SINGLE_SCENE = "SINGLE_SCENE"


@dataclass
class StoryboardSequenceBlock:
    sequence_id: str
    sequence_number: int
    title: str
    summary: str
    included_scenes: list[int]
    characters: list[str]
    location: Optional[str]
    emotional_arc: Optional[str]
    estimated_duration: Optional[int]
    estimated_shots: int


class StoryboardService:
    STORYBOARD_STYLES = [
        "cinematic_realistic",
        "graphic_novel",
        "moody_noir",
        "commercial_pitch",
    ]

    SHOT_KEYWORDS = {
        "WS": ["crowd", "street", "enters", "crosses", "establishing", "wide"],
        "CU": ["looks", "eyes", "face", "tears", "close", "whispers"],
        "OTS": ["talks", "dialogue", "answers", "argues", "asks"],
        "TRACKING": ["runs", "walks", "follows", "chases", "moves"],
        "POV": ["sees", "notices", "discovers", "finds"],
    }

    async def get_storyboard_options(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> dict[str, Any]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        analysis_data = await self._get_analysis_payload(db, project)
        sequences = self._sequence_blocks_from_analysis(analysis_data)
        status = await self._build_storyboard_status(db, project_id=project_id)
        return {
            "modes": [
                StoryboardGenerationMode.FULL_SCRIPT,
                StoryboardGenerationMode.SEQUENCE,
                StoryboardGenerationMode.SCENE_RANGE,
                StoryboardGenerationMode.SINGLE_SCENE,
            ],
            "sequences": [self._sequence_block_dict(block, status) for block in sequences],
            "scenes_detected": analysis_data.get("scenes", []),
            "styles_available": self.STORYBOARD_STYLES,
            "storyboard_status": status,
        }

    async def list_storyboard_sequences(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> list[dict[str, Any]]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        analysis_data = await self._get_analysis_payload(db, project)
        status = await self._build_storyboard_status(db, project_id=project_id)
        return [self._sequence_block_dict(block, status) for block in self._sequence_blocks_from_analysis(analysis_data)]

    async def list_storyboard_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
        mode: Optional[str] = None,
        sequence_id: Optional[str] = None,
        scene_number: Optional[int] = None,
    ) -> tuple[list[StoryboardShot], Optional[int]]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        query = select(StoryboardShot).where(
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == str(project.organization_id),
            StoryboardShot.is_active.is_(True),
        )
        if sequence_id:
            query = query.where(StoryboardShot.sequence_id == sequence_id)
        if scene_number is not None:
            query = query.where(StoryboardShot.scene_number == scene_number)
        if mode:
            query = query.where(StoryboardShot.generation_mode == mode)
        query = query.order_by(
            StoryboardShot.scene_number.asc(),
            StoryboardShot.sequence_id.asc(),
            StoryboardShot.sequence_order.asc(),
            StoryboardShot.created_at.asc(),
        )
        result = await db.execute(query)
        shots = list(result.scalars().all())
        version = max((int(getattr(shot, "version", 1) or 1) for shot in shots), default=None)
        return shots, version

    async def get_sequence_storyboard(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        sequence_id: str,
        tenant: TenantContext,
    ) -> tuple[dict[str, Any], list[StoryboardShot]]:
        sequences = await self.list_storyboard_sequences(db, project_id=project_id, tenant=tenant)
        sequence = next((item for item in sequences if item["sequence_id"] == sequence_id), None)
        if sequence is None:
            raise HTTPException(status_code=404, detail="Sequence not found")
        shots, _version = await self.list_storyboard_shots(
            db,
            project_id=project_id,
            tenant=tenant,
            sequence_id=sequence_id,
        )
        return sequence, shots

    async def generate_storyboard(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
        mode: str,
        style_preset: str,
        shots_per_scene: int,
        overwrite: bool,
        sequence_id: Optional[str] = None,
        scene_start: Optional[int] = None,
        scene_end: Optional[int] = None,
        selected_scene_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        analysis_data = await self._get_analysis_payload(db, project)
        sequences = self._sequence_blocks_from_analysis(analysis_data)
        selected_scenes = self._select_scenes(
            analysis_data=analysis_data,
            sequences=sequences,
            mode=mode,
            sequence_id=sequence_id,
            scene_start=scene_start,
            scene_end=scene_end,
            selected_scene_ids=selected_scene_ids or [],
        )
        if not selected_scenes:
            raise HTTPException(status_code=400, detail="No scenes available for storyboard generation")

        version = await self._next_generation_version(
            db,
            project_id=project_id,
            tenant=tenant,
            mode=mode,
            sequence_id=sequence_id,
            scene_start=scene_start,
            scene_end=scene_end,
            selected_scenes=selected_scenes,
        )

        job = ProjectJob(
            organization_id=tenant.organization_id,
            project_id=project_id,
            job_type="storyboard",
            status="processing",
            created_by=tenant.user_id,
        )
        db.add(job)
        await db.flush()
        await job_tracking_service.record_project_job_event(
            db,
            job=job,
            event_type="job_created",
            status_from=None,
            status_to="processing",
            message="Storyboard generation started",
            metadata_json={
                "mode": mode,
                "sequence_id": sequence_id,
                "scene_start": scene_start,
                "scene_end": scene_end,
                "style_preset": style_preset,
                "version": version,
            },
        )

        if overwrite:
            await self._deactivate_scope_shots(
                db,
                project_id=project_id,
                organization_id=tenant.organization_id,
                mode=mode,
                sequence_id=sequence_id,
                scene_start=scene_start,
                scene_end=scene_end,
                selected_scenes=selected_scenes,
            )

        generated_scenes_payload: list[dict[str, Any]] = []
        created_shots = 0
        sequence_offsets: dict[str, int] = {}
        for scene in selected_scenes:
            scene_number = self._scene_number(scene)
            sequence_for_scene = self._sequence_for_scene(scene_number, sequences)
            sequence_scope_id = sequence_for_scene.sequence_id if sequence_for_scene else ""
            current_offset = sequence_offsets.get(sequence_scope_id, 0)
            shot_payloads = self._build_scene_shots(scene, shots_per_scene=shots_per_scene, style_preset=style_preset)
            generated_scenes_payload.append(
                {
                    "scene_number": scene_number,
                    "heading": scene.get("heading") or f"ESCENA {scene_number}",
                    "location": scene.get("location"),
                    "time_of_day": scene.get("time_of_day"),
                    "shots": shot_payloads,
                }
            )
            for offset, shot in enumerate(shot_payloads, start=1):
                db.add(
                    StoryboardShot(
                        project_id=project_id,
                        organization_id=tenant.organization_id,
                        sequence_id=sequence_for_scene.sequence_id if sequence_for_scene else None,
                        sequence_order=current_offset + offset,
                        scene_number=scene_number,
                        scene_heading=scene.get("heading") or f"ESCENA {scene_number}",
                        narrative_text=shot["description"],
                        shot_type=shot["shot_type"],
                        visual_mode=style_preset,
                        generation_mode=mode,
                        generation_job_id=str(job.id),
                        version=version,
                        is_active=True,
                    )
                )
                created_shots += 1
            sequence_offsets[sequence_scope_id] = current_offset + len(shot_payloads)

        result_payload = {
            "project_id": project_id,
            "mode": mode,
            "sequence_id": sequence_id,
            "scene_start": scene_start,
            "scene_end": scene_end,
            "selected_scene_ids": selected_scene_ids or [],
            "style_preset": style_preset,
            "shots_per_scene": shots_per_scene,
            "version": version,
            "total_scenes": len(generated_scenes_payload),
            "total_shots": created_shots,
            "scenes": generated_scenes_payload,
        }
        job.status = "completed"
        job.result_data = json.dumps(result_payload, ensure_ascii=False)
        job.completed_at = datetime.now(timezone.utc)
        asset = await job_tracking_service.upsert_job_asset(
            db,
            organization_id=tenant.organization_id,
            project_id=project_id,
            job_id=str(job.id),
            file_name=f"{project.name}_storyboard_v{version}.json",
            content_ref=f"virtual://{project_id}/{job.id}/storyboard_v{version}.json",
            asset_source="script_storyboard",
            metadata_json=result_payload,
            created_by=tenant.user_id,
        )
        await job_tracking_service.record_project_job_event(
            db,
            job=job,
            event_type="job_succeeded",
            status_from="processing",
            status_to="completed",
            message="Storyboard generation completed",
            metadata_json={
                "asset_id": str(asset.id),
                "mode": mode,
                "sequence_id": sequence_id,
                "version": version,
                "total_scenes": len(generated_scenes_payload),
                "total_shots": created_shots,
            },
        )
        await db.commit()
        return {
            "job_id": str(job.id),
            "status": "completed",
            "mode": mode,
            "version": version,
            "sequence_id": sequence_id,
            "scene_start": scene_start,
            "scene_end": scene_end,
            "total_scenes": len(generated_scenes_payload),
            "total_shots": created_shots,
            "created_at": job.created_at,
            "generated_assets": [str(asset.id)],
            "scenes": generated_scenes_payload,
        }

    async def _get_project_for_tenant(self, db: AsyncSession, *, project_id: str, tenant: TenantContext) -> Project:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
            raise HTTPException(status_code=403, detail="Project not accessible for tenant")
        return project

    async def _get_analysis_payload(self, db: AsyncSession, project: Project) -> dict[str, Any]:
        result = await db.execute(
            select(ProductionBreakdown).where(ProductionBreakdown.project_id == str(project.id))
        )
        breakdown = result.scalar_one_or_none()
        if breakdown and breakdown.breakdown_json:
            try:
                payload = json.loads(breakdown.breakdown_json)
                if payload.get("scenes"):
                    return payload
            except Exception:
                pass
        if not project.script_text:
            raise HTTPException(status_code=400, detail="Project has no script text available")
        scenes = script_intake_service.parse_script(project.script_text)
        breakdowns = script_intake_service.build_scene_breakdowns(scenes)
        department_breakdown = script_intake_service.build_department_breakdown(breakdowns)
        return {
            "scenes": scenes,
            "breakdowns": breakdowns,
            "department_breakdown": department_breakdown,
            "sequences": self._build_sequences_from_scenes(scenes),
        }

    def _sequence_blocks_from_analysis(self, analysis_data: dict[str, Any]) -> list[StoryboardSequenceBlock]:
        existing = analysis_data.get("sequences")
        if isinstance(existing, list) and existing:
            blocks: list[StoryboardSequenceBlock] = []
            for item in existing:
                blocks.append(
                    StoryboardSequenceBlock(
                        sequence_id=str(item.get("sequence_id") or item.get("id") or f"seq_{item.get('sequence_number', 1):02d}"),
                        sequence_number=int(item.get("sequence_number") or len(blocks) + 1),
                        title=str(item.get("title") or f"Sequence {len(blocks) + 1}"),
                        summary=str(item.get("summary") or ""),
                        included_scenes=[int(value) for value in item.get("included_scenes", []) if value is not None],
                        characters=[str(value) for value in item.get("characters", []) if value],
                        location=item.get("location"),
                        emotional_arc=item.get("emotional_arc"),
                        estimated_duration=item.get("estimated_duration"),
                        estimated_shots=int(item.get("estimated_shots") or 0),
                    )
                )
            return blocks
        return self._build_sequences_from_scenes(analysis_data.get("scenes", []))

    def _build_sequences_from_scenes(self, scenes: list[dict[str, Any]]) -> list[StoryboardSequenceBlock]:
        if not scenes:
            return []
        block_size = 3
        sequences: list[StoryboardSequenceBlock] = []
        for index in range(0, len(scenes), block_size):
            chunk = scenes[index:index + block_size]
            sequence_number = len(sequences) + 1
            first_scene = chunk[0]
            included_scenes = [self._scene_number(scene) for scene in chunk]
            characters = sorted({character for scene in chunk for character in scene.get("characters_detected", []) if character})
            title = first_scene.get("location") or first_scene.get("heading") or f"Sequence {sequence_number}"
            summary = "; ".join(
                (scene.get("heading") or f"Scene {self._scene_number(scene)}") for scene in chunk
            )[:220]
            sequences.append(
                StoryboardSequenceBlock(
                    sequence_id=f"seq_{sequence_number:02d}",
                    sequence_number=sequence_number,
                    title=title,
                    summary=summary,
                    included_scenes=included_scenes,
                    characters=characters,
                    location=first_scene.get("location"),
                    emotional_arc=self._sequence_emotional_arc(chunk),
                    estimated_duration=len(chunk) * 60,
                    estimated_shots=max(1, len(chunk) * 3),
                )
            )
        return sequences

    def _sequence_emotional_arc(self, scenes: list[dict[str, Any]]) -> str:
        text = " ".join(" ".join(scene.get("action_blocks", [])) for scene in scenes).lower()
        if any(token in text for token in ("chase", "screams", "accident", "fight", "run")):
            return "escalation"
        if any(token in text for token in ("confess", "silence", "wait", "observe", "memory")):
            return "introspection"
        return "setup"

    async def _build_storyboard_status(self, db: AsyncSession, *, project_id: str) -> dict[str, Any]:
        total_result = await db.execute(
            select(func.count(StoryboardShot.id)).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        sequence_result = await db.execute(
            select(StoryboardShot.sequence_id, func.count(StoryboardShot.id), func.max(StoryboardShot.version))
            .where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.is_active.is_(True),
            )
            .group_by(StoryboardShot.sequence_id)
        )
        per_sequence: dict[str, dict[str, Any]] = {}
        for seq_id, count, version in sequence_result.all():
            per_sequence[str(seq_id or "")] = {
                "shots": int(count or 0),
                "version": int(version or 0),
            }
        return {
            "total_active_shots": int(total_result.scalar_one() or 0),
            "sequences": per_sequence,
        }

    def _sequence_block_dict(self, block: StoryboardSequenceBlock, status: dict[str, Any]) -> dict[str, Any]:
        seq_status = status.get("sequences", {}).get(block.sequence_id, {})
        current_version = int(seq_status.get("version") or 0)
        return {
            "sequence_id": block.sequence_id,
            "sequence_number": block.sequence_number,
            "title": block.title,
            "summary": block.summary,
            "included_scenes": block.included_scenes,
            "characters": block.characters,
            "location": block.location,
            "emotional_arc": block.emotional_arc,
            "estimated_duration": block.estimated_duration,
            "estimated_shots": block.estimated_shots,
            "storyboard_status": "generated" if seq_status.get("shots") else "not_generated",
            "current_version": current_version,
        }

    def _select_scenes(
        self,
        *,
        analysis_data: dict[str, Any],
        sequences: list[StoryboardSequenceBlock],
        mode: str,
        sequence_id: Optional[str],
        scene_start: Optional[int],
        scene_end: Optional[int],
        selected_scene_ids: list[str],
    ) -> list[dict[str, Any]]:
        scenes = list(analysis_data.get("scenes", []))
        normalized_mode = (mode or StoryboardGenerationMode.FULL_SCRIPT).strip().upper()
        if normalized_mode == StoryboardGenerationMode.FULL_SCRIPT:
            return scenes
        if normalized_mode == StoryboardGenerationMode.SEQUENCE:
            sequence = next((item for item in sequences if item.sequence_id == sequence_id), None)
            if sequence is None:
                raise HTTPException(status_code=404, detail="Sequence not found")
            return [scene for scene in scenes if self._scene_number(scene) in set(sequence.included_scenes)]
        if normalized_mode == StoryboardGenerationMode.SCENE_RANGE:
            if scene_start is None or scene_end is None:
                raise HTTPException(status_code=400, detail="scene_start and scene_end are required")
            return [scene for scene in scenes if scene_start <= self._scene_number(scene) <= scene_end]
        if normalized_mode == StoryboardGenerationMode.SINGLE_SCENE:
            target_ids = {value for value in selected_scene_ids if value}
            if not target_ids and scene_start is not None:
                target_ids = {str(scene_start)}
            return [scene for scene in scenes if str(self._scene_number(scene)) in target_ids or str(scene.get("scene_id")) in target_ids]
        raise HTTPException(status_code=400, detail="Unsupported storyboard generation mode")

    async def _next_generation_version(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
        mode: str,
        sequence_id: Optional[str],
        scene_start: Optional[int],
        scene_end: Optional[int],
        selected_scenes: list[dict[str, Any]],
    ) -> int:
        query = select(func.max(StoryboardShot.version)).where(
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == tenant.organization_id,
        )
        if mode == StoryboardGenerationMode.SEQUENCE and sequence_id:
            query = query.where(StoryboardShot.sequence_id == sequence_id)
        elif mode == StoryboardGenerationMode.SCENE_RANGE and scene_start is not None and scene_end is not None:
            query = query.where(StoryboardShot.scene_number >= scene_start, StoryboardShot.scene_number <= scene_end)
        elif mode == StoryboardGenerationMode.SINGLE_SCENE:
            numbers = [self._scene_number(scene) for scene in selected_scenes]
            query = query.where(StoryboardShot.scene_number.in_(numbers))
        result = await db.execute(query)
        current = result.scalar_one_or_none()
        return int(current or 0) + 1

    async def _deactivate_scope_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        mode: str,
        sequence_id: Optional[str],
        scene_start: Optional[int],
        scene_end: Optional[int],
        selected_scenes: list[dict[str, Any]],
    ) -> None:
        query = select(StoryboardShot).where(
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == organization_id,
            StoryboardShot.is_active.is_(True),
        )
        if mode == StoryboardGenerationMode.SEQUENCE and sequence_id:
            query = query.where(StoryboardShot.sequence_id == sequence_id)
        elif mode == StoryboardGenerationMode.SCENE_RANGE and scene_start is not None and scene_end is not None:
            query = query.where(StoryboardShot.scene_number >= scene_start, StoryboardShot.scene_number <= scene_end)
        elif mode == StoryboardGenerationMode.SINGLE_SCENE:
            scene_numbers = [self._scene_number(scene) for scene in selected_scenes]
            query = query.where(StoryboardShot.scene_number.in_(scene_numbers))
        result = await db.execute(query)
        for shot in result.scalars().all():
            shot.is_active = False

    def _build_scene_shots(self, scene: dict[str, Any], *, shots_per_scene: int, style_preset: str) -> list[dict[str, Any]]:
        actions = [line for line in scene.get("action_blocks", []) if line]
        heading = scene.get("heading") or "Escena"
        text_pool = actions[:shots_per_scene] or [heading]
        shots: list[dict[str, Any]] = []
        for index in range(max(1, shots_per_scene)):
            source_text = text_pool[index] if index < len(text_pool) else heading
            shot_type = self._detect_shot_type(source_text)
            shots.append(
                {
                    "shot_number": index + 1,
                    "shot_type": shot_type,
                    "description": f"{source_text[:140]} ({style_preset})",
                }
            )
        return shots

    def _detect_shot_type(self, text: str) -> str:
        text_lower = text.lower()
        for shot_type, keywords in self.SHOT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return shot_type
        if len(text.split()) <= 6:
            return "CU"
        return "MS"

    def _scene_number(self, scene: dict[str, Any]) -> int:
        for key in ("scene_number", "scene_no"):
            value = scene.get(key)
            if value is not None:
                try:
                    return int(value)
                except Exception:
                    pass
        scene_id = str(scene.get("scene_id") or "")
        match = re.search(r"(\d+)", scene_id)
        if match:
            return int(match.group(1))
        return 0

    def _sequence_for_scene(self, scene_number: int, sequences: list[StoryboardSequenceBlock]) -> Optional[StoryboardSequenceBlock]:
        for sequence in sequences:
            if scene_number in set(sequence.included_scenes):
                return sequence
        return None


storyboard_service = StoryboardService()
