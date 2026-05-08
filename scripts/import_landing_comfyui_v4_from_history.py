#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path("/opt/SERVICIOS_CINE")
JOBS_FILE = REPO / ".tmp/landing_comfyui_v4/image_render_jobs.json"
OUT_DIR = REPO / "src_frontend/public/landing-media"
MANIFEST_FILE = OUT_DIR / "_landing_v4_generated_manifest.txt"

COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://127.0.0.1:8188").rstrip("/")
POLL_SECONDS = int(os.environ.get("LANDING_HISTORY_POLL_SECONDS", "1200"))
POLL_INTERVAL = int(os.environ.get("LANDING_HISTORY_POLL_INTERVAL", "10"))


def read_json_url(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def extract_output_images(history: dict[str, Any], prompt_id: str) -> list[dict[str, Any]]:
    root = history.get(prompt_id, history)
    outputs = root.get("outputs", {}) if isinstance(root, dict) else {}

    images: list[dict[str, Any]] = []
    if not isinstance(outputs, dict):
        return images

    for output in outputs.values():
        if not isinstance(output, dict):
            continue

        output_images = output.get("images", [])
        if not isinstance(output_images, list):
            continue

        for item in output_images:
            if isinstance(item, dict) and item.get("filename"):
                images.append(item)

    return images


def build_view_url(image: dict[str, Any]) -> str:
    params = {
        "filename": image.get("filename", ""),
        "subfolder": image.get("subfolder", "") or "",
        "type": image.get("type", "output") or "output",
    }
    return f"{COMFYUI_BASE_URL}/view?{urllib.parse.urlencode(params)}"


def save_as_webp(raw: bytes, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image  # type: ignore

        image = Image.open(io.BytesIO(raw))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image.save(target_path, format="WEBP", quality=92, method=6)
    except Exception as exc:
        raise RuntimeError(
            "No se pudo convertir a WEBP. Instala Pillow con: "
            "python3 -m pip install pillow"
        ) from exc


def main() -> int:
    if not JOBS_FILE.exists():
        print(f"ERROR: missing jobs file: {JOBS_FILE}")
        return 1

    jobs_data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    jobs = jobs_data.get("jobs", [])

    if not isinstance(jobs, list) or not jobs:
        print("ERROR: no jobs found")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Polling ComfyUI history for {len(jobs)} images...")
    print(f"  ComfyUI: {COMFYUI_BASE_URL}")
    print(f"  timeout: {POLL_SECONDS}s, interval: {POLL_INTERVAL}s")

    pending = {
        job["image_key"]: job
        for job in jobs
        if isinstance(job, dict) and job.get("prompt_id")
    }

    imported: list[str] = []
    failures: list[str] = []
    deadline = time.time() + POLL_SECONDS

    while pending and time.time() < deadline:
        for image_key, job in list(pending.items()):
            prompt_id = job.get("prompt_id")
            target_file_name = (
                job.get("target_file_name")
                or job.get("image_file_name")
                or f"{image_key}.webp"
            )
            target_path = OUT_DIR / target_file_name

            try:
                history = read_json_url(f"{COMFYUI_BASE_URL}/history/{prompt_id}")
                images = extract_output_images(history, str(prompt_id))
            except Exception as exc:
                print(f"  PENDING: {image_key} history not ready: {exc}")
                continue

            if not images:
                print(f"  PENDING: {image_key} todavía sin imagen en outputs")
                continue

            image = images[0]
            view_url = build_view_url(image)

            try:
                raw = download_bytes(view_url)
                save_as_webp(raw, target_path)
                print(f"  OK: {image_key} -> {target_path}")
                print(
                    f"      source: filename={image.get('filename')} "
                    f"subfolder={image.get('subfolder')} type={image.get('type')}"
                )
                imported.append(f"{image_key} -> {target_file_name}")
                del pending[image_key]
            except Exception as exc:
                print(f"  DOWNLOAD FAILED: {image_key}: {exc}")
                print(f"      attempted: {view_url}")
                failures.append(f"{image_key}: download failed")
                del pending[image_key]

        if pending:
            time.sleep(POLL_INTERVAL)

    for image_key in pending:
        failures.append(f"{image_key}: timeout waiting for ComfyUI history")

    MANIFEST_FILE.write_text("\n".join(imported) + "\n", encoding="utf-8")
    print(f"\nManifest written: {MANIFEST_FILE}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\nImportación V4 completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
