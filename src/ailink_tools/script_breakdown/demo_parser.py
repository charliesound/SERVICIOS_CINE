"""Deterministic parser for Proyecto Demo Bruma script."""

from __future__ import annotations

import re
from typing import List

from .schemas import (
    BudgetItem,
    BreakdownResult,
    Character,
    Location,
    Risk,
    Scene,
)

# ---------------------------------------------------------------------------
# Demo markers – the parser only accepts scripts containing these exact
# markers. Any other input is rejected.
# ---------------------------------------------------------------------------

DEMO_PROJECT_TITLE = "Proyecto Demo Bruma"
DEMO_MARKERS = [
    "ESCENA 1. INT. CASA DE ANA - NOCHE",
    "ESCENA 2. EXT. CAMINO RURAL - AMANECER",
    "ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA",
    "ESCENA 4. INT. BAR DEMO ESTACIÓN - NOCHE",
    "ESCENA 5. EXT. CAMPO DE LAVANDA - DÍA",
    "ESCENA 6. EXT. CASA DE ANA - DÍA",
    "ESCENA 7. INT. CASA DE ANA - NOCHE",
    "ESCENA 8. EXT. CAMINO RURAL - NOCHE",
]

# ---------------------------------------------------------------------------
# Scene definitions – deterministic mapping for the demo script
# ---------------------------------------------------------------------------

SCENE_DEFS = [
    {
        "number": 1,
        "header": "INT. CASA DE ANA - NOCHE",
        "location": "Casa Demo de Ana",
        "int_ext": "INT",
        "day_night": "NOCHE",
        "characters": ["Ana Bruma", "Leo Prado"],
        "complexity": "baja",
        "notes": "primera escena, cocina, iluminación interior",
    },
    {
        "number": 2,
        "header": "EXT. CAMINO RURAL - AMANECER",
        "location": "Camino Rural Demo",
        "int_ext": "EXT",
        "day_night": "DÍA",
        "characters": ["Ana Bruma", "Leo Prado"],
        "complexity": "media",
        "notes": "necesita permiso ayuntamiento, perro BISCA",
    },
    {
        "number": 3,
        "header": "EXT. PUEBLO DEMO BRUMA - DÍA",
        "location": "Pueblo Demo Bruma",
        "int_ext": "EXT",
        "day_night": "DÍA",
        "characters": ["Ana Bruma", "Mara Sol", "Nora Cerezo"],
        "complexity": "media",
        "notes": "bar, calles, extras, permiso ayuntamiento",
    },
    {
        "number": 4,
        "header": "INT. BAR DEMO ESTACIÓN - NOCHE",
        "location": "Bar Demo Estación",
        "int_ext": "INT",
        "day_night": "NOCHE",
        "characters": ["Ana Bruma", "Leo Prado", "Mara Sol", "Bruno Valle"],
        "complexity": "media",
        "notes": "reunión producción, sonido directo",
    },
    {
        "number": 5,
        "header": "EXT. CAMPO DE LAVANDA - DÍA",
        "location": "Campo de Lavanda Demo",
        "int_ext": "EXT",
        "day_night": "DÍA",
        "characters": ["Ana Bruma"],
        "complexity": "media",
        "notes": "campo agrícola, necesita permiso propietario",
    },
    {
        "number": 6,
        "header": "EXT. CASA DE ANA - DÍA",
        "location": "Casa Demo de Ana (exterior)",
        "int_ext": "EXT",
        "day_night": "DÍA",
        "characters": ["Ana Bruma", "Leo Prado"],
        "complexity": "baja",
        "notes": "reparación valla, gato NIEBLA",
    },
    {
        "number": 7,
        "header": "INT. CASA DE ANA - NOCHE",
        "location": "Casa Demo de Ana",
        "int_ext": "INT",
        "day_night": "NOCHE",
        "characters": ["Ana Bruma"],
        "complexity": "baja",
        "notes": "escena teléfono, lluvia ambiente",
    },
    {
        "number": 8,
        "header": "EXT. CAMINO RURAL - NOCHE",
        "location": "Camino Rural Demo",
        "int_ext": "EXT",
        "day_night": "NOCHE",
        "characters": ["Ana Bruma", "Leo Prado"],
        "complexity": "alta",
        "notes": "noche, lluvia, truenos, VFX rayo, riesgo bajo",
    },
]

# ---------------------------------------------------------------------------
# Character definitions – deterministic mapping
# ---------------------------------------------------------------------------

