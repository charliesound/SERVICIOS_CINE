from pathlib import Path


DOC_PATH = Path("docs/product/marketing/ailink_marketing_leads_crm_private_ui_spec_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_crm_private_ui_spec_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Marketing Leads — Private CRM UI Spec v1" in DOC


def test_phase_is_documental_spec_only():
    required = [
        "Esta fase es documental y de especificación",
        "No implementa CRM real",
        "no implementa frontend",
        "no implementa backend",
        "no crea rutas",
        "no crea componentes React",
        "no crea tablas",
        "no crea migraciones",
        "no crea workflow n8n",
        "no toca PostgreSQL real",
        "no toca Docker",
        "no toca runtime",
        "no toca configuración",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_depends_on_previous_marketing_leads_contracts():
    required = [
        "AILINK.MARKETING.LEADS.N8N.POSTGRES.CRM.SPEC.PHASE1",
        "AILINK.MARKETING.LEADS.DB.SCHEMA.CONTRACT.PHASE2",
        "AILINK.MARKETING.LEADS.N8N.WORKFLOW.CONTRACT.PHASE3",
    ]
    for text in required:
        assert text in DOC


def test_crm_is_private_and_not_cid():
    required = [
        "No debe ser una parte pública de la landing",
        "No debe ser CID SaaS",
        "No debe acceder a proyectos audiovisuales de clientes",
        "No debe acceder a billing, créditos IA, jobs IA",
        "Mantener separación con CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_minimum_screens_are_defined():
    for screen in [
        "Dashboard privado",
        "Lista de leads",
        "Detalle de lead",
        "Vista de notas",
        "Vista de eventos",
        "Vista de seguimiento",
        "Vista de configuración mínima",
    ]:
        assert screen in DOC


def test_lead_list_columns_and_filters_are_defined():
    required = [
        "Nombre",
        "Email",
        "Organización",
        "Tipo de organización",
        "Área de interés",
        "Estado",
        "Prioridad",
        "Fuente",
        "Próximo seguimiento",
        "status",
        "priority",
        "organization_type",
        "interest_area",
        "next_follow_up_at",
    ]
    for text in required:
        assert text in DOC


def test_lead_detail_and_actions_are_defined():
    required = [
        "La ficha de lead debe mostrar",
        "Consentimientos",
        "Eventos",
        "Notas",
        "Cambiar status",
        "Cambiar priority",
        "Añadir nota",
        "Programar seguimiento",
        "Marcar do_not_contact",
        "Archivar lead",
    ]
    for text in required:
        assert text in DOC


def test_statuses_priorities_and_notes_are_defined():
    for text in [
        "new",
        "qualified",
        "contacted",
        "demo_scheduled",
        "demo_done",
        "beta_candidate",
        "beta_active",
        "do_not_contact",
        "converted",
        "archived",
        "high",
        "medium",
        "low",
        "unknown",
        "qualification",
        "feedback",
        "follow_up",
    ]:
        assert text in DOC


def test_consent_privacy_and_do_not_contact_are_required():
    required = [
        "Consentimiento para contacto beta",
        "Aceptación de política de privacidad",
        "Consentimiento comercial futuro",
        "Si do_not_contact está activo",
        "bloquear acciones comerciales",
        "No deben almacenar material audiovisual",
        "datos bancarios",
        "información sensible innecesaria",
    ]
    for text in required:
        assert text in DOC


def test_september_view_supports_current_strategy():
    required = [
        "Vista de septiembre",
        "Leads high priority",
        "Leads de escuelas",
        "Leads de productoras",
        "Leads con demo_interest",
        "Leads con upcoming_project",
        "Leads beta_candidate",
    ]
    for text in required:
        assert text in DOC


def test_future_acceptance_criteria_are_defined():
    required = [
        "No mezclar CRM de leads con CID SaaS",
        "No exponer CRM públicamente",
        "Mostrar lista de leads",
        "Mostrar detalle de lead",
        "Permitir filtros principales",
        "Permitir cambios de status",
        "Permitir cambios de priority",
        "Permitir notas manuales",
        "Permitir seguimiento",
        "Respetar do_not_contact",
        "Mostrar consentimiento",
        "Registrar eventos",
        "No depender de n8n como panel operativo",
    ]
    for text in required:
        assert text in DOC


def test_contract_does_not_contain_real_ui_or_runtime_implementation():
    forbidden = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "op.create_table",
        "Base.metadata.create_all",
        "docker compose",
        "npm install",
        "pnpm install",
        "useState(",
        "useEffect(",
        "FastAPI(",
        "@router.",
        "app.post(",
        "app.get(",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
