from datetime import datetime, timezone
from pathlib import Path
import os
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from models.delivery import Deliverable, DeliverableStatus
from models.review import Review, ReviewStatus


class DeliveryService:
    def __init__(self, artifact_root: str = "exports") -> None:
        self.artifact_root = Path(artifact_root).resolve()
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    DELIVERABLE_STATUS_VALUES = {
        DeliverableStatus.DRAFT,
        DeliverableStatus.READY,
        DeliverableStatus.DELIVERED,
    }

    def _normalize_required_text(self, value: str, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise HTTPException(
                status_code=400, detail=f"{field_name} must not be blank"
            )
        return normalized

    def _normalize_deliverable_status(self, value: str | None) -> str:
        normalized = (value or DeliverableStatus.DRAFT).strip().lower()
        if normalized not in self.DELIVERABLE_STATUS_VALUES:
            raise HTTPException(status_code=400, detail="Invalid deliverable status")
        return normalized

    def _normalize_payload(self, payload: dict | None) -> dict:
        return dict(payload or {})

    def _normalize_source_review_id(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    async def list_deliverables(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        status: str | None = None,
        format_type: str | None = None,
    ) -> list[Deliverable]:
        query = select(Deliverable).where(
            Deliverable.project_id == project_id,
            Deliverable.organization_id == organization_id,
        )
        if status:
            query = query.where(
                Deliverable.status == self._normalize_deliverable_status(status)
            )
        if format_type:
            query = query.where(
                Deliverable.format_type == self._normalize_required_text(format_type, "format_type")
            )
        query = query.order_by(Deliverable.created_at.desc(), Deliverable.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_deliverable(
        self, db: AsyncSession, deliverable_id: str, organization_id: str
    ) -> Deliverable | None:
        result = await db.execute(
            select(Deliverable).where(
                Deliverable.id == deliverable_id,
                Deliverable.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_deliverable_by_review(
        self, db: AsyncSession, source_review_id: str, organization_id: str
    ) -> Deliverable | None:
        result = await db.execute(
            select(Deliverable)
            .where(
                Deliverable.source_review_id == source_review_id,
                Deliverable.organization_id == organization_id,
            )
            .order_by(Deliverable.created_at.asc(), Deliverable.id.asc())
            .limit(1)
        )
        return result.scalars().first()

    async def create_deliverable(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        source_review_id: str | None,
        name: str,
        format_type: str,
        delivery_payload: dict,
    ) -> Deliverable:
        normalized_source_review_id = self._normalize_source_review_id(source_review_id)

        if not normalized_source_review_id:
            raise HTTPException(
                status_code=400,
                detail="Deliverable requires source_review_id",
            )

        existing = await self.get_deliverable_by_review(
            db, normalized_source_review_id, organization_id
        )
        if existing is not None:
            return existing

        review_result = await db.execute(
            select(Review).where(
                Review.id == normalized_source_review_id,
                Review.project_id == project_id,
            )
        )
        review = review_result.scalar_one_or_none()

        if review is None:
            raise HTTPException(status_code=404, detail="Source review not found")

        review_status = str(getattr(review, "status"))
        if review_status != ReviewStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Deliverable can only be created from approved review",
            )

        deliverable = Deliverable(
            project_id=project_id,
            organization_id=organization_id,
            source_review_id=normalized_source_review_id,
            name=self._normalize_required_text(name, "name"),
            format_type=self._normalize_required_text(format_type, "format_type"),
            delivery_payload=self._normalize_payload(delivery_payload),
            status=DeliverableStatus.DRAFT,
        )
        db.add(deliverable)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            existing = await self.get_deliverable_by_review(
                db, normalized_source_review_id
            )
            if existing is not None:
                return existing
            raise

        await db.refresh(deliverable)
        return deliverable

    async def ensure_deliverable_for_approved_review(
        self, db: AsyncSession, review: Review
    ) -> Deliverable:
        review_status = str(getattr(review, "status"))
        if review_status != ReviewStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Review must be approved before generating deliverable",
            )

        existing = await self.get_deliverable_by_review(
            db, str(review.id), str(review.organization_id)
        )
        if existing is not None:
            return existing

        target_type = str(review.target_type).strip().lower()
        target_type_label = "asset" if target_type == "asset" else "assembly"
        deliverable_name = f"{target_type_label.title()} Review Output"
        format_type = "JSON" if target_type == "asset" else "FCPXML"

        return await self.create_deliverable(
            db,
            project_id=str(review.project_id),
            organization_id=str(review.organization_id),
            source_review_id=str(review.id),
            name=deliverable_name,
            format_type=format_type,
            delivery_payload={
                "source_review_id": str(review.id),
                "project_id": str(review.project_id),
                "organization_id": str(review.organization_id),
                "target_id": str(review.target_id),
                "target_type": target_type,
                "review_status": str(review.status),
                "generated_from_approval": True,
            },
        )

    async def update_status(
        self, db: AsyncSession, deliverable: Deliverable, status: str
    ) -> Deliverable:
        setattr(deliverable, "status", self._normalize_deliverable_status(status))
        await db.commit()
        await db.refresh(deliverable)
        return deliverable

    async def create_project_file_deliverable(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        name: str,
        format_type: str,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
        category: str,
        payload_extra: dict | None = None,
    ) -> Deliverable:
        normalized_name = self._normalize_required_text(name, "name")
        normalized_format_type = self._normalize_required_text(format_type, "format_type")
        normalized_file_name = self._normalize_required_text(file_name, "file_name")
        normalized_mime_type = self._normalize_required_text(mime_type, "mime_type")
        normalized_category = self._normalize_required_text(category, "category")

        storage_dir = self.artifact_root / organization_id / normalized_category
        storage_dir.mkdir(parents=True, exist_ok=True)

        safe_file_name = self._safe_file_name(normalized_file_name)
        stored_file_name = (
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_"
            f"{uuid.uuid4().hex[:12]}_{safe_file_name}"
        )
        file_path = storage_dir / stored_file_name
        file_path.write_bytes(file_bytes)

        payload = {
            "file_path": str(file_path),
            "file_name": normalized_file_name,
            "stored_file_name": stored_file_name,
            "file_size": len(file_bytes),
            "mime_type": normalized_mime_type,
            "category": normalized_category,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(self._normalize_payload(payload_extra))

        deliverable = Deliverable(
            project_id=project_id,
            organization_id=organization_id,
            source_review_id=None,
            name=normalized_name,
            format_type=normalized_format_type,
            delivery_payload=payload,
            status=DeliverableStatus.READY,
        )
        db.add(deliverable)
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            if file_path.exists():
                file_path.unlink()
            raise

        await db.refresh(deliverable)
        return deliverable

    def _safe_file_name(self, file_name: str) -> str:
        sanitized = os.path.basename(file_name).replace(" ", "_")
        return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in sanitized)


delivery_service = DeliveryService()