CHAR_DEFS = [
    {
        "character_id": "CHAR-DEMO-01",
        "name": "Ana Bruma",
        "role": "protagonista",
        "scenes": [1, 2, 3, 5, 6, 7, 8],
        "age": "30",
        "complexity": "alta",
        "notes": "presencia casi constante",
    },
    {
        "character_id": "CHAR-DEMO-02",
        "name": "Leo Prado",
        "role": "coprotagonista",
        "scenes": [1, 2, 4, 6, 8],
        "age": "25",
        "complexity": "media",
        "notes": "hermano de Ana",
    },
    {
        "character_id": "CHAR-DEMO-03",
        "name": "Mara Sol",
        "role": "secundario",
        "scenes": [3, 4],
        "age": "45",
        "complexity": "baja",
        "notes": "dueña del bar",
    },
    {
        "character_id": "CHAR-DEMO-04",
        "name": "Bruno Valle",
        "role": "secundario",
        "scenes": [4],
        "age": "35",
        "complexity": "baja",
        "notes": "técnico de sonido",
    },
    {
        "character_id": "CHAR-DEMO-05",
        "name": "Nora Cerezo",
        "role": "extra",
        "scenes": [3],
        "age": "60",
        "complexity": "muy baja",
        "notes": "solo una escena",
    },
]

# ---------------------------------------------------------------------------
# Location definitions – deterministic mapping
# ---------------------------------------------------------------------------

LOC_DEFS = [
    {
        "location_id": "LOC-DEMO-01",
        "name": "Casa Demo de Ana",
        "type": "casa rural",
        "int_ext": "INT/EXT",
        "scenes": [1, 6, 7],
        "permits": "no",
        "complexity": "baja",
    },
    {
        "location_id": "LOC-DEMO-02",
        "name": "Camino Rural Demo",
        "type": "camino de tierra",
        "int_ext": "EXT",
        "scenes": [2, 8],
        "permits": "sí",
        "complexity": "baja",
    },
    {
        "location_id": "LOC-DEMO-03",
        "name": "Pueblo Demo Bruma",
        "type": "pueblo ficticio",
        "int_ext": "EXT",
        "scenes": [3],
        "permits": "sí",
        "complexity": "media",
    },
    {
        "location_id": "LOC-DEMO-04",
        "name": "Bar Demo Estación",
        "type": "bar local",
        "int_ext": "INT",
        "scenes": [4],
        "permits": "sí",
        "complexity": "baja",
    },
    {
        "location_id": "LOC-DEMO-05",
        "name": "Campo de Lavanda Demo",
        "type": "campo agrícola",
        "int_ext": "EXT",
        "scenes": [5],
        "permits": "sí",
        "complexity": "media",
    },
]

# ---------------------------------------------------------------------------
# Risk definitions – deterministic mapping
# ---------------------------------------------------------------------------

RISK_DEFS = [
    {
        "risk_id": "RISK-DEMO-01",
        "description": "rodaje nocturno en interiores y exteriores",
        "impact": "alto",
        "probability": "alta",
        "mitigation": "planificar iluminación extra y horarios ajustados",
    },
    {
        "risk_id": "RISK-DEMO-02",
        "description": "exterior con clima adverso (lluvia)",
        "impact": "alto",
        "probability": "media",
        "mitigation": "tener cubiertas y plan B de rodaje",
    },
    {
        "risk_id": "RISK-DEMO-03",
        "description": "animal en escena (perro BISCA, gato NIEBLA)",
        "impact": "medio",
        "probability": "alta",
        "mitigation": "coordinar con propietario y tener suplente",
    },
    {
        "risk_id": "RISK-DEMO-04",
        "description": "vehículo en camino rural",
        "impact": "medio",
        "probability": "baja",
        "mitigation": "controlar tráfico, permiso de rodaje",
    },
    {
        "risk_id": "RISK-DEMO-05",
        "description": "permisos de localización múltiples",
        "impact": "alto",
        "probability": "media",
        "mitigation": "gestionar con al menos 2 semanas de antelación",
    },
    {
        "risk_id": "RISK-DEMO-06",
        "description": "sonido complejo en exteriores",
        "impact": "medio",
        "probability": "alta",
        "mitigation": "equipo ADR, grabación de ambiente separada",
    },
    {
        "risk_id": "RISK-DEMO-07",
        "description": "VFX menor (rayo en escena 8)",
        "impact": "bajo",
        "probability": "baja",
        "mitigation": "efecto simple en postproducción",
    },
    {
        "risk_id": "RISK-DEMO-08",
        "description": "continuidad de vestuario entre escenas",
        "impact": "bajo",
        "probability": "media",
        "mitigation": "control de continuity por departamento de vestuario",
    },
    {
        "risk_id": "RISK-DEMO-09",
        "description": "cashflow ajustado por presupuesto limitado",
        "impact": "alto",
        "probability": "alta",
        "mitigation": "aumentar contingencia al 15%",
    },
    {
        "risk_id": "RISK-DEMO-10",
        "description": "menor en escena (no presente pero posible)",
        "impact": "medio",
        "probability": "baja",
        "mitigation": "planificar restricciones si se añade personaje infantil",
    },
]

