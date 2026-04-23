from __future__ import annotations

import atexit
import asyncio
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
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


TEMP_ROOT = Path(tempfile.gettempdir()).resolve()
DATABASE_BASENAME = f"ailinkcinema_s7_review_delivery_{uuid.uuid4().hex}.db"
DEFAULT_DATABASE_FILE = TEMP_ROOT / DATABASE_BASENAME
SERVER_LOG_FILE = TEMP_ROOT / f"ailinkcinema_s7_review_delivery_{uuid.uuid4().hex}.log"


def _cleanup_temp_artifacts() -> None:
    if os.getenv("SMOKE_KEEP_DB") == "1":
        return
    if DEFAULT_DATABASE_FILE.exists():
        DEFAULT_DATABASE_FILE.unlink(missing_ok=True)
    if SERVER_LOG_FILE.exists():
        SERVER_LOG_FILE.unlink(missing_ok=True)


atexit.register(_cleanup_temp_artifacts)


def _default_database_url() -> str:
    return f"sqlite+aiosqlite:///{DEFAULT_DATABASE_FILE.as_posix()}"


def _database_file_from_url(database_url: str) -> Path | None:
    prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(prefix):
        return None
    return Path(database_url.replace(prefix, "", 1))


DATABASE_URL = os.getenv(
    "SMOKE_DATABASE_URL", os.getenv("DATABASE_URL", _default_database_url())
)
DATABASE_FILE = _database_file_from_url(DATABASE_URL)
SMOKE_PORT = os.getenv("SMOKE_PORT", "8017")
BASE_URL = os.getenv("SMOKE_BASE_URL", f"http://127.0.0.1:{SMOKE_PORT}")
SERVER_START_TIMEOUT_SECONDS = float(os.getenv("SMOKE_START_TIMEOUT", "20"))

os.environ["DATABASE_URL"] = DATABASE_URL


async def ensure_project() -> str:
    env = dict(os.environ)
    env["DATABASE_URL"] = DATABASE_URL
    env["PYTHONPATH"] = "src"
    bootstrap_code = """import asyncio
import uuid

from database import AsyncSessionLocal, init_db
from models.core import Organization, Project


async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        org = Organization(
            name=f'Review Delivery Smoke Org {uuid.uuid4().hex[:6]}',
            billing_plan='studio',
        )
        db.add(org)
        await db.flush()

        project = Project(
            name=f'Review Delivery Smoke Project {uuid.uuid4().hex[:6]}',
            organization_id=org.id,
            status='active',
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        print(project.id)


asyncio.run(main())
"""
    result = subprocess.run(
        [sys.executable, "-c", bootstrap_code],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()[-1]


def start_server() -> subprocess.Popen:
    env = dict(os.environ)
    env["DATABASE_URL"] = DATABASE_URL
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
        cwd=str(REPO_ROOT),
        env=env,
        stdout=log_handle,
        stderr=log_handle,
    )
    wait_for_server(process)
    time.sleep(5)
    return process


