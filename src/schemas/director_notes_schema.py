from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DirectorNoteSource(str, Enum):
    MANUAL = "manual"
    VOICE = "voice"
    IMPORTED = "imported"
    SYSTEM = "system"


class DirectorNoteOverrideLevel(str, Enum):
    OVERRIDE_MANUAL = "override_manual"
    SEQUENCE_SHOT = "sequence_shot"
    VISUAL_BIBLE = "visual_bible"
    SCRIPT_ANALYSIS = "script_analysis"
    AUTOMATIC_HEURISTIC = "automatic_heuristic"


class BlockingNotes(BaseModel):
    blocking_notes: str | None = None
    entrance_direction: str | None = None
    exit_direction: str | None = None
    eyeline_target: str | None = None
    movement_path: str | None = None
    actor_position: str | None = None
    camera_relation: str | None = None
    axis_rule: str | None = None


class DramaticIntent(BaseModel):
    tone: str | None = None
    emotional_goal: str | None = None
    suspense_level: str | None = None
    rhythm: str | None = None
    visual_metaphor: str | None = None
    director_intent: str | None = None
    montage_intent: str | None = None


class CharacterDirectorNotes(BaseModel):
    character_id: str
    character_name: str
    age_range: str | None = None
    face_description: str | None = None
    hair: str | None = None
    wardrobe: str | None = None
    body_language: str | None = None
    emotional_state: str | None = None
    continuity_constraints: list[str] = Field(default_factory=list)
    forbidden_changes: list[str] = Field(default_factory=list)
    visual_references: list[str] = Field(default_factory=list)
    blocking: BlockingNotes = Field(default_factory=BlockingNotes)
    dramatic_intent: DramaticIntent = Field(default_factory=DramaticIntent)
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.OVERRIDE_MANUAL
    reviewed_by_user: bool = True
    applied_at: str | None = None


class LocationDirectorNotes(BaseModel):
    location_id: str
    location_name: str
    period: str | None = None
    architecture_style: str | None = None
    atmosphere: str | None = None
    lighting: str | None = None
    color_palette: list[str] = Field(default_factory=list)
    textures: list[str] = Field(default_factory=list)
    spatial_layout: str | None = None
    recurring_elements: list[str] = Field(default_factory=list)
    forbidden_elements: list[str] = Field(default_factory=list)
    continuity_constraints: list[str] = Field(default_factory=list)
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.OVERRIDE_MANUAL
    reviewed_by_user: bool = True
    applied_at: str | None = None


class PropDirectorNotes(BaseModel):
    prop_id: str
    prop_name: str
    description: str | None = None
    placement: str | None = None
    dramatic_importance: str | None = None
    continuity_rule: str | None = None
    must_appear: bool = True
    forbidden_changes: list[str] = Field(default_factory=list)
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.OVERRIDE_MANUAL
    reviewed_by_user: bool = True
    applied_at: str | None = None


class SequenceDirectorNotes(BaseModel):
    sequence_id: str
    sequence_title: str | None = None
    tone: str | None = None
    rhythm: str | None = None
    emotional_goal: str | None = None
    visual_metaphor: str | None = None
    blocking: BlockingNotes = Field(default_factory=BlockingNotes)
    dramatic_intent: DramaticIntent = Field(default_factory=DramaticIntent)
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.SEQUENCE_SHOT
    reviewed_by_user: bool = True
    applied_at: str | None = None


class ShotDirectorNotes(BaseModel):
    shot_id: str | None = None
    shot_number: int | None = None
    sequence_id: str | None = None
    notes: str | None = None
    blocking: BlockingNotes = Field(default_factory=BlockingNotes)
    dramatic_intent: DramaticIntent = Field(default_factory=DramaticIntent)
    coverage_pattern_override: str | None = None
    shot_type_override: str | None = None
    priority_override: str | None = None
    reference_mode_override: str | None = None
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.SEQUENCE_SHOT
    reviewed_by_user: bool = True
    applied_at: str | None = None


class ProjectDirectorNotes(BaseModel):
    project_id: str
    project_title: str | None = None
    global_tone: str | None = None
    global_visual_style: str | None = None
    global_lighting: str | None = None
    global_atmosphere: str | None = None
    notes: str | None = None
    blocking: BlockingNotes = Field(default_factory=BlockingNotes)
    dramatic_intent: DramaticIntent = Field(default_factory=DramaticIntent)
    source: DirectorNoteSource = DirectorNoteSource.MANUAL
    override_priority: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.OVERRIDE_MANUAL
    reviewed_by_user: bool = True
    applied_at: str | None = None


class VoiceDirectorNoteDraft(BaseModel):
    source: DirectorNoteSource = DirectorNoteSource.VOICE
    transcript: str
    transcript_confidence: float = 0.0
    extracted_entities: dict[str, list[str]] = Field(default_factory=dict)
    applied_to_level: str | None = None
    reviewed_by_user: bool = False
    applied_at: str | None = None


class DirectorNoteOverride(BaseModel):
    field_path: str
    previous_value: Any = None
    new_value: Any = None
    override_source: DirectorNoteOverrideLevel = DirectorNoteOverrideLevel.OVERRIDE_MANUAL
    timestamp: str | None = None


class DirectorNotesBundle(BaseModel):
    project: ProjectDirectorNotes | None = None
    sequences: list[SequenceDirectorNotes] = Field(default_factory=list)
    shots: list[ShotDirectorNotes] = Field(default_factory=list)
    characters: list[CharacterDirectorNotes] = Field(default_factory=list)
    locations: list[LocationDirectorNotes] = Field(default_factory=list)
    props: list[PropDirectorNotes] = Field(default_factory=list)
    voice_drafts: list[VoiceDirectorNoteDraft] = Field(default_factory=list)
    overrides: list[DirectorNoteOverride] = Field(default_factory=list)
    director_note_refs: dict[str, list[str]] = Field(default_factory=dict)


class DirectorNotesResolveRequest(BaseModel):
    project_id: str
    sequence_id: str | None = None
    shot_number: int | None = None
    bundle: DirectorNotesBundle
    scene_text: str | None = None
    character_names: list[str] = Field(default_factory=list)


class PromptBlocks(BaseModel):
    prompt_positive_additions: list[str] = Field(default_factory=list)
    prompt_negative_constraints: list[str] = Field(default_factory=list)
    continuity_prompt_block: str | None = None
    character_lock_block: str | None = None
    location_lock_block: str | None = None
    prop_lock_block: str | None = None
    visual_raccord_block: str | None = None


class DirectorNotesResolveResult(BaseModel):
    project_id: str
    sequence_id: str | None = None
    shot_number: int | None = None
    prompt_blocks: PromptBlocks = Field(default_factory=PromptBlocks)
    applied_overrides: list[DirectorNoteOverride] = Field(default_factory=list)
    trace_metadata: dict[str, Any] = Field(default_factory=dict)
    voice_drafts_pending_review: list[VoiceDirectorNoteDraft] = Field(default_factory=list)
    director_note_refs: dict[str, list[str]] = Field(default_factory=dict)
    cinematic_grammar_overrides: dict[str, Any] = Field(default_factory=dict)
