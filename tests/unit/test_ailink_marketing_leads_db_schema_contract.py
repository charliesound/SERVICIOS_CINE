from pathlib import Path


DOC_PATH = Path("docs/product/marketing/ailink_marketing_leads_db_schema_contract_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_schema_contract_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Marketing Leads — PostgreSQL Schema Contract v1" in DOC


def test_phase_is_documental_contract_only():
    required = [
        "Esta fase es documental y de contrato",
        "No crea tablas físicas",
        "no crea migraciones reales",
        "no implementa backend",
        "no implementa frontend",
        "no implementa CRM",
        "no implementa formularios",
        "no implementa workflows de n8n",
        "no modifica runtime",
    ]
    for text in required:
        assert text in DOC


def test_keeps_marketing_leads_separated_from_cid():
    required = [
        "Los leads de marketing pertenecen a una capa separada de AILinkCinema",
        "Usuarios reales de CID SaaS",
        "Billing de CID",
        "Créditos IA de CID",
        "Jobs IA de CID",
        "Convertir un lead en cliente de CID",
    ]
    for text in required:
        assert text in DOC


def test_defines_expected_logical_tables():
    for table in [
        "marketing_leads",
        "marketing_lead_consents",
        "marketing_lead_events",
        "marketing_lead_notes",
    ]:
        assert table in DOC


def test_marketing_leads_required_fields_are_defined():
    for field in [
        "id",
        "created_at",
        "updated_at",
        "source",
        "status",
        "full_name",
        "email",
        "consent_reference",
    ]:
        assert field in DOC


def test_lead_statuses_are_operational_and_simple():
    for status in [
        "new",
        "qualified",
        "contacted",
        "demo_scheduled",
        "demo_done",
        "beta_candidate",
        "beta_active",
        "not_now",
        "not_fit",
        "do_not_contact",
        "converted",
        "archived",
    ]:
        assert status in DOC


def test_consent_table_tracks_legal_operational_context():
    required = [
        "marketing_lead_consents",
        "consent_type",
        "consent_text_version",
        "accepted",
        "accepted_at",
        "legal_basis",
        "withdrawn_at",
        "beta_contact",
        "commercial_updates",
        "privacy_policy_acceptance",
    ]
    for text in required:
        assert text in DOC


def test_events_cover_manual_sales_workflow():
    for event_type in [
        "lead_created",
        "consent_recorded",
        "status_changed",
        "priority_changed",
        "manual_email_sent",
        "manual_call_done",
        "demo_scheduled",
        "demo_completed",
        "feedback_received",
        "do_not_contact_set",
        "converted_to_customer",
        "archived",
    ]:
        assert event_type in DOC


def test_privacy_rules_exclude_sensitive_or_unneeded_data():
    required = [
        "Material audiovisual",
        "Guiones",
        "Contratos",
        "Datos bancarios",
        "Datos de facturación",
        "Documentos de identidad",
        "Información personal sensible innecesaria",
    ]
    for text in required:
        assert text in DOC


def test_email_normalization_and_duplicate_rules_are_defined():
    required = [
        "Normalización de email",
        "Trim de espacios",
        "Conversión a minúsculas",
        "Unicidad lógica por email normalizado",
        "No debe crearse un segundo lead activo por defecto",
        "conservarse el historial anterior",
    ]
    for text in required:
        assert text in DOC


def test_n8n_is_orchestrator_not_source_of_truth():
    required = [
        "n8n podrá usar este contrato",
        "n8n no debe ser el CRM principal",
        "La fuente de verdad será PostgreSQL",
    ]
    for text in required:
        assert text in DOC


def test_contract_does_not_contain_real_database_implementation():
    forbidden = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "Base.metadata.create_all",
        "op.create_table",
        "docker compose",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