# ---------------------------------------------------------------------------
# Budget categories – deterministic mapping
# ---------------------------------------------------------------------------

BUDGET_DEFS = [
    {
        "budget_id": "BUDGET-DEMO-01",
        "category": "equipo técnico",
        "low": 3000,
        "mid": 4500,
        "high": 6000,
        "confidence": "media",
        "assumptions": "4 semanas, equipo básico",
    },
    {
        "budget_id": "BUDGET-DEMO-02",
        "category": "reparto",
        "low": 2000,
        "mid": 3000,
        "high": 4500,
        "confidence": "media",
        "assumptions": "5 personajes, cachés independientes",
    },
    {
        "budget_id": "BUDGET-DEMO-03",
        "category": "figuración",
        "low": 500,
        "mid": 800,
        "high": 1200,
        "confidence": "alta",
        "assumptions": "2 extras, 2 días",
    },
    {
        "budget_id": "BUDGET-DEMO-04",
        "category": "cámara",
        "low": 2500,
        "mid": 3500,
        "high": 5000,
        "confidence": "media",
        "assumptions": "equipo básico, 4 semanas",
    },
    {
        "budget_id": "BUDGET-DEMO-05",
        "category": "sonido",
        "low": 2000,
        "mid": 3000,
        "high": 4500,
        "confidence": "media",
        "assumptions": "directo + ADR",
    },
    {
        "budget_id": "BUDGET-DEMO-06",
        "category": "arte",
        "low": 1500,
        "mid": 2500,
        "high": 3500,
        "confidence": "media",
        "assumptions": "decorados sencillos",
    },
    {
        "budget_id": "BUDGET-DEMO-07",
        "category": "vestuario",
        "low": 800,
        "mid": 1200,
        "high": 1800,
        "confidence": "alta",
        "assumptions": "ropa del actor, pocos cambios",
    },
    {
        "budget_id": "BUDGET-DEMO-08",
        "category": "maquillaje",
        "low": 600,
        "mid": 900,
        "high": 1300,
        "confidence": "alta",
        "assumptions": "maquillaje sencillo",
    },
    {
        "budget_id": "BUDGET-DEMO-09",
        "category": "localizaciones",
        "low": 1500,
        "mid": 2500,
        "high": 4000,
        "confidence": "baja",
        "assumptions": "permisos variables",
    },
    {
        "budget_id": "BUDGET-DEMO-10",
        "category": "transporte",
        "low": 1000,
        "mid": 1500,
        "high": 2500,
        "confidence": "media",
        "assumptions": "furgoneta + desplazamientos",
    },
    {
        "budget_id": "BUDGET-DEMO-11",
        "category": "catering",
        "low": 1200,
        "mid": 1800,
        "high": 2500,
        "confidence": "alta",
        "assumptions": "8 personas, 4 semanas",
    },
    {
        "budget_id": "BUDGET-DEMO-12",
        "category": "seguros",
        "low": 800,
        "mid": 1200,
        "high": 1800,
        "confidence": "media",
        "assumptions": "seguro de producción",
    },
    {
        "budget_id": "BUDGET-DEMO-13",
        "category": "permisos",
        "low": 500,
        "mid": 1000,
        "high": 2000,
        "confidence": "baja",
        "assumptions": "varios permisos",
    },
    {
        "budget_id": "BUDGET-DEMO-14",
        "category": "VFX",
        "low": 300,
        "mid": 600,
        "high": 1000,
        "confidence": "alta",
        "assumptions": "efecto menor, postproducción",
    },
    {
        "budget_id": "BUDGET-DEMO-15",
        "category": "música",
        "low": 500,
        "mid": 800,
        "high": 1200,
        "confidence": "media",
        "assumptions": "compositor independiente",
    },
    {
        "budget_id": "BUDGET-DEMO-16",
        "category": "postproducción",
        "low": 1500,
        "mid": 2500,
        "high": 4000,
        "confidence": "media",
        "assumptions": "montaje + color",
    },
    {
        "budget_id": "BUDGET-DEMO-17",
        "category": "legal",
        "low": 300,
        "mid": 500,
        "high": 800,
        "confidence": "alta",
        "assumptions": "contratos básicos",
    },
    {
        "budget_id": "BUDGET-DEMO-18",
        "category": "contingencia",
        "low": 2000,
        "mid": 3000,
        "high": 5000,
        "confidence": "media",
        "assumptions": "15% del total",
    },
]

