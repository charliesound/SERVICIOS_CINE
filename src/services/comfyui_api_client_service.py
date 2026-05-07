from __future__ import annotations

import json
import os
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


DEFAULT_COMFYUI_BASE_URL = "http://127.0.0.1:8188"
DEFAULT_CLIENT_ID = "ailinkcinema-storyboard"


def get_comfyui_base_url() -> str:
    return os.environ.get("COMFYUI_STORYBOARD_BASE_URL", DEFAULT_COMFYUI_BASE_URL).rstrip("/")


def is_real_render_enabled() -> bool:
    return os.environ.get("ENABLE_COMFYUI_REAL_RENDER", "").strip().lower() == "true"


def _request_json(path: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
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
    return _request_json(f"/history/{prompt_id}")


def get_prompt_status(prompt_id: str) -> dict[str, Any]:
    history = get_prompt_history(prompt_id)
    if prompt_id in history and isinstance(history[prompt_id], dict):
        prompt_history = history[prompt_id]
        outputs = prompt_history.get("outputs", {})
        status = "completed" if outputs else "queued"
        return {
            "prompt_id": prompt_id,
            "status": status,
            "history": prompt_history,
        }
    return {
        "prompt_id": prompt_id,
        "status": "unknown",
        "history": history,
    }
