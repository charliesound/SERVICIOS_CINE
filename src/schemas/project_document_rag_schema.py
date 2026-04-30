from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    project_id: str
    organization_id: str
    chunk_index: int
    chunk_text: str
    chunk_tokens_estimate: int
    metadata_json: dict | None = None
    created_at: datetime


class DocumentChunkListResponse(BaseModel):
    project_id: str
    document_id: str
    count: int
    chunks: list[DocumentChunkResponse]


class ProjectDocumentReindexRequest(BaseModel):
    document_id: str | None = None


class ProjectDocumentReindexResponse(BaseModel):
    project_id: str
    processed_documents: int
    processed_chunks: int
    embedding_provider: str


class ProjectDocumentAskRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    document_type: str
    chunk_index: int
    score: float
    chunk_text: str
    metadata_json: dict | None = None


class ProjectDocumentAskResponse(BaseModel):
    query: str
    top_k: int
    retrieved_chunks: list[RetrievedChunkResponse]
    grounded_summary: str | None = None
    embedding_provider: str