# ---------------------------------------------------------------------------
# Viability indicators – deterministic mapping
# ---------------------------------------------------------------------------

VIABILITY_DEFS = [
    {
        "indicator": "complejidad logística",
        "score": 6,
        "max_score": 10,
        "traffic_light": "amarillo",
        "justification": "varias localizaciones rurales",
        "recommendation": "agrupar escenas por localización",
    },
    {
        "indicator": "complejidad artística",
        "score": 4,
        "max_score": 10,
        "traffic_light": "verde",
        "justification": "drama sencillo, pocos extras",
        "recommendation": "mantener",
    },
    {
        "indicator": "complejidad técnica",
        "score": 5,
        "max_score": 10,
        "traffic_light": "verde",
        "justification": "rodaje nocturno y exterior",
        "recommendation": "preparar equipo extra",
    },
    {
        "indicator": "complejidad financiera",
        "score": 6,
        "max_score": 10,
        "traffic_light": "amarillo",
        "justification": "presupuesto ajustado",
        "recommendation": "buscar patrocinio",
    },
    {
        "indicator": "riesgo de calendario",
        "score": 5,
        "max_score": 10,
        "traffic_light": "amarillo",
        "justification": "4 semanas es ajustado",
        "recommendation": "planificar al día",
    },
    {
        "indicator": "riesgo de permisos",
        "score": 7,
        "max_score": 10,
        "traffic_light": "naranja",
        "justification": "varios permisos necesarios",
        "recommendation": "iniciar gestión ahora",
    },
    {
        "indicator": "riesgo de postproducción",
        "score": 4,
        "max_score": 10,
        "traffic_light": "verde",
        "justification": "VFX menor",
        "recommendation": "mantener",
    },
    {
        "indicator": "riesgo de localizaciones",
        "score": 6,
        "max_score": 10,
        "traffic_light": "amarillo",
        "justification": "rural + urbano",
        "recommendation": "tener alternativas",
    },
    {
        "indicator": "riesgo de reparto",
        "score": 3,
        "max_score": 10,
        "traffic_light": "verde",
        "justification": "5 personajes",
        "recommendation": "mantener",
    },
    {
        "indicator": "riesgo de cashflow",
        "score": 7,
        "max_score": 10,
        "traffic_light": "naranja",
        "justification": "presupuesto ajustado",
        "recommendation": "aumentar contingencia",
    },
    {
        "indicator": "viabilidad global",
        "score": 5.5,
        "max_score": 10,
        "traffic_light": "amarillo",
        "justification": "viable con ajustes",
        "recommendation": "seguir recomendaciones",
    },
]

# ---------------------------------------------------------------------------
# Recommendations – deterministic list
# ---------------------------------------------------------------------------

RECOMMENDATIONS = [
    "agrupar escenas rurales para reducir desplazamientos",
    "reducir noches de rodaje para ahorrar en iluminación",
    "planificar menor con restricciones si se añade personaje infantil",
    "prever permisos de localización con al menos 2 semanas de antelación",
    "simplificar VFX para mantener coste bajo",
    "controlar sonido exterior con equipo ADR",
    "aumentar contingencia al 15% por riesgo de cashflow",
    "revisar vehículo y seguridad para escenas en camino rural",
    "preparar presupuesto editable en formato Excel",
    "revisar plan con productor y dirección de producción antes de rodaje",
]

# ---------------------------------------------------------------------------
# Human review notes – deterministic list
# ---------------------------------------------------------------------------

HUMAN_REVIEW_NOTES = [
    "revisar permisos de localización antes de confirmar fechas",
    "validar rangos de presupuesto con productor y dirección de producción",
    "confirmar disponibilidad de actores para fechas de rodaje",
    "verificar requisitos de seguro para escenas con riesgo",
    "confirmar tecnología de sonido disponible para ADR",
    "revisar necesidades de vestuario con departamento de arte",
    "validar plan de contingencia con equipo financiero",
]


