import json
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.distribution import DistributionPack, PACK_TYPE
from models.producer_pitch import ProducerPitchPack
from models.budget_estimator import BudgetEstimate
from models.script_versioning import ScriptVersion
from models.storyboard import StoryboardShot
from models.production import FundingCall


async def get_active_budget(db: AsyncSession, project_id: str) -> Optional[BudgetEstimate]:
    result = await db.execute(
        select(BudgetEstimate).where(
            BudgetEstimate.project_id == project_id,
            BudgetEstimate.status == "approved",
        ).order_by(BudgetEstimate.updated_at.desc())
    )
    return result.scalar_one_or_none()


async def get_active_producer_pitch(db: AsyncSession, project_id: str) -> Optional[ProducerPitchPack]:
    result = await db.execute(
        select(ProducerPitchPack).where(
            ProducerPitchPack.project_id == project_id,
            ProducerPitchPack.status.in_(["generated", "approved"]),
        ).order_by(ProducerPitchPack.updated_at.desc())
    )
    return result.scalar_one_or_none()


async def get_active_script_version(db: AsyncSession, project_id: str) -> Optional[ScriptVersion]:
    result = await db.execute(
        select(ScriptVersion).where(
            ScriptVersion.project_id == project_id,
            ScriptVersion.status == "approved",
        ).order_by(ScriptVersion.version_number.desc())
    )
    return result.scalar_one_or_none()


async def get_storyboard_shots(db: AsyncSession, project_id: str, limit: int = 6) -> list[dict[str, Any]]:
    result = await db.execute(
        select(StoryboardShot).where(
            StoryboardShot.project_id == project_id,
            StoryboardShot.status == "approved",
        ).order_by(StoryboardShot.sort_order.asc()).limit(limit)
    )
    shots = result.scalars().all()
    return [
        {
            "shot_number": shot.shot_number,
            "description": shot.description or "",
        }
        for shot in shots
    ]


async def get_funding_count(db: AsyncSession, project_id: str) -> int:
    result = await db.execute(
        select(FundingCall).where(FundingCall.status == "active")
    )
    return len(result.scalars().all())


async def generate_distribution_pack(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    pack_type: str = "general_sales",
    created_by: Optional[str] = None,
) -> DistributionPack:
    project = await db.get(Project, project_id)
    if not project:
        raise ValueError("Project not found")

    pack = DistributionPack(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        pack_type=pack_type,
        title=f"Distribution Pack - {project.name} ({pack_type})",
        status="generated",
        created_by=created_by,
    )

    producer_pitch = await get_active_producer_pitch(db, project_id)
    if producer_pitch:
        pack.source_producer_pitch_id = producer_pitch.id
        pack.logline = producer_pitch.logline
        pack.short_synopsis = producer_pitch.short_synopsis

    script_version = await get_active_script_version(db, project_id)
    if script_version:
        pack.source_script_version_id = script_version.id
        if not pack.logline:
            pack.logline = script_version.logline
        if not pack.short_synopsis:
            pack.short_synopsis = script_version.short_synopsis

    pack.commercial_positioning = _generate_commercial_positioning(pack_type, project)
    pack.target_audience = producer_pitch.target_audience if producer_pitch else ""
    pack.comparable_titles_json = json.dumps(_get_comparables(pack_type))
    pack.release_strategy_json = json.dumps(_get_release_strategy(pack_type))
    pack.exploitation_windows_json = json.dumps(_get_exploitation_windows(pack_type))
    pack.territory_strategy_json = json.dumps(_get_territory_strategy(pack_type))
    pack.marketing_hooks_json = json.dumps(_get_marketing_hooks(pack_type))
    pack.available_materials_json = json.dumps(_get_available_materials())
    pack.technical_specs_json = json.dumps(_get_technical_specs())
    pack.sales_arguments_json = json.dumps(_get_sales_arguments(pack_type))
    pack.risks_json = json.dumps(_get_risks(pack_type))
    pack.generated_sections_json = json.dumps({
        "generated_at": datetime.utcnow().isoformat(),
        "source": "auto",
    })

    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


