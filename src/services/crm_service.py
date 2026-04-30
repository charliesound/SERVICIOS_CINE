import json
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.crm import CRMContact, CRMOpportunity, CRMCommunication, CRMTask, OPPORTUNITY_STATUS


async def create_contact(
    db: AsyncSession,
    organization_id: str,
    data: dict[str, Any],
    created_by: Optional[str] = None,
) -> CRMContact:
    contact = CRMContact(
        id=uuid.uuid4().hex,
        organization_id=organization_id,
        contact_type=data.get("contact_type", "producer"),
        company_name=data.get("company_name"),
        contact_name=data.get("contact_name"),
        role_title=data.get("role_title"),
        email=data.get("email"),
        phone=data.get("phone"),
        website=data.get("website"),
        country=data.get("country"),
        region=data.get("region"),
        city=data.get("city"),
        tags_json=json.dumps(data.get("tags_json", [])),
        genres_json=json.dumps(data.get("genres_json", [])),
        formats_json=json.dumps(data.get("formats_json", [])),
        source_type=data.get("source_type", "manual"),
        notes=data.get("notes"),
        created_by=created_by,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contact(db: AsyncSession, contact_id: str) -> Optional[CRMContact]:
    result = await db.execute(
        select(CRMContact).where(CRMContact.id == contact_id)
    )
    return result.scalar_one_or_none()


async def list_contacts(
    db: AsyncSession,
    organization_id: str,
    contact_type: Optional[str] = None,
    status: Optional[str] = None,
) -> list[CRMContact]:
    query = select(CRMContact).where(CRMContact.organization_id == organization_id)
    if contact_type:
        query = query.where(CRMContact.contact_type == contact_type)
    if status:
        query = query.where(CRMContact.status == status)
    result = await db.execute(query.order_by(CRMContact.company_name.asc()))
    return list(result.scalars().all())


async def update_contact(
    db: AsyncSession,
    contact_id: str,
    updates: dict[str, Any],
) -> CRMContact:
    contact = await get_contact(db, contact_id)
    if not contact:
        raise ValueError("Contact not found")

    allowed_fields = [
        "contact_type", "company_name", "contact_name", "role_title",
        "email", "phone", "website", "country", "region", "city",
        "tags_json", "genres_json", "formats_json", "notes", "status",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(contact, field, updates[field])

    contact.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(contact)
    return contact


async def archive_contact(db: AsyncSession, contact_id: str) -> CRMContact:
    contact = await get_contact(db, contact_id)
    if not contact:
        raise ValueError("Contact not found")

    contact.status = "archived"
    contact.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(contact)
    return contact


async def create_opportunity(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    contact_id: Optional[str],
    data: dict[str, Any],
) -> CRMOpportunity:
    opp = CRMOpportunity(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        contact_id=contact_id,
        opportunity_type=data.get("opportunity_type", "distribution"),
        status=data.get("status", "new"),
        priority=data.get("priority", "medium"),
        fit_score=data.get("fit_score", 0),
        pitch_pack_id=data.get("pitch_pack_id"),
        distribution_pack_id=data.get("distribution_pack_id"),
        next_action=data.get("next_action"),
        next_action_date=data.get("next_action_date"),
        notes=data.get("notes"),
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return opp


async def get_opportunity(db: AsyncSession, opportunity_id: str) -> Optional[CRMOpportunity]:
    result = await db.execute(
        select(CRMOpportunity).where(CRMOpportunity.id == opportunity_id)
    )
    return result.scalar_one_or_none()


async def list_project_opportunities(
    db: AsyncSession,
    project_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> list[CRMOpportunity]:
    query = select(CRMOpportunity).where(CRMOpportunity.project_id == project_id)
    if status:
        query = query.where(CRMOpportunity.status == status)
    if priority:
        query = query.where(CRMOpportunity.priority == priority)
    result = await db.execute(query.order_by(CRMOpportunity.priority.desc(), CRMOpportunity.updated_at.desc()))
    return list(result.scalars().all())


async def update_opportunity(
    db: AsyncSession,
    opportunity_id: str,
    updates: dict[str, Any],
) -> CRMOpportunity:
    opp = await get_opportunity(db, opportunity_id)
    if not opp:
        raise ValueError("Opportunity not found")

    allowed_fields = [
        "contact_id", "opportunity_type", "status", "priority", "fit_score",
        "pitch_pack_id", "distribution_pack_id", "next_action", "next_action_date",
        "notes",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(opp, field, updates[field])

    opp.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(opp)
    return opp


async def add_communication(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    contact_id: str,
    data: dict[str, Any],
    created_by: Optional[str] = None,
) -> CRMCommunication:
    comm = CRMCommunication(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        contact_id=contact_id,
        opportunity_id=data.get("opportunity_id"),
        communication_type=data.get("communication_type", "note"),
        direction=data.get("direction", "outbound"),
        subject=data.get("subject"),
        body=data.get("body"),
        occurred_at=data.get("occurred_at") or datetime.utcnow(),
        created_by=created_by,
        attachments_json=json.dumps(data.get("attachments_json", [])),
        next_action=data.get("next_action"),
        next_action_date=data.get("next_action_date"),
    )
    db.add(comm)
    await db.commit()
    await db.refresh(comm)
    return comm


async def list_communications(
    db: AsyncSession,
    project_id: str,
    opportunity_id: Optional[str] = None,
    contact_id: Optional[str] = None,
) -> list[CRMCommunication]:
    query = select(CRMCommunication).where(CRMCommunication.project_id == project_id)
    if opportunity_id:
        query = query.where(CRMCommunication.opportunity_id == opportunity_id)
    if contact_id:
        query = query.where(CRMCommunication.contact_id == contact_id)
    result = await db.execute(query.order_by(CRMCommunication.occurred_at.desc()))
    return list(result.scalars().all())


async def create_task(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    data: dict[str, Any],
    created_by: Optional[str] = None,
) -> CRMTask:
    task = CRMTask(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        opportunity_id=data.get("opportunity_id"),
        contact_id=data.get("contact_id"),
        title=data["title"],
        description=data.get("description"),
        due_date=data.get("due_date"),
        assigned_to_user_id=data.get("assigned_to_user_id"),
        priority=data.get("priority", "medium"),
        created_by=created_by,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def list_tasks(
    db: AsyncSession,
    project_id: str,
    status: Optional[str] = None,
) -> list[CRMTask]:
    query = select(CRMTask).where(CRMTask.project_id == project_id)
    if status:
        query = query.where(CRMTask.status == status)
    result = await db.execute(query.order_by(CRMTask.due_date.asc(), CRMTask.priority.desc()))
    return list(result.scalars().all())


async def complete_task(db: AsyncSession, task_id: str) -> CRMTask:
    from sqlalchemy import select
    result = await db.execute(select(CRMTask).where(CRMTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    task.status = "done"
    task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task


async def cancel_task(db: AsyncSession, task_id: str) -> CRMTask:
    from sqlalchemy import select
    result = await db.execute(select(CRMTask).where(CRMTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    task.status = "cancelled"
    await db.commit()
    await db.refresh(task)
    return task


async def get_crm_summary(db: AsyncSession, project_id: str) -> dict[str, Any]:
    opp_result = await db.execute(
        select(CRMOpportunity).where(CRMOpportunity.project_id == project_id)
    )
    opps = list(opp_result.scalars().all())

    task_result = await db.execute(
        select(CRMTask).where(CRMTask.project_id == project_id, CRMTask.status == "pending")
    )
    tasks = list(task_result.scalar_one_or_none() or [])

    status_counts = {}
    for status in OPPORTUNITY_STATUS:
        status_counts[status] = sum(1 for o in opps if o.status == status)

    return {
        "total_opportunities": len(opps),
        "total_tasks": len(tasks),
        "opportunities_by_status": status_counts,
        "interested_count": status_counts.get("interested", 0),
        "pending_count": status_counts.get("follow_up", 0) + status_counts.get("new", 0),
    }


crm_service = None