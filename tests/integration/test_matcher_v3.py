from __future__ import annotations

import json
import os
import sys
import asyncio
import sqlite3
import unittest
from pathlib import Path

# Set up test environment
TEST_DB_PATH = Path("/tmp/test_matcher_v3.db")
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


# Test constants
ORG_A = "org-a-matcher-v3-000000000001"
PROJECT_A = "project-a-matcher-v3-001"
ADMIN_A = "admin-a-matcher-v3-000000001"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def _table_columns(connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _insert_row(connection, table_name: str, payload: dict[str, object]) -> None:
    available_columns = _table_columns(connection, table_name)
    hydrated_payload = dict(payload)
    timestamp = "2026-04-23 00:00:00"
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
        # Create organization
        _insert_row(
            connection,
            "organizations",
            {"id": ORG_A, "name": "Matcher V3 Test Org", "billing_plan": "free", "is_active": 1},
        )

        # Create admin user
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

        # Create project
        _insert_row(
            connection,
            "projects",
            {
                "id": PROJECT_A,
                "organization_id": ORG_A,
                "name": "Test Project for Matcher V3",
                "description": "A test project for verifying matcher v3 automation",
                "status": "development",
                "script_text": "Test script for matcher v3 verification.",
            },
        )

        # Create a project document
        _insert_row(
            connection,
            "project_documents",
            {
                "id": "doc-test-001",
                "project_id": PROJECT_A,
                "organization_id": ORG_A,
                "uploaded_by_user_id": ADMIN_A,
                "document_type": "treatment",
                "upload_status": "completed",
                "file_name": "test_treatment.txt",
                "mime_type": "text/plain",
                "file_size": 1200,
                "storage_path": "/tmp/test_treatment.txt",
                "checksum": "test-treatment-checksum",
                "extracted_text": "This is a test treatment for matcher v3 verification.",
                "visibility_scope": "project",
            },
        )

        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class MatcherV3IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "matcher_admin_a@example.com")
        _seed_test_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def test_matcher_job_creation_via_api(self):
        """Test that we can create a matcher job via the API endpoint."""
        # Test manual trigger endpoint
        response = self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
            json={"evaluation_version": "v1.0-test"}
        )
        
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["project_id"], PROJECT_A)
        self.assertEqual(data["organization_id"], ORG_A)
        self.assertEqual(data["trigger_type"], "manual")
        self.assertEqual(data["status"], "queued")

    def test_matcher_job_status_endpoint(self):
        """Test that we can get matcher job status."""
        # First create a job
        response = self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        self.assertEqual(response.status_code, 202)
        job_data = response.json()
        job_id = job_data["id"]
        
        # Then check status
        response = self.client.get(
            f"/api/projects/{PROJECT_A}/funding/matcher/status",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_id"], PROJECT_A)
        self.assertEqual(data["organization_id"], ORG_A)
        self.assertIsNotNone(data["latest_job_id"])
        self.assertIsNotNone(data["latest_job_status"])
        self.assertGreaterEqual(data["total_jobs_count"], 1)

    def test_matcher_jobs_history_endpoint(self):
        """Test that we can get matcher job history."""
        # Create a couple of jobs
        self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        
        # Get job history
        response = self.client.get(
            f"/api/projects/{PROJECT_A}/funding/matcher/jobs",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["project_id"], PROJECT_A)
        self.assertEqual(data["organization_id"], ORG_A)
        self.assertGreaterEqual(data["total_count"], 2)
        self.assertEqual(len(data["jobs"]), 2)  # Default limit is 50

    def test_idempotency_of_matcher_jobs(self):
        """Test that duplicate jobs with same input are not created."""
        # Create first job
        response1 = self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        self.assertEqual(response1.status_code, 202)
        job1_data = response1.json()
        job1_id = job1_data["id"]
        
        # Try to create identical job immediately
        response2 = self.client.post(
            f"/api/projects/{PROJECT_A}/funding/matcher/trigger",
            headers=self.admin_headers,
            params={"organization_id": ORG_A},
        )
        self.assertEqual(response2.status_code, 202)
        job2_data = response2.json()
        job2_id = job2_data["id"]
        
        # Should be the same job due to idempotency
        self.assertEqual(job1_id, job2_id)


if __name__ == "__main__":
    # Exact venv command:
    # PYTHONPATH=/opt/SERVICIOS_CINE/src /opt/SERVICIOS_CINE/venv/bin/python -m unittest tests.integration.test_matcher_v3
    unittest.main()
