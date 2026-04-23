from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class IngestScanLaunchRequest(BaseModel):
    watch_path_id: Optional[str] = None

    @field_validator("watch_path_id")
    @classmethod
    def validate_watch_path_id(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class IngestScanResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: str
    watch_path_id: Optional[str]
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    files_discovered_count: int
    files_indexed_count: int
    files_skipped_count: int
    error_message: Optional[str]
    created_by: Optional[str]


class IngestScanListResponse(BaseModel):
    scans: List[IngestScanResponse] = Field(default_factory=list)


class MediaAssetResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: str
    watch_path_id: Optional[str]
    ingest_scan_id: Optional[str]
    file_name: str
    relative_path: str
    canonical_path: str
    file_extension: str
    mime_type: Optional[str]
    asset_type: str
    file_size: int
    modified_at: Optional[datetime]
    discovered_at: datetime
    status: str
    created_by: Optional[str]


class MediaAssetListResponse(BaseModel):
    assets: List[MediaAssetResponse] = Field(default_factory=list)
