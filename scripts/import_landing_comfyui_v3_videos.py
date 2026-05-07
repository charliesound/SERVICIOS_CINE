#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
SELECTION_PATH = ROOT / ".tmp" / "landing_comfyui_v3" / "final_video_selection.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
MANIFEST_PATH = MEDIA_DIR / "_landing_v3_generated_video_manifest.txt"

VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".mkv", ".avi"}
BLOCKED_EXTENSIONS = {".exr", ".tif", ".tiff"}
MAX_COPY_BYTES = 12 * 1024 * 1024
MAX_UNOPTIMIZED_BYTES = 100 * 1024 * 1024


def default_output_dir() -> Path:
    return Path(os.sep) / "mnt" / "g" / "COMFYUI_HUB" / "output"


def output_dir() -> Path:
    raw = os.environ.get("LANDING_COMFYUI_OUTPUT_DIR", "").strip()
    return Path(raw) if raw else default_output_dir()


def ffmpeg_path() -> str | None:
    return shutil.which("ffmpeg")


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    return payload.get("items", [])


def load_selection_map() -> dict[str, str]:
    if not SELECTION_PATH.exists():
        return {}
    payload = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if all(isinstance(value, str) for value in payload.values()):
            return {str(key): str(value) for key, value in payload.items()}
        if isinstance(payload.get("items"), list):
            mapping: dict[str, str] = {}
            for item in payload["items"]:
                if isinstance(item, dict) and item.get("image_key") and item.get("source"):
                    mapping[str(item["image_key"])] = str(item["source"])
            return mapping
    return {}


def resolve_selected_source(base_dir: Path, raw_value: str) -> Path:
    candidate = Path(raw_value)
    if candidate.is_absolute():
        return candidate
    return base_dir / candidate


def discover_source(base_dir: Path, item: dict[str, Any], selection_map: dict[str, str]) -> Path:
    if not base_dir.exists():
        raise FileNotFoundError(f"Output dir not found: {base_dir}")

    selected = selection_map.get(item["image_key"])
    if selected:
        source = resolve_selected_source(base_dir, selected)
        if not source.exists():
            raise FileNotFoundError(f"Selected video source not found for {item['image_key']}: {selected}")
        return source

    file_stem = Path(item["video_file_name"]).stem.lower()
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
        if suffix in BLOCKED_EXTENSIONS or suffix not in VIDEO_EXTENSIONS:
            continue
        name = path.name.lower()
        if any(token in name for token in tokens):
            candidates.append(path)

    if not candidates:
        raise FileNotFoundError(f"No source video found for {item['image_key']}")

    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def relative_source(src: Path, base_dir: Path) -> str:
    try:
        return str(src.relative_to(base_dir)).replace("\\", "/")
    except ValueError:
        return src.name


def transcode_video(src: Path, dst: Path) -> None:
    ffmpeg = ffmpeg_path()
    if not ffmpeg:
        raise RuntimeError("ffmpeg is not available")
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(src),
        "-vf",
        "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        "26",
        "-movflags",
        "+faststart",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> int:
    source_dir = output_dir()
    selection_map = load_selection_map()
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    manifest_lines: list[str] = []
    has_ffmpeg = ffmpeg_path() is not None

    for item in load_prompt_items():
        src = discover_source(source_dir, item, selection_map)
        suffix = src.suffix.lower()
        size_bytes = src.stat().st_size

        if suffix == ".avi":
            raise RuntimeError(f"AVI no permitido para importacion final: {src.name}")
        if suffix == ".mov" and not has_ffmpeg and size_bytes >= MAX_COPY_BYTES:
            raise RuntimeError(f"MOV pesado requiere ffmpeg para optimizacion: {src.name}")
        if size_bytes > MAX_UNOPTIMIZED_BYTES and not has_ffmpeg:
            raise RuntimeError(f"Archivo >100 MB sin optimizacion disponible: {src.name}")

        dst = MEDIA_DIR / item["video_file_name"]
        if has_ffmpeg:
            transcode_video(src, dst)
        else:
            if suffix != ".mp4":
                raise RuntimeError(f"Sin ffmpeg solo se pueden copiar MP4 ya optimizados: {src.name}")
            if size_bytes >= MAX_COPY_BYTES:
                raise RuntimeError(f"Sin ffmpeg el video supera 12 MB: {src.name}")
            shutil.copy2(src, dst)

        final_size = dst.stat().st_size
        if final_size >= MAX_COPY_BYTES:
            raise RuntimeError(f"El video final supera 12 MB: {dst.name}")
        manifest_lines.append(f"{item['video_file_name']}\t{relative_source(src, source_dir)}\t{final_size}")
        print(f"OK {item['video_file_name']} <- {relative_source(src, source_dir)}")

    MANIFEST_PATH.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
