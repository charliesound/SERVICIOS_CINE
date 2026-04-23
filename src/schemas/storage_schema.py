from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class StorageSourceCreate(BaseModel):
    organization_id: str
    project_id: str
    name: str
    source_type: str = "local"
    mount_path: str

    @field_validator("organization_id")
    @classmethod
    def validate_organization_id(cls, value: str) -> str:
        return _normalize_required_text(value, "organization_id")

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value: str) -> str:
        return _normalize_required_text(value, "project_id")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "name")

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        return _normalize_required_text(value, "source_type")

    @field_validator("mount_path")
    @classmethod
    def validate_mount_path(cls, value: str) -> str:
        return _normalize_required_text(value, "mount_path")


class StorageSourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class StorageSourceResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    name: str
    source_type: str
    mount_path: str
    status: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime


class StorageSourceListResponse(BaseModel):
    storage_sources: List[StorageSourceResponse] = Field(default_factory=list)


class StorageSourceValidateResponse(BaseModel):
    source_id: str
    mount_path: str
    metadata: Dict[str, Any]


class StorageAuthorizationCreate(BaseModel):
    authorization_mode: str = "read"
    scope_path: str
    expires_at: Optional[datetime] = None

    @field_validator("authorization_mode")
    @classmethod
    def validate_authorization_mode(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ("read", "write", "read_write"):
            raise ValueError("Invalid authorization_mode. Must be: read, write, or read_write")
        return normalized

    @field_validator("scope_path")
    @classmethod
    def validate_scope_path(cls, value: str) -> str:
        return _normalize_required_text(value, "scope_path")


class StorageAuthorizationResponse(BaseModel):
    id: str
    storage_source_id: str
    authorization_mode: str
    scope_path: str
    status: str
    granted_by: Optional[str]
    granted_at: datetime
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime]


class StorageAuthorizationListResponse(BaseModel):
    authorizations: List[StorageAuthorizationResponse] = Field(default_factory=list)


class StorageWatchPathCreate(BaseModel):
    watch_path: str

    @field_validator("watch_path")
    @classmethod
    def validate_watch_path(cls, value: str) -> str:
        return _normalize_required_text(value, "watch_path")


class StorageWatchPathResponse(BaseModel):
    id: str
    storage_source_id: str
    watch_path: str
    status: str
    last_validated_at: Optional[datetime]
    created_at: datetime


class StorageWatchPathListResponse(BaseModel):
    watch_paths: List[StorageWatchPathResponse] = Field(default_factory=list)


class StorageHandshakeResponse(BaseModel):
    source_id: str
    mount_path: str
    metadata: Dict[str, Any]
    validated: bool
    authorizations: List[StorageAuthorizationResponse] = Field(default_factory=list)


class IngestEventResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: Optional[str]
    event_type: str
    event_payload_json: Optional[str]
    created_by: Optional[str]
    created_at: datetime