def _generate_commercial_positioning(pack_type: str, project: Project) -> str:
    positionings = {
        "distributor": f"Proyecto comercial para exhibición en salas. Potencial de público amplio.",
        "sales_agent": f"Proyecto con potencial internacional para agente de ventas.",
        "festival": f"Proyecto artístico para circuito de festivales.",
        "cinema": f"Proyecto para exhibición en cines independientes.",
        "platform": f"Proyecto para catálogo de streaming.",
        "general_sales": f"Paquete de ventas general para múltiples canales.",
    }
    return positionings.get(pack_type, positionings["general_sales"])


def _get_comparables(pack_type: str) -> list:
    all_comparables = [
        {"title": "Título comparable 1", "year": 2024, "box_office": "2M€", "note": "Género similar"},
        {"title": "Título comparable 2", "year": 2023, "box_office": "1.5M€", "note": "Audiencia similar"},
    ]
    return all_comparables


def _get_release_strategy(pack_type: str) -> dict:
    return {
        "phase_1": "Estreno en salas",
        "phase_2": "VOD/postventa",
        "phase_3": "Televisión",
        "phase_4": "Internacional",
    }


def _get_exploitation_windows(pack_type: str) -> list:
    return [
        {"territory": "España", "window": "Cines primero", "timing": "3 meses"},
        {"territory": "España", "window": "VOD", "timing": "mes 4"},
        {"territory": "España", "window": "TV", "timing": "mes 12"},
    ]


def _get_territory_strategy(pack_type: str) -> list:
    return [
        {"priority": "high", "territory": "España"},
        {"priority": "high", "territory": "Latinoamérica"},
        {"priority": "medium", "territory": "EEUU"},
        {"priority": "medium", "territory": "Europa"},
    ]


def _get_marketing_hooks(pack_type: str) -> list:
    hooks = [
        "Historia universal con sensibilidad local",
        "Potencial comercial demostrado",
        "Equipo técnico profesional",
    ]
    if pack_type == "festival":
        hooks.append(" singularidad artística")
    return hooks


def _get_available_materials() -> list:
    return [
        {"material": "Guión", "status": "available"},
        {"material": "Synopsis", "status": "available"},
        {"material": "Budget", "status": "available"},
        {"material": "Trailer", "status": "pending"},
        {"material": "Still photos", "status": "pending"},
        {"material": "Dossier", "status": "available"},
    ]


def _get_technical_specs() -> dict:
    return {
        "format": "DCP",
        "resolution": "4K",
        "audio": "5.1 Dolby",
        "aspect_ratio": "2.39:1",
        "runtime": "TBD",
    }


def _get_sales_arguments(pack_type: str) -> list:
    args = [
        "Proyecto con equipo profesional",
        "Género de éxito comercial",
        "Potencial de audiencia amplio",
    ]
    return args


def _get_risks(pack_type: str) -> list:
    return [
        "Dependiente de financiación",
        "Calendario sujeto a disponibilidad",
        "No garantiza aceptación por distribuidor",
    ]


async def get_distribution_pack(db: AsyncSession, pack_id: str) -> Optional[DistributionPack]:
    result = await db.execute(
        select(DistributionPack).where(DistributionPack.id == pack_id)
    )
    return result.scalar_one_or_none()


async def get_active_distribution_pack(
    db: AsyncSession,
    project_id: str,
    pack_type: Optional[str] = None,
) -> Optional[DistributionPack]:
    query = select(DistributionPack).where(
        DistributionPack.project_id == project_id,
        DistributionPack.status.in_(["generated", "approved"]),
    )
    if pack_type:
        query = query.where(DistributionPack.pack_type == pack_type)
    result = await db.execute(
        query.order_by(DistributionPack.updated_at.desc())
    )
    return result.scalar_one_or_none()


