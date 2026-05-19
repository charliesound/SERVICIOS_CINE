from __future__ import annotations

import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
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

    def build_storyboard_filmstrip_image(self, *, shots: list[dict[str, Any]]) -> bytes:
        ordered = sorted(
            list(shots),
            key=lambda item: (
                int(item.get("sequence_order") or 0),
                int(item.get("scene_number") or 0),
                str(item.get("shot_id") or ""),
            ),
        )
        frame_width = 300
        frame_height = 170
        label_height = 58
        tile_width = frame_width + 16
        tile_height = frame_height + label_height + 18
        strip_width = max(tile_width * max(1, len(ordered)) + 24, 360)
        strip_height = tile_height + 40

        canvas = Image.new("RGB", (strip_width, strip_height), color=(8, 8, 8))
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default()

        for x in range(0, strip_width, 32):
            draw.rectangle((x + 8, 10, x + 22, 20), fill=(230, 230, 230))
            draw.rectangle((x + 8, strip_height - 20, x + 22, strip_height - 10), fill=(230, 230, 230))

        x_cursor = 16
        for shot in ordered:
            draw.rectangle((x_cursor, 24, x_cursor + tile_width - 6, strip_height - 24), fill=(18, 18, 18), outline=(55, 55, 55), width=1)
            img_box = (x_cursor + 8, 32, x_cursor + 8 + frame_width, 32 + frame_height)
            file_path = shot.get("file_path")
            pasted = False
            if isinstance(file_path, str):
                path = Path(file_path)
                if path.is_file():
                    try:
                        with Image.open(path) as frame_img:
                            frame = frame_img.convert("RGB")
                            frame.thumbnail((frame_width, frame_height))
                            bg = Image.new("RGB", (frame_width, frame_height), (28, 28, 28))
                            off_x = (frame_width - frame.width) // 2
                            off_y = (frame_height - frame.height) // 2
                            bg.paste(frame, (off_x, off_y))
                            canvas.paste(bg, (img_box[0], img_box[1]))
                            pasted = True
                    except Exception:
                        pasted = False
            if not pasted:
                draw.rectangle(img_box, fill=(34, 34, 34))
                draw.text((img_box[0] + 74, img_box[1] + 72), "No image", fill=(190, 190, 190), font=font)

            meta_y = img_box[3] + 8
            draw.text((x_cursor + 10, meta_y), f"Plano {shot.get('sequence_order', 'n/a')}  Escena {shot.get('scene_number', 'n/a')}", fill=(240, 240, 240), font=font)
            draw.text((x_cursor + 10, meta_y + 14), f"Seq {shot.get('sequence_id', 'n/a')}  {shot.get('render_status', 'unknown')}", fill=(180, 180, 180), font=font)
            x_cursor += tile_width

        output = Path("/tmp") / f"storyboard_filmstrip_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.png"
        canvas.save(output, format="PNG")
        data = output.read_bytes()
        output.unlink(missing_ok=True)
        return data


storyboard_pdf_export_service = StoryboardPdfExportService()
