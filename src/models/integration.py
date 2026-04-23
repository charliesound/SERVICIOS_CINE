from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class IntegrationProvider:
    GOOGLE_DRIVE = "google_drive"


class IntegrationConnectionStatus:
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ExternalFolderSyncMode:
    IMPORT_ONLY = "import_only"


class ExternalDocumentSyncStatus:
    PENDING = "pending"
    SYNCED = "synced"
    SKIPPED = "skipped"
    ERROR = "error"


class IntegrationConnection(Base):
    __tablename__ = "integration_connections"
    __table_args__ = (
        Index("ix_integration_connections_org_provider", "organization_id", "provider"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    external_account_email = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default=IntegrationConnectionStatus.CONNECTED)
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


class IntegrationToken(Base):
    __tablename__ = "integration_tokens"
    __table_args__ = (
        Index("ix_integration_tokens_org_connection", "organization_id", "connection_id"),
        UniqueConstraint("connection_id", name="uq_integration_tokens_connection_id"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    connection_id = Column(
        String(36),
        ForeignKey("integration_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(String(36), nullable=False, index=True)
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expiry_at = Column(DateTime(timezone=True), nullable=True)
    scope = Column(Text, nullable=True)
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


class ProjectExternalFolderLink(Base):
    __tablename__ = "project_external_folder_links"
    __table_args__ = (
        Index("ix_project_external_folder_links_org_project", "organization_id", "project_id"),
        UniqueConstraint(
            "project_id",
            "provider",
            "external_folder_id",
            name="uq_project_external_folder_links_project_provider_folder",
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)
    connection_id = Column(
        String(36),
        ForeignKey("integration_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=False, index=True)
    external_folder_id = Column(String(255), nullable=False)
    external_folder_name = Column(String(255), nullable=False)
    sync_mode = Column(String(30), nullable=False, default=ExternalFolderSyncMode.IMPORT_ONLY)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
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


class ExternalDocumentSyncState(Base):
    __tablename__ = "external_document_sync_state"
    __table_args__ = (
        Index("ix_external_document_sync_state_org_project", "organization_id", "project_id"),
        UniqueConstraint(
            "project_id",
            "provider",
            "external_file_id",
            name="uq_external_document_sync_state_project_provider_file",
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    external_file_id = Column(String(255), nullable=False)
    external_modified_time = Column(DateTime(timezone=True), nullable=True)
    external_checksum = Column(String(255), nullable=True)
    linked_project_document_id = Column(
        String(36),
        ForeignKey("project_documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sync_status = Column(String(20), nullable=False, default=ExternalDocumentSyncStatus.PENDING)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
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
