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


def test_build_export_base_name_is_unique_and_includes_template_and_frames() -> None:
    service = StoryboardExportService()

    first = service.build_export_base_name(
        project_id="22e14578-project",
        layout="grid_2x2",
        frame_count=4,
        output_format="png",
        sheet_template="clean_4_panel_pitch",
    )
    second = service.build_export_base_name(
        project_id="22e14578-project",
        layout="grid_2x2",
        frame_count=4,
        output_format="png",
        sheet_template="clean_4_panel_pitch",
    )

    assert first != second
    assert "22e14578" in first
    assert "clean_4_panel_pitch" in first
    assert "grid_2x2" in first
    assert "4f" in first


def test_build_artifact_url_and_page_urls() -> None:
    service = StoryboardExportService()

    artifact_url = service.build_artifact_url("proj-1", "sheet.png")
    page_urls = service.build_page_urls("proj-1", ["/tmp/page_01.png", "/tmp/page_02.png"])

    assert artifact_url == "/api/projects/proj-1/storyboard/sheet/artifacts/sheet.png"
    assert page_urls == [
        "/api/projects/proj-1/storyboard/sheet/artifacts/page_01.png",
        "/api/projects/proj-1/storyboard/sheet/artifacts/page_02.png",
    ]


def test_resolve_artifact_path_blocks_traversal(tmp_path: Path) -> None:
    service = StoryboardExportService()
    service._repo_root = tmp_path

    assert service.resolve_artifact_path("proj-1", "../secret.txt") is None
    assert service.resolve_artifact_path("proj-1", "nested/file.png") is None
