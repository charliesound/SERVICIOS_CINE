from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.storyboard_export_service import StoryboardExportService  # noqa: E402


def test_export_png_creates_file(tmp_path: Path) -> None:
    service = StoryboardExportService()
    service._repo_root = tmp_path
    page = Image.new("RGB", (400, 300), color=(255, 255, 255))

    result = service.export_png(project_id="proj-1", pages=[page], base_name="sheet")

    path = Path(result["artifact_path"])
    assert path.is_file()
    assert path.stat().st_size > 0


def test_export_pdf_creates_file(tmp_path: Path) -> None:
    service = StoryboardExportService()
    service._repo_root = tmp_path
    page = Image.new("RGB", (400, 300), color=(255, 255, 255))

    result = service.export_pdf(project_id="proj-1", pages=[page], base_name="sheet")

    path = Path(result["artifact_path"])
    assert path.is_file()
    assert path.stat().st_size > 0


def test_build_credit_estimate_uses_frame_count() -> None:
    service = StoryboardExportService()

    estimate = service.build_credit_estimate(8)

    assert estimate == {
        "billable_frames": 8,
        "pricing_unit": "storyboard_sheet_frame",
        "estimated_credits": 8,
        "credit_policy": "1 credit per included storyboard frame",
    }
