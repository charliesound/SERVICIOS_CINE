from __future__ import annotations

import atexit
import json
import os
import sqlite3
import socket
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import httpx


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
TEMP_ROOT = (REPO_ROOT / ".smoke_tmp").resolve()
DATABASE_FILE = TEMP_ROOT / f"servicios_cine_restart_{uuid.uuid4().hex}.db"
SERVER_LOG_FILE = TEMP_ROOT / f"servicios_cine_restart_{uuid.uuid4().hex}.log"


def to_wsl_posix(path: Path) -> str:
    raw = str(path)
    prefix = "\\\\wsl.localhost\\Ubuntu\\"
    if raw.startswith(prefix):
        return "/" + raw[len(prefix) :].replace("\\", "/")
    return path.as_posix()


SMOKE_DATABASE_URL = os.getenv(
    "SMOKE_DATABASE_URL",
    f"sqlite+aiosqlite:///{to_wsl_posix(DATABASE_FILE)}",
)
SMOKE_PORT = os.getenv("SMOKE_PORT", "8016")
BASE_URL = os.getenv("SMOKE_BASE_URL", f"http://127.0.0.1:{SMOKE_PORT}")
SERVER_START_TIMEOUT_SECONDS = float(os.getenv("SMOKE_START_TIMEOUT", "30"))
QUEUE_RUNTIME_ORGANIZATION_ID = "__queue_runtime__"
QUEUE_RUNTIME_PROJECT_ID = "__queue_runtime__"
FAKE_BACKEND_HOST = "127.0.0.1"
FAKE_BACKEND_PORT = 0
INSTANCE_CONFIG_FILE = TEMP_ROOT / f"instances_smoke_{uuid.uuid4().hex}.yml"


