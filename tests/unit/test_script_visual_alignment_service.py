from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from schemas.cid_visual_reference_schema import (
    AlignmentMode,
    EnrichedVisualIntent,
    ScriptVisualAlignmentRequest,
    ScriptVisualAlignmentResult,
    StyleReferenceProfile,
)
from services.script_visual_alignment_service import script_visual_alignment_service


class TestScriptVisualAlignmentService:
    def test_align_returns_result_and_enriched_intent(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. ESTUDIO - NOCHE\nUn director revisa la escena. La luz es tenue y dramática.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Warm amber tones with soft dramatic lighting",
                palette_description="Amber, charcoal, deep blues",
                lighting_description="Soft directional with dramatic shadows",
                atmosphere_description="Intimate and tense",
                composition_description="Rule of thirds",
            ),
        )
        result, enriched = script_visual_alignment_service.align(request)
        assert isinstance(result, ScriptVisualAlignmentResult)
        assert isinstance(enriched, EnrichedVisualIntent)
        assert 0.0 <= result.alignment_score <= 1.0

    def test_align_detects_mood_keywords_from_script(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. SALA - NOCHE\nAtmósfera tensa. Luz de velas.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Dark moody atmosphere",
                palette_description="dark, warm",
                lighting_description="not requested",
                atmosphere_description="tenso, dramatico",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert len(result.matching_elements) > 0

    def test_align_detects_tension_when_realism_vs_fantasy(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="EXT. BOSQUE - DIA\nUna escena realista de un caminante.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Fantastical surreal landscape",
                palette_description="Vibrant unnatural colors",
                lighting_description="Dramatic fantasy lighting",
                atmosphere_description="Surreal dreamlike",
                genre_signals=["fantasy"],
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert len(result.tension_points) > 0

    def test_align_empty_script_does_not_crash(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="",
            reference_profile=StyleReferenceProfile(),
        )
        result, enriched = script_visual_alignment_service.align(request)
        assert result.script_summary == "No script excerpt provided"
        assert enriched.narrative_intent != ""

    def test_align_empty_profile_does_not_crash(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. ESTUDIO - DIA\nEscena de prueba.",
            reference_profile=None,
        )
        result, enriched = script_visual_alignment_service.align(request)
        assert result.reference_visual_summary == ""
        assert enriched.visual_intent != ""

    def test_align_missing_from_image_detected(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="EXT. CALLE - NOCHE\nOscuridad total.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Bright sunny day",
                palette_description="bright, vibrant",
                lighting_description="sunny, bright",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert any("dark" in m.lower() or "night" in m.lower() for m in result.missing_from_image)

    def test_align_missing_from_script_detected(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. SALA - DIA\nDos personas conversan.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Futuristic sci-fi environment with tech",
                palette_description="Neon cyan and magenta",
                lighting_description="Glowing neon lights",
                atmosphere_description="Technological advanced",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert any("tech" in m.lower() for m in result.missing_from_script)

    def test_align_enriched_intent_has_merged_summary(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. ESTUDIO - NOCHE\nTensión dramática con iluminación de claroscuro.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Dark chiaroscuro lighting",
                palette_description="Black, white, amber",
                lighting_description="Chiaroscuro dramatic",
                atmosphere_description="Tense noir",
            ),
        )
        _, enriched = script_visual_alignment_service.align(request)
        assert enriched.merged_intent_summary != ""
        assert "Script" in enriched.merged_intent_summary or "script" in enriched.merged_intent_summary

    def test_align_enriched_intent_has_qa_checklist(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. COCINA - DIA\nUna mujer prepara café.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Warm domestic kitchen scene",
            ),
        )
        _, enriched = script_visual_alignment_service.align(request)
        assert len(enriched.qa_checklist) > 0
        assert all("VERIFICAR" in item for item in enriched.qa_checklist)

    def test_align_enriched_intent_non_negotiable_elements(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="EXT. BOSQUE - NOCHE\nUn hombre corre entre los árboles.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Dark mysterious forest",
            ),
        )
        _, enriched = script_visual_alignment_service.align(request)
        assert len(enriched.non_negotiable_story_elements) > 0
        assert len(enriched.non_negotiable_visual_elements) > 0

    def test_align_recommended_direction_includes_script_and_reference(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. DESPACHO - NOCHE\nUn detective enciende una lámpara.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Noir detective atmosphere",
                palette_description="Dark desaturated with warm lamp glow",
                lighting_description="Single source warm practical",
                atmosphere_description="Noir mystery",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert "FROM SCRIPT" in result.recommended_visual_direction
        assert "FROM REFERENCE" in result.recommended_visual_direction

    def test_align_safe_constraints_includes_identity_warning(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. ESTUDIO - DIA\nPrueba.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Generic test",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert any("Do NOT copy" in c for c in result.safe_constraints)

    def test_align_warnings_generated_for_low_confidence(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. ESTUDIO - DIA\nPrueba.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Test",
                confidence_score=0.3,
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert any("Low confidence" in w for w in result.warnings)

    def test_align_extracts_location_and_time(self):
        request = ScriptVisualAlignmentRequest(
            script_excerpt="INT. SALA DE PROYECCION - NOCHE\nUn equipo revisa el metraje.",
            reference_profile=StyleReferenceProfile(
                visual_summary="Dark projection room",
            ),
        )
        result, _ = script_visual_alignment_service.align(request)
        assert result.script_summary != ""
        assert "SALA" in result.script_summary.upper() or "NOCHE" in result.script_summary.upper()
