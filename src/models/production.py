from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ProductionBreakdown(Base):
    __tablename__ = "production_breakdowns"
    __table_args__ = (
        Index("ix_breakdown_project_id", "project_id"),
        Index("ix_breakdown_org_project", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    script_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    breakdown_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    budget_estimate: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DepartmentLineItem(Base):
    __tablename__ = "department_line_items"
    __table_args__ = (
        Index("ix_lineitem_breakdown_id", "breakdown_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    breakdown_id: Mapped[str] = mapped_column(String(36), ForeignKey("production_breakdowns.id", ondelete="CASCADE"), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BudgetScenario(Base):
    __tablename__ = "budget_scenarios"
    __table_args__ = (
        Index("ix_budget_scenario_project_id", "project_id"),
        Index("ix_budget_scenario_breakdown_id", "breakdown_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    breakdown_id: Mapped[str] = mapped_column(String(36), ForeignKey("production_breakdowns.id", ondelete="CASCADE"), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_budget: Mapped[float] = mapped_column(Float, default=0.0)
    contingency: Mapped[float] = mapped_column(Float, default=0.0)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectBudget(Base):
    __tablename__ = "project_budgets"
    __table_args__ = (
        Index("ix_project_budget_project_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scenario_type: Mapped[str] = mapped_column(String(20), default="standard")
    grand_total: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BudgetLine(Base):
    __tablename__ = "budget_lines"
    __table_args__ = (
        Index("ix_budget_line_budget_id", "budget_id"),
        Index("ix_budget_line_section", "section"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("project_budgets.id", ondelete="CASCADE"), nullable=False)
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    is_manual_override: Mapped[bool] = mapped_column(default=False)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FundingSource(Base):
    __tablename__ = "funding_sources"
    __table_args__ = (
        Index("ix_funding_source_name", "name"),
        Index("ix_funding_source_code", "code"),
        Index("ix_funding_source_org_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    agency_name: Mapped[Optional[str]] = mapped_column(String(255))
    official_url: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    region_scope: Mapped[str] = mapped_column(String(32), nullable=False, default="spain")
    country_or_program: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    territory: Mapped[str] = mapped_column(String(50), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="institutional")
    verification_status: Mapped[str] = mapped_column(String(20), nullable=False, default="official")
    is_active: Mapped[bool] = mapped_column(default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FundingCall(Base):
    __tablename__ = "funding_calls"
    __table_args__ = (
        Index("ix_funding_call_source_id", "source_id"),
        Index("ix_funding_call_status", "status"),
        Index("ix_funding_call_region_scope", "region_scope"),
        Index("ix_funding_call_deadline", "deadline"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("funding_sources.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    region_scope: Mapped[str] = mapped_column(String(32), nullable=False, default="spain")
    country_or_program: Mapped[str] = mapped_column(String(100), nullable=False)
    agency_name: Mapped[str] = mapped_column(String(255), nullable=False)
    official_url: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    open_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    amount_range: Mapped[Optional[str]] = mapped_column(String(100))
    amount_min: Mapped[Optional[float]] = mapped_column(Float)
    amount_max: Mapped[Optional[float]] = mapped_column(Float)
    opportunity_type: Mapped[Optional[str]] = mapped_column(String(50))
    phase: Mapped[Optional[str]] = mapped_column(String(30))
    collaboration_mode: Mapped[Optional[str]] = mapped_column(String(30))
    max_award_per_project: Mapped[Optional[float]] = mapped_column(Float)
    total_budget_pool: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    territory: Mapped[str] = mapped_column(String(50), nullable=False)
    eligibility_summary: Mapped[Optional[str]] = mapped_column(Text)
    eligibility_json: Mapped[Optional[str]] = mapped_column(Text)
    requirements_json: Mapped[Optional[str]] = mapped_column(Text)
    collaboration_rules_json: Mapped[Optional[str]] = mapped_column(Text)
    point_system_json: Mapped[Optional[str]] = mapped_column(Text)
    eligible_formats_json: Mapped[Optional[str]] = mapped_column(Text)
    notes_json: Mapped[Optional[str]] = mapped_column(Text)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="open")
    verification_status: Mapped[str] = mapped_column(String(20), default="official")
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FundingRequirement(Base):
    __tablename__ = "funding_requirements"
    __table_args__ = (
        Index("ix_funding_requirement_call_id", "call_id"),
        Index("ix_funding_requirement_category", "category"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    call_id: Mapped[str] = mapped_column(String(36), ForeignKey("funding_calls.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    notes_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectFundingMatch(Base):
    __tablename__ = "project_funding_matches"
    __table_args__ = (
        Index("ix_match_project_id", "project_id"),
        Index("ix_match_project_org", "project_id", "organization_id"),
        Index("ix_match_funding_call_id", "funding_call_id"),
        Index("ix_match_matcher_job_id", "matcher_job_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    funding_call_id: Mapped[str] = mapped_column(String(36), ForeignKey("funding_calls.id"), nullable=False)
    matcher_job_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("matcher_jobs.id"), nullable=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    baseline_score: Mapped[Optional[float]] = mapped_column(Float)
    rag_enriched_score: Mapped[Optional[float]] = mapped_column(Float)
    fit_level: Mapped[Optional[str]] = mapped_column(String(20))
    fit_summary: Mapped[Optional[str]] = mapped_column(Text)
    blocking_reasons: Mapped[Optional[str]] = mapped_column(Text)
    missing_documents: Mapped[Optional[str]] = mapped_column(Text)
    recommended_actions: Mapped[Optional[str]] = mapped_column(Text)
    evidence_chunks_json: Mapped[Optional[str]] = mapped_column(Text)
    rag_rationale: Mapped[Optional[str]] = mapped_column(Text)
    rag_missing_requirements: Mapped[Optional[str]] = mapped_column(Text)
    confidence_level: Mapped[Optional[str]] = mapped_column(String(20))
    rag_confidence_level: Mapped[Optional[str]] = mapped_column(String(20))
    matcher_mode: Mapped[Optional[str]] = mapped_column(String(30), default="classic")
    evaluation_version: Mapped[Optional[str]] = mapped_column(String(20))
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PrivateFundingSource(Base):
    __tablename__ = "private_funding_sources"
    __table_args__ = (
        Index("ix_private_source_org_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    contact_info: Mapped[Optional[str]] = mapped_column(Text)
    amount_range: Mapped[Optional[str]] = mapped_column(String(100))
    eligibility_criteria: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PrivateOpportunity(Base):
    __tablename__ = "private_opportunities"
    __table_args__ = (
        Index("ix_private_opp_org_id", "organization_id"),
        Index("ix_private_opp_source_id", "source_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("private_funding_sources.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[Optional[float]] = mapped_column(Float)
    opportunity_type: Mapped[Optional[str]] = mapped_column(String(50))
    phase: Mapped[Optional[str]] = mapped_column(String(30))
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectFundingSource(Base):
    __tablename__ = "project_funding_sources"
    __table_args__ = (
        Index("ix_pfs_project_org", "project_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(20), default="projected")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OpportunityTracking(Base):
    __tablename__ = "opportunity_trackings"
    __table_args__ = (
        Index("ix_ot_project_id", "project_id"),
        Index("ix_ot_org_project", "organization_id", "project_id"),
        Index("ix_ot_funding_call", "funding_call_id"),
        Index("ix_ot_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    funding_call_id: Mapped[str] = mapped_column(String(36), ForeignKey("funding_calls.id"), nullable=False)
    project_funding_match_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("project_funding_matches.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="interested")  # interested, gathering_docs, ready, submitted, rejected, won, archived
    priority: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # low, medium, high
    owner_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RequirementChecklistItem(Base):
    __tablename__ = "requirement_checklist_items"
    __table_args__ = (
        Index("ix_rci_tracking_id", "tracking_id"),
        Index("ix_rci_org_id", "organization_id"),
        Index("ix_rci_fulfilled", "is_fulfilled"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    tracking_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunity_trackings.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # document, eligibility, budget, etc.
    is_fulfilled: Mapped[bool] = mapped_column(default=False)
    auto_detected: Mapped[bool] = mapped_column(default=False)  # Whether fulfilled status was auto-detected from docs/RAG
    linked_project_document_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Link to project_document if applicable
    evidence_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Text excerpt showing evidence
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notif_org_id", "organization_id"),
        Index("ix_notif_project_id", "project_id"),
        Index("ix_notif_tracking_id", "tracking_id"),
        Index("ix_notif_level", "level"),
        Index("ix_notif_is_read", "is_read"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tracking_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("opportunity_trackings.id", ondelete="SET NULL"), nullable=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False)  # info, warning, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
