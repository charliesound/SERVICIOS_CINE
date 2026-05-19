from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.job_scheduler import (  # noqa: E402
    _apply_storyboard_sketch_postprocess,
    _extract_image_asset_path,
    _should_force_sketch,
)


def test_non_realistic_styles_force_sketch_processing() -> None:
    assert _should_force_sketch("hand_drawn_storyboard") is True
    assert _should_force_sketch("rough_pencil_storyboard") is True
    assert _should_force_sketch("ink_storyboard") is True
    assert _should_force_sketch("charcoal_storyboard") is True
    assert _should_force_sketch("graphic_novel_storyboard") is True
    assert _should_force_sketch("cinematic_realistic") is False


def test_extract_image_asset_path_from_metadata_json_string() -> None:
    asset = SimpleNamespace(canonical_path=None, metadata_json='{"storage_path":"/tmp/test_storyboard.png"}')
    path = _extract_image_asset_path(asset)
    assert path is not None
    assert str(path) == "/tmp/test_storyboard.png"


def test_apply_sketch_postprocess_on_existing_image(tmp_path: Path) -> None:
    from PIL import Image

    image_path = tmp_path / "frame.png"
    Image.new("RGB", (32, 32), color=(120, 80, 60)).save(image_path)
    assert _apply_storyboard_sketch_postprocess(image_path) is True
    assert image_path.exists()
