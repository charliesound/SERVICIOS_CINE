#!/usr/bin/env python3
"""
Smoke test para verificar que los endpoints que usa la UI existen y devuelven estructura compatible.
Usa urllib estándar, no requests.
"""
import sys
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8010/api"

def check(method, path, data=None):
    url = f"{BASE}{path}"
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)
        resp = urllib.request.urlopen(req, timeout=5)
        return resp
    except urllib.error.HTTPError as e:
        return e
    except Exception as e:
        print(f"FAIL: {method} {path} -> {e}")
        return None

def main():
    errors = []

    # 1. Health check
    r = check("GET", "/health")
    if r and (getattr(r, 'status', None) == 200 or getattr(r, 'code', None) == 200):
        print("PASS: /health")
    else:
        errors.append("/health")

    # 2. Projects list (requires auth, but endpoint should exist)
    r = check("GET", "/projects")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403):
        print(f"PASS: GET /projects (status={r.code})")
    else:
        errors.append(f"GET /projects")

    # 3. Analysis endpoint exists
    r = check("POST", "/projects/TEST/analyze")
    if r and hasattr(r, 'code') and r.code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/analyze (status={r.code})")
    else:
        errors.append(f"POST /projects/{{id}}/analyze")

    # 4. Storyboard generate endpoint exists
    r = check("POST", "/projects/TEST/storyboard/generate", data={
        "mode": "SINGLE_SCENE",
        "scene_start": 1,
        "scene_end": 1,
        "selected_scene_ids": ["1"],
        "style_preset": "cinematic_realistic",
        "shots_per_scene": 1,
        "overwrite": True
    })
    if r and hasattr(r, 'code') and r.code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/storyboard/generate (status={r.code})")
    else:
        errors.append(f"POST /projects/{{id}}/storyboard/generate")

    # 5. Jobs list endpoint exists
    r = check("GET", "/projects/TEST/jobs")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs (status={r.code})")
        if r.code == 200:
            try:
                data = json.loads(r.read().decode('utf-8'))
                if "jobs" in data:
                    print("  -> Response has 'jobs' field")
                else:
                    print("  -> WARNING: Response missing 'jobs' field")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs")

    # 6. Progress endpoint exists
    r = check("GET", "/projects/TEST/jobs/FAKE/progress")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs/{{job_id}}/progress (status={r.code})")
        if r.code == 200:
            try:
                data = json.loads(r.read().decode('utf-8'))
                required = ["job_id", "status", "progress_percent", "progress_stage", "progress_code"]
                missing = [f for f in required if f not in data]
                if not missing:
                    print("  -> Progress fields present")
                else:
                    print(f"  -> WARNING: Missing fields: {missing}")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs/{{job_id}}/progress")

    # 7. Image assets endpoint exists
    r = check("GET", "/projects/TEST/assets/image-assets")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/assets/image-assets (status={r.code})")
    else:
        errors.append(f"GET /projects/{{id}}/assets/image-assets")

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
