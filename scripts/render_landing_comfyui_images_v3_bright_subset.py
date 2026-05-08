#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_DIR = ROOT / ".tmp" / "landing_comfyui_v3" / "bright_image_payloads"
JOBS_PATH = ROOT / ".tmp" / "landing_comfyui_v3" / "bright_image_render_jobs.json"
COMFYUI_PROMPT_URL = "http://127.0.0.1:8188/prompt"


def load_payloads() -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(PAYLOADS_DIR.glob("*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads


def submit_prompt(workflow: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(
        {
            "prompt": workflow,
            "client_id": f"landing-v3-bright-{uuid.uuid4().hex}",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        COMFYUI_PROMPT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_jobs(payload: Any) -> None:
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if os.environ.get("ENABLE_REAL_COMFYUI_RENDER") != "1":
        print("Render real de imagenes bright bloqueado. Usa ENABLE_REAL_COMFYUI_RENDER=1.")
        return 0

    payloads = load_payloads()
    if not payloads:
        raise RuntimeError("No bright subset payloads found. Run scripts/build_landing_comfyui_payloads_v3_bright_subset.py first.")

    jobs: list[dict[str, Any]] = []
    for payload in payloads:
        try:
            response = submit_prompt(payload["compiled_workflow"])
            jobs.append(
                {
                    "image_key": payload["image_key"],
                    "image_file_name": payload["image_file_name"],
                    "status": "queued",
                    "prompt_id": response.get("prompt_id"),
                    "response": response,
                }
            )
        except urllib.error.HTTPError as exc:
            jobs.append(
                {
                    "image_key": payload["image_key"],
                    "image_file_name": payload["image_file_name"],
                    "status": "http_error",
                    "http_status": exc.code,
                    "detail": exc.read().decode("utf-8", errors="replace"),
                }
            )
        except urllib.error.URLError as exc:
            jobs.append(
                {
                    "image_key": payload["image_key"],
                    "image_file_name": payload["image_file_name"],
                    "status": "connection_error",
                    "detail": str(exc.reason),
                }
            )

    write_jobs({"jobs": jobs})
    failures = [job for job in jobs if job.get("status") != "queued"]
    print(f"Bright image render jobs saved to {JOBS_PATH.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
