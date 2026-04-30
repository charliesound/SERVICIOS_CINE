from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


REGION_SCOPE_VALUES = ("spain", "europe", "iberoamerica_latam")
OPPORTUNITY_TYPE_VALUES = (
    "development",
    "co-development",
    "co-production",
    "production",
    "distribution_circulation",
    "training",
    "industry_support",
    "festival_market",
)
PHASE_VALUES = (
    "writing",
    "development",
    "production",
    "postproduction",
    "distribution",
)
STATUS_VALUES = ("open", "upcoming", "closed", "archived")


class FundingSourceCreate(BaseModel):
    name: str
    code: str
    agency_name: Optional[str] = None
    official_url: Optional[str] = None
    description: Optional[str] = None
    region_scope: str = "spain"
    country_or_program: Optional[str] = None
    verification_status: str = "official"
    is_active: bool = True


class FundingCallBase(BaseModel):
    source_id: str
    title: str
    region_scope: str
    country_or_program: str
    agency_name: str
    official_url: Optional[str] = None
    description: Optional[str] = None
    status: str = "open"
    open_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    opportunity_type: str
    phase: str
    max_award_per_project: Optional[float] = None
    total_budget_pool: Optional[float] = None
    currency: str = "EUR"
    verification_status: str = "official"
    eligibility_json: Optional[dict[str, Any] | list[Any]] = None
    requirements_json: Optional[dict[str, Any] | list[Any]] = None
    collaboration_rules_json: Optional[dict[str, Any] | list[Any]] = None
    point_system_json: Optional[dict[str, Any] | list[Any]] = None
    eligible_formats_json: Optional[dict[str, Any] | list[Any]] = None
    notes_json: Optional[dict[str, Any] | list[Any]] = None
    requirement_items: list[dict[str, Any]] = Field(default_factory=list)


class FundingCallCreate(FundingCallBase):
    pass


class FundingCallUpdate(BaseModel):
    title: Optional[str] = None
    region_scope: Optional[str] = None
    country_or_program: Optional[str] = None
    agency_name: Optional[str] = None
    official_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    open_date: Optional[datetime] = None
    close_date: Optional[datetime] = None
    opportunity_type: Optional[str] = None
    phase: Optional[str] = None
    max_award_per_project: Optional[float] = None
    total_budget_pool: Optional[float] = None
    currency: Optional[str] = None
    verification_status: Optional[str] = None
    eligibility_json: Optional[dict[str, Any] | list[Any]] = None
    requirements_json: Optional[dict[str, Any] | list[Any]] = None
    collaboration_rules_json: Optional[dict[str, Any] | list[Any]] = None
    point_system_json: Optional[dict[str, Any] | list[Any]] = None
    eligible_formats_json: Optional[dict[str, Any] | list[Any]] = None
    notes_json: Optional[dict[str, Any] | list[Any]] = None
    requirement_items: Optional[list[dict[str, Any]]] = None


class FundingSeedRequest(BaseModel):
    force: bool = False
