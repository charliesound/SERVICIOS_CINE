#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8010"


def fetch_json(path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
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

    try:
        return status, json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{method} {path} -> invalid JSON") from exc


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    try:
        _health_status, health = fetch_json("/health")
        _recommend_status, recommend = fetch_json(
            "/api/ops/comfyui/recommend?"
            + urllib.parse.urlencode(
                {
                    "task_type": "storyboard",
                    "style": "cinematic_realistic",
                    "quality": "balanced",
                }
            )
        )
        _plan_status, plan = fetch_json(
            "/api/ops/comfyui/pipeline-builder",
            method="POST",
            payload={
                "task_type": "storyboard",
                "generation_mode": "SELECTED_SCENES",
                "selected_scenes": [1],
                "visual_style": "cinematic_realistic",
                "quality": "balanced",
                "speed": "medium",
            },
        )

        pipeline = plan.get("pipeline", {})

        ensure(health.get("status") == "healthy", "health status is not healthy")
        ensure(bool(recommend.get("recommendation", {}).get("workflow_id")), "recommendation.workflow_id is empty")
        ensure(bool(pipeline.get("workflow_id")), "pipeline.workflow_id is empty")
        ensure(bool(pipeline.get("checkpoint")), "pipeline.checkpoint is empty")
        ensure(pipeline.get("model_family") == "sdxl", "pipeline.model_family is not sdxl")
        ensure(pipeline.get("safe_to_render") is True, "pipeline.safe_to_render is not true")
        ensure(pipeline.get("lora") is None, "pipeline.lora must be null")
        ensure(pipeline.get("loras") == [], "pipeline.loras must be empty")
        ensure(pipeline.get("selected_scenes") == [1], "pipeline.selected_scenes must equal [1]")

        print("SMOKE PASS")
        print(json.dumps(plan, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
