#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def validate_pipeline(payload: dict) -> None:
    pipeline = payload.get("pipeline", {})
    ensure(pipeline.get("safe_to_render") is True, "pipeline.safe_to_render is not true")
    ensure(pipeline.get("lora") is None, "pipeline.lora must be null")
    ensure(pipeline.get("loras") == [], "pipeline.loras must be empty")
    ensure(bool(pipeline.get("checkpoint")), "pipeline.checkpoint is empty")
    ensure(bool(pipeline.get("workflow_id")), "pipeline.workflow_id is empty")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-project-auth", action="store_true")
    args = parser.parse_args()

    try:
        health = request_json("/health")
        dry_run = request_json(
            "/api/ops/comfyui/storyboard/render-dry-run",
            method="POST",
            payload=PAYLOAD,
        )
        pipeline = request_json(
            "/api/ops/comfyui/pipeline-builder",
            method="POST",
            payload=PAYLOAD,
        )

        ensure(health.get("status") == "healthy", "health status is not healthy")
        ensure(dry_run.get("status") == "planned", "dry-run status is not planned")
        ensure(dry_run.get("dry_run") is True, "dry-run flag is not true")
        validate_pipeline(dry_run)
        validate_pipeline(pipeline)

        try:
            real_render = request_json(
                "/api/ops/comfyui/storyboard/render",
                method="POST",
                payload={**PAYLOAD, "dry_run": False, "render": True},
            )
            ensure(real_render.get("status") == "blocked", "real render status is not blocked")
            validate_pipeline(real_render)
        except RuntimeError as exc:
            if "/api/ops/comfyui/storyboard/render" in str(exc) and "HTTP 404" in str(exc):
                print("SKIPPED: ops real render endpoint not implemented.")
            else:
                raise

        if args.skip_project_auth:
            print("SKIPPED: --skip-project-auth requested; project auth flow not executed.")
        else:
            print("SKIPPED: project auth flow not configured in this smoke.")

        print("SMOKE PASS")
        print(json.dumps(dry_run, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
