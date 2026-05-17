from __future__ import annotations

import asyncio
import json
import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path

TEST_DB_PATH = Path("/tmp/test_breakdown_export.db")
TEST_STORAGE_ROOT = Path("/tmp/test_breakdown_export_storage")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
if TEST_STORAGE_ROOT.exists():
    shutil.rmtree(TEST_STORAGE_ROOT)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
os.environ["USE_ALEMBIC"] = "0"
os.environ["PROJECT_DOCUMENT_STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)
os.environ["AUTH_SECRET_KEY"] = "script-export-auth-secret-2026-very-strong"
os.environ["APP_SECRET_KEY"] = "script-export-app-secret-2026-very-strong"
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

from fastapi.testclient import TestClient

from app import app
import models  # noqa: F401
from database import Base, engine
from routes.auth_routes import create_access_token


ORG_ID = "org-export-0000001"
USER_ID = "user-export-0000001"
PROJECT_ID = "project-export-0000001"
BREAKDOWN_ID = "breakdown-export-0000001"

SAMPLE_SCRIPT = (
    "1 INT. COCINA. NOCHE.\n"
    "MARTA\n"
    "Respira hondo antes de entrar al turno.\n"
    "La cafetera vibra mientras la lluvia golpea la persiana.\n"
    "2 INT. BAR. NOCHE.\n"
    "RAUL\n"
    "Pregunta por la ultima ronda.\n"
    "MARTA esconde una llave debajo del mostrador.\n"
)

SAMPLE_BREAKDOWN_JSON = {
    "project_id": PROJECT_ID,
    "organization_id": ORG_ID,
    "status": "completed",
    "document": {"document_id": "doc-001", "doc_type": "script", "confidence_score": 0.85},
    "structured_payload": {},
    "summary": {"total_scenes": 2, "total_characters": 2, "total_locations": 2},
    "tone": "tenso_suspense",
    "llm_summary": "Drama nocturno con dos personajes en situacion de tension.",
    "production_needs": ["casting: MARTA, RAUL"],
    "storyboard_suggestions": ["Close-ups de miradas"],
    "analysis_engine": "heuristic",
    "scenes": [
        {
            "scene_number": 1,
            "heading": "1 INT. COCINA. NOCHE.",
            "location": "COCINA",
            "int_ext": "INT",
            "time_of_day": "NOCHE",
            "characters_detected": ["MARTA"],
            "action_blocks": ["Respira hondo antes de entrar al turno."],
            "dialogue_blocks": [],
        },
        {
            "scene_number": 2,
            "heading": "2 INT. BAR. NOCHE.",
            "location": "BAR",
            "int_ext": "INT",
            "time_of_day": "NOCHE",
            "characters_detected": ["RAUL", "MARTA"],
            "action_blocks": ["Pregunta por la ultima ronda."],
            "dialogue_blocks": [
                {"character": "RAUL", "text": "Pregunta por la ultima ronda."},
            ],
        },
    ],
    "breakdowns": [
        {
            "scene_id": "scene_001",
            "heading": "1 INT. COCINA. NOCHE.",
            "int_ext": "INT",
            "location": "COCINA",
            "time_of_day": "NOCHE",
            "characters": ["MARTA"],
            "props_detected": ["cafetera", "llave"],
            "dialogue_count": 0,
            "action_lines": 1,
        },
        {
            "scene_id": "scene_002",
            "heading": "2 INT. BAR. NOCHE.",
            "int_ext": "INT",
            "location": "BAR",
            "time_of_day": "NOCHE",
            "characters": ["RAUL", "MARTA"],
            "props_detected": ["mostrador"],
            "dialogue_count": 1,
            "action_lines": 1,
        },
    ],
    "department_breakdown": {
        "summary": {"total_scenes": 2, "total_characters": 2, "total_locations": 2},
        "departments": {
            "direccion": {"notes": "Dirigir 2 escenas, 2 personajes", "flags": []},
            "produccion": {"notes": "Producir 2 escenas", "flags": []},
            "cast": {"characters": ["MARTA", "RAUL"], "estimated_cast": 2},
            "postproduccion": {"notes": "Edición de 2 escenas", "complexity": "low"},
        },
    },
    "sequences": [
        {
            "sequence_id": "seq_01",
            "sequence_number": 1,
            "title": "COCINA",
            "summary": "1 INT. COCINA. NOCHE.; 2 INT. BAR. NOCHE.",
            "included_scenes": [1, 2],
            "characters": ["MARTA", "RAUL"],
            "location": "COCINA",
        },
    ],
    "metadata": {
        "total_scenes": 2,
        "total_characters": 2,
        "total_locations": 2,
        "analysis_engine": "heuristic",
    },
}


def _auth_headers(user_id: str, email: str, role: str = "admin", program: str = "demo") -> dict[str, str]:
    token = create_access_token({
        "sub": user_id,
        "email": email,
        "organization_id": ORG_ID,
        "roles": [role],
        "scopes": ["projects:read", "projects:write"],
        "program": program
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
                "name": "Export Test Org",
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
                "username": "export_admin",
                "email": "export@example.com",
                "hashed_password": "unused",
                "full_name": "Export Admin",
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
            "projects",
            {
                "id": PROJECT_ID,
                "organization_id": ORG_ID,
                "name": "Export Test Project",
                "description": "Proyecto para test de export",
                "status": "development",
                "script_text": SAMPLE_SCRIPT,
            },
        )
        _insert_row(
            connection,
            "production_breakdowns",
            {
                "id": BREAKDOWN_ID,
                "project_id": PROJECT_ID,
                "organization_id": ORG_ID,
                "script_text": SAMPLE_SCRIPT[:200],
                "breakdown_json": json.dumps(SAMPLE_BREAKDOWN_JSON, ensure_ascii=False),
                "status": "completed",
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class BreakdownExportIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.headers = _auth_headers(USER_ID, "export@example.com", "admin", "demo")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    # --- Export JSON ---

    def test_export_json_returns_200_with_structure(self) -> None:
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/breakdown/export?format=json",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "application/json")
        disp = response.headers.get("content-disposition", "")
        self.assertIn("CID_breakdown_", disp)
        self.assertIn(".json", disp)

        data = response.json()
        self.assertEqual(data["project_id"], PROJECT_ID)
        self.assertEqual(data["export_version"], "1.0")
        self.assertEqual(data["source"], "cid_breakdown")
        self.assertIn("characters", data)
        self.assertIn("locations", data)
        self.assertIn("props", data)
        self.assertIn("scenes", data)
        self.assertIn("breakdowns", data)
        self.assertIn("departments", data)
        self.assertIn("generated_at", data)
        self.assertIn("MARTA", data["characters"])

    # --- Export Markdown ---

    def test_export_md_returns_200_with_content(self) -> None:
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/breakdown/export?format=md",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/markdown", response.headers.get("content-type", ""))
        disp = response.headers.get("content-disposition", "")
        self.assertIn("CID_breakdown_", disp)
        self.assertIn(".md", disp)
        body = response.text
        self.assertIn("CID Breakdown", body)
        self.assertIn("Characters", body)
        self.assertIn("Scenes", body)
        self.assertIn("Props", body)

    # --- Export CSV ---

    def test_export_csv_returns_200_with_content(self) -> None:
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/breakdown/export?format=csv",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers.get("content-type", ""))
        disp = response.headers.get("content-disposition", "")
        self.assertIn("CID_breakdown_", disp)
        self.assertIn(".csv", disp)
        body = response.text
        self.assertIn("Scene ID", body)
        self.assertIn("Heading", body)
        self.assertIn("MARTA", body)

    # --- Error cases ---

    def test_export_invalid_format_returns_422(self) -> None:
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/breakdown/export?format=pdf",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 422)

    def test_export_nonexistent_project_returns_404(self) -> None:
        response = self.client.get(
            "/api/projects/nonexistent-project/breakdown/export?format=json",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_export_module_access_blocked_403(self) -> None:
        # User without access to "breakdown" module via plan
        headers = _auth_headers(USER_ID, "export@example.com", "user", "none")
        response = self.client.get(
            f"/api/projects/{PROJECT_ID}/breakdown/export?format=json",
            headers=headers,
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("MODULE_ACCESS_BLOCKED", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
