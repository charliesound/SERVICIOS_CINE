from __future__ import annotations

from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from schemas.storyboard_presentation_schema import (
    StoryboardFrame,
    StoryboardLayoutConfig,
    StoryboardLayoutName,
    StoryboardSheetPreset,
)


class StoryboardLayoutEngine:
    _LAYOUTS: dict[StoryboardLayoutName, tuple[int, int]] = {
        StoryboardLayoutName.grid_2x2: (2, 2),
        StoryboardLayoutName.grid_2x3: (2, 3),
        StoryboardLayoutName.grid_2x4: (2, 4),
        StoryboardLayoutName.grid_3x3: (3, 3),
    }

    _PRESETS = {
        StoryboardSheetPreset.clean_corporate: {
            "background": (244, 245, 247),
            "panel_bg": (255, 255, 255),
            "border": (184, 190, 198),
            "text": (20, 24, 28),
            "subtle": (92, 99, 108),
            "badge_bg": (30, 47, 91),
            "badge_text": (255, 255, 255),
        },
        StoryboardSheetPreset.cinematic_pitch: {
            "background": (28, 30, 34),
            "panel_bg": (40, 42, 47),
            "border": (92, 99, 108),
            "text": (245, 246, 248),
            "subtle": (198, 201, 206),
            "badge_bg": (204, 156, 45),
            "badge_text": (20, 20, 20),
        },
        StoryboardSheetPreset.production_sheet: {
            "background": (255, 255, 255),
            "panel_bg": (255, 255, 255),
            "border": (110, 110, 110),
            "text": (0, 0, 0),
            "subtle": (70, 70, 70),
            "badge_bg": (230, 230, 230),
            "badge_text": (0, 0, 0),
        },
        StoryboardSheetPreset.realistic_client_review: {
            "background": (248, 246, 242),
            "panel_bg": (255, 255, 255),
            "border": (162, 150, 130),
            "text": (34, 32, 28),
            "subtle": (108, 100, 90),
            "badge_bg": (121, 88, 56),
            "badge_text": (255, 250, 245),
        },
    }

    def render_pages(self, frames: list[StoryboardFrame], config: StoryboardLayoutConfig) -> list[Image.Image]:
        if not frames:
            raise ValueError("At least one storyboard frame is required")

        rows, cols = self._LAYOUTS[config.layout]
        per_page = rows * cols
        pages: list[Image.Image] = []
        total_pages = ceil(len(frames) / per_page)
        title_height = 96 if config.title else 32
        caption_height = config.caption_height_px
        palette = self._PRESETS[config.preset]
        font = ImageFont.load_default()

        cell_width = int((config.page_width_px - (2 * config.margin_px) - ((cols - 1) * config.gutter_px)) / cols)
        cell_height = int((config.page_height_px - title_height - (2 * config.margin_px) - ((rows - 1) * config.gutter_px)) / rows)
        image_height = max(120, cell_height - caption_height)

        for page_index in range(total_pages):
            canvas = Image.new("RGB", (config.page_width_px, config.page_height_px), palette["background"])
            draw = ImageDraw.Draw(canvas)
            self._draw_header(draw, config, palette, font, page_index + 1, total_pages)

            chunk = frames[page_index * per_page:(page_index + 1) * per_page]
            for idx, frame in enumerate(chunk):
                row = idx // cols
                col = idx % cols
                x = config.margin_px + col * (cell_width + config.gutter_px)
                y = config.margin_px + title_height + row * (cell_height + config.gutter_px)
                self._draw_frame_panel(
                    canvas=canvas,
                    draw=draw,
                    frame=frame,
                    x=x,
                    y=y,
                    width=cell_width,
                    height=cell_height,
                    image_height=image_height,
                    caption_height=caption_height,
                    palette=palette,
                    font=font,
                )

            pages.append(canvas)

        return pages

    def _draw_header(self, draw: ImageDraw.ImageDraw, config: StoryboardLayoutConfig, palette: dict, font, page_number: int, total_pages: int) -> None:
        title = config.title or "Storyboard Sheet"
        draw.text((config.margin_px, config.margin_px // 2), title, fill=palette["text"], font=font)
        draw.text(
            (config.margin_px, config.margin_px // 2 + 18),
            f"Layout: {config.layout.value} | Preset: {config.preset.value} | Page {page_number}/{total_pages}",
            fill=palette["subtle"],
            font=font,
        )

    def _draw_frame_panel(
        self,
        *,
        canvas: Image.Image,
        draw: ImageDraw.ImageDraw,
        frame: StoryboardFrame,
        x: int,
        y: int,
        width: int,
        height: int,
        image_height: int,
        caption_height: int,
        palette: dict,
        font,
    ) -> None:
        draw.rounded_rectangle((x, y, x + width, y + height), radius=8, fill=palette["panel_bg"], outline=palette["border"], width=2)

        image_box = (x + 12, y + 12, x + width - 12, y + 12 + image_height - 12)
        self._paste_image(canvas, draw, frame.image_path, image_box, palette, font)

        badge = f"Shot {frame.shot_number}"
        badge_width = max(62, len(badge) * 7 + 12)
        draw.rounded_rectangle((x + 14, y + 14, x + 14 + badge_width, y + 34), radius=5, fill=palette["badge_bg"])
        draw.text((x + 20, y + 19), badge, fill=palette["badge_text"], font=font)

        caption_y = y + image_height + 8
        description = frame.info.description or "No description"
        notes = frame.info.notes or ""
        scene = frame.scene_number or frame.info.scene or "n/a"
        shot_size = frame.info.shot_size or "n/a"
        lines = [
            f"Scene: {scene}",
            f"Shot size: {shot_size}",
        ]
        if frame.info.camera_angle:
            lines.append(f"Angle: {frame.info.camera_angle}")
        if frame.info.movement:
            lines.append(f"Move: {frame.info.movement}")
        if frame.info.status:
            lines.append(f"Status: {frame.info.status}")
        if description:
            lines.extend(self._wrap_text(draw, f"Action: {description}", font, width - 24, max_lines=3))
        if frame.info.dialogue:
            lines.extend(self._wrap_text(draw, f"Dialogue: {frame.info.dialogue}", font, width - 24, max_lines=2))
        if notes:
            lines.extend(self._wrap_text(draw, f"Notes: {notes}", font, width - 24, max_lines=2))

        for idx, line in enumerate(lines[:8]):
            fill = palette["text"] if idx < 3 else palette["subtle"]
            draw.text((x + 12, caption_y + idx * 14), line, fill=fill, font=font)

    def _paste_image(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, image_path: str, image_box: tuple[int, int, int, int], palette: dict, font) -> None:
        x1, y1, x2, y2 = image_box
        width = x2 - x1
        height = y2 - y1
        draw.rectangle(image_box, fill=(220, 220, 220), outline=palette["border"])
        path = Path(image_path)
        if not path.is_file():
            draw.text((x1 + 16, y1 + height // 2 - 8), "Missing image", fill=palette["subtle"], font=font)
            return
        with Image.open(path) as source:
            frame_image = source.convert("RGB")
            contained = ImageOps.contain(frame_image, (width, height))
            bg = Image.new("RGB", (width, height), (240, 240, 240))
            offset_x = (width - contained.width) // 2
            offset_y = (height - contained.height) // 2
            bg.paste(contained, (offset_x, offset_y))
            canvas.paste(bg, (x1, y1))

    def _wrap_text(self, draw: ImageDraw.ImageDraw, text: str, font, max_width: int, *, max_lines: int) -> list[str]:
        words = text.split()
        if not words:
            return []
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
                if len(lines) >= max_lines:
                    return lines[:max_lines]
        lines.append(current)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if not lines[-1].endswith("..."):
                lines[-1] = f"{lines[-1][: max(0, len(lines[-1]) - 3)]}..."
        return lines


storyboard_layout_engine = StoryboardLayoutEngine()
