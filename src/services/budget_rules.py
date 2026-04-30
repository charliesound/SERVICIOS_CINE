"""
Budget estimator rules and categories.
These are internal heuristic rules for estimation - NOT official rates.
"""

from typing import Dict, List, Any, Optional


BUDGET_CATEGORIES = [
    "desarrollo",
    "preproducción",
    "producción",
    "dirección",
    "reparto",
    "equipo_técnico",
    "cámara",
    "sonido",
    "arte",
    "vestuario",
    "maquillaje",
    "localizaciones",
    "transporte",
    "alojamiento_dietas",
    "seguros_permisos",
    "postproducción_imagen",
    "postproducción_sonido",
    "música",
    "vfx_ia",
    "marketing",
    "distribución",
    "contingencia",
]


CATEGORY_LABELS = {
    "desarrollo": "Desarrollo",
    "preproducción": "Preproducción",
    "producción": "Producción",
    "dirección": "Dirección",
    "reparto": "Reparto",
    "equipo_técnico": "Equipo Técnico",
    "cámara": "Cámara",
    "sonido": "Sonido",
    "arte": "Arte",
    "vestuario": "Vestuario",
    "maquillaje": "Maquillaje y Peluquería",
    "localizaciones": "Localizaciones",
    "transporte": "Transporte",
    "alojamiento_dietas": "Alojamiento y Dietas",
    "seguros_permisos": "Seguros y Permisos",
    "postproducción_imagen": "Postproducción Imagen",
    "postproducción_sonido": "Postproducción Sonido",
    "música": "Música",
    "vfx_ia": "VFX/IA",
    "marketing": "Marketing",
    "distribución": "Distribución",
    "contingencia": "Contingencia",
}


LEVEL_MULTIPLIERS = {
    "low": 0.7,
    "medium": 1.0,
    "high": 1.4,
}


CONFIDENCE_BY_LEVEL = {
    "low": "low",
    "medium": "medium",
    "high": "high",
}


