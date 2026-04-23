from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String

from database import Base


class DocumentAsset(Base):
    __tablename__ = "document_assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    storage_source_id = Column(
        String, ForeignKey("storage_sources.id"), nullable=True, index=True
    )
    media_asset_id = Column(
        String, ForeignKey("media_assets.id"), nullable=True, index=True
    )
    file_name = Column(String, nullable=False)
    file_extension = Column(String, nullable=False, default="")
    mime_type = Column(String, nullable=True)
    source_kind = Column(String, nullable=False, default="mounted_path")
    original_path = Column(String, nullable=True)
    uploaded_by = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="registered", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=False, index=True
    )
    extraction_status = Column(String, nullable=False, default="pending", index=True)
    extraction_engine = Column(String, nullable=True)
    raw_text = Column(String, nullable=True)
    extracted_table_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentClassification(Base):
    __tablename__ = "document_classifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=False, index=True
    )
    doc_type = Column(String, nullable=False, default="unknown_document", index=True)
    classification_status = Column(
        String, nullable=False, default="suggested", index=True
    )
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentStructuredData(Base):
    __tablename__ = "document_structured_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=False, index=True
    )
    schema_type = Column(String, nullable=False, index=True)
    structured_payload_json = Column(JSON, default={})
    review_status = Column(String, nullable=False, default="pending_review", index=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentLink(Base):
    __tablename__ = "document_links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_asset_id = Column(
        String, ForeignKey("document_assets.id"), nullable=False, index=True
    )
    organization_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    shooting_day_id = Column(String, nullable=True)
    sequence_id = Column(String, nullable=True)
    scene_id = Column(String, nullable=True)
    shot_id = Column(String, nullable=True)
    media_asset_id = Column(String, ForeignKey("media_assets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
