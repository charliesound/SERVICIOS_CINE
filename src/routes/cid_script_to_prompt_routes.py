from __future__ import annotations

from fastapi import APIRouter

from schemas.cid_script_to_prompt_schema import (
    CinematicIntent,
    CinematicIntentRequest,
    DirectorialIntent,
    DirectorialIntentRequest,
    DirectorLensChooseRequest,
    DirectorLensDecision,
    DirectorLensProfile,
    EditorialBeat,
    EditorialBeatsRequest,
    MontageIntent,
    MontageIntentRequest,
    PromptConstructionRequest,
    PromptSpec,
    PromptValidationRequest,
    ScriptParseRequest,
    ScriptParseResponse,
    ScriptToPromptRunRequest,
    ScriptToPromptRunResponse,
    SemanticPromptValidationResult,
    ShotEditorialPurpose,
    ShotEditorialPurposeRequest,
)
from services.cid_script_scene_parser_service import cid_script_scene_parser_service
from services.cid_script_to_prompt_pipeline_service import run_script_to_prompt_pipeline
from services.cinematic_intent_service import cinematic_intent_service
from services.continuity_memory_service import continuity_memory_service
from services.director_lens_service import director_lens_service
from services.directorial_intent_service import directorial_intent_service
from services.montage_intelligence_service import montage_intelligence_service
from services.prompt_construction_service import prompt_construction_service
from services.semantic_prompt_validation_service import semantic_prompt_validation_service


router = APIRouter(prefix="/api/cid/script-to-prompt", tags=["cid-script-to-prompt"])


@router.post("/run", response_model=ScriptToPromptRunResponse)
async def run_script_to_prompt(payload: ScriptToPromptRunRequest) -> ScriptToPromptRunResponse:
    return await run_script_to_prompt_pipeline(
        script_text=payload.script_text,
        output_type=payload.output_type,
        max_scenes=payload.max_scenes,
        scene_numbers=payload.scene_numbers,
        style_preset=payload.style_preset,
        use_llm=payload.use_llm,
        director_lens_id=payload.director_lens_id,
        montage_profile_id=payload.montage_profile_id,
        allow_director_reference_names=payload.allow_director_reference_names,
    )


@router.post("/parse", response_model=ScriptParseResponse)
async def parse_script(payload: ScriptParseRequest) -> ScriptParseResponse:
    sequences, scenes, warnings = cid_script_scene_parser_service.parse_script(payload.script_text)
    if payload.max_scenes is not None and payload.max_scenes > 0:
        scenes = scenes[:payload.max_scenes]
        allowed_numbers = {scene.scene_number for scene in scenes}
        sequences = [sequence for sequence in sequences if any(number in allowed_numbers for number in sequence.scene_numbers)]
    return ScriptParseResponse(sequences=sequences, scenes=scenes, warnings=warnings)


@router.post("/intent", response_model=CinematicIntent)
async def build_intent(payload: CinematicIntentRequest) -> CinematicIntent:
    continuity_anchors = continuity_memory_service.build_continuity_anchors(payload.scene)
    return cinematic_intent_service.build_intent(
        payload.scene,
        payload.output_type,
        continuity_anchors=continuity_anchors,
        director_lens_id=payload.director_lens_id,
        montage_profile_id=payload.montage_profile_id,
    )


@router.post("/prompt", response_model=PromptSpec)
async def build_prompt(payload: PromptConstructionRequest) -> PromptSpec:
    return prompt_construction_service.build_prompt_spec(
        payload.intent,
        allow_director_reference_names=payload.allow_director_reference_names,
    )


@router.post("/validate", response_model=SemanticPromptValidationResult)
async def validate_prompt(payload: PromptValidationRequest) -> SemanticPromptValidationResult:
    return semantic_prompt_validation_service.validate(payload.prompt, payload.intent)


@router.get("/director-lenses", response_model=list[DirectorLensProfile])
async def list_director_lenses() -> list[DirectorLensProfile]:
    return director_lens_service.list_profiles()


@router.get("/director-lenses/{lens_id}", response_model=DirectorLensProfile)
async def get_director_lens(lens_id: str) -> DirectorLensProfile:
    return director_lens_service.get_profile(lens_id)


@router.post("/director-lenses/choose", response_model=DirectorLensDecision)
async def choose_director_lens(payload: DirectorLensChooseRequest) -> DirectorLensDecision:
    return director_lens_service.choose_lens_for_scene(payload.scene, payload.requested_lens_id)


@router.post("/directorial-intent", response_model=DirectorialIntent)
async def build_directorial_intent(payload: DirectorialIntentRequest) -> DirectorialIntent:
    lens_decision = director_lens_service.choose_lens_for_scene(payload.scene, payload.requested_lens_id)
    return directorial_intent_service.build_directorial_intent(
        payload.scene,
        payload.cinematic_intent,
        lens_decision,
    )


@router.get("/montage-profiles", response_model=list[dict])
async def list_montage_profiles() -> list[dict]:
    return montage_intelligence_service.list_profiles()


@router.post("/montage-intent", response_model=MontageIntent)
async def build_montage_intent(payload: MontageIntentRequest) -> MontageIntent:
    return montage_intelligence_service.build_montage_intent(
        payload.scene,
        payload.cinematic_intent,
        payload.directorial_intent,
        requested_profile_id=payload.requested_profile_id,
    )


@router.post("/editorial-beats", response_model=list[EditorialBeat])
async def build_editorial_beats(payload: EditorialBeatsRequest) -> list[EditorialBeat]:
    return montage_intelligence_service.build_editorial_beats(payload.scene)


@router.post("/shot-editorial-purpose", response_model=ShotEditorialPurpose)
async def build_shot_editorial_purpose(payload: ShotEditorialPurposeRequest) -> ShotEditorialPurpose:
    return montage_intelligence_service.build_shot_editorial_purpose(
        payload.scene,
        shot_order=payload.shot_order,
        shot_type=payload.shot_type,
        montage_intent=payload.montage_intent,
        previous_shot_type=payload.previous_shot_type,
        next_shot_type=payload.next_shot_type,
    )
