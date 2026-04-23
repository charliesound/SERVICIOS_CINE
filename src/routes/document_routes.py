import json
from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import User as DBUser
from models.document import (
    DocumentAsset,
    DocumentClassification,
    DocumentExtraction,
    DocumentLink,
    DocumentStructuredData,
)
from models.storage import IngestEvent
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.document_schema import (
    DerivePreviewResponse,
    DeriveReportRequest,
    DeriveReportResponse,
    DocumentApproveRequest,
    DocumentAssetCreate,
    DocumentAssetListResponse,
    DocumentAssetResponse,
    DocumentAssetUpdate,
    DocumentClassificationResponse,
    DocumentEventListResponse,
    DocumentEventResponse,
    DocumentExtractionResponse,
    DocumentLinkResponse,
    DocumentStructuredDataResponse,
)
from services.document_service import document_service


router = APIRouter(prefix="/api/ingest/documents", tags=["documents"])


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


def _parse_json_payload(raw_value: Optional[str]) -> Optional[dict]:
    if not raw_value:
        return None
    try:
        return json.loads(raw_value)
    except Exception:
        return {"raw": raw_value}


def _extraction_response(
    extraction: Optional[DocumentExtraction],
) -> Optional[DocumentExtractionResponse]:
    if extraction is None:
        return None
    return DocumentExtractionResponse(
        id=str(extraction.id),
        document_asset_id=str(extraction.document_asset_id),
        extraction_status=str(extraction.extraction_status),
        extraction_engine=getattr(extraction, "extraction_engine", None),
        raw_text=getattr(extraction, "raw_text", None),
        extracted_table_json=_parse_json_payload(
            getattr(extraction, "extracted_table_json", None)
        ),
        error_message=getattr(extraction, "error_message", None),
        created_at=cast(datetime, extraction.created_at),
        updated_at=cast(datetime, extraction.updated_at),
    )


def _classification_response(
    classification: Optional[DocumentClassification],
) -> Optional[DocumentClassificationResponse]:
    if classification is None:
        return None
    return DocumentClassificationResponse(
        id=str(classification.id),
        document_asset_id=str(classification.document_asset_id),
        doc_type=str(classification.doc_type),
        classification_status=str(classification.classification_status),
        confidence_score=(
            float(classification.confidence_score)
            if getattr(classification, "confidence_score", None) is not None
            else None
        ),
        created_at=cast(datetime, classification.created_at),
        updated_at=cast(datetime, classification.updated_at),
    )


def _structured_data_response(
    structured_data: Optional[DocumentStructuredData],
) -> Optional[DocumentStructuredDataResponse]:
    if structured_data is None:
        return None
    return DocumentStructuredDataResponse(
        id=str(structured_data.id),
        document_asset_id=str(structured_data.document_asset_id),
        schema_type=str(structured_data.schema_type),
        structured_payload_json=_parse_json_payload(
            structured_data.structured_payload_json
        )
        or {},
        review_status=str(structured_data.review_status),
        approved_by=getattr(structured_data, "approved_by", None),
        approved_at=getattr(structured_data, "approved_at", None),
        created_at=cast(datetime, structured_data.created_at),
        updated_at=cast(datetime, structured_data.updated_at),
    )


def _link_response(link: DocumentLink) -> DocumentLinkResponse:
    return DocumentLinkResponse(
        id=str(link.id),
        document_asset_id=str(link.document_asset_id),
        organization_id=str(link.organization_id),
        project_id=str(link.project_id),
        shooting_day_id=getattr(link, "shooting_day_id", None),
        sequence_id=getattr(link, "sequence_id", None),
        scene_id=getattr(link, "scene_id", None),
        shot_id=getattr(link, "shot_id", None),
        media_asset_id=getattr(link, "media_asset_id", None),
        created_at=cast(datetime, link.created_at),
    )


def _document_response(document: DocumentAsset) -> DocumentAssetResponse:
    return DocumentAssetResponse(
        id=str(document.id),
        organization_id=str(document.organization_id),
        project_id=str(document.project_id),
        storage_source_id=getattr(document, "storage_source_id", None),
        media_asset_id=getattr(document, "media_asset_id", None),
        file_name=str(document.file_name),
        file_extension=str(document.file_extension),
        mime_type=getattr(document, "mime_type", None),
        source_kind=str(document.source_kind),
        original_path=getattr(document, "original_path", None),
        uploaded_by=getattr(document, "uploaded_by", None),
        status=str(document.status),
        created_at=cast(datetime, document.created_at),
        extraction=_extraction_response(getattr(document, "extraction", None)),
        classification=_classification_response(
            getattr(document, "classification", None)
        ),
        structured_data=_structured_data_response(
            getattr(document, "structured_data", None)
        ),
        links=[_link_response(link) for link in getattr(document, "links", [])],
    )


