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
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
PAYLOADS_DIR = ROOT / ".tmp" / "landing_comfyui_v3" / "video_payloads"
JOBS_PATH = ROOT / ".tmp" / "landing_comfyui_v3" / "video_render_jobs.json"
COMFYUI_PROMPT_URL = "http://127.0.0.1:8188/prompt"


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    return payload.get("items", [])


def submit_prompt(workflow: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(
        {
            "prompt": workflow,
            "client_id": f"landing-v3-videos-{uuid.uuid4().hex}",
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
    if os.environ.get("ENABLE_REAL_COMFYUI_VIDEO_RENDER") != "1":
        print("Render real de vídeos bloqueado. Usa ENABLE_REAL_COMFYUI_VIDEO_RENDER=1.")
        return 0

    items = load_prompt_items()
    missing_images = [
        item["image_file_name"]
        for item in items
        if not (MEDIA_DIR / item["image_file_name"]).exists()
    ]
    if missing_images:
        write_jobs(
            {
                "status": "blocked_missing_source_images",
                "missing_images": missing_images,
            }
        )
        print("Render de vídeos abortado: faltan imágenes base aprobadas.")
        return 1

    executable_payloads: list[dict[str, Any]] = []
    video_plans: list[dict[str, Any]] = []
    for path in sorted(PAYLOADS_DIR.iterdir()):
        if path.suffixes[-2:] == [".video_plan", ".json"]:
            video_plans.append(json.loads(path.read_text(encoding="utf-8")))
        elif path.suffix == ".json":
            executable_payloads.append(json.loads(path.read_text(encoding="utf-8")))

    if executable_payloads:
        jobs: list[dict[str, Any]] = []
        for payload in executable_payloads:
            try:
                response = submit_prompt(payload["compiled_workflow"])
                jobs.append(
                    {
                        "image_key": payload["image_key"],
                        "video_file_name": payload["video_file_name"],
                        "status": "queued",
                        "prompt_id": response.get("prompt_id"),
                        "response": response,
                    }
                )
            except urllib.error.HTTPError as exc:
                jobs.append(
                    {
                        "image_key": payload["image_key"],
                        "video_file_name": payload["video_file_name"],
                        "status": "http_error",
                        "http_status": exc.code,
                        "detail": exc.read().decode("utf-8", errors="replace"),
                    }
                )
            except urllib.error.URLError as exc:
                jobs.append(
                    {
                        "image_key": payload["image_key"],
                        "video_file_name": payload["video_file_name"],
                        "status": "connection_error",
                        "detail": str(exc.reason),
                    }
                )
        write_jobs({"status": "queued", "jobs": jobs})
        failures = [job for job in jobs if job.get("status") != "queued"]
        print(f"Video render jobs saved to {JOBS_PATH.relative_to(ROOT)}")
        return 1 if failures else 0

    write_jobs(
        {
            "status": "planned_only",
            "message": "No se llamó a /prompt porque todavía falta adaptar un workflow Wan/LTX de image-to-video.",
            "video_plans": video_plans,
        }
    )
    print("No se llamó a /prompt: solo existen video_plan.json y falta adaptar el workflow Wan/LTX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
