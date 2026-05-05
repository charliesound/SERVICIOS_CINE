#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path

import yaml


BASE_URL = os.environ.get("AILINK_BASE_URL", "http://127.0.0.1:8010")
ROOT = Path(__file__).resolve().parents[1]
INSTANCES_PATH = ROOT / "src" / "config" / "instances.yml"
LAST_RUN_PATH = Path("/tmp/smoke_storyboard_still_generation_last.json")
SCRIPT_TEXT = (
    "Guión de largometraje\n\n"
    "1 INT. COCINA BAR. NOCHE.\n"
    "MARTA observa la puerta entreabierta.\n"
    "La cafetera vibra y una luz roja parpadea.\n\n"
    "2 INT. BAR. NOCHE.\n"
    "RAUL entra mojado por la lluvia.\n"
    "MARTA esconde una llave bajo el mostrador.\n"
)


def request_json(
    method: str,
    path: str,
    *,
    payload: dict | None = None,
    token: str | None = None,
    timeout: float = 60.0,
) -> tuple[int, dict]:
    headers: dict[str, str] = {}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else {}


def fail(message: str, *, details: dict | None = None) -> None:
    print(f"FAIL: {message}")
    if details:
        print(json.dumps(details, ensure_ascii=False, indent=2))
    sys.exit(1)


def ok(message: str) -> None:
    print(f"OK: {message}")


def load_routing_rules() -> dict:
    with INSTANCES_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def validate_capabilities() -> dict:
    status, payload = request_json(
        "GET",
        "/api/ops/capabilities/still?force_refresh=true",
        timeout=90.0,
    )
    if status != 200:
        fail("capabilities/still did not return HTTP 200", details=payload)
    if payload.get("healthy") is not True:
        fail("still capabilities are not healthy", details=payload)
    if not payload.get("comfyui_version"):
        fail("still capabilities returned null comfyui_version", details=payload)
    detected = set(payload.get("detected_capabilities") or [])
    if "image_generation" not in detected:
        fail("still capabilities are missing image_generation", details=payload)
    if "Timeout connecting to backend" in (payload.get("warnings") or []):
        fail("still capabilities still return generic backend timeout", details=payload)
    ok("still capabilities are healthy and usable")
    return payload


def validate_routing() -> None:
    config = load_routing_rules()
    mapping = ((config.get("routing_rules") or {}).get("task_type_mapping") or {})
    fallback_backend = (config.get("routing_rules") or {}).get("fallback_backend")
    if mapping.get("storyboard_realistic") != "still":
        fail(
            "storyboard_realistic does not route to still",
            details={"storyboard_realistic": mapping.get("storyboard_realistic")},
        )
    if mapping.get("storyboard_sketch") != "lab":
        fail(
            "storyboard_sketch does not route to lab",
            details={"storyboard_sketch": mapping.get("storyboard_sketch")},
        )
    ok(
        f"routing validated: storyboard_realistic->still, storyboard_sketch->lab, fallback={fallback_backend}"
    )


def bootstrap_user_and_project() -> tuple[str, str, str, dict]:
    email = f"storyboard.still.smoke.{uuid.uuid4().hex[:8]}@example.com"
    password = "StoryboardStill123!"
    username = f"storyboard_smoke_{uuid.uuid4().hex[:6]}"
    status, registered = request_json(
        "POST",
        "/api/auth/register",
        payload={"username": username, "email": email, "password": password},
    )
    if status != 200:
        fail("register failed", details=registered)

    status, login = request_json(
        "POST",
        "/api/auth/login",
        payload={"email": email, "password": password},
    )
    if status != 200:
        fail("login failed", details=login)
    token = login["access_token"]

    status, project = request_json(
        "POST",
        "/api/projects",
        payload={
            "name": "Storyboard Still Smoke",
            "description": "Release validation for storyboard routing to still",
        },
        token=token,
    )
    if status != 200:
        fail("project creation failed", details=project)
    project_id = project["id"]

    status, updated = request_json(
        "PUT",
        f"/api/projects/{project_id}/script",
        payload={"script_text": SCRIPT_TEXT},
        token=token,
    )
    if status != 200:
        fail("project script update failed", details=updated)

    ok(f"created test project {project_id}")
    return token, project_id, registered["user_id"], registered


def run_storyboard_generation(token: str, project_id: str) -> dict:
    status, analysis = request_json(
        "POST",
        f"/api/projects/{project_id}/analyze",
        token=token,
    )
    if status != 200:
        fail("project analysis failed", details=analysis)

    status, storyboard_job = request_json(
        "POST",
        f"/api/projects/{project_id}/storyboard/generate",
        payload={
            "mode": "SINGLE_SCENE",
            "scene_start": 1,
            "scene_end": 1,
            "selected_scene_ids": ["1"],
            "style_preset": "cinematic_realistic",
            "shots_per_scene": 1,
            "overwrite": True,
        },
        token=token,
    )
    if status != 200:
        fail("storyboard generation endpoint failed", details=storyboard_job)
    ok(f"storyboard job created: {storyboard_job['job_id']}")
    return storyboard_job


