from __future__ import annotations

import atexit
import json
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
DATABASE_FILE = TEMP_ROOT / f"servicios_cine_sprint13_{uuid.uuid4().hex}.db"
SERVER_LOG_FILE = TEMP_ROOT / f"servicios_cine_sprint13_{uuid.uuid4().hex}.log"
SMOKE_DATABASE_URL = os.getenv(
    "SMOKE_DATABASE_URL",
    f"sqlite+aiosqlite:///{DATABASE_FILE.as_posix()}",
)
SMOKE_PORT = os.getenv("SMOKE_PORT", "8013")
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
    env.setdefault("APP_ENV", "demo")
    env.setdefault("ENABLE_DEMO_ROUTES", "1")
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


def main() -> None:
    print(f"SMOKE_DATABASE_URL={SMOKE_DATABASE_URL}")
    print(f"SMOKE_LOG={SERVER_LOG_FILE}")
    server = start_server()
    try:
        with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
            health = client.get("/health")
            assert_status(health, 200, "health")

            demo_seed = client.post("/api/demo/quick-start")
            assert_status(demo_seed, 200, "demo quick-start")
            print("DEMO_SEED_OK=1")

            demo_status = client.get("/api/demo/status")
            assert_status(demo_status, 200, "demo status")
            print(f"DEMO_STATUS={demo_status.json()}")

            login = client.post(
                "/api/auth/login",
                json={
                    "email": "demo_free@servicios-cine.com",
                    "password": "demo123",
                },
            )
            assert_status(login, 200, "login free user")
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("LOGIN_OK=1")

            me_before = client.get("/api/auth/me", headers=headers)
            assert_status(me_before, 200, "auth me before plan change")
            print(f"PLAN_BEFORE={me_before.json()['plan']}")
            if me_before.json()["plan"] != "free":
                raise RuntimeError("Expected demo_free to start in free plan")

            plan_before = client.get("/api/plans/me", headers=headers)
            assert_status(plan_before, 200, "plan status before change")
            print(f"PLAN_STATUS_BEFORE={plan_before.json()['plan']}")

            change_plan = client.post(
                "/api/plans/change",
                json={"target_plan": "producer"},
                headers=headers,
            )
            assert_status(change_plan, 200, "internal plan change")
            print(f"PLAN_CHANGE={change_plan.json()}")

            relogin = client.post(
                "/api/auth/login",
                json={
                    "email": "demo_free@servicios-cine.com",
                    "password": "demo123",
                },
            )
            assert_status(relogin, 200, "relogin after plan change")
            token = relogin.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            me_after = client.get("/api/auth/me", headers=headers)
            assert_status(me_after, 200, "auth me after plan change")
            print(f"PLAN_AFTER={me_after.json()['plan']}")
            if me_after.json()["plan"] != "producer":
                raise RuntimeError("Plan change did not persist to producer")

            plan_after = client.get("/api/plans/me", headers=headers)
            assert_status(plan_after, 200, "plan status after change")
            print(f"PLAN_STATUS_AFTER={plan_after.json()['plan']}")

            project_name = f"Sprint13 Smoke {uuid.uuid4().hex[:8]}"
            create_project = client.post(
                "/api/projects",
                json={
                    "name": project_name,
                    "description": "Smoke reproducible Sprint 13",
                },
                headers=headers,
            )
            assert_status(create_project, 200, "create project")
            project = create_project.json()
            project_id = project["id"]
            print(f"PROJECT_ID={project_id}")

            update_script = client.put(
                f"/api/projects/{project_id}/script",
                json={
                    "script_text": (
                        "INT. ESTUDIO - DIA\n\n"
                        "Una productora revisa el plan de rodaje y prepara una demo comercial.\n\n"
                        "PRODUCTORA\nNecesito analisis, storyboard y export completo.\n"
                    )
                },
                headers=headers,
            )
            assert_status(update_script, 200, "update project script")

            analyze = client.post(
                f"/api/projects/{project_id}/analyze", headers=headers
            )
            assert_status(analyze, 200, "analyze project")
            print(f"ANALYZE_RESULT={analyze.json()}")

            storyboard = client.post(
                f"/api/projects/{project_id}/storyboard", headers=headers
            )
            assert_status(storyboard, 200, "storyboard project")
            print(f"STORYBOARD_SCENES={storyboard.json()['total_scenes']}")

            jobs = client.get(f"/api/projects/{project_id}/jobs", headers=headers)
            assert_status(jobs, 200, "list project jobs")
            jobs_body = jobs.json()["jobs"]
            if len(jobs_body) < 2:
                raise RuntimeError(
                    "Expected at least two jobs after analyze and storyboard"
                )
            print(f"JOBS_COUNT={len(jobs_body)}")

            assets = client.get(f"/api/projects/{project_id}/assets", headers=headers)
            assert_status(assets, 200, "list project assets")
            assets_body = assets.json()["assets"]
            if len(assets_body) < 2:
                raise RuntimeError(
                    "Expected at least two assets after analyze and storyboard"
                )
            print(f"ASSETS_COUNT={len(assets_body)}")

            metrics = client.get(f"/api/projects/{project_id}/metrics", headers=headers)
            assert_status(metrics, 200, "project metrics")
            print(f"METRICS={metrics.json()}")

            export_json = client.get(
                f"/api/projects/{project_id}/export/json", headers=headers
            )
            assert_status(export_json, 200, "export json")
            if not export_json.headers.get("content-type", "").startswith(
                "application/json"
            ):
                raise RuntimeError("JSON export did not return application/json")
            json_payload = export_json.json()
            print(f"EXPORT_JSON_KEYS={sorted(json_payload.keys())}")

            export_zip = client.get(
                f"/api/projects/{project_id}/export/zip", headers=headers
            )
            assert_status(export_zip, 200, "export zip")
            if not export_zip.headers.get("content-type", "").startswith(
                "application/zip"
            ):
                raise RuntimeError("ZIP export did not return application/zip")
            print(f"EXPORT_ZIP_BYTES={len(export_zip.content)}")

            history_snapshot = {
                "project_id": project_id,
                "jobs_count": len(jobs_body),
                "assets_count": len(assets_body),
                "plan_after": plan_after.json()["plan"],
            }
            print(
                f"HISTORY_SNAPSHOT={json.dumps(history_snapshot, ensure_ascii=False)}"
            )

        print("SPRINT13_SMOKE_OK=1")
    finally:
        stop_server(server)


if __name__ == "__main__":
    main()
