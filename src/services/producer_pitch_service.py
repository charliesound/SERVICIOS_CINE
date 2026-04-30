import json
import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.producer_pitch import ProducerPitchPack, ProducerPitchSection, PITCH_PACK_STATUSES, SECTION_ORDER
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


async def get_active_script_version(db: AsyncSession, project_id: str) -> Optional[ScriptVersion]:
    result = await db.execute(
        select(ScriptVersion).where(
            ScriptVersion.project_id == project_id,
            ScriptVersion.status == "approved",
        ).order_by(ScriptVersion.version_number.desc())
    )
    return result.scalar_one_or_none()


async def get_storyboard_selection(db: AsyncSession, project_id: str, limit: int = 6) -> list[dict[str, Any]]:
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
            "camera_angle": shot.camera_angle or "",
            "shot_type": shot.shot_type or "",
        }
        for shot in shots
    ]


async def get_active_funding_summary(db: AsyncSession, project_id: str) -> dict[str, Any]:
    result = await db.execute(
        select(FundingCall).where(
            FundingCall.status == "active",
        )
    )
    calls = result.scalars().all()
    active_count = len(calls)
    return {
        "total_opportunities": active_count,
        "message": f"{active_count} oportunidades disponibles" if active_count > 0 else "Sin oportunidades activas",
    }


def extract_logline_from_script(script_text: str) -> str:
    if not script_text:
        return ""
    lines = [l.strip() for l in script_text.split("\n") if l.strip()]
    if len(lines) >= 3:
        return f"{lines[0]} ... {lines[1]} ... {lines[2][:100]}"
    elif lines:
        return lines[0][:200]
    return ""


def extract_short_synopsis(script_text: str, max_length: int = 300) -> str:
    if not script_text:
        return ""
    text = " ".join(script_text.split())[:max_length]
    return text + "..." if len(script_text) > max_length else text


def extract_long_synopsis(script_text: str) -> str:
    if not script_text:
        return ""
    return script_text[:3000] if len(script_text) > 3000 else script_text


async def create_pitch_pack(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    created_by: Optional[str] = None,
) -> ProducerPitchPack:
    pack = ProducerPitchPack(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        status="draft",
        created_by=created_by,
    )
    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


async def generate_pitch_pack(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    created_by: Optional[str] = None,
) -> ProducerPitchPack:
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    pack = ProducerPitchPack(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        title=f"Pitch Pack - {project.name}",
        status="generated",
        created_by=created_by,
    )

    script_version = await get_active_script_version(db, project_id)
    if script_version:
        pack.source_script_version_id = script_version.id
        pack.logline = script_version.logline or extract_logline_from_script(script_version.script_text or "")
        pack.short_synopsis = script_version.short_synopsis or extract_short_synopsis(script_version.script_text or "")
        pack.long_synopsis = script_version.long_synopsis or extract_long_synopsis(script_version.script_text or "")
        pack.intention_note = script_version.intention_note or ""
        pack.genre = script_version.genre or ""
        pack.format = script_version.format or ""
        pack.tone = script_version.tone or ""
        pack.target_audience = script_version.target_audience or ""
    else:
        pack.logline = extract_logline_from_script(project.script_text or "")
        pack.short_synopsis = extract_short_synopsis(project.script_text or "")

    budget = await get_active_budget(db, project_id)
    if budget:
        pack.source_budget_id = budget.id
        pack.budget_summary_json = json.dumps({
            "total_estimated": budget.total_estimated,
            "currency": budget.currency,
            "budget_level": budget.budget_level,
            "status": budget.status,
        })

    storyboard_selection = await get_storyboard_selection(db, project_id)
    if storyboard_selection:
        pack.storyboard_selection_json = json.dumps(storyboard_selection)

    funding_summary = await get_active_funding_summary(db, project_id)
    pack.funding_summary_json = json.dumps(funding_summary)

    pack.commercial_strengths_json = json.dumps([
        "Proyecto con potencial comercial",
        "Historia universal con sensibilidad local",
    ])

    pack.production_needs_json = json.dumps([
        "Equipo técnico completo",
        "Locaciones por definir",
        "Distribución por confirmar",
    ])

    pack.risks_json = json.dumps([
        "Dependiente de financiación",
        "Calendario sujeto a disponibilidad",
    ])

    pack.generated_sections_json = json.dumps({
        "generated_at": datetime.utcnow().isoformat(),
        "source": "auto",
    })

    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


async def get_pitch_pack(db: AsyncSession, pack_id: str) -> Optional[ProducerPitchPack]:
    result = await db.execute(
        select(ProducerPitchPack).where(ProducerPitchPack.id == pack_id)
    )
    return result.scalar_one_or_none()


async def get_active_pitch_pack(db: AsyncSession, project_id: str) -> Optional[ProducerPitchPack]:
    result = await db.execute(
        select(ProducerPitchPack).where(
            ProducerPitchPack.project_id == project_id,
            ProducerPitchPack.status.in_(["draft", "generated", "approved"]),
        ).order_by(ProducerPitchPack.updated_at.desc())
    )
    return result.scalar_one_or_none()


