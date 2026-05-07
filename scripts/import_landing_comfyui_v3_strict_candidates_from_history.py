#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
JOBS_PATH = ROOT / ".tmp" / "landing_comfyui_v3" / "strict_image_render_jobs.json"
CANDIDATES_DIR = ROOT / "src_frontend" / "public" / "landing-media" / "candidates"
MANIFEST_PATH = CANDIDATES_DIR / "_landing_v3_strict_candidates_manifest.txt"
COMFYUI_BASE_URL = "http://127.0.0.1:8188"


def load_jobs() -> list[dict[str, Any]]:
    payload = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return payload.get("jobs", [])


def request_json(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def request_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def extract_images(history_payload: dict[str, Any], prompt_id: str) -> list[dict[str, Any]]:
    prompt_history = history_payload.get(prompt_id, {}) if isinstance(history_payload, dict) else {}
    outputs = prompt_history.get("outputs", {}) if isinstance(prompt_history, dict) else {}
    images: list[dict[str, Any]] = []
    if isinstance(outputs, dict):
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            for image_meta in node_output.get("images", []) or []:
                if isinstance(image_meta, dict):
                    images.append(image_meta)
    return images


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


def next_candidate_path(image_key: str) -> Path:
    index = 1
    while True:
        path = CANDIDATES_DIR / f"candidate-{image_key}-strict-{index:02d}.webp"
        if not path.exists():
            return path
        index += 1


def main() -> int:
    if not JOBS_PATH.exists():
        raise FileNotFoundError(f"Missing strict render jobs file: {JOBS_PATH}")

    jobs = load_jobs()
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    manifest_lines: list[str] = []

    for job in jobs:
        if job.get("status") != "queued" or not job.get("prompt_id"):
            continue
        image_key = str(job["image_key"])
        prompt_id = str(job["prompt_id"])
        history_url = f"{COMFYUI_BASE_URL}/history/{urllib.parse.quote(prompt_id)}"
        history_payload = request_json(history_url)
        image_entries = extract_images(history_payload, prompt_id)
        if not image_entries:
            print(f"WARN no image outputs found for {image_key} ({prompt_id})")
            continue

        target_size = (1920, 1080) if image_key == "landing-hero-main-v3" else (1600, 1000)
        for image_meta in image_entries:
            if str(image_meta.get("filename", "")).lower().endswith(".exr"):
                continue
            query = urllib.parse.urlencode(
                {
                    "filename": image_meta.get("filename", ""),
                    "subfolder": image_meta.get("subfolder", ""),
                    "type": image_meta.get("type", "output"),
                }
            )
            image_bytes = request_bytes(f"{COMFYUI_BASE_URL}/view?{query}")
            dst = next_candidate_path(image_key)
            with Image.open(io.BytesIO(image_bytes)) as img:
                final = center_crop_resize(img, *target_size)
                final.save(dst, "WEBP", quality=90, method=6)
            manifest_lines.append(
                "\t".join(
                    [
                        image_key,
                        dst.name,
                        f"prompt_id={prompt_id}",
                        f"source={image_meta.get('filename', '')}",
                        f"subfolder={image_meta.get('subfolder', '')}",
                        f"type={image_meta.get('type', 'output')}",
                    ]
                )
            )
            print(f"OK {dst.name} <- {image_meta.get('filename', '')}")

    MANIFEST_PATH.write_text("\n".join(manifest_lines) + ("\n" if manifest_lines else ""), encoding="utf-8")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
