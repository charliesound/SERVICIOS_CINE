from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


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