def _validate_demo_input(text: str) -> None:
    """Validate that the input is the controlled demo script."""
    for marker in DEMO_MARKERS:
        if marker not in text:
            raise ValueError(
                f"Input no soportado: falta marcador demo '{marker}'. "
                "Solo se acepta el guion de Proyecto Demo Bruma."
            )


def _extract_scenes() -> List[Scene]:
    """Extract scenes from deterministic definitions."""
    return [
        Scene(
            scene_id=f"SCENE-DEMO-{s['number']:02d}",
            number=s["number"],
            header=s["header"],
            location=s["location"],
            int_ext=s["int_ext"],
            day_night=s["day_night"],
            characters=s["characters"],
            complexity=s["complexity"],
            notes=s["notes"],
        )
        for s in SCENE_DEFS
    ]


def _extract_characters() -> List[Character]:
    """Extract characters from deterministic definitions."""
    return [
        Character(
            character_id=c["character_id"],
            name=c["name"],
            role=c["role"],
            scenes=c["scenes"],
            age=c["age"],
            complexity=c["complexity"],
            notes=c["notes"],
        )
        for c in CHAR_DEFS
    ]


def _extract_locations() -> List[Location]:
    """Extract locations from deterministic definitions."""
    return [
        Location(
            location_id=l["location_id"],
            name=l["name"],
            type=l["type"],
            int_ext=l["int_ext"],
            scenes=l["scenes"],
            permits=l["permits"],
            complexity=l["complexity"],
        )
        for l in LOC_DEFS
    ]


def _extract_risks() -> List[Risk]:
    """Extract risks from deterministic definitions."""
    return [
        Risk(
            risk_id=r["risk_id"],
            description=r["description"],
            impact=r["impact"],
            probability=r["probability"],
            mitigation=r["mitigation"],
        )
        for r in RISK_DEFS
    ]


def _extract_budget() -> List[BudgetItem]:
    """Extract budget items from deterministic definitions."""
    return [
        BudgetItem(
            budget_id=b["budget_id"],
            category=b["category"],
            low=b["low"],
            mid=b["mid"],
            high=b["high"],
            confidence=b["confidence"],
            assumptions=b["assumptions"],
        )
        for b in BUDGET_DEFS
    ]


def _compute_viability() -> dict:
    """Compute viability from deterministic definitions."""
    return {
        "indicators": VIABILITY_DEFS,
        "global_score": 5.5,
        "global_traffic_light": "amarillo",
        "summary": "Viable con ajustes. Seguir recomendaciones.",
    }


def parse_demo_script(text: str) -> BreakdownResult:
    """Parse the controlled demo script and return structured breakdown.

    This parser is deterministic and transparent. It does not simulate
    AI or real analysis. It uses predefined mappings for the demo script.

    Args:
        text: The script text to parse. Must be the controlled demo script.

    Returns:
        BreakdownResult with all structured data.

    Raises:
        ValueError: If the input is not the controlled demo script.
    """
    _validate_demo_input(text)

    scenes = _extract_scenes()
    characters = _extract_characters()
    locations = _extract_locations()
    risks = _extract_risks()
    budget = _extract_budget()
    viability = _compute_viability()

    project = {
        "title": DEMO_PROJECT_TITLE,
        "type": "largometraje independiente",
        "genre": "drama thriller rural",
        "duration_minutes": 90,
        "shooting_weeks": 4,
        "currency": "EUR",
        "objective": "mostrar cómo un guion se convierte en desglose, "
        "riesgos, viabilidad y presupuesto preliminar",
    }

    metadata = {
        "parser_version": "1.0.0-demo",
        "parser_type": "deterministic",
        "is_demo": True,
        "demo_project": DEMO_PROJECT_TITLE,
        "organization_id": "ORG-DEMO-001",
        "tenant_id": "TENANT-DEMO-001",
        "project_id": "PROJECT-DEMO-001",
        "film_id": "FILM-DEMO-001",
        "organization_name": "Productora Demo Bruma",
        "notes": "IDs ficticios para aislamiento multi-cliente/multi-proyecto",
    }

    return BreakdownResult(
        project=project,
        scenes=scenes,
        characters=characters,
        locations=locations,
        risks=risks,
        viability=viability,
        preliminary_budget=budget,
        recommendations=RECOMMENDATIONS,
        human_review_notes=HUMAN_REVIEW_NOTES,
        metadata=metadata,
    )
