from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.storyboard_presentation_schema import (  # noqa: E402
    StoryboardFrame,
    StoryboardFrameMetadata,
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
    StoryboardShotInfo,
)
from services.storyboard_layout_engine import storyboard_layout_engine  # noqa: E402


def _make_frame(tmp_path: Path, idx: int) -> StoryboardFrame:
    image_path = tmp_path / f"frame_{idx}.png"
    Image.new("RGB", (640, 360), color=(30 * idx % 255, 60, 90)).save(image_path)
    return StoryboardFrame(
        shot_number=idx,
        scene_number=str((idx - 1) // 2 + 1),
        image_path=str(image_path),
        info=StoryboardShotInfo(
            scene=f"Scene {idx}",
            shot_size="CU",
            description=f"Description for shot {idx}",
            notes="Wrapped note text for the board",
        ),
        metadata=StoryboardFrameMetadata(),
    )


def _render(tmp_path: Path, layout: StoryboardLayoutName, count: int):
    frames = [_make_frame(tmp_path, idx + 1) for idx in range(count)]
    config = StoryboardLayoutConfig(
        layout=layout,
        preset=StoryboardSheetPreset.clean_corporate,
        title="Storyboard Sheet",
    )
    return storyboard_layout_engine.render_pages(frames, config)


def test_grid_2x2_generates_image(tmp_path: Path) -> None:
    pages = _render(tmp_path, StoryboardLayoutName.grid_2x2, 4)
    assert len(pages) == 1
    assert pages[0].size == (1920, 1080)


def test_grid_2x3_generates_image(tmp_path: Path) -> None:
    pages = _render(tmp_path, StoryboardLayoutName.grid_2x3, 6)
    assert len(pages) == 1


def test_grid_2x4_generates_image(tmp_path: Path) -> None:
    pages = _render(tmp_path, StoryboardLayoutName.grid_2x4, 8)
    assert len(pages) == 1


def test_grid_3x3_generates_image(tmp_path: Path) -> None:
    pages = _render(tmp_path, StoryboardLayoutName.grid_3x3, 9)
    assert len(pages) == 1


def test_multiple_pages_supported(tmp_path: Path) -> None:
    pages = _render(tmp_path, StoryboardLayoutName.grid_2x2, 5)
    assert len(pages) == 2


def test_caption_wrapping_and_numbering_do_not_crash(tmp_path: Path) -> None:
    frame = _make_frame(tmp_path, 1)
    frame.info.description = "This is a much longer description that should wrap across multiple lines without breaking the layout engine rendering process."
    pages = storyboard_layout_engine.render_pages(
        [frame],
        StoryboardLayoutConfig(layout=StoryboardLayoutName.grid_2x2, preset=StoryboardSheetPreset.production_sheet, title="Wrap Test"),
    )
    assert pages[0].size == (1920, 1080)
