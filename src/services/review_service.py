from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from models.review import Review, ApprovalDecision, ReviewComment, ReviewStatus


class ReviewService:
    REVIEW_STATUS_VALUES = {
        ReviewStatus.PENDING,
        ReviewStatus.NEEDS_WORK,
        ReviewStatus.APPROVED,
        ReviewStatus.REJECTED,
    }

    def _normalize_required_text(self, value: str, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise HTTPException(
                status_code=400, detail=f"{field_name} must not be blank"
            )
        return normalized

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def _normalize_review_status(self, value: str | None) -> str:
        normalized = (value or ReviewStatus.PENDING).strip().lower()
        if normalized not in self.REVIEW_STATUS_VALUES:
            raise HTTPException(status_code=400, detail="Invalid review status")
        return normalized

    def _normalized_target_type(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    async def list_reviews(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        target_type: str | None = None,
        status: str | None = None,
    ) -> list[Review]:
        query = select(Review).where(
            Review.project_id == project_id, Review.organization_id == organization_id
        )
        normalized_target_type = self._normalized_target_type(target_type)

        if normalized_target_type:
            query = query.where(Review.target_type == normalized_target_type)
        if status:
            query = query.where(Review.status == self._normalize_review_status(status))

        query = query.order_by(Review.created_at.desc(), Review.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_review(
        self, db: AsyncSession, review_id: str, organization_id: str
    ) -> Review | None:
        result = await db.execute(
            select(Review)
            .options(
                selectinload(Review.approval_decisions), selectinload(Review.comments)
            )
            .where(Review.id == review_id, Review.organization_id == organization_id)
        )
        return result.scalar_one_or_none()

    async def create_review(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        target_id: str,
        target_type: str,
        status: str | None = None,
    ) -> Review:
        review = Review(
            project_id=project_id,
            organization_id=organization_id,
            target_id=self._normalize_required_text(target_id, "target_id"),
            target_type=self._normalize_required_text(target_type, "target_type"),
            status=self._normalize_review_status(status),
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

    async def update_status(
        self, db: AsyncSession, review: Review, status: str
    ) -> Review:
        normalized_status = self._normalize_review_status(status)
        setattr(review, "status", normalized_status)
        await db.commit()
        await db.refresh(review)

        if normalized_status == ReviewStatus.APPROVED:
            from services.delivery_service import delivery_service

            await delivery_service.ensure_deliverable_for_approved_review(db, review)

        return review

    async def add_decision(
        self,
        db: AsyncSession,
        review: Review,
        status_applied: str,
        rationale_note: str | None,
        author_name: str | None,
    ) -> ApprovalDecision:
        normalized_status = self._normalize_review_status(status_applied)
        decision = ApprovalDecision(
            review_id=review.id,
            organization_id=review.organization_id,
            author_name=self._normalize_optional_text(author_name),
            status_applied=normalized_status,
            rationale_note=self._normalize_optional_text(rationale_note),
        )
        db.add(decision)
        setattr(review, "status", normalized_status)
        await db.commit()
        await db.refresh(decision)
        await db.refresh(review)

        if normalized_status == ReviewStatus.APPROVED:
            from services.delivery_service import delivery_service

            await delivery_service.ensure_deliverable_for_approved_review(db, review)

        return decision

    async def list_comments(
        self, db: AsyncSession, review_id: str, organization_id: str
    ) -> list[ReviewComment]:
        result = await db.execute(
            select(ReviewComment)
            .where(
                ReviewComment.review_id == review_id,
                ReviewComment.organization_id == organization_id,
            )
            .order_by(ReviewComment.created_at.asc(), ReviewComment.id.asc())
        )
        return result.scalars().all()

    async def add_comment(
        self,
        db: AsyncSession,
        review: Review,
        body: str,
        author_name: str | None,
    ) -> ReviewComment:
        comment = ReviewComment(
            review_id=review.id,
            organization_id=review.organization_id,
            body=self._normalize_required_text(body, "body"),
            author_name=self._normalize_optional_text(author_name),
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment


review_service = ReviewService()
