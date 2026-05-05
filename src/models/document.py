from datetime import datetime, timezone
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
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


class DocumentSourceKind:
    MEDIA_ASSET = "media_asset"
    PATH = "path"
    SCRIPT_TEXT = "script_text"


class DocumentAssetStatus:
    REGISTERED = "registered"
    EXTRACTED = "extracted"
    CLASSIFIED = "classified"
    STRUCTURED = "structured"
    APPROVED = "approved"
    PENDING_OCR = "pending_ocr"
    UNSUPPORTED = "unsupported"
    ERROR = "error"


class ExtractionStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_OCR = "pending_ocr"
    UNSUPPORTED = "unsupported"


class ClassificationStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class StructuredReviewStatus:
    DRAFT = "draft"
    APPROVED = "approved"


class DocumentType:
    SCRIPT = "script"
    CAMERA_REPORT = "camera_report"
    SOUND_REPORT = "sound_report"
    SCRIPT_NOTE = "script_note"
    DIRECTOR_NOTE = "director_note"
    OPERATOR_NOTE = "operator_note"
    UNKNOWN = "unknown_document"


class ProjectDocumentType:
    SCRIPT = "script"
    BUDGET = "budget"
    CONTRACT = "contract"
    TREATMENT = "treatment"
    FINANCE_PLAN = "finance_plan"
    OTHER = "other"


class ProjectDocumentUploadStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class ProjectDocumentVisibilityScope:
    PROJECT = "project"
    ORGANIZATION_PRIVATE = "organization_private"


class ProjectDocument(Base):
    __tablename__ = "project_documents"
    __table_args__ = (
        Index("ix_project_documents_org_project", "organization_id", "project_id"),
        Index("ix_project_documents_status_created_at", "upload_status", "created_at"),
        Index("ix_project_documents_checksum", "checksum"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)
    uploaded_by_user_id = Column(String(36), nullable=True, index=True)
    document_type = Column(String(50), nullable=False, default=ProjectDocumentType.OTHER)
    upload_status = Column(
        String(20), nullable=False, default=ProjectDocumentUploadStatus.PENDING
    )
    file_name = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    file_size = Column(Float, nullable=False, default=0)
    storage_path = Column(String(2000), nullable=False)
    checksum = Column(String(64), nullable=False)
    extracted_text = Column(Text, nullable=True)
    visibility_scope = Column(
        String(30), nullable=False, default=ProjectDocumentVisibilityScope.PROJECT
    )
    error_message = Column(Text, nullable=True)
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

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_doc_chunk", "document_id", "chunk_index"),
        Index("ix_document_chunks_org_project", "organization_id", "project_id"),
        Index("ix_document_chunks_created_at", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(
        String(36),
        ForeignKey("project_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(String(36), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_tokens_estimate = Column(Integer, nullable=False, default=0)
    embedding_payload = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("ProjectDocument", back_populates="chunks")


class DocumentAsset(Base):
    __tablename__ = "document_assets"
    __table_args__ = (
        Index("ix_document_assets_org_project", "organization_id", "project_id"),
        Index("ix_document_assets_status_created_at", "status", "created_at"),
        Index("ix_document_assets_media_asset", "media_asset_id"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    storage_source_id = Column(String(36), nullable=True, index=True)
    media_asset_id = Column(
        String(36),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_extension = Column(String(50), nullable=False)
    mime_type = Column(String(255), nullable=True)
    source_kind = Column(String(50), nullable=False)
    original_path = Column(String(2000), nullable=True)
    uploaded_by = Column(String(36), nullable=True)
    status = Column(String(50), default=DocumentAssetStatus.REGISTERED, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    extraction = relationship(
        "DocumentExtraction",
        back_populates="document_asset",
        uselist=False,
        cascade="all, delete-orphan",
    )
    classification = relationship(
        "DocumentClassification",
        back_populates="document_asset",
        uselist=False,
        cascade="all, delete-orphan",
    )
    structured_data = relationship(
        "DocumentStructuredData",
        back_populates="document_asset",
        uselist=False,
        cascade="all, delete-orphan",
    )
    links = relationship(
        "DocumentLink", back_populates="document_asset", cascade="all, delete-orphan"
    )


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    __table_args__ = (
        UniqueConstraint(
            "document_asset_id", name="uq_document_extractions_document_asset_id"
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_asset_id = Column(
        String(36),
        ForeignKey("document_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    extraction_status = Column(
        String(50), default=ExtractionStatus.PENDING, nullable=False
    )
    extraction_engine = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=True)
    extracted_table_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
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

    document_asset = relationship("DocumentAsset", back_populates="extraction")


class DocumentClassification(Base):
    __tablename__ = "document_classifications"
    __table_args__ = (
        UniqueConstraint(
            "document_asset_id", name="uq_document_classifications_document_asset_id"
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_asset_id = Column(
        String(36),
        ForeignKey("document_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type = Column(String(100), default=DocumentType.UNKNOWN, nullable=False)
    classification_status = Column(
        String(50), default=ClassificationStatus.PENDING, nullable=False
    )
    confidence_score = Column(Float, nullable=True)
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

    document_asset = relationship("DocumentAsset", back_populates="classification")


class DocumentStructuredData(Base):
    __tablename__ = "document_structured_data"
    __table_args__ = (
        UniqueConstraint(
            "document_asset_id", name="uq_document_structured_data_document_asset_id"
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_asset_id = Column(
        String(36),
        ForeignKey("document_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schema_type = Column(String(100), nullable=False)
    structured_payload_json = Column(Text, nullable=False)
    review_status = Column(
        String(50), default=StructuredReviewStatus.DRAFT, nullable=False
    )
    approved_by = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
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

    document_asset = relationship("DocumentAsset", back_populates="structured_data")


class DocumentLink(Base):
    __tablename__ = "document_links"
    __table_args__ = (
        Index("ix_document_links_org_project", "organization_id", "project_id"),
        Index("ix_document_links_media_asset", "media_asset_id"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_asset_id = Column(
        String(36),
        ForeignKey("document_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=False, index=True)
    shooting_day_id = Column(String(36), nullable=True)
    sequence_id = Column(String(36), nullable=True)
    scene_id = Column(String(36), nullable=True)
    shot_id = Column(String(36), nullable=True)
    media_asset_id = Column(
        String(36),
        ForeignKey("media_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    document_asset = relationship("DocumentAsset", back_populates="links")
