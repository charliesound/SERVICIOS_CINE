from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project, ProjectJob
from models.production import ProductionBreakdown
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from schemas.cid_sequence_first_schema import resolve_sequence_entry
from schemas.cid_script_to_prompt_schema import (
    CinematicIntent,
    PromptSpec,
    ScriptScene,
)
from schemas.cid_director_feedback_schema import (
    DirectorFeedbackInterpretation,
    DirectorFeedbackNote,
    FeedbackCategory,
    FeedbackSeverity,
    FeedbackTargetType,
    PromptRevisionPatch,
    RegenerationStrategy,
    ShotFeedbackRequest,
    StoryboardRevisionPlan,
    StoryboardRevisionResult,
)
from services.cinematic_intent_service import cinematic_intent_service
from services.cinematography_prompt_reference_service import cinematography_prompt_reference_service
from services.continuity_memory_service import continuity_memory_service
from services.director_feedback_interpretation_service import director_feedback_interpretation_service
from services.director_lens_service import director_lens_service
from services.job_tracking_service import job_tracking_service
from services.llm.llm_service import StoryboardPromptLLMOutput, llm_service
from services.montage_intelligence_service import montage_intelligence_service
from services.prompt_construction_service import prompt_construction_service
from services.prompt_revision_service import prompt_revision_service
from services.render_job_service import render_job_service
from services.script_intake_service import script_intake_service
from services.semantic_prompt_validation_service import semantic_prompt_validation_service
from services.storyboard_image_script_validation_service import storyboard_image_script_validation_service
from services.storyboard_prompt_reference_service import storyboard_prompt_reference_service


