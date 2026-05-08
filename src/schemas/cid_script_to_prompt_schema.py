from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _clean_text_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = (value or "").strip()
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(normalized)
    return cleaned


class ScriptSequence(BaseModel):
    sequence_id: str
    sequence_number: int
    title: str
    summary: str
    scene_numbers: list[int] = Field(default_factory=list)
    dramatic_purpose: str | None = None
    emotional_arc: str | None = None
    continuity_notes: list[str] = Field(default_factory=list)

    @field_validator("title", "summary", "dramatic_purpose", "emotional_arc")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("continuity_notes")
    @classmethod
    def validate_continuity_notes(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class ScriptScene(BaseModel):
    scene_id: str
    scene_number: int
    heading: str
    int_ext: str | None = None
    location: str | None = None
    time_of_day: str | None = None
    raw_text: str
    action_summary: str
    dialogue_summary: str | None = None
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    production_needs: list[str] = Field(default_factory=list)
    dramatic_objective: str | None = None
    conflict: str | None = None
    emotional_tone: str | None = None
    visual_anchors: list[str] = Field(default_factory=list)
    forbidden_elements: list[str] = Field(default_factory=list)

    @field_validator(
        "heading",
        "int_ext",
        "location",
        "time_of_day",
        "raw_text",
        "action_summary",
        "dialogue_summary",
        "dramatic_objective",
        "conflict",
        "emotional_tone",
    )
    @classmethod
    def validate_scene_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("characters", "props", "production_needs", "visual_anchors", "forbidden_elements")
    @classmethod
    def validate_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class DirectorLensProfile(BaseModel):
    lens_id: str
    name: str
    description: str
    cinematic_principles: list[str] = Field(default_factory=list)
    framing_bias: list[str] = Field(default_factory=list)
    camera_movement_bias: list[str] = Field(default_factory=list)
    lighting_bias: list[str] = Field(default_factory=list)
    color_bias: list[str] = Field(default_factory=list)
    rhythm_bias: list[str] = Field(default_factory=list)
    emotional_strategy: list[str] = Field(default_factory=list)
    narrative_strategy: list[str] = Field(default_factory=list)
    forbidden_cliches: list[str] = Field(default_factory=list)
    best_for_scene_types: list[str] = Field(default_factory=list)

    @field_validator("lens_id", "name", "description")
    @classmethod
    def validate_profile_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator(
        "cinematic_principles",
        "framing_bias",
        "camera_movement_bias",
        "lighting_bias",
        "color_bias",
        "rhythm_bias",
        "emotional_strategy",
        "narrative_strategy",
        "forbidden_cliches",
        "best_for_scene_types",
    )
    @classmethod
    def validate_profile_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class DirectorLensDecision(BaseModel):
    scene_id: str
    selected_lens_id: str
    selected_lens_name: str
    reason: str
    scene_needs: list[str] = Field(default_factory=list)
    applied_principles: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("scene_id", "selected_lens_id", "selected_lens_name", "reason")
    @classmethod
    def validate_decision_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("scene_needs", "applied_principles", "warnings")
    @classmethod
    def validate_decision_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class DirectorialIntent(BaseModel):
    scene_id: str
    director_lens: DirectorLensDecision
    mise_en_scene: str
    blocking: str
    camera_strategy: str
    suspense_or_emotion_strategy: str
    visual_metaphor: str | None = None
    subtext_strategy: str | None = None
    rhythm_strategy: str
    performance_notes: str
    editorial_notes: str
    montage_notes: str | None = None
    coverage_strategy: list[str] = Field(default_factory=list)
    edit_sensitive_prompt_guidance: list[str] = Field(default_factory=list)
    prompt_guidance: list[str] = Field(default_factory=list)

    @field_validator(
        "scene_id",
        "mise_en_scene",
        "blocking",
        "camera_strategy",
        "suspense_or_emotion_strategy",
        "visual_metaphor",
        "subtext_strategy",
        "rhythm_strategy",
        "performance_notes",
        "editorial_notes",
        "montage_notes",
    )
    @classmethod
    def validate_directorial_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("prompt_guidance", "coverage_strategy", "edit_sensitive_prompt_guidance")
    @classmethod
    def validate_prompt_guidance(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class EditorialBeat(BaseModel):
    beat_id: str
    scene_id: str
    beat_order: int
    dramatic_function: str
    emotional_state_start: str
    emotional_state_end: str
    information_revealed: list[str] = Field(default_factory=list)
    tension_change: str
    suggested_shot_count: int
    suggested_duration_seconds: float | None = None

    @field_validator(
        "beat_id",
        "scene_id",
        "dramatic_function",
        "emotional_state_start",
        "emotional_state_end",
        "tension_change",
    )
    @classmethod
    def validate_beat_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("information_revealed")
    @classmethod
    def validate_information_revealed(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class MontageIntent(BaseModel):
    scene_id: str
    sequence_id: str | None = None
    editorial_function: str
    rhythm: str
    average_shot_duration: str
    cutting_pattern: str
    transition_strategy: str
    continuity_strategy: str
    eyeline_strategy: str
    sound_bridge_strategy: str | None = None
    emotional_cut_points: list[str] = Field(default_factory=list)
    reveal_points: list[str] = Field(default_factory=list)
    coverage_requirements: list[str] = Field(default_factory=list)
    shots_to_avoid: list[str] = Field(default_factory=list)
    editorial_notes: str

    @field_validator(
        "scene_id",
        "sequence_id",
        "editorial_function",
        "rhythm",
        "average_shot_duration",
        "cutting_pattern",
        "transition_strategy",
        "continuity_strategy",
        "eyeline_strategy",
        "sound_bridge_strategy",
        "editorial_notes",
    )
    @classmethod
    def validate_montage_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator(
        "emotional_cut_points",
        "reveal_points",
        "coverage_requirements",
        "shots_to_avoid",
    )
    @classmethod
    def validate_montage_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class ShotEditorialPurpose(BaseModel):
    shot_id: str
    scene_id: str
    shot_order: int
    shot_type: str
    purpose: str
    previous_shot_relationship: str | None = None
    next_shot_relationship: str | None = None
    cut_reason: str
    estimated_duration_seconds: float | None = None
    sound_continuity: str | None = None
    visual_continuity: str | None = None
    emotional_continuity: str | None = None

    @field_validator(
        "shot_id",
        "scene_id",
        "shot_type",
        "purpose",
        "previous_shot_relationship",
        "next_shot_relationship",
        "cut_reason",
        "sound_continuity",
        "visual_continuity",
        "emotional_continuity",
    )
    @classmethod
    def validate_shot_editorial_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)


class SequenceMontagePlan(BaseModel):
    sequence_id: str
    scene_ids: list[str] = Field(default_factory=list)
    sequence_function: str
    rhythm_progression: str
    emotional_progression: str
    tension_curve: list[str] = Field(default_factory=list)
    recurring_visual_motifs: list[str] = Field(default_factory=list)
    transition_plan: list[str] = Field(default_factory=list)
    sound_bridge_plan: list[str] = Field(default_factory=list)
    editorial_risks: list[str] = Field(default_factory=list)

    @field_validator("sequence_id", "sequence_function", "rhythm_progression", "emotional_progression")
    @classmethod
    def validate_sequence_montage_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator(
        "scene_ids",
        "tension_curve",
        "recurring_visual_motifs",
        "transition_plan",
        "sound_bridge_plan",
        "editorial_risks",
    )
    @classmethod
    def validate_sequence_montage_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class CinematicIntent(BaseModel):
    intent_id: str
    scene_id: str
    output_type: str
    subject: str
    action: str
    environment: str
    dramatic_intent: str
    framing: str
    shot_size: str
    camera_angle: str
    lens: str
    lighting: str
    color_palette: str
    composition: str
    movement: str | None = None
    mood: str
    director_lens_id: str | None = None
    directorial_intent: DirectorialIntent | None = None
    montage_intent: MontageIntent | None = None
    editorial_beats: list[EditorialBeat] = Field(default_factory=list)
    shot_editorial_purpose: ShotEditorialPurpose | None = None
    continuity_anchors: list[str] = Field(default_factory=list)
    required_elements: list[str] = Field(default_factory=list)
    forbidden_elements: list[str] = Field(default_factory=list)

    @field_validator(
        "intent_id",
        "scene_id",
        "output_type",
        "subject",
        "action",
        "environment",
        "dramatic_intent",
        "framing",
        "shot_size",
        "camera_angle",
        "lens",
        "lighting",
        "color_palette",
        "composition",
        "movement",
        "mood",
        "director_lens_id",
    )
    @classmethod
    def validate_intent_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("continuity_anchors", "required_elements", "forbidden_elements")
    @classmethod
    def validate_intent_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class PromptSpec(BaseModel):
    prompt_id: str
    scene_id: str
    output_type: str
    positive_prompt: str
    negative_prompt: str
    model_hint: str
    width: int
    height: int
    seed_hint: int | None = None
    continuity_anchors: list[str] = Field(default_factory=list)
    semantic_anchors: list[str] = Field(default_factory=list)
    editorial_purpose: ShotEditorialPurpose | None = None
    montage_intent: MontageIntent | None = None
    validation_status: str
    validation_errors: list[str] = Field(default_factory=list)

    @field_validator(
        "prompt_id",
        "scene_id",
        "output_type",
        "positive_prompt",
        "negative_prompt",
        "model_hint",
        "validation_status",
    )
    @classmethod
    def validate_prompt_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("continuity_anchors", "semantic_anchors", "validation_errors")
    @classmethod
    def validate_prompt_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class SemanticPromptValidationResult(BaseModel):
    is_valid: bool
    score: float
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    missing_required_fields: list[str] = Field(default_factory=list)
    ambiguous_terms: list[str] = Field(default_factory=list)
    forbidden_terms_detected: list[str] = Field(default_factory=list)

    @field_validator(
        "errors",
        "warnings",
        "missing_required_fields",
        "ambiguous_terms",
        "forbidden_terms_detected",
    )
    @classmethod
    def validate_validation_lists(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class VisualQAEvaluation(BaseModel):
    image_ref: str | None = None
    prompt_id: str
    semantic_match_score: float
    cinematic_match_score: float
    continuity_score: float
    detected_issues: list[str] = Field(default_factory=list)
    recommendation: str

    @field_validator("image_ref", "prompt_id", "recommendation")
    @classmethod
    def validate_qa_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("detected_issues")
    @classmethod
    def validate_qa_issues(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class ScriptToPromptRunRequest(BaseModel):
    script_text: str
    output_type: str = "storyboard_frame"
    max_scenes: int | None = 5
    scene_numbers: list[int] | None = None
    style_preset: str = "premium_cinematic_saas"
    use_llm: bool = True
    director_lens_id: str | None = "adaptive_auteur_fusion"
    montage_profile_id: str | None = "adaptive_montage"
    allow_director_reference_names: bool = False

    @field_validator("script_text", "output_type", "style_preset", "director_lens_id", "montage_profile_id")
    @classmethod
    def validate_request_text(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)


class ScriptToPromptRunResponse(BaseModel):
    sequences: list[ScriptSequence] = Field(default_factory=list)
    scenes: list[ScriptScene] = Field(default_factory=list)
    intents: list[CinematicIntent] = Field(default_factory=list)
    prompts: list[PromptSpec] = Field(default_factory=list)
    validations: list[SemanticPromptValidationResult] = Field(default_factory=list)
    qa: list[VisualQAEvaluation] = Field(default_factory=list)
    status: str
    warnings: list[str] = Field(default_factory=list)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        return _clean_text(value)

    @field_validator("warnings")
    @classmethod
    def validate_warnings(cls, values: list[str]) -> list[str]:
        return _clean_text_list(values)


class ScriptParseRequest(BaseModel):
    script_text: str
    max_scenes: int | None = 5


class ScriptParseResponse(BaseModel):
    sequences: list[ScriptSequence] = Field(default_factory=list)
    scenes: list[ScriptScene] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CinematicIntentRequest(BaseModel):
    scene: ScriptScene
    output_type: str = "storyboard_frame"
    director_lens_id: str | None = "adaptive_auteur_fusion"
    montage_profile_id: str | None = "adaptive_montage"


class PromptConstructionRequest(BaseModel):
    intent: CinematicIntent
    allow_director_reference_names: bool = False


class PromptValidationRequest(BaseModel):
    prompt: PromptSpec
    intent: CinematicIntent


class DirectorLensChooseRequest(BaseModel):
    scene: ScriptScene
    requested_lens_id: str | None = "adaptive_auteur_fusion"


class DirectorialIntentRequest(BaseModel):
    scene: ScriptScene
    cinematic_intent: CinematicIntent
    requested_lens_id: str | None = "adaptive_auteur_fusion"


class MontageIntentRequest(BaseModel):
    scene: ScriptScene
    cinematic_intent: CinematicIntent | None = None
    directorial_intent: DirectorialIntent | None = None
    requested_profile_id: str | None = "adaptive_montage"


class EditorialBeatsRequest(BaseModel):
    scene: ScriptScene


class ShotEditorialPurposeRequest(BaseModel):
    scene: ScriptScene
    shot_order: int
    shot_type: str
    montage_intent: MontageIntent
    previous_shot_type: str | None = None
    next_shot_type: str | None = None


class PromptToIntentExample(BaseModel):
    scene: ScriptScene
    intent: CinematicIntent
    prompt: PromptSpec
    validation: SemanticPromptValidationResult
    qa: VisualQAEvaluation
    metadata: dict[str, Any] = Field(default_factory=dict)
