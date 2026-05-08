#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOADS_DIR = ROOT / ".tmp" / "landing_comfyui_v5" / "image_payloads"
JOBS_PATH = ROOT / ".tmp" / "landing_comfyui_v5" / "image_render_jobs.json"
COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
COMFYUI_PROMPT_URL = f"{COMFYUI_BASE_URL}/prompt"


def load_payloads() -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(PAYLOADS_DIR.glob("*.json")):
        payloads.append(json.loads(path.read_text(encoding="utf-8")))
    return payloads


def check_reference_requirements(payload: dict[str, Any]) -> str | None:
    if payload.get("workflow_text_only_fallback"):
        return None
    ref_path = payload.get("reference_image_path", "")
    if not ref_path:
        return "workflow requires reference but reference_image_path is empty"
    if not Path(ref_path).exists():
        return f"workflow requires reference but file not found: {ref_path}"
    return None


def submit_prompt(workflow: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(
        {
            "prompt": workflow,
            "client_id": f"landing-v5-images-{uuid.uuid4().hex}",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        COMFYUI_PROMPT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_jobs(payload: Any) -> None:
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if os.environ.get("ENABLE_REAL_COMFYUI_RENDER") != "1":
        print("Render bloqueado: ENABLE_REAL_COMFYUI_RENDER no esta activado.")
        print("Para renderizar real: ENABLE_REAL_COMFYUI_RENDER=1 python3 scripts/render_landing_comfyui_images_v5_reference_guided.py")
        return 0

    print("=== Render Landing V5 Reference-Guided Images ===\n")

    payloads = load_payloads()
    if not payloads:
        raise RuntimeError("No image payloads found. Run scripts/build_landing_comfyui_payloads_v5_reference_guided.py first.")

    print(f"  Payloads loaded: {len(payloads)}")
    print(f"  ComfyUI URL: {COMFYUI_BASE_URL}\n")

    preflight_failures: list[str] = []
    for payload in payloads:
        error = check_reference_requirements(payload)
        if error:
            preflight_failures.append(f"{payload['image_key']}: {error}")

    if preflight_failures:
        print("PREFLIGHT FAILURES (workflow requires reference but missing):")
        for f in preflight_failures:
            print(f"  - {f}")
        return 1

    jobs: list[dict[str, Any]] = []
    for payload in payloads:
        mode = "reference-guided" if not payload.get("workflow_text_only_fallback") else "text-only"
        print(f"  SUBMITTING: {payload['image_key']} [{mode}]")

        try:
            response = submit_prompt(payload["compiled_workflow"])
            jobs.append({
                "image_key": payload["image_key"],
                "target_file_name": payload["target_file_name"],
                "status": "queued",
                "mode": mode,
                "reference_image_path": payload.get("reference_image_path", ""),
                "prompt_id": response.get("prompt_id"),
                "response": response,
            })
            print(f"    QUEUED -> prompt_id={response.get('prompt_id')}")
        except urllib.error.HTTPError as exc:
            error_detail = exc.read().decode("utf-8", errors="replace")
            jobs.append({
                "image_key": payload["image_key"],
                "target_file_name": payload["target_file_name"],
                "status": "http_error",
                "mode": mode,
                "http_status": exc.code,
                "detail": error_detail,
            })
            print(f"    HTTP ERROR: {exc.code}")
        except urllib.error.URLError as exc:
            jobs.append({
                "image_key": payload["image_key"],
                "target_file_name": payload["target_file_name"],
                "status": "connection_error",
                "mode": mode,
                "detail": str(exc.reason),
            })
            print(f"    CONNECTION ERROR: {exc.reason}")

    write_jobs({"jobs": jobs})
    failures = [job for job in jobs if job.get("status") != "queued"]
    ref_count = sum(1 for j in jobs if j.get("mode") == "reference-guided")
    text_count = sum(1 for j in jobs if j.get("mode") == "text-only")

    print(f"\nRender jobs saved: {JOBS_PATH.relative_to(ROOT)}")
    print(f"  queued: {len(jobs) - len(failures)}/{len(jobs)}")
    print(f"  reference-guided: {ref_count}")
    print(f"  text-only: {text_count}")
    if failures:
        print(f"  failures: {len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
