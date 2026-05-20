from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PIL import Image, ImageDraw

from schemas.storyboard_presentation_schema import (
    StoryboardFrame,
    StoryboardFrameMetadata,
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
    StoryboardShotInfo,
)
from services.storyboard_export_service import storyboard_export_service
from services.storyboard_layout_engine import storyboard_layout_engine


def _make_dummy_frame(image_path: Path, index: int) -> StoryboardFrame:
    image = Image.new("RGB", (960, 540), color=((index * 35) % 255, 70, 120))
    draw = ImageDraw.Draw(image)
    draw.text((30, 30), f"Dummy Shot {index}", fill=(255, 255, 255))
    image.save(image_path)
    return StoryboardFrame(
        shot_number=index,
        scene_number=str((index - 1) // 2 + 1),
        image_path=str(image_path),
        info=StoryboardShotInfo(
            scene=f"INT. SMOKE {index}",
            shot_size="CU" if index % 2 else "WS",
            description=f"Smoke frame {index} generated locally for storyboard sheet validation.",
            notes="Dummy layout note",
        ),
        metadata=StoryboardFrameMetadata(),
    )


def main() -> None:
    smoke_dir = ROOT / "data" / "exports" / "storyboards" / "smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for index in range(1, 7):
        frames.append(_make_dummy_frame(smoke_dir / f"dummy_{index:02d}.png", index))

    config = StoryboardLayoutConfig(
        layout=StoryboardLayoutName.grid_2x3,
        preset=StoryboardSheetPreset.clean_corporate,
        title="Smoke Storyboard Sheet",
    )
    pages = storyboard_layout_engine.render_pages(frames, config)
    png_result = storyboard_export_service.export_png(project_id="smoke", pages=pages, base_name="storyboard_sheet_smoke")
    pdf_result = storyboard_export_service.export_pdf(project_id="smoke", pages=pages, base_name="storyboard_sheet_smoke")

    print("PNG:")
    for path in png_result["page_paths"]:
        p = Path(path)
        print(f"- {p} ({p.stat().st_size} bytes)")

    print("PDF:")
    pdf_path = Path(pdf_result["artifact_path"])
    print(f"- {pdf_path} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
