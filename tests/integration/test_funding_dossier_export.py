from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
import unittest
from pathlib import Path


TEST_DB_PATH = Path("/tmp/test_funding_dossier_export.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
os.environ["USE_ALEMBIC"] = "0"
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

from fastapi.testclient import TestClient

from app import app
import models  # noqa: F401
from database import Base, engine
from routes.auth_routes import create_access_token


ORG_A = "org-a-funding-dossier-00000000001"
ORG_B = "org-b-funding-dossier-00000000001"
ADMIN_A = "admin-a-funding-dossier-0000001"
USER_B = "user-b-funding-dossier-00000001"
PROJECT_ID = "project-funding-dossier-0000001"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _insert_row(connection: sqlite3.Connection, table_name: str, payload: dict[str, object]) -> None:
    available_columns = _table_columns(connection, table_name)
    hydrated_payload = dict(payload)
    timestamp = "2026-04-22 00:00:00"
    if "created_at" in available_columns and "created_at" not in hydrated_payload:
        hydrated_payload["created_at"] = timestamp
    if "updated_at" in available_columns and "updated_at" not in hydrated_payload:
        hydrated_payload["updated_at"] = timestamp
    columns = [column for column in hydrated_payload if column in available_columns]
    values = [hydrated_payload[column] for column in columns]
    placeholders = ", ".join("?" for _ in columns)
    connection.execute(f"DELETE FROM {table_name} WHERE id = ?", (payload["id"],))
    connection.execute(
        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )


def _seed_test_data() -> None:
    connection = sqlite3.connect(str(TEST_DB_PATH))
    try:
        _insert_row(connection, "organizations", {"id": ORG_A, "name": "Funding Dossier Org A", "billing_plan": "free", "is_active": 1})
        _insert_row(connection, "organizations", {"id": ORG_B, "name": "Funding Dossier Org B", "billing_plan": "free", "is_active": 1})

        _insert_row(
            connection,
            "users",
            {
                "id": ADMIN_A,
                "organization_id": ORG_A,
                "username": "dossier_admin_a",
                "email": "dossier_admin_a@example.com",
                "hashed_password": "unused",
                "full_name": "Dossier Admin A",
                "role": "ADMIN",
                "is_active": 1,
                "billing_plan": "free",
                "program": "demo",
                "signup_type": "seed",
                "account_status": "active",
                "access_level": "admin",
                "cid_enabled": 1,
                "onboarding_completed": 1,
            },
        )
        _insert_row(
            connection,
            "users",
            {
                "id": USER_B,
                "organization_id": ORG_B,
                "username": "dossier_user_b",
                "email": "dossier_user_b@example.com",
                "hashed_password": "unused",
                "full_name": "Dossier User B",
                "role": "PRODUCER",
                "is_active": 1,
                "billing_plan": "free",
                "program": "demo",
                "signup_type": "seed",
                "account_status": "active",
                "access_level": "standard",
                "cid_enabled": 1,
                "onboarding_completed": 1,
            },
        )

        _insert_row(
            connection,
            "projects",
            {
                "id": PROJECT_ID,
                "organization_id": ORG_A,
                "name": "Puentes de Sal",
                "description": "Feature film de coproduccion entre Espana, Francia y Colombia.",
                "status": "production",
                "script_text": "Largometraje de coproduccion entre Espana, Francia y Colombia con estrategia europea e iberoamericana.",
            },
        )
        _insert_row(
            connection,
            "production_breakdowns",
            {
                "id": "dossier-breakdown-000000000001",
                "project_id": PROJECT_ID,
                "organization_id": ORG_A,
                "script_text": "Seed script",
                "breakdown_json": json.dumps(
                    {
                        "metadata": {"total_scenes": 36, "total_characters": 14, "total_locations": 11},
                        "department_breakdown": {
                            "production": {"count": 6},
                            "travel": {"count": 3},
                            "cast": {"count": 14},
                        },
                    },
                    ensure_ascii=True,
                ),
                "budget_estimate": 875000.0,
                "status": "completed",
            },
        )
        _insert_row(
            connection,
            "project_budgets",
            {
                "id": "dossier-budget-00000000000001",
                "project_id": PROJECT_ID,
                "organization_id": ORG_A,
                "scenario_type": "premium",
                "grand_total": 875000.0,
                "status": "draft",
            },
        )

        budget_lines = [
            ("budget-line-1", "above_the_line", 180000.0),
            ("budget-line-2", "production_btl", 320000.0),
            ("budget-line-3", "postproduction", 150000.0),
            ("budget-line-4", "contingency", 87500.0),
        ]
        for line_id, section, total_cost in budget_lines:
            _insert_row(
                connection,
                "budget_lines",
                {
                    "id": line_id,
                    "budget_id": "dossier-budget-00000000000001",
                    "section": section,
                    "category": section,
                    "description": section,
                    "quantity": 1,
                    "unit_cost": total_cost,
                    "total_cost": total_cost,
                    "is_manual_override": 0,
                    "is_enabled": 1,
                },
            )

        project_sources = [
            ("dossier-source-1", "equity", 120000.0, "secured"),
            ("dossier-source-2", "pre_sale", 180000.0, "negotiating"),
            ("dossier-source-3", "private_investor", 90000.0, "projected"),
        ]
        for source_id, source_type, amount, status in project_sources:
            _insert_row(
                connection,
                "project_funding_sources",
                {
                    "id": source_id,
                    "project_id": PROJECT_ID,
                    "organization_id": ORG_A,
                    "source_name": f"{source_type}-{status}",
                    "source_type": source_type,
                    "amount": amount,
                    "currency": "EUR",
                    "status": status,
                    "notes": "seed",
                },
            )

        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class FundingDossierExportIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "dossier_admin_a@example.com")
        cls.tenant_b_headers = _auth_headers(USER_B, "dossier_user_b@example.com")
        seed_response = cls.client.post(
            "/api/admin/funding/sync/seed",
            headers=cls.admin_headers,
            json={"force": True},
        )
        if seed_response.status_code != 200:
            raise RuntimeError(seed_response.text)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def test_funding_dossier_json_pdf_and_persist(self) -> None:
        dossier = self.client.get(
            f"/api/projects/{PROJECT_ID}/funding/dossier",
            headers=self.admin_headers,
        )
        self.assertEqual(dossier.status_code, 200)
        dossier_json = dossier.json()
        self.assertEqual(dossier_json["project_profile"]["project_id"], PROJECT_ID)
        self.assertEqual(dossier_json["project_profile"]["organization_id"], ORG_A)
        self.assertEqual(dossier_json["budget_summary"]["total_budget"], 875000.0)
        self.assertIn("current_funding_gap", dossier_json["private_funding_summary"])
        self.assertGreaterEqual(dossier_json["funding_match_summary"]["matches_count"], 5)
        self.assertTrue(dossier_json["top_matches"])
        self.assertIn("missing_documents", dossier_json["checklist"])

        pdf_response = self.client.get(
            f"/api/projects/{PROJECT_ID}/funding/dossier/export/pdf",
            headers=self.admin_headers,
        )
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response.headers.get("content-type"), "application/pdf")
        self.assertEqual(pdf_response.content[:8], b"%PDF-1.7")

        persist = self.client.post(
            f"/api/projects/{PROJECT_ID}/funding/dossier/export/pdf/persist",
            headers=self.admin_headers,
        )
        self.assertEqual(persist.status_code, 201)
        persist_json = persist.json()
        self.assertEqual(persist_json["format_type"], "FUNDING_DOSSIER_PDF")
        self.assertEqual(persist_json["status"], "ready")
        self.assertIn("manifest_summary", persist_json["delivery_payload"])
        self.assertEqual(
            persist_json["delivery_payload"]["manifest_summary"]["project_id"],
            PROJECT_ID,
        )

        deliverable_id = persist_json["id"]
        listed = self.client.get(
            f"/api/delivery/projects/{PROJECT_ID}/deliverables?format_type=FUNDING_DOSSIER_PDF",
            headers=self.admin_headers,
        )
        self.assertEqual(listed.status_code, 200)
        listed_json = listed.json()
        self.assertTrue(any(item["id"] == deliverable_id for item in listed_json["deliverables"]))

        downloaded = self.client.get(
            f"/api/delivery/deliverables/{deliverable_id}/download",
            headers=self.admin_headers,
        )
        self.assertEqual(downloaded.status_code, 200)
        self.assertEqual(downloaded.headers.get("content-type"), "application/pdf")
        self.assertEqual(downloaded.content[:8], b"%PDF-1.7")

        denied_json = self.client.get(
            f"/api/projects/{PROJECT_ID}/funding/dossier",
            headers=self.tenant_b_headers,
        )
        denied_pdf = self.client.get(
            f"/api/projects/{PROJECT_ID}/funding/dossier/export/pdf",
            headers=self.tenant_b_headers,
        )
        denied_persist = self.client.post(
            f"/api/projects/{PROJECT_ID}/funding/dossier/export/pdf/persist",
            headers=self.tenant_b_headers,
        )
        denied_download = self.client.get(
            f"/api/delivery/deliverables/{deliverable_id}/download",
            headers=self.tenant_b_headers,
        )
        self.assertEqual(denied_json.status_code, 403)
        self.assertEqual(denied_pdf.status_code, 403)
        self.assertEqual(denied_persist.status_code, 403)
        self.assertEqual(denied_download.status_code, 404)


if __name__ == "__main__":
    unittest.main()
