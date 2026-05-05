from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path


TEST_DB_PATH = Path("/tmp/test_project_script_analysis_flow.db")
TEST_STORAGE_ROOT = Path("/tmp/test_project_script_analysis_flow_storage")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
if TEST_STORAGE_ROOT.exists():
    shutil.rmtree(TEST_STORAGE_ROOT)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
os.environ["USE_ALEMBIC"] = "0"
os.environ["PROJECT_DOCUMENT_STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)
os.environ["AUTH_SECRET_KEY"] = "script-analysis-flow-auth-secret-2026-very-strong"
os.environ["APP_SECRET_KEY"] = "script-analysis-flow-app-secret-2026-very-strong"
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

from fastapi.testclient import TestClient

from app import app
import models  # noqa: F401
from database import Base, engine
from routes.auth_routes import create_access_token


ORG_ID = "org-script-analysis-flow-0000001"
USER_ID = "user-script-analysis-flow-000001"
PROJECT_ID = "project-script-analysis-flow-001"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
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


def _build_long_script() -> str:
    scene_a = "\n".join(
        [
            "1 INT. COCINA BAR. NOCHE.",
            "MARTA",
            "Respira hondo antes de entrar al turno.",
            "La cafetera vibra mientras la lluvia golpea la persiana.",
            "MARTA mira la caja vacia y anota una deuda en una libreta.",
        ]
    )
    scene_b = "\n".join(
        [
            "2 INT. BAR. NOCHE.",
            "RAUL",
            "Pregunta por la ultima ronda y exige respuestas.",
            "Los clientes escuchan en silencio mientras una botella cae al suelo.",
            "MARTA esconde una llave debajo del mostrador antes de contestar.",
        ]
    )
    body = "\n\n".join([scene_a, scene_b] * 90)
    script_text = "Guión de largometraje\n\n" + body
    assert len(script_text) > 10000
    return script_text


def _seed_test_data() -> None:
    connection = sqlite3.connect(str(TEST_DB_PATH))
    try:
        _insert_row(
            connection,
            "organizations",
            {
                "id": ORG_ID,
                "name": "Script Analysis Org",
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
                "username": "script_analysis_admin",
                "email": "script.analysis@example.com",
                "hashed_password": "unused",
                "full_name": "Script Analysis Admin",
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
                "name": "Guion Largo",
                "description": "Proyecto de regresion para analisis de guion TXT.",
                "status": "development",
                "script_text": _build_long_script(),
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class ProjectScriptAnalysisFlowIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.headers = _auth_headers(USER_ID, "script.analysis@example.com")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    def test_long_txt_script_analysis_persists_summary(self) -> None:
        analyze = self.client.post(
            f"/api/projects/{PROJECT_ID}/analyze",
            headers=self.headers,
        )
        self.assertEqual(analyze.status_code, 200)
        analyze_json = analyze.json()
        self.assertEqual(analyze_json["doc_type"], "script")
        self.assertGreaterEqual(analyze_json["confidence_score"], 0.70)
        self.assertEqual(
            analyze_json["structured_payload"]["analysis_summary"]["status"],
            "completed",
        )
        self.assertGreaterEqual(
            analyze_json["structured_payload"]["analysis_summary"]["scenes_count"],
            2,
        )

        summary = self.client.get(
            f"/api/projects/{PROJECT_ID}/analysis/summary",
            headers=self.headers,
        )
        self.assertEqual(summary.status_code, 200)
        summary_json = summary.json()
        self.assertNotEqual(summary_json.get("status"), "not_found")
        self.assertEqual(summary_json["project_id"], PROJECT_ID)
        self.assertTrue(summary_json["document_id"])
        self.assertEqual(summary_json["doc_type"], "script")
        self.assertEqual(summary_json["source_kind"], "script_text")
        self.assertGreaterEqual(summary_json["confidence_score"], 0.70)
        self.assertIn("structured_payload", summary_json)
        self.assertTrue(summary_json["structured_payload"])
        self.assertIn("summary", summary_json)
        self.assertTrue(summary_json["summary"])
        self.assertGreaterEqual(summary_json["scenes_count"], 2)
        self.assertGreater(summary_json["sequences_count"], 0)


if __name__ == "__main__":
    unittest.main()
