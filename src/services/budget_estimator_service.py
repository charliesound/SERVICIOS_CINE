"""
Budget estimator service.
Generates budgets from script text or project data.
"""

import re
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.budget_estimator import BudgetEstimate, BudgetLineItem
from models.script_versioning import ScriptVersion
from models.production import ProductionBreakdown
from services.budget_rules import (
    RULES,
    LEVEL_MULTIPLIERS,
    get_default_contingency_percent,
    CATEGORY_LABELS,
)
from models.core import Project


SCENE_PATTERN = re.compile(r'^(INT\.|EXT\.|INT/EXT\.)', re.IGNORECASE)
LOCATION_PATTERN = re.compile(r'^(INT|EXT)\.\s*([A-Z\.]+)\s*[-–—]?\s*(.+?)(?:\s*-\s*([A-Z]+))?$', re.IGNORECASE)
CHARACTER_PATTERN = re.compile(r'^[A-Z][A-Z\s]+$', re.MULTILINE)


def analyze_script_text(script_text: str) -> Dict[str, Any]:
    """Extract metrics from script text."""
    if not script_text:
        return {
            "scene_count": 0,
            "location_count": 0,
            "exterior_count": 0,
            "interior_count": 0,
            "day_count": 0,
            "night_count": 0,
            "character_count": 0,
            "extras_estimate": 0,
            "action_scenes": 0,
            "vfx_potential": 0,
        }
    
    lines = script_text.split('\n')
    scenes = []
    locations = set()
    day_scenes = 0
    night_scenes = 0
    characters = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if SCENE_PATTERN.match(line):
            scenes.append(line)
            
            loc_match = LOCATION_PATTERN.match(line)
            if loc_match:
                loc_type = loc_match.group(1).upper()
                loc_name = loc_match.group(2).strip() if loc_match.group(2) else ""
                
                if loc_type == "EXT":
                    locations.add(f"EXT:{loc_name}")
                elif loc_type == "INT":
                    locations.add(f"INT:{loc_name}")
                
                time_of_day = loc_match.group(3) if loc_match.group(3) else ""
                if "DÍA" in time_of_day.upper() or "DAY" in time_of_day.upper():
                    day_scenes += 1
                elif "NOCHE" in time_of_day.upper() or "NIGHT" in time_of_day.upper():
                    night_scenes += 1
        
        if CHARACTER_PATTERN.match(line) and len(line) < 50:
            for char in line.split():
                if char.isupper() and len(char) > 1:
                    characters.add(char)
    
    unique_locs = set()
    for loc in locations:
        loc_type, loc_name = loc.split(':', 1) if ':' in loc else ("", loc)
        if loc_name:
            unique_locs.add(loc_name)
    
    action_count = sum(1 for l in lines if 'ACCIÓN' in l.upper() or 'ACTION' in l.upper())
    
    return {
        "scene_count": len(scenes),
        "location_count": len(unique_locs),
        "exterior_count": sum(1 for l in locations if l.startswith("EXT:")),
        "interior_count": sum(1 for l in locations if l.startswith("INT:")),
        "day_count": day_scenes,
        "night_count": night_scenes,
        "character_count": len(characters),
        "extras_estimate": max(0, len(scenes) // 5),
        "action_scenes": action_count,
        "vfx_potential": action_count // 2,
    }


def estimate_jornadas(metrics: Dict[str, Any]) -> int:
    """Estimate production days from script metrics."""
    scenes = metrics.get("scene_count", 0)
    locations = metrics.get("location_count", 0)
    extras = metrics.get("extras_estimate", 0)
    
    base_days = max(1, scenes // 10)
    location_factor = 1 + (locations // 5) * 0.15
    extra_factor = 1 + (extras // 10) * 0.1
    
    return int(base_days * location_factor * extra_factor)


def generate_line_items(
    metrics: Dict[str, Any],
    level: str = "medium"
) -> List[Dict[str, Any]]:
    """Generate budget line items based on metrics."""
    multiplier = LEVEL_MULTIPLIERS.get(level, 1.0)
    
    jornadas = estimate_jornadas(metrics)
    locations = metrics.get("location_count", 1)
    characters = metrics.get("character_count", 0)
    extras = metrics.get("extras_estimate", 0)
    action_scenes = metrics.get("action_scenes", 0)
    
    items = []
    
    items.append({
        "category": "desarrollo",
        "description": "Desarrollo y derechos de guion",
        "unit": "proyecto",
        "quantity": 1,
        "unit_cost_min": 1750 * multiplier,
        "unit_cost_estimated": 2500 * multiplier,
        "unit_cost_max": 3500 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "preproducción",
        "description": "Locaciones y permisos de rodar",
        "unit": "localización",
        "quantity": max(1, locations),
        "unit_cost_min": 560 * multiplier,
        "unit_cost_estimated": 800 * multiplier,
        "unit_cost_max": 1120 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "preproducción",
        "description": "Diseño de producción y arte",
        "unit": "semana",
        "quantity": max(1, jornadas // 5),
        "unit_cost_min": 2100 * multiplier,
        "unit_cost_estimated": 3000 * multiplier,
        "unit_cost_max": 4200 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "dirección",
        "description": "Dirección artística",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 1050 * multiplier,
        "unit_cost_estimated": 1500 * multiplier,
        "unit_cost_max": 2100 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "dirección",
        "description": "Ayte. de dirección",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 280 * multiplier,
        "unit_cost_estimated": 400 * multiplier,
        "unit_cost_max": 560 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "producción",
        "description": "Producción por jornada",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 560 * multiplier,
        "unit_cost_estimated": 800 * multiplier,
        "unit_cost_max": 1120 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "producción",
        "description": "Unidad adicional-exterior",
        "unit": "jornada",
        "quantity": max(0, (locations - 1) * jornadas // 3),
        "unit_cost_min": 420 * multiplier,
        "unit_cost_estimated": 600 * multiplier,
        "unit_cost_max": 840 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    if characters > 0:
        items.append({
            "category": "reparto",
            "description": "Actor/actriz protagonista",
            "unit": "jornada",
            "quantity": max(1, min(3, characters)) * jornadas,
            "unit_cost_min": 2100 * multiplier,
            "unit_cost_estimated": 3000 * multiplier,
            "unit_cost_max": 4200 * multiplier,
            "source": "default_rule",
            "confidence": "low",
        })
    
    if characters > 3:
        items.append({
            "category": "reparto",
            "description": "Actor/actriz secundario",
            "unit": "jornada",
            "quantity": min(max(0, characters - 3), 5) * jornadas,
            "unit_cost_min": 840 * multiplier,
            "unit_cost_estimated": 1200 * multiplier,
            "unit_cost_max": 1680 * multiplier,
            "source": "default_rule",
            "confidence": "low",
        })
    
    if extras > 0:
        items.append({
            "category": "reparto",
            "description": "Figuración",
            "unit": "jornada",
            "quantity": extras * jornadas,
            "unit_cost_min": 56 * multiplier,
            "unit_cost_estimated": 80 * multiplier,
            "unit_cost_max": 112 * multiplier,
            "source": "default_rule",
            "confidence": "medium",
        })
    
    items.append({
        "category": "equipo_técnico",
        "description": "Director de Fotografía",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 840 * multiplier,
        "unit_cost_estimated": 1200 * multiplier,
        "unit_cost_max": 1680 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "equipo_técnico",
        "description": "Gaffer/eléctricos",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 350 * multiplier,
        "unit_cost_estimated": 500 * multiplier,
        "unit_cost_max": 700 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "cámara",
        "description": "Alquiler cámara y óptica",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 1050 * multiplier,
        "unit_cost_estimated": 1500 * multiplier,
        "unit_cost_max": 2100 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "cámara",
        "description": "Grip y movimiento",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 280 * multiplier,
        "unit_cost_estimated": 400 * multiplier,
        "unit_cost_max": 560 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "sonido",
        "description": "Micófono y boom",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 245 * multiplier,
        "unit_cost_estimated": 350 * multiplier,
        "unit_cost_max": 490 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "arte",
        "description": "Escenografía",
        "unit": "escena",
        "quantity": max(1, locations),
        "unit_cost_min": 840 * multiplier,
        "unit_cost_estimated": 1200 * multiplier,
        "unit_cost_max": 1680 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    if characters > 0:
        items.append({
            "category": "vestuario",
            "description": "Vestuario actores",
            "unit": "actor",
            "quantity": max(1, characters),
            "unit_cost_min": 210 * multiplier,
            "unit_cost_estimated": 300 * multiplier,
            "unit_cost_max": 420 * multiplier,
            "source": "default_rule",
            "confidence": "low",
        })
    
    items.append({
        "category": "maquillaje",
        "description": "Maquillaje y peinado",
        "unit": "jornada",
        "quantity": jornadas,
        "unit_cost_min": 280 * multiplier,
        "unit_cost_estimated": 400 * multiplier,
        "unit_cost_max": 560 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "localizaciones",
        "description": "Tasa película ubicación",
        "unit": "día",
        "quantity": jornadas,
        "unit_cost_min": 350 * multiplier,
        "unit_cost_estimated": 500 * multiplier,
        "unit_cost_max": 700 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    items.append({
        "category": "transporte",
        "description": "Furgonetas equipo",
        "unit": "día",
        "quantity": jornadas,
        "unit_cost_min": 175 * multiplier,
        "unit_cost_estimated": 250 * multiplier,
        "unit_cost_max": 350 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "alojamiento_dietas",
        "description": "Alojamiento y dietas equipo",
        "unit": "persona_día",
        "quantity": max(5, characters + 10) * jornadas,
        "unit_cost_min": 84 * multiplier,
        "unit_cost_estimated": 120 * multiplier,
        "unit_cost_max": 168 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "seguros_permisos",
        "description": "Seguro de producción",
        "unit": "proyecto",
        "quantity": 1,
        "unit_cost_min": 1750 * multiplier,
        "unit_cost_estimated": 2500 * multiplier,
        "unit_cost_max": 3500 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "seguros_permisos",
        "description": "Permisos y tasas",
        "unit": "proyecto",
        "quantity": 1,
        "unit_cost_min": 1050 * multiplier,
        "unit_cost_estimated": 1500 * multiplier,
        "unit_cost_max": 2100 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    post_weeks = max(1, jornadas // 3)
    items.append({
        "category": "postproducción_imagen",
        "description": "Montaje/Edición",
        "unit": "semana",
        "quantity": post_weeks,
        "unit_cost_min": 1750 * multiplier,
        "unit_cost_estimated": 2500 * multiplier,
        "unit_cost_max": 3500 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "postproducción_imagen",
        "description": "Gradación de color",
        "unit": "semana",
        "quantity": max(1, post_weeks // 2),
        "unit_cost_min": 2100 * multiplier,
        "unit_cost_estimated": 3000 * multiplier,
        "unit_cost_max": 4200 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    items.append({
        "category": "postproducción_sonido",
        "description": "Edición de sonido",
        "unit": "semana",
        "quantity": post_weeks,
        "unit_cost_min": 1400 * multiplier,
        "unit_cost_estimated": 2000 * multiplier,
        "unit_cost_max": 2800 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    mix_days = max(1, post_weeks)
    items.append({
        "category": "postproducción_sonido",
        "description": "Mezcla final",
        "unit": "día",
        "quantity": mix_days,
        "unit_cost_min": 1050 * multiplier,
        "unit_cost_estimated": 1500 * multiplier,
        "unit_cost_max": 2100 * multiplier,
        "source": "default_rule",
        "confidence": "medium",
    })
    
    run_time = max(80, min(120, jornadas * 4))
    items.append({
        "category": "música",
        "description": "Banda sonora original",
        "unit": "minuto",
        "quantity": run_time,
        "unit_cost_min": 350 * multiplier,
        "unit_cost_estimated": 500 * multiplier,
        "unit_cost_max": 700 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    if action_scenes > 0:
        items.append({
            "category": "vfx_ia",
            "description": "VFX básico (acciones)",
            "unit": "shot",
            "quantity": action_scenes,
            "unit_cost_min": 210 * multiplier,
            "unit_cost_estimated": 300 * multiplier,
            "unit_cost_max": 420 * multiplier,
            "source": "default_rule",
            "confidence": "medium",
        })
    
    items.append({
        "category": "marketing",
        "description": "Material promocional",
        "unit": "proyecto",
        "quantity": 1,
        "unit_cost_min": 2100 * multiplier,
        "unit_cost_estimated": 3000 * multiplier,
        "unit_cost_max": 4200 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    items.append({
        "category": "distribución",
        "description": "Entrada festivales",
        "unit": "proyecto",
        "quantity": 1,
        "unit_cost_min": 1400 * multiplier,
        "unit_cost_estimated": 2000 * multiplier,
        "unit_cost_max": 2800 * multiplier,
        "source": "default_rule",
        "confidence": "low",
    })
    
    for item in items:
        item["total_min"] = item["quantity"] * item["unit_cost_min"]
        item["total_estimated"] = item["quantity"] * item["unit_cost_estimated"]
        item["total_max"] = item["quantity"] * item["unit_cost_max"]
    
    return items


def build_assumptions(metrics: Dict[str, Any], level: str) -> List[str]:
    """Build assumption notes based on script analysis."""
    assumptions = []
    
    assumptions.append(f"Estimación basada en {metrics.get('scene_count', 0)} escenas")
    assumptions.append(f"{estimate_jornadas(metrics)} jornadas de grabación estimadas")
    assumptions.append(f"{metrics.get('location_count', 0)} ubicaciones únicas")
    assumptions.append(f"{metrics.get('character_count', 0)} personajes")
    
    if metrics.get('exterior_count', 0) > metrics.get('interior_count', 0):
        assumptions.append("Mayormente exteriores - mayor producción en localizaciones")
    
    if metrics.get('night_count', 0) > metrics.get('day_count', 0):
        assumptions.append("Mayormente escenas nocturnas - lighting adicional")
    
    if level == "low":
        assumptions.append("Nivel conservador - tarifas mínimas estimadas")
    elif level == "high":
        assumptions.append("Nivel alto - tarifas elevadas para calidad")
    
    assumptions.append("Tarifas orientativas - validar con producción real")
    
    return assumptions


def build_role_summary(
    budget: BudgetEstimate,
    metrics: Dict[str, Any],
    role: str
) -> Dict[str, Any]:
    """Build role-specific summary."""
    summary = {
        "total": budget.total_estimated,
        "range": f"€{budget.total_min:,.0f} - €{budget.total_max:,.0f}",
        "contingency_percent": budget.contingency_percent,
    }
    
    if role in ["owner", "producer", "admin"]:
        summary["riesgo_financiero"] = "medio"
        if budget.total_max > budget.total_estimated * 1.3:
            summary["riesgo_financiero"] = "alto"
        if budget.total_min < budget.total_estimated * 0.7:
            summary["riesgo_financiero"] = "bajo"
        
        summary["partidas_grandes"] = [
            {"category": "reparto", "percent": 20},
            {"category": "producción", "percent": 15},
            {"category": "postproducción imagen", "percent": 15},
        ]
        
        summary["advertencias"] = []
        if budget.total_estimated > 150000:
            summary["advertencias"].append("Presupuesto elevado - requerir financiación")
        if metrics.get("night_count", 0) > metrics.get("day_count", 0):
            summary["advertencias"].append("Escenas nocturnas requieren iluminación especial")
    
    elif role == "production_manager":
        summary["jornadas_estimadas"] = estimate_jornadas(metrics)
        summary["localizaciones"] = metrics.get("location_count", 0)
        summary["necesidades_operativas"] = [
            "Coordinación de equipos múltiples" if metrics.get("location_count", 0) > 3 else "Locaciones concentradas",
            "Figuración necesaria" if metrics.get("extras_estimate", 0) > 0 else "Sin figuración",
        ]
    
    elif role == "director":
        summary["impacto_creativo"] = "medio"
        summary["secuencias_costosas"] = [
            {"type": "exteriores", "count": metrics.get("exterior_count", 0)},
            {"type": "nocturnas", "count": metrics.get("night_count", 0)},
            {"type": "acción", "count": metrics.get("action_scenes", 0)},
        ]
        summary["necesidades_visuales"] = f"VFX potencial: {metrics.get('vfx_potential', 0)} shots"
    
    elif role == "editor":
        summary["postproducción_imagen"] = "edición + color"
        summary["postproducción_sonido"] = "edición + mezcla"
        summary["vfx_ia"] = metrics.get("vfx_potential", 0)
        summary["coste_finishing"] = budget.total_estimated * 0.12
    
    elif role == "viewer":
        pass
    
    return summary


async def generate_budget_from_project(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    level: str = "medium",
    created_by: Optional[str] = None
) -> BudgetEstimate:
    """Generate budget from existing project data."""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    script_text = None
    if project and project.script_text:
        script_text = project.script_text
    
    script_version_id = None
    if not script_text:
        result = await db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id,
                ScriptVersion.status == "active"
            )
        )
        sv = result.scalars().first()
        if sv:
            script_text = sv.script_text
            script_version_id = sv.id
    
    breakdown_id = None
    result = await db.execute(
        select(ProductionBreakdown).where(
            ProductionBreakdown.project_id == project_id
        )
    )
    breakdown = result.scalars().first()
    if breakdown:
        breakdown_id = breakdown.id
    
    return await generate_budget_from_text(
        db, project_id, organization_id, script_text,
        level, created_by, script_version_id, breakdown_id
    )


async def generate_budget_from_text(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    script_text: Optional[str],
    level: str = "medium",
    created_by: Optional[str] = None,
    source_script_version_id: Optional[str] = None,
    source_breakdown_id: Optional[str] = None
) -> BudgetEstimate:
    """Generate budget from script text."""
    if not script_text:
        script_text = ""
    
    metrics = analyze_script_text(script_text)
    line_items = generate_line_items(metrics, level)
    multiplier = LEVEL_MULTIPLIERS.get(level, 1.0)
    
    total_min = sum(item["total_min"] for item in line_items)
    total_estimated = sum(item["total_estimated"] for item in line_items)
    total_max = sum(item["total_max"] for item in line_items)
    
    contingency_percent = get_default_contingency_percent(level)
    
    total_with_contingency = total_estimated * (1 + contingency_percent / 100)
    total_min_with_cont = total_min * (1 + contingency_percent / 100)
    total_max_with_cont = total_max * (1 + contingency_percent / 100)
    
    estimate = BudgetEstimate(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        source_script_version_id=source_script_version_id,
        source_breakdown_id=source_breakdown_id,
        title=f"Presupuesto estimado - {level}",
        currency="EUR",
        budget_level=level,
        status="draft",
        total_min=total_min_with_cont,
        total_estimated=total_with_contingency,
        total_max=total_max_with_cont,
        contingency_percent=contingency_percent,
        assumptions_json=build_assumptions(metrics, level),
        created_by=created_by,
    )
    db.add(estimate)
    await db.flush()
    
    for item_data in line_items:
        line_item = BudgetLineItem(
            id=uuid.uuid4().hex,
            budget_estimate_id=estimate.id,
            category=item_data["category"],
            description=item_data.get("description", ""),
            unit=item_data.get("unit"),
            quantity=item_data.get("quantity", 1),
            unit_cost_min=item_data.get("unit_cost_min", 0),
            unit_cost_estimated=item_data.get("unit_cost_estimated", 0),
            unit_cost_max=item_data.get("unit_cost_max", 0),
            total_min=item_data.get("total_min", 0),
            total_estimated=item_data.get("total_estimated", 0),
            total_max=item_data.get("total_max", 0),
            source=item_data.get("source", "default_rule"),
            confidence=item_data.get("confidence", "medium"),
        )
        db.add(line_item)
    
    summary_json = {
        "producer": build_role_summary(estimate, metrics, "producer"),
        "production_manager": build_role_summary(estimate, metrics, "production_manager"),
        "director": build_role_summary(estimate, metrics, "director"),
        "editor": build_role_summary(estimate, metrics, "editor"),
        "viewer": build_role_summary(estimate, metrics, "viewer"),
    }
    estimate.role_summaries_json = summary_json
    
    await db.commit()
    await db.refresh(estimate)
    
    return estimate


async def recalculate_budget(
    db: AsyncSession,
    budget_id: str,
    level: Optional[str] = None
) -> BudgetEstimate:
    """Recalculate an existing budget with a new level."""
    result = await db.execute(
        select(BudgetEstimate).where(BudgetEstimate.id == budget_id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise ValueError(f"Budget {budget_id} not found")
    
    new_level = level if level else budget.budget_level
    
    result = await db.execute(
        select(BudgetLineItem).where(
            BudgetLineItem.budget_estimate_id == budget_id
        )
    )
    lines = result.scalars().all()
    
    for line in lines:
        line.unit_cost_min = line.unit_cost_min * LEVEL_MULTIPLIERS.get(new_level, 1.0)
        line.unit_cost_estimated = line.unit_cost_estimated * LEVEL_MULTIPLIERS.get(new_level, 1.0)
        line.unit_cost_max = line.unit_cost_max * LEVEL_MULTIPLIERS.get(new_level, 1.0)
        line.total_min = line.quantity * line.unit_cost_min
        line.total_estimated = line.quantity * line.unit_cost_estimated
        line.total_max = line.quantity * line.unit_cost_max
    
    total_min = sum(l.total_min for l in lines)
    total_estimated = sum(l.total_estimated for l in lines)
    total_max = sum(l.total_max for l in lines)
    
    contingency = get_default_contingency_percent(new_level)
    
    budget.total_min = total_min * (1 + contingency / 100)
    budget.total_estimated = total_estimated * (1 + contingency / 100)
    budget.total_max = total_max * (1 + contingency / 100)
    budget.contingency_percent = contingency
    budget.budget_level = new_level
    
    await db.commit()
    await db.refresh(budget)
    
    return budget


async def archive_budget(db: AsyncSession, budget_id: str) -> BudgetEstimate:
    """Archive a budget."""
    result = await db.execute(
        select(BudgetEstimate).where(BudgetEstimate.id == budget_id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise ValueError(f"Budget {budget_id} not found")
    
    budget.status = "archived"
    await db.commit()
    await db.refresh(budget)
    return budget


async def get_active_budget(
    db: AsyncSession,
    project_id: str
) -> Optional[BudgetEstimate]:
    """Get the active budget for a project."""
    result = await db.execute(
        select(BudgetEstimate).where(
            BudgetEstimate.project_id == project_id,
            BudgetEstimate.status == "active"
        )
    )
    return result.scalars().first()


async def get_budget_by_id(
    db: AsyncSession,
    budget_id: str
) -> Optional[BudgetEstimate]:
    """Get a budget by ID."""
    return await db.get(BudgetEstimate, budget_id)


async def list_budgets(
    db: AsyncSession,
    project_id: str
) -> List[BudgetEstimate]:
    """List all budgets for a project."""
    result = await db.execute(
        select(BudgetEstimate).where(
            BudgetEstimate.project_id == project_id
        ).order_by(BudgetEstimate.created_at.desc())
    )
    return list(result.scalars().all())


async def get_budget_lines(
    db: AsyncSession,
    budget_id: str
) -> List[BudgetLineItem]:
    """Get all line items for a budget."""
    result = await db.execute(
        select(BudgetLineItem).where(
            BudgetLineItem.budget_estimate_id == budget_id
        )
    )
    return list(result.scalars().all())


async def get_budget_summary(db: AsyncSession, project_id: str) -> dict:
    """Get budget summary for a project (backwards compatibility)."""
    budget = await get_active_budget(db, project_id)
    if not budget:
        return {"error": "No budget found", "grand_total": 0.0}
    
    return {
        "scenario_type": budget.budget_level,
        "grand_total": budget.total_estimated,
        "total_min": budget.total_min,
        "total_max": budget.total_max,
    }


class _LegacyBudgetEstimatorService:
    @staticmethod
    async def get_budget(db: AsyncSession, project_id: str) -> dict:
        return await get_budget_summary(db, project_id)


budget_estimator_service = _LegacyBudgetEstimatorService()