class FakeComfyHandler(BaseHTTPRequestHandler):
    prompt_counter = 0

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        del format, args

    def do_GET(self) -> None:
        if self.path == "/system_stats":
            self._send_json({"status": "ok"})
            return
        if self.path.startswith("/history/"):
            self._send_json({})
            return
        self._send_json({"detail": "not_found"}, status=404)

    def do_POST(self) -> None:
        if self.path != "/prompt":
            self._send_json({"detail": "not_found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        type(self).prompt_counter += 1
        self._send_json({"prompt_id": f"smoke-prompt-{self.prompt_counter}"})


def cleanup_temp_artifacts() -> None:
    if os.getenv("SMOKE_KEEP_DB") == "1":
        return
    DATABASE_FILE.unlink(missing_ok=True)
    SERVER_LOG_FILE.unlink(missing_ok=True)
    INSTANCE_CONFIG_FILE.unlink(missing_ok=True)


atexit.register(cleanup_temp_artifacts)


def sqlite_path_from_url(database_url: str) -> Path:
    if not database_url.startswith("sqlite+"):
        raise RuntimeError(f"Smoke solo soporta SQLite real, recibido: {database_url}")
    parsed = urlparse(database_url.replace("+aiosqlite", "", 1))
    return Path(parsed.path).resolve()


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((FAKE_BACKEND_HOST, 0))
        return int(sock.getsockname()[1])


def write_instances_config(fake_backend_port: int) -> None:
    INSTANCE_CONFIG_FILE.write_text(
        """
backends:
  still:
    name: "Smoke Still Backend"
    type: "comfyui"
    host: "127.0.0.1"
    port: PORT_PLACEHOLDER
    base_url: "http://127.0.0.1:PORT_PLACEHOLDER"
    health_endpoint: "/system_stats"
    max_concurrent_jobs: 2
    priority: 1
    enabled: true
    capabilities:
      - "image_generation"

routing_rules:
  task_type_mapping:
    still: "still"
    image: "still"
  fallback_backend: "still"
  experimental_backend: "still"

health_check:
  interval_seconds: 30
  timeout_seconds: 5
  max_retries: 3
""".strip().replace("PORT_PLACEHOLDER", str(fake_backend_port))
        + "\n",
        encoding="utf-8",
    )


def start_fake_backend(port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((FAKE_BACKEND_HOST, port), FakeComfyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def stop_fake_backend(server: ThreadingHTTPServer | None) -> None:
    if server is None:
        return
    server.shutdown()
    server.server_close()


def start_server(queue_mode: str, auto_start_scheduler: bool) -> subprocess.Popen:
    env = dict(os.environ)
    env["DATABASE_URL"] = SMOKE_DATABASE_URL
    env["INSTANCE_CONFIG_PATH"] = to_wsl_posix(INSTANCE_CONFIG_FILE)
    env["PYTHONPATH"] = str(SRC_DIR)
    env["QUEUE_PERSISTENCE_MODE"] = queue_mode
    env["QUEUE_AUTO_START_SCHEDULER"] = "1" if auto_start_scheduler else "0"
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
    log_handle.close()
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


def create_render_job(client: httpx.Client, suffix: str) -> str:
    response = client.post(
        "/api/render/jobs",
        json={
            "task_type": "still",
            "workflow_key": "sd_xl",
            "prompt": {"text": f"smoke {suffix}"},
            "user_id": f"smoke-user-{suffix}",
            "user_plan": "producer",
            "priority": 5,
        },
    )
    assert_status(response, 200, f"create job {suffix}")
    payload = response.json()
    return payload["job_id"]


def wait_for_queue_status(
    client: httpx.Client,
    job_id: str,
    expected_status: str,
    timeout_seconds: float,
) -> dict:
    deadline = time.time() + timeout_seconds
    last_payload: dict | None = None
    while time.time() < deadline:
        response = client.get(f"/api/queue/status/{job_id}")
        if response.status_code == 200:
            payload = response.json()
            last_payload = payload
            if payload.get("status") == expected_status:
                return payload
        time.sleep(0.5)
    raise RuntimeError(
        f"Job {job_id} did not reach status {expected_status}. Last={last_payload}"
    )


def get_db_job(job_id: str) -> dict:
    db_path = sqlite_path_from_url(SMOKE_DATABASE_URL)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, status, error_message, result_data FROM project_jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    if row is None:
        raise RuntimeError(f"Job {job_id} not found in DB")
    return {
        "id": row[0],
        "status": row[1],
        "error_message": row[2],
        "result_data": json.loads(row[3]) if row[3] else {},
    }


def set_db_job_status(job_id: str, status: str) -> None:
    db_path = sqlite_path_from_url(SMOKE_DATABASE_URL)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT result_data FROM project_jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Job {job_id} not found for DB update")
        payload = json.loads(row[0]) if row[0] else {}
        payload["status"] = status
        if status == "scheduled":
            payload["scheduled_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        conn.execute(
            "UPDATE project_jobs SET organization_id = ?, project_id = ?, status = ?, result_data = ? WHERE id = ?",
            (
                QUEUE_RUNTIME_ORGANIZATION_ID,
                QUEUE_RUNTIME_PROJECT_ID,
                status,
                json.dumps(payload, ensure_ascii=True),
                job_id,
            ),
        )
        conn.commit()


def expect_db_state(job_id: str, status: str, error_message: str | None = None) -> dict:
    row = get_db_job(job_id)
    if row["status"] != status:
        raise RuntimeError(
            f"DB job {job_id} expected status={status} got {row['status']}"
        )
    if error_message is not None and row["error_message"] != error_message:
        raise RuntimeError(
            f"DB job {job_id} expected error={error_message} got {row['error_message']}"
        )
    return row


def expect_render_detail(client: httpx.Client, job_id: str, status: str) -> dict:
    response = client.get(f"/api/render/jobs/{job_id}")
    assert_status(response, 200, f"render detail {job_id}")
    payload = response.json()
    if payload.get("status") != status:
        raise RuntimeError(
            f"Render detail {job_id} expected status={status} got {payload}"
        )
    return payload


def run_db_recovery_smoke() -> None:
    running_job_id: str | None = None
    queued_job_id: str | None = None
    scheduled_job_id: str | None = None

    server = start_server(queue_mode="db", auto_start_scheduler=True)
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "db_boot_running")
            running_job_id = create_render_job(client, "running")
            wait_for_queue_status(client, running_job_id, "running", 20.0)
            expect_db_state(running_job_id, "running")
            print(f"DB_RUNNING_JOB={running_job_id}")
    finally:
        stop_server(server)

    server = start_server(queue_mode="db", auto_start_scheduler=False)
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "db_boot_recovery")
            if running_job_id is None:
                raise RuntimeError("Running job id missing before recovery check")
            running_recovered = expect_render_detail(client, running_job_id, "failed")
            running_row = expect_db_state(running_job_id, "failed", "backend_restart")
            recovery_reason = running_row["result_data"].get("recovery_reason")
            if recovery_reason != "backend_restart":
                raise RuntimeError(
                    f"Expected recovery_reason=backend_restart got {recovery_reason}"
                )

            queued_job_id = create_render_job(client, "queued")
            wait_for_queue_status(client, queued_job_id, "queued", 5.0)
            expect_db_state(queued_job_id, "queued")

            scheduled_job_id = create_render_job(client, "scheduled")
            wait_for_queue_status(client, scheduled_job_id, "queued", 5.0)
            set_db_job_status(scheduled_job_id, "scheduled")
            expect_db_state(scheduled_job_id, "scheduled")

            print(f"DB_RECOVERED_FAILED_JOB={running_recovered['job_id']}")
            print(f"DB_QUEUED_JOB={queued_job_id}")
            print(f"DB_SCHEDULED_JOB={scheduled_job_id}")
    finally:
        stop_server(server)

    server = start_server(queue_mode="db", auto_start_scheduler=False)
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "db_boot_requeue")
            if queued_job_id is None or scheduled_job_id is None:
                raise RuntimeError("Queued recovery ids missing before requeue check")
            queued_payload = wait_for_queue_status(client, queued_job_id, "queued", 5.0)
            scheduled_payload = wait_for_queue_status(
                client, scheduled_job_id, "queued", 5.0
            )
            expect_db_state(queued_job_id, "queued")
            scheduled_row = expect_db_state(scheduled_job_id, "queued")
            if scheduled_row["result_data"].get("event") != "startup_requeue":
                raise RuntimeError(
                    f"Expected startup_requeue event for {scheduled_job_id}, got {scheduled_row['result_data']}"
                )
            print(
                f"DB_QUEUED_RECOVERED={queued_payload['job_id']}:{queued_payload['status']}"
            )
            print(
                f"DB_SCHEDULED_RECOVERED={scheduled_payload['job_id']}:{scheduled_payload['status']}"
            )
    finally:
        stop_server(server)


def run_memory_smoke() -> None:
    server = start_server(queue_mode="memory", auto_start_scheduler=False)
    try:
        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            validate_cycle(client, "memory_boot")
            job_id = create_render_job(client, "memory")
            payload = wait_for_queue_status(client, job_id, "queued", 5.0)
            print(f"MEMORY_JOB={payload['job_id']}:{payload['status']}")
    finally:
        stop_server(server)


def main() -> None:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    fake_backend_port = get_free_port()
    write_instances_config(fake_backend_port)
    print(f"SMOKE_DATABASE_URL={SMOKE_DATABASE_URL}")
    print(f"SMOKE_LOG={SERVER_LOG_FILE}")
    print(f"SMOKE_INSTANCE_CONFIG={INSTANCE_CONFIG_FILE}")
    print(f"SMOKE_FAKE_BACKEND_PORT={fake_backend_port}")

    fake_backend = start_fake_backend(fake_backend_port)
    try:
        run_db_recovery_smoke()
        run_memory_smoke()
    finally:
        stop_fake_backend(fake_backend)

    print("RESTART_RECOVERY_SMOKE_OK=1")


if __name__ == "__main__":
    main()
