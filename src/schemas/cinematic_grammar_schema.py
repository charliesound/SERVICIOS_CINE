from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CinematicShotType(str, Enum):
    EXTREME_LONG_SHOT = "extreme_long_shot"
    LONG_SHOT = "long_shot"
    MEDIUM_LONG_SHOT = "medium_long_shot"
    MEDIUM_SHOT = "medium_shot"
    MEDIUM_CLOSE_UP = "medium_close_up"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    POV = "pov"
    OVER_THE_SHOULDER = "over_the_shoulder"
    INSERT = "insert"
    TWO_SHOT = "two_shot"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"
    DUTCH_ANGLE = "dutch_angle"
    AERIAL = "aerial"
    MACRO = "macro"
    REVERSE = "reverse"


class CoveragePattern(str, Enum):
    CLASSIC_COVERAGE = "classic_coverage"
    THREAT_COVERAGE = "threat_coverage"
    SUSPENSE_COVERAGE = "suspense_coverage"
    EXPLORATION_COVERAGE = "exploration_coverage"
    ACTION_LINEAR = "action_linear"
    DIALOGUE_COVERAGE = "dialogue_coverage"
    CONFRONTATION_COVERAGE = "confrontation_coverage"
    DISCOVERY_COVERAGE = "discovery_coverage"
    TRANSITION_COVERAGE = "transition_coverage"
    EMOTIONAL_COVERAGE = "emotional_coverage"
    SOUND_FOCUS_COVERAGE = "sound_focus_coverage"


class ContinuityRule(str, Enum):
    EYELINE_MATCH = "eyeline_match"
    MATCH_ON_ACTION = "match_on_action"
    CROSS_CUTTING = "cross_cutting"
    JUMP_CUT = "jump_cut"
    CONTINUITY_CUT = "continuity_cut"
    MONTAGE = "montage"
    AXIS_OF_ACTION = "axis_of_action"
    SCREEN_DIRECTION = "screen_direction"
    SOUND_BRIDGE = "sound_bridge"
    MATCH_CUT = "match_cut"
    CUTAWAY = "cutaway"
    INSERT_CUT = "insert_cut"


class EditorialRole(str, Enum):
    ESTABLISHING = "establishing"
    MASTER = "master"
    COVERAGE = "coverage"
    INSERT = "insert"
    REACTION = "reaction"
    POV = "pov"
    TRANSITION = "transition"
    CLOSING = "closing"
    BRIDGE = "bridge"
    SOUND_DETAIL = "sound_detail"
    THREAT_INDICATOR = "threat_indicator"
    ACTION_BEAT = "action_beat"


class ShotPriority(str, Enum):
    MUST_HAVE = "must_have"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class CinematicFunction(str, Enum):
    ESTABLISH_CONTEXT = "establish_context"
    EXPOSITION = "exposition"
    BUILD_TENSION = "build_tension"
    REVEAL_THREAT = "reveal_threat"
    ACTION_BEAT = "action_beat"
    DIALOGUE = "dialogue"
    REACTION = "reaction"
    ATMOSPHERE = "atmosphere"
    SOUND_FOCUS = "sound_focus"
    TRANSITION_DEVICE = "transition_device"
    DISCOVERY = "discovery"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class SceneType(str, Enum):
    SUSPENSE = "suspense"
    TERROR = "terror"
    INTERIOR_EXPLORATION = "interior_exploration"
    PURSUIT = "pursuit"
    DIALOGUE = "dialogue"
    CONFRONTATION = "confrontation"
    PHYSICAL_ACTION = "physical_action"
    DISCOVERY = "discovery"
    TRANSITION = "transition"
    EMOTIONAL_SCENE = "emotional_scene"
    KEY_OBJECT = "key_object"
    IMPORTANT_SOUND = "important_sound"


class ReferenceMode(str, Enum):
    FILMIC = "filmic"
    LITERARY = "literary"
    MIXED = "mixed"


class BeatType(str, Enum):
    ACTION = "action"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    ATMOSPHERE = "atmosphere"
    REACTION = "reaction"
    TRANSITION = "transition"
    SOUND = "sound"
    REVEAL = "reveal"


class CinematicShotSpec(BaseModel):
    shot_number: int
    coverage_pattern: CoveragePattern
    reference_mode: ReferenceMode = ReferenceMode.FILMIC
    shot_type: CinematicShotType
    coverage_role: EditorialRole
    beat_type: BeatType | None = None
    dramatic_function: CinematicFunction | None = None
    edit_role: EditorialRole | None = None
    edit_reason: str | None = None
    continuity_note: str | None = None
    eyeline_note: str | None = None
    sound_visualization_note: str | None = None
    camera_angle: str | None = None
    lens_suggestion: str | None = None
    movement: str | None = None
    priority: ShotPriority = ShotPriority.MEDIUM
    prompt_intent: str | None = None
    montage_note: str | None = None
    raccord_note: str | None = None
    character_continuity_note: str | None = None
    character_reference_id: str | None = None
    wardrobe_continuity_note: str | None = None
    prop_continuity_note: str | None = None
    set_continuity_note: str | None = None
    location_reference_id: str | None = None
    lighting_continuity_note: str | None = None
    atmosphere_continuity_note: str | None = None
    axis_continuity_note: str | None = None
    movement_direction_note: str | None = None
    visual_raccord_note: str | None = None
    cinematic_grammar_version: str = "v0.1"


class OrderedShotPlan(BaseModel):
    scene_type: SceneType
    coverage_pattern: CoveragePattern
    shots: list[CinematicShotSpec] = Field(default_factory=list)
    continuity_rules: list[ContinuityRule] = Field(default_factory=list)
    cinematic_grammar_version: str = "v0.1"


class CinematicGrammarRequest(BaseModel):
    scene_text: str
    scene_type_hint: SceneType | None = None
    character_names: list[str] = Field(default_factory=list)
    beats: list[BeatType] = Field(default_factory=list)
    reference_mode: ReferenceMode = ReferenceMode.FILMIC


class CinematicGrammarResult(BaseModel):
    plan: OrderedShotPlan
    scene_text: str
    detected_scene_type: SceneType
    confidence: float
    cinematic_grammar_version: str = "v0.1"
