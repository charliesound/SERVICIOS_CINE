from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OpportunityTrackingBase(BaseModel):
    project_id: str
    organization_id: str
    funding_call_id: str
    project_funding_match_id: Optional[str] = None
    status: str = "interested"  # interested, gathering_docs, ready, submitted, rejected, won, archived
    priority: Optional[str] = None  # low, medium, high
    owner_user_id: Optional[str] = None
    notes: Optional[str] = None


class OpportunityTrackingCreate(OpportunityTrackingBase):
    pass


class OpportunityTrackingUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_user_id: Optional[str] = None
    notes: Optional[str] = None


class OpportunityTrackingResponse(OpportunityTrackingBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)