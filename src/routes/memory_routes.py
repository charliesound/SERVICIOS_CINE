from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from services.cid_memory_ingestion_service import index_project
from services.logging_service import logger
from services.qdrant_memory_service import qdrant_memory_service
from services.rag_embedding_service import rag_embedding_service
from core.config import get_settings
from services.cid_rag_answer_service import cid_rag_answer_service
from services.ollama_llm_service import (
    OllamaLLMConnectionError,
    OllamaLLMEmptyResponseError,
    OllamaLLMTimeoutError,
)


router = APIRouter(prefix="/api/projects/{project_id}/memory", tags=["cid-memory"])


class IndexResponse(BaseModel):
    project_id: str
    organization_id: str
    project_name: str
    sources_indexed: list[dict[str, Any]]
    total_chunks: int
    total_points_upserted: int
    deleted_points: int = 0
    errors: list[str] | None = None


class StatusResponse(BaseModel):
    project_id: str
    organization_id: str
    total_points_for_project: int
    points_by_source_type: dict[str, int]
    embedding_model: str
    collection_name: str
    collection_vector_size: int
    collection_distance: str
    sources: list[str]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)
    source_type: str | None = None


class SearchResult(BaseModel):
    id: str
    score: float
    source_type: str
    source_id: str
    source_table: str
    title: str
    text: str
    chunk_index: int
    chunk_count: int
    tags: list[str]


class SearchResponse(BaseModel):
    query: str
    project_id: str
    organization_id: str
    results: list[SearchResult]
    total_results: int


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)
    source_types: list[str] | None = None
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    include_sources: bool = True


class AnswerUsage(BaseModel):
    context_chunks: int
    prompt_chars: int


class AnswerResponse(BaseModel):
    answer: str
    project_id: str
    organization_id: str
    model: str
    sources: list[SearchResult]
    usage: AnswerUsage


class IndexRequest(BaseModel):
    clean: bool = False


@router.post("/index", response_model=IndexResponse)
async def memory_index(
    project_id: str,
    request: IndexRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        "Memory index requested project=%s org=%s user=%s clean=%s",
        project_id, tenant.organization_id, tenant.user_id, request.clean,
    )

    deleted_points = 0
    if request.clean:
        # Delete existing points for this project before reindexing
        deleted_points = await qdrant_memory_service.delete_project_points(
            organization_id=tenant.organization_id,
            project_id=project_id,
        )
        if deleted_points < 0:
            raise HTTPException(status_code=500, detail="Failed to delete existing points")

    result = await index_project(
        db,
        organization_id=tenant.organization_id,
        project_id=project_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response_data = IndexResponse(**result)
    response_data.deleted_points = deleted_points
    return response_data


@router.get("/status", response_model=StatusResponse)
async def memory_status(
    project_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    # Get detailed collection info
    collection_info = await qdrant_memory_service.get_collection_info()
    settings = get_settings()

    # Get project-specific points count and breakdown by source type
    total_points = await qdrant_memory_service.count_project_points(
        organization_id=tenant.organization_id,
        project_id=project_id,
    )

    points_by_source = await qdrant_memory_service.count_points_by_source_type(
        organization_id=tenant.organization_id,
        project_id=project_id,
    )

    return StatusResponse(
        project_id=project_id,
        organization_id=tenant.organization_id,
        total_points_for_project=total_points,
        points_by_source_type=points_by_source,
        embedding_model=collection_info.get("embedding_model", settings.embedding_model),
        collection_name=collection_info.get("collection_name", settings.cid_memory_collection),
        collection_vector_size=collection_info.get("vector_size", settings.embedding_vector_size),
        collection_distance=collection_info.get("distance", "Cosine"),
        sources=list(points_by_source.keys()) if points_by_source else ["script_text", "storyboard_shots", "production_breakdowns"],
    )


@router.post("/search", response_model=SearchResponse)
async def memory_search(
    project_id: str,
    req: SearchRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    try:
        query_vector = await rag_embedding_service.embed_query(req.query)
    except Exception as exc:
        logger.error("Search embedding failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Embedding failed: {exc}")

    results = await qdrant_memory_service.search(
        organization_id=tenant.organization_id,
        project_id=project_id,
        query_vector=query_vector,
        limit=req.limit,
        source_type=req.source_type,
    )

    out = [SearchResult(**r) for r in results]
    return SearchResponse(
        query=req.query,
        project_id=project_id,
        organization_id=tenant.organization_id,
        results=out,
        total_results=len(out),
    )


@router.post("/answer", response_model=AnswerResponse)
async def memory_answer(
    project_id: str,
    req: AnswerRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    del db
    try:
        result = await cid_rag_answer_service.answer_question(
            organization_id=tenant.organization_id,
            project_id=project_id,
            question=req.question,
            limit=req.limit,
            source_types=req.source_types,
            temperature=req.temperature,
            include_sources=req.include_sources,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OllamaLLMTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except (OllamaLLMConnectionError, OllamaLLMEmptyResponseError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Memory answer failed project=%s org=%s: %s", project_id, tenant.organization_id, exc)
        raise HTTPException(status_code=500, detail="Failed to generate RAG answer") from exc

    return AnswerResponse(**result)
