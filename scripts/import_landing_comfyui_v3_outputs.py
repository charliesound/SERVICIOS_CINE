#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
MANIFEST_PATH = MEDIA_DIR / "_landing_v3_generated_manifest.txt"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
BLOCKED_EXTENSIONS = {".exr", ".tif", ".tiff", ".mp4", ".mov", ".avi", ".webm", ".mkv"}
HERO_FILE = "landing-hero-main-v3.webp"


def default_output_dir() -> Path:
    return Path(os.sep) / "mnt" / "g" / "COMFYUI_HUB" / "output"


def output_dir() -> Path:
    raw = os.environ.get("LANDING_COMFYUI_OUTPUT_DIR", "").strip()
    return Path(raw) if raw else default_output_dir()


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    return payload.get("items", [])


def center_crop_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    img = img.convert("RGB")
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)

    return img.crop(box).resize((target_w, target_h), Image.LANCZOS)


def discover_source(base_dir: Path, item: dict[str, Any]) -> Path:
    if not base_dir.exists():
        raise FileNotFoundError(f"Output dir not found: {base_dir}")

    file_stem = Path(item["image_file_name"]).stem.lower()
    tokens = {
        file_stem,
        item["image_key"].lower(),
        file_stem.replace("-", "_"),
        item["image_key"].lower().replace("-", "_"),
    }

    candidates: list[Path] = []
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in BLOCKED_EXTENSIONS:
            continue
        if suffix not in IMAGE_EXTENSIONS:
            continue
        name = path.name.lower()
        if any(token in name for token in tokens):
            candidates.append(path)

    if not candidates:
        raise FileNotFoundError(f"No source image found for {item['image_key']}")

    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def export_webp(src: Path, dst: Path, size: tuple[int, int]) -> None:
    with Image.open(src) as img:
        final = center_crop_resize(img, *size)
        final.save(dst, "WEBP", quality=90, method=6)


def relative_source(src: Path, base_dir: Path) -> str:
    try:
        return str(src.relative_to(base_dir)).replace("\\", "/")
    except ValueError:
        return src.name


def main() -> int:
    source_dir = output_dir()
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    manifest_lines: list[str] = []
    for item in load_prompt_items():
        src = discover_source(source_dir, item)
        target_name = item["image_file_name"]
        target_size = (1920, 1080) if target_name == HERO_FILE else (1600, 1000)
        dst = MEDIA_DIR / target_name
        export_webp(src, dst, target_size)
        manifest_lines.append(f"{target_name}\t{relative_source(src, source_dir)}")
        print(f"OK {target_name} <- {relative_source(src, source_dir)}")

    MANIFEST_PATH.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
