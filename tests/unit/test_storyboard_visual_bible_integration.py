from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture(autouse=True)
def _reset_taxonomy_service():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    CinematicTaxonomyService._instance = None


def _make_settings(enabled: bool = True):
    return SimpleNamespace(
        visual_bible_storyboard_enrichment_enabled=enabled,
    )


def _make_vb_data(
    active_preset_id: str | None = "noir_classic",
    custom_tags: list[str] | None = None,
    is_active: bool = True,
):
    return {
        "id": "vb-test-1",
        "active_preset_id": active_preset_id,
        "custom_prompt_tags_json": custom_tags or [],
        "selected_elements_json": {},
        "prompt_mode": "tag_soup",
        "target_model": "SDXL",
        "is_active": is_active,
    }


class TestApplyVisualBibleEnrichment:
    def test_feature_flag_off_returns_base_prompt(self):
        from services.storyboard_service import storyboard_service

        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={"existing_key": "keep_me"},
            visual_bible_data=_make_vb_data(),
            settings=_make_settings(enabled=False),
        )
        assert result_prompt == "A detective"
        assert result_meta["existing_key"] == "keep_me"
        assert result_meta["visual_bible"]["enabled"] is False
        assert result_meta["visual_bible"]["applied"] is False
        assert result_meta["visual_bible"]["reason"] == "feature_flag_disabled"

    def test_no_visual_bible_data_returns_base_prompt(self):
        from services.storyboard_service import storyboard_service

        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={},
            visual_bible_data=None,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt == "A detective"
        assert result_meta["visual_bible"]["enabled"] is False
        assert result_meta["visual_bible"]["reason"] == "no_visual_bible"

    def test_no_active_rules_returns_base_prompt(self):
        from services.storyboard_service import storyboard_service

        vb_data = _make_vb_data(active_preset_id=None)
        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={},
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt == "A detective"
        assert result_meta["visual_bible"]["enabled"] is True
        assert result_meta["visual_bible"]["applied"] is False
        assert result_meta["visual_bible"]["reason"] == "no_active_rules"

    def test_inactive_visual_bible_returns_base_prompt(self):
        from services.storyboard_service import storyboard_service

        vb_data = _make_vb_data(is_active=False)
        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={},
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt == "A detective"
        assert result_meta["visual_bible"]["applied"] is False
        assert result_meta["visual_bible"]["reason"] == "no_active_rules"

    def test_preset_noir_classic_enriches_prompt(self):
        from services.storyboard_service import storyboard_service

        vb_data = _make_vb_data(active_preset_id="noir_classic")
        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective walking in the rain",
            existing_metadata={"scene_heading": "INT. OFFICE - NIGHT"},
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt.startswith("A detective walking in the rain")
        assert result_prompt != "A detective walking in the rain"
        assert result_meta["visual_bible"]["enabled"] is True
        assert result_meta["visual_bible"]["applied"] is True
        assert result_meta["visual_bible"]["active_preset_id"] == "noir_classic"
        assert result_meta["visual_bible"]["visual_bible_id"] == "vb-test-1"
        assert "enriched_prompt" in result_meta["visual_bible"]
        assert "negative_prompt" in result_meta["visual_bible"]
        assert len(result_meta["visual_bible"]["applied_tags"]) > 0
        assert result_meta["scene_heading"] == "INT. OFFICE - NIGHT"

    def test_preset_not_found_falls_back_to_base(self):
        from services.storyboard_service import storyboard_service

        vb_data = _make_vb_data(active_preset_id="nonexistent_preset_xyz")
        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={},
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt == "A detective"
        assert result_meta["visual_bible"]["applied"] is False
        assert result_meta["visual_bible"]["reason"] == "enrichment_failed"
        assert len(result_meta["visual_bible"]["warnings"]) > 0

    def test_metadata_is_preserved_after_enrichment(self):
        from services.storyboard_service import storyboard_service

        existing_meta = {
            "scene_heading": "EXT. BEACH - SUNSET",
            "shot_type": "WS",
            "continuity_notes": "consistent outfit",
        }
        vb_data = _make_vb_data(active_preset_id="epic_blockbuster")
        _result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A couple walking on the beach",
            existing_metadata=existing_meta,
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_meta["scene_heading"] == "EXT. BEACH - SUNSET"
        assert result_meta["shot_type"] == "WS"
        assert result_meta["continuity_notes"] == "consistent outfit"

    def test_dedup_removes_duplicate_tags(self):
        from services.storyboard_service import storyboard_service

        vb_data = _make_vb_data(
            active_preset_id="noir_classic",
            custom_tags=["film noir", "low key lighting", "film noir"],
        )
        result_prompt, result_meta = storyboard_service._apply_visual_bible_enrichment_to_shot_prompt(
            base_prompt="A detective",
            existing_metadata={},
            visual_bible_data=vb_data,
            settings=_make_settings(enabled=True),
        )
        assert result_prompt != "A detective"
        assert result_meta["visual_bible"]["applied"] is True
