import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class DocumentAssetCreate(BaseModel):
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    storage_source_id: Optional[str] = None
    media_asset_id: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    source_kind: Optional[str] = None
    original_path: Optional[str] = None
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None

    @field_validator(
        "organization_id",
        "project_id",
        "storage_source_id",
        "media_asset_id",
        "file_name",
        "mime_type",
        "source_kind",
        "original_path",
        "shooting_day_id",
        "sequence_id",
        "scene_id",
        "shot_id",
    )
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DocumentAssetUpdate(BaseModel):
    status: Optional[str] = None
    original_path: Optional[str] = None
    structured_payload_json: Optional[Dict[str, Any]] = None
    review_status: Optional[str] = None

    @field_validator("status", "original_path", "review_status")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DocumentExtractionResponse(BaseModel):
    id: str
    document_asset_id: str
    extraction_status: str
    extraction_engine: Optional[str]
    raw_text: Optional[str]
    extracted_table_json: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class DocumentClassificationResponse(BaseModel):
    id: str
    document_asset_id: str
    doc_type: str
    classification_status: str
    confidence_score: Optional[float]
    created_at: datetime
    updated_at: datetime


class DocumentStructuredDataResponse(BaseModel):
    id: str
    document_asset_id: str
    schema_type: str
    structured_payload_json: Dict[str, Any]
    review_status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class DocumentLinkResponse(BaseModel):
    id: str
    document_asset_id: str
    organization_id: str
    project_id: str
    shooting_day_id: Optional[str]
    sequence_id: Optional[str]
    scene_id: Optional[str]
    shot_id: Optional[str]
    media_asset_id: Optional[str]
    created_at: datetime


class DocumentAssetResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: Optional[str]
    media_asset_id: Optional[str]
    file_name: str
    file_extension: str
    mime_type: Optional[str]
    source_kind: str
    original_path: Optional[str]
    uploaded_by: Optional[str]
    status: str
    created_at: datetime
    extraction: Optional[DocumentExtractionResponse] = None
    classification: Optional[DocumentClassificationResponse] = None
    structured_data: Optional[DocumentStructuredDataResponse] = None
    links: List[DocumentLinkResponse] = Field(default_factory=list)


class DocumentAssetListResponse(BaseModel):
    documents: List[DocumentAssetResponse] = Field(default_factory=list)


class DocumentApproveRequest(BaseModel):
    approved_by: Optional[str] = None

    @field_validator("approved_by")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DocumentEventResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: Optional[str]
    document_asset_id: Optional[str]
    event_type: str
    event_payload_json: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_at: datetime


class DocumentEventListResponse(BaseModel):
    events: List[DocumentEventResponse] = Field(default_factory=list)


class DerivePreviewResponse(BaseModel):
    target_report_type: str
    initial_report_payload: Dict[str, Any]
    source_document_id: str
    allowed: bool
    reason: Optional[str] = None


class DeriveReportRequest(BaseModel):
    report_payload: Dict[str, Any]
    report_type: str
    shooting_day_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    report_date: Optional[date] = None

    @field_validator(
        "report_type", "shooting_day_id", "sequence_id", "scene_id", "shot_id"
    )
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class DeriveReportResponse(BaseModel):
    report_id: str
    report_type: str
    message: str
