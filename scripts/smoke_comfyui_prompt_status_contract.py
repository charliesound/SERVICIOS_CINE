#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "http://127.0.0.1:8010"


def request_json(path: str) -> tuple[int, Any]:
    request = urllib.request.Request(f"{BASE_URL}{path}", method="GET")
    try:
        with urllib.request.urlopen(request) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GET {path} -> {exc.reason}") from exc

    if "Traceback" in body or "<html" in body.lower():
        raise RuntimeError("response contains traceback/html instead of JSON")

    try:
        parsed = json.loads(body) if body else None
    except json.JSONDecodeError as exc:
        raise RuntimeError("response is not valid JSON") from exc
    return status, parsed


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    try:
        status, health = request_json("/health")
        ensure(status == 200, f"GET /health failed with HTTP {status}")
        ensure(isinstance(health, dict) and health.get("status") == "healthy", "health status is not healthy")

        status, body = request_json("/api/ops/comfyui/prompt/fake_prompt_id/status")
        ensure(status in {200, 404}, f"unexpected HTTP {status} for fake prompt status")
        ensure(isinstance(body, dict), "prompt status response is not JSON object")
        ensure(body.get("prompt_id") == "fake_prompt_id", "prompt_id is missing or incorrect")
        ensure(bool(body.get("status")), "status field is missing")
        if status == 404:
            ensure("detail" in body, "404 response missing detail field")

        print("SMOKE PASS")
        print(json.dumps(body, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
