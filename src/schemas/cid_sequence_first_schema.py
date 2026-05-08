from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


class PlannedStoryboardShot(BaseModel):
    shot_number: int
    shot_type: str
    framing: str = ""
    camera_angle: str = ""
    camera_movement: str = ""
    lens_suggestion: str = ""
    action: str = ""
    characters: list[str] = Field(default_factory=list)
    location: str = ""
    lighting: str = ""
    emotional_intent: str = ""
    continuity_notes: list[str] = Field(default_factory=list)
    prompt_brief: str = ""
    negative_prompt_guidance: str = ""
    shot_plan_reason: str = ""
    script_excerpt_used: str = ""


class SequenceStoryboardPlan(BaseModel):
    project_id: str = ""
    sequence_id: str = ""
    sequence_title: str = ""
    sequence_summary: str = ""
    shot_plan: list[PlannedStoryboardShot] = Field(default_factory=list)
    continuity_plan: list[str] = Field(default_factory=list)
    visual_style_guidance: str = ""
    estimated_shot_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class ScriptSequenceMapEntry(BaseModel):
    sequence_id: str
    sequence_number: int
    title: str = ""
    script_excerpt: str = ""
    summary: str = ""
    location: str = ""
    time_of_day: str = ""
    characters: list[str] = Field(default_factory=list)
    dramatic_function: str = ""
    emotional_goal: str = ""
    visual_opportunity: str = ""
    production_complexity: str = ""
    recommended_for_storyboard: bool = False
    suggested_shot_count: int = 0
    technical_notes: list[str] = Field(default_factory=list)


class ScriptSequenceMap(BaseModel):
    project_id: str = ""
    script_id: str | None = None
    sequences: list[ScriptSequenceMapEntry] = Field(default_factory=list)
    total_sequences: int = 0
    recommended_priority_order: list[str] = Field(default_factory=list)


class ScriptSynopsisResult(BaseModel):
    logline: str = ""
    synopsis_short: str = ""
    synopsis_extended: str = ""
    premise: str = ""
    theme: str = ""
    genre: str = ""
    tone: str = ""
    main_characters: list[str] = Field(default_factory=list)
    main_locations: list[str] = Field(default_factory=list)
    dramatic_structure: str = ""
    production_notes: list[str] = Field(default_factory=list)
    recommended_storyboard_sequences: list[str] = Field(default_factory=list)
    raw_analysis: dict[str, Any] = Field(default_factory=dict)


class FullScriptAnalysisRequest(BaseModel):
    project_id: str = ""
    script_text: str = ""


class FullScriptAnalysisResult(BaseModel):
    synopsis: ScriptSynopsisResult = Field(default_factory=ScriptSynopsisResult)
    sequence_map: ScriptSequenceMap = Field(default_factory=ScriptSequenceMap)
    warnings: list[str] = Field(default_factory=list)


def resolve_sequence_entry(
    seq_map: ScriptSequenceMap,
    sequence_id: str,
) -> ScriptSequenceMapEntry | None:
    """Resolve a sequence_id (possibly in seq_01, seq_001, sequence_01, '1', '01' format)
    to a ScriptSequenceMapEntry, tolerating the 02d vs 03d padding mismatch.
    """
    # 1. Exact match
    for entry in seq_map.sequences:
        if entry.sequence_id == sequence_id:
            return entry

    # 2. Try parsing as int (plain number or zero-padded)
    number: int | None = None
    stripped = sequence_id.strip()
    if stripped.isdigit():
        number = int(stripped)
    else:
        # Try extracting digits from patterns like seq_01, seq_001, sequence_01, s01
        m = re.search(r'(?:seq|sequence|s)_?0*(\d+)$', sequence_id, re.IGNORECASE)
        if m:
            number = int(m.group(1))

    if number is not None:
        formats = (
            f"seq_{number:02d}",
            f"seq_{number:03d}",
            f"sequence_{number:02d}",
            f"sequence_{number:03d}",
            f"s_{number:02d}",
            f"s_{number:03d}",
        )
        for entry in seq_map.sequences:
            if entry.sequence_number == number:
                return entry
            if entry.sequence_id in formats:
                return entry

    return None
