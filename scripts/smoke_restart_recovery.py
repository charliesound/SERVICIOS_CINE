from __future__ import annotations

import atexit
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import httpx


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()
DATABASE_FILE = TEMP_ROOT / f"servicios_cine_restart_{uuid.uuid4().hex}.db"
SERVER_LOG_FILE = TEMP_ROOT / f"servicios_cine_restart_{uuid.uuid4().hex}.log"
SMOKE_DATABASE_URL = os.getenv(
    "SMOKE_DATABASE_URL",
    f"sqlite+aiosqlite:///{DATABASE_FILE.as_posix()}",
)
SMOKE_PORT = os.getenv("SMOKE_PORT", "8016")
BASE_URL = os.getenv("SMOKE_BASE_URL", f"http://127.0.0.1:{SMOKE_PORT}")
SERVER_START_TIMEOUT_SECONDS = float(os.getenv("SMOKE_START_TIMEOUT", "30"))


def cleanup_temp_artifacts() -> None:
    if os.getenv("SMOKE_KEEP_DB") == "1":
        return
    DATABASE_FILE.unlink(missing_ok=True)
    SERVER_LOG_FILE.unlink(missing_ok=True)


atexit.register(cleanup_temp_artifacts)


def start_server() -> subprocess.Popen:
    env = dict(os.environ)
    env["DATABASE_URL"] = SMOKE_DATABASE_URL
    env["PYTHONPATH"] = str(SRC_DIR)
    env.setdefault("APP_ENV", "production")
    env.setdefault("ENABLE_DEMO_ROUTES", "0")
    env.setdefault("ENABLE_EXPERIMENTAL_ROUTES", "0")
    env.setdefault("ENABLE_POSTPRODUCTION_ROUTES", "0")
    log_handle = SERVER_LOG_FILE.open("ab")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app:app",
            "--host",
            "127.0.0.1",
            "--port",
            SMOKE_PORT,
        ],
        cwd=str(SRC_DIR),
        env=env,
        stdout=log_handle,
        stderr=log_handle,
    )
    wait_for_server(process)
    return process


def wait_for_server(process: subprocess.Popen) -> None:
    deadline = time.time() + SERVER_START_TIMEOUT_SECONDS
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"Uvicorn exited before healthy. Revisa {SERVER_LOG_FILE}"
            )
        try:
            response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    process.terminate()
    raise RuntimeError(
        f"Timed out waiting for backend health. Revisa {SERVER_LOG_FILE}"
    )


def stop_server(process: subprocess.Popen | None) -> None:
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def assert_status(response: httpx.Response, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise RuntimeError(
            f"{label} failed: status={response.status_code} body={response.text}"
        )


def validate_cycle(client: httpx.Client, cycle_name: str) -> None:
    health = client.get("/health")
    assert_status(health, 200, f"{cycle_name} health")

    ready = client.get("/ready")
    assert_status(ready, 200, f"{cycle_name} ready")

    demo_status = client.get("/api/demo/status")
    assert_status(demo_status, 404, f"{cycle_name} demo disabled")
    print(f"{cycle_name.upper()}_OK=1")


def main() -> None:
    print(f"SMOKE_DATABASE_URL={SMOKE_DATABASE_URL}")
    print(f"SMOKE_LOG={SERVER_LOG_FILE}")

    server = start_server()
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "boot_1")
    finally:
        stop_server(server)

    server = start_server()
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "boot_2")
    finally:
        stop_server(server)

    print("RESTART_RECOVERY_SMOKE_OK=1")


if __name__ == "__main__":
    main()