async def list_pitch_packs(db: AsyncSession, project_id: str) -> list[ProducerPitchPack]:
    result = await db.execute(
        select(ProducerPitchPack).where(
            ProducerPitchPack.project_id == project_id,
        ).order_by(ProducerPitchPack.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_pitch_pack(
    db: AsyncSession,
    pack_id: str,
    updates: dict[str, Any],
) -> ProducerPitchPack:
    pack = await get_pitch_pack(db, pack_id)
    if not pack:
        raise ValueError("Pitch pack not found")

    allowed_fields = [
        "title", "logline", "short_synopsis", "long_synopsis", "intention_note",
        "genre", "format", "tone", "target_audience", "status",
    ]
    for field in allowed_fields:
        if field in updates:
            setattr(pack, field, updates[field])

    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


async def approve_pitch_pack(db: AsyncSession, pack_id: str) -> ProducerPitchPack:
    pack = await get_pitch_pack(db, pack_id)
    if not pack:
        raise ValueError("Pitch pack not found")

    pack.status = "approved"
    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


async def archive_pitch_pack(db: AsyncSession, pack_id: str) -> ProducerPitchPack:
    pack = await get_pitch_pack(db, pack_id)
    if not pack:
        raise ValueError("Pitch pack not found")

    pack.status = "archived"
    pack.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(pack)
    return pack


def export_pitch_json(pack: ProducerPitchPack) -> dict[str, Any]:
    return {
        "id": pack.id,
        "project_id": pack.project_id,
        "title": pack.title,
        "status": pack.status,
        "logline": pack.logline,
        "short_synopsis": pack.short_synopsis,
        "long_synopsis": pack.long_synopsis,
        "intention_note": pack.intention_note,
        "genre": pack.genre,
        "format": pack.format,
        "tone": pack.tone,
        "target_audience": pack.target_audience,
        "commercial_strengths": json.loads(pack.commercial_strengths_json or "[]"),
        "production_needs": json.loads(pack.production_needs_json or "[]"),
        "budget_summary": json.loads(pack.budget_summary_json or "{}"),
        "funding_summary": json.loads(pack.funding_summary_json or "{}"),
        "storyboard_selection": json.loads(pack.storyboard_selection_json or "[]"),
        "risks": json.loads(pack.risks_json or "[]"),
        "generated_at": pack.created_at.isoformat() if pack.created_at else None,
        "updated_at": pack.updated_at.isoformat() if pack.updated_at else None,
    }


def export_pitch_markdown(pack: ProducerPitchPack) -> str:
    lines = [
        f"# {pack.title or 'Pitch Pack'}",
        "",
        f"**Estado**: {pack.status}",
        "",
        "---",
        "",
        "## Logline",
        "",
        pack.logline or "_No disponible_",
        "",
        "## Sinopsis Corta",
        "",
        pack.short_synopsis or "_No disponible_",
        "",
        "## Sinopsis Larga",
        "",
        pack.long_synopsis or "_No disponible_",
        "",
        "## Nota de Intención",
        "",
        pack.intention_note or "_No disponible_",
        "",
        "---",
        "",
        "## Género / Formato",
        "",
        f"**Género**: {pack.genre or 'N/A'} | **Formato**: {pack.format or 'N/A'} | **Tono**: {pack.tone or 'N/A'}",
        "",
        "## Público Objetivo",
        "",
        pack.target_audience or "_No definido_",
        "",
        "---",
        "",
    ]

    commercial_strengths = json.loads(pack.commercial_strengths_json or "[]")
    if commercial_strengths:
        lines.extend([
            "## Fortalezas Comerciales",
            "",
        ])
        for strength in commercial_strengths:
            lines.append(f"- {strength}")
        lines.append("")

    production_needs = json.loads(pack.production_needs_json or "[]")
    if production_needs:
        lines.extend([
            "## Necesidades de Producción",
            "",
        ])
        for need in production_needs:
            lines.append(f"- {need}")
        lines.append("")

    budget_summary = json.loads(pack.budget_summary_json or "{}")
    if budget_summary:
        lines.extend([
            "## Resumen de Presupuesto",
            "",
            f"- **Total**: {budget_summary.get('total_estimated', 0):,.0f} {budget_summary.get('currency', 'EUR')}",
            f"- **Nivel**: {budget_summary.get('budget_level', 'N/A')}",
            "",
        ])

    funding_summary = json.loads(pack.funding_summary_json or "{}")
    if funding_summary:
        lines.extend([
            "## Ayudas/Funding",
            "",
            f"- {funding_summary.get('message', 'Sin información')}",
            "",
        ])

    storyboard_selection = json.loads(pack.storyboard_selection_json or "[]")
    if storyboard_selection:
        lines.extend([
            "## Selección de Storyboard",
            "",
        ])
        for shot in storyboard_selection[:6]:
            lines.append(f"- Shot {shot.get('shot_number')}: {shot.get('description', '')[:80]}")
        lines.append("")

    risks = json.loads(pack.risks_json or "[]")
    if risks:
        lines.extend([
            "## Riesgos",
            "",
        ])
        for risk in risks:
            lines.append(f"- {risk}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "*Documento de trabajo para pitching. Revisar antes de enviar.*",
        "",
    ])

    return "\n".join(lines)


producer_pitch_service = None