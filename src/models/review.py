import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ReviewStatus:
    PENDING = "pending"
    NEEDS_WORK = "needs_work"
    APPROVED = "approved"
    REJECTED = "rejected"


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint(
            "length(trim(target_id)) > 0", name="ck_reviews_target_id_not_blank"
        ),
        CheckConstraint(
            "length(trim(target_type)) > 0",
            name="ck_reviews_target_type_not_blank",
        ),
        CheckConstraint(
            "status IN ('pending', 'needs_work', 'approved', 'rejected')",
            name="ck_reviews_status",
        ),
        Index(
            "ix_reviews_project_target_created_at",
            "project_id",
            "target_type",
            "created_at",
        ),
        Index(
            "ix_reviews_project_target_id_created_at",
            "project_id",
            "target_type",
            "target_id",
            "created_at",
        ),
        Index(
            "ix_reviews_project_status_created_at",
            "project_id",
            "status",
            "created_at",
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id = Column(String(36), nullable=False)
    target_type = Column(String(50), nullable=False)
    status = Column(
        String(50),
        default=ReviewStatus.PENDING,
        server_default=ReviewStatus.PENDING,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship("Project", backref="reviews")
    approval_decisions = relationship(
        "ApprovalDecision",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ApprovalDecision.created_at",
    )
    comments = relationship(
        "ReviewComment",
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ReviewComment.created_at",
    )
    deliverable = relationship(
        "Deliverable",
        back_populates="source_review",
        uselist=False,
    )


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"
    __table_args__ = (
        CheckConstraint(
            "status_applied IN ('pending', 'needs_work', 'approved', 'rejected')",
            name="ck_approval_decisions_status_applied",
        ),
        Index("ix_approval_decisions_review_created_at", "review_id", "created_at"),
        Index(
            "ix_approval_decisions_review_status_created_at",
            "review_id",
            "status_applied",
            "created_at",
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    review_id = Column(
        String(36),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_name = Column(String(100), nullable=True)
    status_applied = Column(String(50), nullable=False)
    rationale_note = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    review = relationship("Review", back_populates="approval_decisions")


class ReviewComment(Base):
    __tablename__ = "review_comments"
    __table_args__ = (
        CheckConstraint(
            "length(trim(body)) > 0", name="ck_review_comments_body_not_blank"
        ),
        Index("ix_review_comments_review_created_at", "review_id", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    review_id = Column(
        String(36),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author_name = Column(String(100), nullable=True)
    body = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    review = relationship("Review", back_populates="comments")


__all__ = [
    "Review",
    "ApprovalDecision",
    "ReviewComment",
    "ReviewStatus",
]