async def list_distribution_packs(db: AsyncSession, project_id: str) -> list[DistributionPack]:
    result = await db.execute(
        select(DistributionPack).where(
            DistributionPack.project_id == project_id,
        ).order_by(DistributionPack.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_distribution_pack(
    db: AsyncSession,
    pack_id: str,
    updates: dict[str, Any],
) -> DistributionPack:
    pack = await get_distribution_pack(db, pack_id)
    if not pack:
        raise ValueError("Distribution pack not found")

    allowed_fields = [
        "title", "logline", "short_synopsis", "commercial_positioning",
        "target_audience", "status",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(pack, field, updates[field])

    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


async def approve_distribution_pack(db: AsyncSession, pack_id: str) -> DistributionPack:
    pack = await get_distribution_pack(db, pack_id)
    if not pack:
        raise ValueError("Distribution pack not found")

    pack.status = "approved"
    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


async def archive_distribution_pack(db: AsyncSession, pack_id: str) -> DistributionPack:
    pack = await get_distribution_pack(db, pack_id)
    if not pack:
        raise ValueError("Distribution pack not found")

    pack.status = "archived"
    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


def export_distribution_pack_json(pack: DistributionPack) -> dict[str, Any]:
    return {
        "id": pack.id,
        "project_id": pack.project_id,
        "title": pack.title,
        "pack_type": pack.pack_type,
        "status": pack.status,
        "logline": pack.logline,
        "short_synopsis": pack.short_synopsis,
        "commercial_positioning": pack.commercial_positioning,
        "target_audience": pack.target_audience,
        "comparables": json.loads(pack.comparable_titles_json or "[]"),
        "release_strategy": json.loads(pack.release_strategy_json or "{}"),
        "exploitation_windows": json.loads(pack.exploitation_windows_json or "[]"),
        "territory_strategy": json.loads(pack.territory_strategy_json or "[]"),
        "marketing_hooks": json.loads(pack.marketing_hooks_json or "[]"),
        "available_materials": json.loads(pack.available_materials_json or "[]"),
        "technical_specs": json.loads(pack.technical_specs_json or "{}"),
        "sales_arguments": json.loads(pack.sales_arguments_json or "[]"),
        "risks": json.loads(pack.risks_json or "[]"),
    }


def export_distribution_pack_markdown(pack: DistributionPack) -> str:
    lines = [
        f"# {pack.title or 'Distribution Pack'}",
        "",
        f"**Tipo**: {pack.pack_type} | **Estado**: {pack.status}",
        "",
        "---",
        "",
        "## Logline",
        "",
        pack.logline or "_No disponible_",
        "",
        "## Sinopsis",
        "",
        pack.short_synopsis or "_No disponible_",
        "",
        "## Posicionamiento Comercial",
        "",
        pack.commercial_positioning or "_No disponible_",
        "",
        "## Público Objetivo",
        "",
        pack.target_audience or "_No definido_",
        "",
        "---",
        "",
    ]

    comparables = json.loads(pack.comparable_titles_json or "[]")
    if comparables:
        lines.extend(["## Títulos Comparables", ""])
        for comp in comparables:
            lines.append(f"- **{comp.get('title')}** ({comp.get('year')}) - {comp.get('box_office', 'N/A')}")
        lines.append("")

    territory = json.loads(pack.territory_strategy_json or "[]")
    if territory:
        lines.extend(["## Estrategia Territorial", ""])
        for t in territory:
            lines.append(f"- **{t.get('priority', 'N/A').upper()}**: {t.get('territory')}")
        lines.append("")

    windows = json.loads(pack.exploitation_windows_json or "[]")
    if windows:
        lines.extend(["## Ventanas de Explotación", ""])
        for w in windows:
            lines.append(f"- {w.get('territory')}: {w.get('window')} ({w.get('timing')})")
        lines.append("")

    materials = json.loads(pack.available_materials_json or "[]")
    if materials:
        lines.extend(["## Materiales Disponibles", ""])
        for m in materials:
            lines.append(f"- {m.get('material')}: **{m.get('status')}**")
        lines.append("")

    sales_args = json.loads(pack.sales_arguments_json or "[]")
    if sales_args:
        lines.extend(["## Argumentos de Venta", ""])
        for arg in sales_args:
            lines.append(f"- {arg}")
        lines.append("")

    risks = json.loads(pack.risks_json or "[]")
    if risks:
        lines.extend(["## Riesgos", ""])
        for risk in risks:
            lines.append(f"- {risk}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "*Este documento es herramienta de preparación comercial. No garantiza aceptación por distribuidores o plataformas.*",
        "",
    ])

    return "\n".join(lines)


distribution_pack_service = None