import json
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.distribution import SalesTarget, ProjectSalesOpportunity, SALES_TARGET_TYPES


SAMPLE_SALES_TARGETS = [
    {
        "name": "Demo Cine Independiente",
        "target_type": "distributor",
        "country": "España",
        "region": "Iberia",
        "genres_json": ["drama", "thriller"],
        "formats_json": ["feature"],
        "source_type": "sample",
        "status": "sample",
        "notes": "Dato de ejemplo, no contacto real.",
    },
    {
        "name": "Demo Plataforma Documental",
        "target_type": "platform",
        "country": "Internacional",
        "region": "Global",
        "genres_json": ["documentary"],
        "formats_json": ["series", "feature"],
        "source_type": "sample",
        "status": "sample",
        "notes": "Dato de ejemplo, no contacto real.",
    },
    {
        "name": "Demo Festival Ópera Prima",
        "target_type": "festival",
        "country": "España",
        "region": "Europa",
        "genres_json": ["drama"],
        "formats_json": ["feature"],
        "source_type": "sample",
        "status": "sample",
        "notes": "Dato de ejemplo, no contacto real.",
    },
    {
        "name": "Demo Circuito Exhibición Educativa",
        "target_type": "cinema",
        "country": "España",
        "region": "Iberia",
        "genres_json": ["documentary", "educational"],
        "formats_json": ["feature"],
        "source_type": "sample",
        "status": "sample",
        "notes": "Dato de ejemplo, no contacto real.",
    },
]


async def create_sales_target(
    db: AsyncSession,
    organization_id: str,
    data: dict[str, Any],
) -> SalesTarget:
    target = SalesTarget(
        id=uuid.uuid4().hex,
        organization_id=organization_id,
        name=data["name"],
        target_type=data.get("target_type", "distributor"),
        country=data.get("country"),
        region=data.get("region"),
        genres_json=json.dumps(data.get("genres_json", [])),
        formats_json=json.dumps(data.get("formats_json", [])),
        contact_name=data.get("contact_name"),
        email=data.get("email"),
        website=data.get("website"),
        notes=data.get("notes"),
        source_type=data.get("source_type", "manual"),
        status=data.get("status", "active"),
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target


async def create_sample_targets(db: AsyncSession, organization_id: str) -> list[SalesTarget]:
    created = []
    for sample in SAMPLE_SALES_TARGETS:
        existing = await db.execute(
            select(SalesTarget).where(
                SalesTarget.organization_id == organization_id,
                SalesTarget.name == sample["name"],
                SalesTarget.source_type == "sample",
            )
        )
        if existing.scalar_one_or_none():
            continue

        target = await create_sales_target(db, organization_id, sample)
        created.append(target)
    return created


async def get_sales_target(db: AsyncSession, target_id: str) -> Optional[SalesTarget]:
    result = await db.execute(
        select(SalesTarget).where(SalesTarget.id == target_id)
    )
    return result.scalar_one_or_none()


async def list_sales_targets(
    db: AsyncSession,
    organization_id: str,
    target_type: Optional[str] = None,
    status: Optional[str] = None,
) -> list[SalesTarget]:
    query = select(SalesTarget).where(SalesTarget.organization_id == organization_id)

    if target_type:
        query = query.where(SalesTarget.target_type == target_type)
    if status:
        query = query.where(SalesTarget.status == status)

    result = await db.execute(query.order_by(SalesTarget.name.asc()))
    return list(result.scalars().all())


async def suggest_sales_targets_for_project(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    target_type: Optional[str] = None,
) -> list[SalesTarget]:
    await create_sample_targets(db, organization_id)

    query = select(SalesTarget).where(
        SalesTarget.organization_id == organization_id,
        SalesTarget.status.in_(["active", "sample"]),
    )

    if target_type:
        query = query.where(SalesTarget.target_type == target_type)

    result = await db.execute(query.order_by(SalesTarget.name.asc()))
    return list(result.scalars().all()[:5])


async def create_sales_opportunity(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    sales_target_id: Optional[str] = None,
    distribution_pack_id: Optional[str] = None,
    target_type: str = "distributor",
) -> ProjectSalesOpportunity:
    opp = ProjectSalesOpportunity(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        sales_target_id=sales_target_id,
        distribution_pack_id=distribution_pack_id,
        target_type=target_type,
        status="suggested",
        fit_score=50,
        fit_summary="Coincidencia basada en tipo de proyecto",
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return opp


async def get_sales_opportunity(
    db: AsyncSession,
    opportunity_id: str,
) -> Optional[ProjectSalesOpportunity]:
    result = await db.execute(
        select(ProjectSalesOpportunity).where(ProjectSalesOpportunity.id == opportunity_id)
    )
    return result.scalar_one_or_none()


async def update_sales_opportunity(
    db: AsyncSession,
    opportunity_id: str,
    updates: dict[str, Any],
) -> ProjectSalesOpportunity:
    opp = await get_sales_opportunity(db, opportunity_id)
    if not opp:
        raise ValueError("Sales opportunity not found")

    allowed_fields = [
        "status", "fit_score", "fit_summary", "recommended_pitch_angle",
        "next_action", "last_contact_at", "notes",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(opp, field, updates[field])

    opp.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(opp)
    return opp


async def list_project_sales_opportunities(
    db: AsyncSession,
    project_id: str,
) -> list[ProjectSalesOpportunity]:
    result = await db.execute(
        select(ProjectSalesOpportunity).where(
            ProjectSalesOpportunity.project_id == project_id,
        ).order_by(ProjectSalesOpportunity.fit_score.desc())
    )
    return list(result.scalars().all())


sales_target_service = None