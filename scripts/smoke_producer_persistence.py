from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

import httpx


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database import AsyncSessionLocal, init_db  # noqa: E402
from models.core import Organization, Project  # noqa: E402


async def ensure_project() -> str:
    await init_db()
    async with AsyncSessionLocal() as db:
        org = Organization(
            name=f"Smoke Org {uuid.uuid4().hex[:6]}", billing_plan="studio"
        )
        db.add(org)
        await db.flush()

        project = Project(
            name=f"Smoke Project {uuid.uuid4().hex[:6]}",
            organization_id=org.id,
            status="active",
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return str(project.id)


async def main() -> None:
    base_url = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1:8000")
    project_id = os.getenv("SMOKE_PROJECT_ID") or await ensure_project()
    unique_suffix = uuid.uuid4().hex[:8]
    demo_request_email = f"smoke-{unique_suffix}@example.com"
    demo_request_name = f"Smoke Tester {unique_suffix}"

    async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
        initial_dashboard = await client.get("/api/producer/dashboard")
        initial_dashboard.raise_for_status()
        initial_dashboard_json = initial_dashboard.json()
        initial_saved_count = int(initial_dashboard_json["saved_opportunities"])
        initial_demo_request_count = int(initial_dashboard_json["demo_requests"])
        print("INITIAL_DASHBOARD_STATUS=", initial_dashboard.status_code)
        print("INITIAL_DASHBOARD_SAVED_OPPORTUNITIES=", initial_saved_count)
        print("INITIAL_DASHBOARD_DEMO_REQUESTS=", initial_demo_request_count)

        demo_request_payload = {
            "name": demo_request_name,
            "email": demo_request_email,
            "organization": f"Smoke Studio {unique_suffix}",
            "role": "Producer",
            "message": "Smoke test for producer persistence",
            "source": "smoke_test",
        }
        create_demo_request = await client.post(
            "/api/producer/demo-request", json=demo_request_payload
        )
        create_demo_request.raise_for_status()
        created_demo_request = create_demo_request.json()
        print("CREATE_DEMO_REQUEST_STATUS=", create_demo_request.status_code)
        print("CREATE_DEMO_REQUEST_ID=", created_demo_request["id"])

        list_demo_requests = await client.get("/api/producer/demo-requests")
        list_demo_requests.raise_for_status()
        demo_requests = list_demo_requests.json()
        if not any(
            request["id"] == created_demo_request["id"] for request in demo_requests
        ):
            raise RuntimeError(
                "Created demo request not returned by GET /api/producer/demo-requests"
            )
        print("LIST_DEMO_REQUESTS_STATUS=", list_demo_requests.status_code)
        print("LIST_DEMO_REQUESTS_COUNT=", len(demo_requests))

        opportunities = await client.get("/api/producer/funding/opportunities")
        opportunities.raise_for_status()
        opportunity_id = opportunities.json()[0]["id"]
        print("FUNDING_OPPORTUNITY_ID=", opportunity_id)

        create_saved = await client.post(
            "/api/producer/saved-opportunities",
            json={
                "project_id": project_id,
                "funding_opportunity_id": opportunity_id,
            },
        )
        create_saved.raise_for_status()
        created_saved = create_saved.json()
        print("CREATE_SAVED_STATUS=", create_saved.status_code)
        print("CREATE_SAVED_ID=", created_saved["id"])

        list_saved = await client.get(
            f"/api/producer/saved-opportunities?project_id={project_id}"
        )
        list_saved.raise_for_status()
        saved_items = list_saved.json()
        if not any(item["id"] == created_saved["id"] for item in saved_items):
            raise RuntimeError(
                "Created saved opportunity not returned by GET /api/producer/saved-opportunities"
            )
        print("LIST_SAVED_STATUS=", list_saved.status_code)
        print("LIST_SAVED_COUNT=", len(saved_items))

        dashboard = await client.get("/api/producer/dashboard")
        dashboard.raise_for_status()
        dashboard_json = dashboard.json()
        dashboard_saved_count = int(dashboard_json["saved_opportunities"])
        dashboard_demo_request_count = int(dashboard_json["demo_requests"])
        if dashboard_saved_count < initial_saved_count + 1:
            raise RuntimeError(
                "Dashboard saved_opportunities did not reflect persisted data"
            )
        if dashboard_demo_request_count < initial_demo_request_count + 1:
            raise RuntimeError("Dashboard demo_requests did not reflect persisted data")
        print("DASHBOARD_STATUS=", dashboard.status_code)
        print("DASHBOARD_SAVED_OPPORTUNITIES=", dashboard_saved_count)
        print("DASHBOARD_DEMO_REQUESTS=", dashboard_demo_request_count)

        delete_saved = await client.delete(
            f"/api/producer/saved-opportunities/{created_saved['id']}"
        )
        delete_saved.raise_for_status()
        print("DELETE_SAVED_STATUS=", delete_saved.status_code)

        list_saved_after_delete = await client.get(
            f"/api/producer/saved-opportunities?project_id={project_id}"
        )
        list_saved_after_delete.raise_for_status()
        saved_items_after_delete = list_saved_after_delete.json()
        if any(item["id"] == created_saved["id"] for item in saved_items_after_delete):
            raise RuntimeError("Saved opportunity still present after DELETE")
        print("LIST_SAVED_AFTER_DELETE_COUNT=", len(saved_items_after_delete))

        final_dashboard = await client.get("/api/producer/dashboard")
        final_dashboard.raise_for_status()
        final_dashboard_json = final_dashboard.json()
        final_saved_count = int(final_dashboard_json["saved_opportunities"])
        final_demo_request_count = int(final_dashboard_json["demo_requests"])
        if final_saved_count > dashboard_saved_count - 1:
            raise RuntimeError(
                "Dashboard saved_opportunities did not decrease after DELETE"
            )
        if final_demo_request_count < dashboard_demo_request_count:
            raise RuntimeError("Dashboard demo_requests regressed unexpectedly")
        print("FINAL_DASHBOARD_STATUS=", final_dashboard.status_code)
        print("FINAL_DASHBOARD_SAVED_OPPORTUNITIES=", final_saved_count)
        print("FINAL_DASHBOARD_DEMO_REQUESTS=", final_demo_request_count)
        print("SMOKE_OK=1")


if __name__ == "__main__":
    asyncio.run(main())
