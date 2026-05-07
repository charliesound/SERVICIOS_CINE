#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8010"
OPS_PAYLOAD = {
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-project-auth", action="store_true")
    args = parser.parse_args()

    try:
        ops_result = request_json(
            "/api/ops/comfyui/storyboard/render-dry-run",
            method="POST",
            payload=OPS_PAYLOAD,
        )
        if ops_result.get("status") != "planned":
            raise RuntimeError("ops dry-run did not return status=planned")
    except Exception as exc:
        print(f"SMOKE FAIL: ops dry-run prerequisite failed: {exc}")
        return 1

    if args.skip_project_auth:
        print("SKIPPED: --skip-project-auth requested; project auth flow not executed.")
        return 0

    print("SKIPPED: project auth smoke is not configured for this environment yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
