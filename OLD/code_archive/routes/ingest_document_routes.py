from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.ingest_document import (
    DocumentAsset,
    DocumentClassification,
    DocumentExtraction,
    DocumentStructuredData,
)
from routes.auth_routes import get_authenticated_user, get_token_payload
from schemas.ingest_document_schema import (
    DocumentApproveRequest,
    DocumentAssetCreate,
    DocumentAssetDetailResponse,
    DocumentAssetListResponse,
    DocumentAssetResponse,
    DocumentAssetUpdate,
    DocumentClassifyRequest,
    DocumentClassificationResponse,
    DocumentEventListResponse,
    DocumentExtractRequest,
    DocumentExtractionResponse,
    DocumentStructureRequest,
    DocumentStructuredDataResponse,
)
from services.document_understanding_service import (
    classify_document_content,
    detect_file_metadata,
    extract_document_content,
    generate_structured_payload,
    get_document_events,
    get_document_source_path,
    get_latest_classification,
    get_latest_extraction,
    get_latest_structured_data,
    get_owned_document,
    resolve_document_context,
)
from services.storage_handshake_service import (
    log_ingest_event,
    normalize_mounted_path,
    resolve_organization_id,
)

router = APIRouter(prefix="/api/ingest/documents", tags=["documents"])


def to_detail_response(
    document: DocumentAsset,
    extraction: Optional[DocumentExtraction],
    classification: Optional[DocumentClassification],
    structured: Optional[DocumentStructuredData],
) -> DocumentAssetDetailResponse:
    return DocumentAssetDetailResponse(
        **DocumentAssetResponse.model_validate(document).model_dump(),
        latest_extraction=DocumentExtractionResponse.model_validate(extraction)
        if extraction
        else None,
        latest_classification=DocumentClassificationResponse.model_validate(
            classification
        )
        if classification
        else None,
        latest_structured_data=DocumentStructuredDataResponse.model_validate(structured)
        if structured
        else None,
    )


@router.post("", response_model=DocumentAssetResponse)
async def create_document_asset(
    payload: DocumentAssetCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    if not payload.original_path and not payload.media_asset_id:
        raise HTTPException(
            status_code=400, detail="Provide original_path or media_asset_id"
        )

    organization_id, media_asset, source = await resolve_document_context(
        db,
        token_payload,
        user.user_id,
        payload.organization_id,
        payload.project_id,
        payload.media_asset_id,
        payload.storage_source_id,
    )

    source_path = payload.original_path or (
        media_asset.canonical_path if media_asset else None
    )
    if not source_path:
        raise HTTPException(
            status_code=400, detail="Document source path could not be resolved"
        )
    normalized_path = normalize_mounted_path(source_path)
    if not Path(normalized_path).exists():
        raise HTTPException(status_code=400, detail="Document path does not exist")

    file_name = payload.file_name or Path(normalized_path).name
    file_extension, mime_type = detect_file_metadata(file_name, normalized_path)
    document = DocumentAsset(
        organization_id=organization_id,
        project_id=payload.project_id,
        storage_source_id=source.id
        if source
        else (media_asset.storage_source_id if media_asset else None),
        media_asset_id=media_asset.id if media_asset else payload.media_asset_id,
        file_name=file_name,
        file_extension=file_extension,
        mime_type=mime_type,
        source_kind="media_asset" if media_asset else payload.source_kind,
        original_path=normalized_path,
        uploaded_by=user.user_id,
        status="registered",
    )
    db.add(document)
    await db.flush()
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.created",
        payload={
            "document_asset_id": document.id,
            "file_name": document.file_name,
            "source_kind": document.source_kind,
        },
        created_by=user.user_id,
    )
    await db.refresh(document)
    return document


