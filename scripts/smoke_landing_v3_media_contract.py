#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
FRONTEND_DIR = ROOT / "src_frontend" / "src"
LANDING_COMPONENTS_DIR = FRONTEND_DIR / "components" / "landing"

IMAGE_LIMIT_BYTES = 2 * 1024 * 1024
VIDEO_LIMIT_BYTES = 12 * 1024 * 1024
OLD_REFERENCES = [
    "hero-cinematic",
    "pipeline-frame",
    "storyboard-panel",
    "moodboard-frame",
    "delivery-frame",
    "studio-interface",
    "character-scene",
    "bg-abstract",
    "cinematic-frame",
]


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    return payload.get("items", [])


def read_frontend_sources() -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = []
    for path in FRONTEND_DIR.rglob("*"):
        if path.suffix not in {".ts", ".tsx", ".css", ".md"}:
            continue
        sources.append((path, path.read_text(encoding="utf-8", errors="ignore")))
    return sources


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    items = load_prompt_items()
    if len(items) != 10:
        fail("Prompt pack must contain 10 items")

    frontend_sources = read_frontend_sources()
    frontend_blob = "\n".join(text for _, text in frontend_sources)

    for item in items:
        image_name = item["image_file_name"]
        image_path = MEDIA_DIR / image_name
        if not image_path.exists():
            fail(f"Missing image: {image_name}")
        if image_path.suffix.lower() != ".webp":
            fail(f"Image is not WebP: {image_name}")
        if image_path.stat().st_size >= IMAGE_LIMIT_BYTES:
            fail(f"Image exceeds 2 MB: {image_name}")
        if image_name not in frontend_blob:
            fail(f"Frontend does not reference image: {image_name}")

    referenced_videos = sorted(set(re.findall(r"landing-[a-z0-9-]+-v3\.(?:mp4|webm)", frontend_blob)))
    for video_name in referenced_videos:
        video_path = MEDIA_DIR / video_name
        if not video_path.exists():
            fail(f"Frontend references missing video: {video_name}")
        if video_path.suffix.lower() not in {".mp4", ".webm"}:
            fail(f"Invalid video extension: {video_name}")
        if video_path.stat().st_size >= VIDEO_LIMIT_BYTES:
            fail(f"Video exceeds 12 MB: {video_name}")

    for path in MEDIA_DIR.iterdir():
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".exr":
            fail(f"EXR is not allowed in landing media: {path.name}")
        if suffix == ".mov":
            fail(f"MOV is not allowed in landing media: {path.name}")

    for old_reference in OLD_REFERENCES:
        if old_reference in frontend_blob:
            fail(f"Old landing reference still present: {old_reference}")

    if "/mnt/g" in frontend_blob or "G:\\" in frontend_blob or "C:\\" in frontend_blob:
        fail("Frontend contains absolute local paths")

    print("SMOKE PASS")
    print(f"Checked images: {len(items)}")
    print(f"Checked video references: {len(referenced_videos)}")
    print(f"Scanned frontend files: {len(frontend_sources)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"SMOKE FAIL: {exc}")
        raise SystemExit(1)
