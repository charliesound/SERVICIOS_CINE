#!/usr/bin/env python3
from __future__ import annotations

import atexit
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8010")
SAMPLE_SCRIPT = """1 INT. SALA DE REUNIONES. NOCHE.
Una directora revisa un storyboard sobre una mesa llena de notas. El productor espera una decisión.
DIRECTORA
Necesito ver si esta escena respira.
PRODUCTOR
Entonces generemos otra versión."""


def request_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict | list]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def wait_for_health(base_url: str, timeout_seconds: float = 25.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            status, payload = request_json("GET", f"{base_url}/health")
            if status == 200 and isinstance(payload, dict) and payload.get("status") in {"healthy", "ok"}:
                return True
        except Exception:
            time.sleep(0.5)
    return False


def maybe_start_server(base_url: str) -> subprocess.Popen[str] | None:
    parsed = urllib.parse.urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8010
    try:
        with socket.create_connection((host, port), timeout=1):
            return None
    except OSError:
        pass

    if host not in {"127.0.0.1", "localhost"}:
        return None

    python_exec = str((ROOT / ".venv" / "bin" / "python").resolve()) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
    child_env = os.environ.copy()
    child_env.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
    child_env.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
    process = subprocess.Popen(
        [python_exec, "-m", "uvicorn", "app:app", "--host", host, "--port", str(port)],
        cwd=ROOT / "src",
        env=child_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    atexit.register(_terminate_process, process)
    return process


def _terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def validate_contract(base_url: str) -> None:
    status, profiles_payload = request_json("GET", f"{base_url}/api/cid/script-to-prompt/director-lenses")
    if status != 200 or not isinstance(profiles_payload, list) or not profiles_payload:
        raise RuntimeError("Director lenses endpoint did not return profiles")

    status, run_payload = request_json(
        "POST",
        f"{base_url}/api/cid/script-to-prompt/run",
        {
            "script_text": SAMPLE_SCRIPT,
            "output_type": "storyboard_frame",
            "max_scenes": 5,
            "style_preset": "premium_cinematic_saas",
            "use_llm": False,
            "director_lens_id": "adaptive_auteur_fusion",
            "allow_director_reference_names": False,
        },
    )
    if status != 200 or not isinstance(run_payload, dict):
        raise RuntimeError(f"Unexpected run response status: {status}")

    intents = run_payload.get("intents") or []
    prompts = run_payload.get("prompts") or []
    validations = run_payload.get("validations") or []
    if not intents:
        raise RuntimeError("No intents returned")
    if not prompts:
        raise RuntimeError("No prompts returned")
    if not validations:
        raise RuntimeError("No validations returned")

    first_intent = intents[0]
    first_prompt = prompts[0]
    first_validation = validations[0]
    directorial_intent = first_intent.get("directorial_intent")
    if not directorial_intent:
        raise RuntimeError("Missing directorial_intent in intent")
    positive_prompt = str(first_prompt.get("positive_prompt", ""))
    if "in the style of" in positive_prompt.lower():
        raise RuntimeError("Prompt contains forbidden director-style phrase")
    if len(positive_prompt.split()) < 35:
        raise RuntimeError("Prompt is not detailed enough")
    if "mise en scene" not in positive_prompt.lower():
        raise RuntimeError("Prompt missing mise en scene guidance")
    if float(first_validation.get("score", 0.0) or 0.0) < 0.6:
        raise RuntimeError("Validation score below threshold")


def main() -> int:
    process = maybe_start_server(BASE_URL)
    try:
        if not wait_for_health(BASE_URL):
            raise RuntimeError(f"Health endpoint not ready at {BASE_URL}")
        validate_contract(BASE_URL)
        print("PASS: Director lens contract smoke test")
        return 0
    finally:
        if process is not None:
            _terminate_process(process)


if __name__ == "__main__":
    raise SystemExit(main())
