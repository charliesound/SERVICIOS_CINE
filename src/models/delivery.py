from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base
from models.review import Review


def generate_uuid() -> str:
    import uuid

    return str(uuid.uuid4())


class DeliverableStatus:
    DRAFT = "draft"
    READY = "ready"
    DELIVERED = "delivered"


class Deliverable(Base):
    """
    The Zenith of the App. The actual exported data bridge (e.g. FCPXML).
    """

    __tablename__ = "deliverables"
    __table_args__ = (
        UniqueConstraint("source_review_id", name="uq_deliverables_source_review_id"),
        CheckConstraint(
            "length(trim(name)) > 0", name="ck_deliverables_name_not_blank"
        ),
        CheckConstraint(
            "length(trim(format_type)) > 0",
            name="ck_deliverables_format_type_not_blank",
        ),
        CheckConstraint(
            "status IN ('draft', 'ready', 'delivered')",
            name="ck_deliverables_status",
        ),
        Index(
            "ix_deliverables_project_status_created_at",
            "project_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_deliverables_project_source_review_created_at",
            "project_id",
            "source_review_id",
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
    organization_id = Column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    source_review_id = Column(
        String(36),
        ForeignKey("reviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String(255), nullable=False)
    format_type = Column(String(50), nullable=False)
    delivery_payload = Column(JSON, nullable=False)
    status = Column(
        String(20),
        default=DeliverableStatus.DRAFT,
        server_default=DeliverableStatus.DRAFT,
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

    project = relationship("Project", backref="deliverables")
    source_review = relationship("Review", back_populates="deliverable")
