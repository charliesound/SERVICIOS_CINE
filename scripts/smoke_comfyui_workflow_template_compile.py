#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8010"
BASE_PAYLOAD = {
    "task_type": "storyboard",
    "generation_mode": "SELECTED_SCENES",
    "selected_scenes": [1],
    "visual_style": "cinematic_realistic",
    "quality": "balanced",
    "speed": "medium",
    "dry_run": True,
}
COMPILE_PAYLOAD = {
    **BASE_PAYLOAD,
    "prompt": "wide cinematic shot of a lonely detective entering a neon-lit alley at night",
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
        render_dry_run = request_json(
            "/api/ops/comfyui/storyboard/render-dry-run",
            method="POST",
            payload=BASE_PAYLOAD,
        )
        compiled_preview = render_dry_run.get("compiled_workflow_preview")
        ensure(health.get("status") == "healthy", "health status is not healthy")
        ensure(isinstance(compiled_preview, dict), "compiled_workflow_preview is missing")
        ensure(compiled_preview.get("status") == "ok", "compiled_workflow_preview.status is not ok")
        ensure(compiled_preview.get("ready_for_comfyui_prompt") is True, "ready_for_comfyui_prompt is not true")
        ensure(compiled_preview.get("template_mapping_status") == "compiled", "template_mapping_status is not compiled")
        workflow = compiled_preview.get("compiled_workflow", {})
        ensure(bool(workflow), "compiled_workflow is empty")

        dumped = json.dumps(workflow, ensure_ascii=True)
        ensure("Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors" in dumped, "checkpoint missing from compiled workflow")
        ensure('1344' in dumped, "width 1344 missing from compiled workflow")
        ensure('768' in dumped, "height 768 missing from compiled workflow")
        ensure('28' in dumped, "steps 28 missing from compiled workflow")
        ensure('6.5' in dumped, "cfg 6.5 missing from compiled workflow")
        ensure('/mnt/i/COMFYUI_OK/models' not in dumped, "absolute model path leaked into compiled workflow")
        ensure('docs/validation/comfyui_models_inventory.json' not in dumped, "inventory path leaked into compiled workflow")
        ensure('.env' not in dumped, ".env reference leaked into compiled workflow")

        compile_endpoint = request_json(
            "/api/ops/comfyui/storyboard/compile-workflow-dry-run",
            method="POST",
            payload=COMPILE_PAYLOAD,
        )
        ensure(compile_endpoint.get("status") == "ok", "compile-workflow-dry-run status is not ok")
        ensure(compile_endpoint.get("validation", {}).get("valid") is True, "compiled workflow validation is not true")
        ensure(bool(compile_endpoint.get("compiled_workflow")), "compile endpoint returned empty workflow")

        print("SMOKE PASS")
        print(json.dumps(compile_endpoint, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
