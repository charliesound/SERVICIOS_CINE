from __future__ import annotations

import json
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.module_access import require_module_access
from dependencies.tenant_context import (
    get_tenant_context,
    require_write_permission,
    validate_project_access,
)
from models.core import Project
from models.crm import (
    COMMUNICATION_TYPES,
    CONTACT_TYPES,
    OPPORTUNITY_STATUS,
    OPPORTUNITY_TYPES,
    CRMContact,
    CRMOpportunity,
    CRMTask,
)
from schemas.auth_schema import TenantContext
from services.crm_service import (
    create_contact,
    get_contact,
    list_contacts,
    update_contact,
    archive_contact,
    create_opportunity,
    get_opportunity,
    list_project_opportunities,
    update_opportunity,
    add_communication,
    list_communications,
    create_task,
    list_tasks,
    complete_task,
    cancel_task,
    get_crm_summary,
)


router = APIRouter(
    prefix="/api",
    tags=["commercial-crm"],
    dependencies=[
        Depends(get_tenant_context),
        Depends(require_module_access("delivery_distribution")),
    ],
)


async def _get_contact_for_tenant_or_404(
    db: AsyncSession,
    *,
    contact_id: str,
    tenant: TenantContext,
) -> CRMContact:
    contact = await get_contact(db, contact_id)
    if not contact or str(contact.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


async def _get_opportunity_for_project_or_404(
    db: AsyncSession,
    *,
    project_id: str,
    opportunity_id: str,
    tenant: TenantContext,
) -> CRMOpportunity:
    opp = await get_opportunity(db, opportunity_id)
    if (
        not opp
        or opp.project_id != project_id
        or str(opp.organization_id) != str(tenant.organization_id)
    ):
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


async def _get_task_for_project_or_404(
    db: AsyncSession,
    *,
    project_id: str,
    task_id: str,
    tenant: TenantContext,
) -> CRMTask:
    result = await db.execute(
        select(CRMTask).where(
            CRMTask.id == task_id,
            CRMTask.project_id == project_id,
            CRMTask.organization_id == tenant.organization_id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


class CRMContactCreate(BaseModel):
    contact_type: str = "producer"
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    role_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    tags_json: Optional[list] = None
    genres_json: Optional[list] = None
    formats_json: Optional[list] = None
    notes: Optional[str] = None


class CRMOpportunityCreate(BaseModel):
    contact_id: Optional[str] = None
    opportunity_type: str = "distribution"
    status: str = "new"
    priority: str = "medium"
    fit_score: int = 0
    pitch_pack_id: Optional[str] = None
    distribution_pack_id: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


class CRMCommunicationCreate(BaseModel):
    opportunity_id: Optional[str] = None
    communication_type: str = "note"
    direction: str = "outbound"
    subject: Optional[str] = None
    body: Optional[str] = None
    occurred_at: Optional[datetime] = None
    attachments_json: Optional[list] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None


class CRMTaskCreate(BaseModel):
    opportunity_id: Optional[str] = None
    contact_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_user_id: Optional[str] = None
    priority: str = "medium"


class CRMOpportunityUpdate(BaseModel):
    contact_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    fit_score: Optional[int] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None


@router.get("/crm/contacts")
async def list_crm_contacts(
    contact_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    contacts = await list_contacts(db, tenant.organization_id, contact_type, status)
    return JSONResponse(content={
        "count": len(contacts),
        "contacts": [
            {
                "id": c.id,
                "contact_type": c.contact_type,
                "company_name": c.company_name,
                "contact_name": c.contact_name,
                "email": c.email,
                "status": c.status,
            }
            for c in contacts
        ],
    })


@router.post("/crm/contacts")
async def create_crm_contact(
    payload: CRMContactCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
):
    if payload.contact_type not in CONTACT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid contact type")

    contact = await create_contact(
        db,
        tenant.organization_id,
        payload.model_dump(),
        created_by=tenant.user_id,
    )
    return JSONResponse(content={"contact_id": contact.id})


@router.get("/crm/contacts/{contact_id}")
async def get_crm_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    contact = await _get_contact_for_tenant_or_404(
        db, contact_id=contact_id, tenant=tenant
    )

    return JSONResponse(content={"contact": {
        "id": contact.id,
        "contact_type": contact.contact_type,
        "company_name": contact.company_name,
        "contact_name": contact.contact_name,
        "role_title": contact.role_title,
        "email": contact.email,
        "phone": contact.phone,
        "website": contact.website,
        "country": contact.country,
        "region": contact.region,
        "notes": contact.notes,
    }})


@router.patch("/crm/contacts/{contact_id}")
async def update_crm_contact(
    contact_id: str,
    payload: CRMContactCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
):
    await _get_contact_for_tenant_or_404(db, contact_id=contact_id, tenant=tenant)
    try:
        contact = await update_contact(db, contact_id, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"contact_id": contact.id})


@router.post("/crm/contacts/{contact_id}/archive")
async def archive_crm_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
):
    await _get_contact_for_tenant_or_404(db, contact_id=contact_id, tenant=tenant)
    try:
        contact = await archive_contact(db, contact_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"contact_id": contact.id, "status": contact.status})


@router.get("/projects/{project_id}/crm/summary")
async def get_crm_summary_endpoint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    summary = await get_crm_summary(db, project_id)
    return JSONResponse(content=summary)


@router.get("/projects/{project_id}/crm/opportunities")
async def list_crm_opportunities(
    project_id: str,
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    opps = await list_project_opportunities(db, project_id, status, priority)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(opps),
        "opportunities": [
            {
                "id": o.id,
                "contact_id": o.contact_id,
                "opportunity_type": o.opportunity_type,
                "status": o.status,
                "priority": o.priority,
                "fit_score": o.fit_score,
                "next_action": o.next_action,
                "next_action_date": o.next_action_date.isoformat() if o.next_action_date else None,
            }
            for o in opps
        ],
    })


