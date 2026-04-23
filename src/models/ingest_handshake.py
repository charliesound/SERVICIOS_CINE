from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String

from database import Base


class StorageSource(Base):
    __tablename__ = "storage_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False, default="local_mounted_path")
    mount_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_by = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StorageAuthorization(Base):
    __tablename__ = "storage_authorizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    storage_source_id = Column(
        String, ForeignKey("storage_sources.id"), nullable=False, index=True
    )
    authorization_mode = Column(String, nullable=False, default="explicit")
    scope_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="authorized")
    granted_by = Column(String, nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)


class StorageWatchPath(Base):
    __tablename__ = "storage_watch_paths"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    storage_source_id = Column(
        String, ForeignKey("storage_sources.id"), nullable=False, index=True
    )
    watch_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    last_validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class IngestEvent(Base):
    __tablename__ = "ingest_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    storage_source_id = Column(String, nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    event_payload_json = Column(JSON, default={})
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
