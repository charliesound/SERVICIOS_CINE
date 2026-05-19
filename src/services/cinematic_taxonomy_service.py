from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from schemas.cinematic_taxonomy_schema import (
    AppliedTag,
    CinematicPreset,
    EnrichPromptResponse,
    TaxonomyElement,
)

MAX_POSITIVE_TAGS = 20
MAX_NEGATIVE_TAGS = 10


class CinematicTaxonomyError(Exception):
    """Base error for cinematic taxonomy operations."""


class TaxonomyLoadError(CinematicTaxonomyError):
    """Raised when taxonomy YAML cannot be loaded."""


class CategoryNotFoundError(CinematicTaxonomyError):
    """Raised when a requested category does not exist."""


class PresetNotFoundError(CinematicTaxonomyError):
    """Raised when a requested preset does not exist."""


class CinematicTaxonomyService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._elements: dict[str, list[TaxonomyElement]] = {}
        self._presets: dict[str, CinematicPreset] = {}
        self._load_taxonomy()

    def _taxonomy_path(self, config_path: Optional[str] = None) -> Path:
        if config_path:
            return Path(config_path)
        return Path(__file__).parent.parent / "config" / "cinematic_taxonomy.yml"

    def _load_taxonomy(self, config_path: Optional[str] = None) -> None:
        path = self._taxonomy_path(config_path)
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except FileNotFoundError as e:
            raise TaxonomyLoadError(f"Taxonomy file not found: {path}") from e
        except yaml.YAMLError as e:
            raise TaxonomyLoadError(f"Invalid YAML in taxonomy file: {e}") from e

        categories = set()
        for category_name in (
            "shot_types",
            "composition",
            "camera_movements",
            "visual_styles",
            "modern_cameras",
            "analog_cameras",
            "film_stocks",
            "lighting_styles",
            "color_grading",
            "narrative_styles",
        ):
            raw_list = data.get(category_name, [])
            elements = []
            for raw in raw_list:
                element = TaxonomyElement(
                    id=raw["id"],
                    name=raw["name"],
                    category=raw.get("category", category_name),
                    description=raw.get("description", ""),
                    prompt_tags=raw.get("prompt_tags", []),
                    negative_prompt_tags=raw.get("negative_prompt_tags", []),
                    use_cases=raw.get("use_cases", []),
                )
                elements.append(element)
                categories.add(element.category)
            self._elements[category_name] = elements

        raw_presets = data.get("cinematic_presets", [])
        for raw in raw_presets:
            preset = CinematicPreset(
                id=raw["id"],
                name=raw["name"],
                description=raw.get("description", ""),
                shot_types=raw.get("shot_types", []),
                composition=raw.get("composition", []),
                camera_movements=raw.get("camera_movements", []),
                visual_styles=raw.get("visual_styles", []),
                modern_cameras=raw.get("modern_cameras", []),
                analog_cameras=raw.get("analog_cameras", []),
                film_stocks=raw.get("film_stocks", []),
                lighting_styles=raw.get("lighting_styles", []),
                color_grading=raw.get("color_grading", []),
                narrative_styles=raw.get("narrative_styles", []),
                prompt_tags=raw.get("prompt_tags", []),
                negative_prompt_tags=raw.get("negative_prompt_tags", []),
            )
            self._presets[preset.id] = preset

    def get_full_taxonomy(self) -> dict[str, list[TaxonomyElement]]:
        return dict(self._elements)

    def get_category(self, category_name: str) -> list[TaxonomyElement]:
        if category_name not in self._elements:
            raise CategoryNotFoundError(f"Category '{category_name}' not found. Available: {list(self._elements.keys())}")
        return list(self._elements[category_name])

    def get_presets(self) -> list[CinematicPreset]:
        return list(self._presets.values())

    def get_preset(self, preset_id: str) -> CinematicPreset:
        if preset_id not in self._presets:
            raise PresetNotFoundError(f"Preset '{preset_id}' not found. Available: {list(self._presets.keys())}")
        return self._presets[preset_id]

    def enrich_prompt(
        self,
        base_prompt: str,
        preset_id: Optional[str] = None,
        selected_tags: Optional[list[str]] = None,
    ) -> EnrichPromptResponse:
        warnings: list[str] = []
        applied_tags: list[AppliedTag] = []
        positive_tags: list[str] = []
        negative_tags: list[str] = []
        applied_preset: Optional[CinematicPreset] = None

        if preset_id:
            applied_preset = self.get_preset(preset_id)
            positive_tags.extend(applied_preset.prompt_tags)
            negative_tags.extend(applied_preset.negative_prompt_tags)
            for tag in applied_preset.prompt_tags:
                applied_tags.append(AppliedTag(source=f"preset:{preset_id}", tag=tag))
            for tag in applied_preset.negative_prompt_tags:
                applied_tags.append(AppliedTag(source=f"preset:{preset_id}_negative", tag=tag))

        if selected_tags:
            for tag in selected_tags:
                if tag not in positive_tags:
                    positive_tags.append(tag)
                    applied_tags.append(AppliedTag(source="user_selected", tag=tag))

        if len(positive_tags) > MAX_POSITIVE_TAGS:
            warnings.append(
                f"Se superó el límite de {MAX_POSITIVE_TAGS} tags positivos "
                f"({len(positive_tags)} aplicados). El prompt puede ser demasiado complejo."
            )

        if len(negative_tags) > MAX_NEGATIVE_TAGS:
            warnings.append(
                f"Se superó el límite de {MAX_NEGATIVE_TAGS} tags negativos "
                f"({len(negative_tags)} aplicados). Los resultados pueden ser restrictivos."
            )

        enriched_parts = [base_prompt]
        if positive_tags:
            enriched_parts.append(" | ".join(positive_tags))
        enriched_prompt = ". ".join(enriched_parts)

        combined_negative = ", ".join(negative_tags) if negative_tags else ""

        return EnrichPromptResponse(
            base_prompt=base_prompt,
            enriched_prompt=enriched_prompt,
            applied_preset=applied_preset,
            applied_tags=applied_tags,
            negative_prompt=combined_negative,
            warnings=warnings,
        )


cinematic_taxonomy_service = CinematicTaxonomyService()
