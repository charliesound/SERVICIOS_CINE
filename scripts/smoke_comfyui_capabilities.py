#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8010"
BACKENDS = ["still", "video", "dubbing", "lab"]
EXPECTED_STILL_CAPABILITIES = {
    "image_generation",
    "image_to_image",
    "inpainting",
    "outpainting",
}


def fetch_json(path: str, timeout: float = 15.0) -> tuple[int, dict, float]:
    started = time.perf_counter()
    request = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
        elapsed = time.perf_counter() - started
        return response.status, payload, elapsed


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    try:
        status, payload, elapsed = fetch_json("/health")
    except urllib.error.URLError as exc:
        fail(f"/health unreachable: {exc}")

    print(f"health: HTTP {status} in {elapsed:.3f}s")
    if status != 200:
        fail("/health did not return HTTP 200")

    backend_payloads: dict[str, dict] = {}
    for backend in BACKENDS:
        status, payload, elapsed = fetch_json(f"/api/ops/capabilities/{backend}")
        backend_payloads[backend] = payload
        print(
            f"{backend}: HTTP {status} in {elapsed:.3f}s | "
            f"healthy={payload.get('healthy')} version={payload.get('comfyui_version')} "
            f"nodes={payload.get('nodes_count')} models={payload.get('models_count')}"
        )
        if status != 200:
            fail(f"/api/ops/capabilities/{backend} did not return HTTP 200")

    status, payload, elapsed = fetch_json("/api/ops/capabilities")
    print(f"all backends: HTTP {status} in {elapsed:.3f}s")
    if status != 200:
        fail("/api/ops/capabilities did not return HTTP 200")

    still = backend_payloads["still"]
    if still.get("healthy") is not True:
        fail("still backend is not healthy even though /system_stats should be enough")
    if not still.get("comfyui_version"):
        fail("still backend returned null comfyui_version")

    detected_capabilities = set(still.get("detected_capabilities") or [])
    if "image_generation" not in detected_capabilities:
        fail("still backend is missing image_generation capability")
    if not EXPECTED_STILL_CAPABILITIES.issubset(detected_capabilities):
        fail(
            "still backend is missing configured capability fallback: "
            f"{sorted(EXPECTED_STILL_CAPABILITIES - detected_capabilities)}"
        )

    warnings = still.get("warnings") or []
    if still.get("healthy") and "Timeout connecting to backend" in warnings:
        fail("still backend still reports generic backend timeout after successful system_stats")
    if still.get("models_count", 0) == 0 and not warnings:
        fail("still backend returned zero models without a specific discovery warning")
    if still.get("nodes_count", 0) == 0 and "object_info discovery timeout" not in warnings:
        print("WARN: still backend has zero nodes without object_info timeout warning")

    all_backends = payload.get("backends") or {}
    if sorted(all_backends.keys()) != sorted(BACKENDS):
        fail(f"unexpected backend keys: {sorted(all_backends.keys())}")

    print("PASS: ComfyUI capability smoke checks passed")


if __name__ == "__main__":
    main()
