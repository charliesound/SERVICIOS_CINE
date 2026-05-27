from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class GoogleDriveConnectionStatusResponse(BaseModel):
    provider: str
    status: str
    connected: bool
    external_account_email: str | None = None
    scope: str | None = None
    token_expiry_at: datetime | None = None


class GoogleDriveFolderItemResponse(BaseModel):
    folder_id: str
    name: str
    parent_id: str | None = None
    path_hint: str | None = None


class GoogleDriveFolderListResponse(BaseModel):
    project_id: str
    count: int
    folders: list[GoogleDriveFolderItemResponse]


class GoogleDriveLinkFolderRequest(BaseModel):
    external_folder_id: str
    external_folder_name: str


class GoogleDriveFolderLinkResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    connection_id: str
    provider: str
    external_folder_id: str
    external_folder_name: str
    sync_mode: str
    last_sync_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GoogleDriveFolderLinkListResponse(BaseModel):
    project_id: str
    count: int
    links: list[GoogleDriveFolderLinkResponse]


class GoogleDriveSyncResponse(BaseModel):
    project_id: str
    provider: str
    status: str
    imported: int
    updated: int
    skipped: int
    errors: int
    stale: int
    linked_folders: int
    synced_at: datetime


class GoogleDriveSyncStateItemResponse(BaseModel):
    external_file_id: str
    linked_project_document_id: str | None = None
    sync_status: str
    external_modified_time: datetime | None = None
    external_checksum: str | None = None
    last_seen_at: datetime | None = None
    stale: bool


class GoogleDriveSyncStatusResponse(BaseModel):
    project_id: str
    provider: str
    count: int
    links: list[GoogleDriveFolderLinkResponse]
    states: list[GoogleDriveSyncStateItemResponse]
    last_sync_at: datetime | None = None


class N8NStatusResponse(BaseModel):
    provider: str = "n8n"
    enabled: bool
    status: str
    base_url: str | None = None
    reachable: bool = False
    test_webhook_path: str | None = None
    timeout_seconds: int
    trace_id: str | None = None
    error: str | None = None


class N8NTestRequest(BaseModel):
    event_type: str = "cid.integration.test"
    project_id: str | None = None
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class N8NTestResponse(BaseModel):
    sent: bool
    status: Literal["sent", "skipped", "failed"]
    trace_id: str
    event_type: str
    endpoint_path: str | None = None
    response_status_code: int | None = None
    error: str | None = None


class IntegrationEventPayload(BaseModel):
    event_type: str
    trace_id: str
    project_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str = "cid"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
