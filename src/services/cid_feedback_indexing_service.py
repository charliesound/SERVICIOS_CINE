from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.client_feedback import CIDClientFeedback, CIDFeedbackMemoryEntry
from services.logging_service import logger
from services.qdrant_memory_service import _build_point_id, qdrant_memory_service
from services.rag_embedding_service import rag_embedding_service

SOURCE_TYPE_FEEDBACK = "client_feedback"
SOURCE_TABLE_FEEDBACK = "cid_client_feedback"

NON_INDEXABLE_TYPES: frozenset[str] = frozenset({"source_blacklist"})


def build_feedback_text(feedback: CIDClientFeedback) -> str:
    parts: list[str] = []
    if feedback.original_question:
        parts.append(f"Pregunta: {feedback.original_question}")
    if feedback.corrected_answer:
        parts.append(f"Respuesta corregida: {feedback.corrected_answer}")
    elif feedback.feedback_text:
        parts.append(feedback.feedback_text)
    elif feedback.original_answer:
        parts.append(f"Respuesta original: {feedback.original_answer}")
    text = "\n\n".join(parts)
    return text if text else ""


def is_feedback_indexable(feedback: CIDClientFeedback) -> bool:
    if feedback.status != "approved":
        return False
    if not feedback.approved_for_memory:
        return False
    if feedback.feedback_type in NON_INDEXABLE_TYPES:
        return False
    if not build_feedback_text(feedback):
        return False
    return True


async def already_indexed(db: AsyncSession, feedback_id: str) -> bool:
    stmt = select(CIDFeedbackMemoryEntry).where(
        CIDFeedbackMemoryEntry.feedback_id == feedback_id,
        CIDFeedbackMemoryEntry.qdrant_point_id.isnot(None),
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


def compute_feedback_point_id(feedback: CIDClientFeedback) -> str:
    return _build_point_id(
        organization_id=feedback.organization_id,
        project_id=feedback.project_id,
        source_table=SOURCE_TABLE_FEEDBACK,
        source_id=feedback.id,
        chunk_index=0,
    )


class CIDFeedbackIndexingService:

    async def index_single_feedback(
        self,
        db: AsyncSession,
        feedback: CIDClientFeedback,
    ) -> dict[str, Any]:
        if not is_feedback_indexable(feedback):
            return {"indexed": False, "reason": "feedback not indexable"}

        if await already_indexed(db, feedback.id):
            return {"indexed": False, "reason": "already indexed"}

        text = build_feedback_text(feedback)
        point_id = compute_feedback_point_id(feedback)

        vector = await rag_embedding_service.embed(text)

        upserted = await qdrant_memory_service.upsert_memory(
            organization_id=feedback.organization_id,
            project_id=feedback.project_id,
            source_type=SOURCE_TYPE_FEEDBACK,
            source_id=feedback.id,
            source_table=SOURCE_TABLE_FEEDBACK,
            title=f"feedback-{feedback.feedback_type}",
            chunks=[text],
            embedding_vectors=[vector],
            tags=[feedback.feedback_type, "client_feedback"],
            metadata={
                "feedback_id": feedback.id,
                "feedback_type": feedback.feedback_type,
                "status": feedback.status,
                "approved_for_memory": feedback.approved_for_memory,
                "confidence": feedback.confidence,
            },
        )

        if upserted == 0:
            logger.error(
                "Qdrant upsert failed for feedback %s org=%s project=%s",
                feedback.id, feedback.organization_id, feedback.project_id,
            )
            return {"indexed": False, "reason": "qdrant upsert failed"}

        entry = CIDFeedbackMemoryEntry(
            id=uuid.uuid4().hex,
            feedback_id=feedback.id,
            organization_id=feedback.organization_id,
            project_id=feedback.project_id,
            source_type=SOURCE_TYPE_FEEDBACK,
            source_id=feedback.id,
            source_text=text,
            approved_for_memory=True,
            approved_by_user_id=feedback.approved_by_user_id,
            qdrant_point_id=point_id,
            indexed_at=datetime.utcnow(),
            confidence=feedback.confidence,
            metadata_json={
                "feedback_type": feedback.feedback_type,
                "status": feedback.status,
            },
        )
        db.add(entry)
        await db.commit()

        logger.info(
            "Feedback indexed org=%s project=%s feedback=%s point=%s",
            feedback.organization_id, feedback.project_id, feedback.id, point_id,
        )

        return {"indexed": True, "point_id": point_id, "entry_id": entry.id}

    async def index_approved_feedbacks(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
    ) -> dict[str, Any]:
        stmt = select(CIDClientFeedback).where(
            CIDClientFeedback.organization_id == organization_id,
            CIDClientFeedback.project_id == project_id,
            CIDClientFeedback.status == "approved",
            CIDClientFeedback.approved_for_memory == True,
        )
        result = await db.execute(stmt)
        feedbacks = list(result.scalars().all())

        results: list[dict[str, Any]] = []
        for feedback in feedbacks:
            r = await self.index_single_feedback(db, feedback)
            results.append({
                "feedback_id": feedback.id,
                "indexed": r.get("indexed", False),
                "reason": r.get("reason"),
                "point_id": r.get("point_id"),
            })

        indexed_count = sum(1 for r in results if r["indexed"])

        return {
            "organization_id": organization_id,
            "project_id": project_id,
            "total_candidates": len(feedbacks),
            "indexed_count": indexed_count,
            "results": results,
        }


cid_feedback_indexing_service = CIDFeedbackIndexingService()
