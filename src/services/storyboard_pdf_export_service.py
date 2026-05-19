from __future__ import annotations

import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from weasyprint import HTML


class StoryboardPdfExportService:
    def _image_data_uri(self, file_path: str | None) -> str | None:
        if not file_path:
            return None
        path = Path(file_path)
        if not path.is_file():
            return None
        suffix = path.suffix.lower()
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(suffix)
        if not mime:
            return None
        raw = path.read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    def build_manifest(
        self,
        *,
        project_id: str,
        sequence_id: str,
        exported_at: str,
        shots: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "sequence_id": sequence_id,
            "exported_at": exported_at,
            "total_shots": len(shots),
            "shots": shots,
        }

    def render_contact_sheet_pdf(
        self,
        *,
        project_name: str,
        sequence_id: str,
        exported_at: str,
        shots: list[dict[str, Any]],
    ) -> bytes:
        cards: list[str] = []
        for shot in shots:
            image_uri = self._image_data_uri(shot.get("file_path"))
            if image_uri:
                image_block = f'<img src="{image_uri}" alt="shot" />'
            else:
                image_block = '<div class="missing">Imagen no disponible</div>'
            cards.append(
                "".join(
                    [
                        '<div class="card">',
                        image_block,
                        '<div class="meta">',
                        f"<p><strong>Plano:</strong> {shot.get('sequence_order', 'n/a')}</p>",
                        f"<p><strong>Escena:</strong> {shot.get('scene_number', 'n/a')}</p>",
                        f"<p><strong>Secuencia:</strong> {shot.get('sequence_id', sequence_id)}</p>",
                        f"<p><strong>Estado:</strong> {shot.get('render_status', 'unknown')}</p>",
                        f"<p><strong>Estilo:</strong> {shot.get('style_preset', 'n/a')}</p>",
                        f"<p><strong>Prompt:</strong> {str(shot.get('prompt_brief', ''))[:180]}</p>",
                        "</div>",
                        "</div>",
                    ]
                )
            )

        html = "".join(
            [
                "<html><head><style>",
                "@page { size: A4 landscape; margin: 12mm; }",
                "body { font-family: Arial, sans-serif; color: #111; }",
                ".header { margin-bottom: 12px; }",
                ".header h1 { font-size: 20px; margin: 0; }",
                ".header p { font-size: 11px; margin: 2px 0; color: #444; }",
                ".grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }",
                ".card { border: 1px solid #ccc; border-radius: 6px; overflow: hidden; page-break-inside: avoid; }",
                ".card img { width: 100%; height: 120px; object-fit: cover; display: block; background: #f3f3f3; }",
                ".missing { width: 100%; height: 120px; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #666; background: #f3f3f3; }",
                ".meta { padding: 6px; }",
                ".meta p { font-size: 10px; margin: 2px 0; line-height: 1.3; }",
                "</style></head><body>",
                '<div class="header">',
                f"<h1>Storyboard Contact Sheet - {project_name}</h1>",
                f"<p>Secuencia: {sequence_id}</p>",
                f"<p>Fecha export: {exported_at}</p>",
                "</div>",
                f'<div class="grid">{"".join(cards)}</div>',
                "</body></html>",
            ]
        )
        return HTML(string=html).write_pdf()


storyboard_pdf_export_service = StoryboardPdfExportService()
