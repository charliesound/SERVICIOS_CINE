from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TaxonomyElement(BaseModel):
    id: str
    name: str
    category: str
    description: str
    prompt_tags: list[str]
    negative_prompt_tags: list[str]
    use_cases: list[str]


class CinematicPreset(BaseModel):
    id: str
    name: str
    description: str
    shot_types: list[str]
    composition: list[str]
    camera_movements: list[str]
    visual_styles: list[str]
    modern_cameras: list[str]
    analog_cameras: list[str]
    film_stocks: list[str]
    lighting_styles: list[str]
    color_grading: list[str]
    narrative_styles: list[str]
    prompt_tags: list[str]
    negative_prompt_tags: list[str]


class CinematicTaxonomyResponse(BaseModel):
    categories: dict[str, list[TaxonomyElement]]
    total_elements: int


class EnrichPromptRequest(BaseModel):
    base_prompt: str
    preset_id: Optional[str] = None
    selected_tags: Optional[list[str]] = None


class AppliedTag(BaseModel):
    source: str
    tag: str


class EnrichPromptResponse(BaseModel):
    base_prompt: str
    enriched_prompt: str
    applied_preset: Optional[CinematicPreset] = None
    applied_tags: list[AppliedTag]
    negative_prompt: str
    warnings: list[str]
