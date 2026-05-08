from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from schemas.cid_visual_reference_schema import (
    DirectorVisualReferenceRequest,
    ReferencePurpose,
    ReferenceIntensity,
    ReferenceMode,
)
from services.visual_reference_analysis_service import visual_reference_analysis_service


class TestVisualReferenceAnalysisService:
    def test_analyze_stub_returns_result_with_profile(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            reference_purpose=ReferencePurpose.scene_mood,
            intensity=ReferenceIntensity.medium,
            reference_mode=ReferenceMode.palette_lighting,
            notes_from_director="Warm amber lighting with soft shadows",
        )
        result = visual_reference_analysis_service.analyze(request)
        assert result is not None
        assert result.profile is not None
        assert result.profile.reference_id != ""
        assert result.needs_human_review is True
        assert len(result.warnings) > 0

    def test_analyze_stub_profile_has_expected_fields(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
        )
        result = visual_reference_analysis_service.analyze(request)
        profile = result.profile
        assert profile.visual_summary != ""
        assert profile.palette_description != ""
        assert profile.lighting_description != ""
        assert profile.atmosphere_description != ""
        assert isinstance(profile.transferable_traits, list)
        assert isinstance(profile.non_transferable_traits, list)
        assert isinstance(profile.negative_constraints, list)
        assert isinstance(profile.prompt_modifiers, list)
        assert isinstance(profile.qa_requirements, list)

    def test_analyze_purpose_lighting_generates_lighting_focused_summary(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            reference_purpose=ReferencePurpose.lighting_reference,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "lighting" in result.profile.visual_summary.lower()

    def test_analyze_purpose_color_palette_generates_palette_focused_summary(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            reference_purpose=ReferencePurpose.color_palette_reference,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "palette" in result.profile.visual_summary.lower()

    def test_palette_transfer_disabled_returns_no_palette(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            allow_palette_transfer=False,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "not requested" in result.profile.palette_description

    def test_lighting_transfer_disabled_returns_no_lighting(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            allow_lighting_transfer=False,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "not requested" in result.profile.lighting_description

    def test_composition_transfer_disabled_returns_no_composition(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            allow_composition_transfer=False,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "not requested" in result.profile.composition_description

    def test_director_notes_amber_produces_warm_palette(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            notes_from_director="I want warm amber tones",
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "amber" in result.profile.palette_description.lower()

    def test_director_notes_cold_produces_cool_palette(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            notes_from_director="Cold blue steel atmosphere",
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "blue" in result.profile.palette_description.lower() or "cool" in result.profile.palette_description.lower()

    def test_to_prompt_guidance_block_contains_visual_reference_label(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
        )
        result = visual_reference_analysis_service.analyze(request)
        guidance = result.profile.to_prompt_guidance_block()
        assert "VISUAL REFERENCE GUIDANCE" in guidance
        assert "Do NOT copy" in guidance

    def test_analyze_without_url_still_returns_profile(self):
        request = DirectorVisualReferenceRequest(
            reference_image_asset_id="asset_001",
        )
        result = visual_reference_analysis_service.analyze(request)
        assert result.profile is not None
        assert result.profile.source_image_asset_id == "asset_001"

    def test_full_art_direction_enables_texture_transfer(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            allow_texture_transfer=True,
        )
        result = visual_reference_analysis_service.analyze(request)
        assert "not requested" not in result.profile.texture_description

    def test_negative_constraints_include_no_artist_style(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
        )
        result = visual_reference_analysis_service.analyze(request)
        constraints = " ".join(result.profile.negative_constraints).lower()
        assert "in the style of" in constraints

    def test_qa_requirements_exist(self):
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
        )
        result = visual_reference_analysis_service.analyze(request)
        assert len(result.profile.qa_requirements) > 0
        for qa in result.profile.qa_requirements:
            assert qa.startswith("VERIFICAR:")
