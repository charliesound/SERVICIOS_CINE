import uuid
import re
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import BudgetEstimate, BudgetLineItem

LEVEL_MULTIPLIERS = {"low": 0.7, "medium": 1.0, "high": 1.4}
SCENE_PATTERN = re.compile(r"^(INT\.|EXT\.|INT/EXT\.)", re.IGNORECASE)
LOCATION_PATTERN = re.compile(r"^(INT|EXT)\.\s*([A-Z\.]+)\s*[-–—]?\s*(.+?)(?:\s*-\s*([A-Z]+))?$", re.IGNORECASE)
CHARACTER_PATTERN = re.compile(r"^[A-Z][A-Z\s]+$", re.MULTILINE)


def analyze_script_text(script_text: str) -> dict:
    if not script_text:
        return {"scene_count": 0, "location_count": 0, "exterior_count": 0, "interior_count": 0, "day_count": 0, "night_count": 0, "character_count": 0, "extras_estimate": 0, "action_scenes": 0, "vfx_potential": 0}
    lines = script_text.split("\n")
    scenes, locations, characters = [], set(), set()
    day_scenes = night_scenes = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if SCENE_PATTERN.match(line):
            scenes.append(line)
            m = LOCATION_PATTERN.match(line)
            if m:
                loc_type = m.group(1).upper()
                loc_name = m.group(2).strip() if m.group(2) else ""
                if loc_type == "EXT":
                    locations.add(f"EXT:{loc_name}")
                elif loc_type == "INT":
                    locations.add(f"INT:{loc_name}")
                tod = (m.group(3) or "").upper()
                if "DÍA" in tod or "DAY" in tod:
                    day_scenes += 1
                elif "NOCHE" in tod or "NIGHT" in tod:
                    night_scenes += 1
        if CHARACTER_PATTERN.match(line) and len(line) < 50:
            for ch in line.split():
                if ch.isupper() and len(ch) > 1:
                    characters.add(ch)
    unique_locs = set()
    for loc in locations:
        parts = loc.split(":", 1)
        if len(parts) > 1 and parts[1]:
            unique_locs.add(parts[1])
    action_count = sum(1 for l in lines if "ACCIÓN" in l.upper() or "ACTION" in l.upper())
    return {"scene_count": len(scenes), "location_count": len(unique_locs), "exterior_count": sum(1 for l in locations if l.startswith("EXT:")), "interior_count": sum(1 for l in locations if l.startswith("INT:")), "day_count": day_scenes, "night_count": night_scenes, "character_count": len(characters), "extras_estimate": max(0, len(scenes) // 5), "action_scenes": action_count, "vfx_potential": action_count // 2}


def estimate_jornadas(metrics: dict) -> int:
    scenes = metrics.get("scene_count", 0)
    locations = metrics.get("location_count", 0)
    extras = metrics.get("extras_estimate", 0)
    base = max(1, scenes // 10)
    loc_factor = 1 + (locations // 5) * 0.15
    extra_factor = 1 + (extras // 10) * 0.1
    return int(base * loc_factor * extra_factor)


def generate_line_items(metrics: dict, level: str = "medium") -> list[dict]:
    mult = LEVEL_MULTIPLIERS.get(level, 1.0)
    jornadas = estimate_jornadas(metrics)
    locations = metrics.get("location_count", 1)
    characters = metrics.get("character_count", 0)
    extras = metrics.get("extras_estimate", 0)
    action_scenes = metrics.get("action_scenes", 0)
    post_weeks = max(1, jornadas // 3)

    items = [
        {"category": "desarrollo", "description": "Desarrollo y derechos de guion", "unit": "proyecto", "quantity": 1, "unit_cost_min": 1750 * mult, "unit_cost_estimated": 2500 * mult, "unit_cost_max": 3500 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "preproducción", "description": "Locaciones y permisos de rodar", "unit": "localización", "quantity": max(1, locations), "unit_cost_min": 560 * mult, "unit_cost_estimated": 800 * mult, "unit_cost_max": 1120 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "preproducción", "description": "Diseño de producción y arte", "unit": "semana", "quantity": max(1, jornadas // 5), "unit_cost_min": 2100 * mult, "unit_cost_estimated": 3000 * mult, "unit_cost_max": 4200 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "dirección", "description": "Dirección artística", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 1050 * mult, "unit_cost_estimated": 1500 * mult, "unit_cost_max": 2100 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "dirección", "description": "Ayte. de dirección", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 280 * mult, "unit_cost_estimated": 400 * mult, "unit_cost_max": 560 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "producción", "description": "Producción por jornada", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 560 * mult, "unit_cost_estimated": 800 * mult, "unit_cost_max": 1120 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "producción", "description": "Unidad adicional-exterior", "unit": "jornada", "quantity": max(0, (locations - 1) * jornadas // 3), "unit_cost_min": 420 * mult, "unit_cost_estimated": 600 * mult, "unit_cost_max": 840 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "equipo_técnico", "description": "Director de Fotografía", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 840 * mult, "unit_cost_estimated": 1200 * mult, "unit_cost_max": 1680 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "equipo_técnico", "description": "Gaffer/eléctricos", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 350 * mult, "unit_cost_estimated": 500 * mult, "unit_cost_max": 700 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "cámara", "description": "Alquiler cámara y óptica", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 1050 * mult, "unit_cost_estimated": 1500 * mult, "unit_cost_max": 2100 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "cámara", "description": "Grip y movimiento", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 280 * mult, "unit_cost_estimated": 400 * mult, "unit_cost_max": 560 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "sonido", "description": "Micófono y boom", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 245 * mult, "unit_cost_estimated": 350 * mult, "unit_cost_max": 490 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "arte", "description": "Escenografía", "unit": "escena", "quantity": max(1, locations), "unit_cost_min": 840 * mult, "unit_cost_estimated": 1200 * mult, "unit_cost_max": 1680 * mult, "source": "default_rule", "confidence": "low"},
        {"category": "maquillaje", "description": "Maquillaje y peinado", "unit": "jornada", "quantity": jornadas, "unit_cost_min": 280 * mult, "unit_cost_estimated": 400 * mult, "unit_cost_max": 560 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "localizaciones", "description": "Tasa película ubicación", "unit": "día", "quantity": jornadas, "unit_cost_min": 350 * mult, "unit_cost_estimated": 500 * mult, "unit_cost_max": 700 * mult, "source": "default_rule", "confidence": "low"},
        {"category": "transporte", "description": "Furgonetas equipo", "unit": "día", "quantity": jornadas, "unit_cost_min": 175 * mult, "unit_cost_estimated": 250 * mult, "unit_cost_max": 350 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "alojamiento_dietas", "description": "Alojamiento y dietas equipo", "unit": "persona_día", "quantity": max(5, characters + 10) * jornadas, "unit_cost_min": 84 * mult, "unit_cost_estimated": 120 * mult, "unit_cost_max": 168 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "seguros_permisos", "description": "Seguro de producción", "unit": "proyecto", "quantity": 1, "unit_cost_min": 1750 * mult, "unit_cost_estimated": 2500 * mult, "unit_cost_max": 3500 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "seguros_permisos", "description": "Permisos y tasas", "unit": "proyecto", "quantity": 1, "unit_cost_min": 1050 * mult, "unit_cost_estimated": 1500 * mult, "unit_cost_max": 2100 * mult, "source": "default_rule", "confidence": "low"},
        {"category": "postproducción_imagen", "description": "Montaje/Edición", "unit": "semana", "quantity": post_weeks, "unit_cost_min": 1750 * mult, "unit_cost_estimated": 2500 * mult, "unit_cost_max": 3500 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "postproducción_imagen", "description": "Gradación de color", "unit": "semana", "quantity": max(1, post_weeks // 2), "unit_cost_min": 2100 * mult, "unit_cost_estimated": 3000 * mult, "unit_cost_max": 4200 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "postproducción_sonido", "description": "Edición de sonido", "unit": "semana", "quantity": post_weeks, "unit_cost_min": 1400 * mult, "unit_cost_estimated": 2000 * mult, "unit_cost_max": 2800 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "postproducción_sonido", "description": "Mezcla final", "unit": "día", "quantity": max(1, post_weeks), "unit_cost_min": 1050 * mult, "unit_cost_estimated": 1500 * mult, "unit_cost_max": 2100 * mult, "source": "default_rule", "confidence": "medium"},
        {"category": "música", "description": "Banda sonora original", "unit": "minuto", "quantity": max(80, min(120, jornadas * 4)), "unit_cost_min": 350 * mult, "unit_cost_estimated": 500 * mult, "unit_cost_max": 700 * mult, "source": "default_rule", "confidence": "low"},
        {"category": "marketing", "description": "Material promocional", "unit": "proyecto", "quantity": 1, "unit_cost_min": 2100 * mult, "unit_cost_estimated": 3000 * mult, "unit_cost_max": 4200 * mult, "source": "default_rule", "confidence": "low"},
        {"category": "distribución", "description": "Entrada festivales", "unit": "proyecto", "quantity": 1, "unit_cost_min": 1400 * mult, "unit_cost_estimated": 2000 * mult, "unit_cost_max": 2800 * mult, "source": "default_rule", "confidence": "low"},
    ]

    if characters > 0:
        items.append({"category": "reparto", "description": "Actor/actriz protagonista", "unit": "jornada", "quantity": max(1, min(3, characters)) * jornadas, "unit_cost_min": 2100 * mult, "unit_cost_estimated": 3000 * mult, "unit_cost_max": 4200 * mult, "source": "default_rule", "confidence": "low"})
    if characters > 3:
        items.append({"category": "reparto", "description": "Actor/actriz secundario", "unit": "jornada", "quantity": min(max(0, characters - 3), 5) * jornadas, "unit_cost_min": 840 * mult, "unit_cost_estimated": 1200 * mult, "unit_cost_max": 1680 * mult, "source": "default_rule", "confidence": "low"})
    if extras > 0:
        items.append({"category": "reparto", "description": "Figuración", "unit": "jornada", "quantity": extras * jornadas, "unit_cost_min": 56 * mult, "unit_cost_estimated": 80 * mult, "unit_cost_max": 112 * mult, "source": "default_rule", "confidence": "medium"})
    if characters > 0:
        items.append({"category": "vestuario", "description": "Vestuario actores", "unit": "actor", "quantity": max(1, characters), "unit_cost_min": 210 * mult, "unit_cost_estimated": 300 * mult, "unit_cost_max": 420 * mult, "source": "default_rule", "confidence": "low"})
    if action_scenes > 0:
        items.append({"category": "vfx_ia", "description": "VFX básico (acciones)", "unit": "shot", "quantity": action_scenes, "unit_cost_min": 210 * mult, "unit_cost_estimated": 300 * mult, "unit_cost_max": 420 * mult, "source": "default_rule", "confidence": "medium"})

    for item in items:
        item["total_min"] = item["quantity"] * item["unit_cost_min"]
        item["total_estimated"] = item["quantity"] * item["unit_cost_estimated"]
        item["total_max"] = item["quantity"] * item["unit_cost_max"]

    return items


def get_default_contingency_percent(level: str) -> float:
    return {"low": 15, "medium": 12, "high": 10}.get(level, 12)


def generate_budget(db: Session, project_id: str, level: str = "medium", script_text: str = "", organization_id: str = "", created_by: str = "") -> BudgetEstimate:
    metrics = analyze_script_text(script_text)
    line_items = generate_line_items(metrics, level)

    total_min = sum(i["total_min"] for i in line_items)
    total_estimated = sum(i["total_estimated"] for i in line_items)
    total_max = sum(i["total_max"] for i in line_items)
    contingency = get_default_contingency_percent(level)

    budget = BudgetEstimate(
        project_id=project_id,
        organization_id=organization_id or None,
        title=f"Presupuesto estimado - {level}",
        currency="EUR",
        budget_level=level,
        status="draft",
        total_min=total_min * (1 + contingency / 100),
        total_estimated=total_estimated * (1 + contingency / 100),
        total_max=total_max * (1 + contingency / 100),
        contingency_percent=contingency,
        assumptions_json=[f"Estimación basada en {metrics['scene_count']} escenas", f"{estimate_jornadas(metrics)} jornadas de grabación", f"{metrics['location_count']} ubicaciones", f"{metrics['character_count']} personajes", f"Nivel: {level}"],
        created_by=created_by or None,
    )
    db.add(budget)
    db.flush()

    for item_data in line_items:
        line = BudgetLineItem(
            budget_estimate_id=budget.id,
            category=item_data["category"],
            description=item_data.get("description", ""),
            unit=item_data.get("unit", ""),
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
        db.add(line)

    db.commit()
    db.refresh(budget)
    return budget


def recalculate_budget(db: Session, budget_id: str, level: str) -> BudgetEstimate:
    budget = db.get(BudgetEstimate, budget_id)
    if not budget:
        raise ValueError(f"Budget {budget_id} not found")

    lines = db.execute(select(BudgetLineItem).where(BudgetLineItem.budget_estimate_id == budget_id)).scalars().all()
    mult = LEVEL_MULTIPLIERS.get(level, 1.0)

    for line in lines:
        base_min = line.unit_cost_min / LEVEL_MULTIPLIERS.get(budget.budget_level, 1.0)
        base_est = line.unit_cost_estimated / LEVEL_MULTIPLIERS.get(budget.budget_level, 1.0)
        base_max = line.unit_cost_max / LEVEL_MULTIPLIERS.get(budget.budget_level, 1.0)
        line.unit_cost_min = base_min * mult
        line.unit_cost_estimated = base_est * mult
        line.unit_cost_max = base_max * mult
        line.total_min = line.quantity * line.unit_cost_min
        line.total_estimated = line.quantity * line.unit_cost_estimated
        line.total_max = line.quantity * line.unit_cost_max

    total_min = sum(l.total_min for l in lines)
    total_estimated = sum(l.total_estimated for l in lines)
    total_max = sum(l.total_max for l in lines)
    contingency = get_default_contingency_percent(level)

    budget.total_min = total_min * (1 + contingency / 100)
    budget.total_estimated = total_estimated * (1 + contingency / 100)
    budget.total_max = total_max * (1 + contingency / 100)
    budget.contingency_percent = contingency
    budget.budget_level = level

    db.commit()
    db.refresh(budget)
    return budget
