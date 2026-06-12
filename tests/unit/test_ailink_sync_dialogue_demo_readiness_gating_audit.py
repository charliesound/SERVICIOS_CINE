from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_readiness_gating_audit_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_gating_audit_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Readiness Gating Audit v1" in DOC


def test_phase_is_documental_audit_only():
    required = [
        "Esta fase es documental y de auditoría",
        "No implementa código",
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


def test_relationship_with_phase7_is_explicit():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "Qué se puede enseñar ya",
        "Qué debe presentarse como beta",
        "Qué no se debe prometer",
        "Estructura de demo comercial de 5 a 7 minutos",
        "si un gate crítico falla, la demo no debe enseñarse",
    ]
    for text in required:
        assert text in DOC


def test_gate_classification_is_defined():
    required = [
        "CRITICAL: bloquea la demo",
        "HIGH: puede bloquear",
        "MEDIUM: no bloquea si se explica bien",
        "LOW: mejora futura",
        "Los gates críticos son bloqueantes",
    ]
    for text in required:
        assert text in DOC


def test_critical_privacy_and_tech_gates_are_present():
    required = [
        "GATE-PRIVACY-001",
        "No usar material de cliente",
        "GATE-PRIVACY-002",
        "No subir material sensible",
        "GATE-TECH-001",
        "Ejecución repetible",
        "GATE-TECH-002",
        "Outputs comprensibles",
        "La ejecución no depende de GPU",
        "La ejecución no depende de n8n",
        "La ejecución no depende de Docker",
        "La ejecución no depende de CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_critical_commercial_gates_are_present():
    required = [
        "GATE-COMM-001",
        "No venderlo como sincronizador final",
        "GATE-COMM-002",
        "No prometer funciones futuras como actuales",
        "GATE-COMM-003",
        "Mensaje beta claro",
        "Se evita prometer sincronización perfecta",
        "Transcripción robusta",
        "Matching por waveform",
        "OCR de claqueta",
        "Export XML/AAF/EDL final",
    ]
    for text in required:
        assert text in DOC


def test_no_go_and_go_conditions_are_defined():
    required = [
        "No-go conditions",
        "Hay material de cliente",
        "Hay datos personales reales",
        "El flujo falla de forma intermitente",
        "Se vende como sincronizador automático final",
        "Go conditions",
        "Usa material seguro",
        "Ejecuta end-to-end",
        "El mensaje local-first es claro",
        "Hay mecanismo de feedback posterior",
    ]
    for text in required:
        assert text in DOC


def test_decision_matrix_is_defined():
    required = [
        "Matriz de decisión",
        "Resultado PASS",
        "Resultado LIMITED PASS",
        "Resultado FAIL",
        "Todos los gates críticos pasan",
        "Falla cualquier gate crítico",
        "El mensaje comercial induce a error",
    ]
    for text in required:
        assert text in DOC


def test_review_checklist_and_evidence_are_defined():
    required = [
        "Checklist de revisión antes de demo",
        "GATE-PRIVACY-001 revisado",
        "GATE-COMM-002 revisado",
        "No-go conditions revisadas",
        "Matriz de decisión aplicada",
        "Evidencias mínimas recomendadas",
        "Captura del reporte HTML",
        "Confirmación de que no se usa material de cliente",
        "Esta fase no crea esas evidencias",
    ]
    for text in required:
        assert text in DOC


def test_next_steps_keep_focus_before_more_features():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SAFE_SAMPLE.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8",
        "no construir más funcionalidades hasta tener una demo interna clasificada",
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
