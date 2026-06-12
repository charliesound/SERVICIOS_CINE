"""Tests for AILink Marketing Leads n8n + PostgreSQL + CRM spec."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DOC = ROOT / "docs" / "product" / "marketing" / "ailink_marketing_leads_n8n_postgres_crm_spec_v1.md"

REFERENCED_CONTEXT = [
    ROOT / "docs" / "product" / "launch" / "ailink_sync_dialogue_commercial_readiness_qa_v1.md",
    ROOT / "docs" / "product" / "launch" / "ailink_sync_dialogue_launch_index_summary_v1.md",
    ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_outreach_starter_pack_v1.md",
]

REQUIRED = [
    "# AILink Marketing Leads — n8n + PostgreSQL + Private CRM Spec v1",
    "## 2. Decisión de arquitectura",
    "Landing pública / formulario beta",
    "n8n recibe el lead",
    "PostgreSQL guarda el lead",
    "CRM privado permite revisar y gestionar leads",
    "## 3. Diferencia entre n8n, PostgreSQL y CRM",
    "PostgreSQL es la base de datos",
    "n8n es el orquestador",
    "El CRM privado es el panel de gestión",
    "## 4. Separación con CID",
    "No mezclar leads de marketing con usuarios reales de CID",
    "## 5. Tabla conceptual `marketing_leads`",
    "consent_contact",
    "privacy_version",
    "no_contactar",
    "## 6. Estados del lead",
    "interesado_septiembre",
    "demo_agendada",
    "beta_aprobada",
    "## 7. Workflow n8n futuro: captura de lead",
    "Evitar duplicados por email",
    "## 8. Workflow n8n futuro: resumen semanal",
    "## 9. Workflow n8n futuro: preparación de septiembre",
    "## 10. CRM privado futuro",
    "Exportar CSV",
    "## 11. Formulario futuro de landing",
    "No envíes material audiovisual",
    "## 15. RGPD operativo básico",
    "## 17. No-goals",
    "No implementa n8n real",
    "No crea tablas reales",
    "No implementa CRM",
]

FORBIDDEN = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "Stripe",
    "checkout",
    "ComfyUI",
    "Ollama",
    "Qdrant",
    "SUPABASE_SERVICE_ROLE",
    "SECRET_KEY",
    "C:\\",
    "/mnt/",
    "\\\\wsl.localhost",
]


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_marketing_leads_spec_exists():
    assert DOC.exists()


def test_marketing_leads_spec_context_files_exist():
    for path in REFERENCED_CONTEXT:
        assert path.exists(), path


def test_marketing_leads_spec_has_required_content():
    content = _doc()
    for text in REQUIRED:
        assert text in content


def test_marketing_leads_spec_defines_minimal_fields():
    content = _doc()
    for text in [
        "name",
        "email",
        "organization",
        "profile_type",
        "tools_used",
        "main_problem",
        "wants_september_beta",
        "status",
        "priority",
        "last_contacted_at",
        "next_action_at",
    ]:
        assert text in content


def test_marketing_leads_spec_defines_statuses():
    content = _doc()
    for text in [
        "nuevo",
        "pendiente_revision",
        "cualificado",
        "interesado_septiembre",
        "contactado",
        "respondio",
        "demo_agendada",
        "beta_aprobada",
        "no_interesado",
        "no_contactar",
        "descartado",
    ]:
        assert text in content


def test_marketing_leads_spec_blocks_runtime_scope():
    content = _doc()
    for text in [
        "Esta fase no implementa workflows reales de n8n",
        "No implementa n8n real",
        "No crea tablas reales",
        "No implementa formulario real",
        "No conecta PostgreSQL real",
        "No toca CID",
    ]:
        assert text in content


def test_marketing_leads_spec_has_no_forbidden_terms():
    content = _doc()
    for text in FORBIDDEN:
        assert text not in content


def test_marketing_leads_spec_does_not_overpromise():
    content = _doc().lower()
    for text in [
        "workflow real creado",
        "tabla creada",
        "crm implementado",
        "formulario publicado",
        "email real enviado",
        "campaña automática activa",
        "scraping activo",
        "cuenta cid creada automáticamente",
    ]:
        assert text not in content
