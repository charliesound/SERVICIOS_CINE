from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.project_document_schema import (
    ProjectDocumentListResponse,
    ProjectDocumentResponse,
)
from schemas.project_document_rag_schema import (
    DocumentChunkListResponse,
    DocumentChunkResponse,
    ProjectDocumentAskRequest,
    ProjectDocumentAskResponse,
    ProjectDocumentReindexRequest,
    ProjectDocumentReindexResponse,
    RetrievedChunkResponse,
)
from services.project_document_service import project_document_service
from services.project_document_rag_service import project_document_rag_service


router = APIRouter(prefix="/api/projects", tags=["project-documents"])


def _to_response(document) -> ProjectDocumentResponse:
    return ProjectDocumentResponse(
        id=str(document.id),
        project_id=str(document.project_id),
        organization_id=str(document.organization_id),
        uploaded_by_user_id=getattr(document, "uploaded_by_user_id", None),
        document_type=str(document.document_type),
        upload_status=str(document.upload_status),
        file_name=str(document.file_name),
        mime_type=str(document.mime_type),
        file_size=float(document.file_size),
        storage_path=str(document.storage_path),
        checksum=str(document.checksum),
        extracted_text=getattr(document, "extracted_text", None),
        visibility_scope=str(document.visibility_scope),
        error_message=getattr(document, "error_message", None),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _to_chunk_response(chunk) -> DocumentChunkResponse:
    metadata = None
    if getattr(chunk, "metadata_json", None):
        import json

        try:
            metadata = json.loads(chunk.metadata_json)
        except json.JSONDecodeError:
            metadata = None
    return DocumentChunkResponse(
        id=str(chunk.id),
        document_id=str(chunk.document_id),
        project_id=str(chunk.project_id),
        organization_id=str(chunk.organization_id),
        chunk_index=int(chunk.chunk_index),
        chunk_text=str(chunk.chunk_text),
        chunk_tokens_estimate=int(chunk.chunk_tokens_estimate),
        metadata_json=metadata,
        created_at=chunk.created_at,
    )


async def _get_project_or_403(project_id: str, db: AsyncSession, tenant: TenantContext):
    project = await project_document_service.get_project_for_tenant(
        db, project_id, tenant.organization_id
    )
    if project is None:
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


@router.post("/{project_id}/documents", response_model=ProjectDocumentResponse, status_code=201)
async def upload_project_document(
    project_id: str,
    document_type: str = Form(...),
    visibility_scope: str = Form("project"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ProjectDocumentResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    document = await project_document_service.create_document(
        db,
        project=project,
        uploaded_by_user_id=tenant.user_id,
        document_type=document_type,
        visibility_scope=visibility_scope,
        upload=file,
    )
    return _to_response(document)


@router.get("/{project_id}/documents", response_model=ProjectDocumentListResponse)
async def list_project_documents(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ProjectDocumentListResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    documents = await project_document_service.list_documents(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
    )
    return ProjectDocumentListResponse(
        project_id=project_id,
        count=len(documents),
        documents=[_to_response(item) for item in documents],
    )


@router.get("/{project_id}/documents/{document_id}", response_model=ProjectDocumentResponse)
async def get_project_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ProjectDocumentResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    document = await project_document_service.get_document(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=document_id,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Project document not found")
    return _to_response(document)


@router.get("/{project_id}/documents/{document_id}/download")
async def download_project_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    document = await project_document_service.get_document(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=document_id,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Project document not found")
    file_path = project_document_service.ensure_downloadable_file(document)
    return FileResponse(path=file_path, filename=document.file_name, media_type=document.mime_type)


@router.delete("/{project_id}/documents/{document_id}")
async def delete_project_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    document = await project_document_service.get_document(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=document_id,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Project document not found")
    await project_document_service.delete_document(db, document=document)
    return JSONResponse(
        content={
            "project_id": project_id,
            "document_id": document_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "status": "deleted",
        }
    )


@router.post("/{project_id}/documents/reindex", response_model=ProjectDocumentReindexResponse)
async def reindex_project_documents(
    project_id: str,
    payload: ProjectDocumentReindexRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ProjectDocumentReindexResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    if payload and payload.document_id:
        document = await project_document_service.get_document(
            db,
            project_id=str(project.id),
            organization_id=str(project.organization_id),
            document_id=payload.document_id,
        )
        if document is None:
            raise HTTPException(status_code=404, detail="Project document not found")
    result = await project_document_rag_service.index_project(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=payload.document_id if payload else None,
    )
    return ProjectDocumentReindexResponse(**result)


@router.get(
    "/{project_id}/documents/{document_id}/chunks",
    response_model=DocumentChunkListResponse,
)
async def list_project_document_chunks(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DocumentChunkListResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    document = await project_document_service.get_document(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=document_id,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Project document not found")
    chunks = await project_document_rag_service.list_document_chunks(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        document_id=document_id,
    )
    return DocumentChunkListResponse(
        project_id=project_id,
        document_id=document_id,
        count=len(chunks),
        chunks=[_to_chunk_response(chunk) for chunk in chunks],
    )


@router.post("/{project_id}/ask", response_model=ProjectDocumentAskResponse)
async def ask_project_documents(
    project_id: str,
    payload: ProjectDocumentAskRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ProjectDocumentAskResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    result = await project_document_rag_service.ask(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        query_text=payload.query,
        top_k=payload.top_k,
    )
    result["retrieved_chunks"] = [RetrievedChunkResponse(**item) for item in result["retrieved_chunks"]]
    return ProjectDocumentAskResponse(**result)
