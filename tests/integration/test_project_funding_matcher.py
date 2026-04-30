from __future__ import annotations

import json
import os
import sqlite3
import sys
import asyncio
import unittest
from pathlib import Path


TEST_DB_PATH = Path("/tmp/test_project_funding_matcher.db")
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


ORG_A = "org-a-funding-matcher-000000000001"
ORG_B = "org-b-funding-matcher-000000000001"
ADMIN_A = "admin-a-funding-matcher-000000001"
USER_B = "user-b-funding-matcher-00000000001"
PROJECT_SPAIN = "project-spain-funding-match-0001"
PROJECT_COLLAB = "project-collab-funding-match-001"
PROJECT_BLOCKED = "project-blocked-funding-match-01"
PROJECT_TENANT_B = "project-tenant-b-funding-match1"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _insert_row(connection: sqlite3.Connection, table_name: str, payload: dict[str, object]) -> None:
    available_columns = _table_columns(connection, table_name)
    hydrated_payload = dict(payload)
    timestamp = "2026-04-22 00:00:00"
    if "created_at" in available_columns and "created_at" not in hydrated_payload:
        hydrated_payload["created_at"] = timestamp
    if "updated_at" in available_columns and "updated_at" not in hydrated_payload:
        hydrated_payload["updated_at"] = timestamp
    columns = [column for column in hydrated_payload if column in available_columns]
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(columns)
    values = [hydrated_payload[column] for column in columns]
    connection.execute(f"DELETE FROM {table_name} WHERE id = ?", (payload["id"],))
    connection.execute(
        f"INSERT INTO {table_name} ({quoted_columns}) VALUES ({placeholders})",
        values,
    )


