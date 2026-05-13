from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

DB_PATH = Path(
    os.environ.get("PRESENTATION_VISUAL_DB_PATH", "/opt/SERVICIOS_CINE/ailinkcinema_s2.db")
).resolve()
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
os.environ.setdefault("QUEUE_AUTO_START_SCHEDULER", "0")

from fastapi.testclient import TestClient

from app import app
from routes.auth_routes import create_access_token

def _auth_headers(user_id: str, email: str, org_id: str | None = None, roles: list[str] | None = None) -> dict[str, str]:
    effective_roles = roles or ["admin"]
    scopes_map = {
        "global_admin": ["admin:read", "admin:write", "projects:read", "projects:write", "comfyui:read", "comfyui:health"],
        "admin": ["projects:read", "projects:write", "comfyui:read", "comfyui:health"],
        "viewer": ["projects:read", "comfyui:read"],
    }
    role_key = effective_roles[0] if effective_roles else "admin"
    scopes = scopes_map.get(role_key, scopes_map["admin"])
    token = create_access_token({
        "sub": user_id,
        "email": email,
        "organization_id": org_id or "db4d7a5dadc9457ebaa2993a30d48201",
        "roles": effective_roles,
        "scopes": scopes,
    })
    return {"Authorization": f"Bearer {token}"}


class FundingIngestionCatalogIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
        os.environ.setdefault("QUEUE_AUTO_START_SCHEDULER", "0")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            env={**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{DB_PATH}"},
        )
        cls.admin_headers = _auth_headers(
            "dd66db71cbe643eb9494abd8616d3f64", "smoke_admin@example.com", roles=["global_admin"]
        )
        cls.tenant_headers = _auth_headers(
            "4b153c715f76428b9e299698e5ab5561", "smoke_tenant_a@example.com", roles=["viewer"]
        )

    def test_admin_seed_crud_and_public_read(self) -> None:
        with TestClient(app) as client:
            seed = client.post(
                "/api/admin/funding/sync/seed",
                headers=self.admin_headers,
                json={"force": True},
            )
            self.assertEqual(seed.status_code, 200)
            seed_json = seed.json()
            self.assertGreaterEqual(seed_json["sources_total"], 5)
            self.assertGreaterEqual(seed_json["calls_total"], 5)

            sources = client.get("/api/admin/funding/sources", headers=self.admin_headers)
            self.assertEqual(sources.status_code, 200)
            source_items = sources.json()["sources"]
            self.assertGreaterEqual(len(source_items), 5)
            iccaa = next(item for item in source_items if item["code"] == "ICAA")
            self.assertEqual(iccaa["region_scope"], "spain")

            denied = client.post(
                "/api/admin/funding/sources",
                headers=self.tenant_headers,
                json={
                    "name": "Denied source",
                    "code": "DENIED",
                    "region_scope": "spain",
                },
            )
            self.assertEqual(denied.status_code, 403)

            created_source = client.post(
                "/api/admin/funding/sources",
                headers=self.admin_headers,
                json={
                    "name": "Test Admin Source",
                    "code": "TEST_ADMIN_SOURCE",
                    "agency_name": "Admin QA",
                    "official_url": "https://example.com/source",
                    "region_scope": "europe",
                    "country_or_program": "Europe QA",
                    "verification_status": "official",
                },
            )
            self.assertEqual(created_source.status_code, 201)
            source_id = created_source.json()["id"]

            created_call = client.post(
                "/api/admin/funding/calls",
                headers=self.admin_headers,
                json={
                    "source_id": source_id,
                    "title": "QA Funding Call",
                    "region_scope": "europe",
                    "country_or_program": "Europe QA",
                    "agency_name": "Admin QA",
                    "official_url": "https://example.com/call",
                    "status": "upcoming",
                    "open_date": "2026-11-01T00:00:00+00:00",
                    "close_date": "2026-12-01T00:00:00+00:00",
                    "opportunity_type": "training",
                    "phase": "development",
                    "max_award_per_project": 25000,
                    "total_budget_pool": 500000,
                    "currency": "EUR",
                    "verification_status": "official",
                    "eligibility_json": {"eligible_applicants": ["Training labs"]},
                    "requirements_json": {"documents": ["Deck"]},
                    "collaboration_rules_json": {"minimum_partners": 1},
                    "point_system_json": {"criteria": ["Impact"]},
                    "eligible_formats_json": ["lab", "training"],
                    "notes_json": {"created_by": "integration_test"},
                    "requirement_items": [
                        {
                            "category": "documents",
                            "requirement_text": "Deck submission",
                            "is_mandatory": True,
                        }
                    ],
                },
            )
            self.assertEqual(created_call.status_code, 201)
            call_id = created_call.json()["id"]

            patched = client.patch(
                f"/api/admin/funding/calls/{call_id}",
                headers=self.admin_headers,
                json={"status": "open", "max_award_per_project": 30000},
            )
            self.assertEqual(patched.status_code, 200)
            self.assertEqual(patched.json()["status"], "open")
            self.assertEqual(patched.json()["max_award_per_project"], 30000)

            listed_calls = client.get(
                "/api/admin/funding/calls?region_scope=europe",
                headers=self.admin_headers,
            )
            self.assertEqual(listed_calls.status_code, 200)
            self.assertTrue(any(item["id"] == call_id for item in listed_calls.json()["calls"]))

            public_list = client.get("/api/funding/opportunities")
            self.assertEqual(public_list.status_code, 200)
            self.assertGreaterEqual(public_list.json()["count"], 4)

            public_detail = client.get(f"/api/funding/opportunities/{call_id}")
            self.assertEqual(public_detail.status_code, 200)
            detail_json = public_detail.json()
            self.assertEqual(detail_json["source"], "Test Admin Source")
            self.assertEqual(detail_json["official_url"], "https://example.com/call")
            self.assertEqual(detail_json["title"], "QA Funding Call")
            self.assertEqual(detail_json["status"], "open")
