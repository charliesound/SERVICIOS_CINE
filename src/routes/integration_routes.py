from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request

from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.integration_schema import (
    IntegrationEventPayload,
    N8NStatusResponse,
    N8NTestRequest,
    N8NTestResponse,
)
from services.n8n_webhook_service import n8n_webhook_service


router = APIRouter(prefix="/api/integrations", tags=["integrations"])


def _resolve_trace_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or uuid.uuid4().hex


@router.get("/n8n/status", response_model=N8NStatusResponse)
async def get_n8n_status(
    request: Request,
    tenant: TenantContext = Depends(get_tenant_context),
) -> N8NStatusResponse:
    del tenant
    return await n8n_webhook_service.get_status(trace_id=_resolve_trace_id(request))


@router.post("/n8n/test", response_model=N8NTestResponse)
async def send_n8n_test_event(
    payload: N8NTestRequest,
    request: Request,
    tenant: TenantContext = Depends(get_tenant_context),
) -> N8NTestResponse:
    event = IntegrationEventPayload(
        event_type=payload.event_type,
        trace_id=_resolve_trace_id(request),
        project_id=payload.project_id,
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
        message=payload.message,
        payload=payload.payload,
    )
    return await n8n_webhook_service.send_test_event(event)
