from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

#!/usr/bin/env python3
"""
Smoke test: Script-Visual Alignment Contract

Verifies that:
1. script_visual_alignment_service.align() returns result + enriched intent
2. prompt_construction_service.build_prompt_spec() accepts enriched_intent
3. cid_script_to_prompt_pipeline_service runs with visual_reference_profile
4. EnrichedVisualIntent.to_enriched_prompt_block() produces expected output
5. Alignment data flows end-to-end without crashing

Run:  python -m scripts.smoke_cid_script_visual_alignment_contract
"""

import json
import sys


def step(label: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print("=" * 60)
    print("SMOKE: Script-Visual Alignment Contract")
    print("=" * 60)

    # 1. ScriptVisualAlignmentService.align()
    print("\n[1] ScriptVisualAlignmentService.align()")
    from schemas.cid_visual_reference_schema import (
        EnrichedVisualIntent,
        ScriptVisualAlignmentRequest,
        ScriptVisualAlignmentResult,
        StyleReferenceProfile,
    )
    from services.script_visual_alignment_service import script_visual_alignment_service

    request = ScriptVisualAlignmentRequest(
        script_excerpt="INT. ESTUDIO - NOCHE\nUn director revisa la escena. Atmósfera tensa y dramática.",
        reference_profile=StyleReferenceProfile(
            visual_summary="Warm amber tones with soft dramatic lighting",
            palette_description="Amber, charcoal, deep blues",
            lighting_description="Soft directional with dramatic shadows",
            atmosphere_description="Intimate and tense",
            composition_description="Rule of thirds",
            transferable_traits=["warm palette", "dramatic shadows", "intimate framing"],
            non_transferable_traits=["specific character identity", "logos"],
        ),
    )
    result, enriched = script_visual_alignment_service.align(request)
    step("align returns ScriptVisualAlignmentResult", isinstance(result, ScriptVisualAlignmentResult))
    step("align returns EnrichedVisualIntent", isinstance(enriched, EnrichedVisualIntent))
    step(f"alignment_score is float: {result.alignment_score}", isinstance(result.alignment_score, float))
    step(f"matching_elements: {result.matching_elements}", len(result.matching_elements) > 0)
    step("recommended_visual_direction is non-empty", bool(result.recommended_visual_direction))
    step("safe_constraints includes identity warning", any("copy" in c.lower() for c in result.safe_constraints))

    # 2. EnrichedVisualIntent fields
    print("\n[2] EnrichedVisualIntent structure")
    step("merged_intent_summary is non-empty", bool(enriched.merged_intent_summary))
    step("scene_requirements is list", isinstance(enriched.scene_requirements, list))
    step("non_negotiable_story_elements is non-empty", len(enriched.non_negotiable_story_elements) > 0)
    step("non_negotiable_visual_elements is non-empty", len(enriched.non_negotiable_visual_elements) > 0)
    step("qa_checklist includes VERIFICAR items", all("VERIFICAR" in item for item in enriched.qa_checklist))
    step("prompt_guidance is non-empty", bool(enriched.prompt_guidance))
    step("negative_guidance is non-empty", bool(enriched.negative_guidance))

    # 3. to_enriched_prompt_block()
    print("\n[3] EnrichedVisualIntent.to_enriched_prompt_block()")
    block = enriched.to_enriched_prompt_block()
    step("block contains STORY TRUTH", "STORY TRUTH" in block)
    step("block contains VISUAL REFERENCE GUIDANCE", "VISUAL REFERENCE GUIDANCE" in block)
    step("block contains ALIGNMENT DECISION", "ALIGNMENT DECISION" in block)
    step("block contains NEGATIVE / SAFETY GUIDANCE", "NEGATIVE / SAFETY GUIDANCE" in block)

    # 4. PromptConstructionService with enriched_intent
    print("\n[4] PromptConstructionService.build_prompt_spec() with enriched_intent")
    from schemas.cid_script_to_prompt_schema import CinematicIntent
    from services.prompt_construction_service import prompt_construction_service

    intent = CinematicIntent(
        intent_id="smoke_intent_001",
        scene_id="smoke_scene_001",
        output_type="storyboard_frame",
        subject="Un director revisando un storyboard",
        action="señala un panel en la pantalla",
        environment="sala de proyección oscura",
        dramatic_intent="decisión creativa",
        framing="medio",
        shot_size="MS",
        camera_angle="normal",
        lens="50mm",
        lighting="suave direccional",
        color_palette="carbón y ámber",
        composition="tercios",
        movement="estática",
        mood="profesional intensa",
        required_elements=["pantalla", "storyboard", "director", "sala oscura"],
        forbidden_elements=["oficina genérica", "luz fluorescente"],
        continuity_anchors=["misma localización", "misma hora"],
    )
    prompt = prompt_construction_service.build_prompt_spec(
        intent,
        style_preset="premium_cinematic_saas",
        enriched_intent=enriched,
    )
    step("build_prompt_spec returns PromptSpec", prompt is not None)
    step("positive_prompt is non-empty", bool(prompt.positive_prompt))
    step("negative_prompt is non-empty", bool(prompt.negative_prompt))
    step("positive contains alignment text", "script-reference alignment" in prompt.positive_prompt.lower() or "alignment" in prompt.positive_prompt.lower())
    step("positive contains non-negotiable story", "non-negotiable story" in prompt.positive_prompt.lower())

    # 5. build_prompt_spec with both profile and enriched_intent
    print("\n[5] build_prompt_spec() with both visual_reference_profile and enriched_intent")
    profile = StyleReferenceProfile(
        visual_summary="Warm amber environment",
        palette_description="Amber tones",
        lighting_description="Soft directional",
        atmosphere_description="Professional",
    )
    prompt2 = prompt_construction_service.build_prompt_spec(
        intent,
        style_preset="premium_cinematic_saas",
        visual_reference_profile=profile,
        enriched_intent=enriched,
    )
    step("prompt with both sources is valid", prompt2 is not None and bool(prompt2.positive_prompt))
    step("contains visual reference guidance", "visual reference guidance" in prompt2.positive_prompt.lower())
    step("contains script-reference alignment", "script-reference alignment" in prompt2.positive_prompt.lower())

    # 6. Pipeline integration
    print("\n[6] Pipeline integration (cid_script_to_prompt_pipeline_service)")
    from services.cid_script_to_prompt_pipeline_service import run_script_to_prompt_pipeline

    import asyncio
    response = asyncio.run(
        run_script_to_prompt_pipeline(
            script_text="INT. ESTUDIO - NOCHE\nUn director revisa el storyboard con su equipo. La atmósfera es tensa pero creativa.\n\nEXT. CALLE - DIA\nEl equipo sale a filmar una escena nocturna.",
            output_type="storyboard_frame",
            max_scenes=2,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
    )
    step("pipeline returns response", response is not None)
    step("pipeline status is completed", response.status == "completed")
    step("alignment_results is list", isinstance(response.alignment_results, list))
    step("enriched_intents is list", isinstance(response.enriched_intents, list))
    if response.alignment_results:
        step("alignment_results contains data", len(response.alignment_results) > 0)
        first_alignment = response.alignment_results[0]
        if "error" not in first_alignment:
            step("alignment_result has alignment_score", "alignment_score" in first_alignment)
    if response.enriched_intents:
        step("enriched_intent has merged_intent_summary", "merged_intent_summary" in response.enriched_intents[0])

    # 7. Pipeline with NO visual reference (backward compat)
    print("\n[7] Pipeline backward compatibility (no visual reference)")
    response2 = asyncio.run(
        run_script_to_prompt_pipeline(
            script_text="INT. ESTUDIO - NOCHE\nUn director revisa el storyboard.",
            output_type="storyboard_frame",
            max_scenes=1,
        )
    )
    step("pipeline works without reference", response2.status == "completed")
    step("alignment_results empty when no reference", len(response2.alignment_results) == 0)
    step("enriched_intents empty when no reference", len(response2.enriched_intents) == 0)

    print("\n[8] Model dump serialization (EnrichedVisualIntent)")
    dump = enriched.model_dump()
    step("model_dump works", "merged_intent_summary" in dump)
    step("model_dump has qa_checklist", "qa_checklist" in dump)

    from schemas.cid_visual_reference_schema import ScriptVisualAlignmentResult
    dump2 = result.model_dump()
    step("ScriptVisualAlignmentResult model_dump works", "alignment_score" in dump2)

    print("\n" + "=" * 60)
    print("ALL SMOKE CHECKS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
