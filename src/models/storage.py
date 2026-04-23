from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class StorageSourceStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class StorageAuthorizationMode:
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"


class StorageAuthorizationStatus:
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class StorageWatchPathStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"


class StorageSource(Base):
    __tablename__ = "storage_sources"
    __table_args__ = (
        Index(
            "ix_storage_sources_organization_project", "organization_id", "project_id"
        ),
        Index("ix_storage_sources_status", "status"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, default="local")
    mount_path = Column(String(1000), nullable=False)
    status = Column(
        String(20),
        default=StorageSourceStatus.ACTIVE,
        nullable=False,
    )
    created_by = Column(String(36), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    authorizations = relationship(
        "StorageAuthorization",
        back_populates="storage_source",
        cascade="all, delete-orphan",
    )
    watch_paths = relationship(
        "StorageWatchPath",
        back_populates="storage_source",
        cascade="all, delete-orphan",
    )


class StorageAuthorization(Base):
    __tablename__ = "storage_authorizations"
    __table_args__ = (
        Index("ix_storage_authorizations_source_status", "storage_source_id", "status"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    storage_source_id = Column(
        String(36),
        ForeignKey("storage_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    authorization_mode = Column(
        String(20),
        default=StorageAuthorizationMode.READ,
        nullable=False,
    )
    scope_path = Column(String(1000), nullable=False)
    status = Column(
        String(20),
        default=StorageAuthorizationStatus.ACTIVE,
        nullable=False,
    )
    granted_by = Column(String(36), nullable=True)
    granted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    storage_source = relationship("StorageSource", back_populates="authorizations")


class StorageWatchPath(Base):
    __tablename__ = "storage_watch_paths"
    __table_args__ = (
        Index("ix_storage_watch_paths_source_status", "storage_source_id", "status"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    storage_source_id = Column(
        String(36),
        ForeignKey("storage_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    watch_path = Column(String(1000), nullable=False)
    status = Column(
        String(20),
        default=StorageWatchPathStatus.ACTIVE,
        nullable=False,
    )
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    storage_source = relationship("StorageSource", back_populates="watch_paths")


class IngestEventType:
    SOURCE_CREATED = "source_created"
    SOURCE_VALIDATED = "source_validated"
    SOURCE_AUTHORIZED = "source_authorized"
    WATCH_PATH_ADDED = "watch_path_added"
    WATCH_PATH_VALIDATED = "watch_path_validated"
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    ASSET_INDEXED = "asset_indexed"
    DOCUMENT_REGISTERED = "document_registered"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_EXTRACTED = "document_extracted"
    DOCUMENT_CLASSIFIED = "document_classified"
    DOCUMENT_STRUCTURED = "document_structured"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_DERIVE_PREVIEW = "document.derive_preview"
    DOCUMENT_DERIVE_REPORT_CREATED = "document.derive_report_created"
    DOCUMENT_DERIVE_REPORT_REJECTED = "document.derive_report_rejected"
    REPORT_CREATED = "report_created"
    REPORT_UPDATED = "report_updated"
    REPORT_LINKED_TO_DOCUMENT = "report.linked_to_document"
    ERROR = "error"


class IngestScanStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MediaAssetStatus:
    INDEXED = "indexed"


class MediaAssetType:
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class IngestEvent(Base):
    __tablename__ = "ingest_events"
    __table_args__ = (
        Index("ix_ingest_events_org_project", "organization_id", "project_id"),
        Index("ix_ingest_events_source", "storage_source_id"),
        Index("ix_ingest_events_created_at", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    storage_source_id = Column(String(36), nullable=True, index=True)
    document_asset_id = Column(String(36), nullable=True, index=True)
    event_type = Column(String(50), nullable=False)
    event_payload_json = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )


class IngestScan(Base):
    __tablename__ = "ingest_scans"
    __table_args__ = (
        Index("ix_ingest_scans_org_project", "organization_id", "project_id"),
        Index("ix_ingest_scans_source_started_at", "storage_source_id", "started_at"),
        Index("ix_ingest_scans_status_started_at", "status", "started_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    storage_source_id = Column(
        String(36),
        ForeignKey("storage_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    watch_path_id = Column(
        String(36),
        ForeignKey("storage_watch_paths.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(String(20), default=IngestScanStatus.RUNNING, nullable=False)
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)
    files_discovered_count = Column(Integer, default=0, nullable=False)
    files_indexed_count = Column(Integer, default=0, nullable=False)
    files_skipped_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=True)

    storage_source = relationship("StorageSource")
    watch_path = relationship("StorageWatchPath")


class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint(
            "storage_source_id",
            "canonical_path",
            name="uq_media_assets_source_canonical_path",
        ),
        Index("ix_media_assets_org_project", "organization_id", "project_id"),
        Index("ix_media_assets_source_asset_type", "storage_source_id", "asset_type"),
        Index("ix_media_assets_scan_status", "ingest_scan_id", "status"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    storage_source_id = Column(
        String(36),
        ForeignKey("storage_sources.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    watch_path_id = Column(
        String(36),
        ForeignKey("storage_watch_paths.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ingest_scan_id = Column(
        String(36),
        ForeignKey("ingest_scans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    relative_path = Column(String(1000), nullable=False)
    canonical_path = Column(String(2000), nullable=False)
    content_ref = Column(String(2000), nullable=True)
    file_extension = Column(String(50), nullable=False)
    mime_type = Column(String(255), nullable=True)
    asset_type = Column(String(50), default=MediaAssetType.OTHER, nullable=False)
    metadata_json = Column(Text, nullable=True)
    file_size = Column(Integer, default=0, nullable=False)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    discovered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    status = Column(String(20), default=MediaAssetStatus.INDEXED, nullable=False)
    created_by = Column(String(36), nullable=True)
    job_id = Column(String(36), nullable=True, index=True)
    asset_source = Column(String(50), nullable=True)

    storage_source = relationship("StorageSource")
    watch_path = relationship("StorageWatchPath")
    ingest_scan = relationship("IngestScan")
