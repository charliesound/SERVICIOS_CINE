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


router = APIRouter(prefix="/api/projects/{project_id}/memory", tags=["cid-memory"])


class IndexResponse(BaseModel):
    project_id: str
    organization_id: str
    project_name: str
    sources_indexed: list[dict[str, Any]]
    total_chunks: int
    total_points_upserted: int
    errors: list[str] | None = None


class StatusResponse(BaseModel):
    project_id: str
    organization_id: str
    indexed_chunks: int
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


@router.post("/index", response_model=IndexResponse)
async def memory_index(
    project_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        "Memory index requested project=%s org=%s user=%s",
        project_id, tenant.organization_id, tenant.user_id,
    )
    result = await index_project(
        db,
        organization_id=tenant.organization_id,
        project_id=project_id,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return IndexResponse(**result)


@router.get("/status", response_model=StatusResponse)
async def memory_status(
    project_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    count = await qdrant_memory_service.count_project_points(
        organization_id=tenant.organization_id,
        project_id=project_id,
    )
    return StatusResponse(
        project_id=project_id,
        organization_id=tenant.organization_id,
        indexed_chunks=count,
        sources=["script_text", "storyboard_shots", "production_breakdowns"],
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
