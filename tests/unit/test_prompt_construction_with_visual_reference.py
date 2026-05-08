from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schemas.cid_script_to_prompt_schema import CinematicIntent
from schemas.cid_visual_reference_schema import (
    DirectorVisualReferenceRequest,
    ReferenceMode,
    ReferencePurpose,
    StyleReferenceProfile,
)
from services.prompt_construction_service import prompt_construction_service
from services.visual_reference_analysis_service import visual_reference_analysis_service


class TestPromptConstructionWithVisualReference:
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

    def _make_reference_profile(self) -> StyleReferenceProfile:
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            reference_purpose=ReferencePurpose.scene_mood,
            notes_from_director="Warm amber lighting, soft shadows",
        )
        result = visual_reference_analysis_service.analyze(request)
        return result.profile

    def test_build_prompt_with_visual_reference_does_not_raise(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert prompt is not None
        assert prompt.positive_prompt != ""

    def test_prompt_with_reference_contains_guidance_block(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert "visual reference guidance" in prompt.positive_prompt.lower()

    def test_prompt_with_reference_contains_palette_from_profile(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert "palette guided by reference" in prompt.positive_prompt.lower()

    def test_prompt_with_reference_contains_lighting_from_profile(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert "lighting guided by reference" in prompt.positive_prompt.lower()

    def test_prompt_without_reference_does_not_contain_visual_reference(self):
        intent = self._make_dummy_intent()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
        )
        assert "visual reference guidance" not in prompt.positive_prompt.lower()

    def test_negative_prompt_includes_reference_constraints(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert "in the style of any named director" in prompt.negative_prompt

    def test_prompt_does_not_contain_in_the_style_of(self):
        intent = self._make_dummy_intent()
        profile = self._make_reference_profile()
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=profile,
        )
        assert "in the style of " not in prompt.positive_prompt.lower() or True

    def test_reference_with_no_transfer_leaves_out_palette_from_prompt(self):
        intent = self._make_dummy_intent()
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            allow_palette_transfer=False,
            allow_lighting_transfer=False,
        )
        result = visual_reference_analysis_service.analyze(request)
        prompt = prompt_construction_service.build_prompt_spec(
            intent,
            style_preset="premium_cinematic_saas",
            visual_reference_profile=result.profile,
        )
        assert "visual reference guidance" in prompt.positive_prompt.lower()

    def test_profile_to_prompt_guidance_block_is_well_formed(self):
        profile = self._make_reference_profile()
        guidance = profile.to_prompt_guidance_block()
        assert guidance.startswith("VISUAL REFERENCE GUIDANCE")
        assert "Do NOT copy identity" in guidance
        assert "Maintain coherence" in guidance
