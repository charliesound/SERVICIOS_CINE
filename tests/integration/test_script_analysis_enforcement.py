from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

TEST_DB_PATH = Path("/tmp/test_script_analysis_enforcement.db")
TEST_STORAGE_ROOT = Path("/tmp/test_script_analysis_enforcement_storage")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
if TEST_STORAGE_ROOT.exists():
    shutil.rmtree(TEST_STORAGE_ROOT)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
os.environ["USE_ALEMBIC"] = "0"
os.environ["PROJECT_DOCUMENT_STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)
os.environ["APP_ENV"] = "development"
os.environ["AUTH_SECRET_KEY"] = "script-enforcement-auth-secret-2026-very-strong"
os.environ["APP_SECRET_KEY"] = "script-enforcement-app-secret-2026-very-strong"
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

from fastapi.testclient import TestClient

from app import app
import models  # noqa: F401
from database import Base, engine
from routes.auth_routes import create_access_token
from services.module_catalog_service import ModuleAccessState


ORG_ID = "org-enforcement-0000001"
USER_ID = "user-enforcement-0000001"
USER_ID_NON_ADMIN = "user-enforcement-nonadmin-0000001"
PROJECT_ID = "project-enforcement-0000001"


def _auth_headers(user_id: str, email: str, roles: list[str] | None = None) -> dict[str, str]:
    token = create_access_token({
        "sub": user_id,
        "email": email,
        "organization_id": ORG_ID,
        "roles": roles or ["admin"],
        "scopes": ["projects:read", "projects:write"],
    })
    return {"Authorization": f"Bearer {token}"}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }


def _insert_row(
    connection: sqlite3.Connection,
    table_name: str,
    payload: dict[str, object],
) -> None:
    available_columns = _table_columns(connection, table_name)
    hydrated_payload = dict(payload)
    timestamp = "2026-05-05 00:00:00"
    if "created_at" in available_columns and "created_at" not in hydrated_payload:
        hydrated_payload["created_at"] = timestamp
    if "updated_at" in available_columns and "updated_at" not in hydrated_payload:
        hydrated_payload["updated_at"] = timestamp
    columns = [column for column in hydrated_payload if column in available_columns]
    placeholders = ", ".join("?" for _ in columns)
    values = [hydrated_payload[column] for column in columns]
    connection.execute(f"DELETE FROM {table_name} WHERE id = ?", (payload["id"],))
    connection.execute(
        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )


def _seed_test_data() -> None:
    connection = sqlite3.connect(str(TEST_DB_PATH))
    try:
        _insert_row(
            connection,
            "organizations",
            {
                "id": ORG_ID,
                "name": "Enforcement Test Org",
                "billing_plan": "demo",
                "is_active": 1,
            },
        )
        _insert_row(
            connection,
            "users",
            {
                "id": USER_ID,
                "organization_id": ORG_ID,
                "username": "enforcement_admin",
                "email": "enforcement@example.com",
                "hashed_password": "unused",
                "full_name": "Enforcement Admin",
                "role": "ADMIN",
                "is_active": 1,
                "billing_plan": "demo",
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
                "id": USER_ID_NON_ADMIN,
                "organization_id": ORG_ID,
                "username": "enforcement_user",
                "email": "enforcement-nonadmin@example.com",
                "hashed_password": "unused",
                "full_name": "Enforcement User",
                "role": "USER",
                "is_active": 1,
                "billing_plan": "free",
                "program": "free",
                "signup_type": "seed",
                "account_status": "active",
                "access_level": "user",
                "cid_enabled": 1,
                "onboarding_completed": 1,
            },
        )
        _insert_row(
            connection,
            "projects",
            {
                "id": PROJECT_ID,
                "organization_id": ORG_ID,
                "name": "Enforcement Test Project",
                "description": "Proyecto para test de enforcement",
                "status": "development",
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class ScriptAnalysisEnforcementIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.headers = _auth_headers(USER_ID, "enforcement@example.com")
        cls.non_admin_headers = _auth_headers(
            USER_ID_NON_ADMIN, "enforcement-nonadmin@example.com", roles=["user"],
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    # --- Protected endpoints ---

    def test_intake_script_with_valid_plan_returns_200(self) -> None:
        response = self.client.post(
            f"/api/projects/{PROJECT_ID}/intake/script",
            json={"script_text": "1 INT. COCINA. DIA.\n\nAccion."},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_id"], PROJECT_ID)

    def test_analysis_summary_with_valid_plan_returns_200(self) -> None:
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/analysis/summary",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_put_script_with_valid_plan_returns_200(self) -> None:
        response = self.client.put(
            f"/api/projects/{PROJECT_ID}/script",
            json={"script_text": "1 INT. SALA. NOCHE.\n\nDialogo."},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], PROJECT_ID)

    # --- Enforcement 403 ---

    def test_protected_endpoint_without_module_access_returns_403(self) -> None:
        target = (
            "dependencies.module_access.module_catalog_service.get_module_access_state"
        )
        with patch(target) as mock_get:
            mock_get.return_value = ModuleAccessState(
                enabled=False,
                locked_reason="plan_feature_missing",
            )
            response = self.client.post(
                f"/api/projects/{PROJECT_ID}/intake/script",
                json={"script_text": "1 INT. PLAYA. DIA.\n\nSol."},
                headers=self.non_admin_headers,
            )
        self.assertEqual(response.status_code, 403)

    # --- Unprotected endpoints ---

    def test_intake_idea_unprotected_returns_200(self) -> None:
        response = self.client.post(
            "/api/projects/intake/idea",
            json={
                "title": "Idea sin analisis",
                "logline": "Una historia de prueba.",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("project_id", data)

    def test_ollama_status_unprotected_returns_200(self) -> None:
        response = self.client.get("/api/ops/ollama/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ollama_available", data)


if __name__ == "__main__":
    unittest.main()
