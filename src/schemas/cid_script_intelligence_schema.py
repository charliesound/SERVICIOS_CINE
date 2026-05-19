from __future__ import annotations

from pydantic import BaseModel, Field


class ScriptIntelligenceAnalyzeRequest(BaseModel):
    sequence_ids: list[str] | None = None
    theory_focus: list[str] | None = None
    include_storyboard_actionables: bool = True


class ScriptIntelligenceResponse(BaseModel):
    project_id: str
    overall_diagnosis: str
    syd_field: dict
    comparato: dict
    mckee: dict
    scores: dict[str, int]
    storyboard_actionables: list[str] = Field(default_factory=list)
    theory_sources_used: list[dict] = Field(default_factory=list)
    fallback_used: bool = False
