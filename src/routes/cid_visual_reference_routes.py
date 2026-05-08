from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.cid_script_to_prompt_schema import PromptSpec, ScriptToPromptRunResponse
from schemas.cid_visual_reference_schema import (
    DirectorVisualReferenceRequest,
    EnrichedVisualIntent,
    ScriptVisualAlignmentRequest,
    ScriptVisualAlignmentResult,
    StyleReferenceProfile,
    VisualReferenceAnalysisResult,
)
from services.cid_script_to_prompt_pipeline_service import run_script_to_prompt_pipeline
from services.prompt_construction_service import prompt_construction_service
from services.script_visual_alignment_service import script_visual_alignment_service
from services.visual_reference_analysis_service import visual_reference_analysis_service


router = APIRouter(prefix="/api/cid/visual-reference", tags=["cid-visual-reference"])


@router.post("/analyze", response_model=VisualReferenceAnalysisResult)
async def analyze_visual_reference(payload: DirectorVisualReferenceRequest) -> VisualReferenceAnalysisResult:
    return visual_reference_analysis_service.analyze(payload)


@router.post("/apply-to-scene", response_model=PromptSpec)
async def apply_visual_reference_to_scene(
    payload: DirectorVisualReferenceRequest,
    script_text: str = "",
    output_type: str = "storyboard_frame",
    style_preset: str = "premium_cinematic_saas",
) -> PromptSpec:
    result = visual_reference_analysis_service.analyze(payload)
    profile = result.profile
    prompt = prompt_construction_service.build_prompt_spec(
        intent=None,
        style_preset=style_preset,
        visual_reference_profile=profile,
    )
    return prompt


@router.post("/apply-to-storyboard", response_model=ScriptToPromptRunResponse)
async def apply_visual_reference_to_storyboard(
    payload: DirectorVisualReferenceRequest,
    script_text: str = "",
    output_type: str = "storyboard_frame",
    max_scenes: int | None = 3,
    style_preset: str = "premium_cinematic_saas",
) -> ScriptToPromptRunResponse:
    result = visual_reference_analysis_service.analyze(payload)
    return await run_script_to_prompt_pipeline(
        script_text=script_text or "INT. ESTUDIO - DIA\nUna escena cinematografica de prueba para aplicar referencia visual del director.",
        output_type=output_type,
        max_scenes=max_scenes,
        style_preset=style_preset,
        visual_reference_profile=result.profile,
    )


@router.get("/profiles/{project_id}", response_model=list[StyleReferenceProfile])
async def list_visual_reference_profiles(project_id: str) -> list[StyleReferenceProfile]:
    return []


@router.post("/align-with-script", response_model=ScriptVisualAlignmentResult)
async def align_visual_reference_with_script(
    payload: ScriptVisualAlignmentRequest,
) -> ScriptVisualAlignmentResult:
    result, _ = script_visual_alignment_service.align(payload)
    return result


@router.post("/enriched-intent", response_model=EnrichedVisualIntent)
async def build_enriched_visual_intent(
    payload: ScriptVisualAlignmentRequest,
) -> EnrichedVisualIntent:
    _, enriched = script_visual_alignment_service.align(payload)
    return enriched
