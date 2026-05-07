#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
DEFAULT_COMFYUI_URL = "http://127.0.0.1:8188"
PAYLOAD = {
    "task_type": "storyboard",
    "generation_mode": "SELECTED_SCENES",
    "selected_scenes": [1],
    "visual_style": "cinematic_realistic",
    "quality": "balanced",
    "speed": "medium",
    "render": True,
    "dry_run": False,
    "prompt": "wide cinematic shot of a lonely detective entering a neon-lit alley at night",
}


def request_json(base_url: str, path: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {path} -> {exc.reason}") from exc

    try:
        parsed = json.loads(body) if body else None
    except json.JSONDecodeError:
        parsed = body
    return status, parsed


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def dump_body(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--poll", action="store_true")
    parser.add_argument("--allow-skip-render", action="store_true")
    parser.add_argument("--allow-timeout", action="store_true")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    parser.add_argument("--comfyui-url", default=DEFAULT_COMFYUI_URL)
    args = parser.parse_args()

    try:
        status, health = request_json(args.backend_url, "/health")
        ensure(status == 200, f"GET /health failed with HTTP {status}")
        ensure(isinstance(health, dict) and health.get("status") == "healthy", "backend health is not healthy")

        if not args.render:
            status, dry_run_body = request_json(
                args.backend_url,
                "/api/ops/comfyui/storyboard/render-dry-run",
                method="POST",
                payload={**PAYLOAD, "dry_run": True, "render": False},
            )
            ensure(status == 200, f"dry-run failed with HTTP {status}: {dump_body(dry_run_body)}")
            ensure(dry_run_body.get("status") == "planned", "dry-run status is not planned")

            status, blocked_body = request_json(
                args.backend_url,
                "/api/ops/comfyui/storyboard/render",
                method="POST",
                payload=PAYLOAD,
            )
            ensure(status == 200, f"guarded render failed with HTTP {status}: {dump_body(blocked_body)}")
            ensure(blocked_body.get("status") == "blocked", "render status is not blocked by default")
            ensure(not blocked_body.get("prompt_id"), "blocked render unexpectedly returned prompt_id")
            ensure(blocked_body.get("real_render") is not True, "blocked render unexpectedly marked real_render=true")
            print("SMOKE PASS")
            print(json.dumps(blocked_body, ensure_ascii=True, indent=2))
            return 0

        if os.environ.get("ENABLE_COMFYUI_REAL_RENDER", "").strip().lower() != "true":
            raise RuntimeError("ENABLE_COMFYUI_REAL_RENDER=true is required when using --render")

        status, comfyui_health = request_json(args.comfyui_url, "/system_stats")
        if status != 200:
            message = f"SKIPPED real render: ComfyUI health returned HTTP {status}"
            if args.allow_skip_render:
                print(message)
                return 0
            raise RuntimeError(message)
        ensure(isinstance(comfyui_health, dict), "ComfyUI /system_stats did not return JSON")

        status, queued_body = request_json(
            args.backend_url,
            "/api/ops/comfyui/storyboard/render",
            method="POST",
            payload=PAYLOAD,
        )
        ensure(status == 200, f"real render enqueue failed with HTTP {status}: {dump_body(queued_body)}")
        ensure(queued_body.get("status") == "queued", "real render did not return queued")
        ensure(bool(queued_body.get("prompt_id")), "queued render did not return prompt_id")
        ensure(
            queued_body.get("checkpoint_used") == "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            "queued render returned unexpected checkpoint",
        )
        ensure(queued_body.get("workflow_id") == "cinematic_storyboard_sdxl", "queued render returned unexpected workflow_id")

        if args.poll:
            status_url = queued_body.get("status_url")
            ensure(bool(status_url), "queued render did not return status_url")
            status_code, poll_body = request_json(
                args.backend_url,
                f"{status_url}?poll=true&timeout_seconds=30",
            )
            ensure(status_code == 200, f"poll status failed with HTTP {status_code}: {dump_body(poll_body)}")
            ensure(bool(poll_body.get("prompt_id")), "poll response did not return prompt_id")
            if poll_body.get("status") == "timeout":
                if args.allow_timeout:
                    print("SKIPPED prompt completion: poll timed out within 30s")
                    print(json.dumps(poll_body, ensure_ascii=True, indent=2))
                    return 0
                raise RuntimeError("prompt polling timed out before completion")
            ensure(poll_body.get("status") == "completed", "prompt polling did not complete successfully")
            outputs = poll_body.get("outputs", {})
            ensure(isinstance(outputs, dict), "poll outputs is not a dict")

        print("SMOKE PASS")
        print(json.dumps(queued_body, ensure_ascii=True, indent=2))
        return 0
    except RuntimeError as exc:
        if args.render and args.allow_skip_render and "ComfyUI" in str(exc):
            print(f"SKIPPED real render: {exc}")
            return 0
        print(f"SMOKE FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