def _event_response(event: IngestEvent) -> DocumentEventResponse:
    return DocumentEventResponse(
        id=str(event.id),
        organization_id=str(event.organization_id),
        project_id=str(event.project_id),
        storage_source_id=getattr(event, "storage_source_id", None),
        document_asset_id=getattr(event, "document_asset_id", None),
        event_type=str(event.event_type),
        event_payload_json=_parse_json_payload(
            getattr(event, "event_payload_json", None)
        ),
        created_by=getattr(event, "created_by", None),
        created_at=cast(datetime, event.created_at),
    )


async def _get_document_or_404(
    document_id: str,
    user_org_id: str,
    db: AsyncSession,
) -> DocumentAsset:
    document = await document_service.get_document(db, document_id, user_org_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("", response_model=DocumentAssetResponse)
async def create_document_asset(
    payload: DocumentAssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await document_service.create_document(
        db,
        user_org_id=user_org_id,
        payload=payload.model_dump(exclude_none=True),
        uploaded_by=current_user.user_id,
    )
    return _document_response(document)


@router.get("", response_model=DocumentAssetListResponse)
async def list_document_assets(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    doc_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    documents = await document_service.list_documents(
        db,
        organization_id=user_org_id,
        project_id=project_id,
        status=status,
        doc_type=doc_type,
    )
    return DocumentAssetListResponse(
        documents=[_document_response(document) for document in documents]
    )


@router.get("/{document_id}", response_model=DocumentAssetResponse)
async def get_document_asset(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    return _document_response(document)


@router.patch("/{document_id}", response_model=DocumentAssetResponse)
async def update_document_asset(
    document_id: str,
    payload: DocumentAssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    updated = await document_service.update_document(
        db,
        document,
        status=payload.status,
        original_path=payload.original_path,
        structured_payload_json=payload.structured_payload_json,
        review_status=payload.review_status,
        updated_by=current_user.user_id,
    )
    return _document_response(updated)


@router.post("/{document_id}/extract", response_model=DocumentAssetResponse)
async def extract_document_asset(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    extracted = await document_service.extract_document(
        db, document, created_by=current_user.user_id
    )
    return _document_response(extracted)


@router.post("/{document_id}/classify", response_model=DocumentAssetResponse)
async def classify_document_asset(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    classified = await document_service.classify_document(
        db, document, created_by=current_user.user_id
    )
    return _document_response(classified)


@router.post("/{document_id}/structure", response_model=DocumentAssetResponse)
async def structure_document_asset(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    structured = await document_service.structure_document(
        db, document, created_by=current_user.user_id
    )
    return _document_response(structured)


@router.post("/{document_id}/approve", response_model=DocumentAssetResponse)
async def approve_document_asset(
    document_id: str,
    payload: DocumentApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    approved = await document_service.approve_document(
        db,
        document,
        approved_by=payload.approved_by or current_user.user_id,
    )
    return _document_response(approved)


@router.get("/{document_id}/events", response_model=DocumentEventListResponse)
async def list_document_asset_events(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DocumentEventListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    events = await document_service.list_document_events(db, document)
    return DocumentEventListResponse(
        events=[_event_response(event) for event in events]
    )


@router.post("/{document_id}/derive-preview", response_model=DerivePreviewResponse)
async def derive_document_preview(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DerivePreviewResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    preview = await document_service.derive_preview(
        db, document, created_by=current_user.user_id
    )
    return DerivePreviewResponse(**preview)


@router.post("/{document_id}/derive-report", response_model=DeriveReportResponse)
async def derive_document_report(
    document_id: str,
    payload: DeriveReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DeriveReportResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    document = await _get_document_or_404(document_id, user_org_id, db)
    report_payload = {
        **payload.report_payload,
        "shooting_day_id": payload.shooting_day_id,
        "sequence_id": payload.sequence_id,
        "scene_id": payload.scene_id,
        "shot_id": payload.shot_id,
        "report_date": payload.report_date,
    }
    result = await document_service.derive_report(
        db,
        document,
        report_payload=report_payload,
        report_type=payload.report_type,
        created_by=current_user.user_id,
    )
    return DeriveReportResponse(**result)
