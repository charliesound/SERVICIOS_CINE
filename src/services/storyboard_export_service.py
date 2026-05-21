from __future__ import annotations

from datetime import datetime, timezone
from pathlib import PurePath
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from PIL import Image


class StoryboardExportService:
    def __init__(self) -> None:
        self._repo_root = Path(__file__).resolve().parents[2]

    def get_export_dir(self, project_id: str) -> Path:
        export_dir = self._repo_root / "data" / "exports" / "storyboards" / project_id
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def build_export_base_name(
        self,
        *,
        project_id: str,
        layout: str,
        frame_count: int,
        output_format: str,
        sheet_template: str | None = None,
    ) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        suffix = uuid4().hex[:6]
        parts = [
            "storyboard_sheet",
            project_id[:8],
        ]
        if sheet_template:
            parts.append(sheet_template)
        parts.extend([
            layout,
            f"{frame_count}f",
            output_format,
            timestamp,
            suffix,
        ])
        return "_".join(parts)

    def build_artifact_url(self, project_id: str, filename: str) -> str:
        return f"/api/projects/{project_id}/storyboard/sheet/artifacts/{quote(filename)}"

    def build_page_urls(self, project_id: str, page_paths: list[str]) -> list[str]:
        return [self.build_artifact_url(project_id, Path(path).name) for path in page_paths]

    def resolve_artifact_path(self, project_id: str, filename: str) -> Path | None:
        candidate_name = PurePath(filename)
        if not filename or any(part in ("..", "") for part in candidate_name.parts):
            return None
        if len(candidate_name.parts) != 1:
            return None

        export_dir = self.get_export_dir(project_id).resolve()
        resolved = (export_dir / candidate_name.name).resolve()
        if export_dir not in resolved.parents:
            return None
        return resolved

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
