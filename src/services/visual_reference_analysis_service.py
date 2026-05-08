from __future__ import annotations

import json
import os
import uuid
from typing import Any

from schemas.cid_visual_reference_schema import (
    DirectorVisualReferenceRequest,
    ReferenceMode,
    ReferencePurpose,
    StyleReferenceProfile,
    VisualReferenceAnalysisResult,
)


class VisualReferenceAnalysisService:
    def __init__(self) -> None:
        self._ollama_vision_model: str | None = os.environ.get("OLLAMA_VISION_MODEL")
        self._ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self._comfyui_base_url: str | None = os.environ.get("COMFYUI_BASE_URL")

    def analyze(
        self,
        request: DirectorVisualReferenceRequest,
    ) -> VisualReferenceAnalysisResult:
        if self._ollama_vision_model:
            return self._analyze_with_ollama(request)
        return self._analyze_stub(request)

    def _analyze_stub(
        self,
        request: DirectorVisualReferenceRequest,
    ) -> VisualReferenceAnalysisResult:
        profile = StyleReferenceProfile(
            reference_id=uuid.uuid4().hex[:16],
            project_id=request.project_id,
            source_image_url=request.reference_image_url,
            source_image_asset_id=request.reference_image_asset_id,
            reference_purpose=request.reference_purpose,
            director_notes=request.notes_from_director,
            visual_summary=self._stub_visual_summary(request),
            palette_description=self._stub_palette(request),
            lighting_description=self._stub_lighting(request),
            contrast_description=self._stub_contrast(request),
            camera_language_description=self._stub_camera(request),
            composition_description=self._stub_composition(request),
            texture_description=self._stub_texture(request),
            atmosphere_description=self._stub_atmosphere(request),
            genre_signals=self._stub_genre_signals(request),
            production_design_signals=self._stub_production_design_signals(request),
            negative_constraints=self._stub_negative_constraints(request),
            transferable_traits=self._stub_transferable_traits(request),
            non_transferable_traits=self._stub_non_transferable_traits(request),
            prompt_modifiers=self._stub_prompt_modifiers(request),
            qa_requirements=self._stub_qa_requirements(request),
            confidence_score=0.4,
        )

        result = VisualReferenceAnalysisResult(
            profile=profile,
            warnings=["Stub analysis: no real vision backend available. Review manually."],
            needs_human_review=True,
            extracted_prompt_guidance=profile.to_prompt_guidance_block(),
            safe_prompt_guidance=profile.to_prompt_guidance_block(),
            risks=["Reference image not analyzed by vision model. Manual review required."],
        )
        return result

    def _analyze_with_ollama(
        self,
        request: DirectorVisualReferenceRequest,
    ) -> VisualReferenceAnalysisResult:
        return self._analyze_stub(request)

    def _stub_visual_summary(self, request: DirectorVisualReferenceRequest) -> str:
        base = "Premium cinematic visual reference"
        if request.reference_purpose == ReferencePurpose.lighting_reference:
            return f"{base} focused on lighting design and shadow structure"
        if request.reference_purpose == ReferencePurpose.color_palette_reference:
            return f"{base} focused on color temperature and palette"
        if request.reference_purpose == ReferencePurpose.composition_reference:
            return f"{base} focused on frame composition and camera language"
        if request.reference_purpose in (
            ReferencePurpose.scene_mood,
            ReferencePurpose.global_project_style,
        ):
            return f"{base} for overall mood and atmosphere direction"
        if request.reference_purpose == ReferencePurpose.location_reference:
            return f"{base} for location and environment design reference"
        if request.reference_purpose == ReferencePurpose.character_visual_reference:
            return f"{base} for character visual design reference"
        return base

    def _stub_palette(self, request: DirectorVisualReferenceRequest) -> str:
        if not request.allow_palette_transfer:
            return "Palette transfer not requested"
        notes = request.notes_from_director or ""
        if "amber" in notes.lower() or "cálido" in notes.lower() or "warm" in notes.lower():
            return "Warm amber and charcoal dominant palette, subtle teal accents for depth"
        if "frío" in notes.lower() or "cold" in notes.lower() or "blue" in notes.lower():
            return "Cool blue-steel palette with controlled cyan highlights and deep shadows"
        if "oscuro" in notes.lower() or "dark" in notes.lower():
            return "Dark charcoal and graphite palette with targeted warm accents"
        return "Charcoal and graphite dominated palette with controlled amber highlights"

    def _stub_lighting(self, request: DirectorVisualReferenceRequest) -> str:
        if not request.allow_lighting_transfer:
            return "Lighting transfer not requested"
        notes = request.notes_from_director or ""
        if "volumétric" in notes.lower() or "volumetric" in notes.lower():
            return "Volumetric lighting with visible light rays and atmospheric depth"
        if "suave" in notes.lower() or "soft" in notes.lower():
            return "Soft diffused lighting with gentle shadows and wrapped highlights"
        if "contraste" in notes.lower() or "hard" in notes.lower() or "duro" in notes.lower():
            return "Hard directional lighting with strong contrast and defined shadow areas"
        return "Soft directional lighting with controlled contrast and subtle rim highlights"

    def _stub_contrast(self, request: DirectorVisualReferenceRequest) -> str:
        return "Medium-high contrast with deep blacks and preserved shadow detail"

    def _stub_camera(self, request: DirectorVisualReferenceRequest) -> str:
        purpose = request.reference_purpose
        if purpose == ReferencePurpose.composition_reference:
            return "Symmetrical composition with centered subject, medium establishing coverage"
        if purpose == ReferencePurpose.storyboard_reference:
            return "Multi-shot sequence coverage with standard to tight framing progression"
        return "Standard cinematic coverage with balanced framing and controlled depth"

    def _stub_composition(self, request: DirectorVisualReferenceRequest) -> str:
        if not request.allow_composition_transfer:
            return "Composition transfer not requested"
        return "Balanced frame composition with subject placement following rule of thirds"

    def _stub_texture(self, request: DirectorVisualReferenceRequest) -> str:
        if not request.allow_texture_transfer:
            return "Texture transfer not requested"
        return "Clean premium texture with controlled grain and refined surface quality"

    def _stub_atmosphere(self, request: DirectorVisualReferenceRequest) -> str:
        purpose = request.reference_purpose
        if purpose in (ReferencePurpose.scene_mood, ReferencePurpose.global_project_style):
            return "Premium cinematic atmosphere with controlled dramatic tension"
        if purpose == ReferencePurpose.lighting_reference:
            return "Atmosphere defined primarily by lighting quality and shadow structure"
        if purpose == ReferencePurpose.location_reference:
            return "Environmental atmosphere emphasizing location-specific ambience"
        return "Controlled professional atmosphere suitable for film production context"

    def _stub_genre_signals(self, request: DirectorVisualReferenceRequest) -> list[str]:
        return ["premium cinematic", "professional film production", "controlled aesthetic"]

    def _stub_production_design_signals(self, request: DirectorVisualReferenceRequest) -> list[str]:
        return ["modern production environment", "professional workspace", "controlled set design"]

    def _stub_negative_constraints(self, request: DirectorVisualReferenceRequest) -> list[str]:
        constraints = [
            "in the style of any named director or artist",
            "direct copy of reference composition or content",
            "reproduction of reference identity, logos, people or brands",
            "generic stock photography aesthetic",
            "low quality or rushed production look",
        ]
        if not request.allow_composition_transfer:
            constraints.append("copying the frame composition from reference")
        if not request.allow_palette_transfer:
            constraints.append("copying the exact color palette from reference")
        if not request.allow_lighting_transfer:
            constraints.append("copying the lighting setup from reference")
        return constraints

    def _stub_transferable_traits(self, request: DirectorVisualReferenceRequest) -> list[str]:
        traits = []
        if request.allow_palette_transfer:
            traits.append("general color temperature and palette family")
        if request.allow_lighting_transfer:
            traits.append("lighting quality and shadow structure approach")
        if request.allow_composition_transfer:
            traits.append("framing and composition philosophy")
        if request.allow_texture_transfer:
            traits.append("surface texture and image quality approach")
        traits.append("overall mood and dramatic atmosphere")
        return traits

    def _stub_non_transferable_traits(self, request: DirectorVisualReferenceRequest) -> list[str]:
        return [
            "specific people, faces, or characters",
            "brand logos, text, or trademarks",
            "exact object placement or prop layout",
            "identity-defining characteristics of the reference",
        ]

    def _stub_prompt_modifiers(self, request: DirectorVisualReferenceRequest) -> list[str]:
        modifiers = []
        if request.allow_palette_transfer:
            modifiers.append("palette guided by reference: charcoal and amber family")
        if request.allow_lighting_transfer:
            modifiers.append("lighting guided by reference: soft directional with controlled contrast")
        modifiers.append("mood guided by reference: premium cinematic atmosphere")
        return modifiers

    def _stub_qa_requirements(self, request: DirectorVisualReferenceRequest) -> list[str]:
        return [
            "VERIFICAR: La imagen generada NO copia literalmente la referencia",
            "VERIFICAR: El prompt evita 'in the style of' cualquier artista",
            "VERIFICAR: La paleta de color sigue la familia de la referencia sin duplicarla",
            "VERIFICAR: La atmósfera es coherente con la referencia pero adaptada al guion",
            "VERIFICAR: No hay identidad, logos, marcas ni personas específicas de la referencia",
        ]


visual_reference_analysis_service = VisualReferenceAnalysisService()
