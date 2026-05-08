from __future__ import annotations

import logging

from schemas.cid_script_to_prompt_schema import (
    PromptSpec,
    ScriptScene,
    ScriptSequence,
    ScriptToPromptRunResponse,
)
from schemas.cid_visual_reference_schema import (
    ScriptVisualAlignmentRequest,
    StyleReferenceProfile,
)
from services.cid_script_scene_parser_service import cid_script_scene_parser_service
from services.cinematic_intent_service import cinematic_intent_service
from services.continuity_memory_service import continuity_memory_service
from services.prompt_construction_service import prompt_construction_service
from services.semantic_prompt_validation_service import semantic_prompt_validation_service
from services.script_visual_alignment_service import script_visual_alignment_service
from services.visual_qc_service import visual_qc_service


logger = logging.getLogger(__name__)


async def run_script_to_prompt_pipeline(
    script_text: str,
    output_type: str = "storyboard_frame",
    max_scenes: int | None = 5,
    scene_numbers: list[int] | None = None,
    style_preset: str = "premium_cinematic_saas",
    use_llm: bool = True,
    director_lens_id: str | None = "adaptive_auteur_fusion",
    montage_profile_id: str | None = "adaptive_montage",
    allow_director_reference_names: bool = False,
    visual_reference_profile: StyleReferenceProfile | None = None,
) -> ScriptToPromptRunResponse:
    warnings: list[str] = []
    if not (script_text or "").strip():
        return ScriptToPromptRunResponse(
            sequences=[],
            scenes=[],
            intents=[],
            prompts=[],
            validations=[],
            qa=[],
            status="failed",
            warnings=["script_text_required"],
        )

    sequences, scenes, parser_warnings = cid_script_scene_parser_service.parse_script(script_text)
    warnings.extend(parser_warnings)

    if scene_numbers:
        scene_number_set = {int(number) for number in scene_numbers}
        scenes = [scene for scene in scenes if scene.scene_number in scene_number_set]
        sequences = _filter_sequences(sequences, scene_number_set)
        if not scenes:
            warnings.append("scene_number_filter_removed_all_scenes")

    if max_scenes is not None and max_scenes > 0:
        scenes = scenes[:max_scenes]
        allowed_numbers = {scene.scene_number for scene in scenes}
        sequences = _filter_sequences(sequences, allowed_numbers)

    if use_llm:
        warnings.append("llm_enrichment_not_applied_in_v1_using_heuristic_pipeline")
        logger.warning("Script-to-prompt pipeline running in heuristic mode; LLM enrichment is not enabled in v1.")

    if not scenes:
        return ScriptToPromptRunResponse(
            sequences=sequences,
            scenes=[],
            intents=[],
            prompts=[],
            validations=[],
            qa=[],
            status="failed",
            warnings=list(dict.fromkeys(warnings + ["no_scenes_available_after_filtering"])),
        )

    project_memory = continuity_memory_service.build_project_visual_bible(scenes)
    intents = []
    prompts = []
    validations = []
    qa_results = []
    alignment_results: list[dict] = []
    enriched_intents: list[dict] = []

    for scene in scenes:
        continuity_anchors = continuity_memory_service.build_continuity_anchors(scene, project_memory)
        intent = cinematic_intent_service.build_intent(
            scene,
            output_type,
            continuity_anchors=continuity_anchors,
            director_lens_id=director_lens_id,
            montage_profile_id=montage_profile_id,
            allow_director_reference_names=allow_director_reference_names,
        )

        enriched = None
        if visual_reference_profile is not None:
            try:
                align_request = ScriptVisualAlignmentRequest(
                    project_id=visual_reference_profile.project_id,
                    scene_id=scene.scene_id,
                    script_excerpt=scene.raw_text,
                    reference_profile=visual_reference_profile,
                )
                align_result, enriched = script_visual_alignment_service.align(align_request)
                alignment_results.append(align_result.model_dump())
                enriched_intents.append(enriched.model_dump())
                if align_result.warnings:
                    warnings.extend(align_result.warnings)
            except Exception as exc:
                logger.warning("Visual reference alignment failed for scene %s: %s", scene.scene_id, exc)
                alignment_results.append({"error": str(exc), "scene_id": scene.scene_id})

        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset=style_preset,
            allow_director_reference_names=allow_director_reference_names,
            visual_reference_profile=visual_reference_profile,
            enriched_intent=enriched,
        )
        validation = semantic_prompt_validation_service.validate(prompt, intent)
        prompt.validation_status = "valid" if validation.is_valid else "invalid"
        prompt.validation_errors = validation.errors
        qa = visual_qc_service.evaluate_prompt(prompt, validation)

        intents.append(intent)
        prompts.append(prompt)
        validations.append(validation)
        qa_results.append(qa)

    status = "completed" if prompts else "failed"
    return ScriptToPromptRunResponse(
        sequences=sequences,
        scenes=scenes,
        intents=intents,
        prompts=prompts,
        validations=validations,
        qa=qa_results,
        alignment_results=alignment_results,
        enriched_intents=enriched_intents,
        status=status,
        warnings=list(dict.fromkeys(warnings)),
    )


def _filter_sequences(sequences: list[ScriptSequence], allowed_numbers: set[int]) -> list[ScriptSequence]:
    filtered: list[ScriptSequence] = []
    for sequence in sequences:
        scene_numbers = [number for number in sequence.scene_numbers if number in allowed_numbers]
        if not scene_numbers:
            continue
        filtered.append(
            ScriptSequence(
                sequence_id=sequence.sequence_id,
                sequence_number=sequence.sequence_number,
                title=sequence.title,
                summary=sequence.summary,
                scene_numbers=scene_numbers,
                dramatic_purpose=sequence.dramatic_purpose,
                emotional_arc=sequence.emotional_arc,
                continuity_notes=sequence.continuity_notes,
            )
        )
    return filtered
