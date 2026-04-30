from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path


TEST_DB_PATH = Path("/tmp/test_project_document_rag.db")
TEST_STORAGE_ROOT = Path("/tmp/test_project_document_rag_storage")
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


ORG_A = "org-a-document-rag-000000000001"
ORG_B = "org-b-document-rag-000000000001"
ADMIN_A = "admin-a-document-rag-000000001"
USER_B = "user-b-document-rag-00000000001"
PROJECT_A = "project-a-document-rag-0000001"


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
        _insert_row(connection, "organizations", {"id": ORG_A, "name": "Document RAG Org A", "billing_plan": "free", "is_active": 1})
        _insert_row(connection, "organizations", {"id": ORG_B, "name": "Document RAG Org B", "billing_plan": "free", "is_active": 1})
        _insert_row(
            connection,
            "users",
            {
                "id": ADMIN_A,
                "organization_id": ORG_A,
                "username": "document_rag_admin_a",
                "email": "document_rag_admin_a@example.com",
                "hashed_password": "unused",
                "full_name": "Document Rag Admin A",
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
                "username": "document_rag_user_b",
                "email": "document_rag_user_b@example.com",
                "hashed_password": "unused",
                "full_name": "Document Rag User B",
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
                "name": "RAG Interno",
                "description": "Proyecto para retrieval documental.",
                "status": "development",
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class ProjectDocumentRagIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "document_rag_admin_a@example.com")
        cls.tenant_b_headers = _auth_headers(USER_B, "document_rag_user_b@example.com")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    def test_project_document_rag_reindex_chunks_and_ask(self) -> None:
        upload = self.client.post(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
            data={"document_type": "finance_plan", "visibility_scope": "project"},
            files={
                "file": (
                    "finance.txt",
                    b"The finance plan includes regional grants, equity investors, and a phased production budget. The producer expects support from Spain and Europe.",
                    "text/plain",
                )
            },
        )
        self.assertEqual(upload.status_code, 201)
        document_id = upload.json()["id"]

        chunks = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}/chunks",
            headers=self.admin_headers,
        )
        self.assertEqual(chunks.status_code, 200)
        chunks_json = chunks.json()
        self.assertGreaterEqual(chunks_json["count"], 1)
        self.assertIn("finance_plan", chunks_json["chunks"][0]["metadata_json"]["document_type"])

        reindex = self.client.post(
            f"/api/projects/{PROJECT_A}/documents/reindex",
            headers=self.admin_headers,
            json={"document_id": document_id},
        )
        self.assertEqual(reindex.status_code, 200)
        reindex_json = reindex.json()
        self.assertEqual(reindex_json["processed_documents"], 1)
        self.assertGreaterEqual(reindex_json["processed_chunks"], 1)
        self.assertEqual(reindex_json["embedding_provider"], "local_hash")

        ask = self.client.post(
            f"/api/projects/{PROJECT_A}/ask",
            headers=self.admin_headers,
            json={"query": "What does the finance plan say about grants in Spain?", "top_k": 3},
        )
        self.assertEqual(ask.status_code, 200)
        ask_json = ask.json()
        self.assertEqual(ask_json["query"], "What does the finance plan say about grants in Spain?")
        self.assertEqual(ask_json["top_k"], 3)
        self.assertTrue(ask_json["retrieved_chunks"])
        self.assertEqual(ask_json["retrieved_chunks"][0]["document_id"], document_id)
        self.assertIn("Spain", ask_json["retrieved_chunks"][0]["chunk_text"])
        self.assertTrue(ask_json["grounded_summary"])

        denied_reindex = self.client.post(
            f"/api/projects/{PROJECT_A}/documents/reindex",
            headers=self.tenant_b_headers,
            json={"document_id": document_id},
        )
        denied_chunks = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}/chunks",
            headers=self.tenant_b_headers,
        )
        denied_ask = self.client.post(
            f"/api/projects/{PROJECT_A}/ask",
            headers=self.tenant_b_headers,
            json={"query": "Spain grants", "top_k": 2},
        )
        self.assertEqual(denied_reindex.status_code, 403)
        self.assertEqual(denied_chunks.status_code, 403)
        self.assertEqual(denied_ask.status_code, 403)


if __name__ == "__main__":
    unittest.main()
