#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8010"
PAYLOAD = {
    "task_type": "storyboard",
    "generation_mode": "SELECTED_SCENES",
    "selected_scenes": [1],
    "visual_style": "cinematic_realistic",
    "quality": "balanced",
    "speed": "medium",
    "dry_run": True,
}


def request_json(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {path} -> {exc.reason}") from exc

    if status != 200:
        raise RuntimeError(f"{method} {path} -> HTTP {status}")

    return json.loads(body)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    try:
        health = request_json("/health")
        pipeline = request_json("/api/ops/comfyui/pipeline-builder", method="POST", payload=PAYLOAD)
        render = request_json(
            "/api/ops/comfyui/storyboard/render-dry-run",
            method="POST",
            payload=PAYLOAD,
        )

        render_pipeline = render.get("pipeline", {})
        preview = render.get("comfyui_payload_preview")

        ensure(health.get("status") == "healthy", "health status is not healthy")
        ensure(bool(pipeline.get("pipeline", {}).get("workflow_id")), "pipeline-builder returned empty workflow_id")
        ensure(render.get("status") == "planned", "render dry-run status is not planned")
        ensure(render.get("dry_run") is True, "render dry-run flag is not true")
        ensure(bool(render_pipeline.get("workflow_id")), "pipeline.workflow_id is empty")
        ensure(bool(render_pipeline.get("checkpoint")), "pipeline.checkpoint is empty")
        ensure(render_pipeline.get("model_family") == "sdxl", "pipeline.model_family is not sdxl")
        ensure(render_pipeline.get("safe_to_render") is True, "pipeline.safe_to_render is not true")
        ensure(render_pipeline.get("lora") is None, "pipeline.lora must be null")
        ensure(render_pipeline.get("loras") == [], "pipeline.loras must be empty")
        ensure(preview is not None, "comfyui_payload_preview is missing")
        ensure(render_pipeline.get("selected_scenes") == [1], "pipeline.selected_scenes must equal [1]")

        print("SMOKE PASS")
        print(json.dumps(render, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
