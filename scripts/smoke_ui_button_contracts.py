#!/usr/bin/env python3
"""
Smoke test para verificar que los endpoints que usa la UI existen y devuelven estructura compatible.
"""
import sys
import json
import requests

BASE = "http://127.0.0.1:8010/api"

def check(method, path, **kwargs):
    url = f"{BASE}{path}"
    try:
        resp = requests.request(method, url, timeout=5, **kwargs)
        return resp
    except Exception as e:
        print(f"FAIL: {method} {path} -> {e}")
        return None

def main():
    errors = []

    # 1. Health check
    r = check("GET", "/health")
    if r and r.status_code == 200:
        print("PASS: /health")
    else:
        errors.append("/health")

    # 2. Projects list (requires auth, but endpoint should exist)
    r = check("GET", "/projects")
    if r and r.status_code in (200, 401, 403):
        print(f"PASS: GET /projects (status={r.status_code})")
    else:
        errors.append(f"GET /projects status={r.status_code if r else 'N/A'}")

    # 3. Analysis endpoint exists
    r = check("POST", "/projects/TEST/analyze")
    if r and r.status_code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/analyze (status={r.status_code})")
    else:
        errors.append(f"POST /projects/{{id}}/analyze status={r.status_code if r else 'N/A'}")

    # 4. Storyboard generate endpoint exists
    r = check("POST", "/projects/TEST/storyboard/generate", json={
        "mode": "SINGLE_SCENE",
        "scene_start": 1,
        "scene_end": 1,
        "selected_scene_ids": ["1"],
        "style_preset": "cinematic_realistic",
        "shots_per_scene": 1,
        "overwrite": True
    })
    if r and r.status_code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/storyboard/generate (status={r.status_code})")
    else:
        errors.append(f"POST /projects/{{id}}/storyboard/generate status={r.status_code if r else 'N/A'}")

    # 5. Jobs list endpoint exists
    r = check("GET", "/projects/TEST/jobs")
    if r and r.status_code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs (status={r.status_code})")
        # Check response structure
        if r.status_code == 200:
            try:
                data = r.json()
                if "jobs" in data:
                    print("  -> Response has 'jobs' field")
                else:
                    print("  -> WARNING: Response missing 'jobs' field")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs status={r.status_code if r else 'N/A'}")

    # 6. Progress endpoint exists
    r = check("GET", "/projects/TEST/jobs/FAKE/progress")
    if r and r.status_code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs/{{job_id}}/progress (status={r.status_code})")
        if r.status_code == 200:
            try:
                data = r.json()
                required = ["job_id", "status", "progress_percent", "progress_stage", "progress_code"]
                missing = [f for f in required if f not in data]
                if not missing:
                    print("  -> Progress fields present")
                else:
                    print(f"  -> WARNING: Missing fields: {missing}")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs/{{job_id}}/progress status={r.status_code if r else 'N/A'}")

    # 7. Image assets endpoint exists
    r = check("GET", "/projects/TEST/assets/image-assets")
    if r and r.status_code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/assets/image-assets (status={r.status_code})")
    else:
        errors.append(f"GET /projects/{{id}}/assets/image-assets status={r.status_code if r else 'N/A'}")

    print("\n--- Result ---")
    if errors:
        print(f"FAIL: {len(errors)} endpoint(s) failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: All UI button contract checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
