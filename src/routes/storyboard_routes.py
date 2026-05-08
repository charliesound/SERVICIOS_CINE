from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.shot_schema import StoryboardShotListResponse, StoryboardShotResponse
from schemas.storyboard_schema import (
    StoryboardGenerateRequest,
    StoryboardGenerationAuditResponse,
    StoryboardJobResponse,
    StoryboardListResponse,
    StoryboardOptionsResponse,
    StoryboardSequenceDetailResponse,
    StoryboardSequenceResponse,
)
from services.comfyui_model_inventory_service import ComfyUIInventoryError
from services.comfyui_pipeline_builder_service import build_storyboard_pipeline_plan
from services.comfyui_storyboard_render_service import comfyui_storyboard_render_service
from schemas.cid_sequence_first_schema import (
    ScriptSequenceMapEntry,
    SequenceStoryboardPlan,
)
from schemas.storyboard_schema import StoryboardSequencePlanRequest, StoryboardSequencePlanResponse
from services.cid_script_to_prompt_pipeline_service import (
    analyze_full_script,
    prepare_sequence_storyboard,
)
from services.cid_script_scene_parser_service import cid_script_scene_parser_service
from services.script_sequence_mapping_service import script_sequence_mapping_service
from services.storyboard_service import storyboard_service, StoryboardGenerationMode


router = APIRouter(prefix="/api/projects", tags=["storyboard"])


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
        use_montage_intelligence=payload.use_montage_intelligence,
        validate_prompts=payload.validate_prompts,
    )
    return StoryboardJobResponse(**{k: result[k] for k in StoryboardJobResponse.model_fields.keys()})


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
    entry = next((s for s in seq_map.sequences if s.sequence_id == sequence_id), None)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Sequence {sequence_id} not found in script analysis")
    plan = prepare_sequence_storyboard(entry, project_id=project_id)
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
        use_montage_intelligence=payload.use_montage_intelligence,
        validate_prompts=payload.validate_prompts,
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
    )
    return StoryboardGenerationAuditResponse(
        job_id=result["job_id"],
        mode=result["mode"],
        sequence_id=sequence_id,
        scene_start=None,
        scene_end=None,
        style_preset=payload.style_preset,
        shots_per_scene=max(1, min(payload.shots_per_scene, 8)),
        overwrite=True,
        version=result["version"],
        generated_assets=result.get("generated_assets", []),
        created_at=result["created_at"],
    )
