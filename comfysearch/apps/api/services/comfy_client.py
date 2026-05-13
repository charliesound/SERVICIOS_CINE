"""
comfy_client.py — Envía workflows a ComfyUI y recibe resultados.

Soporta las 4 instancias (still, video, dubbing, lab).
Puede inyectar parámetros (prompts, seed, etc.) antes de enviar.
"""

import json
import time
import re
from typing import Optional
import requests

INSTANCES = {
    "still": "http://127.0.0.1:8188",
    "video": "http://127.0.0.1:8189",
    "dubbing": "http://127.0.0.1:8190",
    "lab": "http://127.0.0.1:8191",
}

DEFAULT_CLIENT_ID = "comfysearch"


def resolve_url(backend: str = "still") -> str:
    return INSTANCES.get(backend, INSTANCES["still"])


def inject_parameters(workflow: dict, params: dict) -> dict:
    """Inyecta parámetros en un workflow JSON usando placeholders {{KEY}} o directamente."""
    serialized = json.dumps(workflow)
    for key, value in params.items():
        placeholder = "{{" + key.upper() + "}}"
        serialized = serialized.replace(placeholder, str(value))
    return json.loads(serialized)


def submit_prompt(workflow: dict, backend: str = "still", client_id: str = None, timeout: int = 30) -> dict:
    url = f"{resolve_url(backend)}/prompt"
    payload = {
        "prompt": workflow,
        "client_id": client_id or DEFAULT_CLIENT_ID,
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_history(prompt_id: str, backend: str = "still") -> dict:
    url = f"{resolve_url(backend)}/history/{prompt_id}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def poll_until_complete(prompt_id: str, backend: str = "still", timeout: int = 120, interval: int = 2) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id, backend)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(interval)
    raise TimeoutError(f"Prompt {prompt_id} no completó en {timeout}s")


def extract_outputs(history: dict, prompt_id: str) -> dict:
    outputs = {"images": [], "videos": [], "audio": [], "files": []}
    prompt_history = history.get(prompt_id, {})
    node_outputs = prompt_history.get("outputs", {})
    for node_id, node_data in node_outputs.items():
        for key, items in node_data.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    fname = item.get("filename", "")
                    ftype = item.get("type", "")
                    if fname:
                        entry = {"filename": fname, "node_id": node_id}
                        if ftype in ("video", "animation", "gif"):
                            outputs["videos"].append(entry)
                        elif ftype in ("audio", "wav", "mp3"):
                            outputs["audio"].append(entry)
                        else:
                            outputs["images"].append(entry)
    return outputs


def run_workflow(workflow_path: str, backend: str = "still", params: dict = None, inject: bool = True) -> dict:
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    if inject and params:
        workflow = inject_parameters(workflow, params)

    result = submit_prompt(workflow, backend=backend)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI no devolvió prompt_id: {result}")

    history = poll_until_complete(prompt_id, backend=backend)
    outputs = extract_outputs(history, prompt_id)

    return {
        "prompt_id": prompt_id,
        "status": "completed",
        "outputs": outputs,
        "history": history,
    }
