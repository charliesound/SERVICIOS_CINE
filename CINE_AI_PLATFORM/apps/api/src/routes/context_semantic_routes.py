from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.auth.dependencies import require_roles
from src.schemas.context_semantic import (
    ContextSemanticErrorResponse,
    ContextSemanticIngestRequest,
    ContextSemanticIngestResponse,
    ContextSemanticSearchRequest,
    ContextSemanticSearchResponse,
)
from src.services.embeddings_service import EmbeddingsService, EmbeddingsServiceError
from src.services.qdrant_context_service import QdrantContextService, QdrantContextServiceError


def create_context_semantic_router(
    embeddings_service: EmbeddingsService,
    qdrant_context_service: QdrantContextService,
) -> APIRouter:
    router = APIRouter(prefix="/api/context/semantic", tags=["semantic-context"])

    @router.post(
        "/ingest",
        status_code=201,
        response_model=ContextSemanticIngestResponse,
        responses={400: {"model": ContextSemanticErrorResponse}, 500: {"model": ContextSemanticErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def ingest_context(payload: ContextSemanticIngestRequest):
        try:
            text = str(payload.text or "").strip() or f"{payload.title.strip()}\n\n{payload.content.strip()}"
            embedding = embeddings_service.embed_text(
                text=text,
                metadata={
                    "project_id": payload.project_id,
                    "sequence_id": payload.sequence_id,
                    "scene_id": payload.scene_id,
                    "shot_id": payload.shot_id,
                    "entity_type": payload.entity_type,
                    "title": payload.title,
                    "source": payload.source,
                },
            )
            return qdrant_context_service.upsert_context(
                payload=payload,
                vector=embedding["vector"],
                embedding_model=embedding["model"],
                dimensions=embedding["dimensions"],
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_CONTEXT_SEMANTIC_INGEST_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except EmbeddingsServiceError as error:
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                    },
                },
            )
        except QdrantContextServiceError as error:
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "CONTEXT_SEMANTIC_INGEST_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/search",
        response_model=ContextSemanticSearchResponse,
        responses={400: {"model": ContextSemanticErrorResponse}, 500: {"model": ContextSemanticErrorResponse}},
    )
    def search_context(payload: ContextSemanticSearchRequest):
        try:
            embedding = embeddings_service.embed_text(
                text=payload.text,
                metadata={
                    "project_id": payload.project_id,
                    "sequence_id": payload.sequence_id,
                    "scene_id": payload.scene_id,
                    "shot_id": payload.shot_id,
                    "entity_type": payload.entity_type,
                    "source": payload.source,
                    "limit": payload.limit,
                },
            )
            return qdrant_context_service.search_context(
                payload=payload,
                vector=embedding["vector"],
                embedding_model=embedding["model"],
                dimensions=embedding["dimensions"],
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_CONTEXT_SEMANTIC_SEARCH_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except EmbeddingsServiceError as error:
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                    },
                },
            )
        except QdrantContextServiceError as error:
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                        "details": error.details,
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "CONTEXT_SEMANTIC_SEARCH_FAILED",
                        "message": str(error),
                    },
                },
            )

    return router
