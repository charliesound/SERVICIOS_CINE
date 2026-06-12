from pathlib import Path


DOC_PATH = Path("docs/product/marketing/ailink_marketing_leads_n8n_workflow_contract_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_n8n_workflow_contract_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Marketing Leads — n8n Workflow Contract v1" in DOC


def test_phase_is_documental_contract_only():
    required = [
        "Esta fase es documental y de contrato",
        "No crea workflows reales de n8n",
        "no crea JSON importable en n8n",
        "no llama webhooks reales",
        "no crea credenciales",
        "no toca PostgreSQL real",
        "no crea tablas",
        "no crea migraciones",
        "no implementa backend",
        "no implementa frontend",
        "no implementa CRM",
        "no toca Docker",
        "no toca runtime",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_depends_on_previous_marketing_lead_contracts():
    required = [
        "AILINK.MARKETING.LEADS.N8N.POSTGRES.CRM.SPEC.PHASE1",
        "AILINK.MARKETING.LEADS.DB.SCHEMA.CONTRACT.PHASE2",
        "marketing_leads",
        "marketing_lead_consents",
        "marketing_lead_events",
        "marketing_lead_notes",
    ]
    for text in required:
        assert text in DOC


def test_n8n_is_orchestrator_not_crm_or_source_of_truth():
    required = [
        "n8n debe actuar como orquestador de entrada",
        "no como CRM",
        "no como fuente de verdad",
        "La fuente de verdad será PostgreSQL",
        "El CRM privado será la interfaz de gestión manual",
    ]
    for text in required:
        assert text in DOC


def test_expected_logical_flow_is_defined():
    for step in [
        "Recibir lead",
        "Validar campos mínimos",
        "Normalizar email",
        "Clasificar fuente del lead",
        "Consultar si el email ya existe",
        "Insertar o actualizar lead lógico",
        "Registrar consentimiento",
        "Registrar evento operativo",
        "Notificar internamente",
        "Devolver respuesta segura",
    ]:
        assert step in DOC


def test_expected_input_fields_are_defined():
    for field in [
        "full_name",
        "email",
        "source",
        "beta_contact_consent",
        "privacy_policy_acceptance",
        "organization_type",
        "interest_area",
        "main_problem",
        "upcoming_project",
        "demo_interest",
        "beta_interest",
    ]:
        assert field in DOC


def test_email_normalization_and_duplicate_logic_are_required():
    required = [
        "Eliminar espacios al principio y al final",
        "Convertir a minúsculas",
        "Validar formato básico",
        "Si el email normalizado no existe",
        "Si el email normalizado ya existe",
        "No crear un segundo lead activo por defecto",
        "lead_created",
        "lead_updated",
    ]
    for text in required:
        assert text in DOC


def test_consent_is_separated_and_required_for_contactable_leads():
    required = [
        "Consentimiento para responder a una solicitud beta",
        "Aceptación de política de privacidad",
        "Consentimiento para comunicaciones comerciales futuras",
        "El consentimiento comercial no debe estar preaceptado",
        "Si no hay consentimiento beta o aceptación de privacidad",
        "no debe entrar como lead contactable",
    ]
    for text in required:
        assert text in DOC


def test_security_and_privacy_boundaries_are_explicit():
    required = [
        "Guardar material audiovisual",
        "Pedir subida de archivos",
        "Guardar guiones",
        "Guardar contratos",
        "Guardar documentos de identidad",
        "Guardar datos bancarios",
        "Mezclar leads con usuarios CID",
        "Escribir en tablas de CID SaaS",
        "Usar credenciales hardcodeadas",
    ]
    for text in required:
        assert text in DOC


def test_public_response_and_error_handling_are_safe():
    required = [
        "Las respuestas al usuario deben ser genéricas",
        "Sin detalles técnicos",
        "Sin promesas comerciales cerradas",
        "Sin indicar que el usuario ya existía",
        "No exponer errores internos al usuario",
    ]
    for text in required:
        assert text in DOC


def test_future_acceptance_criteria_are_defined():
    required = [
        "No usar n8n como CRM",
        "No usar n8n como fuente de verdad",
        "Validar campos mínimos",
        "Normalizar email",
        "Detectar duplicados por email normalizado",
        "Registrar consentimiento separado",
        "Registrar evento inicial",
        "No crear leads contactables sin consentimiento",
        "No escribir en tablas de CID SaaS",
        "No incluir credenciales en el repo",
    ]
    for text in required:
        assert text in DOC


def test_contract_does_not_contain_real_n8n_or_runtime_implementation():
    forbidden = [
        "\"nodes\"",
        "\"connections\"",
        "\"credentials\"",
        "workflowId",
        "webhookId",
        "http://localhost:5678",
        "n8n import",
        "docker compose",
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "op.create_table",
        "Base.metadata.create_all",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
