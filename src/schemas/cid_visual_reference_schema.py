from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ReferencePurpose(str, Enum):
    global_project_style = "global_project_style"
    scene_mood = "scene_mood"
    character_visual_reference = "character_visual_reference"
    location_reference = "location_reference"
    lighting_reference = "lighting_reference"
    color_palette_reference = "color_palette_reference"
    composition_reference = "composition_reference"
    storyboard_reference = "storyboard_reference"


class ReferenceIntensity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ReferenceMode(str, Enum):
    mood_only = "mood_only"
    palette_lighting = "palette_lighting"
    composition_guidance = "composition_guidance"
    full_art_direction = "full_art_direction"


class DirectorVisualReferenceRequest(BaseModel):
    project_id: str | None = None
    scene_id: str | None = None
    sequence_id: str | None = None
    shot_id: str | None = None
    reference_image_asset_id: str | None = None
    reference_image_url: str | None = None
    reference_purpose: ReferencePurpose = ReferencePurpose.scene_mood
    notes_from_director: str | None = None
    intensity: ReferenceIntensity = ReferenceIntensity.medium
    reference_mode: ReferenceMode = ReferenceMode.palette_lighting
    allow_composition_transfer: bool = False
    allow_palette_transfer: bool = True
    allow_lighting_transfer: bool = True
    allow_texture_transfer: bool = False
    forbid_identity_copy: bool = True


class StyleReferenceProfile(BaseModel):
    reference_id: str = ""
    project_id: str | None = None
    source_image_asset_id: str | None = None
    source_image_url: str | None = None
    reference_purpose: ReferencePurpose = ReferencePurpose.scene_mood
    director_notes: str | None = None
    visual_summary: str = ""
    palette_description: str = ""
    lighting_description: str = ""
    contrast_description: str = ""
    camera_language_description: str = ""
    composition_description: str = ""
    texture_description: str = ""
    atmosphere_description: str = ""
    genre_signals: list[str] = Field(default_factory=list)
    production_design_signals: list[str] = Field(default_factory=list)
    negative_constraints: list[str] = Field(default_factory=list)
    transferable_traits: list[str] = Field(default_factory=list)
    non_transferable_traits: list[str] = Field(default_factory=list)
    prompt_modifiers: list[str] = Field(default_factory=list)
    qa_requirements: list[str] = Field(default_factory=list)
    confidence_score: float = 0.5
    raw_analysis: dict[str, Any] = Field(default_factory=dict)

    def to_prompt_guidance_block(self) -> str:
        lines = ["VISUAL REFERENCE GUIDANCE"]
        if self.visual_summary:
            lines.append(f"  Summary: {self.visual_summary}")
        if self.palette_description:
            lines.append(f"  Palette: {self.palette_description}")
        if self.lighting_description:
            lines.append(f"  Lighting: {self.lighting_description}")
        if self.atmosphere_description:
            lines.append(f"  Atmosphere: {self.atmosphere_description}")
        if self.texture_description:
            lines.append(f"  Texture: {self.texture_description}")
        if self.composition_description:
            lines.append(f"  Composition: {self.composition_description}")
        if self.camera_language_description:
            lines.append(f"  Camera language: {self.camera_language_description}")
        if self.transferable_traits:
            lines.append(f"  Transferable traits: {', '.join(self.transferable_traits)}")
        if self.non_transferable_traits:
            lines.append(f"  Do NOT transfer: {', '.join(self.non_transferable_traits)}")
        lines.append("  Do NOT copy identity, logos, people, brands, or specific content from reference")
        lines.append("  Maintain coherence with script, characters, and established continuity")
        return "\n".join(lines)


class VisualReferenceAnalysisResult(BaseModel):
    profile: StyleReferenceProfile
    warnings: list[str] = Field(default_factory=list)
    needs_human_review: bool = False
    extracted_prompt_guidance: str = ""
    safe_prompt_guidance: str = ""
    risks: list[str] = Field(default_factory=list)


class AlignmentMode(str, Enum):
    mood_alignment = "mood_alignment"
    scene_alignment = "scene_alignment"
    shot_alignment = "shot_alignment"
    full_semantic_alignment = "full_semantic_alignment"


class ScriptVisualAlignmentRequest(BaseModel):
    project_id: str | None = None
    scene_id: str | None = None
    sequence_id: str | None = None
    shot_id: str | None = None
    script_excerpt: str = ""
    reference_profile_id: str | None = None
    reference_image_asset_id: str | None = None
    reference_image_url: str | None = None
    director_notes: str | None = None
    alignment_mode: AlignmentMode = AlignmentMode.scene_alignment
    reference_profile: StyleReferenceProfile | None = None


class ScriptVisualAlignmentResult(BaseModel):
    script_summary: str = ""
    reference_visual_summary: str = ""
    alignment_score: float = 0.5
    matching_elements: list[str] = Field(default_factory=list)
    missing_from_image: list[str] = Field(default_factory=list)
    missing_from_script: list[str] = Field(default_factory=list)
    tension_points: list[str] = Field(default_factory=list)
    recommended_visual_direction: str = ""
    recommended_prompt_guidance: str = ""
    continuity_notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    safe_constraints: list[str] = Field(default_factory=list)


class EnrichedVisualIntent(BaseModel):
    narrative_intent: str = ""
    visual_intent: str = ""
    merged_intent_summary: str = ""
    scene_requirements: list[str] = Field(default_factory=list)
    visual_requirements: list[str] = Field(default_factory=list)
    non_negotiable_story_elements: list[str] = Field(default_factory=list)
    non_negotiable_visual_elements: list[str] = Field(default_factory=list)
    prompt_guidance: str = ""
    negative_guidance: str = ""
    qa_checklist: list[str] = Field(default_factory=list)

    def to_enriched_prompt_block(self) -> str:
        lines = [
            "STORY TRUTH",
            f"  {self.narrative_intent}",
            "",
            "VISUAL REFERENCE GUIDANCE",
            f"  {self.visual_intent}",
            "",
            "ALIGNMENT DECISION",
            f"  {self.merged_intent_summary}",
        ]
        if self.scene_requirements:
            lines.append(f"  Scene requirements: {'; '.join(self.scene_requirements)}")
        if self.visual_requirements:
            lines.append(f"  Visual requirements: {'; '.join(self.visual_requirements)}")
        if self.non_negotiable_story_elements:
            lines.append(f"  Non-negotiable story: {'; '.join(self.non_negotiable_story_elements)}")
        if self.non_negotiable_visual_elements:
            lines.append(f"  Non-negotiable visual: {'; '.join(self.non_negotiable_visual_elements)}")
        lines.append("")
        lines.append("NEGATIVE / SAFETY GUIDANCE")
        lines.append(f"  {self.negative_guidance}")
        return "\n".join(lines)
