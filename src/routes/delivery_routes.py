from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from models.delivery import Deliverable
from schemas.delivery_schema import (
    DeliverableCreate,
    DeliverableListResponse,
    DeliverableResponse,
    DeliverableUpdate,
)
from services.delivery_service import delivery_service


router = APIRouter(prefix="/api/delivery", tags=["delivery"])


def _deliverable_response(deliverable: Deliverable) -> DeliverableResponse:
    source_review_id = cast(
        Optional[str], getattr(deliverable, "source_review_id", None)
    )
    updated_at = cast(Optional[datetime], getattr(deliverable, "updated_at", None))
    created_at = cast(datetime, deliverable.created_at)
    payload = getattr(deliverable, "delivery_payload", None)
    return DeliverableResponse(
        id=str(deliverable.id),
        project_id=str(deliverable.project_id),
        source_review_id=str(source_review_id)
        if source_review_id is not None
        else None,
        name=cast(str, deliverable.name),
        format_type=cast(str, deliverable.format_type),
        delivery_payload=payload if isinstance(payload, dict) else {},
        status=str(deliverable.status),
        created_at=created_at,
        updated_at=updated_at or created_at,
    )


@router.get(
    "/projects/{project_id}/deliverables", response_model=DeliverableListResponse
)
async def list_deliverables(
    project_id: str, status: Optional[str] = None, db: AsyncSession = Depends(get_db)
) -> DeliverableListResponse:
    deliverables = await delivery_service.list_deliverables(db, project_id, status)
    return DeliverableListResponse(
        deliverables=[
            _deliverable_response(deliverable) for deliverable in deliverables
        ]
    )


@router.get("/deliverables/{deliverable_id}", response_model=DeliverableResponse)
async def get_deliverable_detail(
    deliverable_id: str, db: AsyncSession = Depends(get_db)
) -> DeliverableResponse:
    deliverable = await delivery_service.get_deliverable(db, deliverable_id)

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    return _deliverable_response(deliverable)


@router.get("/reviews/{review_id}/deliverable", response_model=DeliverableResponse)
async def get_deliverable_from_review(
    review_id: str, db: AsyncSession = Depends(get_db)
) -> DeliverableResponse:
    deliverable = await delivery_service.get_deliverable_by_review(db, review_id)

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found for review")

    return _deliverable_response(deliverable)


@router.post("/projects/{project_id}/deliverables", response_model=DeliverableResponse)
async def create_deliverable(
    project_id: str, deliverable: DeliverableCreate, db: AsyncSession = Depends(get_db)
) -> DeliverableResponse:
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    db_deliverable = await delivery_service.create_deliverable(
        db,
        project_id=project_id,
        source_review_id=deliverable.source_review_id,
        name=deliverable.name,
        format_type=deliverable.format_type,
        delivery_payload=deliverable.delivery_payload,
    )

    return _deliverable_response(db_deliverable)


@router.patch("/deliverables/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    deliverable_id: str, update: DeliverableUpdate, db: AsyncSession = Depends(get_db)
) -> DeliverableResponse:
    deliverable = await delivery_service.get_deliverable(db, deliverable_id)

    if deliverable is None:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if update.status is not None:
        deliverable = await delivery_service.update_status(
            db, deliverable, update.status
        )

    return _deliverable_response(deliverable)