@router.get("", response_model=DocumentAssetListResponse)
async def list_document_assets(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    doc_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    filters = [DocumentAsset.uploaded_by == user.user_id]
    if organization_id is not None:
        filters.append(DocumentAsset.organization_id == organization_id)
    if project_id is not None:
        filters.append(DocumentAsset.project_id == project_id)
    if status is not None:
        filters.append(DocumentAsset.status == status)

    result = await db.execute(select(DocumentAsset).where(and_(*filters)))
    items = result.scalars().all()
    if doc_type is not None:
        filtered = []
        for item in items:
            latest_classification = await get_latest_classification(db, item.id)
            if latest_classification and latest_classification.doc_type == doc_type:
                filtered.append(item)
        items = filtered
    return DocumentAssetListResponse(items=items)


@router.get("/{document_id}", response_model=DocumentAssetDetailResponse)
async def get_document_asset(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    extraction = await get_latest_extraction(db, document.id)
    classification = await get_latest_classification(db, document.id)
    structured = await get_latest_structured_data(db, document.id)
    return to_detail_response(document, extraction, classification, structured)


@router.patch("/{document_id}", response_model=DocumentAssetResponse)
async def update_document_asset(
    document_id: str,
    payload: DocumentAssetUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    if payload.file_name is not None:
        document.file_name = payload.file_name
    if payload.original_path is not None:
        normalized_path = normalize_mounted_path(payload.original_path)
        if not Path(normalized_path).exists():
            raise HTTPException(status_code=400, detail="Document path does not exist")
        document.original_path = normalized_path
        document.file_extension, document.mime_type = detect_file_metadata(
            document.file_name, normalized_path
        )
    if payload.status is not None:
        document.status = payload.status
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.updated",
        payload={"document_asset_id": document.id},
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(document)
    return document


@router.post("/{document_id}/extract", response_model=DocumentExtractionResponse)
async def extract_document(
    document_id: str,
    payload: DocumentExtractRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    source_path = get_document_source_path(document, None)
    extraction_status, raw_text, extracted_table_json, error_message, engine = (
        extract_document_content(
            source_path,
            document.file_extension,
        )
    )
    extraction = DocumentExtraction(
        document_asset_id=document.id,
        extraction_status=extraction_status,
        extraction_engine=engine,
        raw_text=raw_text,
        extracted_table_json=extracted_table_json,
        error_message=error_message,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(extraction)
    document.status = (
        "extracted" if extraction_status == "completed" else "needs_review"
    )
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.extracted",
        payload={
            "document_asset_id": document.id,
            "extraction_status": extraction_status,
            "extraction_engine": engine,
        },
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(extraction)
    return extraction


@router.post("/{document_id}/classify", response_model=DocumentClassificationResponse)
async def classify_document(
    document_id: str,
    payload: DocumentClassifyRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    extraction = await get_latest_extraction(db, document.id)
    doc_type, confidence = classify_document_content(
        extraction.raw_text if extraction else None,
        extraction.extracted_table_json if extraction else None,
    )
    classification = DocumentClassification(
        document_asset_id=document.id,
        doc_type=doc_type,
        classification_status="suggested",
        confidence_score=confidence,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(classification)
    document.status = "classified"
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.classified",
        payload={
            "document_asset_id": document.id,
            "doc_type": doc_type,
            "confidence_score": confidence,
        },
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(classification)
    return classification


@router.post("/{document_id}/structure", response_model=DocumentStructuredDataResponse)
async def structure_document(
    document_id: str,
    payload: DocumentStructureRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    extraction = await get_latest_extraction(db, document.id)
    classification = await get_latest_classification(db, document.id)
    if classification is None:
        doc_type, confidence = classify_document_content(
            extraction.raw_text if extraction else None,
            extraction.extracted_table_json if extraction else None,
        )
        classification = DocumentClassification(
            document_asset_id=document.id,
            doc_type=doc_type,
            classification_status="suggested",
            confidence_score=confidence,
        )
        db.add(classification)
        await db.flush()

    schema_type = payload.schema_type or classification.doc_type
    structured = DocumentStructuredData(
        document_asset_id=document.id,
        schema_type=schema_type,
        structured_payload_json=generate_structured_payload(
            document, classification, extraction
        ),
        review_status="pending_review",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(structured)
    document.status = "structured"
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.structured",
        payload={
            "document_asset_id": document.id,
            "schema_type": schema_type,
        },
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(structured)
    return structured


@router.post("/{document_id}/approve", response_model=DocumentStructuredDataResponse)
async def approve_document_structure(
    document_id: str,
    payload: DocumentApproveRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    structured = await get_latest_structured_data(db, document.id)
    if structured is None:
        raise HTTPException(
            status_code=400, detail="No structured payload exists for this document"
        )
    if payload.structured_payload_json is not None:
        structured.structured_payload_json = payload.structured_payload_json
    structured.review_status = "approved"
    structured.approved_by = user.user_id
    structured.approved_at = datetime.utcnow()
    structured.updated_at = datetime.utcnow()
    document.status = "approved"
    await log_ingest_event(
        db=db,
        organization_id=document.organization_id,
        project_id=document.project_id,
        storage_source_id=document.storage_source_id,
        event_type="document_asset.approved",
        payload={"document_asset_id": document.id},
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(structured)
    return structured


@router.get("/{document_id}/events", response_model=DocumentEventListResponse)
async def list_document_events(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    document = await get_owned_document(db, document_id, organization_id, user.user_id)
    events = await get_document_events(db, document)
    return DocumentEventListResponse(items=events)
