from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from database import Base

if TYPE_CHECKING:
    from models.history import JobHistory
    from models.storage import MediaAsset
    from models.storyboard import StoryboardShot


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_plan: Mapped[Optional[str]] = mapped_column(String(50), default="free")
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    status: Mapped[Optional[str]] = mapped_column(String(50), default="active")
    script_text: Mapped[Optional[str]] = mapped_column(String(16777215), default=None)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    project_jobs: Mapped[list["ProjectJob"]] = relationship(
        "ProjectJob",
        back_populates="project",
        primaryjoin="foreign(ProjectJob.project_id) == Project.id",
    )
    job_history_entries: Mapped[list["JobHistory"]] = relationship(
        "JobHistory",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        "MediaAsset",
        back_populates="project",
        primaryjoin="foreign(MediaAsset.project_id) == Project.id",
    )
    storyboard_shots: Mapped[list["StoryboardShot"]] = relationship(
        "StoryboardShot",
        back_populates="project",
        primaryjoin="foreign(StoryboardShot.project_id) == Project.id",
        cascade="all, delete-orphan",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(8), default="user")
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    billing_plan: Mapped[Optional[str]] = mapped_column(String(50), default="free")
    program: Mapped[Optional[str]] = mapped_column(String(50), default="demo")
    signup_type: Mapped[Optional[str]] = mapped_column(String(50), default="cid_user")
    account_status: Mapped[Optional[str]] = mapped_column(String(50), default="active")
    access_level: Mapped[Optional[str]] = mapped_column(String(50), default="standard")
    cid_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    onboarding_completed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    created_project_jobs: Mapped[list["ProjectJob"]] = relationship(
        "ProjectJob",
        back_populates="creator",
        primaryjoin="foreign(ProjectJob.created_by) == User.id",
    )
    job_history_entries: Mapped[list["JobHistory"]] = relationship(
        "JobHistory",
        back_populates="creator",
    )


class ProjectJob(Base):
    __tablename__ = "project_jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    result_data: Mapped[Optional[str]] = mapped_column(String(16777215), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    progress_percent: Mapped[Optional[int]] = mapped_column(default=0, nullable=True)
    progress_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    progress_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="project_jobs",
        primaryjoin="foreign(ProjectJob.project_id) == Project.id",
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_project_jobs",
        primaryjoin="foreign(ProjectJob.created_by) == User.id",
    )
    history_entries: Mapped[list["JobHistory"]] = relationship(
        "JobHistory",
        back_populates="project_job",
        cascade="all, delete-orphan",
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        "MediaAsset",
        back_populates="project_job",
        primaryjoin="foreign(MediaAsset.job_id) == ProjectJob.id",
    )
