from __future__ import annotations

import hashlib
import re
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

MEMORY_TYPE_FEEDBACK = "client_feedback"
MEMORY_TYPE_COMMON_QUESTION = "common_question"

NON_INDEXABLE_TYPES: frozenset[str] = frozenset({"source_blacklist"})


def normalize_canonical_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()


def compute_canonical_hash(text: str) -> str:
    normalized = normalize_canonical_text(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def determine_memory_type(feedback: CIDClientFeedback) -> str:
    if feedback.corrected_answer or feedback.feedback_text:
        return MEMORY_TYPE_FEEDBACK
    return MEMORY_TYPE_COMMON_QUESTION


def build_variant_questions(feedback: CIDClientFeedback) -> list[str]:
    if feedback.original_question:
        return [feedback.original_question]
    return []


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


async def find_existing_by_hash(
    db: AsyncSession,
    canonical_hash: str,
    organization_id: str,
    project_id: str,
) -> CIDFeedbackMemoryEntry | None:
    stmt = select(CIDFeedbackMemoryEntry).where(
        CIDFeedbackMemoryEntry.organization_id == organization_id,
        CIDFeedbackMemoryEntry.project_id == project_id,
        CIDFeedbackMemoryEntry.qdrant_point_id.isnot(None),
    )
    result = await db.execute(stmt)
    entries = list(result.scalars().all())
    for entry in entries:
        meta = entry.metadata_json or {}
        if meta.get("canonical_hash") == canonical_hash:
            return entry
    return None


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
        canonical_hash = compute_canonical_hash(text)
        memory_type = determine_memory_type(feedback)
        variant_questions = build_variant_questions(feedback)

        existing = await find_existing_by_hash(
            db, canonical_hash,
            feedback.organization_id, feedback.project_id,
        )
        if existing is not None and existing.qdrant_point_id:
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
                qdrant_point_id=existing.qdrant_point_id,
                indexed_at=datetime.utcnow(),
                confidence=feedback.confidence,
                metadata_json={
                    "feedback_type": feedback.feedback_type,
                    "status": feedback.status,
                    "canonical_hash": canonical_hash,
                    "memory_type": memory_type,
                    "is_duplicate": True,
                    "original_entry_id": existing.id,
                },
            )
            db.add(entry)
            await db.commit()

            logger.info(
                "Feedback dedup org=%s project=%s feedback=%s -> existing_point=%s",
                feedback.organization_id, feedback.project_id,
                feedback.id, existing.qdrant_point_id,
            )

            return {
                "indexed": True,
                "dedup": True,
                "point_id": existing.qdrant_point_id,
                "entry_id": entry.id,
            }

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
                "canonical_hash": canonical_hash,
                "memory_type": memory_type,
                "occurrence_count": 1,
                "variant_questions": variant_questions,
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
                "canonical_hash": canonical_hash,
                "memory_type": memory_type,
                "occurrence_count": 1,
                "variant_questions": variant_questions,
            },
        )
        db.add(entry)
        await db.commit()

        logger.info(
            "Feedback indexed org=%s project=%s feedback=%s point=%s",
            feedback.organization_id, feedback.project_id, feedback.id, point_id,
        )

        return {"indexed": True, "dedup": False, "point_id": point_id, "entry_id": entry.id}

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
                "dedup": r.get("dedup", False),
                "reason": r.get("reason"),
                "point_id": r.get("point_id"),
            })

        indexed_count = sum(1 for r in results if r["indexed"])
        dedup_count = sum(1 for r in results if r.get("dedup"))

        return {
            "organization_id": organization_id,
            "project_id": project_id,
            "total_candidates": len(feedbacks),
            "indexed_count": indexed_count,
            "dedup_count": dedup_count,
            "results": results,
        }


cid_feedback_indexing_service = CIDFeedbackIndexingService()