RULES = [
    {
        "id": "desarrollo_legal",
        "category": "desarrollo",
        "description": "Desarrollo y derechos de guion",
        "unit": "proyecto",
        "base_cost": 2500,
        "complexity_multiplier": 1.0,
        "notes": "Derechos de opción-adaptación estimados",
        "confidence": "medium",
    },
    {
        "id": "preproduccion_scenic",
        "category": "preproducción",
        "description": "Locaciones y permisos de rodar",
        "unit": "localización",
        "base_cost": 800,
        "complexity_multiplier": 1.0,
        "notes": "Permisos estimado por localización",
        "confidence": "medium",
    },
    {
        "id": "preproduccion_arte",
        "category": "preproducción",
        "description": "Diseño de producción y arte",
        "unit": "semana",
        "base_cost": 3000,
        "complexity_multiplier": 1.0,
        "notes": "Diseño de arte y escenografía",
        "confidence": "medium",
    },
    {
        "id": "direccion_director",
        "category": "dirección",
        "description": "Dirección artística",
        "unit": "jornada",
        "base_cost": 1500,
        "complexity_multiplier": 1.0,
        "notes": "Honorarios del director por jornada",
        "confidence": "medium",
    },
    {
        "id": "direccion_asistencia",
        "category": "dirección",
        "description": "Ayte. de dirección",
        "unit": "jornada",
        "base_cost": 400,
        "complexity_multiplier": 1.0,
        "notes": "Primer/a ayte. de dirección",
        "confidence": "medium",
    },
    {
        "id": "produccion_jornada",
        "category": "producción",
        "description": "Producción por jornada",
        "unit": "jornada",
        "base_cost": 800,
        "complexity_multiplier": 1.0,
        "notes": "Equipo de producción por día",
        "confidence": "medium",
    },
    {
        "id": "produccion_exterior",
        "category": "producción",
        "description": "Unidad adicional-exterior",
        "unit": "jornada",
        "base_cost": 600,
        "complexity_multiplier": 1.2,
        "notes": "Equipo adicional para exteriores",
        "confidence": "medium",
    },
    {
        "id": "reparto_protag",
        "category": "reparto",
        "description": "Actor/actriz protagonista",
        "unit": "jornada",
        "base_cost": 3000,
        "complexity_multiplier": 1.0,
        "notes": "Honorarios día - estimado",
        "confidence": "low",
    },
    {
        "id": "reparto_secundario",
        "category": "reparto",
        "description": "Actor/actriz secundario",
        "unit": "jornada",
        "base_cost": 1200,
        "complexity_multiplier": 1.0,
        "notes": "Actor secundario - estimado",
        "confidence": "low",
    },
    {
        "id": "reparto_fondo",
        "category": "reparto",
        "description": "Figuración",
        "unit": "jornada",
        "base_cost": 80,
        "complexity_multiplier": 1.0,
        "notes": "Por persona por día",
        "confidence": "medium",
    },
    {
        "id": "equipo_tecnico_dop",
        "category": "equipo_técnico",
        "description": "Director de Fotografía",
        "unit": "jornada",
        "base_cost": 1200,
        "complexity_multiplier": 1.0,
        "notes": "DOP por jornada",
        "confidence": "medium",
    },
    {
        "id": "equipo_tecnico_gaffer",
        "category": "equipo_técnico",
        "description": "Gaffer/eléctricos",
        "unit": "jornada",
        "base_cost": 500,
        "complexity_multiplier": 1.0,
        "notes": "Gaffer + equipo eléctrico",
        "confidence": "medium",
    },
    {
        "id": "camera_alquiler",
        "category": "cámara",
        "description": "Alquiler cámara y ópticas",
        "unit": "jornada",
        "base_cost": 1500,
        "complexity_multiplier": 1.0,
        "notes": "Cámara profesional - estimado",
        "confidence": "medium",
    },
    {
        "id": "camera_grip",
        "category": "cámara",
        "description": "Grip y movimiento",
        "unit": "jornada",
        "base_cost": 400,
        "complexity_multiplier": 1.0,
        "notes": "Steadicam/rig/dolly",
        "confidence": "medium",
    },
    {
        "id": "sonido_micro",
        "category": "sonido",
        "description": "Micófono y boom",
        "unit": "jornada",
        "base_cost": 350,
        "complexity_multiplier": 1.0,
        "notes": "Sonidista + equipo",
        "confidence": "medium",
    },
    {
        "id": "arte_escenografia",
        "category": "arte",
        "description": "Escenografía",
        "unit": "escena",
        "base_cost": 1200,
        "complexity_multiplier": 1.0,
        "notes": "Por set - estimado",
        "confidence": "low",
    },
    {
        "id": "vestuario_actor",
        "category": "vestuario",
        "description": "Vestuario actores",
        "unit": "actor",
        "base_cost": 300,
        "complexity_multiplier": 1.0,
        "notes": "Por actor - estimado",
        "confidence": "low",
    },
    {
        "id": "maquillaje_atencion",
        "category": "maquillaje",
        "description": "Maquillaje y peinado",
        "unit": "jornada",
        "base_cost": 400,
        "complexity_multiplier": 1.0,
        "notes": "MUA + Hair",
        "confidence": "medium",
    },
    {
        "id": "localizacion_exterior",
        "category": "localizaciones",
        "description": "Tasa película ubicación",
        "unit": "día",
        "base_cost": 500,
        "complexity_multiplier": 1.0,
        "notes": "Tasa municipal estimada",
        "confidence": "low",
    },
    {
        "id": "transporte_equipo",
        "category": "transporte",
        "description": "Furgonetas equipo",
        "unit": "día",
        "base_cost": 250,
        "complexity_multiplier": 1.0,
        "notes": "2-3 furgonetas",
        "confidence": "medium",
    },
    {
        "id": "alojamiento_dietas",
        "category": "alojamiento_dietas",
        "description": "Alojamiento y dietas equipo",
        "unit": "persona_día",
        "base_cost": 120,
        "complexity_multiplier": 1.0,
        "notes": "Hotel + manutención",
        "confidence": "medium",
    },
    {
        "id": "seguros_produccion",
        "category": "seguros_permisos",
        "description": "Seguro de producción",
        "unit": "proyecto",
        "base_cost": 2500,
        "complexity_multiplier": 1.0,
        "notes": "Seguro todo riesgo - estimado",
        "confidence": "medium",
    },
    {
        "id": "permisos_rodaje",
        "category": "seguros_permisos",
        "description": "Permisos y tasas",
        "unit": "proyecto",
        "base_cost": 1500,
        "complexity_multiplier": 1.0,
        "notes": "ICUB/delegaciones",
        "confidence": "low",
    },
    {
        "id": "postpro_imagen_edicion",
        "category": "postproducción_imagen",
        "description": "Montaje/Edición",
        "unit": "semana",
        "base_cost": 2500,
        "complexity_multiplier": 1.0,
        "notes": "Editor/a + post",
        "confidence": "medium",
    },
    {
        "id": "postpro_imagen_color",
        "category": "postproducción_imagen",
        "description": "Gradación de color",
        "unit": "semana",
        "base_cost": 3000,
        "complexity_multiplier": 1.0,
        "notes": "Colourist - estimado",
        "confidence": "medium",
    },
    {
        "id": "postpro_sonido_edicion",
        "category": "postproducción_sonido",
        "description": "Edición de sonido",
        "unit": "semana",
        "base_cost": 2000,
        "complexity_multiplier": 1.0,
        "notes": "Sound editor",
        "confidence": "medium",
    },
    {
        "id": "postpro_sonido_mix",
        "category": "postproducción_sonido",
        "description": "Mezcla final",
        "unit": "día",
        "base_cost": 1500,
        "complexity_multiplier": 1.0,
        "notes": "Mix 5.1/7.1",
        "confidence": "medium",
    },
    {
        "id": "musica_derechos",
        "category": "música",
        "description": "Banda sonora original",
        "unit": "minuto",
        "base_cost": 500,
        "complexity_multiplier": 1.0,
        "notes": "Composer - estimado",
        "confidence": "low",
    },
    {
        "id": "vfx_basico",
        "category": "vfx_ia",
        "description": "VFX básico (titulos/stingers)",
        "unit": "shot",
        "base_cost": 300,
        "complexity_multiplier": 1.0,
        "notes": "Por shot simple",
        "confidence": "medium",
    },
    {
        "id": "vfx_ia_upscaling",
        "category": "vfx_ia",
        "description": "AI upscaling/restoration",
        "unit": "minuto",
        "base_cost": 200,
        "complexity_multiplier": 1.0,
        "notes": "Por minuto - estimado",
        "confidence": "low",
    },
    {
        "id": "marketing_poster",
        "category": "marketing",
        "description": "Material promocional",
        "unit": "proyecto",
        "base_cost": 3000,
        "complexity_multiplier": 1.0,
        "notes": "Poster + materiales",
        "confidence": "low",
    },
    {
        "id": "distribucion_festivales",
        "category": "distribución",
        "description": "Entrada festivales",
        "unit": "proyecto",
        "base_cost": 2000,
        "complexity_multiplier": 1.0,
        "notes": "Fees submitting",
        "confidence": "low",
    },
]


def get_category_rules(category):
    return [r for r in RULES if r["category"] == category]


def get_rule(rule_id):
    for r in RULES:
        if r["id"] == rule_id:
            return r
    return None


def calculate_category_total(category, quantity, level="medium"):
    rules = get_category_rules(category)
    if not rules:
        return {"min": 0, "estimated": 0, "max": 0}
    
    total_base = sum(r["base_cost"] * quantity for r in rules)
    multiplier = LEVEL_MULTIPLIERS.get(level, 1.0)
    
    return {
        "min": total_base * 0.7 * multiplier,
        "estimated": total_base * multiplier,
        "max": total_base * 1.4 * multiplier,
    }


def get_default_contingency_percent(level="medium"):
    contingency_map = {
        "low": 10.0,
        "medium": 15.0,
        "high": 20.0,
    }
    return contingency_map.get(level, 15.0)


def get_rule_names_by_category():
    names = {}
    for r in RULES:
        cat = r["category"]
        if cat not in names:
            names[cat] = []
        names[cat].append(r["description"])
    return names