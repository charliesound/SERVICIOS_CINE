#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8010")
TOKEN = os.environ.get("TOKEN", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "")


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def request_json(path: str, method: str = "GET", payload: dict | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=_headers(),
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {exc.read().decode('utf-8')}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{method} {path} -> {exc.reason}") from exc
    if status != 200:
        raise RuntimeError(f"{method} {path} -> HTTP {status}")
    return json.loads(body)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"ASSERT FAILED: {message}")


def main() -> int:
    if not PROJECT_ID:
        print("FATAL: PROJECT_ID env var is required")
        return 1

    print(f"=== Storyboard Sequence Regenerate Smoke Test ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Project:  {PROJECT_ID}")
    print(f"Auth:     {'Bearer token' if TOKEN else 'NONE'}")
    print()

    # 1. Health check
    print("[1/5] Health check...")
    health = request_json("/health")
    ensure(health.get("status") == "ok" or health.get("status") == "healthy", f"Health check failed: {health}")
    print("  OK")

    # 2. Get storyboard options to obtain a sequence_id
    print("[2/5] Fetching storyboard options (sequences)...")
    options = request_json(f"/api/projects/{PROJECT_ID}/storyboard/options")
    sequences = options.get("sequences", [])
    ensure(len(sequences) > 0, "No sequences found in storyboard options; at least one sequence required")
    seq = sequences[0]
    sequence_id: str = seq["sequence_id"]
    print(f"  Selected sequence: {sequence_id} ({seq.get('title', '?')})")
    print(f"  Storyboard status: {seq.get('storyboard_status', '?')}")

    # 3. Call regenerate endpoint
    print("[3/5] Calling regenerate endpoint...")
    regenerate_payload = {
        "style_preset": "cinematic_realistic",
        "shots_per_scene": 3,
        "overwrite": True,
    }
    regenerate_result = request_json(
        f"/api/projects/{PROJECT_ID}/storyboard/sequences/{sequence_id}/regenerate",
        method="POST",
        payload=regenerate_payload,
    )
    print(f"  job_id:           {regenerate_result.get('job_id', 'MISSING')}")
    print(f"  mode:             {regenerate_result.get('mode', 'MISSING')}")
    print(f"  version:          {regenerate_result.get('version', 'MISSING')}")
    print(f"  shots_per_scene:  {regenerate_result.get('shots_per_scene', 'MISSING')}")
    print(f"  generated_assets: {regenerate_result.get('generated_assets', [])}")
    print(f"  total_shots:      {regenerate_result.get('total_shots', 'MISSING')}")
    print(f"  total_scenes:     {regenerate_result.get('total_scenes', 'MISSING')}")
    print(f"  render_jobs:      {len(regenerate_result.get('render_jobs', []))}")
    ensure("job_id" in regenerate_result and regenerate_result["job_id"], "Response missing job_id")
    ensure(regenerate_result.get("version", 0) >= 1, "version should be >= 1")
    ensure(regenerate_result.get("total_shots", 0) > 0, "total_shots should be > 0")
    ensure(regenerate_result.get("total_scenes", 0) > 0, "total_scenes should be > 0")
    print("  OK")

    # 4. Verify job detail via GET /projects/jobs/{job_id}
    print("[4/5] Verifying job detail...")
    job_id = regenerate_result["job_id"]
    job_detail = request_json(f"/api/projects/jobs/{job_id}")
    ensure(job_detail.get("id") == job_id, "Job detail id mismatch")
    ensure(job_detail.get("status") in ("completed", "processing"), f"Unexpected job status: {job_detail.get('status')}")
    print(f"  Job status: {job_detail.get('status')}")
    print("  OK")

    # 5. Verify shots appear in the sequence storyboard
    print("[5/5] Verifying sequence storyboard shots...")
    seq_storyboard = request_json(f"/api/projects/{PROJECT_ID}/storyboard/sequences/{sequence_id}")
    shots = seq_storyboard.get("shots", [])
    print(f"  Shots returned: {len(shots)}")
    ensure(len(shots) > 0, "No shots found in sequence storyboard after regeneration")
    for i, shot in enumerate(shots[:3]):
        print(f"    Shot {i+1}: id={shot.get('id', '?')} type={shot.get('shot_type', '?')} version={shot.get('version', '?')}")
        if shot.get("render_job_id"):
            print(f"      render_job_id={shot['render_job_id']} render_status={shot.get('render_status', '?')}")
        if shot.get("asset_id"):
            print(f"      asset_id={shot['asset_id']}")
    print("  OK")

    print()
    print("=== ALL CHECKS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
