from __future__ import annotations

import mimetypes
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.module_access import require_module_access
from models.storage import MediaAsset
from models.storyboard import StoryboardShot
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.shot_schema import StoryboardShotListResponse, StoryboardShotResponse
from schemas.storyboard_schema import (
    StoryboardAutoExportItem,
    StoryboardCreditEstimateRequest,
    StoryboardCreditEstimateResponse,
    StoryboardFailedRegenerateRequest,
    StoryboardGenerateRequest,
    StoryboardGenerationAuditResponse,
    StoryboardJobResponse,
    StoryboardListResponse,
    StoryboardOptionsResponse,
    StoryboardRegenerateShotsResponse,
    StoryboardShotRegenerateRequest,
    StoryboardSequenceDetailResponse,
    StoryboardSequenceResponse,
)
from schemas.storyboard_presentation_schema import (
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
    StoryboardSheetTemplate,
)
from services.comfyui_model_inventory_service import ComfyUIInventoryError
from services.comfyui_pipeline_builder_service import build_storyboard_pipeline_plan
from services.comfyui_storyboard_render_service import comfyui_storyboard_render_service
from schemas.cid_director_feedback_schema import (
    SequenceFeedbackRequest,
    ShotFeedbackRequest,
    StoryboardRevisionPlan,
    StoryboardRevisionResult,
)
from schemas.cid_sequence_first_schema import (
    ScriptSequenceMapEntry,
    SequenceStoryboardPlan,
)
from schemas.storyboard_schema import StoryboardSequencePlanRequest, StoryboardSequencePlanResponse
from schemas.storyboard_trace_schema import StoryboardTraceRecord, StoryboardTraceSummary
from services.cid_script_to_prompt_pipeline_service import (
    analyze_full_script,
    prepare_sequence_storyboard,
)
from services.cid_script_scene_parser_service import cid_script_scene_parser_service
from services.script_sequence_mapping_service import script_sequence_mapping_service
from services.storyboard_service import storyboard_service, StoryboardGenerationMode
from services.storyboard_credit_estimator_service import storyboard_credit_estimator_service
from services.storyboard_asset_repair_service import storyboard_asset_repair_service
from services.storyboard_export_service import storyboard_export_service
from services.storyboard_frame_service import storyboard_frame_service
from services.storyboard_layout_engine import storyboard_layout_engine
from services.storyboard_pdf_export_service import storyboard_pdf_export_service
from services.storyboard_trace_service import storyboard_trace_service


router = APIRouter(
    prefix="/api/projects",
    tags=["storyboard"],
    dependencies=[Depends(require_module_access("storyboard_ai"))],
)


async def _get_storyboard_shot_and_asset(
    db: AsyncSession,
    *,
    project_id: str,
    shot_id: str,
    tenant: TenantContext,
) -> tuple[StoryboardShot, MediaAsset | None]:
    await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    shot_result = await db.execute(
        select(StoryboardShot).where(
            StoryboardShot.id == shot_id,
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == tenant.organization_id,
            StoryboardShot.is_active.is_(True),
        )
    )
    shot = shot_result.scalar_one_or_none()
    if shot is None:
        raise HTTPException(status_code=404, detail="Storyboard shot not found")

    if not getattr(shot, "asset_id", None):
        return shot, None

    asset_result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == shot.asset_id,
            MediaAsset.project_id == project_id,
            MediaAsset.organization_id == tenant.organization_id,
        )
    )
    asset = asset_result.scalar_one_or_none()
    return shot, asset


def _file_response_for_storyboard_media(path_value: str, media_type: str | None, filename: str) -> FileResponse:
    resolved_media_type = media_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return FileResponse(
        path=path_value,
        media_type=resolved_media_type,
        filename=filename,
        content_disposition_type="inline",
    )


