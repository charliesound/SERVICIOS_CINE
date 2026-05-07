#!/usr/bin/env python3
"""Smoke test: persist Flux concept art / key visual dry-run jobs.
Registers user, logs in, creates project, calls both endpoints,
validates job_id + dry_run flags, then GET /concept-art/jobs to verify persistence.
Does NOT call /prompt or execute render."""

import json
import sys
import uuid
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8010"
FAILED = False

UNIQUE = uuid.uuid4().hex[:8]
TEST_EMAIL = f"flux_jobs_{UNIQUE}@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_PROJECT_NAME = f"Flux Jobs Smoke {UNIQUE}"


def check(label: str, condition: bool, detail: str = "") -> None:
    global FAILED
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILED = True


def _req(method: str, path: str, data: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    body = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail_text = exc.read().decode()[:500] if exc.read() else ""
        return exc.code, {"_error_detail": detail_text}


def run_endpoint(label: str, endpoint_path: str, expected_task_type: str, token: str, project_id: str) -> str:
    global FAILED
    print(f"\n--- 5.{label} POST {endpoint_path} ---")
    payload = {
        "prompt": "cinematic key visual, detective in neon alley, anamorphic lighting",
        "negative_prompt": "low quality, blurry, watermark",
        "width": 1344,
        "height": 768,
        "steps": 28,
        "cfg": 3.5,
        "seed": 0,
    }
    status, resp = _req("POST", endpoint_path, payload, token=token)
    check(f"HTTP 200", status == 200, f"status={status}")

    check("status == ok", resp.get("status") == "ok", str(resp.get("status")))
    check("project_id matches", resp.get("project_id") == project_id, str(resp.get("project_id")))
    check("workflow_id == cinematic_flux_cine_2", resp.get("workflow_id") == "cinematic_flux_cine_2",
          str(resp.get("workflow_id")))

    # Job contract — new fields
    job_id = resp.get("job_id", "")
    check("has job_id", bool(job_id), str(job_id))
    check("dry_run == true", resp.get("dry_run") is True, str(resp.get("dry_run")))
    check("render_executed == false", resp.get("render_executed") is False, str(resp.get("render_executed")))
    check("prompt_called == false", resp.get("prompt_called") is False, str(resp.get("prompt_called")))

    pipeline = resp.get("pipeline", {})
    check("pipeline present", bool(pipeline))
    check(f"task_type == {expected_task_type}", pipeline.get("task_type") == expected_task_type,
          str(pipeline.get("task_type")))
    check("model_family == flux", pipeline.get("model_family") == "flux", str(pipeline.get("model_family")))

    for model_key in ("unet", "clip_l", "t5xxl", "vae"):
        check(f"pipeline.{model_key} resolved", bool(pipeline.get(model_key)), str(pipeline.get(model_key)))
    check("missing_models empty", pipeline.get("missing_models") == [], str(pipeline.get("missing_models")))

    safe = pipeline.get("safe_to_render")
    check("safe_to_render is bool", isinstance(safe, bool), str(safe))

    preview = resp.get("compiled_workflow_preview", {})
    check("preview present", bool(preview))
    check("preview.status == ok", preview.get("status") == "ok", str(preview.get("status")))

    validation = preview.get("validation", {})
    check("validation.valid == true", validation.get("valid") is True, str(validation.get("valid")))
    missing_phs = validation.get("missing_placeholders", [])
    check("missing_placeholders empty", missing_phs == [], str(missing_phs))
    check("node_count > 0", (validation.get("node_count") or 0) > 0, str(validation.get("node_count")))

    compiled = preview.get("compiled_workflow", {})
    compiled_text = json.dumps(compiled)
    check("no absolute paths", ":/" not in compiled_text and "C:\\" not in compiled_text, "abs path")
    check("no api_key", "api_key" not in compiled_text.lower(), "api_key found")
    check("no password", "password" not in compiled_text.lower(), "password found")
    check("no secret", "secret" not in compiled_text.lower(), "secret found")

    remaining = __import__("re").findall(r'\{\{[A-Z0-9_]+\}\}', compiled_text)
    check("no remaining placeholders", len(remaining) == 0, str(remaining))

    return job_id


def main() -> int:
    global FAILED

    # 1. Health
    print("\n--- 1. Health check ---")
    status, data = _req("GET", "/health")
    check("health endpoint", status == 200, f"status={status}")

    # 2. Register user
    print("\n--- 2. Register user ---")
    status, data = _req("POST", "/api/auth/register", {
        "username": f"flux_jobs_{UNIQUE}",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    check("register HTTP 200", status == 200, f"status={status}")
    check("register has user_id", bool(data.get("user_id")), str(data.get("user_id")))
    user_id = data.get("user_id", "")

    # 3. Login
    print("\n--- 3. Login ---")
    status, data = _req("POST", "/api/auth/login", {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    check("login HTTP 200", status == 200, f"status={status}")
    check("has access_token", bool(data.get("access_token")), "no token")
    token = data.get("access_token", "")
    if not token:
        print("  ABORT: no auth token")
        return 1

    # 4. Create project
    print("\n--- 4. Create project ---")
    status, data = _req("POST", "/api/projects", {"name": TEST_PROJECT_NAME}, token=token)
    check("create project HTTP 200", status == 200, f"status={status}")
    check("has project id", bool(data.get("id")), str(data.get("id")))
    project_id = data.get("id", "")
    if not project_id:
        print("  ABORT: no project id")
        return 1

    # 5a. concept-art dry-run
    job_id_ca = run_endpoint("a", f"/api/projects/{project_id}/concept-art/compile-workflow-dry-run", "concept_art", token, project_id)

    # 5b. key-visual dry-run
    job_id_kv = run_endpoint("b", f"/api/projects/{project_id}/key-visual/compile-workflow-dry-run", "key_visual", token, project_id)

    # 6. GET /concept-art/jobs
    print("\n--- 6. GET /concept-art/jobs ---")
    status, data = _req("GET", f"/api/projects/{project_id}/concept-art/jobs", token=token)
    check("HTTP 200", status == 200, f"status={status}")
    check("status == ok", data.get("status") == "ok", str(data.get("status")))
    check("project_id matches", data.get("project_id") == project_id, str(data.get("project_id")))

    jobs = data.get("jobs", [])
    check("at least 2 jobs", len(jobs) >= 2, f"got {len(jobs)}")

    job_ids_found = set()
    for j in jobs:
        check("job has job_id", bool(j.get("job_id")), str(j.get("job_id")))
        check("job has task_type", j.get("task_type") in ("concept_art", "key_visual"), str(j.get("task_type")))
        check("job status == dry_run_completed", j.get("status") == "dry_run_completed", str(j.get("status")))
        check("job workflow_id == cinematic_flux_cine_2", j.get("workflow_id") == "cinematic_flux_cine_2",
              str(j.get("workflow_id")))
        check("job model_family == flux", j.get("model_family") == "flux", str(j.get("model_family")))
        check("job safe_to_render is bool", isinstance(j.get("safe_to_render"), bool), str(j.get("safe_to_render")))
        check("job dry_run is True", j.get("dry_run") is True, str(j.get("dry_run")))
        check("job render_executed is False", j.get("render_executed") is False, str(j.get("render_executed")))
        check("job prompt_called is False", j.get("prompt_called") is False, str(j.get("prompt_called")))
        check("job has created_at", bool(j.get("created_at")), str(j.get("created_at")))
        job_ids_found.add(j.get("job_id"))

    check("concept-art job_id in list", job_id_ca in job_ids_found, f"{job_id_ca} not in {job_ids_found}")
    check("key-visual job_id in list", job_id_kv in job_ids_found, f"{job_id_kv} not in {job_ids_found}")

    # Summary
    print()
    if FAILED:
        print("SMOKE JOBS AUTH FAILED")
        return 1
    else:
        print("SMOKE JOBS AUTH PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
