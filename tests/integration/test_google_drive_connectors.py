from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


TEST_DB_PATH = Path("/tmp/test_google_drive_connectors.db")
TEST_STORAGE_ROOT = Path("/tmp/test_google_drive_connectors_storage")
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
from services.google_drive_service import OAuthTokenPayload, google_drive_service


ORG_A = "org-a-gdrive-000000000000000001"
ORG_B = "org-b-gdrive-000000000000000001"
ADMIN_A = "admin-a-gdrive-000000000000001"
USER_B = "user-b-gdrive-00000000000000001"
PROJECT_A = "project-a-gdrive-0000000000001"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _insert_row(connection: sqlite3.Connection, table_name: str, payload: dict[str, object]) -> None:
    available_columns = _table_columns(connection, table_name)
    hydrated_payload = dict(payload)
    timestamp = "2026-04-23 00:00:00"
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
        _insert_row(connection, "organizations", {"id": ORG_A, "name": "Drive Org A", "billing_plan": "free", "is_active": 1})
        _insert_row(connection, "organizations", {"id": ORG_B, "name": "Drive Org B", "billing_plan": "free", "is_active": 1})
        _insert_row(
            connection,
            "users",
            {
                "id": ADMIN_A,
                "organization_id": ORG_A,
                "username": "drive_admin_a",
                "email": "drive_admin_a@example.com",
                "hashed_password": "unused",
                "full_name": "Drive Admin A",
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
                "username": "drive_user_b",
                "email": "drive_user_b@example.com",
                "hashed_password": "unused",
                "full_name": "Drive User B",
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
                "name": "Drive Project",
                "description": "Project with Google Drive sync.",
                "status": "development",
            },
        )
        connection.commit()
    finally:
        connection.close()


async def _force_initialize_schema() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


class FakeGoogleDriveClient:
    files_by_folder = {
        "folder-001": [
            {
                "id": "file-001",
                "name": "production_notes.txt",
                "mimeType": "text/plain",
                "modifiedTime": "2026-04-23T10:00:00Z",
                "md5Checksum": "md5-v1",
                "parents": ["folder-001"],
            },
            {
                "id": "file-unsupported",
                "name": "poster.jpg",
                "mimeType": "image/jpeg",
                "modifiedTime": "2026-04-23T10:00:00Z",
                "md5Checksum": "jpg-v1",
                "parents": ["folder-001"],
            },
        ]
    }
    file_bytes = {
        "file-001": b"First sync text from Google Drive for funding and production.",
    }

    def build_authorize_url(self, *, redirect_uri: str, state: str) -> str:
        return f"https://fake.google/oauth?redirect_uri={redirect_uri}&state={state}"

    async def exchange_code(self, *, code: str, redirect_uri: str) -> OAuthTokenPayload:
        del code, redirect_uri
        return OAuthTokenPayload(
            access_token="fake-access-token",
            refresh_token="fake-refresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            scope="https://www.googleapis.com/auth/drive.readonly",
        )

    async def refresh_access_token(self, *, refresh_token: str) -> OAuthTokenPayload:
        del refresh_token
        return OAuthTokenPayload(
            access_token="fake-access-token-refreshed",
            refresh_token="fake-refresh-token",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            scope="https://www.googleapis.com/auth/drive.readonly",
        )

    async def get_account_email(self, *, access_token: str) -> str | None:
        del access_token
        return "producer@example.com"

    async def list_folders(self, *, access_token: str, parent_id: str | None):
        del access_token
        if parent_id == "folder-001":
            return [{"id": "folder-001-a", "name": "Contracts", "parents": ["folder-001"]}]
        return [{"id": "folder-001", "name": "Producer Vault", "parents": ["root"]}]

    async def list_files(self, *, access_token: str, folder_id: str):
        del access_token
        return list(self.files_by_folder.get(folder_id, []))

    async def download_file(self, *, access_token: str, file_id: str) -> bytes:
        del access_token
        return self.file_bytes[file_id]


class GoogleDriveConnectorsIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        asyncio.run(_force_initialize_schema())
        _seed_test_data()
        cls.original_factory = google_drive_service.client_factory
        google_drive_service.client_factory = FakeGoogleDriveClient
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()
        cls.admin_headers = _auth_headers(ADMIN_A, "drive_admin_a@example.com")
        cls.tenant_b_headers = _auth_headers(USER_B, "drive_user_b@example.com")

    @classmethod
    def tearDownClass(cls) -> None:
        google_drive_service.client_factory = cls.original_factory
        cls.client_cm.__exit__(None, None, None)
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        if TEST_STORAGE_ROOT.exists():
            shutil.rmtree(TEST_STORAGE_ROOT)

    def test_google_drive_oauth_link_and_incremental_sync(self) -> None:
        status_before = self.client.get(
            "/api/integrations/google-drive/status",
            headers=self.admin_headers,
        )
        self.assertEqual(status_before.status_code, 200)
        self.assertFalse(status_before.json()["connected"])

        connect = self.client.get(
            "/api/integrations/google-drive/connect",
            headers=self.admin_headers,
            follow_redirects=False,
        )
        self.assertEqual(connect.status_code, 307)
        redirect_location = connect.headers["location"]
        redirect_query = parse_qs(urlparse(redirect_location).query)
        state = redirect_query["state"][0]

        callback = self.client.get(
            f"/api/integrations/google-drive/callback?code=fake-code&state={state}"
        )
        self.assertEqual(callback.status_code, 200)
        self.assertEqual(callback.json()["status"], "connected")
        self.assertEqual(callback.json()["external_account_email"], "producer@example.com")

        status_after = self.client.get(
            "/api/integrations/google-drive/status",
            headers=self.admin_headers,
        )
        self.assertEqual(status_after.status_code, 200)
        self.assertTrue(status_after.json()["connected"])

        folders = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/folders",
            headers=self.admin_headers,
        )
        self.assertEqual(folders.status_code, 200)
        self.assertEqual(folders.json()["count"], 1)
        self.assertEqual(folders.json()["folders"][0]["folder_id"], "folder-001")

        link = self.client.post(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/link-folder",
            headers=self.admin_headers,
            json={
                "external_folder_id": "folder-001",
                "external_folder_name": "Producer Vault",
            },
        )
        self.assertEqual(link.status_code, 201)
        link_id = link.json()["id"]

        links = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/link-folder",
            headers=self.admin_headers,
        )
        self.assertEqual(links.status_code, 200)
        self.assertEqual(links.json()["count"], 1)

        first_sync = self.client.post(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync",
            headers=self.admin_headers,
        )
        self.assertEqual(first_sync.status_code, 200)
        first_sync_json = first_sync.json()
        self.assertEqual(first_sync_json["imported"], 1)
        self.assertEqual(first_sync_json["updated"], 0)
        self.assertEqual(first_sync_json["errors"], 0)

        project_documents = self.client.get(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
        )
        self.assertEqual(project_documents.status_code, 200)
        self.assertEqual(project_documents.json()["count"], 1)
        document_id = project_documents.json()["documents"][0]["id"]
        checksum_v1 = project_documents.json()["documents"][0]["checksum"]
        self.assertIn("First sync text", project_documents.json()["documents"][0]["extracted_text"])

        chunks = self.client.get(
            f"/api/projects/{PROJECT_A}/documents/{document_id}/chunks",
            headers=self.admin_headers,
        )
        self.assertEqual(chunks.status_code, 200)
        self.assertGreaterEqual(chunks.json()["count"], 1)

        second_sync = self.client.post(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync",
            headers=self.admin_headers,
        )
        self.assertEqual(second_sync.status_code, 200)
        self.assertEqual(second_sync.json()["imported"], 0)
        self.assertEqual(second_sync.json()["updated"], 0)
        self.assertEqual(second_sync.json()["skipped"], 1)

        FakeGoogleDriveClient.files_by_folder["folder-001"][0]["modifiedTime"] = "2026-04-23T11:15:00Z"
        FakeGoogleDriveClient.files_by_folder["folder-001"][0]["md5Checksum"] = "md5-v2"
        FakeGoogleDriveClient.file_bytes["file-001"] = b"Updated sync text from Google Drive with revised financing notes."

        third_sync = self.client.post(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync",
            headers=self.admin_headers,
        )
        self.assertEqual(third_sync.status_code, 200)
        self.assertEqual(third_sync.json()["imported"], 0)
        self.assertEqual(third_sync.json()["updated"], 1)

        documents_after_update = self.client.get(
            f"/api/projects/{PROJECT_A}/documents",
            headers=self.admin_headers,
        )
        self.assertEqual(documents_after_update.status_code, 200)
        self.assertEqual(documents_after_update.json()["count"], 1)
        self.assertEqual(documents_after_update.json()["documents"][0]["id"], document_id)
        self.assertNotEqual(documents_after_update.json()["documents"][0]["checksum"], checksum_v1)
        self.assertIn("Updated sync text", documents_after_update.json()["documents"][0]["extracted_text"])

        sync_status = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync-status",
            headers=self.admin_headers,
        )
        self.assertEqual(sync_status.status_code, 200)
        self.assertEqual(sync_status.json()["count"], 1)
        self.assertEqual(sync_status.json()["states"][0]["linked_project_document_id"], document_id)
        self.assertFalse(sync_status.json()["states"][0]["stale"])

        tenant_b_folders = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/folders",
            headers=self.tenant_b_headers,
        )
        tenant_b_links = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/link-folder",
            headers=self.tenant_b_headers,
        )
        tenant_b_sync = self.client.post(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync",
            headers=self.tenant_b_headers,
        )
        tenant_b_sync_status = self.client.get(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/sync-status",
            headers=self.tenant_b_headers,
        )
        self.assertEqual(tenant_b_folders.status_code, 403)
        self.assertEqual(tenant_b_links.status_code, 403)
        self.assertEqual(tenant_b_sync.status_code, 403)
        self.assertEqual(tenant_b_sync_status.status_code, 403)

        delete_link = self.client.delete(
            f"/api/projects/{PROJECT_A}/integrations/google-drive/link-folder/{link_id}",
            headers=self.admin_headers,
        )
        self.assertEqual(delete_link.status_code, 200)

        disconnect = self.client.post(
            "/api/integrations/google-drive/disconnect",
            headers=self.admin_headers,
        )
        self.assertEqual(disconnect.status_code, 200)
        self.assertFalse(disconnect.json()["connected"])


if __name__ == "__main__":
    unittest.main()
