from datetime import datetime
from typing import Optional, List, Dict, Any

DEMO_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "id": "demo-funding-001",
        "title": "Fondo de Producción Audiovisual 2024",
        "description": "Fondo gubernamentales para producción de largometraxjes y documentales.",
        "amount_range": "$50,000 - $200,000",
        "deadline": "2024-12-31",
        "source_id": "gov-prod-001",
        "eligibility": ["Producción independiente", "Cortos", "Largometraxjes"],
        "tags": ["gobierno", "producción", "audiovisual"],
    },
    {
        "id": "demo-funding-002",
        "title": "Convocatoria Festivales Internacionales",
        "description": "Apoyo para participación en festivales internacionales de cine.",
        "amount_range": "$5,000 - $30,000",
        "deadline": "2024-06-30",
        "source_id": "fest-intl-001",
        "eligibility": ["Películas terminadas", "Premiere required"],
        "tags": ["festivales", "internacional", "promoción"],
    },
    {
        "id": "demo-funding-003",
        "title": "Fondo de Postproducción Digital",
        "description": "Financiamiento para servicios de postproducción digital y VFX.",
        "amount_range": "$10,000 - $100,000",
        "deadline": "2024-09-30",
        "source_id": "post-prod-001",
        "eligibility": ["Proyectos en postproducción", "VFX", "Colorización"],
        "tags": ["postproducción", "VFX", "digital"],
    },
]


def parse_catalog_deadline(deadline_str: Optional[str]) -> Optional[datetime]:
    """Parse deadline string to datetime object."""
    if not deadline_str:
        return None

    try:
        return datetime.strptime(deadline_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None
