from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class StorageSourceCreate(BaseModel):
    organization_id: Optional[str] = None
    project_id: str
    name: str
    source_type: str = "local_mounted_path"
    mount_path: str


class StorageSourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    mount_path: Optional[str] = None
    status: Optional[str] = None


class StorageSourceResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    name: str
    source_type: str
    mount_path: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StorageValidateRequest(BaseModel):
    path_override: Optional[str] = None


class StorageHandshakeResponse(BaseModel):
    source_id: str
    validated_path: str
    exists: bool
    is_dir: bool
    readable: bool
    free_space: Optional[int] = None
    total_space: Optional[int] = None
    status: str
    message: str


class StorageAuthorizeRequest(BaseModel):
    authorization_mode: str = "explicit"
    scope_path: str
    expires_at: Optional[datetime] = None


class StorageAuthorizationResponse(BaseModel):
    id: str
    storage_source_id: str
    authorization_mode: str
    scope_path: str
    status: str
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StorageWatchPathCreate(BaseModel):
    watch_path: str


class StorageWatchPathResponse(BaseModel):
    id: str
    storage_source_id: str
    watch_path: str
    status: str
    last_validated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StorageSourceListResponse(BaseModel):
    items: List[StorageSourceResponse]


class StorageWatchPathListResponse(BaseModel):
    items: List[StorageWatchPathResponse]


class IngestEventResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: Optional[str] = None
    event_type: str
    event_payload_json: Dict[str, Any]
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
