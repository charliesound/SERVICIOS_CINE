from datetime import datetime, timezone
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from models.review import ApprovalDecision, Review, ReviewComment
from schemas.review_schema import (
    ApprovalDecisionCreate,
    ApprovalDecisionResponse,
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    ReviewCreate,
    ReviewDetailResponse,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)
from services.review_service import review_service


router = APIRouter(prefix="/api/reviews", tags=["reviews"])


def _approval_decision_response(log: ApprovalDecision) -> ApprovalDecisionResponse:
    author_id = cast(Optional[str], getattr(log, "author_id", None))
    return ApprovalDecisionResponse(
        id=str(log.id),
        review_id=str(log.review_id),
        author_id=str(author_id) if author_id else None,
        author_name=cast(Optional[str], getattr(log, "author_name", None)),
        status_applied=str(log.status_applied),
        rationale_note=cast(Optional[str], getattr(log, "rationale_note", None)),
        created_at=cast(datetime, log.created_at),
    )


def _comment_response(comment: ReviewComment) -> CommentResponse:
    return CommentResponse(
        id=str(comment.id),
        review_id=str(comment.review_id),
        author_name=cast(Optional[str], getattr(comment, "author_name", None)),
        body=cast(str, comment.body),
        created_at=cast(datetime, comment.created_at),
    )


def _review_response(review: Review) -> ReviewResponse:
    return ReviewResponse(
        id=str(review.id),
        project_id=str(review.project_id),
        target_id=str(review.target_id),
        target_type=str(review.target_type),
        status=str(review.status),
        created_at=cast(datetime, review.created_at),
        updated_at=cast(Optional[datetime], getattr(review, "updated_at", None))
        or cast(datetime, review.created_at)
        or datetime.now(timezone.utc),
    )


@router.get("/projects/{project_id}", response_model=ReviewListResponse)
async def list_reviews(
    project_id: str,
    target_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> ReviewListResponse:
    reviews = await review_service.list_reviews(db, project_id, target_type, status)
    return ReviewListResponse(reviews=[_review_response(review) for review in reviews])


@router.get("/{review_id}", response_model=ReviewDetailResponse)
async def get_review_detail(
    review_id: str, db: AsyncSession = Depends(get_db)
) -> ReviewDetailResponse:
    review = await review_service.get_review(db, review_id)

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    logs = sorted(
        list(review.approval_decisions or []),
        key=lambda log: log.created_at or datetime.now(timezone.utc),
    )
    comments = sorted(
        list(review.comments or []),
        key=lambda comment: comment.created_at or datetime.now(timezone.utc),
    )
    latest_log = logs[-1] if logs else None

    return ReviewDetailResponse(
        **_review_response(review).model_dump(),
        logs=[_approval_decision_response(log) for log in logs],
        comments=[_comment_response(comment) for comment in comments],
        approval_decision=_approval_decision_response(latest_log)
        if latest_log
        else None,
    )


@router.post("/projects/{project_id}", response_model=ReviewResponse)
async def create_review(
    project_id: str, review: ReviewCreate, db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    db_review = await review_service.create_review(
        db,
        project_id=project_id,
        target_id=review.target_id,
        target_type=review.target_type,
        status=review.status,
    )
    return _review_response(db_review)


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review_status(
    review_id: str, update: ReviewUpdate, db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    if update.status is not None:
        review = await review_service.update_status(db, review, update.status)

    return _review_response(review)


@router.post("/{review_id}/decisions", response_model=ApprovalDecisionResponse)
async def add_decision(
    review_id: str, decision: ApprovalDecisionCreate, db: AsyncSession = Depends(get_db)
) -> ApprovalDecisionResponse:
    review_result = await db.execute(select(Review).where(Review.id == review_id))
    review = review_result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    db_decision = await review_service.add_decision(
        db,
        review,
        status_applied=decision.status_applied,
        rationale_note=decision.rationale_note,
        author_name=decision.author_name,
    )
    return _approval_decision_response(db_decision)


@router.get("/{review_id}/comments", response_model=CommentListResponse)
async def list_comments(
    review_id: str, db: AsyncSession = Depends(get_db)
) -> CommentListResponse:
    comments = await review_service.list_comments(db, review_id)
    return CommentListResponse(
        comments=[_comment_response(comment) for comment in comments]
    )


@router.post("/{review_id}/comments", response_model=CommentResponse)
async def add_comment(
    review_id: str, comment: CommentCreate, db: AsyncSession = Depends(get_db)
) -> CommentResponse:
    review_result = await db.execute(select(Review).where(Review.id == review_id))
    review = review_result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    db_comment = await review_service.add_comment(
        db,
        review_id=review_id,
        body=comment.body,
        author_name=comment.author_name,
    )
    return _comment_response(db_comment)
