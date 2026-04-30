from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RequirementChecklistItemBase(BaseModel):
    tracking_id: str
    organization_id: str
    label: str
    requirement_type: Optional[str] = None  # document, eligibility, budget, etc.
    is_fulfilled: bool = False
    auto_detected: bool = False
    linked_project_document_id: Optional[str] = None
    evidence_excerpt: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class RequirementChecklistItemCreate(RequirementChecklistItemBase):
    pass


class RequirementChecklistItemUpdate(BaseModel):
    label: Optional[str] = None
    requirement_type: Optional[str] = None
    is_fulfilled: Optional[bool] = None
    auto_detected: Optional[bool] = None
    linked_project_document_id: Optional[str] = None
    evidence_excerpt: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class RequirementChecklistItemResponse(RequirementChecklistItemBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True