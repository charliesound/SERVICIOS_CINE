from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext
from schemas.client_feedback_schema import (
    AggregatedFeedbackResponse,
    CIDClientFeedbackCreate,
    CIDClientFeedbackResponse,
    CIDClientFeedbackUpdate,
    CIDFeedbackListResponse,
    FeedbackDeleteResponse,
    FeedbackQueryParams,
)
from services.client_feedback_service import cid_client_feedback_service

router = APIRouter(prefix="/api/v1/client-feedback", tags=["cid-feedback"])


@router.post("/", response_model=CIDClientFeedbackResponse, status_code=201)
async def create_feedback(
    data: CIDClientFeedbackCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
    _write: None = Depends(require_write_permission),
):
    feedback = await cid_client_feedback_service.create_feedback(
        db=db,
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
        data=data,
    )
    return feedback


@router.put("/{feedback_id}", response_model=CIDClientFeedbackResponse)
async def update_feedback(
    feedback_id: str,
    data: CIDClientFeedbackUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
    _write: None = Depends(require_write_permission),
):
    feedback = await cid_client_feedback_service.update_feedback(
        db=db,
        organization_id=tenant.organization_id,
        feedback_id=feedback_id,
        data=data,
    )
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.delete("/{feedback_id}", status_code=204)
async def delete_feedback(
    feedback_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
    _write: None = Depends(require_write_permission),
):
    deleted = await cid_client_feedback_service.soft_delete_feedback(
        db=db,
        organization_id=tenant.organization_id,
        feedback_id=feedback_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")


@router.get("/aggregated", response_model=AggregatedFeedbackResponse)
async def get_aggregated_feedback(
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    data = await cid_client_feedback_service.get_aggregated_feedback(
        db=db,
        organization_id=tenant.organization_id,
    )
    return AggregatedFeedbackResponse(**data)


@router.get("/{feedback_id}", response_model=CIDClientFeedbackResponse)
async def get_feedback(
    feedback_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    feedback = await cid_client_feedback_service.get_feedback(
        db=db,
        organization_id=tenant.organization_id,
        feedback_id=feedback_id,
    )
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.get("/", response_model=CIDFeedbackListResponse)
async def list_feedback(
    params: FeedbackQueryParams = Depends(),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    feedbacks, total = await cid_client_feedback_service.list_feedback(
        db=db,
        organization_id=tenant.organization_id,
        feedback_type=params.feedback_type,
        status=params.status,
        limit=params.limit,
        offset=params.offset,
    )
    return CIDFeedbackListResponse(
        feedbacks=[CIDClientFeedbackResponse.model_validate(fb) for fb in feedbacks],
        total_count=total,
        limit=params.limit,
        offset=params.offset,
    )