def wait_for_server(process: subprocess.Popen) -> None:
    deadline = time.time() + SERVER_START_TIMEOUT_SECONDS

    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Uvicorn process exited before becoming healthy")

        try:
            response = httpx.get(f"{BASE_URL}/health", timeout=2.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass

        time.sleep(0.5)

    process.terminate()
    raise RuntimeError("Timed out waiting for uvicorn health endpoint")


def stop_server(process: subprocess.Popen | None) -> None:
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


async def main() -> None:
    print("DATABASE_URL=", DATABASE_URL)
    print("DATABASE_FILE=", DATABASE_FILE)
    print(
        "DATABASE_FILE_EXISTS_AFTER_INIT=",
        DATABASE_FILE.exists() if DATABASE_FILE is not None else "n/a",
    )

    # Check if external server is available
    use_external = False
    if os.getenv("SMOKE_BASE_URL"):
        try:
            response = httpx.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                use_external = True
                print(f"Using external server at {BASE_URL}")
        except Exception:
            pass

    server = None
    if not use_external:
        server = start_server()
    try:
        project_id = await ensure_project()
        time.sleep(5)
        print("PROJECT_ID=", project_id)

        with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
            openapi = client.get("/openapi.json")
            print("FIRST_START_OPENAPI_STATUS=", openapi.status_code)

            review = client.post(
                f"/api/reviews/projects/{project_id}",
                json={
                    "target_id": "asset-smoke-001",
                    "target_type": "asset",
                    "status": "pending",
                },
            )
            print("CREATE_REVIEW_STATUS=", review.status_code)
            print("CREATE_REVIEW_BODY=", review.text)
            review_id = review.json()["id"]

            comment = client.post(
                f"/api/reviews/{review_id}/comments",
                json={
                    "body": "Smoke comment for review-delivery persistence",
                    "author_name": "Smoke Reviewer",
                },
            )
            print("CREATE_COMMENT_STATUS=", comment.status_code)
            print("CREATE_COMMENT_BODY=", comment.text)
            comment_id = comment.json()["id"]

            decision = client.post(
                f"/api/reviews/{review_id}/decisions",
                json={
                    "status_applied": "approved",
                    "rationale_note": "Approved during smoke test",
                    "author_name": "Smoke Reviewer",
                },
            )
            print("CREATE_DECISION_STATUS=", decision.status_code)
            print("CREATE_DECISION_BODY=", decision.text)
            decision_id = decision.json()["id"]

            review_detail = client.get(f"/api/reviews/{review_id}")
            print("REVIEW_DETAIL_STATUS=", review_detail.status_code)
            print("REVIEW_DETAIL_BODY=", review_detail.text)

            deliverables = client.get(
                f"/api/delivery/projects/{project_id}/deliverables"
            )
            print("LIST_DELIVERABLES_STATUS=", deliverables.status_code)
            print("LIST_DELIVERABLES_BODY=", deliverables.text)
            deliverable_body = deliverables.json()["deliverables"]
            print("DELIVERABLE_COUNT_AFTER_FIRST_APPROVAL=", len(deliverable_body))
            if len(deliverable_body) != 1:
                raise RuntimeError("Expected exactly one deliverable after approval")
            deliverable_id = deliverable_body[0]["id"]

            review_deliverable = client.get(
                f"/api/delivery/reviews/{review_id}/deliverable"
            )
            print("GET_DELIVERABLE_BY_REVIEW_STATUS=", review_deliverable.status_code)
            print("GET_DELIVERABLE_BY_REVIEW_BODY=", review_deliverable.text)

            second_decision = client.post(
                f"/api/reviews/{review_id}/decisions",
                json={
                    "status_applied": "approved",
                    "rationale_note": "Approved again to verify idempotency",
                    "author_name": "Smoke Reviewer",
                },
            )
            print("SECOND_DECISION_STATUS=", second_decision.status_code)
            print("SECOND_DECISION_BODY=", second_decision.text)

            deliverables_after_second_decision = client.get(
                f"/api/delivery/projects/{project_id}/deliverables"
            )
            print(
                "LIST_DELIVERABLES_AFTER_SECOND_DECISION_STATUS=",
                deliverables_after_second_decision.status_code,
            )
            print(
                "LIST_DELIVERABLES_AFTER_SECOND_DECISION_BODY=",
                deliverables_after_second_decision.text,
            )
            deliverables_after_body = deliverables_after_second_decision.json()[
                "deliverables"
            ]
            print(
                "DELIVERABLE_COUNT_AFTER_SECOND_APPROVAL=",
                len(deliverables_after_body),
            )
            if len(deliverables_after_body) != 1:
                raise RuntimeError(
                    "Deliverable duplicated after second approval decision"
                )
    finally:
        stop_server(server)

    # Second run - also check for external server
    server2 = None
    if use_external:
        print("Using external server for second run")
    else:
        server2 = start_server()
    try:
        with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
            openapi = client.get("/openapi.json")
            review_detail = client.get(f"/api/reviews/{review_id}")
            comments = client.get(f"/api/reviews/{review_id}/comments")
            deliverables = client.get(
                f"/api/delivery/projects/{project_id}/deliverables"
            )
            review_deliverable = client.get(
                f"/api/delivery/reviews/{review_id}/deliverable"
            )

            print("SECOND_START_OPENAPI_STATUS=", openapi.status_code)
            print("REVIEW_DETAIL_AFTER_RESTART_STATUS=", review_detail.status_code)
            print("REVIEW_DETAIL_AFTER_RESTART_BODY=", review_detail.text)
            print("COMMENTS_AFTER_RESTART_STATUS=", comments.status_code)
            print("COMMENTS_AFTER_RESTART_BODY=", comments.text)
            print("DELIVERABLES_AFTER_RESTART_STATUS=", deliverables.status_code)
            print("DELIVERABLES_AFTER_RESTART_BODY=", deliverables.text)
            print(
                "GET_DELIVERABLE_BY_REVIEW_AFTER_RESTART_STATUS=",
                review_deliverable.status_code,
            )
            print(
                "GET_DELIVERABLE_BY_REVIEW_AFTER_RESTART_BODY=",
                review_deliverable.text,
            )

            review_detail_body = review_detail.json()
            comment_list_body = comments.json()["comments"]
            deliverables_body = deliverables.json()["deliverables"]

            comment_ids = [item["id"] for item in comment_list_body]
            deliverable_ids = [item["id"] for item in deliverables_body]
            decision_ids = [item["id"] for item in review_detail_body["logs"]]
            print(
                "DATABASE_FILE_EXISTS_AFTER_RESTART=",
                DATABASE_FILE.exists() if DATABASE_FILE is not None else "n/a",
            )

            print(
                "REVIEW_ID_FOUND_AFTER_RESTART=", review_detail_body["id"] == review_id
            )
            print("COMMENT_ID_FOUND_AFTER_RESTART=", comment_id in comment_ids)
            print("DECISION_ID_FOUND_AFTER_RESTART=", decision_id in decision_ids)
            print(
                "DELIVERABLE_ID_FOUND_AFTER_RESTART=",
                deliverable_id in deliverable_ids,
            )
            print("SMOKE_OK=1")
    finally:
        if server2:
            stop_server(server2)
        elif use_external:
            pass  # External server, don't stop it


if __name__ == "__main__":
    asyncio.run(main())