@router.get("/{project_id}/storyboard/options", response_model=StoryboardOptionsResponse)
async def get_storyboard_options(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardOptionsResponse:
    payload = await storyboard_service.get_storyboard_options(
        db,
        project_id=project_id,
        tenant=tenant,
    )
    return StoryboardOptionsResponse(**payload)


@router.get("/{project_id}/storyboard/sequences", response_model=list[StoryboardSequenceResponse])
async def list_storyboard_sequences(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[StoryboardSequenceResponse]:
    sequences = await storyboard_service.list_storyboard_sequences(
        db,
        project_id=project_id,
        tenant=tenant,
    )
    return [StoryboardSequenceResponse(**item) for item in sequences]


async def _generate_auto_exports(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
    payload: StoryboardGenerateRequest,
) -> tuple[list[StoryboardAutoExportItem], list[str]]:
    exports: list[StoryboardAutoExportItem] = []
    errors: list[str] = []

    try:
        frames = await storyboard_frame_service.collect_by_project(
            db, project_id, organization_id=tenant.organization_id
        )
        frames = storyboard_frame_service.limit_frames(
            frames,
            max_frames=payload.auto_export_max_frames,
            frame_selection_mode="first",
        )
    except Exception as exc:
        errors.append(f"Failed to collect frames for auto-export: {exc}")
        return exports, errors

    if not frames:
        errors.append("No frames available for auto-export")
        return exports, errors

    layout_config = StoryboardLayoutConfig(
        layout=StoryboardLayoutName.grid_2x2,
        preset=StoryboardSheetPreset.realistic_client_review,
        page_width_px=1080,
        page_height_px=1920,
    )

    sheet_template_enum = None
    if payload.auto_export_template:
        try:
            sheet_template_enum = StoryboardSheetTemplate(payload.auto_export_template)
        except ValueError:
            pass

    try:
        pages = storyboard_layout_engine.render_pages(frames, layout_config)
    except Exception as exc:
        errors.append(f"Failed to render pages for auto-export: {exc}")
        return exports, errors

    for fmt in payload.auto_export_formats or ["png", "pdf"]:
        try:
            base_name = storyboard_export_service.build_export_base_name(
                project_id=project_id,
                layout=layout_config.layout.value,
                frame_count=len(frames),
                output_format=fmt,
                sheet_template=sheet_template_enum.value if sheet_template_enum else None,
            )
            if fmt == "png":
                export_result = storyboard_export_service.export_png(
                    project_id=project_id, pages=pages, base_name=base_name
                )
            else:
                export_result = storyboard_export_service.export_pdf(
                    project_id=project_id, pages=pages, base_name=base_name
                )

            artifact_path = Path(str(export_result["artifact_path"]))
            artifact_url = storyboard_export_service.build_artifact_url(project_id, artifact_path.name)

            exports.append(StoryboardAutoExportItem(
                output_format=fmt,
                artifact_url=artifact_url,
                artifact_path=str(artifact_path),
                frame_count=len(frames),
                page_count=int(export_result.get("page_count", 1)),
                credit_estimate=storyboard_export_service.build_credit_estimate(len(frames)),
            ))
        except Exception as exc:
            errors.append(f"Auto-export {fmt.upper()} failed: {exc}")

    return exports, errors


@router.post("/{project_id}/storyboard/generate", response_model=StoryboardJobResponse)
async def generate_storyboard(
    project_id: str,
    payload: StoryboardGenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardJobResponse:
    mode = (payload.generation_mode or payload.mode or "").upper()
    has_sequence = bool(payload.sequence_id or payload.sequence_ids)

    if mode in (StoryboardGenerationMode.FULL_SCRIPT, "") and not has_sequence:
        raise HTTPException(
            status_code=400,
            detail=(
                "Storyboard generation requires selected sequence_id or selected_sequence_ids. "
                "Run full script analysis first: POST /api/cid/script/analyze-full"
            ),
        )

    result = await storyboard_service.generate_storyboard(
        db,
        project_id=project_id,
        tenant=tenant,
        mode=mode or StoryboardGenerationMode.SEQUENCE,
        sequence_id=payload.sequence_id,
        sequence_ids=payload.sequence_ids,
        scene_start=payload.scene_start,
        scene_end=payload.scene_end,
        selected_scene_ids=payload.selected_scene_ids,
        scene_numbers=payload.scene_numbers,
        style_preset=payload.style_preset,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        max_scenes=payload.max_scenes,
        overwrite=payload.overwrite,
        director_lens_id=payload.director_lens_id,
        montage_profile_id=payload.montage_profile_id,
        use_cinematic_intelligence=payload.use_cinematic_intelligence,
        include_coverage_shots=payload.include_coverage_shots,
        use_montage_intelligence=payload.use_montage_intelligence,
        validate_prompts=payload.validate_prompts,
        sheet_template=payload.sheet_template,
        workflow_profile=payload.workflow_profile,
        render_quality=payload.render_quality,
        model_family=payload.model_family,
        motion_ready=payload.motion_ready,
        image_edit_mode=payload.image_edit_mode,
        shots_per_sequence_mode=payload.shots_per_sequence_mode,
    )

    service_response = {k: result[k] for k in StoryboardJobResponse.model_fields if k in result}
    response = StoryboardJobResponse(**service_response)

    if payload.auto_export_sheet:
        auto_exports, auto_errors = await _generate_auto_exports(
            db, project_id, tenant, payload
        )
        response.auto_exports = auto_exports
        response.auto_export_errors = auto_errors

    return response


@router.post("/{project_id}/storyboard/estimate-credits", response_model=StoryboardCreditEstimateResponse)
async def estimate_storyboard_credits(
    project_id: str,
    payload: StoryboardCreditEstimateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardCreditEstimateResponse:
    project = await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    analysis_data = await storyboard_service._get_analysis_payload(db, project)
    scenes = analysis_data.get("scenes") or []
    sequence_blocks = storyboard_service._sequence_blocks_from_analysis(analysis_data)

    mode = (payload.mode or StoryboardGenerationMode.SEQUENCE).upper()
    estimated_scenes = 0
    notes: list[str] = []

    if payload.sequence_ids:
        selected_scene_numbers: set[int] = set()
        missing_sequence_ids: list[str] = []
        seen_sequence_ids: set[str] = set()
        for requested_id in payload.sequence_ids:
            block = storyboard_service._resolve_sequence_block(sequence_blocks, requested_id)
            if block is None:
                missing_sequence_ids.append(str(requested_id))
                continue
            if block.sequence_id in seen_sequence_ids:
                continue
            seen_sequence_ids.add(block.sequence_id)
            selected_scene_numbers.update(int(item) for item in block.included_scenes)
        estimated_scenes = len(selected_scene_numbers)
        if missing_sequence_ids:
            notes.append('Secuencias no encontradas: ' + ', '.join(missing_sequence_ids))
    elif mode == StoryboardGenerationMode.SCENE_RANGE and payload.scene_start is not None and payload.scene_end is not None:
        estimated_scenes = len([scene for scene in scenes if payload.scene_start <= storyboard_service._scene_number(scene) <= payload.scene_end])
    elif mode == StoryboardGenerationMode.SINGLE_SCENE and payload.scene_start is not None:
        estimated_scenes = len([scene for scene in scenes if storyboard_service._scene_number(scene) == payload.scene_start])
    else:
        estimated_scenes = len(scenes)

    estimate = storyboard_credit_estimator_service.estimate_credits(
        mode=mode,
        estimated_scenes=estimated_scenes,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        include_coverage_shots=payload.include_coverage_shots,
        sequence_ids=payload.sequence_ids,
        scene_start=payload.scene_start,
        scene_end=payload.scene_end,
    )
    merged_notes = list(estimate.get("notes") or []) + notes
    return StoryboardCreditEstimateResponse(
        project_id=project_id,
        mode=str(estimate["mode"]),
        estimated_scenes=int(estimate["estimated_scenes"]),
        base_shots=int(estimate["base_shots"]),
        coverage_shots=int(estimate["coverage_shots"]),
        total_estimated_shots=int(estimate["total_estimated_shots"]),
        credits={k: int(v) for k, v in dict(estimate["credits"]).items()},
        plan_warning=estimate.get("plan_warning"),
        notes=[str(item) for item in merged_notes],
    )


@router.post("/{project_id}/storyboard/sequences/{sequence_id}/plan", response_model=SequenceStoryboardPlan)
async def plan_sequence_storyboard(
    project_id: str,
    sequence_id: str,
    payload: StoryboardSequencePlanRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> SequenceStoryboardPlan:
    await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    project = await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    analysis_data = await storyboard_service._get_analysis_payload(db, project)
    scenes_raw = analysis_data.get("scenes", [])
    script_text = project.script_text or ""
    _, scenes, _ = cid_script_scene_parser_service.parse_script(script_text)
    if not scenes:
        raise HTTPException(status_code=400, detail="No scenes parsed from script")
    seq_map = script_sequence_mapping_service.build_sequence_map(scenes, script_text)
    from schemas.cid_sequence_first_schema import resolve_sequence_entry
    entry = resolve_sequence_entry(seq_map, sequence_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Sequence {sequence_id} not found in script analysis")
    plan = prepare_sequence_storyboard(entry, project_id=project_id)
    if entry.suggested_shot_count != plan.estimated_shot_count:
        plan.warnings.append(
            f"Estimated shots ({entry.suggested_shot_count}) differs from planned shots ({plan.estimated_shot_count}). "
            f"The planner generated {plan.estimated_shot_count} shots based on content analysis; "
            f"the estimate ({entry.suggested_shot_count}) is a heuristic from scene grouping and is not a hard limit."
        )
    return plan


@router.post(
    "/{project_id}/storyboard/sequences/{sequence_id}/generate",
    response_model=StoryboardJobResponse,
)
async def generate_sequence_storyboard(
    project_id: str,
    sequence_id: str,
    payload: StoryboardGenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardJobResponse:
    if not sequence_id:
        raise HTTPException(
            status_code=400,
            detail="Storyboard generation requires a sequence_id. Run full script analysis first.",
        )
    result = await storyboard_service.generate_storyboard(
        db,
        project_id=project_id,
        tenant=tenant,
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id=sequence_id,
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        style_preset=payload.style_preset,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        overwrite=payload.overwrite,
        director_lens_id=payload.director_lens_id,
        montage_profile_id=payload.montage_profile_id,
        use_cinematic_intelligence=payload.use_cinematic_intelligence,
        include_coverage_shots=payload.include_coverage_shots,
        use_montage_intelligence=payload.use_montage_intelligence,
        validate_prompts=payload.validate_prompts,
        sheet_template=payload.sheet_template,
        workflow_profile=payload.workflow_profile,
        render_quality=payload.render_quality,
        model_family=payload.model_family,
        motion_ready=payload.motion_ready,
        image_edit_mode=payload.image_edit_mode,
        shots_per_sequence_mode=payload.shots_per_sequence_mode,
    )
    return StoryboardJobResponse(**{k: result[k] for k in StoryboardJobResponse.model_fields.keys()})


@router.post("/{project_id}/storyboard/comfyui/plan")
async def plan_storyboard_comfyui_pipeline(
    project_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        return build_storyboard_pipeline_plan(project_id=project_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{project_id}/storyboard/comfyui/render-dry-run")
async def storyboard_comfyui_render_dry_run(
    project_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        request_payload = dict(payload)
        request_payload["dry_run"] = True
        request_payload["render"] = False
        return comfyui_storyboard_render_service.render_storyboard_with_plan(
            project_id=project_id,
            payload=request_payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{project_id}/storyboard/render")
async def render_storyboard_contract(
    project_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        return comfyui_storyboard_render_service.render_storyboard_with_plan(
            project_id=project_id,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/storyboard", response_model=StoryboardListResponse)
async def get_storyboard(
    project_id: str,
    mode: str | None = Query(default=None),
    sequence_id: str | None = Query(default=None),
    scene_number: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardListResponse:
    shots, version = await storyboard_service.list_storyboard_shots(
        db,
        project_id=project_id,
        tenant=tenant,
        mode=mode,
        sequence_id=sequence_id,
        scene_number=scene_number,
    )
    return StoryboardListResponse(
        project_id=project_id,
        mode=mode or StoryboardGenerationMode.FULL_SCRIPT,
        sequence_id=sequence_id,
        scene_number=scene_number,
        version=version,
        shots=[StoryboardShotResponse.model_validate(shot, from_attributes=True) for shot in shots],
    )


@router.get("/{project_id}/storyboard/trace", response_model=StoryboardTraceSummary)
async def get_storyboard_trace_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardTraceSummary:
    return await storyboard_trace_service.get_project_trace_summary(
        db,
        project_id=project_id,
        tenant=tenant,
    )


@router.get("/{project_id}/storyboard/shots/{shot_id}/trace", response_model=StoryboardTraceRecord)
async def get_storyboard_shot_trace(
    project_id: str,
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardTraceRecord:
    return await storyboard_trace_service.get_shot_trace(
        db,
        project_id=project_id,
        shot_id=shot_id,
        tenant=tenant,
    )


@router.get("/{project_id}/storyboard/assets/{asset_id}/trace", response_model=StoryboardTraceRecord)
async def get_storyboard_asset_trace(
    project_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardTraceRecord:
    return await storyboard_trace_service.get_asset_trace(
        db,
        project_id=project_id,
        asset_id=asset_id,
        tenant=tenant,
    )


def _resolve_media_from_shot_metadata(shot: StoryboardShot) -> str | None:
    meta = storyboard_frame_service.decode_metadata(getattr(shot, "metadata_json", None))
    for key in ("rendered_image_path", "output_path", "image_path", "storage_path"):
        candidate = meta.get(key)
        if isinstance(candidate, str) and candidate.strip():
            resolved = storyboard_frame_service.resolve_asset_thumbnail_path(
                SimpleNamespace(canonical_path=candidate, content_ref=None, relative_path=""),
                {"storage_path": candidate, "relative_path": None},
            ) or storyboard_frame_service.resolve_asset_image_path(
                SimpleNamespace(canonical_path=candidate, content_ref=None, relative_path="", mime_type=None, file_name=None),
                {"storage_path": candidate, "relative_path": None},
            )
            if resolved:
                return resolved
    return None


@router.get("/{project_id}/storyboard/shots/{shot_id}/image")
async def get_storyboard_shot_image(
    project_id: str,
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    shot, asset = await _get_storyboard_shot_and_asset(
        db,
        project_id=project_id,
        shot_id=shot_id,
        tenant=tenant,
    )
    if asset is not None:
        metadata = storyboard_frame_service.decode_metadata(getattr(asset, "metadata_json", None))
        image_path = storyboard_frame_service.resolve_asset_image_path(asset, metadata)
        if image_path:
            return _file_response_for_storyboard_media(
                image_path,
                getattr(asset, "mime_type", None),
                getattr(asset, "file_name", None) or f"storyboard-shot-{shot.id}",
            )

    fallback_path = _resolve_media_from_shot_metadata(shot)
    if fallback_path:
        return _file_response_for_storyboard_media(fallback_path, None, f"storyboard-shot-{shot.id}")

    raise HTTPException(status_code=404, detail="Storyboard image not found")


@router.get("/{project_id}/storyboard/shots/{shot_id}/thumbnail")
async def get_storyboard_shot_thumbnail(
    project_id: str,
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    shot, asset = await _get_storyboard_shot_and_asset(
        db,
        project_id=project_id,
        shot_id=shot_id,
        tenant=tenant,
    )
    if asset is not None:
        metadata = storyboard_frame_service.decode_metadata(getattr(asset, "metadata_json", None))
        thumbnail_path = storyboard_frame_service.resolve_asset_thumbnail_path(asset, metadata)
        if thumbnail_path is None:
            thumbnail_path = storyboard_frame_service.resolve_asset_image_path(asset, metadata)
        if thumbnail_path:
            return _file_response_for_storyboard_media(
                thumbnail_path,
                mimetypes.guess_type(thumbnail_path)[0] or getattr(asset, "mime_type", None),
                Path(thumbnail_path).name,
            )

    fallback_path = _resolve_media_from_shot_metadata(shot)
    if fallback_path:
        return _file_response_for_storyboard_media(fallback_path, None, Path(fallback_path).name)

    raise HTTPException(status_code=404, detail="Storyboard thumbnail not found")


@router.get("/{project_id}/storyboard/sequences/{sequence_id}", response_model=StoryboardSequenceDetailResponse)
async def get_storyboard_sequence_detail(
    project_id: str,
    sequence_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardSequenceDetailResponse:
    sequence, shots = await storyboard_service.get_sequence_storyboard(
        db,
        project_id=project_id,
        sequence_id=sequence_id,
        tenant=tenant,
    )
    return StoryboardSequenceDetailResponse(
        sequence=StoryboardSequenceResponse(**sequence),
        shots=[StoryboardShotResponse.model_validate(shot, from_attributes=True) for shot in shots],
    )


@router.post(
    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate",
    response_model=StoryboardGenerationAuditResponse,
)
async def regenerate_storyboard_sequence(
    project_id: str,
    sequence_id: str,
    payload: StoryboardGenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardGenerationAuditResponse:
    result = await storyboard_service.generate_storyboard(
        db,
        project_id=project_id,
        tenant=tenant,
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id=sequence_id,
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        style_preset=payload.style_preset,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        overwrite=True,
        include_coverage_shots=payload.include_coverage_shots,
        shots_per_sequence_mode=payload.shots_per_sequence_mode,
    )
    return StoryboardGenerationAuditResponse(
        job_id=result["job_id"],
        mode=result["mode"],
        sequence_id=result.get("sequence_id"),
        scene_start=None,
        scene_end=None,
        style_preset=payload.style_preset,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        overwrite=True,
        version=result["version"],
        generated_assets=result.get("generated_assets", []),
        total_shots=result.get("total_shots", 0),
        total_scenes=result.get("total_scenes", 0),
        render_jobs=result.get("render_jobs", []),
        render_errors=result.get("render_errors", []),
        created_at=result["created_at"],
    )


@router.post(
    "/{project_id}/storyboard/shots/{shot_id}/feedback",
    response_model=StoryboardRevisionResult,
)
async def submit_shot_director_feedback(
    project_id: str,
    shot_id: str,
    payload: ShotFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardRevisionResult:
    return await storyboard_service.revise_storyboard_shot_with_feedback(
        db,
        project_id=project_id,
        shot_id=shot_id,
        feedback=payload,
        tenant=tenant,
    )


@router.post(
    "/{project_id}/storyboard/shots/{shot_id}/regenerate",
    response_model=StoryboardRegenerateShotsResponse,
)
async def regenerate_storyboard_shot(
    project_id: str,
    shot_id: str,
    payload: StoryboardShotRegenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardRegenerateShotsResponse:
    result = await storyboard_service.regenerate_storyboard_shot_from_validation(
        db,
        project_id=project_id,
        shot_id=shot_id,
        tenant=tenant,
        threshold=payload.threshold,
        include_unvalidated=payload.include_unvalidated,
    )
    return StoryboardRegenerateShotsResponse(**result)


@router.post(
    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate-failed",
    response_model=StoryboardRegenerateShotsResponse,
)
async def regenerate_failed_storyboard_sequence_shots(
    project_id: str,
    sequence_id: str,
    payload: StoryboardFailedRegenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardRegenerateShotsResponse:
    result = await storyboard_service.regenerate_failed_storyboard_shots(
        db,
        project_id=project_id,
        sequence_id=sequence_id,
        tenant=tenant,
        threshold=payload.threshold,
        include_unvalidated=payload.include_unvalidated,
    )
    return StoryboardRegenerateShotsResponse(**result)


@router.post(
    "/{project_id}/storyboard/sequences/{sequence_id}/feedback",
    response_model=StoryboardRevisionPlan,
)
async def submit_sequence_director_feedback(
    project_id: str,
    sequence_id: str,
    payload: SequenceFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StoryboardRevisionPlan:
    if payload.apply_to not in ("selected_shots", "all_sequence_shots"):
        raise HTTPException(status_code=400, detail="apply_to must be 'selected_shots' or 'all_sequence_shots'")

    from sqlalchemy import select
    from models.storyboard import StoryboardShot

    query = select(StoryboardShot).where(
        StoryboardShot.project_id == project_id,
        StoryboardShot.sequence_id == sequence_id,
        StoryboardShot.organization_id == tenant.organization_id,
        StoryboardShot.is_active.is_(True),
    )
    if payload.apply_to == "selected_shots" and payload.shot_ids:
        query = query.where(StoryboardShot.id.in_(payload.shot_ids))
    result = await db.execute(query)
    shots = list(result.scalars().all())

    if not shots:
        raise HTTPException(status_code=404, detail="No shots found for feedback")

    results: list[StoryboardRevisionResult] = []
    first_plan: StoryboardRevisionPlan | None = None

    from schemas.cid_director_feedback_schema import (
        FeedbackCategory,
        FeedbackSeverity,
        ShotFeedbackRequest as InnerShotFeedbackRequest,
    )

    for shot in shots:
        shot_feedback = InnerShotFeedbackRequest(
            note_text=payload.note_text,
            category=FeedbackCategory(payload.note_text) if hasattr(FeedbackCategory, payload.note_text) else FeedbackCategory.other,
            severity=FeedbackSeverity.minor,
            preserve_original_logic=payload.preserve_original_logic,
        )
        try:
            revision_result = await storyboard_service.revise_storyboard_shot_with_feedback(
                db,
                project_id=project_id,
                shot_id=shot.id,
                feedback=shot_feedback,
                tenant=tenant,
            )
            results.append(revision_result)
            if first_plan is None:
                first_plan = revision_result.revision_plan
        except Exception:
            pass

    if not first_plan:
        raise HTTPException(status_code=422, detail="Could not process feedback for any shot")

    combined_plan = first_plan
    combined_plan.qa_checklist.append(f"VERIFICAR: Feedback aplicado a {len(results)}/{len(shots)} shots de la secuencia {sequence_id}")
    return combined_plan


@router.get(
    "/{project_id}/storyboard/shots/{shot_id}/revisions",
    response_model=list[dict[str, Any]],
)
async def get_shot_revision_history(
    project_id: str,
    shot_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[dict[str, Any]]:
    from sqlalchemy import select
    from models.storyboard import StoryboardShot

    result = await db.execute(
        select(StoryboardShot).where(
            StoryboardShot.id == shot_id,
            StoryboardShot.project_id == project_id,
            StoryboardShot.organization_id == tenant.organization_id,
        )
    )
    shot = result.scalar_one_or_none()
    if shot is None:
        raise HTTPException(status_code=404, detail="Shot not found")

    import json
    metadata_raw: dict[str, Any] = {}
    if shot.metadata_json:
        try:
            metadata_raw = json.loads(shot.metadata_json) if isinstance(shot.metadata_json, str) else dict(shot.metadata_json)
        except (json.JSONDecodeError, TypeError):
            metadata_raw = {}
    return metadata_raw.get("revision_history", [])


@router.get(
    "/{project_id}/storyboard/sequences/{sequence_id}/export/zip",
)
async def export_sequence_storyboard_zip(
    project_id: str,
    sequence_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> Response:
    import json
    from datetime import datetime, timezone
    sequence, shots = await storyboard_service.get_sequence_storyboard(
        db,
        project_id=project_id,
        sequence_id=sequence_id,
        tenant=tenant,
    )

    if not shots:
        raise HTTPException(
            status_code=404,
            detail=f"No shots found for sequence {sequence_id}"
        )

    from services.presentation_service import presentation_service
    import io
    import zipfile
    from pathlib import Path
    
    try:
        project = await storyboard_service._get_project_for_tenant(
            db,
            project_id=project_id,
            tenant=tenant,
        )
    except Exception:
        project = None

    sorted_shots = sorted(
        list(shots),
        key=lambda s: (
            int(getattr(s, "sequence_order", 0) or 0),
            int(getattr(s, "scene_number", 0) or 0),
            str(getattr(s, "id", "")),
        ),
    )

    zip_buffer = io.BytesIO()
    exported_at = datetime.now(timezone.utc).isoformat()
    manifest_shots: list[dict[str, Any]] = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        added_filenames = set()
        for shot in sorted_shots:
            if not getattr(shot, "asset_id", None):
                manifest_shots.append(
                    {
                        "shot_id": str(getattr(shot, "id", "")),
                        "sequence_order": int(getattr(shot, "sequence_order", 0) or 0),
                        "scene_number": getattr(shot, "scene_number", None),
                        "asset_id": None,
                        "image_filename": None,
                        "render_status": "no_asset",
                        "validation_score": None,
                        "style_preset": str(getattr(shot, "visual_mode", "") or ""),
                        "prompt_brief": str(getattr(shot, "narrative_text", "") or "")[:180],
                        "sequence_id": str(getattr(shot, "sequence_id", sequence_id) or sequence_id),
                        "file_path": None,
                    }
                )
                continue

            try:
                payload = await presentation_service.get_asset_preview_payload(
                    db,
                    project_id=project_id,
                    asset_id=getattr(shot, "asset_id", None),
                    tenant=tenant,
                )
            except Exception:
                continue

            if payload.get("kind") != "file":
                continue

            file_path_str = payload.get("path")
            if not file_path_str:
                continue

            file_path = Path(file_path_str)
            if not file_path.is_file():
                manifest_shots.append(
                    {
                        "shot_id": str(getattr(shot, "id", "")),
                        "sequence_order": int(getattr(shot, "sequence_order", 0) or 0),
                        "scene_number": getattr(shot, "scene_number", None),
                        "asset_id": str(getattr(shot, "asset_id", "")),
                        "image_filename": None,
                        "render_status": "missing_file",
                        "validation_score": None,
                        "style_preset": str(getattr(shot, "visual_mode", "") or ""),
                        "prompt_brief": str(getattr(shot, "narrative_text", "") or "")[:180],
                        "sequence_id": str(getattr(shot, "sequence_id", sequence_id) or sequence_id),
                        "file_path": None,
                    }
                )
                continue

            file_bytes = file_path.read_bytes()
            original_filename = payload.get("filename") or file_path.name
            suffix = Path(original_filename).suffix or ".webp"

            clean_sequence_order = str(shot.sequence_order).zfill(2)
            zip_filename = f"shot_{clean_sequence_order}{suffix}"

            counter = 1
            base_zip_filename = f"shot_{clean_sequence_order}"
            while zip_filename in added_filenames:
                zip_filename = f"{base_zip_filename}_{counter}{suffix}"
                counter += 1

            added_filenames.add(zip_filename)
            zip_file.writestr(zip_filename, file_bytes)
            metadata = getattr(shot, "metadata_json", None)
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except Exception:
                    metadata = {}
            if not isinstance(metadata, dict):
                metadata = {}
            validation_score = metadata.get("validation_score")
            if validation_score is None and isinstance(metadata.get("validation_result"), dict):
                validation_score = metadata.get("validation_result", {}).get("overall_match_score")
            manifest_shots.append(
                {
                    "shot_id": str(getattr(shot, "id", "")),
                    "sequence_order": int(getattr(shot, "sequence_order", 0) or 0),
                    "scene_number": getattr(shot, "scene_number", None),
                    "asset_id": str(getattr(shot, "asset_id", "")),
                    "image_filename": zip_filename,
                    "render_status": "completed",
                    "validation_score": validation_score,
                    "style_preset": str(getattr(shot, "visual_mode", None) or metadata.get("normalized_style_preset") or ""),
                    "prompt_brief": str(getattr(shot, "narrative_text", "") or "")[:180],
                    "sequence_id": str(getattr(shot, "sequence_id", sequence_id) or sequence_id),
                    "file_path": str(file_path),
                }
            )

    if not added_filenames:
        raise HTTPException(
            status_code=404,
            detail="No physical render assets found to export for this sequence."
        )

    manifest_shots = sorted(
        manifest_shots,
        key=lambda item: (
            int(item.get("sequence_order") or 0),
            int(item.get("scene_number") or 0),
            str(item.get("shot_id") or ""),
        ),
    )

    manifest_payload = storyboard_pdf_export_service.build_manifest(
        project_id=project_id,
        sequence_id=str(sequence.get("sequence_id") or sequence_id),
        exported_at=exported_at,
        shots=[
            {
                key: value
                for key, value in item.items()
                if key != "file_path"
            }
            for item in manifest_shots
        ],
    )

    pdf_bytes = storyboard_pdf_export_service.render_contact_sheet_pdf(
        project_name=str(getattr(project, "name", "Project")),
        sequence_id=str(sequence.get("sequence_id") or sequence_id),
        exported_at=exported_at,
        shots=manifest_shots,
    )
    filmstrip_png = storyboard_pdf_export_service.build_storyboard_filmstrip_image(
        shots=manifest_shots,
    )

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(
            "storyboard_manifest.json",
            json.dumps(manifest_payload, ensure_ascii=False, indent=2, default=str),
        )
        zip_file.writestr("storyboard_contact_sheet.pdf", pdf_bytes)
        zip_file.writestr("storyboard_filmstrip.png", filmstrip_png)

    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()

    canonical_sequence_id = str(sequence.get("sequence_id") or sequence_id)
    safe_sequence_id = "".join(c if c.isalnum() else "_" for c in canonical_sequence_id)
    zip_filename = f"sequence_{safe_sequence_id}_storyboard.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
    )


@router.post("/{project_id}/storyboard/repair-assets")
async def repair_storyboard_shot_assets(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    await storyboard_service._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    result = await storyboard_asset_repair_service.repair_storyboard_shot_asset_links(
        db, project_id=project_id, tenant=tenant
    )
    return result
