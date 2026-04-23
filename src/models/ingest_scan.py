from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base


class IngestScan(Base):
    __tablename__ = "ingest_scans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    storage_source_id = Column(
        String, ForeignKey("storage_sources.id"), nullable=False, index=True
    )
    watch_path_id = Column(
        String, ForeignKey("storage_watch_paths.id"), nullable=True, index=True
    )
    status = Column(String, nullable=False, default="queued", index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    files_discovered_count = Column(Integer, nullable=False, default=0)
    files_indexed_count = Column(Integer, nullable=False, default=0)
    files_skipped_count = Column(Integer, nullable=False, default=0)
    error_message = Column(String, nullable=True)
    created_by = Column(String, nullable=True, index=True)


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    storage_source_id = Column(
        String, ForeignKey("storage_sources.id"), nullable=False, index=True
    )
    watch_path_id = Column(
        String, ForeignKey("storage_watch_paths.id"), nullable=True, index=True
    )
    ingest_scan_id = Column(
        String, ForeignKey("ingest_scans.id"), nullable=True, index=True
    )
    file_name = Column(String, nullable=False)
    relative_path = Column(String, nullable=False, index=True)
    canonical_path = Column(String, nullable=False, index=True)
    file_extension = Column(String, nullable=False, default="")
    mime_type = Column(String, nullable=True)
    asset_type = Column(String, nullable=False, default="other", index=True)
    file_size = Column(Integer, nullable=False, default=0)
    modified_at = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="indexed", index=True)
    created_by = Column(String, nullable=True, index=True)
