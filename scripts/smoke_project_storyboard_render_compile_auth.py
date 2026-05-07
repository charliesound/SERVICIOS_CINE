#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BACKEND_URL = "http://127.0.0.1:8010"
SMOKE_PASSWORD = "SmokeTest123!"


def make_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    token: str | None = None,
) -> tuple[int, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        f"{base_url}{path}",
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


def validate_pipeline(pipeline: dict[str, Any]) -> None:
    ensure(bool(pipeline.get("workflow_id")), "pipeline.workflow_id is empty")
    ensure(bool(pipeline.get("checkpoint")), "pipeline.checkpoint is empty")
    ensure(pipeline.get("model_family") == "sdxl", "pipeline.model_family is not sdxl")
    ensure(pipeline.get("safe_to_render") is True, "pipeline.safe_to_render is not true")
    ensure(pipeline.get("lora") is None, "pipeline.lora must be null")
    ensure(pipeline.get("loras") == [], "pipeline.loras must be empty")
    ensure(pipeline.get("selected_scenes") == [1], "pipeline.selected_scenes must equal [1]")


def validate_compiled_preview(compiled_preview: dict[str, Any]) -> None:
    ensure(isinstance(compiled_preview, dict), "compiled_workflow_preview is missing")
    ensure(compiled_preview.get("status") == "ok", "compiled_workflow_preview.status is not ok")
    ensure(compiled_preview.get("ready_for_comfyui_prompt") is True, "ready_for_comfyui_prompt is not true")
    ensure(compiled_preview.get("template_mapping_status") == "compiled", "template_mapping_status is not compiled")
    validation = compiled_preview.get("validation", {})
    ensure(validation.get("valid") is True, "compiled_workflow_preview.validation.valid is not true")
    compiled_workflow = compiled_preview.get("compiled_workflow")
    ensure(isinstance(compiled_workflow, dict) and compiled_workflow, "compiled_workflow is missing")
    dumped = json.dumps(compiled_workflow, ensure_ascii=True)
    ensure("/mnt/i/COMFYUI_OK/models" not in dumped, "absolute model path leaked into compiled workflow")
    ensure("docs/validation/comfyui_models_inventory.json" not in dumped, "inventory path leaked into compiled workflow")
    ensure(".env" not in dumped, ".env leaked into compiled workflow")


def run_ops_baseline(base_url: str) -> None:
    payload = {
        "task_type": "storyboard",
        "generation_mode": "SELECTED_SCENES",
        "selected_scenes": [1],
        "visual_style": "cinematic_realistic",
        "quality": "balanced",
        "speed": "medium",
        "dry_run": True,
        "prompt": "wide cinematic shot of a lonely detective entering a neon-lit alley at night",
    }
    status, body = make_request(
        base_url,
        "/api/ops/comfyui/storyboard/render-dry-run",
        method="POST",
        payload=payload,
    )
    ensure(status == 200, f"ops dry-run failed with HTTP {status}: {dump_body(body)}")
    ensure(body.get("status") == "planned", "ops dry-run status is not planned")
    validate_pipeline(body.get("pipeline", {}))
    validate_compiled_preview(body.get("compiled_workflow_preview", {}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-skip-project", action="store_true")
    parser.add_argument("--skip-real-block-check", action="store_true")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    args = parser.parse_args()

    base_url = args.backend_url.rstrip("/")

    try:
        status, health = make_request(base_url, "/health")
        ensure(status == 200, f"GET /health returned HTTP {status}")
        ensure(isinstance(health, dict) and health.get("status") == "healthy", "health status is not healthy")

        run_ops_baseline(base_url)

        timestamp = int(time.time())
        email = f"storyboard_compile_smoke_{timestamp}@test.com"
        username = f"storyboard_compile_smoke_{timestamp}"

        register_payload = {
            "username": username,
            "email": email,
            "password": SMOKE_PASSWORD,
        }
        status, register_body = make_request(
            base_url,
            "/api/auth/register",
            method="POST",
            payload=register_payload,
        )
        ensure(status == 200, f"register failed with HTTP {status}: {dump_body(register_body)}")

        status, login_body = make_request(
            base_url,
            "/api/auth/login",
            method="POST",
            payload={"email": email, "password": SMOKE_PASSWORD},
        )
        ensure(status == 200, f"login failed with HTTP {status}: {dump_body(login_body)}")
        ensure(isinstance(login_body, dict) and login_body.get("access_token"), "login did not return access_token")
        token = login_body["access_token"]

        project_payloads = [
            {
                "title": "Smoke Storyboard Compile",
                "name": "Smoke Storyboard Compile",
                "description": "Smoke project for storyboard dry-run compile validation",
            },
            {
                "name": "Smoke Storyboard Compile",
                "description": "Smoke project for storyboard dry-run compile validation",
            },
        ]

        project_status = None
        project_body: Any = None
        for candidate in project_payloads:
            project_status, project_body = make_request(
                base_url,
                "/api/projects",
                method="POST",
                payload=candidate,
                token=token,
            )
            if project_status == 200:
                break

        if project_status != 200 or not isinstance(project_body, dict) or not project_body.get("id"):
            message = f"SKIPPED project creation: HTTP {project_status} body={dump_body(project_body)}"
            print(message)
            return 0 if args.allow_skip_project else 1

        project_id = project_body["id"]

        plan_payload = {
            "task_type": "storyboard",
            "generation_mode": "SELECTED_SCENES",
            "selected_scenes": [1],
            "visual_style": "cinematic_realistic",
            "quality": "balanced",
            "speed": "medium",
        }
        status, plan_body = make_request(
            base_url,
            f"/api/projects/{project_id}/storyboard/comfyui/plan",
            method="POST",
            payload=plan_payload,
            token=token,
        )
        ensure(status == 200, f"project storyboard plan failed with HTTP {status}: {dump_body(plan_body)}")
        ensure(plan_body.get("status") == "ok", "project storyboard plan status is not ok")
        validate_pipeline(plan_body.get("pipeline", {}))

        render_dry_payload = {
            **plan_payload,
            "dry_run": True,
            "prompt": "wide cinematic shot of a lonely detective entering a neon-lit alley at night",
        }
        status, render_body = make_request(
            base_url,
            f"/api/projects/{project_id}/storyboard/render",
            method="POST",
            payload=render_dry_payload,
            token=token,
        )
        ensure(status == 200, f"project storyboard render dry-run failed with HTTP {status}: {dump_body(render_body)}")
        ensure(render_body.get("status") == "planned", "project storyboard render dry-run status is not planned")
        ensure(render_body.get("dry_run") is True, "project storyboard render dry-run flag is not true")
        pipeline = render_body.get("pipeline", {})
        validate_pipeline(pipeline)
        ensure(pipeline.get("workflow_id") == "cinematic_storyboard_sdxl", "unexpected workflow_id in project render dry-run")
        ensure(
            pipeline.get("checkpoint") == "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            "unexpected checkpoint in project render dry-run",
        )
        ensure(isinstance(render_body.get("comfyui_payload_preview"), dict), "comfyui_payload_preview is missing")
        validate_compiled_preview(render_body.get("compiled_workflow_preview", {}))

        if not args.skip_real_block_check:
            real_payload = {
                **plan_payload,
                "dry_run": False,
                "render": True,
                "prompt": "wide cinematic shot of a lonely detective entering a neon-lit alley at night",
            }
            status, real_body = make_request(
                base_url,
                f"/api/projects/{project_id}/storyboard/render",
                method="POST",
                payload=real_payload,
                token=token,
            )
            ensure(status in {200, 400, 403, 409, 422}, f"unexpected HTTP {status} for real render blocked check")
            if status == 200:
                ensure(real_body.get("status") == "blocked", "real render did not return blocked status")
                validate_pipeline(real_body.get("pipeline", {}))
            else:
                ensure(real_body is not None, "real render blocked response body is empty")

        print("PASS project storyboard plan")
        print("PASS project storyboard render dry-run compile")
        if args.skip_real_block_check:
            print("SKIPPED real render blocked check: --skip-real-block-check requested")
        else:
            print("PASS real render blocked")
        print(
            json.dumps(
                {
                    "project_id": project_id,
                    "workflow_id": pipeline.get("workflow_id"),
                    "checkpoint": pipeline.get("checkpoint"),
                    "model_family": pipeline.get("model_family"),
                    "safe_to_render": pipeline.get("safe_to_render"),
                    "compiled_workflow_preview": {
                        "status": render_body.get("compiled_workflow_preview", {}).get("status"),
                        "validation": render_body.get("compiled_workflow_preview", {}).get("validation"),
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
