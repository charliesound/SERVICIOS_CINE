from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.storyboard_presentation_schema import (  # noqa: E402
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
    StoryboardSheetRequest,
)


def test_layouts_valid() -> None:
    for layout in StoryboardLayoutName:
        cfg = StoryboardLayoutConfig(layout=layout, preset=StoryboardSheetPreset.clean_corporate)
        assert cfg.layout == layout


def test_layout_invalid_fails() -> None:
    with pytest.raises(ValidationError):
        StoryboardLayoutConfig(layout="grid_9x9", preset=StoryboardSheetPreset.clean_corporate)


def test_preset_valid() -> None:
    cfg = StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.realistic_client_review)
    assert cfg.preset == StoryboardSheetPreset.realistic_client_review


def test_storyboard_presentation_schema_accepts_realistic_client_review() -> None:
    req = StoryboardSheetRequest(
        project_id="proj-1",
        layout=StoryboardLayoutConfig(
            layout=StoryboardLayoutName.grid_2x3,
            preset=StoryboardSheetPreset.realistic_client_review,
        ),
        output_format="pdf",
    )
    assert req.layout.preset == StoryboardSheetPreset.realistic_client_review
    assert req.frame_selection_mode == "first"


def test_storyboard_presentation_schema_accepts_max_frames() -> None:
    req = StoryboardSheetRequest(
        project_id="proj-1",
        layout=StoryboardLayoutConfig(
            layout=StoryboardLayoutName.grid_2x2,
            preset=StoryboardSheetPreset.realistic_client_review,
        ),
        output_format="png",
        max_frames=8,
    )
    assert req.max_frames == 8


def test_output_format_valid() -> None:
    req = StoryboardSheetRequest(
        project_id="proj-1",
        layout=StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.clean_corporate),
        output_format="png",
    )
    assert req.output_format == "png"


def test_output_format_invalid() -> None:
    with pytest.raises(ValidationError):
        StoryboardSheetRequest(
            project_id="proj-1",
            layout=StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.clean_corporate),
            output_format="jpg",
        )


@pytest.mark.parametrize("max_frames", [0, -1, 101])
def test_max_frames_invalid(max_frames: int) -> None:
    with pytest.raises(ValidationError):
        StoryboardSheetRequest(
            project_id="proj-1",
            layout=StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.clean_corporate),
            output_format="png",
            max_frames=max_frames,
        )


def test_frame_selection_mode_invalid() -> None:
    with pytest.raises(ValidationError):
        StoryboardSheetRequest(
            project_id="proj-1",
            layout=StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.clean_corporate),
            output_format="png",
            frame_selection_mode="latest",
        )
