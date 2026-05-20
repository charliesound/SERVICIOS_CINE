from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.storyboard_style_preset_service import storyboard_style_preset_service  # noqa: E402


def test_realistic_client_review_positive_prompt_enrichment() -> None:
    enriched = storyboard_style_preset_service.enrich_prompt_with_storyboard_style(
        "A team walks into a conference room",
        "realistic_client_review",
    )

    lowered = enriched.lower()
    assert "client-facing" in lowered
    assert "clean professional" in lowered
    assert "consistent characters" in lowered
    assert "realistic lighting" in lowered


def test_realistic_client_review_negative_prompt() -> None:
    negative = storyboard_style_preset_service.get_negative_prompt_for_storyboard_style("realistic_client_review")

    lowered = negative.lower()
    assert "inconsistent characters" in lowered
    assert "messy composition" in lowered
    assert "distorted faces" in lowered
