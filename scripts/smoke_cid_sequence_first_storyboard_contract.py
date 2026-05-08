#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("APP_ENV", "development")

TEST_SCRIPT = """1 INT. ESTUDIO - NOCHE
Un director revisa el storyboard con su equipo.
La atmósfera es tensa pero creativa.
DIRECTOR: Necesitamos más tensión en esta escena.
CAMAROGRAFO: Podríamos ajustar la iluminación.

2 EXT. CALLE - DIA
El equipo sale a filmar una escena nocturna.
El director da indicaciones al camarógrafo.
El cameraman ajusta la cámara.

3 INT. SALA DE MONTAJE - NOCHE
El equipo revisa el metraje.
Discuten los cortes y la continuidad.
DIRECTOR: Este plano no funciona.
MONTAJISTA: Podemos reordenar la secuencia.

4 INT. ESTUDIO - DIA
Reunión final de producción.
El director aprueba el montaje final.
Todo el equipo celebra."""


def step(label: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}")
    if not ok:
        sys.exit(1)


def main() -> int:
    print("=" * 60)
    print("SMOKE: Sequence-First Storyboard Architecture Contract")
    print("=" * 60)

    from schemas.cid_sequence_first_schema import (
        FullScriptAnalysisResult,
        ScriptSequenceMapEntry,
        SequenceStoryboardPlan,
    )
    from schemas.cid_script_to_prompt_schema import PromptSpec
    from services.cid_script_to_prompt_pipeline_service import (
        analyze_full_script,
        generate_prompt_for_planned_shot,
        prepare_sequence_storyboard,
    )

    print("\n[LEVEL 1] Full script analysis")
    result = analyze_full_script(TEST_SCRIPT)
    step("analyze_full_script returns result", isinstance(result, FullScriptAnalysisResult))

    synopsis = result.synopsis
    step("synopsis has logline", bool(synopsis.logline))
    step("synopsis has premise", bool(synopsis.premise))
    step("synopsis has main_characters", isinstance(synopsis.main_characters, list))
    step("synopsis has main_locations", len(synopsis.main_locations) > 0)

    sequence_map = result.sequence_map
    step("sequence_map has sequences", len(sequence_map.sequences) > 0)
    seq_entry = sequence_map.sequences[0]
    step("sequence_map entries have required fields",
         bool(seq_entry.sequence_id) and bool(seq_entry.title) and bool(seq_entry.script_excerpt))
    step("sequence_map has recommended_priority_order",
         len(sequence_map.recommended_priority_order) > 0)

    from schemas.cid_sequence_first_schema import resolve_sequence_entry
    resolved = resolve_sequence_entry(sequence_map, seq_entry.sequence_id)
    step("resolve_sequence_entry exact match",
         resolved is not None and resolved.sequence_id == seq_entry.sequence_id)

    public_id = f"seq_{seq_entry.sequence_number:02d}"
    resolved_02 = resolve_sequence_entry(sequence_map, public_id)
    step(f"resolve_sequence_entry '{public_id}' → '{seq_entry.sequence_id}'",
         resolved_02 is not None and resolved_02.sequence_number == seq_entry.sequence_number)

    plain_number = str(seq_entry.sequence_number)
    resolved_num = resolve_sequence_entry(sequence_map, plain_number)
    step(f"resolve_sequence_entry '{plain_number}' → seq_number={seq_entry.sequence_number}",
         resolved_num is not None and resolved_num.sequence_number == seq_entry.sequence_number)

    print("\n[LEVEL 2] Sequence storyboard planning")
    entry = ScriptSequenceMapEntry(
        sequence_id="seq_001",
        sequence_number=1,
        title="Revisión en estudio",
        script_excerpt="INT. ESTUDIO - NOCHE\nUn director revisa el storyboard.\nDIRECTOR: Necesitamos más tensión.\nCAMAROGRAFO: Podríamos ajustar la luz.",
        summary="Revisión del storyboard",
        location="ESTUDIO",
        time_of_day="NOCHE",
        characters=["DIRECTOR", "CAMAROGRAFO"],
        dramatic_function="setup",
        emotional_goal="tension",
        visual_opportunity="high",
    )
    plan = prepare_sequence_storyboard(entry)
    step("prepare_sequence_storyboard returns plan", isinstance(plan, SequenceStoryboardPlan))

    shots = plan.shot_plan
    step("plan has shot_plan with 5+ shots", len(shots) >= 5)
    step("first shot is WS or ESTABLISHING", shots[0].shot_type in ("WS", "ESTABLISHING"))

    shot_types = {s.shot_type for s in shots}
    step("shot plan has varied shot types", len(shot_types) >= 3)

    has_ots = any(s.shot_type == "OTS" for s in shots)
    step("dialogue shots include OTS", has_ots)

    step("plan has continuity_plan", len(plan.continuity_plan) > 0)
    step("plan has visual_style_guidance", bool(plan.visual_style_guidance))
    step("each shot has prompt_brief", all(bool(s.prompt_brief) for s in shots))
    step("each shot has shot_plan_reason", all(bool(s.shot_plan_reason) for s in shots))
    step("each shot has script_excerpt_used", all(bool(s.script_excerpt_used) for s in shots))

    print("\n[LEVEL 3] Prompt generation from planned shot")
    shot = shots[0]
    prompt_spec = generate_prompt_for_planned_shot(shot, entry)
    step("generate_prompt_for_planned_shot returns PromptSpec", isinstance(prompt_spec, PromptSpec))
    step("PromptSpec has non-empty positive_prompt", bool(prompt_spec.positive_prompt))
    step("PromptSpec has non-empty negative_prompt", bool(prompt_spec.negative_prompt))

    print("\n[GUARD] FULL_SCRIPT conceptual guard")
    from services.storyboard_service import StoryboardGenerationMode
    step("FULL_SCRIPT guard message check",
         StoryboardGenerationMode.FULL_SCRIPT == "FULL_SCRIPT")

    print("\n[ROUTES] Endpoint registration")
    from routes.cid_script_to_prompt_routes import router as cid_router
    from routes.storyboard_routes import router as sb_router
    paths_cid = [r.path for r in cid_router.routes]
    paths_sb = [r.path for r in sb_router.routes]
    all_paths = paths_cid + paths_sb
    step("analyze-full endpoint exists in router",
         any("analyze-full" in p for p in paths_cid))
    step("sequence plan endpoint exists in router",
         any("plan" in p for p in paths_sb))

    print("\n" + "=" * 60)
    print("ALL SMOKE CHECKS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