@router.post("/projects/{project_id}/crm/opportunities")
async def create_crm_opportunity(
    project_id: str,
    payload: CRMOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    if payload.opportunity_type not in OPPORTUNITY_TYPES:
        raise HTTPException(status_code=400, detail="Invalid opportunity type")

    opp = await create_opportunity(
        db,
        project_id,
        tenant.organization_id,
        payload.contact_id,
        payload.model_dump(),
    )
    return JSONResponse(content={"opportunity_id": opp.id})


@router.get("/projects/{project_id}/crm/opportunities/{opportunity_id}")
async def get_crm_opportunity(
    project_id: str,
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    opp = await _get_opportunity_for_project_or_404(
        db,
        project_id=project_id,
        opportunity_id=opportunity_id,
        tenant=tenant,
    )

    return JSONResponse(content={"opportunity": {
        "id": opp.id,
        "contact_id": opp.contact_id,
        "opportunity_type": opp.opportunity_type,
        "status": opp.status,
        "priority": opp.priority,
        "fit_score": opp.fit_score,
        "next_action": opp.next_action,
        "notes": opp.notes,
    }})


@router.patch("/projects/{project_id}/crm/opportunities/{opportunity_id}")
async def update_crm_opportunity(
    project_id: str,
    opportunity_id: str,
    payload: CRMOpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    await _get_opportunity_for_project_or_404(
        db,
        project_id=project_id,
        opportunity_id=opportunity_id,
        tenant=tenant,
    )
    try:
        opp = await update_opportunity(db, opportunity_id, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"opportunity_id": opp.id})


@router.post("/projects/{project_id}/crm/opportunities/{opportunity_id}/status")
async def update_crm_opportunity_status(
    project_id: str,
    opportunity_id: str,
    status: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    if status not in OPPORTUNITY_STATUS:
        raise HTTPException(status_code=400, detail="Invalid status")

    await _get_opportunity_for_project_or_404(
        db,
        project_id=project_id,
        opportunity_id=opportunity_id,
        tenant=tenant,
    )

    try:
        opp = await update_opportunity(db, opportunity_id, {"status": status})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"opportunity_id": opp.id, "status": opp.status})


@router.get("/projects/{project_id}/crm/communications")
async def list_crm_communications(
    project_id: str,
    opportunity_id: Optional[str] = Query(default=None),
    contact_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    comms = await list_communications(db, project_id, opportunity_id, contact_id)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(comms),
        "communications": [
            {
                "id": c.id,
                "contact_id": c.contact_id,
                "communication_type": c.communication_type,
                "direction": c.direction,
                "subject": c.subject,
                "occurred_at": c.occurred_at.isoformat() if c.occurred_at else None,
            }
            for c in comms
        ],
    })


@router.post("/projects/{project_id}/crm/communications")
async def add_crm_communication(
    project_id: str,
    contact_id: str,
    payload: CRMCommunicationCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    if payload.communication_type not in COMMUNICATION_TYPES:
        raise HTTPException(status_code=400, detail="Invalid communication type")

    await _get_contact_for_tenant_or_404(db, contact_id=contact_id, tenant=tenant)
    if payload.opportunity_id:
        await _get_opportunity_for_project_or_404(
            db,
            project_id=project_id,
            opportunity_id=payload.opportunity_id,
            tenant=tenant,
        )

    comm = await add_communication(
        db,
        project_id,
        tenant.organization_id,
        contact_id,
        payload.model_dump(),
        created_by=tenant.user_id,
    )
    return JSONResponse(content={"communication_id": comm.id})


@router.get("/projects/{project_id}/crm/tasks")
async def list_crm_tasks(
    project_id: str,
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
):
    tasks = await list_tasks(db, project_id, status)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in tasks
        ],
    })


@router.post("/projects/{project_id}/crm/tasks")
async def create_crm_task(
    project_id: str,
    payload: CRMTaskCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    if payload.contact_id:
        await _get_contact_for_tenant_or_404(
            db, contact_id=payload.contact_id, tenant=tenant
        )
    if payload.opportunity_id:
        await _get_opportunity_for_project_or_404(
            db,
            project_id=project_id,
            opportunity_id=payload.opportunity_id,
            tenant=tenant,
        )
    task = await create_task(
        db,
        project_id,
        tenant.organization_id,
        payload.model_dump(),
        created_by=tenant.user_id,
    )
    return JSONResponse(content={"task_id": task.id})


@router.post("/projects/{project_id}/crm/tasks/{task_id}/complete")
async def complete_crm_task(
    project_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    await _get_task_for_project_or_404(
        db,
        project_id=project_id,
        task_id=task_id,
        tenant=tenant,
    )
    try:
        task = await complete_task(db, task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"task_id": task.id, "status": task.status})


@router.post("/projects/{project_id}/crm/tasks/{task_id}/cancel")
async def cancel_crm_task(
    project_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    project: Project = Depends(validate_project_access),
):
    await _get_task_for_project_or_404(
        db,
        project_id=project_id,
        task_id=task_id,
        tenant=tenant,
    )
    try:
        task = await cancel_task(db, task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"task_id": task.id, "status": task.status})
