"""Tests for the AILink Sync Dialogue beta leads operations runbook."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
RUNBOOK = ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_beta_leads_operations_runbook_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "ailink_sync_dialogue_beta_form_spec_v1.md",
    ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_legal_web_texts_spec_v1.md",
    ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_landing_legal_integration_spec_v1.md",
    ROOT / "docs" / "product" / "social" / "ailink_sync_dialogue_social_launch_pack_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_assembly_runbook_v1.md",
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html",
]

REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Beta Leads Operations Runbook v1",
    "## 1. Objetivo",
    "## 3. Non-goals",
    "## 4. Principio operativo",
    "## 6. Estados operativos del lead",
    "## 7. Criterios de cualificación",
    "## 8. Datos mínimos a registrar manualmente",
    "## 9. Datos que no deben registrarse manualmente",
    "## 10. Hoja manual temporal",
    "## 11. Respuesta inicial recomendada",
    "## 12. Preguntas de cualificación",
    "## 13. Flujo operativo manual",
    "## 14. Preparación de demo",
    "## 15. Feedback posterior a demo",
    "## 17. Política no_contactar",
    "## 20. Separación AILink Sync Dialogue y CID",
    "## 22. Señales para pasar a CRM o Supabase real",
    "## 23. Criterios de aceptación",
]

REQUIRED_TERMS = [
    "beta privada",
    "formulario real",
    "CRM",
    "Supabase",
    "no_contactar",
    "lead_id",
    "qualification_level",
    "next_action_date",
    "No se debe pedir ni recibir material audiovisual real",
    "No guardar material audiovisual",
    "No vender AILink Sync Dialogue como CID",
    "No implementar CRM",
    "No implementar Supabase",
    "No implementa formulario",
    "No toca runtime",
]

FORBIDDEN_RUNTIME_TERMS = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "service role",
    "secret key",
    "payment intent",
    "checkout session",
]

FORBIDDEN_UNSAFE_CLAIMS = [
    "subir material audiovisual obligatorio",
    "acceso inmediato garantizado",
    "producto final garantizado",
    "CRM implementado",
    "Supabase implementado",
    "formulario funcional implementado",
    "automatizaciones activas",
]


def _runbook() -> str:
    return RUNBOOK.read_text(encoding="utf-8")


def test_beta_leads_operations_runbook_exists():
    assert RUNBOOK.exists()


def test_beta_leads_operations_runbook_references_existing_files():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_beta_leads_operations_runbook_has_required_headings():
    content = _runbook()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_beta_leads_operations_runbook_has_required_terms():
    content = _runbook()
    for term in REQUIRED_TERMS:
        assert term in content


def test_beta_leads_operations_runbook_defines_statuses():
    content = _runbook()
    for status in [
        "nuevo",
        "pendiente_respuesta",
        "cualificacion_inicial",
        "apto_beta",
        "beta_prioritaria",
        "demo_propuesta",
        "demo_agendada",
        "demo_realizada",
        "esperando_feedback",
        "descartado",
        "no_contactar",
    ]:
        assert status in content


def test_beta_leads_operations_runbook_defines_qualification_levels():
    content = _runbook()
    assert "### 7.1 Encaje alto" in content
    assert "### 7.2 Encaje medio" in content
    assert "### 7.3 Encaje bajo" in content
    for text in [
        "Escuela de cine",
        "Productora",
        "Equipo de postproducción",
        "Profesional audiovisual individual",
        "Interés genérico sin relación con audiovisual",
    ]:
        assert text in content


def test_beta_leads_operations_runbook_defines_manual_sheet_columns():
    content = _runbook()
    for column in [
        "lead_id",
        "created_at",
        "source",
        "email_or_contact",
        "editing_tool",
        "has_separate_audio",
        "has_timecode",
        "main_problem",
        "beta_contact_permission",
        "marketing_permission",
        "next_action_date",
    ]:
        assert column in content


def test_beta_leads_operations_runbook_forbids_sensitive_collection():
    content = _runbook()
    for text in [
        "Material audiovisual",
        "Enlaces a material sensible",
        "Guiones completos",
        "Contratos",
        "Presupuestos",
        "Datos bancarios",
        "Documentos de identidad",
        "Contraseñas",
        "Accesos a discos",
    ]:
        assert text in content


def test_beta_leads_operations_runbook_includes_response_template():
    content = _runbook()
    for text in [
        "Hola, gracias por tu interés",
        "beta privada",
        "Todavía no necesitamos que envíes material audiovisual",
        "qué editor usas",
        "si trabajas con audio separado",
        "si usas timecode",
    ]:
        assert text in content


def test_beta_leads_operations_runbook_includes_demo_preparation_limits():
    content = _runbook()
    for text in [
        "No prometer waveform sync",
        "No prometer transcripción",
        "No prometer claqueta visual",
        "No prometer integración directa con editores",
        "No pedir archivos del interesado",
    ]:
        assert text in content


def test_beta_leads_operations_runbook_keeps_ailink_and_cid_separate():
    content = _runbook()
    assert "AILink Sync Dialogue debe gestionarse como herramienta independiente" in content
    assert "No vender AILink Sync Dialogue como CID" in content
    assert "No usar cuenta CID como requisito de beta" in content
    assert "No mezclar leads beta con usuarios internos del SaaS CID" in content


def test_beta_leads_operations_runbook_has_no_forbidden_runtime_terms():
    content = _runbook()
    for term in FORBIDDEN_RUNTIME_TERMS:
        assert term not in content


def test_beta_leads_operations_runbook_has_no_unsafe_claims():
    content = _runbook().lower()
    for claim in FORBIDDEN_UNSAFE_CLAIMS:
        assert claim.lower() not in content


def test_beta_leads_operations_runbook_has_no_local_paths_or_windows_paths():
    content = _runbook()
    assert "/mnt/" not in content
    assert "C:\\" not in content
    assert "\\\\wsl.localhost" not in content
