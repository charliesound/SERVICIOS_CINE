#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8010"


def fetch_json(path: str) -> dict:
    url = f"{BASE_URL}{path}"
    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{url} -> HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{url} -> {exc.reason}") from exc

    if status != 200:
        raise RuntimeError(f"{url} -> HTTP {status}")

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{url} -> invalid JSON") from exc


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    try:
        health = fetch_json("/health")
        models = fetch_json("/api/ops/comfyui/models")
        classify = fetch_json("/api/ops/comfyui/classify")
        workflows = fetch_json("/api/ops/comfyui/workflows?task_type=storyboard")
        search = fetch_json(
            "/api/ops/comfyui/search?"
            + urllib.parse.urlencode({"q": "juggernaut"})
        )
        recommend = fetch_json(
            "/api/ops/comfyui/recommend?"
            + urllib.parse.urlencode(
                {
                    "task_type": "storyboard",
                    "style": "cinematic_realistic",
                    "quality": "balanced",
                }
            )
        )

        recommendation = recommend.get("recommendation", {})

        assert_true(health.get("status") == "healthy", "health status is not healthy")
        assert_true(models.get("status") == "ok", "models endpoint did not return status=ok")
        assert_true(classify.get("status") == "ok", "classify endpoint did not return status=ok")
        assert_true(workflows.get("total", 0) > 0, "no storyboard workflows returned")
        assert_true(search.get("total", 0) > 0, "juggernaut search returned no results")
        assert_true(bool(recommendation.get("workflow_id")), "recommendation.workflow_id is empty")
        assert_true(bool(recommendation.get("checkpoint")), "recommendation.checkpoint is empty")
        assert_true(recommendation.get("model_family") == "sdxl", "storyboard model_family is not sdxl")
        assert_true(recommendation.get("storyboard_lora") is None, "storyboard_lora must be null")
        assert_true(recommendation.get("loras") == [], "loras must be empty")

        print("SMOKE PASS")
        print(json.dumps(recommend, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"SMOKE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
