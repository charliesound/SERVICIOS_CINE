from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

DEFAULT_CLIENT_ID = "ailinkcinema-storyboard"


def get_comfyui_base_url() -> str:
    storyboard_override = os.environ.get("COMFYUI_STORYBOARD_BASE_URL", "").strip()
    if storyboard_override:
        return storyboard_override.rstrip("/")

    from services.instance_registry import registry

    if not registry.get_all_backends():
        registry.load_config()

    backend = registry.resolve_backend_for_task("storyboard_realistic")
    if backend and backend.base_url:
        return backend.base_url.rstrip("/")

    fallback = registry.get_backend("still")
    if fallback and fallback.base_url:
        return fallback.base_url.rstrip("/")

    return (os.environ.get("COMFYUI_BASE_URL", "http://localhost:8188")).rstrip("/")


def is_real_render_enabled() -> bool:
    return os.environ.get("ENABLE_COMFYUI_REAL_RENDER", "").strip().lower() == "true"


def _request_json(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    allow_statuses: set[int] | None = None,
) -> dict[str, Any]:
    base_url = get_comfyui_base_url()
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urlrequest.Request(
        f"{base_url}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlrequest.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except urlerror.HTTPError as exc:
        if allow_statuses and exc.code in allow_statuses:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body) if body else {}
            except json.JSONDecodeError:
                parsed = {}
            if isinstance(parsed, dict):
                parsed["http_status"] = exc.code
                return parsed
            return {"http_status": exc.code}
        response_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI {method} {path} failed with HTTP {exc.code}: {response_body[:400]}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"ComfyUI at {base_url} is unavailable: {exc.reason}") from exc
    except Exception as exc:
        raise RuntimeError(f"ComfyUI request to {base_url}{path} failed: {exc}") from exc

    try:
        parsed = json.loads(body) if body else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ComfyUI {method} {path} returned invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError(f"ComfyUI {method} {path} returned an unexpected payload")
    return parsed


def check_comfyui_health() -> dict[str, Any]:
    data = _request_json("/system_stats")
    device = data.get("devices", [{}])[0] if isinstance(data.get("devices"), list) else {}
    system = data.get("system", {}) if isinstance(data.get("system"), dict) else {}
    return {
        "available": True,
        "base_url": get_comfyui_base_url(),
        "device": device.get("name") or system.get("os") or "unknown",
        "system": system,
        "raw": data,
    }


def submit_prompt_to_comfyui(workflow: dict, client_id: str | None = None) -> dict[str, Any]:
    if not isinstance(workflow, dict) or not workflow:
        raise RuntimeError("Compiled workflow is empty; nothing can be submitted to ComfyUI")

    payload = {
        "prompt": workflow,
        "client_id": client_id or DEFAULT_CLIENT_ID,
    }
    response = _request_json("/prompt", method="POST", payload=payload)
    if not response.get("prompt_id"):
        raise RuntimeError(f"ComfyUI /prompt did not return prompt_id: {response}")
    return response


def get_prompt_history(prompt_id: str) -> dict[str, Any]:
    if not prompt_id:
        raise RuntimeError("prompt_id is required to fetch ComfyUI history")
    history = _request_json(f"/history/{prompt_id}", allow_statuses={404})
    if history.get("http_status") == 404:
        return {
            "prompt_id": prompt_id,
            "status": "not_found",
            "history": {},
        }
    if prompt_id in history and isinstance(history[prompt_id], dict):
        return {
            "prompt_id": prompt_id,
            "status": "history_found",
            "history": history,
        }
    return {
        "prompt_id": prompt_id,
        "status": "running_or_pending",
        "history": history,
    }


def extract_comfyui_outputs(history: dict, prompt_id: str) -> dict[str, Any]:
    prompt_history = history.get(prompt_id, {}) if isinstance(history, dict) else {}
    outputs = prompt_history.get("outputs", {}) if isinstance(prompt_history, dict) else {}
    images: list[dict[str, Any]] = []
    videos: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []

    if isinstance(outputs, dict):
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            for image in node_output.get("images", []) or []:
                if isinstance(image, dict):
                    images.append(image)
            for file_item in node_output.get("files", []) or []:
                if isinstance(file_item, dict):
                    files.append(file_item)
            for gif in node_output.get("gifs", []) or []:
                if isinstance(gif, dict):
                    videos.append(gif)
            for animation in node_output.get("animations", []) or []:
                if isinstance(animation, dict):
                    videos.append(animation)

    return {
        "images": images,
        "videos": videos,
        "files": files,
        "raw_outputs": outputs,
    }


def get_prompt_status(prompt_id: str) -> dict[str, Any]:
    history_response = get_prompt_history(prompt_id)
    if history_response.get("status") == "not_found":
        return {
            "prompt_id": prompt_id,
            "status": "not_found",
            "history": {},
            "outputs": extract_comfyui_outputs({}, prompt_id),
        }

    history = history_response.get("history", {})
    if prompt_id in history and isinstance(history[prompt_id], dict):
        prompt_history = history[prompt_id]
        outputs = prompt_history.get("outputs", {})
        status = "completed" if outputs else "running_or_pending"
        return {
            "prompt_id": prompt_id,
            "status": status,
            "history": prompt_history,
            "outputs": extract_comfyui_outputs(history, prompt_id),
        }

    return {
        "prompt_id": prompt_id,
        "status": "running_or_pending",
        "history": history,
        "outputs": extract_comfyui_outputs(history, prompt_id),
    }


def poll_prompt_until_complete(
    prompt_id: str,
    timeout_seconds: int = 30,
    interval_seconds: float = 1.0,
) -> dict[str, Any]:
    started_at = time.monotonic()
    timeout_seconds = max(1, int(timeout_seconds))
    interval_seconds = max(0.1, float(interval_seconds))

    last_status = get_prompt_status(prompt_id)
    while True:
        if last_status.get("status") == "completed":
            return {
                "prompt_id": prompt_id,
                "status": "completed",
                "outputs": last_status.get("outputs", {}),
                "history": last_status.get("history", {}),
                "timed_out": False,
            }

        elapsed = time.monotonic() - started_at
        if elapsed >= timeout_seconds:
            return {
                "prompt_id": prompt_id,
                "status": "timeout",
                "outputs": last_status.get("outputs", {}),
                "history": last_status.get("history", {}),
                "timed_out": True,
                "elapsed_seconds": round(elapsed, 2),
            }

        time.sleep(interval_seconds)
        last_status = get_prompt_status(prompt_id)


def get_prompt_status_contract(prompt_id: str) -> dict[str, Any]:
    status = get_prompt_status(prompt_id)
    return {
        "prompt_id": prompt_id,
        "status": status.get("status"),
        "outputs": status.get("outputs", {}),
        "history": status.get("history", {}),
    }
