from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


@pytest.fixture(autouse=True)
def _reset_taxonomy_service():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    CinematicTaxonomyService._instance = None


def test_taxonomy_loads_expected_categories():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    taxonomy = service.get_full_taxonomy()
    expected_categories = [
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
    ]
    for cat in expected_categories:
        assert cat in taxonomy, f"Missing category: {cat}"
        assert len(taxonomy[cat]) > 0, f"Empty category: {cat}"


def test_taxonomy_elements_have_required_fields():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    taxonomy = service.get_full_taxonomy()
    for cat, elements in taxonomy.items():
        for el in elements:
            assert el.id, f"Element in {cat} missing id"
            assert el.name, f"Element {el.id} missing name"
            assert el.category, f"Element {el.id} missing category"
            assert el.description, f"Element {el.id} missing description"
            assert isinstance(el.prompt_tags, list), f"Element {el.id} prompt_tags not a list"
            assert isinstance(el.negative_prompt_tags, list), f"Element {el.id} negative_prompt_tags not a list"
            assert isinstance(el.use_cases, list), f"Element {el.id} use_cases not a list"


def test_get_category_returns_elements():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    elements = service.get_category("shot_types")
    assert len(elements) > 0
    assert all(el.category == "shot_types" for el in elements)


def test_get_category_not_found():
    from services.cinematic_taxonomy_service import (
        CategoryNotFoundError,
        CinematicTaxonomyService,
    )

    service = CinematicTaxonomyService()
    with pytest.raises(CategoryNotFoundError):
        service.get_category("nonexistent_category")


def test_presets_load_with_required_fields():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    presets = service.get_presets()
    assert len(presets) > 0
    for p in presets:
        assert p.id, f"Preset missing id"
        assert p.name, f"Preset {p.id} missing name"
        assert isinstance(p.shot_types, list)
        assert isinstance(p.composition, list)
        assert isinstance(p.camera_movements, list)
        assert isinstance(p.visual_styles, list)
        assert isinstance(p.prompt_tags, list)
        assert isinstance(p.negative_prompt_tags, list)


def test_get_preset_by_id():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    preset = service.get_preset("noir_classic")
    assert preset.id == "noir_classic"
    assert preset.name == "Classic Film Noir"
    assert "cu" in preset.shot_types
    assert "low_key" in preset.lighting_styles


def test_get_preset_not_found():
    from services.cinematic_taxonomy_service import (
        CinematicTaxonomyService,
        PresetNotFoundError,
    )

    service = CinematicTaxonomyService()
    with pytest.raises(PresetNotFoundError):
        service.get_preset("nonexistent_preset")


def test_enrich_prompt_with_preset():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    result = service.enrich_prompt(
        base_prompt="A detective walking down a rainy street",
        preset_id="noir_classic",
    )
    assert result.base_prompt == "A detective walking down a rainy street"
    assert result.enriched_prompt.startswith(result.base_prompt)
    assert result.applied_preset is not None
    assert result.applied_preset.id == "noir_classic"
    assert len(result.applied_tags) > 0
    assert any(t.source.startswith("preset:") for t in result.applied_tags)


def test_enrich_prompt_with_selected_tags():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    result = service.enrich_prompt(
        base_prompt="A couple dancing",
        selected_tags=["golden hour lighting", "romantic mood", "shallow depth of field"],
    )
    assert result.applied_preset is None
    assert len(result.applied_tags) == 3
    assert all(t.source == "user_selected" for t in result.applied_tags)


def test_enrich_prompt_with_both_preset_and_tags():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    result = service.enrich_prompt(
        base_prompt="A car chase through the city",
        preset_id="epic_blockbuster",
        selected_tags=["night time", "neon lights"],
    )
    assert result.applied_preset is not None
    assert len(result.applied_tags) >= 2  # at least preset + user tags


def test_enrich_prompt_over_tag_limit():
    from services.cinematic_taxonomy_service import (
        MAX_POSITIVE_TAGS,
        CinematicTaxonomyService,
    )

    service = CinematicTaxonomyService()
    many_tags = [f"tag_{i}" for i in range(MAX_POSITIVE_TAGS + 5)]
    result = service.enrich_prompt(
        base_prompt="A test scene",
        selected_tags=many_tags,
    )
    assert len(result.warnings) > 0
    assert any("superó el límite" in w for w in result.warnings)


def test_enrich_prompt_negative_prompt():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    result = service.enrich_prompt(
        base_prompt="A sunny beach scene",
        preset_id="noir_classic",
    )
    assert result.negative_prompt
    assert isinstance(result.negative_prompt, str)
    assert len(result.negative_prompt) > 0


def test_enrich_prompt_no_preset_no_tags():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    result = service.enrich_prompt(base_prompt="A simple scene")
    assert result.enriched_prompt == "A simple scene"
    assert result.applied_preset is None
    assert result.applied_tags == []
    assert result.negative_prompt == ""
    assert result.warnings == []


def test_taxonomy_total_elements_count():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    service = CinematicTaxonomyService()
    taxonomy = service.get_full_taxonomy()
    total = sum(len(elements) for elements in taxonomy.values())
    assert total > 30  # at least 30 elements across all categories
