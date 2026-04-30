from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class JobHistory(Base):
    __tablename__ = "job_history"
    __table_args__ = (
        Index(
            "ix_job_history_org_project_created",
            "organization_id",
            "project_id",
            "created_at",
        ),
        Index("ix_job_history_job_created", "job_id", "created_at"),
        Index("ix_job_history_event_type_created", "event_type", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        String(36),
        ForeignKey("project_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(100), nullable=False)
    status_from = Column(String(50), nullable=True)
    status_to = Column(String(50), nullable=True)
    message = Column(String(500), nullable=True)
    detail = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship("Project", back_populates="job_history_entries")
    project_job = relationship("ProjectJob", back_populates="history_entries")
    creator = relationship("User", back_populates="job_history_entries")
