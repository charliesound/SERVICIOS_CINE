from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, field_validator

from models.delivery import DeliverableStatus


DELIVERABLE_STATUS_VALUES = {
    DeliverableStatus.DRAFT,
    DeliverableStatus.READY,
    DeliverableStatus.DELIVERED,
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


def _normalize_deliverable_status(
    value: Optional[str], default: Optional[str] = None
) -> Optional[str]:
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized not in DELIVERABLE_STATUS_VALUES:
        raise ValueError("Invalid deliverable status")
    return normalized


class DeliverableCreate(BaseModel):
    source_review_id: Optional[str] = None
    name: str
    format_type: str
    delivery_payload: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_review_id")
    @classmethod
    def validate_source_review_id(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_optional_text(value)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_required_text(value, "name")

    @field_validator("format_type")
    @classmethod
    def validate_format_type(cls, value: str) -> str:
        return _normalize_required_text(value, "format_type")


class DeliverableUpdate(BaseModel):
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        return _normalize_deliverable_status(value)


class DeliverableResponse(BaseModel):
    id: str
    project_id: str
    source_review_id: Optional[str]
    name: str
    format_type: str
    delivery_payload: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


class DeliverableListResponse(BaseModel):
    deliverables: List[DeliverableResponse] = Field(default_factory=list)
