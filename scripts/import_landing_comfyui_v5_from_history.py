#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JOBS_PATH = ROOT / ".tmp" / "landing_comfyui_v5" / "image_render_jobs.json"
MANIFEST_PATH = ROOT / "src_frontend" / "public" / "landing-media" / "_landing_v5_generated_manifest.txt"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://127.0.0.1:8188")

POLL_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 5


def load_jobs() -> list[dict[str, Any]]:
    if not JOBS_PATH.exists():
        raise FileNotFoundError(f"No render jobs found at {JOBS_PATH}. Run render script first.")
    data = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return data.get("jobs", [])


def query_history(prompt_id: str) -> dict[str, Any] | None:
    url = f"{COMFYUI_BASE_URL}/history/{prompt_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    except urllib.error.URLError:
        return None


def extract_image_filename(outputs: dict[str, Any]) -> str | None:
    for node_id, node_data in outputs.items():
        if not isinstance(node_data, dict):
            continue
        images = node_data.get("images")
        if not isinstance(images, list):
            continue
        for img in images:
            if not isinstance(img, dict):
                continue
            for key in ("filename", "file_name", "image_file_name"):
                value = img.get(key)
                if value and isinstance(value, str):
                    return value
        for img in images:
            if isinstance(img, dict):
                nested = img.get("outputs")
                if isinstance(nested, dict):
                    result = extract_image_filename(nested)
                    if result:
                        return result
    return None


def download_image(filename: str, subfolder: str, output_path: Path) -> bool:
    url = f"{COMFYUI_BASE_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(data)
            return True
    except Exception as exc:
        print(f"    DOWNLOAD FAILED: {exc}")
        return False


def main() -> int:
    jobs = load_jobs()
    if not jobs:
        raise RuntimeError("No render jobs found")

    queued_jobs = [j for j in jobs if j.get("status") == "queued"]
    if not queued_jobs:
        raise RuntimeError("No queued jobs found. All jobs had errors.")

    print(f"=== Import Landing V5 Images from ComfyUI History ===\n")
    print(f"Polling ComfyUI history for {len(queued_jobs)} images...")
    print(f"  timeout: {POLL_TIMEOUT_SECONDS}s, interval: {POLL_INTERVAL_SECONDS}s")

    manifest_lines: list[str] = []
    failures: list[str] = []

    for job in queued_jobs:
        image_key = job["image_key"]
        target_file = job["target_file_name"]
        prompt_id = job.get("prompt_id")
        mode = job.get("mode", "unknown")
        if not prompt_id:
            failures.append(f"{image_key}: no prompt_id")
            continue

        print(f"  {image_key} [{mode}] -> prompt_id={prompt_id}")

        start_time = time.time()
        result: dict[str, Any] | None = None
        while time.time() - start_time < POLL_TIMEOUT_SECONDS:
            time.sleep(POLL_INTERVAL_SECONDS)
            history = query_history(prompt_id)
            if history is None:
                continue
            prompt_data = history.get(prompt_id)
            if prompt_data is None:
                continue
            outputs = prompt_data.get("outputs")
            if outputs:
                result = {"outputs": outputs}
                break

        if result is None:
            failures.append(f"{image_key}: timeout after {POLL_TIMEOUT_SECONDS}s")
            print(f"    TIMEOUT")
            continue

        outputs = result.get("outputs", {})
        filename = extract_image_filename(outputs)
        if not filename:
            failures.append(f"{image_key}: could not extract filename from outputs")
            print(f"    NO FILENAME in outputs")
            continue

        subfolder = f"landing_v5/{image_key}"
        output_path = MEDIA_DIR / target_file
        if output_path.exists():
            print(f"    EXISTS (skipped): {target_file}")
            manifest_lines.append(f"{image_key}\t{target_file}\tstatus=exists\tmode={mode}")
            continue

        success = download_image(filename, subfolder, output_path)
        if success:
            print(f"    IMPORTED: {target_file} (from {filename}) [{mode}]")
            manifest_lines.append(f"{image_key}\t{target_file}\tstatus=imported\tsource={filename}\tmode={mode}")
        else:
            failures.append(f"{image_key}: download failed")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"\nManifest written: {MANIFEST_PATH.relative_to(ROOT)}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\nAll {len(queued_jobs)} images imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
