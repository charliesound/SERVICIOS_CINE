from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path


TEST_DB_PATH = Path("/tmp/test_project_private_documents.db")
TEST_STORAGE_ROOT = Path("/tmp/test_project_private_documents_storage")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()
if TEST_STORAGE_ROOT.exists():
    shutil.rmtree(TEST_STORAGE_ROOT)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
os.environ["USE_ALEMBIC"] = "0"
os.environ["PROJECT_DOCUMENT_STORAGE_ROOT"] = str(TEST_STORAGE_ROOT)
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

from fastapi.testclient import TestClient

from app import app
import models  # noqa: F401
from database import Base, engine
from routes.auth_routes import create_access_token


ORG_A = "org-a-private-docs-000000000001"
ORG_B = "org-b-private-docs-000000000001"
ADMIN_A = "admin-a-private-docs-000000001"
USER_B = "user-b-private-docs-00000000001"
PROJECT_A = "project-a-private-docs-0000001"


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
        _insert_row(connection, "organizations", {"id": ORG_A, "name": "Private Docs Org A", "billing_plan": "free", "is_active": 1})
        _insert_row(connection, "organizations", {"id": ORG_B, "name": "Private Docs Org B", "billing_plan": "free", "is_active": 1})
        _insert_row(
            connection,
            "users",
            {
                "id": ADMIN_A,
                "organization_id": ORG_A,
                "username": "private_docs_admin_a",
                "email": "private_docs_admin_a@example.com",
                "hashed_password": "unused",
                "full_name": "Private Docs Admin A",
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
                "username": "private_docs_user_b",
                "email": "private_docs_user_b@example.com",
                "hashed_password": "unused",
                "full_name": "Private Docs User B",
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
                "id": PROJECT_A,
                "organization_id": ORG_A,
                "name": "Archivo Interno",
                "description": "Proyecto para documentos privados.",
                "status": "development",
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class ProjectPrivateDocumentsIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "private_docs_admin_a@example.com")
        cls.tenant_b_headers = _auth_headers(USER_B, "private_docs_user_b@example.com")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    def test_project_private_document_upload_flow(self) -> None:
        upload = self.client.post(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
            data={"document_type": "script", "visibility_scope": "project"},
            files={
                "file": (
                    "notes.txt",
                    b"Internal project notes for funding and production planning.",
                    "text/plain",
                )
            },
        )
        self.assertEqual(upload.status_code, 201)
        upload_json = upload.json()
        self.assertEqual(upload_json["document_type"], "script")
        self.assertEqual(upload_json["upload_status"], "completed")
        self.assertIn("Internal project notes", upload_json["extracted_text"])
        self.assertTrue(Path(upload_json["storage_path"]).exists())

        document_id = upload_json["id"]
        stored_file = Path(upload_json["storage_path"])

        listed = self.client.get(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
        )
        self.assertEqual(listed.status_code, 200)
        listed_json = listed.json()
        self.assertEqual(listed_json["count"], 1)
        self.assertEqual(listed_json["documents"][0]["id"], document_id)

        detail = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}",
            headers=self.admin_headers,
        )
        self.assertEqual(detail.status_code, 200)
        detail_json = detail.json()
        self.assertEqual(detail_json["checksum"], upload_json["checksum"])
        self.assertEqual(detail_json["visibility_scope"], "project")

        download = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}/download",
            headers=self.admin_headers,
        )
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.content, b"Internal project notes for funding and production planning.")

        tenant_b_list = self.client.get(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.tenant_b_headers,
        )
        tenant_b_detail = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}",
            headers=self.tenant_b_headers,
        )
        tenant_b_delete = self.client.delete(
            f"/api/projects/{PROJECT_A}/documents/{document_id}",
            headers=self.tenant_b_headers,
        )
        self.assertEqual(tenant_b_list.status_code, 403)
        self.assertEqual(tenant_b_detail.status_code, 403)
        self.assertEqual(tenant_b_delete.status_code, 403)

        deleted = self.client.delete(
            f"/api/projects/{PROJECT_A}/documents/{document_id}",
            headers=self.admin_headers,
        )
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse(stored_file.exists())

        after_delete = self.client.get(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
        )
        self.assertEqual(after_delete.status_code, 200)
        self.assertEqual(after_delete.json()["count"], 0)


if __name__ == "__main__":
    unittest.main()