def _seed_test_data() -> None:
    connection = sqlite3.connect(str(TEST_DB_PATH))
    try:
        _insert_row(
            connection,
            "organizations",
            {"id": ORG_A, "name": "Funding Matcher Org A", "billing_plan": "free", "is_active": 1},
        )
        _insert_row(
            connection,
            "organizations",
            {"id": ORG_B, "name": "Funding Matcher Org B", "billing_plan": "free", "is_active": 1},
        )

        _insert_row(
            connection,
            "users",
            {
                "id": ADMIN_A,
                "organization_id": ORG_A,
                "username": "matcher_admin_a",
                "email": "matcher_admin_a@example.com",
                "hashed_password": "not_used",
                "full_name": "Matcher Admin A",
                "role": "ADMIN",
                "is_active": 1,
                "billing_plan": "free",
                "program": "demo",
                "signup_type": "seed",
                "account_status": "active",
                "access_level": "admin",
                "cid_enabled": 1,
                "onboarding_completed": 1,
                "country": "Spain",
            },
        )
        _insert_row(
            connection,
            "users",
            {
                "id": USER_B,
                "organization_id": ORG_B,
                "username": "matcher_user_b",
                "email": "matcher_user_b@example.com",
                "hashed_password": "not_used",
                "full_name": "Matcher User B",
                "role": "PRODUCER",
                "is_active": 1,
                "billing_plan": "free",
                "program": "demo",
                "signup_type": "seed",
                "account_status": "active",
                "access_level": "standard",
                "cid_enabled": 1,
                "onboarding_completed": 1,
                "country": "France",
            },
        )

        projects = [
            {
                "id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "name": "La Ruta del Barrio",
                "description": "Largometraje dramatico ambientado en Madrid para productor independiente espanol.",
                "status": "development",
                "script_text": "Largometraje espanol sobre una familia en Madrid. Proyecto de Espana con potencial documental y ficcion.",
            },
            {
                "id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "name": "Puentes Abiertos",
                "description": "Coproduccion entre Espana, Francia y Colombia en fase de production.",
                "status": "production",
                "script_text": "Feature film de coproduccion entre Espana, Francia y Colombia con estrategia europea e iberoamericana.",
            },
            {
                "id": PROJECT_BLOCKED,
                "organization_id": ORG_A,
                "name": "Signal Drift",
                "description": "Series experimental en distribution sin paquete financiero cerrado.",
                "status": "distribution",
                "script_text": "Series experimental de ciencia ficcion sin coproduccion ni presupuesto confirmado.",
            },
            {
                "id": PROJECT_TENANT_B,
                "organization_id": ORG_B,
                "name": "Tenant B Secret",
                "description": "Proyecto privado de otro tenant.",
                "status": "development",
                "script_text": "Proyecto con menciones muy fuertes a ICAA, Eurimages e Ibermedia que no debe filtrarse.",
            },
        ]
        for project in projects:
            _insert_row(connection, "projects", project)

        breakdowns = [
            {
                "id": "breakdown-spain-funding-match01",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "script_text": projects[0]["script_text"],
                "breakdown_json": json.dumps(
                    {
                        "metadata": {"total_scenes": 22, "total_characters": 10, "total_locations": 8},
                        "department_breakdown": {"production": {"count": 4}, "cast": {"count": 10}},
                    },
                    ensure_ascii=True,
                ),
                "budget_estimate": 250000.0,
                "status": "completed",
            },
            {
                "id": "breakdown-collab-funding-match1",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "script_text": projects[1]["script_text"],
                "breakdown_json": json.dumps(
                    {
                        "metadata": {"total_scenes": 40, "total_characters": 16, "total_locations": 12},
                        "department_breakdown": {"production": {"count": 7}, "travel": {"count": 3}},
                    },
                    ensure_ascii=True,
                ),
                "budget_estimate": 900000.0,
                "status": "completed",
            },
            {
                "id": "breakdown-blocked-funding-match",
                "project_id": PROJECT_BLOCKED,
                "organization_id": ORG_A,
                "script_text": projects[2]["script_text"],
                "breakdown_json": json.dumps(
                    {
                        "metadata": {"total_scenes": 8, "total_characters": 4, "total_locations": 3},
                        "department_breakdown": {"postproduction": {"count": 2}},
                    },
                    ensure_ascii=True,
                ),
                "budget_estimate": 0.0,
                "status": "completed",
            },
        ]
        for breakdown in breakdowns:
            _insert_row(connection, "production_breakdowns", breakdown)

        budgets = [
            {
                "id": "budget-spain-funding-match-0001",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "scenario_type": "standard",
                "grand_total": 250000.0,
                "status": "draft",
            },
            {
                "id": "budget-collab-funding-match-001",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "scenario_type": "premium",
                "grand_total": 900000.0,
                "status": "draft",
            },
        ]
        for budget in budgets:
            _insert_row(connection, "project_budgets", budget)

        project_sources = [
            {
                "id": "private-spain-secured-000000001",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "source_name": "Angel Investor Madrid",
                "source_type": "private_investor",
                "amount": 50000.0,
                "currency": "EUR",
                "status": "secured",
                "notes": "Seed capital",
            },
            {
                "id": "private-collab-secured-00000001",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "source_name": "Copro Lead Spain",
                "source_type": "equity",
                "amount": 100000.0,
                "currency": "EUR",
                "status": "secured",
                "notes": "Lead producer commitment",
            },
            {
                "id": "private-collab-negotiating-0001",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "source_name": "French Broadcaster",
                "source_type": "pre_sale",
                "amount": 150000.0,
                "currency": "EUR",
                "status": "negotiating",
                "notes": "Soft circle",
            },
        ]
        for project_source in project_sources:
            _insert_row(connection, "project_funding_sources", project_source)

        project_documents = [
            {
                "id": "doc-spain-treatment-00000001",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "treatment",
                "upload_status": "completed",
                "file_name": "la_ruta_treatment.txt",
                "mime_type": "text/plain",
                "file_size": 1200,
                "storage_path": "/tmp/la_ruta_treatment.txt",
                "checksum": "spain-treatment-checksum",
                "extracted_text": "Treatment for La Ruta del Barrio. Spanish independent producer based in Madrid. The project targets ICAA support with a Spanish cultural focus and a completed creative dossier.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-spain-budget-000000001",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "budget",
                "upload_status": "completed",
                "file_name": "la_ruta_budget.txt",
                "mime_type": "text/plain",
                "file_size": 1300,
                "storage_path": "/tmp/la_ruta_budget.txt",
                "checksum": "spain-budget-checksum",
                "extracted_text": "Budget breakdown in EUR for La Ruta del Barrio. Total budget 250000 EUR. Producer contribution 50000 EUR. Application package includes budget, financing plan, and treatment for ICAA.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-spain-finance-0000001",
                "project_id": PROJECT_SPAIN,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "finance_plan",
                "upload_status": "completed",
                "file_name": "la_ruta_finance_plan.txt",
                "mime_type": "text/plain",
                "file_size": 1500,
                "storage_path": "/tmp/la_ruta_finance_plan.txt",
                "checksum": "spain-finance-checksum",
                "extracted_text": "Financing plan for La Ruta del Barrio with ICAA as the main Spanish institutional target, private investor seed capital, and regional support from Madrid.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-collab-contract-000001",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "contract",
                "upload_status": "completed",
                "file_name": "puentes_coproduction_agreement.txt",
                "mime_type": "text/plain",
                "file_size": 1800,
                "storage_path": "/tmp/puentes_coproduction_agreement.txt",
                "checksum": "collab-contract-checksum",
                "extracted_text": "Coproduction agreement between producers from Spain, France, and Colombia. The lead producer coordinates the Eurimages application and confirms collaborative financing responsibilities.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-collab-finance-000001",
                "project_id": PROJECT_COLLAB,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "finance_plan",
                "upload_status": "completed",
                "file_name": "puentes_finance_plan.txt",
                "mime_type": "text/plain",
                "file_size": 1800,
                "storage_path": "/tmp/puentes_finance_plan.txt",
                "checksum": "collab-finance-checksum",
                "extracted_text": "Finance plan for Puentes Abiertos with Eurimages and Ibermedia as priority calls. Confirmed partner territories are Spain, France, and Colombia with a shared production calendar.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-blocked-note-00000001",
                "project_id": PROJECT_BLOCKED,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "other",
                "upload_status": "completed",
                "file_name": "signal_drift_note.txt",
                "mime_type": "text/plain",
                "file_size": 600,
                "storage_path": "/tmp/signal_drift_note.txt",
                "checksum": "blocked-note-checksum",
                "extracted_text": "Loose creative note without budget, financing plan, contracts, or applicant documentation.",
                "visibility_scope": "project",
            },
            {
                "id": "doc-tenant-b-secret-000001",
                "project_id": PROJECT_TENANT_B,
                "organization_id": ORG_B,
                "uploaded_by_user_id": USER_B,
                "document_type": "finance_plan",
                "upload_status": "completed",
                "file_name": "tenant_b_secret_finance.txt",
                "mime_type": "text/plain",
                "file_size": 900,
                "storage_path": "/tmp/tenant_b_secret_finance.txt",
                "checksum": "tenant-b-secret-checksum",
                "extracted_text": "This tenant B financing plan mentions ICAA, Eurimages, Ibermedia, Spain, France, and Colombia in one place. It must never appear in tenant A evidence.",
                "visibility_scope": "project",
            },
        ]
        for document in project_documents:
            _insert_row(connection, "project_documents", document)

        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class ProjectFundingMatcherIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "matcher_admin_a@example.com")
        cls.tenant_b_headers = _auth_headers(USER_B, "matcher_user_b@example.com")
        _seed_test_data()
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

    def test_project_funding_matcher_es_eu_latam(self) -> None:
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)

        reindex_spain = self.client.post(
            f"/api/projects/{PROJECT_SPAIN}/documents/reindex",
            headers=self.admin_headers,
        )
        reindex_collab = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/documents/reindex",
            headers=self.admin_headers,
        )
        reindex_blocked = self.client.post(
            f"/api/projects/{PROJECT_BLOCKED}/documents/reindex",
            headers=self.admin_headers,
        )
        self.assertEqual(reindex_spain.status_code, 200)
        self.assertEqual(reindex_collab.status_code, 200)
        self.assertEqual(reindex_blocked.status_code, 200)
        self.assertGreaterEqual(reindex_spain.json()["processed_chunks"], 1)
        self.assertGreaterEqual(reindex_collab.json()["processed_chunks"], 1)

        public_catalog = self.client.get("/api/funding/opportunities")
        self.assertEqual(public_catalog.status_code, 200)
        self.assertGreaterEqual(public_catalog.json()["count"], 5)

        budget_view = self.client.get(
            f"/api/projects/{PROJECT_SPAIN}/budget",
            headers=self.admin_headers,
        )
        self.assertEqual(budget_view.status_code, 200)
        self.assertEqual(budget_view.json()["grand_total"], 250000.0)

        profile = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/profile",
            headers=self.admin_headers,
        )
        self.assertEqual(profile.status_code, 200)
        profile_json = profile.json()
        self.assertEqual(profile_json["phase"], "production")
        self.assertIn("France", profile_json["countries_involved"])
        self.assertIn("Colombia", profile_json["countries_involved"])
        self.assertGreater(profile_json["funding_gap"], 0)

        spain_recompute = self.client.post(
            f"/api/projects/{PROJECT_SPAIN}/funding/recompute",
            headers=self.admin_headers,
        )
        self.assertEqual(spain_recompute.status_code, 200)
        spain_matches = spain_recompute.json()["matches"]
        self.assertGreaterEqual(len(spain_matches), 5)
        spain_codes = {match["source_code"]: match for match in spain_matches}
        self.assertIn("ICAA", spain_codes)
        self.assertIn(spain_codes["ICAA"]["fit_level"], {"high", "medium"})
        self.assertGreaterEqual(spain_codes["ICAA"]["match_score"], 55)

        collab_recompute = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute",
            headers=self.admin_headers,
        )
        self.assertEqual(collab_recompute.status_code, 200)
        collab_matches = collab_recompute.json()["matches"]
        collab_codes = {match["source_code"]: match for match in collab_matches}
        self.assertIn(collab_codes["EURIMAGES"]["fit_level"], {"high", "medium"})
        self.assertIn(collab_codes["IBERMEDIA"]["fit_level"], {"high", "medium"})
        self.assertGreaterEqual(collab_codes["EURIMAGES"]["match_score"], 55)
        self.assertGreaterEqual(collab_codes["IBERMEDIA"]["match_score"], 50)

        blocked_recompute = self.client.post(
            f"/api/projects/{PROJECT_BLOCKED}/funding/recompute",
            headers=self.admin_headers,
        )
        self.assertEqual(blocked_recompute.status_code, 200)
        blocked_matches = blocked_recompute.json()["matches"]
        self.assertTrue(any(match["fit_level"] == "blocked" for match in blocked_matches))
        blocked_icaa = next(match for match in blocked_matches if match["source_code"] == "ICAA")
        self.assertIn(blocked_icaa["fit_level"], {"blocked", "low"})
        self.assertTrue(blocked_icaa["blocking_reasons_json"])
        self.assertIn("Budget not generated yet", blocked_icaa["blocking_reasons_json"])

        checklist = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/checklist",
            headers=self.admin_headers,
        )
        self.assertEqual(checklist.status_code, 200)
        checklist_json = checklist.json()
        self.assertGreaterEqual(checklist_json["high_matches"] + checklist_json["medium_matches"], 2)
        self.assertTrue(checklist_json["priority_actions"])

        matches_view = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches",
            headers=self.admin_headers,
        )
        self.assertEqual(matches_view.status_code, 200)
        self.assertEqual(matches_view.json()["count"], len(collab_matches))

        second_recompute = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute",
            headers=self.admin_headers,
        )
        self.assertEqual(second_recompute.status_code, 200)
        with sqlite3.connect(str(TEST_DB_PATH)) as connection:
            persisted_count = connection.execute(
                "SELECT COUNT(*) FROM project_funding_matches WHERE project_id = ? AND organization_id = ?",
                (PROJECT_COLLAB, ORG_A),
            ).fetchone()[0]
        self.assertEqual(persisted_count, len(collab_matches))

        tenant_b_denied_recompute = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute",
            headers=self.tenant_b_headers,
        )
        tenant_b_denied_matches = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches",
            headers=self.tenant_b_headers,
        )
        self.assertEqual(tenant_b_denied_recompute.status_code, 403)
        self.assertEqual(tenant_b_denied_matches.status_code, 403)

        rag_spain = self.client.post(
            f"/api/projects/{PROJECT_SPAIN}/funding/recompute-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_spain.status_code, 202)
        rag_spain_status = self.client.get(
            f"/api/projects/{PROJECT_SPAIN}/funding/matcher-status",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_spain_status.status_code, 200)
        self.assertEqual(rag_spain_status.json()["job"]["status"], "completed")

        rag_spain_matches_response = self.client.get(
            f"/api/projects/{PROJECT_SPAIN}/funding/matches-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_spain_matches_response.status_code, 200)
        rag_spain_matches = rag_spain_matches_response.json()["matches"]
        rag_spain_codes = {match["source_code"]: match for match in rag_spain_matches}
        self.assertIn("ICAA", rag_spain_codes)
        self.assertGreaterEqual(rag_spain_codes["ICAA"]["match_score"], spain_codes["ICAA"]["match_score"])
        self.assertTrue(rag_spain_codes["ICAA"]["evidence_chunks_json"]["retrieved_chunks"])
        self.assertTrue(rag_spain_codes["ICAA"]["rag_rationale"])
        self.assertEqual(rag_spain_codes["ICAA"]["matcher_mode"], "rag_enriched")

        rag_collab = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_collab.status_code, 202)
        rag_collab_matches_response = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_collab_matches_response.status_code, 200)
        rag_collab_matches = rag_collab_matches_response.json()["matches"]
        rag_collab_codes = {match["source_code"]: match for match in rag_collab_matches}
        self.assertGreaterEqual(rag_collab_codes["EURIMAGES"]["match_score"], collab_codes["EURIMAGES"]["match_score"])
        self.assertGreaterEqual(rag_collab_codes["IBERMEDIA"]["match_score"], collab_codes["IBERMEDIA"]["match_score"])
        self.assertTrue(rag_collab_codes["EURIMAGES"]["evidence_chunks_json"]["requirement_evaluations"])

        rag_blocked = self.client.post(
            f"/api/projects/{PROJECT_BLOCKED}/funding/recompute-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_blocked.status_code, 202)
        rag_blocked_matches_response = self.client.get(
            f"/api/projects/{PROJECT_BLOCKED}/funding/matches-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_blocked_matches_response.status_code, 200)
        rag_blocked_matches = rag_blocked_matches_response.json()["matches"]
        rag_blocked_icaa = next(match for match in rag_blocked_matches if match["source_code"] == "ICAA")
        self.assertTrue(rag_blocked_icaa["rag_missing_requirements"])
        self.assertTrue(rag_blocked_icaa["missing_documents_json"])

        rag_filtered = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches-rag?page=1&size=1&region_scope=europe&sort_by=deadline&sort_dir=asc&q=Eurimages",
            headers=self.admin_headers,
        )
        self.assertEqual(rag_filtered.status_code, 200)
        rag_filtered_json = rag_filtered.json()
        self.assertEqual(rag_filtered_json["page"], 1)
        self.assertEqual(rag_filtered_json["size"], 1)
        self.assertGreaterEqual(rag_filtered_json["total"], 1)
        self.assertEqual(rag_filtered_json["count"], 1)
        self.assertEqual(rag_filtered_json["matches"][0]["source_code"], "EURIMAGES")
        self.assertEqual(rag_filtered_json["matches"][0]["region_scope"], "europe")

        classic_filtered = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches?page=1&size=2&sort_by=fit_level&sort_dir=desc&fit_level=high,medium",
            headers=self.admin_headers,
        )
        self.assertEqual(classic_filtered.status_code, 200)
        classic_filtered_json = classic_filtered.json()
        self.assertEqual(classic_filtered_json["page"], 1)
        self.assertEqual(classic_filtered_json["size"], 2)
        self.assertLessEqual(classic_filtered_json["count"], 2)
        self.assertGreaterEqual(classic_filtered_json["total"], classic_filtered_json["count"])

        eurimages_match_id = rag_collab_codes["EURIMAGES"]["match_id"]
        eurimages_evidence = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches/{eurimages_match_id}/evidence",
            headers=self.admin_headers,
        )
        self.assertEqual(eurimages_evidence.status_code, 200)
        eurimages_evidence_json = eurimages_evidence.json()
        self.assertEqual(eurimages_evidence_json["source_code"], "EURIMAGES")
        self.assertTrue(eurimages_evidence_json["evidence_chunks_json"]["retrieved_chunks"])
        retrieved_file_names = {
            item["file_name"]
            for item in eurimages_evidence_json["evidence_chunks_json"]["retrieved_chunks"]
        }
        self.assertIn("puentes_coproduction_agreement.txt", retrieved_file_names)
        self.assertNotIn("tenant_b_secret_finance.txt", retrieved_file_names)

        tenant_b_denied_rag_recompute = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute-rag",
            headers=self.tenant_b_headers,
        )
        tenant_b_denied_rag_matches = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/matches-rag",
            headers=self.tenant_b_headers,
        )
        self.assertEqual(tenant_b_denied_rag_recompute.status_code, 403)
        self.assertEqual(tenant_b_denied_rag_matches.status_code, 403)

        second_rag_collab = self.client.post(
            f"/api/projects/{PROJECT_COLLAB}/funding/recompute-rag",
            headers=self.admin_headers,
        )
        self.assertEqual(second_rag_collab.status_code, 202)
        with sqlite3.connect(str(TEST_DB_PATH)) as connection:
            rag_persisted_count = connection.execute(
                "SELECT COUNT(*) FROM project_funding_matches WHERE project_id = ? AND organization_id = ? AND matcher_mode = ?",
                (PROJECT_COLLAB, ORG_A, "rag_enriched"),
            ).fetchone()[0]
        self.assertEqual(rag_persisted_count, len(rag_collab_matches))

        dossier_after_rag = self.client.get(
            f"/api/projects/{PROJECT_COLLAB}/funding/dossier",
            headers=self.admin_headers,
        )
        self.assertEqual(dossier_after_rag.status_code, 200)
        self.assertGreaterEqual(dossier_after_rag.json()["funding_match_summary"]["matches_count"], 5)


if __name__ == "__main__":
    # Exact venv command:
    # PYTHONPATH=/opt/SERVICIOS_CINE/src /opt/SERVICIOS_CINE/venv/bin/python -m unittest tests.integration.test_project_funding_matcher
    unittest.main()
