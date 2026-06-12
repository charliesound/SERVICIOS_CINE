from pathlib import Path


DOC_PATH = Path("docs/product/marketing/ailink_marketing_leads_operations_index_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_operations_index_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Marketing Leads — Operations Index v1" in DOC


def test_phase_is_documental_index_only():
    required = [
        "Esta fase es documental e índice operativo",
        "No implementa n8n real",
        "no implementa CRM real",
        "no crea frontend",
        "no crea backend",
        "no crea formulario real",
        "no crea tablas reales",
        "no crea migraciones",
        "no toca Docker",
        "no toca runtime",
        "no toca configuración",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_references_all_marketing_leads_contracts():
    required = [
        "ailink_marketing_leads_n8n_postgres_crm_spec_v1.md",
        "ailink_marketing_leads_db_schema_contract_v1.md",
        "ailink_marketing_leads_n8n_workflow_contract_v1.md",
        "ailink_marketing_leads_crm_private_ui_spec_v1.md",
    ]
    for text in required:
        assert text in DOC


def test_decisions_are_explicit():
    required = [
        "No contactar escuelas de forma fuerte antes de septiembre",
        "Junio, julio y agosto se orientan a captación pasiva",
        "Septiembre será el momento natural para demos",
        "n8n encaja como orquestador",
        "PostgreSQL será la fuente de verdad de leads",
        "El CRM privado será la interfaz manual",
        "CID SaaS debe permanecer separado",
    ]
    for text in required:
        assert text in DOC


def test_no_implementation_yet_list_is_present():
    required = [
        "Workflow real de n8n",
        "Webhook real",
        "JSON importable de n8n",
        "Credenciales reales",
        "Formulario real conectado",
        "CRM real",
        "Migraciones reales",
        "Tablas reales",
        "Automatización de emails",
        "Scraping",
        "Integración con CID SaaS",
        "Pagos",
    ]
    for text in required:
        assert text in DOC


def test_activation_conditions_are_defined():
    required = [
        "Condiciones para activar n8n real",
        "Landing o formulario beta con texto revisado",
        "Política de privacidad y consentimiento preparados",
        "Producto demo suficientemente claro",
        "Condiciones para activar CRM real",
        "Existan leads suficientes",
        "Haya demos programadas",
    ]
    for text in required:
        assert text in DOC


def test_september_checklist_is_defined():
    required = [
        "Checklist de septiembre",
        "Demo local de AILink Sync Dialogue funcionando",
        "Guion de demo comercial de 5 a 7 minutos",
        "Landing revisada",
        "CTA beta claro",
        "Texto legal mínimo revisado",
        "Calendario de demos",
        "Plantilla de feedback post-demo",
    ]
    for text in required:
        assert text in DOC


def test_product_checklist_before_strong_marketing_is_defined():
    required = [
        "Checklist de producto antes de marketing fuerte",
        "Escaneo local de carpeta",
        "Detección de archivos de vídeo y audio",
        "Lectura de metadata",
        "Sugerencias de matching",
        "Reporte HTML",
        "Demo end-to-end reproducible",
        "Explicación clara de límites actuales",
    ]
    for text in required:
        assert text in DOC


def test_next_phase_points_back_to_product_demo_readiness():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "Auditar si la demo actual está lista para enseñar",
        "Preparar una demo de 5 a 7 minutos",
        "Marketing debe acompañar al producto",
    ]
    for text in required:
        assert text in DOC


def test_contract_does_not_contain_real_runtime_implementation():
    forbidden = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "op.create_table",
        "Base.metadata.create_all",
        "docker compose",
        "n8n import",
        "\"nodes\"",
        "\"connections\"",
        "\"credentials\"",
        "FastAPI(",
        "@router.",
        "app.post(",
        "app.get(",
        "useState(",
        "useEffect(",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
