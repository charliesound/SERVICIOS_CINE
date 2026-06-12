"""Tests for AILink Sync Dialogue outreach starter pack."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DOC = ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_outreach_starter_pack_v1.md"

REQUIRED = [
    "# AILink Sync Dialogue — Outreach Starter Pack v1",
    "## 3. Perfil de lead prioritario",
    "## 4. Criterios para elegir los primeros 10 contactos",
    "## 5. Datos mínimos a registrar manualmente",
    "## 6. Mensaje inicial para escuela de cine",
    "## 7. Mensaje inicial para productora",
    "## 8. Mensaje inicial para montador o ayudante de montaje",
    "## 9. Respuesta si preguntan si ya está terminado",
    "## 10. Respuesta si preguntan por DaVinci, Avid o Premiere",
    "## 11. Respuesta si preguntan por privacidad",
    "## 12. Respuesta si preguntan por precio",
    "## 13. Respuesta si preguntan por CID",
    "## 14. Preguntas para la conversación",
    "## 15. Plantilla manual de seguimiento",
    "## 19. Próxima acción recomendada",
    "Contactar poco",
    "Contactar bien",
    "No automatizar todavía",
    "No hacer scraping todavía",
    "No abrir CRM todavía",
    "AILink Sync Dialogue es una herramienta independiente",
    "CID es la visión SaaS integral",
]

FORBIDDEN = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "STRIPE_SECRET",
    "SUPABASE_SERVICE_ROLE",
    "scrape automático",
    "email automático",
    "automatización n8n activa",
    "C:\\",
    "/mnt/",
    "\\\\wsl.localhost",
]


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_outreach_starter_pack_exists():
    assert DOC.exists()


def test_outreach_starter_pack_has_required_content():
    content = _doc()
    for text in REQUIRED:
        assert text in content


def test_outreach_starter_pack_blocks_automation_scope():
    content = _doc()
    for text in [
        "Esta fase no implementa CRM",
        "No automatizar todavía.",
        "No hacer scraping todavía.",
        "No abrir CRM todavía.",
    ]:
        assert text in content


def test_outreach_starter_pack_has_minimal_tracking_fields():
    content = _doc()
    for text in [
        "organización",
        "contacto",
        "rol",
        "tipo",
        "motivo_encaje",
        "estado",
        "fecha_contacto",
        "próxima_accion",
        "notas",
    ]:
        assert text in content


def test_outreach_starter_pack_has_no_forbidden_runtime_terms():
    content = _doc()
    for text in FORBIDDEN:
        assert text not in content


def test_outreach_starter_pack_does_not_overpromise():
    content = _doc().lower()
    for text in [
        "producto público terminado",
        "integración directa inmediata",
        "automatización completa garantizada",
        "subida segura de material sensible",
        "crm listo",
        "supabase listo",
        "formulario listo",
    ]:
        assert text not in content
