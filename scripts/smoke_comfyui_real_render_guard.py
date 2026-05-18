#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BACKEND_URL = os.environ.get("CID_BACKEND_BASE_URL", "http://127.0.0.1:8010")


def _default_comfyui_url() -> str:
    return (
        os.environ.get("COMFYUI_STILL_BASE_URL")
        or os.environ.get("COMFYUI_BASE_URL")
        or os.environ.get("COMFYUI_STORYBOARD_BASE_URL")
        or "http://127.0.0.1:8188"
    )


DEFAULT_COMFYUI_URL = _default_comfyui_url()
ENQUEUE_OK_HTTP_STATUSES = {200, 202}
ENQUEUE_OK_STATUSES = {"queued", "pending", "running", "accepted", "processing"}
INTERMEDIATE_STATUSES = {"queued", "pending", "running", "processing", "accepted", "running_or_pending"}
FINAL_OK_STATUSES = {"completed", "succeeded", "success"}
FINAL_ERROR_STATUSES = {"failed", "error"}
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


def backend_is_healthy(health: Any) -> bool:
    if not isinstance(health, dict):
        return False
    return str(health.get("status", "")).strip().lower() in {"ok", "healthy"}


def _normalized_status(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("status", "")).strip().lower()


def check_backend_health(base_url: str) -> None:
    attempts: list[tuple[str, int, Any]] = []
    for path in ("/health/live", "/health"):
        status, body = request_json(base_url, path)
        attempts.append((path, status, body))
        if status == 200 and backend_is_healthy(body):
            return

    details = "; ".join(
        f"{path} -> HTTP {status} body={dump_body(body)}"
        for path, status, body in attempts
    )
    raise RuntimeError(f"backend health is not healthy: {details}")


def build_poll_path(payload: dict[str, Any]) -> str | None:
    status_url = payload.get("status_url")
    if isinstance(status_url, str) and status_url.strip():
        return status_url.strip()

    job_id = payload.get("job_id")
    if isinstance(job_id, str) and job_id.strip():
        return f"/api/render/jobs/{job_id.strip()}"

    prompt_id = payload.get("prompt_id")
    if isinstance(prompt_id, str) and prompt_id.strip():
        return f"/api/ops/comfyui/prompt/{prompt_id.strip()}/status"

    return None


def enqueue_is_accepted(http_status: int, payload: Any) -> bool:
    if http_status not in ENQUEUE_OK_HTTP_STATUSES or not isinstance(payload, dict):
        return False

    normalized_status = _normalized_status(payload)
    has_job_id = isinstance(payload.get("job_id"), str) and bool(payload.get("job_id", "").strip())
    has_prompt_id = isinstance(payload.get("prompt_id"), str) and bool(payload.get("prompt_id", "").strip())

    if normalized_status and normalized_status in ENQUEUE_OK_STATUSES:
        return has_job_id or has_prompt_id
    if has_job_id:
        return True
    if has_prompt_id and normalized_status == "queued":
        return True
    return False


def poll_until_terminal(base_url: str, path: str, timeout_seconds: int = 30, interval_seconds: float = 2.0) -> tuple[int, Any]:
    started_at = time.monotonic()
    last_status_code = 0
    last_body: Any = None

    while True:
        status_code, body = request_json(base_url, path)
        last_status_code = status_code
        last_body = body

        if status_code >= 400:
            raise RuntimeError(
                f"poll failed for {path} with HTTP {status_code}: {dump_body(body)}"
            )

        normalized_status = _normalized_status(body)
        if normalized_status in FINAL_OK_STATUSES:
            return status_code, body
        if normalized_status in FINAL_ERROR_STATUSES:
            raise RuntimeError(
                f"poll returned terminal error status '{normalized_status}' for {path}: {dump_body(body)}"
            )
        if normalized_status == "timeout":
            raise RuntimeError(f"poll returned timeout for {path}: {dump_body(body)}")

        elapsed = time.monotonic() - started_at
        if elapsed >= timeout_seconds:
            raise RuntimeError(
                f"poll timed out after {timeout_seconds}s for {path}; last HTTP {last_status_code}: {dump_body(last_body)}"
            )

        if normalized_status and normalized_status not in INTERMEDIATE_STATUSES:
            raise RuntimeError(
                f"poll returned unsupported status '{normalized_status}' for {path}: {dump_body(body)}"
            )

        time.sleep(interval_seconds)


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
        check_backend_health(args.backend_url)

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
            print(f"SKIPPED real render: ComfyUI health returned HTTP {status} at {args.comfyui_url}")
            return 0
        ensure(isinstance(comfyui_health, dict), "ComfyUI /system_stats did not return JSON")

        status, queued_body = request_json(
            args.backend_url,
            "/api/ops/comfyui/storyboard/render",
            method="POST",
            payload=PAYLOAD,
        )
        ensure(
            enqueue_is_accepted(status, queued_body),
            f"real render enqueue returned unsupported response HTTP {status}: {dump_body(queued_body)}",
        )
        ensure(
            queued_body.get("checkpoint_used") == "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            "queued render returned unexpected checkpoint",
        )
        ensure(queued_body.get("workflow_id") == "cinematic_storyboard_sdxl", "queued render returned unexpected workflow_id")

        if args.poll:
            poll_path = build_poll_path(queued_body)
            ensure(bool(poll_path), f"queued render did not return pollable reference: {dump_body(queued_body)}")
            try:
                status_code, poll_body = poll_until_terminal(
                    args.backend_url,
                    poll_path,
                    timeout_seconds=30,
                )
            except RuntimeError as exc:
                if args.allow_timeout and "timed out" in str(exc).lower():
                    print(f"SKIPPED prompt completion: {exc}")
                    return 0
                raise
            ensure(status_code in ENQUEUE_OK_HTTP_STATUSES, f"poll status failed with HTTP {status_code}: {dump_body(poll_body)}")
            outputs = poll_body.get("outputs", {})
            ensure(isinstance(outputs, dict), "poll outputs is not a dict")

        print("SMOKE PASS")
        print(json.dumps(queued_body, ensure_ascii=True, indent=2))
        return 0
    except RuntimeError as exc:
        message = str(exc)
        if args.render and (
            "ComfyUI health returned HTTP" in message
            or "/system_stats" in message
        ):
            print(f"SKIPPED real render: {exc}")
            return 0
        print(f"SMOKE FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
