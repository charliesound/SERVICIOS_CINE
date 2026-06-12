from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_readiness_gating_evidence_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_gating_evidence_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Readiness Gating Evidence v1" in DOC


def test_phase_is_documental_evidence_only():
    required = [
        "Esta fase es documental y de evidencias",
        "No implementa código",
        "no ejecuta demo",
        "no modifica scanner",
        "no modifica matching",
        "no modifica exports",
        "no modifica reportes",
        "no crea UI real",
        "no crea backend",
        "no crea frontend",
        "no crea instalador",
        "no crea n8n",
        "no crea CRM",
        "no toca PostgreSQL real",
        "no toca Docker",
        "no toca runtime",
        "no toca configuración",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_relationship_with_previous_phases_is_explicit():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1",
        "PASS, LIMITED PASS o FAIL",
        "qué evidencias mínimas deben existir",
    ]
    for text in required:
        assert text in DOC


def test_evidence_principles_and_forbidden_content_are_defined():
    required = [
        "Una evidencia no es una promesa",
        "concreta, revisable, localizable, comprensible, no sensible",
        "Material audiovisual de cliente",
        "Datos personales reales",
        "Credenciales",
        "Tokens",
        "Promesas comerciales no implementadas",
        "confundan AILink Sync Dialogue con CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_critical_evidence_items_are_defined():
    required = [
        "EV-PRIVACY-001",
        "Declaración de material seguro",
        "EV-PRIVACY-002",
        "Confirmación local-first",
        "EV-TECH-001",
        "Registro de ejecución repetible",
        "EV-OUTPUT-001",
        "Lista de outputs generados",
        "EV-REPORT-001",
        "Captura o revisión del reporte HTML",
    ]
    for text in required:
        assert text in DOC


def test_commercial_evidence_items_are_defined():
    required = [
        "EV-COMM-001",
        "Mensaje de apertura",
        "EV-COMM-002",
        "Lista de funciones no prometidas",
        "EV-COMM-003",
        "Mensaje beta",
        "Transcripción robusta",
        "Matching por waveform",
        "OCR de claqueta",
        "Export XML/AAF/EDL final",
        "Integración real con CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_operational_feedback_and_decision_evidence_are_defined():
    required = [
        "EV-OPS-001",
        "Guion o escaleta de 5 a 7 minutos",
        "EV-OPS-002",
        "Preguntas y respuestas preparadas",
        "EV-FEEDBACK-001",
        "Mecanismo de feedback",
        "Evidencia de decisión final",
        "fecha de revisión",
        "público permitido",
    ]
    for text in required:
        assert text in DOC


def test_decision_template_and_result_interpretation_are_present():
    required = [
        "AILink Sync Dialogue demo gating decision",
        "Resultado: PASS / LIMITED PASS / FAIL",
        "GATE-PRIVACY-001",
        "GATE-COMM-003",
        "Riesgos pendientes",
        "Siguiente acción",
        "### PASS",
        "### LIMITED PASS",
        "### FAIL",
        "Puede enseñarse a una persona de confianza",
        "Puede enseñarse solo internamente",
        "No debe enseñarse",
        "Se vende como sincronizador final",
        "Se prometen funciones futuras como actuales",
    ]
    for text in required:
        assert text in DOC


def test_evidence_not_to_create_yet_is_defined():
    required = [
        "Evidencias que no conviene crear todavía",
        "integración real con NLE",
        "instalador",
        "CRM",
        "n8n",
        "SaaS multiusuario",
        "procesamiento cloud",
        "transcripción robusta",
        "waveform matching",
        "OCR de claqueta",
        "serían engañosas si se presentan como actuales",
    ]
    for text in required:
        assert text in DOC


def test_next_phases_keep_focus_on_evidence_before_features():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.3",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SAFE_SAMPLE.PHASE7.3",
        "AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8",
        "preparar primero una ejecución interna de evidencias",
    ]
    for text in required:
        assert text in DOC


def test_document_does_not_include_runtime_implementation_commands():
    forbidden = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "op.create_table",
        "Base.metadata.create_all",
        "docker compose",
        "n8n import",
        "npm install",
        "pnpm install",
        "ffmpeg -i",
        "uvicorn",
        "FastAPI(",
        "@router.",
        "app.post(",
        "useState(",
        "useEffect(",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
