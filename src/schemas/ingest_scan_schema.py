from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class IngestScanCreate(BaseModel):
    watch_path_id: Optional[str] = None


class IngestScanResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: str
    watch_path_id: Optional[str] = None
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    files_discovered_count: int
    files_indexed_count: int
    files_skipped_count: int
    error_message: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class IngestScanListResponse(BaseModel):
    items: List[IngestScanResponse]


class MediaAssetResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: str
    watch_path_id: Optional[str] = None
    ingest_scan_id: Optional[str] = None
    file_name: str
    relative_path: str
    canonical_path: str
    file_extension: str
    mime_type: Optional[str] = None
    asset_type: str
    file_size: int
    modified_at: Optional[datetime] = None
    discovered_at: datetime
    status: str
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class MediaAssetListResponse(BaseModel):
    items: List[MediaAssetResponse]
