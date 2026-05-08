from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schemas.cid_script_to_prompt_schema import CinematicIntent
from schemas.cid_visual_reference_schema import (
    EnrichedVisualIntent,
    ScriptVisualAlignmentRequest,
    StyleReferenceProfile,
)
from services.prompt_construction_service import prompt_construction_service
from services.script_visual_alignment_service import script_visual_alignment_service


class TestPromptConstructionWithScriptVisualAlignment:
    def _make_dummy_intent(self) -> CinematicIntent:
        return CinematicIntent(
            intent_id="intent_001",
            scene_id="scene_001",
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

    def _make_enriched_intent(self) -> EnrichedVisualIntent:
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. SALA DE PROYECCION - NOCHE\nUn equipo revisa el metraje. Atmósfera tensa y profesional.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Warm amber tones with soft dramatic lighting",
                palette_description="Ámber, carbón, azules profundos",
                lighting_description="Suave direccional con sombras dramáticas",
                atmosphere_description="Profesional e intensa",
            ),
        )
        _, enriched = script_visual_alignment_service.align(request)
        return enriched

    def test_build_prompt_with_enriched_intent_does_not_raise(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert prompt is not None
        assert prompt.positive_prompt != ""

    def test_prompt_with_enriched_intent_contains_alignment_text(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert "script-reference alignment" in prompt.positive_prompt.lower() or "alignment" in prompt.positive_prompt.lower()

    def test_prompt_with_enriched_intent_contains_scene_requirements(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert "scene requirements" in prompt.positive_prompt.lower()

    def test_prompt_with_enriched_intent_contains_non_negotiable_story(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert "non-negotiable story" in prompt.positive_prompt.lower()

    def test_prompt_with_enriched_intent_and_reference_profile(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        profile = StyleReferenceProfile(
            visual_summary="Warm amber and charcoal",
            palette_description="Ámber y carbón",
            lighting_description="Suave direccional",
            atmosphere_description="Profesional",
        )
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
            enriched_intent=enriched,
        )
        assert prompt is not None
        assert "visual reference guidance" in prompt.positive_prompt.lower() or "script-reference alignment" in prompt.positive_prompt.lower()

    def test_prompt_with_enriched_intent_negative_includes_constraints(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert prompt.negative_prompt != ""
        assert "in the style of any named director" in prompt.negative_prompt

    def test_prompt_with_enriched_intent_keeps_core_identity(self):
        intent = self._make_dummy_intent()
        enriched = self._make_enriched_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=enriched,
        )
        assert intent.subject in prompt.positive_prompt
        assert intent.action in prompt.positive_prompt

    def test_prompt_with_enriched_intent_qa_checklist_available(self):
        enriched = self._make_enriched_intent()
        assert len(enriched.qa_checklist) > 0
        assert all("VERIFICAR" in item for item in enriched.qa_checklist)

    def test_prompt_with_minimal_enriched_intent_does_not_crash(self):
        intent = self._make_dummy_intent()
        minimal = EnrichedVisualIntent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            enriched_intent=minimal,
        )
        assert prompt is not None
        assert prompt.positive_prompt != ""
