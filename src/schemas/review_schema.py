from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from models.review import ReviewStatus


REVIEW_STATUS_VALUES = {
    ReviewStatus.PENDING,
    ReviewStatus.NEEDS_WORK,
    ReviewStatus.APPROVED,
    ReviewStatus.REJECTED,
}


def _normalize_required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def _normalize_review_status(
    value: Optional[str], default: Optional[str] = None
) -> Optional[str]:
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized not in REVIEW_STATUS_VALUES:
        raise ValueError("Invalid review status")
    return normalized


class ReviewCreate(BaseModel):
    target_id: str
    target_type: str
    status: Optional[str] = "pending"

    @field_validator("target_id")
    @classmethod
    def validate_target_id(cls, value: str) -> str:
        return _normalize_required_text(value, "target_id")

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, value: str) -> str:
        return _normalize_required_text(value, "target_type")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_review_status(value, ReviewStatus.PENDING)


class ReviewUpdate(BaseModel):
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_review_status(value)


class CommentCreate(BaseModel):
    body: str
    author_name: Optional[str] = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        return _normalize_required_text(value, "body")

    @field_validator("author_name")
    @classmethod
    def validate_author_name(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class ApprovalDecisionCreate(BaseModel):
    status_applied: str
    rationale_note: Optional[str] = None
    author_name: Optional[str] = None

    @field_validator("status_applied")
    @classmethod
    def validate_status_applied(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in REVIEW_STATUS_VALUES:
            raise ValueError("Invalid approval decision status")
        return normalized

    @field_validator("rationale_note", "author_name")
    @classmethod
    def validate_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)


class CommentResponse(BaseModel):
    id: str
    review_id: str
    author_name: Optional[str]
    body: str
    created_at: datetime


class ApprovalDecisionResponse(BaseModel):
    id: str
    review_id: str
    author_id: Optional[str]
    author_name: Optional[str]
    status_applied: str
    rationale_note: Optional[str]
    created_at: datetime


class ReviewResponse(BaseModel):
    id: str
    project_id: str
    target_id: str
    target_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class ReviewDetailResponse(ReviewResponse):
    logs: List[ApprovalDecisionResponse] = Field(default_factory=list)
    comments: List[CommentResponse] = Field(default_factory=list)
    approval_decision: Optional[ApprovalDecisionResponse] = None


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse] = Field(default_factory=list)


class CommentListResponse(BaseModel):
    comments: List[CommentResponse] = Field(default_factory=list)