def fetch_storyboard_context(token: str, project_id: str) -> tuple[str, dict, dict, dict]:
    _, shots = request_json(
        "GET",
        f"/api/projects/{project_id}/storyboard?scene_number=1",
        token=token,
    )
    prompt = ((shots.get("shots") or [{}])[0]).get("narrative_text")
    if not prompt:
        fail("storyboard endpoint returned no shot prompt", details=shots)

    _, project_jobs = request_json(
        "GET",
        f"/api/projects/{project_id}/jobs",
        token=token,
    )
    _, project_assets = request_json(
        "GET",
        f"/api/projects/{project_id}/assets",
        token=token,
    )
    _, image_assets = request_json(
        "GET",
        f"/api/projects/{project_id}/assets/image-assets",
        token=token,
    )
    return prompt, project_jobs, project_assets, image_assets


def wait_for_render_job_record(token: str, project_id: str) -> dict:
    for _ in range(6):
        _, project_jobs = request_json(
            "GET",
            f"/api/projects/{project_id}/jobs",
            token=token,
        )
        render_jobs = [
            job
            for job in project_jobs.get("jobs", [])
            if str(job.get("job_type")) == "render:still"
        ]
        if render_jobs:
            return render_jobs[0]
        time.sleep(2)
    fail(
        "storyboard generation did not create a still render job",
        details=project_jobs,
    )


def poll_render_job(token: str, job_id: str) -> tuple[dict, dict | None]:
    detail: dict = {}
    queue_detail: dict | None = None
    for _ in range(12):
        time.sleep(5)
        _, detail = request_json("GET", f"/api/render/jobs/{job_id}", token=token)
        try:
            _, queue_detail = request_json(
                "GET",
                f"/api/queue/status/{job_id}",
                token=token,
            )
        except urllib.error.HTTPError:
            queue_detail = None

        terminal_history = [
            entry
            for entry in detail.get("history", [])
            if entry.get("event_type") in {"job_succeeded", "job_failed", "job_cancelled"}
        ]
        queue_status = (queue_detail or {}).get("status")
        if queue_status in {"succeeded", "failed", "timeout", "canceled", "rejected"}:
            return detail, queue_detail
        if terminal_history:
            return detail, queue_detail
    return detail, queue_detail


def validate_render_result(
    detail: dict,
    queue_detail: dict | None,
    *,
    project_assets: dict,
    image_assets: dict,
) -> None:
    history = detail.get("history", [])
    assets = detail.get("assets", [])
    terminal_event = next(
        (
            entry
            for entry in reversed(history)
            if entry.get("event_type") in {"job_succeeded", "job_failed", "job_cancelled"}
        ),
        None,
    )
    image_asset_count = len(image_assets.get("items", []))
    if terminal_event and terminal_event.get("event_type") == "job_succeeded":
        image_assets_from_job = [asset for asset in assets if asset.get("asset_type") == "image"]
        if not image_assets_from_job:
            fail(
                "render job succeeded but no image media asset was persisted",
                details={
                    "render_job": detail,
                    "queue_status": queue_detail,
                    "project_assets": project_assets,
                    "image_assets": image_assets,
                },
            )
        ok("render job completed with at least one image asset")
        return

    fail(
        "storyboard still render did not complete successfully",
        details={
            "render_job": detail,
            "queue_status": queue_detail,
            "project_assets": project_assets,
            "image_asset_count": image_asset_count,
            "root_cause_hint": (
                "UI storyboard endpoint only creates storyboard shots + JSON asset, and the render queue path "
                "still fails before producing image assets."
            ),
        },
    )


def main() -> None:
    capabilities = validate_capabilities()
    validate_routing()
    token, project_id, _user_id, _registered = bootstrap_user_and_project()
    storyboard_job = run_storyboard_generation(token, project_id)
    prompt, project_jobs, project_assets, image_assets = fetch_storyboard_context(token, project_id)
    print(
        json.dumps(
            {
                "project_id": project_id,
                "storyboard_job": storyboard_job,
                "project_jobs": project_jobs,
                "project_assets": project_assets,
                "image_assets": image_assets,
                "storyboard_prompt": prompt,
                "capabilities": {
                    "healthy": capabilities.get("healthy"),
                    "comfyui_version": capabilities.get("comfyui_version"),
                    "warnings": capabilities.get("warnings"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    render_job = wait_for_render_job_record(token, project_id)
    render_result_data = render_job.get("result_data") or {}
    workflow_key = render_result_data.get("workflow_key")
    prompt_payload = render_result_data.get("prompt") or {}
    if workflow_key != "still_storyboard_frame":
        fail(
            "render job lost workflow_key integrity",
            details=render_job,
        )
    if not prompt_payload:
        fail(
            "render job lost prompt payload integrity",
            details=render_job,
        )
    ok(f"render job created: {render_job['id']}")

    detail, queue_detail = poll_render_job(token, render_job["id"])
    validate_render_result(
        detail,
        queue_detail,
        project_assets=request_json("GET", f"/api/projects/{project_id}/assets", token=token)[1],
        image_assets=request_json("GET", f"/api/projects/{project_id}/assets/image-assets", token=token)[1],
    )
    LAST_RUN_PATH.write_text(
        json.dumps(
            {
                "token": token,
                "project_id": project_id,
                "render_job_id": render_job["id"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
