"""Email templates for follow-up campaigns.

Each template is a callable that receives lead data and returns
(subject, body) ready for delivery.
"""

from typing import Any, Dict, Tuple

TemplateResult = Tuple[str, str]


def interpolate(text: str, variables: Dict[str, str]) -> str:
    """Replace {{key}} placeholders with values."""
    result = text
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value or "")
    return result


def cid_storyboard_ia_initial(lead: Dict[str, Any]) -> TemplateResult:
    """V1 — Autorespuesta inicial para leads de Storyboard IA de CID.

    Variables:
        name: nombre completo del lead
        company: empresa o productora (puede estar vacía)
        interest: uso previsto (pitch, storyboard, preproducción, etc.)
        priority: hot / warm / cold
    """
    name = lead.get("full_name", "")
    company = lead.get("company", "")
    interest = lead.get("role", "") or lead.get("use_case", "") or "Storyboard IA"
    priority = lead.get("priority", "") or ""

    company_line = f" de {company}" if company else ""

    subject = f"CID — Tu interés en Storyboard IA{company_line}"

    body = interpolate(
        """Hola {{name}},

Gracias por tu interés en Storyboard IA de CID — Cine Inteligente Digital.

Hemos recibido tu solicitud y nos gustaría mostrarte en detalle cómo CID puede ayudarte a visualizar tu proyecto antes de rodar.

Qué hace CID:
• Analiza tu guion y detecta escenas, personajes y estructura narrativa.
• Genera un desglose cinematográfico con props, localizaciones y necesidades de producción.
• Propone una cobertura visual con beats narrativos y tipo de plano por escena.
• Genera un storyboard con renders automáticos, grounding visual y continuidad formal.

No es un generador de imágenes genérico. CID entiende cine: escenas, planos, continuidad de eje y estructura narrativa.

Para avanzar, nos ayudaría saber:
1. ¿En qué fase está tu proyecto? (desarrollo, preproducción, pitch, otro)
2. ¿Qué tipo de material visual necesitas? (storyboard, previs, prueba de look, presentación)
3. ¿Cuándo necesitarías tener el material listo?

Puedes responder directamente a este email o solicitar una demo personalizada donde te mostraremos CID en acción con un fragmento de tu propio guion.

Un saludo,
Equipo CID
Cine Inteligente Digital
{{signature}}""",
        {
            "name": name,
            "company": company,
            "interest": interest,
            "priority": priority,
            "signature": "CID — Cine Inteligente Digital",
        },
    )

    return subject, body


# Registry: template_key → callable
TEMPLATES: Dict[str, Any] = {
    "cid_storyboard_ia_initial": cid_storyboard_ia_initial,
}


def get_template(template_key: str):
    """Return a template function by key, or None if not found."""
    return TEMPLATES.get(template_key)


def list_templates() -> list:
    """Return list of available template keys."""
    return list(TEMPLATES.keys())
