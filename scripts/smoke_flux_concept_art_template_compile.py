#!/usr/bin/env python3
"""Smoke test: Flux concept art template compilation dry-run via OPS endpoint.
Validates status, model resolution, compilation, and security.
Does NOT call /prompt or execute render."""

import json
import sys
import urllib.request
import urllib.error
import re

BASE_URL = "http://127.0.0.1:8010"
ENDPOINT = "/api/ops/comfyui/concept-art/compile-workflow-dry-run"

PAYLOAD = {
    "task_type": "concept_art",
    "prompt": "cinematic key visual, detective in neon alley, anamorphic lighting",
    "negative_prompt": "low quality, blurry, watermark",
    "width": 1344,
    "height": 768,
    "steps": 28,
    "cfg": 3.5,
    "seed": 0,
}

FAILED = False


def check(label: str, condition: bool, detail: str = "") -> None:
    global FAILED
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILED = True


def main() -> int:
    global FAILED

    # 1. /health
    print("\n--- 1. Health check ---")
    try:
        req = urllib.request.Request(f"{BASE_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            health_data = json.loads(resp.read().decode())
        check("health endpoint", resp.status == 200, f"status={resp.status}")
    except Exception as exc:
        check(f"health endpoint: {exc}", False)
        print("\nABORT: backend not reachable")
        return 1

    # 2. POST dry-run
    print("\n--- 2. POST concept-art/compile-workflow-dry-run ---")
    try:
        body = json.dumps(PAYLOAD).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}{ENDPOINT}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            response = json.loads(resp.read().decode())
        check("HTTP 200", resp.status == 200, f"status={resp.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()[:500] if exc.read() else ""
        check(f"HTTP {exc.code}: {detail}", False)
        FAILED = True
        # still try to parse if possible
        try:
            response = json.loads(exc.read().decode()) if exc.read() else {}
        except Exception:
            response = {}
    except Exception as exc:
        check(f"request failed: {exc}", False)
        return 1

    # 3. Top-level status
    print("\n--- 3. Top-level validation ---")
    check("status == ok", response.get("status") == "ok", str(response.get("status")))
    check("workflow_id present", bool(response.get("workflow_id")), str(response.get("workflow_id")))
    check(
        "workflow_id == cinematic_flux_cine_2",
        response.get("workflow_id") == "cinematic_flux_cine_2",
        str(response.get("workflow_id")),
    )

    # 4. Pipeline validation
    print("\n--- 4. Pipeline validation ---")
    pipeline = response.get("pipeline", {})
    check("pipeline present", bool(pipeline))
    check("task_type == concept_art", pipeline.get("task_type") == "concept_art", str(pipeline.get("task_type")))
    check("model_family == flux", pipeline.get("model_family") == "flux", str(pipeline.get("model_family")))
    check("workflow_id in pipeline", pipeline.get("workflow_id") == "cinematic_flux_cine_2", str(pipeline.get("workflow_id")))

    flux_models = {"unet": pipeline.get("unet"), "clip_l": pipeline.get("clip_l"),
                   "t5xxl": pipeline.get("t5xxl"), "vae": pipeline.get("vae")}
    for model_key, model_val in flux_models.items():
        check(f"pipeline.{model_key} resolved", bool(model_val), str(model_val))

    check("missing_models empty", pipeline.get("missing_models") == [], str(pipeline.get("missing_models")))

    params = pipeline.get("params", {})
    check("params.width == 1344", params.get("width") == 1344, str(params.get("width")))
    check("params.height == 768", params.get("height") == 768, str(params.get("height")))
    check("params.steps == 28", params.get("steps") == 28, str(params.get("steps")))
    check("params.cfg == 3.5", params.get("cfg") == 3.5, str(params.get("cfg")))

    safe_to_render = pipeline.get("safe_to_render")
    check("safe_to_render is bool", isinstance(safe_to_render, bool), str(safe_to_render))

    # 5. Compiled workflow preview validation
    print("\n--- 5. Compiled workflow preview validation ---")
    preview = response.get("compiled_workflow_preview", {})
    check("preview present", bool(preview))
    check("preview.status == ok", preview.get("status") == "ok", str(preview.get("status")))
    check("ready_for_comfyui_prompt == true", preview.get("ready_for_comfyui_prompt") is True,
          str(preview.get("ready_for_comfyui_prompt")))
    validation = preview.get("validation", {})
    check("validation.valid == true", validation.get("valid") is True, str(validation.get("valid")))
    check("no missing_placeholders", validation.get("missing_placeholders") == [],
          str(validation.get("missing_placeholders")))
    check("node_count > 0", (validation.get("node_count") or 0) > 0, str(validation.get("node_count")))

    # 6. Security: no absolute paths, no secrets in compiled workflow
    print("\n--- 6. Security scan (compiled) ---")
    compiled = preview.get("compiled_workflow", {})
    compiled_text = json.dumps(compiled)

    check("no absolute windows paths", not re.search(r'[A-Za-z]:\\\\', compiled_text), "windows path found")
    check("no /mnt/ paths", "/mnt/" not in compiled_text, "/mnt/ found")
    check("no api_key", "api_key" not in compiled_text.lower(), "api_key found")
    check("no token", bool(re.search(r'\btoken\b', compiled_text)) is False, "token found")
    check("no password", "password" not in compiled_text.lower(), "password found")
    check("no secret", "secret" not in compiled_text.lower(), "secret found")
    check("no sk- keys", "sk-" not in compiled_text, "sk- found")

    # 7. Verify all placeholders resolved — no {{...}} remaining
    print("\n--- 7. No unresolved placeholders ---")
    remaining = re.findall(r'\{\{[A-Z0-9_]+\}\}', compiled_text)
    check("no remaining placeholders", len(remaining) == 0, str(remaining))

    # Summary
    print()
    if FAILED:
        print("SMOKE TEST FAILED")
        return 1
    else:
        print("SMOKE TEST PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
