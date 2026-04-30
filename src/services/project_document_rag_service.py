from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import DocumentChunk, ProjectDocument
from services.logging_service import logger


class ProjectDocumentRagService:
    def __init__(self) -> None:
        self.chunk_size_chars = int(os.getenv("PROJECT_DOCUMENT_CHUNK_SIZE", "900"))
        self.chunk_overlap_chars = int(os.getenv("PROJECT_DOCUMENT_CHUNK_OVERLAP", "150"))
        self.embedding_dimensions = int(os.getenv("PROJECT_DOCUMENT_EMBEDDING_DIMENSIONS", "96"))
        self.embedding_provider = os.getenv("PROJECT_DOCUMENT_EMBEDDING_PROVIDER", "local_hash").strip() or "local_hash"

    def _normalize_text(self, value: str) -> str:
        compact = re.sub(r"\s+", " ", (value or "").strip())
        return compact

    def _tokenize(self, value: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9_\-]{2,}", value.lower())

    def _estimate_tokens(self, value: str) -> int:
        return max(1, len(self._tokenize(value)))

    def _chunk_text(self, text: str) -> list[str]:
        normalized = self._normalize_text(text)
        if not normalized:
            return []
        if len(normalized) <= self.chunk_size_chars:
            return [normalized]

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + self.chunk_size_chars)
            if end < len(normalized):
                boundary = normalized.rfind(" ", start, end)
                if boundary > start + int(self.chunk_size_chars * 0.6):
                    end = boundary
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(normalized):
                break
            start = max(end - self.chunk_overlap_chars, start + 1)
        return chunks

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.embedding_dimensions
        tokens = self._tokenize(text)
        counts = Counter(tokens)
        if not counts:
            return vector
        for token, count in counts.items():
            token_hash = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            index = token_hash % self.embedding_dimensions
            sign = -1.0 if (token_hash >> 8) % 2 else 1.0
            vector[index] += float(count) * sign
        magnitude = math.sqrt(sum(item * item for item in vector))
        if magnitude <= 0:
            return vector
        return [item / magnitude for item in vector]

    def _log_embedding_usage(self, *, texts: int, tokens: int) -> None:
        logger.info(
            "ProjectDocumentRAG embedding usage provider=%s texts=%s tokens=%s estimated_cost=0",
            self.embedding_provider,
            texts,
            tokens,
        )

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        return float(sum(a * b for a, b in zip(left, right)))

    def _serialize_embedding(self, vector: list[float]) -> str:
        return json.dumps(vector, ensure_ascii=True)

    def _deserialize_embedding(self, payload: str | None) -> list[float]:
        if not payload:
            return []
        try:
            raw = json.loads(payload)
        except json.JSONDecodeError:
            return []
        if not isinstance(raw, list):
            return []
        return [float(item) for item in raw]

    async def index_document(
        self,
        db: AsyncSession,
        *,
        document: ProjectDocument,
        force: bool = True,
    ) -> int:
        if force:
            await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
            await db.flush()

        chunks = self._chunk_text(document.extracted_text or "")
        self._log_embedding_usage(
            texts=len(chunks),
            tokens=sum(self._estimate_tokens(chunk) for chunk in chunks),
        )
        metadata = {
            "document_type": document.document_type,
            "file_name": document.file_name,
            "checksum": document.checksum,
            "visibility_scope": document.visibility_scope,
        }
        for index, chunk_text in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=str(document.id),
                    project_id=str(document.project_id),
                    organization_id=str(document.organization_id),
                    chunk_index=index,
                    chunk_text=chunk_text,
                    chunk_tokens_estimate=self._estimate_tokens(chunk_text),
                    embedding_payload=self._serialize_embedding(self._embed_text(chunk_text)),
                    metadata_json=json.dumps(metadata, ensure_ascii=True),
                )
            )
        return len(chunks)

    async def index_project(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        query = select(ProjectDocument).where(
            ProjectDocument.project_id == project_id,
            ProjectDocument.organization_id == organization_id,
        )
        if document_id:
            query = query.where(ProjectDocument.id == document_id)
        result = await db.execute(query.order_by(ProjectDocument.created_at.asc()))
        documents = list(result.scalars().all())

        processed_documents = 0
        processed_chunks = 0
        for document in documents:
            if not (document.extracted_text or "").strip():
                continue
            processed_documents += 1
            processed_chunks += await self.index_document(db, document=document, force=True)
        await db.commit()
        return {
            "project_id": project_id,
            "processed_documents": processed_documents,
            "processed_chunks": processed_chunks,
            "embedding_provider": self.embedding_provider,
        }

    async def list_document_chunks(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        document_id: str,
    ) -> list[DocumentChunk]:
        result = await db.execute(
            select(DocumentChunk)
            .where(
                DocumentChunk.project_id == project_id,
                DocumentChunk.organization_id == organization_id,
                DocumentChunk.document_id == document_id,
            )
            .order_by(DocumentChunk.chunk_index.asc())
        )
        return list(result.scalars().all())

    async def ask(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        query_text: str,
        top_k: int,
    ) -> dict[str, Any]:
        query_embedding = self._embed_text(query_text)
        self._log_embedding_usage(texts=1, tokens=self._estimate_tokens(query_text))
        result = await db.execute(
            select(DocumentChunk, ProjectDocument)
            .join(ProjectDocument, ProjectDocument.id == DocumentChunk.document_id)
            .where(
                DocumentChunk.project_id == project_id,
                DocumentChunk.organization_id == organization_id,
                ProjectDocument.project_id == project_id,
                ProjectDocument.organization_id == organization_id,
            )
        )

        ranked: list[dict[str, Any]] = []
        for chunk, document in result.all():
            metadata = None
            if chunk.metadata_json:
                try:
                    metadata = json.loads(chunk.metadata_json)
                except json.JSONDecodeError:
                    metadata = None
            ranked.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(document.id),
                    "file_name": str(document.file_name),
                    "document_type": str(document.document_type),
                    "chunk_index": int(chunk.chunk_index),
                    "score": self._cosine_similarity(
                        query_embedding,
                        self._deserialize_embedding(chunk.embedding_payload),
                    ),
                    "chunk_text": str(chunk.chunk_text),
                    "metadata_json": metadata,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        selected = ranked[:top_k]
        grounded_summary = None
        if selected:
            grounded_summary = " ".join(item["chunk_text"] for item in selected[:3])[:1200]
        return {
            "query": query_text,
            "top_k": top_k,
            "retrieved_chunks": selected,
            "grounded_summary": grounded_summary,
            "embedding_provider": self.embedding_provider,
        }


project_document_rag_service = ProjectDocumentRagService()
