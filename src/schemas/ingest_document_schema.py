from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from schemas.storage_handshake_schema import IngestEventResponse


class DocumentAssetCreate(BaseModel):
    organization_id: Optional[str] = None
    project_id: str
    storage_source_id: Optional[str] = None
    media_asset_id: Optional[str] = None
    file_name: Optional[str] = None
    original_path: Optional[str] = None
    source_kind: str = "mounted_path"


class DocumentAssetUpdate(BaseModel):
    file_name: Optional[str] = None
    original_path: Optional[str] = None
    status: Optional[str] = None


class DocumentExtractionResponse(BaseModel):
    id: str
    document_asset_id: str
    extraction_status: str
    extraction_engine: Optional[str] = None
    raw_text: Optional[str] = None
    extracted_table_json: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentClassificationResponse(BaseModel):
    id: str
    document_asset_id: str
    doc_type: str
    classification_status: str
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStructuredDataResponse(BaseModel):
    id: str
    document_asset_id: str
    schema_type: str
    structured_payload_json: Dict[str, Any]
    review_status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentAssetResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    storage_source_id: Optional[str] = None
    media_asset_id: Optional[str] = None
    file_name: str
    file_extension: str
    mime_type: Optional[str] = None
    source_kind: str
    original_path: Optional[str] = None
    uploaded_by: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentAssetDetailResponse(DocumentAssetResponse):
    latest_extraction: Optional[DocumentExtractionResponse] = None
    latest_classification: Optional[DocumentClassificationResponse] = None
    latest_structured_data: Optional[DocumentStructuredDataResponse] = None


class DocumentAssetListResponse(BaseModel):
    items: List[DocumentAssetResponse]


class DocumentExtractRequest(BaseModel):
    force: bool = False


class DocumentClassifyRequest(BaseModel):
    force: bool = False


class DocumentStructureRequest(BaseModel):
    schema_type: Optional[str] = None


class DocumentApproveRequest(BaseModel):
    structured_payload_json: Optional[Dict[str, Any]] = None


class DocumentEventListResponse(BaseModel):
    items: List[IngestEventResponse]
