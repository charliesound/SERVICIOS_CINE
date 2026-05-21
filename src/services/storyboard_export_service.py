from __future__ import annotations

from pathlib import Path

from PIL import Image


class StoryboardExportService:
    def __init__(self) -> None:
        self._repo_root = Path(__file__).resolve().parents[2]

    def get_export_dir(self, project_id: str) -> Path:
        export_dir = self._repo_root / "data" / "exports" / "storyboards" / project_id
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def export_png(self, *, project_id: str, pages: list[Image.Image], base_name: str = "storyboard_sheet") -> dict[str, object]:
        if not pages:
            raise ValueError("At least one page is required to export PNG")
        export_dir = self.get_export_dir(project_id)
        page_paths: list[str] = []
        for index, page in enumerate(pages, start=1):
            suffix = "" if len(pages) == 1 else f"_page_{index:02d}"
            path = export_dir / f"{base_name}{suffix}.png"
            page.save(path, format="PNG")
            page_paths.append(str(path))
        return {
            "artifact_path": page_paths[0],
            "page_paths": page_paths,
            "page_count": len(page_paths),
        }

    def export_pdf(self, *, project_id: str, pages: list[Image.Image], base_name: str = "storyboard_sheet") -> dict[str, object]:
        if not pages:
            raise ValueError("At least one page is required to export PDF")
        export_dir = self.get_export_dir(project_id)
        pdf_path = export_dir / f"{base_name}.pdf"
        rgb_pages = [page.convert("RGB") for page in pages]
        first, *rest = rgb_pages
        first.save(pdf_path, format="PDF", save_all=True, append_images=rest)
        return {
            "artifact_path": str(pdf_path),
            "page_paths": [str(pdf_path)],
            "page_count": len(pages),
        }

    def build_credit_estimate(self, frame_count: int) -> dict[str, object]:
        return {
            "billable_frames": frame_count,
            "pricing_unit": "storyboard_sheet_frame",
            "estimated_credits": frame_count,
            "credit_policy": "1 credit per included storyboard frame",
        }


storyboard_export_service = StoryboardExportService()
