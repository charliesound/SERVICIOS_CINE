from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CRMContact(Base):
    __tablename__ = "crm_contacts"
    __table_args__ = (
        Index("ix_crm_contact_org", "organization_id"),
        Index("ix_crm_contact_type", "contact_type"),
        Index("ix_crm_contact_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    contact_type: Mapped[str] = mapped_column(String(20), default="producer")
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_name: Mapped[Optional[str]] = mapped_column(String(100))
    role_title: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    region: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    tags_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    genres_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    formats_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    source_type: Mapped[str] = mapped_column(String(20), default="manual")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CRMOpportunity(Base):
    __tablename__ = "crm_opportunities"
    __table_args__ = (
        Index("ix_crm_opp_project", "project_id"),
        Index("ix_crm_opp_contact", "contact_id"),
        Index("ix_crm_opp_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crm_contacts.id"))
    related_sales_opportunity_id: Mapped[Optional[str]] = mapped_column(String(36))
    related_funding_match_id: Mapped[Optional[str]] = mapped_column(String(36))
    opportunity_type: Mapped[str] = mapped_column(String(20), default="distribution")
    status: Mapped[str] = mapped_column(String(20), default="new")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    fit_score: Mapped[int] = mapped_column(Integer, default=0)
    pitch_pack_id: Mapped[Optional[str]] = mapped_column(String(36))
    distribution_pack_id: Mapped[Optional[str]] = mapped_column(String(36))
    next_action: Mapped[Optional[str]] = mapped_column(String(100))
    next_action_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_contact_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    owner_user_id: Mapped[Optional[str]] = mapped_column(String(36))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CRMCommunication(Base):
    __tablename__ = "crm_communications"
    __table_args__ = (
        Index("ix_crm_comm_project", "project_id"),
        Index("ix_crm_comm_opp", "opportunity_id"),
        Index("ix_crm_comm_contact", "contact_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36))
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("crm_contacts.id"), nullable=False)
    communication_type: Mapped[str] = mapped_column(String(20), default="note")
    direction: Mapped[str] = mapped_column(String(20), default="outbound")
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    attachments_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    next_action: Mapped[Optional[str]] = mapped_column(String(100))
    next_action_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CRMTask(Base):
    __tablename__ = "crm_tasks"
    __table_args__ = (
        Index("ix_crm_task_project", "project_id"),
        Index("ix_crm_task_opp", "opportunity_id"),
        Index("ix_crm_task_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36))
    contact_id: Mapped[Optional[str]] = mapped_column(String(36))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    assigned_to_user_id: Mapped[Optional[str]] = mapped_column(String(36))
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


CONTACT_TYPES = ["producer", "distributor", "sales_agent", "cinema", "platform", "festival", "investor", "institution", "other"]

OPPORTUNITY_TYPES = ["producer_pitch", "distribution", "sales_agent", "cinema", "platform", "festival", "funding", "investment", "other"]

OPPORTUNITY_STATUS = ["new", "prepared", "contacted", "follow_up", "interested", "meeting_scheduled", "negotiating", "accepted", "rejected", "closed", "archived"]

COMMUNICATION_TYPES = ["email", "call", "meeting", "note", "screening", "submission", "other"]

COMMUNICATION_DIRECTIONS = ["outbound", "inbound", "internal"]

TASK_STATUS = ["pending", "done", "cancelled"]

TASK_PRIORITIES = ["low", "medium", "high"]