class StoryboardGenerationMode:
    FULL_SCRIPT = "FULL_SCRIPT"
    SEQUENCE = "SEQUENCE"
    SCENE_RANGE = "SCENE_RANGE"
    SINGLE_SCENE = "SINGLE_SCENE"
    SELECTED_SCENES = "SELECTED_SCENES"


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
        "hand_drawn_storyboard",
        "rough_pencil_storyboard",
        "ink_storyboard",
        "charcoal_storyboard",
        "graphic_novel_storyboard",
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
    RENDER_ENABLED_STYLES = {
        "hand_drawn_storyboard",
        "rough_pencil_storyboard",
        "ink_storyboard",
        "charcoal_storyboard",
        "graphic_novel_storyboard",
        "cinematic_realistic",
        "storyboard_realistic",
        "moody_noir",
        "commercial_pitch",
    }

    NON_REALISTIC_NEGATIVE = (
        "photograph, photorealistic, hyperreal, hyper realistic, ultra realistic, realistic face, realistic skin, "
        "natural skin texture, detailed skin, DSLR, RAW photo, cinematic still, cinematic photography, movie frame, "
        "final frame, final movie frame, concept art render, 3d render, octane render, unreal engine, glossy"
    )

    def build_storyboard_visual_style_prompt(self, style_preset: str) -> dict[str, str]:
        preset = (style_preset or "hand_drawn_storyboard").strip().lower()
        aliases = {
            "graphic_novel": "graphic_novel_storyboard",
        }
        normalized = aliases.get(preset, preset)
        if normalized not in {
            "hand_drawn_storyboard",
            "rough_pencil_storyboard",
            "ink_storyboard",
            "charcoal_storyboard",
            "graphic_novel_storyboard",
            "cinematic_realistic",
            "moody_noir",
            "commercial_pitch",
        }:
            normalized = "hand_drawn_storyboard"

        style_prompts = {
            "hand_drawn_storyboard": "rough hand drawn storyboard, pencil line art, unfinished production sketch, loose construction lines, storyboard thumbnails, black and white, monochrome, no color, director blocking sketch, rough pencil sketch, expressive loose strokes, previsualization drawing",
            "rough_pencil_storyboard": "rough pencil storyboard drawing, hand-sketched cinematic panel, monochrome graphite lines, production storyboard rough pass, gesture-driven linework",
            "ink_storyboard": "ink storyboard line art, strong black contours, monochrome storyboard frame, cinematic blocking illustration, clean directional hatching",
            "charcoal_storyboard": "charcoal storyboard concept frame, expressive dark tonal sketch, cinematic silhouette planning, monochrome textured strokes",
            "graphic_novel_storyboard": "graphic novel storyboard panel, dramatic line art, stylized monochrome shading, cinematic framing and action readability",
            "cinematic_realistic": "cinematic realistic storyboard frame",
            "moody_noir": "moody noir storyboard frame",
            "commercial_pitch": "commercial pitch storyboard frame",
        }
        legacy_realistic = normalized in {"cinematic_realistic", "moody_noir", "commercial_pitch"}
        return {
            "positive_style_prompt": style_prompts[normalized],
            "negative_style_prompt": "" if legacy_realistic else self.NON_REALISTIC_NEGATIVE,
            "normalized_style_preset": normalized,
            "preset_key": "storyboard_realistic" if legacy_realistic else "storyboard_sketch",
            "checkpoint": "Realistic_Vision_V2.0.safetensors" if legacy_realistic else "",
        }

    async def _run_llm_storyboard_prompts_or_none(
        self,
        *,
        project: Project,
        scene: dict[str, Any],
        style_preset: str,
        shots_per_scene: int,
    ) -> StoryboardPromptLLMOutput | None:
        if not llm_service.is_enabled_for("storyboard_prompt_provider"):
            return None
        try:
            return await llm_service.generate_storyboard_prompts(
                project_name=str(project.name),
                project_description=str(project.description or ""),
                scene=scene,
                style_preset=style_preset,
                shots_per_scene=shots_per_scene,
            )
        except Exception as exc:
            if llm_service.should_fallback(exc):
                return None
            raise

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
                StoryboardGenerationMode.SELECTED_SCENES,
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
        if sequence_id:
            try:
                analysis_data = await self._get_analysis_payload(db, project)
                sequence_id = self._canonical_sequence_id(
                    self._sequence_blocks_from_analysis(analysis_data),
                    sequence_id,
                )
            except HTTPException:
                pass
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

        # Populate asset URLs and compute render_status from MediaAsset + metadata
        asset_ids = [s.asset_id for s in shots if s.asset_id]
        assets_map: dict[str, Any] = {}
        if asset_ids:
            from models.storage import MediaAsset
            asset_result = await db.execute(
                select(MediaAsset).where(MediaAsset.id.in_(asset_ids))
            )
            assets_map = {str(a.id): a for a in asset_result.scalars().all()}

        for shot in shots:
            meta: dict[str, Any] = {}
            if shot.metadata_json:
                try:
                    meta = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
                except Exception:
                    meta = {}

            render_job_id = meta.get("render_job_id")
            render_status_from_meta = meta.get("render_status", "")

            if shot.asset_id and shot.asset_id in assets_map:
                asset = assets_map[shot.asset_id]
                shot.asset_file_name = asset.file_name  # type: ignore[attr-defined]
                shot.asset_mime_type = asset.mime_type  # type: ignore[attr-defined]
                shot.thumbnail_url = f"/api/projects/{project_id}/presentation/assets/{shot.asset_id}/thumbnail"  # type: ignore[attr-defined]
                content_ref = asset.content_ref
                if content_ref and content_ref.startswith("file://"):
                    shot.preview_url = f"/api/projects/{project_id}/presentation/assets/{shot.asset_id}/preview"  # type: ignore[attr-defined]
                else:
                    shot.preview_url = content_ref or f"/api/projects/{project_id}/presentation/assets/{shot.asset_id}/preview"  # type: ignore[attr-defined]
                shot.render_status = "completed"  # type: ignore[attr-defined]
            elif render_job_id:
                shot.render_job_id = render_job_id  # type: ignore[attr-defined]
                shot.render_status = render_status_from_meta or "render_pending"  # type: ignore[attr-defined]
            else:
                shot.render_status = "no_asset"  # type: ignore[attr-defined]

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
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        analysis_data = await self._get_analysis_payload(db, project)
        blocks = self._sequence_blocks_from_analysis(analysis_data)
        resolved = self._resolve_sequence_block(blocks, sequence_id)
        if resolved is None:
            raise HTTPException(status_code=404, detail="Sequence not found")
        canonical_sequence_id = resolved.sequence_id
        sequence = self._sequence_block_dict(
            resolved,
            await self._build_storyboard_status(db, project_id=project_id),
        )
        shots, _version = await self.list_storyboard_shots(
            db,
            project_id=project_id,
            tenant=tenant,
            sequence_id=canonical_sequence_id,
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
        sequence_ids: Optional[list[str]] = None,
        scene_start: Optional[int] = None,
        scene_end: Optional[int] = None,
        selected_scene_ids: Optional[list[str]] = None,
        scene_numbers: Optional[list[int]] = None,
        max_scenes: Optional[int] = None,
        director_lens_id: Optional[str] = None,
        montage_profile_id: Optional[str] = None,
        use_cinematic_intelligence: bool = False,
        use_montage_intelligence: bool = False,
        validate_prompts: bool = False,
        visual_reference_profile_id: str | None = None,
        visual_reference_mode: str | None = None,
    ) -> dict[str, Any]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        analysis_data = await self._get_analysis_payload(db, project)
        sequences = self._sequence_blocks_from_analysis(analysis_data)
        sequence_id = self._canonical_sequence_id(sequences, sequence_id)
        sequence_ids = self._canonical_sequence_ids(sequences, sequence_ids or [])

        if use_cinematic_intelligence and director_lens_id:
            try:
                director_lens_service.get_profile(director_lens_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))

        if use_montage_intelligence and montage_profile_id:
            valid = montage_intelligence_service.list_profiles()
            valid_ids = {p["profile_id"] for p in valid}
            if montage_profile_id not in valid_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown montage profile: {montage_profile_id}",
                )

        selected_scenes = self._select_scenes(
            analysis_data=analysis_data,
            sequences=sequences,
            mode=mode,
            sequence_id=sequence_id,
            sequence_ids=sequence_ids,
            scene_start=scene_start,
            scene_end=scene_end,
            selected_scene_ids=selected_scene_ids or [],
            scene_numbers=scene_numbers or [],
            max_scenes=max_scenes,
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

        await job_tracking_service.update_progress(
            db, job=job, percent=10, stage="Cargando análisis del proyecto", code="loading_project_analysis"
        )

        await job_tracking_service.update_progress(
            db, job=job, percent=20, stage="Seleccionando escenas", code="selecting_scenes"
        )

        await job_tracking_service.record_project_job_event(
            db,
            job=job,
            event_type="job_created",
            status_from=None,
            status_to="processing",
            message="Storyboard generation started",
            metadata_json={
                "mode": mode,
                "generation_mode": mode,
                "sequence_id": sequence_id,
                "sequence_ids": sequence_ids,
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
        render_requests: list[dict[str, Any]] = []
        created_shots = 0
        sequence_offsets: dict[str, int] = {}

        await job_tracking_service.update_progress(
            db, job=job, percent=35, stage="Generando planos de storyboard", code="generating_storyboard_shots"
        )

        for scene in selected_scenes:
            scene_number = self._scene_number(scene)
            sequence_for_scene = self._sequence_for_scene(scene_number, sequences)
            sequence_scope_id = sequence_for_scene.sequence_id if sequence_for_scene else ""
            current_offset = sequence_offsets.get(sequence_scope_id, 0)

            if use_cinematic_intelligence:
                shot_payloads = self._build_cinematic_storyboard_shot(
                    scene,
                    shots_per_scene=shots_per_scene,
                    style_preset=style_preset,
                    director_lens_id=director_lens_id,
                    montage_profile_id=montage_profile_id,
                    use_montage_intelligence=use_montage_intelligence,
                    validate_prompts=validate_prompts,
                    visual_reference_profile_id=visual_reference_profile_id,
                    visual_reference_mode=visual_reference_mode,
                )
            else:
                llm_shot_bundle = await self._run_llm_storyboard_prompts_or_none(
                    project=project,
                    scene=scene,
                    style_preset=style_preset,
                    shots_per_scene=shots_per_scene,
                )
                shot_payloads = (
                    [shot.model_dump() for shot in llm_shot_bundle.shots]
                    if llm_shot_bundle and llm_shot_bundle.shots
                    else self._build_scene_shots(scene, shots_per_scene=shots_per_scene, style_preset=style_preset)
                )
            shot_payloads = [
                self._enrich_storyboard_shot_payload(
                    scene=scene,
                    shot_payload=shot,
                    sequence_for_scene=sequence_for_scene,
                    style_preset=style_preset,
                    shot_order=index + 1,
                )
                for index, shot in enumerate(shot_payloads)
            ]
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
                metadata_raw = shot.get("metadata_json") or {}
                if isinstance(metadata_raw, str):
                    try:
                        metadata_raw = json.loads(metadata_raw)
                    except Exception:
                        metadata_raw = {}
                metadata_raw["source_scope"] = "sequence" if sequence_for_scene else "scene"
                metadata_raw["sequence_id"] = sequence_for_scene.sequence_id if sequence_for_scene else None
                metadata_raw["sequence_title"] = sequence_for_scene.title if sequence_for_scene else None
                metadata_raw["sequence_summary"] = sequence_for_scene.summary if sequence_for_scene else None
                metadata_raw["shot_plan_reason"] = shot.get("shot_plan_reason", "automatic from scene analysis")
                metadata_raw["script_excerpt_used"] = shot.get("script_excerpt_used", "")
                metadata_str = json.dumps(metadata_raw, ensure_ascii=False, default=str)
                shot_record = StoryboardShot(
                    project_id=project_id,
                    organization_id=tenant.organization_id,
                    sequence_id=sequence_for_scene.sequence_id if sequence_for_scene else None,
                    sequence_order=current_offset + offset,
                    scene_number=scene_number,
                    scene_heading=scene.get("heading") or f"ESCENA {scene_number}",
                    narrative_text=shot.get("narrative_text") or shot.get("positive_prompt") or shot.get("description"),
                    shot_type=shot["shot_type"],
                    visual_mode=style_preset,
                    generation_mode=mode,
                    generation_job_id=str(job.id),
                    version=version,
                    metadata_json=metadata_str,
                    is_active=True,
                )
                db.add(shot_record)
                await db.flush()
                render_requests.append(
                    {
                        "shot_id": str(shot_record.id),
                        "scene": scene,
                        "shot_payload": shot,
                        "scene_number": shot_record.scene_number,
                        "shot_type": shot_record.shot_type,
                        "prompt_summary": shot.get("positive_prompt") or shot_record.narrative_text,
                    }
                )
                created_shots += 1
            sequence_offsets[sequence_scope_id] = current_offset + len(shot_payloads)

        await job_tracking_service.update_progress(
            db, job=job, percent=50, stage="Creando prompts visuales", code="creating_visual_prompts"
        )

        render_jobs: list[dict[str, Any]] = []
        render_errors: list[dict[str, Any]] = []

        await job_tracking_service.update_progress(
            db, job=job, percent=65, stage="Encolando render still", code="enqueueing_still_render"
        )

        result_payload = {
            "project_id": project_id,
            "mode": mode,
            "generation_mode": mode,
            "sequence_id": sequence_id,
            "sequence_ids": sequence_ids,
            "scene_start": scene_start,
            "scene_end": scene_end,
            "selected_scene_ids": selected_scene_ids or [],
            "selected_scene_numbers": [self._scene_number(scene) for scene in selected_scenes],
            "total_selected": len(selected_scenes),
            "style_preset": style_preset,
            "shots_per_scene": shots_per_scene,
            "max_scenes": max_scenes,
            "version": version,
            "total_scenes": len(generated_scenes_payload),
            "total_shots": created_shots,
            "render_jobs": render_jobs,
            "render_errors": render_errors,
            "scenes": generated_scenes_payload,
        }

        await job_tracking_service.update_progress(
            db, job=job, percent=75, stage="Render jobs creados", code="render_job_created"
        )

        has_render_jobs = bool(render_requests) and self._should_enqueue_render(mode=mode, style_preset=style_preset, shots_per_scene=shots_per_scene)

        await job_tracking_service.update_progress(
            db,
            job=job,
            percent=100,
            stage="Estructura de storyboard completada. Render pendiente." if has_render_jobs else "Estructura de storyboard completada",
            code="storyboard_structure_completed",
        )

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

        if self._should_enqueue_render(mode=mode, style_preset=style_preset, shots_per_scene=shots_per_scene):
            max_render_shots = min(shots_per_scene, len(render_requests))
            for request in render_requests[:max_render_shots]:
                prompt_payload = self._build_render_prompt_payload(
                    project=project,
                    scene=request["scene"],
                    shot_payload=request["shot_payload"],
                    style_preset=style_preset,
                    shot_id=request["shot_id"],
                    scene_number=request["scene_number"],
                )
                response, queue_item = await render_job_service.submit_job(
                    tenant=tenant,
                    task_type="still",
                    workflow_key="still_storyboard_frame",
                    prompt=prompt_payload,
                    priority=5,
                    target_instance="still",
                    project_id=project_id,
                    metadata={
                        "storyboard_shot_id": request["shot_id"],
                        "storyboard_job_id": str(job.id),
                        "storyboard_mode": mode,
                        "style_preset": style_preset,
                        "scene_number": request["scene_number"],
                        "shot_type": request["shot_type"],
                        "prompt_summary": request["prompt_summary"],
                    },
                )
                if response.status.value == "queued" and queue_item is not None:
                    render_jobs.append(
                        {
                            "job_id": response.job_id,
                            "backend": response.backend,
                            "workflow_key": "still_storyboard_frame",
                            "storyboard_shot_id": request["shot_id"],
                        }
                    )
                else:
                    render_errors.append(
                        {
                            "storyboard_shot_id": request["shot_id"],
                            "error": response.error or "Render queue unavailable",
                        }
                    )

            if render_jobs or render_errors:
                result_payload["render_jobs"] = render_jobs
                result_payload["render_errors"] = render_errors
                job.result_data = json.dumps(result_payload, ensure_ascii=False)
                await job_tracking_service.upsert_job_asset(
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

                # Persist render_job_id on each shot's metadata_json
                for rj in render_jobs:
                    shot_id = rj["storyboard_shot_id"]
                    shot_result = await db.execute(
                        select(StoryboardShot).where(StoryboardShot.id == shot_id)
                    )
                    shot = shot_result.scalar_one_or_none()
                    if shot is not None:
                        meta: dict[str, Any] = {}
                        if shot.metadata_json:
                            try:
                                meta = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
                            except Exception:
                                meta = {}
                        meta["render_job_id"] = rj["job_id"]
                        meta["render_status"] = "render_pending"
                        shot.metadata_json = json.dumps(meta, ensure_ascii=False, default=str)

                await db.commit()

        return {
            "job_id": str(job.id),
            "status": "completed",
            "mode": mode,
            "generation_mode": mode,
            "version": version,
            "sequence_id": sequence_id,
            "sequence_ids": sequence_ids,
            "scene_start": scene_start,
            "scene_end": scene_end,
            "selected_scene_numbers": [self._scene_number(scene) for scene in selected_scenes],
            "total_selected": len(selected_scenes),
            "total_scenes": len(generated_scenes_payload),
            "total_shots": created_shots,
            "created_at": job.created_at,
            "generated_assets": [str(asset.id)],
            "render_jobs": render_jobs,
            "render_errors": render_errors,
            "scenes": generated_scenes_payload,
        }

    async def _get_project_for_tenant(self, db: AsyncSession, *, project_id: str, tenant: TenantContext) -> Project:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
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
        def _value(block: Any, key: str, default: Any = None) -> Any:
            if isinstance(block, dict):
                return block.get(key, default)
            return getattr(block, key, default)

        existing = analysis_data.get("sequences")
        if isinstance(existing, list) and existing:
            blocks: list[StoryboardSequenceBlock] = []
            for item in existing:
                sequence_number = _value(item, "sequence_number", len(blocks) + 1)
                try:
                    sequence_number = int(sequence_number or len(blocks) + 1)
                except (TypeError, ValueError):
                    sequence_number = len(blocks) + 1

                included_scenes_raw = _value(item, "included_scenes", []) or []
                characters_raw = _value(item, "characters", []) or []
                blocks.append(
                    StoryboardSequenceBlock(
                        sequence_id=str(
                            _value(item, "sequence_id")
                            or _value(item, "id")
                            or f"seq_{sequence_number:02d}"
                        ),
                        sequence_number=sequence_number,
                        title=str(_value(item, "title") or f"Sequence {len(blocks) + 1}"),
                        summary=str(_value(item, "summary") or ""),
                        included_scenes=[int(value) for value in included_scenes_raw if value is not None],
                        characters=[str(value) for value in characters_raw if value],
                        location=_value(item, "location"),
                        emotional_arc=_value(item, "emotional_arc"),
                        estimated_duration=_value(item, "estimated_duration"),
                        estimated_shots=int(_value(item, "estimated_shots") or 0),
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
                    sequence_id=f"seq_{sequence_number:03d}",
                    sequence_number=sequence_number,
                    title=f"Secuencia {sequence_number} — Escenas {min(included_scenes)}-{max(included_scenes)}" if included_scenes else title,
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

    def _resolve_sequence_block(self, blocks: list[StoryboardSequenceBlock], sequence_id: str) -> StoryboardSequenceBlock | None:
        """Resolve a sequence block from any seq_01/seq_001/1 format."""
        if not sequence_id or not str(sequence_id).strip():
            return None
        # 1. Exact match
        for b in blocks:
            if b.sequence_id == sequence_id:
                return b
        # 2. Try number-based patterns
        number: int | None = None
        stripped = sequence_id.strip()
        if stripped.isdigit():
            number = int(stripped)
        else:
            m = re.search(r'(?:seq|sequence|s)_?0*(\d+)$', sequence_id, re.IGNORECASE)
            if m:
                number = int(m.group(1))
        if number is not None:
            for b in blocks:
                if b.sequence_number == number:
                    return b
                for fmt in (f"seq_{number:02d}", f"seq_{number:03d}", f"sequence_{number:02d}", f"sequence_{number:03d}"):
                    if b.sequence_id == fmt:
                        return b
        return None

    def _canonical_sequence_id(
        self,
        blocks: list[StoryboardSequenceBlock],
        sequence_id: Optional[str],
    ) -> Optional[str]:
        if sequence_id is None:
            return None
        stripped = str(sequence_id).strip()
        if not stripped:
            return None
        resolved = self._resolve_sequence_block(blocks, stripped)
        return resolved.sequence_id if resolved is not None else stripped

    def _canonical_sequence_ids(
        self,
        blocks: list[StoryboardSequenceBlock],
        sequence_ids: list[str],
    ) -> list[str]:
        canonical_ids: list[str] = []
        seen: set[str] = set()
        for sequence_id in sequence_ids:
            canonical = self._canonical_sequence_id(blocks, sequence_id)
            if canonical and canonical not in seen:
                seen.add(canonical)
                canonical_ids.append(canonical)
        return canonical_ids

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
        sequence_ids: list[str],
        scene_start: Optional[int],
        scene_end: Optional[int],
        selected_scene_ids: list[str],
        scene_numbers: list[int],
        max_scenes: Optional[int],
    ) -> list[dict[str, Any]]:
        scenes = list(analysis_data.get("scenes", []))
        normalized_mode = (mode or StoryboardGenerationMode.FULL_SCRIPT).strip().upper()
        if normalized_mode == StoryboardGenerationMode.FULL_SCRIPT:
            return scenes[:max_scenes] if max_scenes and max_scenes > 0 else scenes
        if normalized_mode == StoryboardGenerationMode.SEQUENCE:
            if sequence_id is None or not str(sequence_id).strip():
                raise HTTPException(status_code=400, detail="sequence_id is required for SEQUENCE mode")
            sequence = next((item for item in sequences if item.sequence_id == sequence_id), None)
            if sequence is None:
                sequence = self._resolve_sequence_block(sequences, sequence_id)
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
        if normalized_mode == StoryboardGenerationMode.SELECTED_SCENES:
            target_numbers = {int(value) for value in scene_numbers if value is not None}
            if not target_numbers:
                target_numbers = {int(value) for value in selected_scene_ids if str(value).isdigit()}
            if sequence_ids:
                selected_sequences: list[StoryboardSequenceBlock] = []
                for sid in sequence_ids:
                    match = next((item for item in sequences if item.sequence_id == sid), None)
                    if match is None:
                        match = self._resolve_sequence_block(sequences, sid)
                    if match is not None:
                        selected_sequences.append(match)
                for sequence in selected_sequences:
                    target_numbers.update(sequence.included_scenes)
            return [scene for scene in scenes if self._scene_number(scene) in target_numbers]
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
        elif mode in {StoryboardGenerationMode.SINGLE_SCENE, StoryboardGenerationMode.SELECTED_SCENES}:
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
        elif mode in {StoryboardGenerationMode.SINGLE_SCENE, StoryboardGenerationMode.SELECTED_SCENES}:
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

    def _normalize_text_list(self, values: list[Any]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = str(value or "").strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(text)
        return cleaned

    def _dialogue_lines(self, scene: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        for block in scene.get("dialogue_blocks", []) or []:
            if isinstance(block, dict):
                character = str(block.get("character") or "").strip()
                text = str(block.get("text") or "").strip()
            else:
                character = str(getattr(block, "character", "") or "").strip()
                text = str(getattr(block, "text", "") or "").strip()
            if character and text:
                lines.append(f"{character}: {text}")
            elif text:
                lines.append(text)
        return lines

    def _scene_script_excerpt(self, scene: dict[str, Any], *, max_length: int = 240) -> str:
        fragments: list[str] = []
        heading = str(scene.get("heading") or "").strip()
        if heading:
            fragments.append(heading)
        fragments.extend(str(item).strip() for item in (scene.get("action_blocks") or []) if str(item).strip())
        fragments.extend(self._dialogue_lines(scene)[:2])
        excerpt = " ".join(fragment for fragment in fragments if fragment).strip()
        if len(excerpt) <= max_length:
            return excerpt
        return excerpt[: max_length - 1].rstrip() + "..."

    def _build_enriched_negative_prompt(self, base_negative: str | None) -> str:
        tokens = self._normalize_text_list(
            [
                base_negative or "",
                "blurry",
                "low quality",
                "distorted",
                "deformed hands",
                "extra fingers",
                "watermark",
                "text",
                "logo",
                "daylight in night scenes",
                "extra characters not present in script",
                "wrong props",
                "inconsistent wardrobe",
                "inconsistent location",
                "generic fantasy elements",
            ]
        )
        return ", ".join(tokens)

    def _enrich_storyboard_shot_payload(
        self,
        *,
        scene: dict[str, Any],
        shot_payload: dict[str, Any],
        sequence_for_scene: Optional[StoryboardSequenceBlock],
        style_preset: str,
        shot_order: int,
    ) -> dict[str, Any]:
        payload = dict(shot_payload)
        metadata_payload = payload.get("metadata_json") or {}
        if isinstance(metadata_payload, str):
            try:
                metadata_payload = json.loads(metadata_payload)
            except Exception:
                metadata_payload = {}
        elif not isinstance(metadata_payload, dict):
            metadata_payload = {}

        script_scene = self._scene_dict_to_script_scene(scene)
        continuity_anchors = continuity_memory_service.build_continuity_anchors(script_scene)
        scene_heading = str(scene.get("heading") or f"ESCENA {self._scene_number(scene)}").strip()
        location = str(scene.get("location") or sequence_for_scene.location or scene_heading).strip()
        time_of_day = str(scene.get("time_of_day") or "").strip() or "unspecified time"
        characters = self._normalize_text_list(
            list(scene.get("characters_detected") or [])
            + list(scene.get("characters") or [])
            + (sequence_for_scene.characters if sequence_for_scene else [])
        )
        main_character = ", ".join(characters[:2]) if characters else "main subject from the script"
        action_line = str(payload.get("description") or payload.get("narrative_text") or "").strip()
        script_excerpt = self._scene_script_excerpt(scene)
        if not action_line:
            action_line = script_excerpt or scene_heading
        visual_elements = self._normalize_text_list(
            list(scene.get("visual_anchors") or [])
            + list(scene.get("props") or [])
            + continuity_anchors[:4]
        )
        key_visual = ", ".join(visual_elements[:4]) if visual_elements else "script-faithful visual continuity"
        emotional_intent = str(
            scene.get("emotional_tone")
            or metadata_payload.get("directorial_intent", {}).get("dramatic_intent")
            or payload.get("visual_style")
            or (sequence_for_scene.emotional_arc if sequence_for_scene else "")
            or "cinematic tension"
        ).strip()
        shot_objective = str(
            metadata_payload.get("shot_editorial_purpose", {}).get("purpose")
            or payload.get("shot_plan_reason")
            or scene.get("dramatic_objective")
            or action_line
        ).strip()
        shot_type = str(payload.get("shot_type") or "MS").strip() or "MS"
        camera_motion = str(
            metadata_payload.get("shot_editorial_purpose", {}).get("cut_reason")
            or payload.get("camera_movement")
            or ("handheld subtle" if shot_type == "POV" else "dolly in" if shot_type == "TRACKING" else "locked frame")
        ).strip()
        lighting_style = str(payload.get("lighting") or metadata_payload.get("directorial_intent", {}).get("lighting") or time_of_day).strip()
        lens_style = str(payload.get("lens") or metadata_payload.get("directorial_intent", {}).get("lens") or "50mm cinematic prime").strip()
        prompt_model_family = str(metadata_payload.get("prompt_model_family") or payload.get("prompt_model_family") or "wan22").strip() or "wan22"
        continuity_phrase = ", ".join(
            self._normalize_text_list(
                [
                    f"sequence {sequence_for_scene.sequence_id}" if sequence_for_scene else "",
                    f"location {location}" if location else "",
                    f"time {time_of_day}" if time_of_day else "",
                    *visual_elements[:2],
                ]
            )
        )
        visual_constraints = self._normalize_text_list(
            [
                "stable identity",
                "consistent outfit",
                "prop continuity",
                "no text",
                "no watermark",
                "avoid elements not present in the script",
            ]
        )
        base_positive = str(payload.get("positive_prompt") or payload.get("prompt") or "").strip()
        prompt_package = storyboard_prompt_reference_service.build_wan22_t2v_prompt_package(
            main_character=main_character,
            character_continuity=characters,
            action=action_line if not base_positive else f"{action_line}; script-faithful detail: {base_positive}",
            location=location,
            time_of_day=time_of_day,
            emotional_intent=emotional_intent,
            camera_motion=camera_motion,
            lighting_style=lighting_style,
            lens_style=lens_style,
            background_details=key_visual,
            continuity_constraints=self._normalize_text_list([continuity_phrase, *characters]),
            visual_constraints=visual_constraints,
            shot_type=shot_type,
            scene_heading=scene_heading,
            shot_objective=shot_objective,
            script_excerpt_used=script_excerpt,
            model_family=prompt_model_family,
            strict_negative=True,
            diagnostic_rules_applied=["wan22_t2v_prompt_director", "negative_prompt_library", "camera_motion_dictionary"],
            shot_plan={
                "shot_type": shot_type,
                "camera_motion": camera_motion,
                "lighting_style": lighting_style,
                "lens_style": lens_style,
            },
            single_continuous_take=True,
        )
        scene_guidance = cinematography_prompt_reference_service.build_cinematography_guidance_for_script_scene(
            scene_heading=scene_heading,
            emotional_intent=emotional_intent,
            location=location,
            time_of_day=time_of_day,
        )
        shot_guidance = cinematography_prompt_reference_service.build_visual_prompt_guidance_for_shot(
            shot_type=shot_type,
            action=action_line,
            emotional_intent=emotional_intent,
        )
        color_grading_vocab = cinematography_prompt_reference_service.extract_color_grading_vocabulary()
        color_grading = color_grading_vocab[0] if color_grading_vocab else "cinematic grade"
        model_guidance = cinematography_prompt_reference_service.build_model_specific_prompt_guidance(
            model_family=prompt_model_family,
            subject=main_character,
            action=action_line,
            environment=location,
            lighting=scene_guidance["lighting_style"],
            style=style_preset,
        )
        cinematography_sources = [
            value["path"]
            for value in cinematography_prompt_reference_service.load_cinematography_prompt_references()["references"].values()
        ]
        enriched_positive = prompt_package["positive_prompt"]
        enriched_negative = prompt_package["negative_prompt"]
        metadata_payload.update(prompt_package["metadata"])
        metadata_payload["location_continuity"]["sequence_id"] = sequence_for_scene.sequence_id if sequence_for_scene else None
        metadata_payload["visual_continuity"]["continuity_phrase"] = continuity_phrase
        metadata_payload["visual_continuity"]["anchors"] = visual_elements
        metadata_payload["shot_order"] = shot_order
        metadata_payload["cinematography_reference_sources"] = cinematography_sources
        metadata_payload["shot_type"] = shot_guidance["shot_type"]
        metadata_payload["framing"] = shot_guidance["framing"]
        metadata_payload["camera_angle"] = shot_guidance["camera_angle"]
        metadata_payload["camera_motion"] = shot_guidance["camera_motion"]
        metadata_payload["lens_suggestion"] = lens_style
        metadata_payload["lighting_style"] = scene_guidance["lighting_style"]
        metadata_payload["color_palette"] = scene_guidance["color_palette"]
        metadata_payload["color_grading"] = color_grading
        metadata_payload["atmosphere"] = scene_guidance["atmosphere"]
        metadata_payload["composition_notes"] = shot_guidance["composition"]
        metadata_payload["visual_constraints"] = visual_constraints
        metadata_payload["model_prompt_family"] = model_guidance["model_prompt_family"]
        metadata_payload["model_specific_guidance"] = model_guidance

        validation_payload = storyboard_image_script_validation_service.build_validation_payload(
            script_excerpt_used=script_excerpt,
            positive_prompt=enriched_positive,
            scene_heading=scene_heading,
            shot_type=shot_type,
            characters=characters,
            location=location,
            visual_constraints=visual_constraints,
            atmosphere=scene_guidance["atmosphere"],
        )
        validation_result = storyboard_image_script_validation_service.validate_shot(
            validation_payload=validation_payload,
            observed_visual_text=str(metadata_payload.get("render_observation_text") or ""),
        )
        metadata_payload["validation_result"] = validation_result
        metadata_payload["validation_score"] = validation_result["overall_match_score"]
        metadata_payload["validation_failures"] = validation_result["missing_elements"] + validation_result["incorrect_elements"]
        metadata_payload["suggested_regeneration_prompt"] = validation_result["suggested_regeneration_prompt"]

        payload["description"] = action_line[:180]
        payload["narrative_text"] = enriched_positive[:500]
        payload["positive_prompt"] = enriched_positive
        payload["negative_prompt"] = enriched_negative
        payload["metadata_json"] = metadata_payload
        payload["continuity_notes"] = continuity_phrase or camera_motion
        payload["script_excerpt_used"] = script_excerpt
        payload["shot_plan_reason"] = payload.get("shot_plan_reason") or shot_objective
        return payload

    def _detect_shot_type(self, text: str) -> str:
        text_lower = text.lower()
        for shot_type, keywords in self.SHOT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return shot_type
        if len(text.split()) <= 6:
            return "CU"
        return "MS"

    def _scene_dict_to_script_scene(self, scene: dict[str, Any]) -> ScriptScene:
        scene_number = self._scene_number(scene)
        heading = scene.get("heading") or f"ESCENA {scene_number}"
        int_ext = None
        location = scene.get("location")
        time_of_day = scene.get("time_of_day")
        heading_upper = heading.upper()
        if heading_upper.startswith("INT") or heading_upper.startswith("INT."):
            int_ext = "INT"
        elif heading_upper.startswith("EXT") or heading_upper.startswith("EXT."):
            int_ext = "EXT"
        elif "/" in heading_upper:
            int_ext = "INT/EXT"
        action_blocks = scene.get("action_blocks") or []
        raw_text = " ".join(action_blocks) if action_blocks else heading
        characters_raw = scene.get("characters_detected") or scene.get("characters") or []
        return ScriptScene(
            scene_id=str(scene.get("scene_id") or f"scene_{scene_number:04d}"),
            scene_number=scene_number,
            heading=heading,
            int_ext=int_ext,
            location=location,
            time_of_day=time_of_day,
            raw_text=raw_text,
            action_summary=raw_text[:500],
            dialogue_summary=scene.get("dialogue_summary"),
            characters=list(set(str(c) for c in characters_raw if c)),
            props=scene.get("props") or [],
            production_needs=scene.get("production_needs") or [],
            dramatic_objective=scene.get("dramatic_objective"),
            conflict=scene.get("conflict"),
            emotional_tone=scene.get("emotional_tone"),
            visual_anchors=scene.get("visual_anchors") or [],
            forbidden_elements=scene.get("forbidden_elements") or [],
        )

    def _build_cinematic_storyboard_shot(
        self,
        scene: dict[str, Any],
        *,
        shots_per_scene: int,
        style_preset: str,
        director_lens_id: Optional[str] = None,
        montage_profile_id: Optional[str] = None,
        use_montage_intelligence: bool = False,
        validate_prompts: bool = False,
        visual_reference_profile_id: str | None = None,
        visual_reference_mode: str | None = None,
    ) -> list[dict[str, Any]]:
        script_scene = self._scene_dict_to_script_scene(scene)
        continuity_anchors = continuity_memory_service.build_continuity_anchors(
            script_scene,
            continuity_memory_service.build_project_visual_bible([script_scene]),
        )
        intent = cinematic_intent_service.build_intent(
            script_scene,
            "storyboard_frame",
            continuity_anchors=continuity_anchors,
            director_lens_id=director_lens_id or "adaptive_auteur_fusion",
            montage_profile_id=montage_profile_id or "adaptive_montage",
        )
        enriched = None
        alignment_score_captured = None
        if visual_reference_profile_id:
            from schemas.cid_visual_reference_schema import ScriptVisualAlignmentRequest
            from services.script_visual_alignment_service import script_visual_alignment_service
            try:
                align_request = ScriptVisualAlignmentRequest(
                    scene_id=script_scene.scene_id,
                    script_excerpt=script_scene.raw_text,
                )
                align_result, enriched = script_visual_alignment_service.align(align_request)
                alignment_score_captured = align_result.alignment_score
            except Exception:
                pass
        prompt_spec = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset=style_preset,
            enriched_intent=enriched,
        )
        validation = None
        if validate_prompts:
            validation = semantic_prompt_validation_service.validate(prompt_spec, intent)
            if validation and not validation.is_valid:
                prompt_spec.validation_status = "invalid"
                prompt_spec.validation_errors = validation.errors
            elif validation:
                prompt_spec.validation_status = "valid"

        shot_payloads: list[dict[str, Any]] = []
        shot_types_pool = [intent.shot_size, "CU", "MS", "WS", "OTS"]
        for index in range(max(1, shots_per_scene)):
            shot_order = index + 1
            shot_type = shot_types_pool[index] if index < len(shot_types_pool) else "MS"
            shot_editorial = None
            if use_montage_intelligence and intent.montage_intent:
                next_type = shot_types_pool[index + 1] if index + 1 < len(shot_types_pool) else "reaction_or_reveal"
                prev_type = shot_types_pool[index - 1] if index > 0 else None
                shot_editorial = montage_intelligence_service.build_shot_editorial_purpose(
                    script_scene,
                    shot_order=shot_order,
                    shot_type=shot_type,
                    montage_intent=intent.montage_intent,
                    previous_shot_type=prev_type,
                    next_shot_type=next_type,
                )

            description = intent.action or script_scene.action_summary
            prompt_text = prompt_spec.positive_prompt or description
            negative = prompt_spec.negative_prompt

            metadata_payload: dict[str, Any] = {
                "directorial_intent": self._serialize_model(intent.directorial_intent),
                "montage_intent": self._serialize_model(intent.montage_intent),
                "editorial_beats": [self._serialize_model(b) for b in intent.editorial_beats],
                "shot_editorial_purpose": self._serialize_model(shot_editorial or intent.shot_editorial_purpose),
                "prompt_spec": self._serialize_model(prompt_spec),
                "cinematic_intent_id": intent.intent_id,
                "director_lens_id": intent.director_lens_id,
                "visual_reference_profile_id": visual_reference_profile_id,
                "visual_reference_mode": visual_reference_mode or "palette_lighting",
            }
            if enriched is not None:
                metadata_payload["script_visual_alignment"] = {
                    "enriched_intent_summary": enriched.merged_intent_summary,
                    "alignment_score": alignment_score_captured,
                    "non_negotiable_story": enriched.non_negotiable_story_elements,
                    "non_negotiable_visual": enriched.non_negotiable_visual_elements,
                }
            if validation:
                metadata_payload["validation"] = self._serialize_model(validation)

            shot_payloads.append(
                {
                    "shot_number": shot_order,
                    "shot_type": shot_type,
                    "description": description[:180],
                    "narrative_text": prompt_text[:500],
                    "positive_prompt": prompt_text,
                    "negative_prompt": negative,
                    "lens": intent.lens,
                    "lighting": intent.lighting,
                    "composition": intent.composition,
                    "visual_style": intent.mood,
                    "metadata_json": metadata_payload,
                    "source_scope": "scene",
                    "shot_plan_reason": "automatic from scene analysis",
                    "script_excerpt_used": script_scene.raw_text[:200] if hasattr(script_scene, 'raw_text') else "",
                }
            )
        return shot_payloads

    def _serialize_model(self, model: Any) -> dict[str, Any] | None:
        if model is None:
            return None
        if hasattr(model, "model_dump"):
            return model.model_dump()
        if hasattr(model, "_asdict"):
            return model._asdict()
        if isinstance(model, dict):
            return model
        return None

    def _should_enqueue_render(self, *, mode: str, style_preset: str, shots_per_scene: int) -> bool:
        return (
            mode in {
                StoryboardGenerationMode.SINGLE_SCENE,
                StoryboardGenerationMode.SELECTED_SCENES,
                StoryboardGenerationMode.SEQUENCE,
            }
            and shots_per_scene <= 3
            and style_preset in self.RENDER_ENABLED_STYLES
        )

    def _build_render_prompt_payload(
        self,
        *,
        project: Project,
        scene: dict[str, Any],
        shot_payload: dict[str, Any],
        style_preset: str,
        shot_id: str,
        scene_number: Optional[int],
    ) -> dict[str, Any]:
        metadata_payload = shot_payload.get("metadata_json") or {}
        if isinstance(metadata_payload, str):
            try:
                metadata_payload = json.loads(metadata_payload)
            except Exception:
                metadata_payload = {}
        elif not isinstance(metadata_payload, dict):
            metadata_payload = {}
        scene_heading = scene.get("heading") or "Scene"
        location = scene.get("location") or "unknown location"
        time_of_day = scene.get("time_of_day") or "unspecified time"
        shot_type = shot_payload.get("shot_type") or "MS"
        style_cfg = self.build_storyboard_visual_style_prompt(style_preset)
        tone = shot_payload.get("visual_style") or style_cfg["positive_style_prompt"]
        project_context = str(project.description or "").strip()
        primary_prompt = (
            metadata_payload.get("positive_prompt")
            or shot_payload.get("positive_prompt")
            or shot_payload.get("prompt")
            or shot_payload.get("narrative_text")
            or shot_payload.get("description")
            or scene_heading
        )
        prompt_parts = [
            style_cfg["positive_style_prompt"],
            tone,
            f"{shot_type} shot",
            primary_prompt,
            f"Scene heading: {scene_heading}",
            f"Location: {location}",
            f"Time of day: {time_of_day}",
            f"Project: {project.name}",
        ]
        if shot_payload.get("lens"):
            prompt_parts.append(f"Lens: {shot_payload['lens']}")
        if shot_payload.get("lighting"):
            prompt_parts.append(f"Lighting: {shot_payload['lighting']}")
        if shot_payload.get("composition"):
            prompt_parts.append(f"Composition: {shot_payload['composition']}")
        if shot_payload.get("continuity_notes"):
            prompt_parts.append(f"Continuity: {shot_payload['continuity_notes']}")
        if metadata_payload.get("shot_objective"):
            prompt_parts.append(f"Shot objective: {metadata_payload['shot_objective']}")
        if metadata_payload.get("script_excerpt_used"):
            prompt_parts.append(f"Script excerpt: {metadata_payload['script_excerpt_used']}")
        if project_context:
            prompt_parts.append(f"Project context: {project_context}")
        base_negative = (
            metadata_payload.get("negative_prompt")
            or shot_payload.get("negative_prompt")
            or "blurry, low quality, distorted, deformed hands, extra fingers, watermark, text, logo"
        )
        style_negative = style_cfg["negative_style_prompt"]
        negative = ", ".join(part for part in [base_negative, style_negative] if part)
        return {
            "preset_key": style_cfg.get("preset_key") or "storyboard_realistic",
            "prompt": ", ".join(part for part in prompt_parts if part),
            "negative_prompt": negative,
            "checkpoint": style_cfg.get("checkpoint") or "",
            "width": 1024,
            "height": 576,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "filename_prefix": f"storyboard_{str(project.id)[:8]}_{int(scene_number or 0):03d}_{shot_id[:8]}",
            "style_preset": style_preset,
        }

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


    async def revise_storyboard_shot_with_feedback(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        shot_id: str,
        feedback: ShotFeedbackRequest,
        tenant: TenantContext,
    ) -> StoryboardRevisionResult:
        import uuid

        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.id == shot_id,
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == tenant.organization_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        shot = result.scalar_one_or_none()
        if shot is None:
            raise HTTPException(status_code=404, detail="Shot not found")

        metadata_raw: dict[str, Any] = {}
        if shot.metadata_json:
            try:
                metadata_raw = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
            except (json.JSONDecodeError, TypeError):
                metadata_raw = {}

        prompt_spec = metadata_raw.get("prompt_spec", {})
        if isinstance(prompt_spec, str):
            try:
                prompt_spec = json.loads(prompt_spec)
            except (json.JSONDecodeError, TypeError):
                prompt_spec = {}

        script_context: dict[str, Any] = {
            "location": shot.metadata_json.get("scene_heading", "") if isinstance(shot.metadata_json, dict) else "",
            "time_of_day": "",
            "characters": [],
            "action_summary": shot.narrative_text or "",
        }
        if isinstance(shot.metadata_json, dict):
            sv_align = shot.metadata_json.get("script_visual_alignment", {})
            if isinstance(sv_align, dict):
                for req in sv_align.get("scene_requirements", []):
                    if ":" in str(req):
                        parts = str(req).split(":", 1)
                        key = parts[0].strip().lower()
                        val = parts[1].strip()
                        if "location" in key:
                            script_context["location"] = val
                        elif "time" in key:
                            script_context["time_of_day"] = val

        visual_ref_context: dict[str, Any] = {}
        if isinstance(shot.metadata_json, dict):
            ref_profile = shot.metadata_json.get("visual_reference_profile", {})
            if isinstance(ref_profile, dict):
                visual_ref_context = ref_profile

        note = DirectorFeedbackNote(
            note_id=f"fb_{uuid.uuid4().hex[:12]}",
            target_type=FeedbackTargetType.shot,
            target_id=shot_id,
            note_text=feedback.note_text,
            category=feedback.category,
            severity=feedback.severity,
            created_by_role=feedback.created_by_role,
            preserve_original_logic=feedback.preserve_original_logic,
        )

        interpretation = director_feedback_interpretation_service.interpret_feedback(
            note=note,
            original_prompt=prompt_spec if isinstance(prompt_spec, dict) else None,
            script_context=script_context,
            visual_reference_context=visual_ref_context,
            storyboard_metadata=metadata_raw,
        )

        original_intent = metadata_raw.get("directorial_intent", {})
        if isinstance(original_intent, str):
            try:
                original_intent = json.loads(original_intent)
            except (json.JSONDecodeError, TypeError):
                original_intent = {}

        revision = prompt_revision_service.revise_prompt_with_director_feedback(
            prompt_spec=prompt_spec if isinstance(prompt_spec, dict) else None,
            feedback_interpretation=interpretation,
            original_intent=original_intent if isinstance(original_intent, dict) else None,
        )

        regeneration_strategy = RegenerationStrategy.single_shot
        if interpretation.risk_level == "high":
            regeneration_strategy = RegenerationStrategy.single_shot

        requires_confirmation = interpretation.risk_level in ("high", "medium") and feedback.preserve_original_logic

        qa_list = [
            f"VERIFICAR: La nota del director '{feedback.note_text[:60]}' fue interpretada correctamente",
            f"VERIFICAR: Elementos narrativos protegidos: {len(interpretation.protected_story_elements)}",
            f"VERIFICAR: Elementos visuales protegidos: {len(interpretation.protected_visual_elements)}",
        ]
        if interpretation.conflict_with_script:
            qa_list.append(f"VERIFICAR: Conflicto con guion resuelto: {interpretation.conflict_with_script_details[:100]}")
        if interpretation.conflict_with_reference:
            qa_list.append(f"VERIFICAR: Conflicto con referencia resuelto: {interpretation.conflict_with_reference_details[:100]}")

        revised_prompt_spec = dict(prompt_spec) if isinstance(prompt_spec, dict) else {}
        revised_prompt_spec["positive_prompt"] = revision.revised_prompt
        revised_prompt_spec["negative_prompt"] = revision.revised_negative_prompt
        revised_prompt_spec["_revision_version"] = revision.version_number
        revised_prompt_spec["_revision_parent"] = prompt_spec.get("prompt_id", shot_id) if isinstance(prompt_spec, dict) else shot_id

        revision_history = metadata_raw.get("revision_history", [])
        if not isinstance(revision_history, list):
            revision_history = []
        revision_history.append({
            "revision_version": revision.version_number,
            "director_note": feedback.note_text,
            "note_category": feedback.category.value,
            "note_severity": feedback.severity.value,
            "interpretation": interpretation.model_dump(),
            "revision_patch": revision.model_dump(),
            "original_prompt_id": prompt_spec.get("prompt_id", "") if isinstance(prompt_spec, dict) else "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        updated_metadata = dict(metadata_raw)
        updated_metadata["revision_history"] = revision_history
        updated_metadata["latest_revision"] = {
            "version": revision.version_number,
            "revised_prompt_spec": revised_prompt_spec,
            "director_note": feedback.note_text,
            "interpretation": interpretation.model_dump(),
            "revision_patch": revision.model_dump(),
        }
        updated_metadata["prompt_spec"] = revised_prompt_spec
        shot.metadata_json = json.dumps(updated_metadata, ensure_ascii=False, default=str)
        await db.flush()

        revision_plan = StoryboardRevisionPlan(
            project_id=project_id,
            sequence_id=shot.sequence_id or "",
            shot_id=shot_id,
            original_story_logic=shot.narrative_text or "",
            director_feedback=note,
            interpretation=interpretation,
            prompt_revision=revision,
            regeneration_strategy=regeneration_strategy,
            requires_director_confirmation=requires_confirmation,
            qa_checklist=qa_list,
        )

        return StoryboardRevisionResult(
            status="prompt_revised" if not requires_confirmation else "requires_confirmation",
            revision_id=f"rev_{uuid.uuid4().hex[:12]}",
            revision_plan=revision_plan,
            revised_prompt_spec=revised_prompt_spec,
            metadata_json=updated_metadata,
            message=self._build_revision_message(interpretation, revision, requires_confirmation),
        )

    def _failed_shots_from_candidates(
        self,
        candidates: list[StoryboardShot],
        threshold: float = 70,
        include_unvalidated: bool = True,
    ) -> list[StoryboardShot]:
        failed: list[StoryboardShot] = []
        for shot in candidates:
            metadata = self._shot_metadata_dict(shot)
            score_value = metadata.get("validation_score")
            if score_value is None:
                validation_result = metadata.get("validation_result")
                if isinstance(validation_result, dict):
                    score_value = validation_result.get("overall_match_score")
            if score_value is None:
                if include_unvalidated:
                    failed.append(shot)
                continue
            try:
                numeric = float(score_value)
            except Exception:
                continue
            normalized = numeric * 100.0 if numeric <= 1.0 else numeric
            if normalized < threshold:
                failed.append(shot)
        return failed

    async def find_failed_storyboard_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        sequence_id: str,
        organization_id: str,
        threshold: float = 70,
        include_unvalidated: bool = True,
    ) -> tuple[str, list[StoryboardShot]]:
        project = await self._get_project_for_tenant(
            db,
            project_id=project_id,
            tenant=TenantContext(
                organization_id=organization_id,
                user_id="system",
                role="system",
                is_global_admin=False,
            ),
        )
        analysis_data = await self._get_analysis_payload(db, project)
        canonical_sequence_id = self._canonical_sequence_id(
            self._sequence_blocks_from_analysis(analysis_data),
            sequence_id,
        )
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
                StoryboardShot.sequence_id == canonical_sequence_id,
                StoryboardShot.is_active.is_(True),
            ).order_by(StoryboardShot.sequence_order.asc(), StoryboardShot.created_at.asc())
        )
        shots = list(result.scalars().all())
        return canonical_sequence_id, self._failed_shots_from_candidates(
            shots,
            threshold=threshold,
            include_unvalidated=include_unvalidated,
        )

    async def regenerate_storyboard_shot_from_validation(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        shot_id: str,
        tenant: TenantContext,
        threshold: float = 70,
        include_unvalidated: bool = True,
    ) -> dict[str, Any]:
        regen_job_id = f"regen-{uuid4().hex}"
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.id == shot_id,
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == tenant.organization_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        source_shot = result.scalar_one_or_none()
        if source_shot is None:
            raise HTTPException(status_code=404, detail="Shot not found")

        metadata = self._shot_metadata_dict(source_shot)
        score = metadata.get("validation_score")
        if score is None and isinstance(metadata.get("validation_result"), dict):
            score = metadata["validation_result"].get("overall_match_score")
        score_pct = self._normalize_score_to_percentage(score)
        if score_pct is None and not include_unvalidated:
            return {
                "job_id": regen_job_id,
                "project_id": project_id,
                "sequence_id": source_shot.sequence_id,
                "regenerated_shots": [],
                "skipped_shots": [
                    {
                        "shot_id": str(source_shot.id),
                        "source_shot_id": str(source_shot.id),
                        "sequence_id": source_shot.sequence_id,
                        "status": "skipped",
                        "reason": "validation_score is null and include_unvalidated=false",
                    }
                ],
                "threshold": threshold,
                "status": "completed",
            }
        if score_pct is not None and score_pct >= threshold:
            return {
                "job_id": regen_job_id,
                "project_id": project_id,
                "sequence_id": source_shot.sequence_id,
                "regenerated_shots": [],
                "skipped_shots": [
                    {
                        "shot_id": str(source_shot.id),
                        "source_shot_id": str(source_shot.id),
                        "sequence_id": source_shot.sequence_id,
                        "status": "skipped",
                        "reason": f"validation_score {score_pct:.2f} >= threshold {threshold}",
                    }
                ],
                "threshold": threshold,
                "status": "completed",
            }

        regenerated_item = await self._regenerate_single_shot(
            db,
            tenant=tenant,
            project_id=project_id,
            source_shot=source_shot,
            regen_job_id=regen_job_id,
        )
        await db.commit()
        return {
            "job_id": regen_job_id,
            "project_id": project_id,
            "sequence_id": source_shot.sequence_id,
            "regenerated_shots": [regenerated_item],
            "skipped_shots": [],
            "threshold": threshold,
            "status": "completed",
        }

    async def regenerate_failed_storyboard_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        sequence_id: str,
        tenant: TenantContext,
        threshold: float = 70,
        include_unvalidated: bool = True,
    ) -> dict[str, Any]:
        regen_job_id = f"regen-{uuid4().hex}"
        canonical_sequence_id, failed_shots = await self.find_failed_storyboard_shots(
            db,
            project_id=project_id,
            sequence_id=sequence_id,
            organization_id=tenant.organization_id,
            threshold=threshold,
            include_unvalidated=include_unvalidated,
        )
        regenerated: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        if not failed_shots:
            return {
                "job_id": regen_job_id,
                "project_id": project_id,
                "sequence_id": canonical_sequence_id,
                "regenerated_shots": [],
                "skipped_shots": [],
                "threshold": threshold,
                "status": "completed",
            }
        for shot in failed_shots:
            try:
                item = await self._regenerate_single_shot(
                    db,
                    tenant=tenant,
                    project_id=project_id,
                    source_shot=shot,
                    regen_job_id=regen_job_id,
                )
                regenerated.append(item)
            except Exception as exc:
                skipped.append(
                    {
                        "shot_id": str(shot.id),
                        "source_shot_id": str(shot.id),
                        "sequence_id": shot.sequence_id,
                        "status": "skipped",
                        "reason": str(exc),
                    }
                )
        await db.commit()
        return {
            "job_id": regen_job_id,
            "project_id": project_id,
            "sequence_id": canonical_sequence_id,
            "regenerated_shots": regenerated,
            "skipped_shots": skipped,
            "threshold": threshold,
            "status": "completed",
        }

    async def _regenerate_single_shot(
        self,
        db: AsyncSession,
        *,
        tenant: TenantContext,
        project_id: str,
        source_shot: StoryboardShot,
        regen_job_id: str,
    ) -> dict[str, Any]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        metadata = self._shot_metadata_dict(source_shot)
        regen_prompt = self._resolve_regeneration_prompt(metadata)
        metadata["manual_regeneration"] = {
            "source_shot_id": str(source_shot.id),
            "regen_job_id": regen_job_id,
            "used_prompt": regen_prompt,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        metadata.setdefault("validation_result", {})
        metadata["validation_result"]["used_for_regeneration"] = True
        new_shot = StoryboardShot(
            project_id=source_shot.project_id,
            organization_id=source_shot.organization_id,
            sequence_id=source_shot.sequence_id,
            sequence_order=source_shot.sequence_order,
            scene_number=source_shot.scene_number,
            scene_heading=source_shot.scene_heading,
            narrative_text=regen_prompt,
            shot_type=source_shot.shot_type,
            visual_mode=source_shot.visual_mode,
            generation_mode=source_shot.generation_mode,
            generation_job_id=regen_job_id,
            version=source_shot.version,
            metadata_json=json.dumps(metadata, ensure_ascii=False, default=str),
            is_active=True,
        )
        db.add(new_shot)
        await db.flush()
        await db.commit()
        await db.refresh(new_shot)

        regen_style = self.build_storyboard_visual_style_prompt(source_shot.visual_mode or "hand_drawn_storyboard")
        prompt_payload = {
            "preset_key": regen_style.get("preset_key") or "storyboard_realistic",
            "prompt": regen_prompt,
            "negative_prompt": ", ".join(
                part
                for part in [
                    metadata.get("negative_prompt") or "blurry, low quality, distorted, watermark, text",
                    regen_style.get("negative_style_prompt") or "",
                ]
                if part
            ),
            "checkpoint": regen_style.get("checkpoint") or "",
            "width": 1024,
            "height": 576,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "filename_prefix": f"storyboard_regen_{str(project.id)[:8]}_{str(new_shot.id)[:8]}",
            "style_preset": source_shot.visual_mode or "hand_drawn_storyboard",
        }
        response, queue_item = await render_job_service.submit_job(
            tenant=tenant,
            task_type="still",
            workflow_key="still_storyboard_frame",
            prompt=prompt_payload,
            priority=5,
            target_instance="still",
            project_id=project_id,
            metadata={
                "storyboard_shot_id": str(new_shot.id),
                "storyboard_regen_job_id": regen_job_id,
                "source_shot_id": str(source_shot.id),
                "sequence_id": source_shot.sequence_id,
            },
        )
        render_job_id = response.job_id if queue_item is not None else None
        status = "queued" if queue_item is not None else "skipped"
        reason = None if queue_item is not None else (response.error or "Render queue unavailable")
        return {
            "shot_id": str(new_shot.id),
            "source_shot_id": str(source_shot.id),
            "sequence_id": source_shot.sequence_id,
            "status": status,
            "render_job_id": render_job_id,
            "reason": reason,
        }

    def _normalize_score_to_percentage(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except Exception:
            return None
        return numeric * 100.0 if numeric <= 1.0 else numeric

    def _shot_metadata_dict(self, shot: StoryboardShot) -> dict[str, Any]:
        if not shot.metadata_json:
            return {}
        if isinstance(shot.metadata_json, dict):
            return dict(shot.metadata_json)
        try:
            parsed = json.loads(shot.metadata_json)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _resolve_regeneration_prompt(self, metadata: dict[str, Any]) -> str:
        prompt = str(metadata.get("suggested_regeneration_prompt") or "").strip()
        if prompt:
            return prompt
        failures = metadata.get("validation_failures") or []
        if not isinstance(failures, list):
            failures = []
        script_excerpt = str(metadata.get("script_excerpt_used") or "")
        positive_prompt = str(metadata.get("positive_prompt") or "")
        payload = storyboard_image_script_validation_service.build_validation_payload(
            script_excerpt_used=script_excerpt,
            positive_prompt=positive_prompt,
            scene_heading=str(metadata.get("scene_heading") or ""),
            shot_type=str(metadata.get("shot_type") or "MS"),
            characters=list(metadata.get("character_continuity") or []),
            location=str((metadata.get("location_continuity") or {}).get("location") or ""),
            visual_constraints=list(metadata.get("visual_constraints") or []),
            atmosphere=str(metadata.get("atmosphere") or ""),
        )
        base = storyboard_image_script_validation_service.build_regeneration_prompt(validation_payload=payload)
        if failures:
            return f"{base} Critical fixes: {', '.join(str(item) for item in failures)}."
        return base

    def _build_revision_message(
        self,
        interpretation: DirectorFeedbackInterpretation,
        revision: PromptRevisionPatch,
        requires_confirmation: bool,
    ) -> str:
        parts: list[str] = ["CID ha interpretado la nota del director."]
        if interpretation.protected_story_elements:
            parts.append(f"Elementos narrativos protegidos: {len(interpretation.protected_story_elements)}.")
        if interpretation.protected_visual_elements:
            parts.append(f"Elementos visuales protegidos: {len(interpretation.protected_visual_elements)}.")
        if revision.changed_elements:
            parts.append(f"Cambios aplicados: {len(revision.changed_elements)}.")
        if revision.rejected_changes:
            parts.append(f"Cambios rechazados: {len(revision.rejected_changes)}.")
        if interpretation.conflict_with_script:
            parts.append("CONFLICTO CON GUION DETECTADO.")
        if interpretation.conflict_with_reference:
            parts.append("CONFLICTO CON REFERENCIA VISUAL DETECTADO.")
        if requires_confirmation:
            parts.append("Requiere confirmacion del director antes de aplicar.")
        else:
            parts.append("Revision de prompt preparada. Prompt original preservado en metadata.")
        return " ".join(parts)


storyboard_service = StoryboardService()
