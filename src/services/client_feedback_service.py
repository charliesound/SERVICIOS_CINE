from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.client_feedback import (
    CIDClientFeedback,
    CIDFeedbackAudit,
    CID_FEEDBACK_STATUSES,
)
from schemas.client_feedback_schema import (
    CIDClientFeedbackCreate,
    CIDClientFeedbackUpdate,
)


class CIDClientFeedbackService:

    async def create_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
        user_id: str,
        data: CIDClientFeedbackCreate,
    ) -> CIDClientFeedback:
        feedback = CIDClientFeedback(
            id=uuid.uuid4().hex,
            organization_id=organization_id,
            project_id=data.project_id,
            user_id=user_id,
            feedback_type=data.feedback_type,
            feedback_scope=data.feedback_scope or "project_feedback",
            original_question=data.original_question,
            original_answer=data.original_answer,
            corrected_answer=data.corrected_answer,
            feedback_text=data.feedback_text,
            source_ids=data.source_ids,
            source_types=data.source_types,
            approved_for_memory=data.approved_for_memory,
            confidence=data.confidence,
            model_used=data.model_used,
            prompt_version=data.prompt_version,
            answer_version=data.answer_version,
            metadata_json=data.metadata_json,
        )
        db.add(feedback)
        await self._create_audit(
            db, organization_id, data.project_id, user_id,
            feedback.id, "created", None, "pending",
        )
        await db.commit()
        await db.refresh(feedback)
        return feedback

    async def update_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
        feedback_id: str,
        data: CIDClientFeedbackUpdate,
    ) -> CIDClientFeedback | None:
        stmt = select(CIDClientFeedback).where(
            CIDClientFeedback.id == feedback_id,
            CIDClientFeedback.organization_id == organization_id,
        )
        result = await db.execute(stmt)
        feedback = result.scalar_one_or_none()
        if feedback is None:
            return None

        old_status = feedback.status
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)

        await self._create_audit(
            db, organization_id, feedback.project_id, feedback.user_id,
            feedback_id, "edited", old_status, feedback.status,
        )
        await db.commit()
        await db.refresh(feedback)
        return feedback

    async def soft_delete_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
        feedback_id: str,
    ) -> bool:
        stmt = select(CIDClientFeedback).where(
            CIDClientFeedback.id == feedback_id,
            CIDClientFeedback.organization_id == organization_id,
        )
        result = await db.execute(stmt)
        feedback = result.scalar_one_or_none()
        if feedback is None:
            return False

        old_status = feedback.status
        feedback.status = "archived"
        await self._create_audit(
            db, organization_id, feedback.project_id, feedback.user_id,
            feedback_id, "archived", old_status, "archived",
        )
        await db.commit()
        return True

    async def get_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
        feedback_id: str,
    ) -> CIDClientFeedback | None:
        stmt = select(CIDClientFeedback).where(
            CIDClientFeedback.id == feedback_id,
            CIDClientFeedback.organization_id == organization_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
        feedback_type: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CIDClientFeedback], int]:
        base = select(CIDClientFeedback).where(
            CIDClientFeedback.organization_id == organization_id,
        )
        count_base = select(func.count(CIDClientFeedback.id)).where(
            CIDClientFeedback.organization_id == organization_id,
        )

        if feedback_type:
            base = base.where(CIDClientFeedback.feedback_type == feedback_type)
            count_base = count_base.where(CIDClientFeedback.feedback_type == feedback_type)
        if status:
            base = base.where(CIDClientFeedback.status == status)
            count_base = count_base.where(CIDClientFeedback.status == status)

        total_result = await db.execute(count_base)
        total = total_result.scalar() or 0

        base = base.order_by(CIDClientFeedback.created_at.desc())
        base = base.offset(offset).limit(limit)
        result = await db.execute(base)
        feedbacks = list(result.scalars().all())

        return feedbacks, total

    async def get_aggregated_feedback(
        self,
        db: AsyncSession,
        organization_id: str,
    ) -> dict[str, Any]:
        total_result = await db.execute(
            select(func.count(CIDClientFeedback.id)).where(
                CIDClientFeedback.organization_id == organization_id,
            )
        )
        total = total_result.scalar() or 0

        status_counts: dict[str, int] = {}
        for s in CID_FEEDBACK_STATUSES:
            r = await db.execute(
                select(func.count(CIDClientFeedback.id)).where(
                    CIDClientFeedback.organization_id == organization_id,
                    CIDClientFeedback.status == s,
                )
            )
            cnt = r.scalar() or 0
            if cnt:
                status_counts[s] = cnt

        type_result = await db.execute(
            select(
                CIDClientFeedback.feedback_type,
                func.count(CIDClientFeedback.id),
            ).where(
                CIDClientFeedback.organization_id == organization_id,
            ).group_by(CIDClientFeedback.feedback_type)
        )
        type_counts = dict(type_result.all())

        return {
            "total_count": total,
            "status_counts": status_counts,
            "type_counts": type_counts,
        }

    async def _create_audit(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
        user_id: str,
        feedback_id: str | None,
        action: str,
        previous_status: str | None,
        new_status: str | None,
    ) -> CIDFeedbackAudit:
        entry = CIDFeedbackAudit(
            id=uuid.uuid4().hex,
            feedback_id=feedback_id,
            organization_id=organization_id,
            project_id=project_id,
            user_id=user_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
        )
        db.add(entry)
        return entry


cid_client_feedback_service = CIDClientFeedbackService()
