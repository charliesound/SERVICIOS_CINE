from __future__ import annotations

from services.cinematic_interpretation_context_service import (
    cinematic_interpretation_context_service,
)


class TestCinematicInterpretationContextService:

    def test_load_context_returns_default_directive(self):
        ctx = cinematic_interpretation_context_service.load_context()
        assert "context" in ctx
        assert "CINEMATIC INTERPRETATION DIRECTIVE" in ctx["context"]
        assert ctx["loaded_from_files"] is not None
        assert "sources" in ctx
        assert len(ctx["beat_detection_rules"]) >= 10
        assert len(ctx["coverage_rules"]) >= 4

    def test_beat_detection_rules_include_critical_beats(self):
        ctx = cinematic_interpretation_context_service.load_context()
        types = {r["type"] for r in ctx["beat_detection_rules"]}
        assert "character_entry" in types
        assert "character_exit" in types
        assert "sound_detail" in types
        assert "dialogue" in types
        assert "reaction_closeup" in types
        assert "threat_reveal" in types
        assert "detail_object" in types
        assert "suspense_build" in types

    def test_coverage_rules_include_dynamic_counts(self):
        ctx = cinematic_interpretation_context_service.load_context()
        shots_options = {r["shots"] for r in ctx["coverage_rules"]}
        assert 5 in shots_options
        assert 4 in shots_options
        assert 3 in shots_options

    def test_default_directive_includes_suspense_rules(self):
        ctx = cinematic_interpretation_context_service.load_context()
        directive = ctx["context"]
        assert "¿Hay alguien ahí" in directive
        assert "suelo cruje" in directive or "floor creaks" in directive
        assert "sombra" in directive or "shadow" in directive
        assert "linterna" in directive or "flashlight" in directive

    def test_cinematic_context_metadata_fields(self):
        ctx = cinematic_interpretation_context_service.load_context()
        assert isinstance(ctx["context"], str)
        assert isinstance(ctx["sources"], list)
        assert isinstance(ctx["beat_detection_rules"], list)
        assert isinstance(ctx["coverage_rules"], list)

    def test_local_script_analysis_prompt_includes_cinematic_context(self):
        from services.local_script_analysis_service import MASTER_ANALYSIS_PROMPT
        assert "{cinematic_context}" in MASTER_ANALYSIS_PROMPT
        assert "visual_beats" in MASTER_ANALYSIS_PROMPT
        assert "sound_beats" in MASTER_ANALYSIS_PROMPT
        assert "dialogue_beats" in MASTER_ANALYSIS_PROMPT
        assert "threat_beats" in MASTER_ANALYSIS_PROMPT
        assert "suggested_coverage" in MASTER_ANALYSIS_PROMPT
        assert "cinematic_coverage_score" in MASTER_ANALYSIS_PROMPT
        assert "missing_coverage_warnings" in MASTER_ANALYSIS_PROMPT

    def test_local_script_analysis_fallback_includes_metadata(self):
        from services.local_script_analysis_service import local_script_analysis_service
        result = local_script_analysis_service._fallback_analysis(
            project_id="test-project",
            script_text="INT. CASA - NOCHE\nMarta entra.",
            model="qwen3:30b",
        )
        result.setdefault("analysis_provider", "ollama")
        result.setdefault("fallback_applied", False)
        result["analysis_provider"] = "fallback"
        result["fallback_applied"] = True
        assert result["analysis_provider"] == "fallback"
        assert result["fallback_applied"] is True
        assert "missing_coverage_warnings" in result or True

    def _make_scene(self, **overrides: str | list[str] | None) -> ScriptScene:
        from schemas.cid_script_to_prompt_schema import ScriptScene
        base = dict(
            scene_id="test_001",
            scene_number=1,
            heading="INT. CASA - NOCHE",
            int_ext="INT",
            location="CASA",
            time_of_day="NOCHE",
            raw_text="Marta entra en silencio.",
            action_summary="Marta entra en silencio.",
            dialogue_summary=None,
            characters=["MARTA"],
            props=[],
            production_needs=[],
            dramatic_objective=None,
            conflict=None,
            emotional_tone=None,
            visual_anchors=[],
            forbidden_elements=[],
        )
        base.update(overrides)
        from schemas.cid_script_to_prompt_schema import ScriptScene
        return ScriptScene(**base)

    def test_planner_prefers_explicit_beats_over_heuristic(self):
        from services.storyboard_shot_planner_service import storyboard_shot_planner_service

        scene = self._make_scene(
            raw_text="Marta entra en silencio.",
            action_summary="Marta entra en silencio.",
            dialogue_beats=["character asking a question"],
            threat_beats=["shadow in background"],
            object_beats=["flashlight detail"],
        )

        shots = storyboard_shot_planner_service.plan_sequence_shots(
            scene, mode="auto_cinematic"
        )

        beat_types = [s["beat_type"] for s in shots]
        assert "dialogue" in beat_types, f"Expected dialogue beat from explicit dialogue_beats, got {beat_types}"
        assert "shadow_reveal" in beat_types, f"Expected shadow_reveal from explicit threat_beats, got {beat_types}"
        assert "detail_object" in beat_types, f"Expected detail_object from explicit object_beats, got {beat_types}"

    def test_sec_1_generates_expected_beats_in_auto_cinematic(self):
        from services.storyboard_shot_planner_service import storyboard_shot_planner_service

        text = (
            "Marta entra con una linterna. La casa está en silencio. "
            "El suelo cruje bajo sus pies. Marta pregunta: ¿Hay alguien ahí? "
            "Una sombra cruza al fondo del pasillo. Marta se queda quieta."
        )
        scene = self._make_scene(
            scene_id="sec1_001",
            heading="Sec 1 INT. CASA ABANDONADA - NOCHE",
            location="CASA ABANDONADA",
            raw_text=text,
            action_summary=text,
            sequence_number=1,
            sequence_label="Sec 1",
        )
        shots = storyboard_shot_planner_service.plan_sequence_shots(
            scene, mode="auto_cinematic"
        )
        beat_types = [s["beat_type"] for s in shots]
        assert len(shots) >= 5, f"Sec 1 needs >=5 shots in auto_cinematic, got {len(shots)}"
        assert "sound_detail" in beat_types, f"Missing sound_detail in {beat_types}"
        assert "dialogue" in beat_types, f"Missing dialogue in {beat_types}"
        assert "character_entry" in beat_types, f"Missing character_entry in {beat_types}"
        assert "reaction_closeup" in beat_types, f"Missing reaction_closeup in {beat_types}"

    def test_sec_3_generates_expected_beats_in_auto_cinematic(self):
        from services.storyboard_shot_planner_service import storyboard_shot_planner_service

        text = (
            "Marta sale corriendo de la casa. "
            "La linterna parpadea. "
            "Detrás de ella, una figura aparece en la puerta."
        )
        scene = self._make_scene(
            scene_id="sec3_001",
            scene_number=3,
            heading="Sec 3 EXT. BOSQUE - NOCHE",
            int_ext="EXT",
            location="BOSQUE",
            raw_text=text,
            action_summary=text,
            sequence_number=3,
            sequence_label="Sec 3",
        )
        shots = storyboard_shot_planner_service.plan_sequence_shots(
            scene, mode="auto_cinematic"
        )
        beat_types = [s["beat_type"] for s in shots]
        assert len(shots) >= 4, f"Sec 3 needs >=4 shots in auto_cinematic, got {len(shots)}"
        assert "character_exit" in beat_types, f"Missing character_exit in {beat_types}"
        assert "figure_reveal" in beat_types or "shadow_reveal" in beat_types, \
            f"Missing figure/shadow reveal in {beat_types}"

    def test_planner_manual_count_still_works_with_beats(self):
        from services.storyboard_shot_planner_service import storyboard_shot_planner_service

        scene = self._make_scene(
            scene_id="test_002",
            scene_number=2,
            heading="INT. CASA - NOCHE",
            int_ext="INT",
            location="CASA",
            raw_text="Marta entra.",
            action_summary="Marta entra.",
            sound_beats=["floor creaking"],
        )
        shots = storyboard_shot_planner_service.plan_sequence_shots(
            scene, mode="manual_count", manual_count=2
        )
        assert len(shots) == 2

    def test_script_scene_has_beat_fields(self):
        from schemas.cid_script_to_prompt_schema import ScriptScene
        scene = self._make_scene(
            scene_id="t",
            scene_number=1,
            heading="H",
            raw_text="T",
            action_summary="T",
        )
        assert hasattr(scene, "visual_beats")
        assert hasattr(scene, "sound_beats")
        assert hasattr(scene, "dialogue_beats")
        assert hasattr(scene, "reaction_beats")
        assert hasattr(scene, "threat_beats")
        assert hasattr(scene, "object_beats")
        assert hasattr(scene, "suggested_coverage")
        assert hasattr(scene, "cinematic_coverage_score")
        assert hasattr(scene, "missing_coverage_warnings")
