from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_readiness_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_demo_readiness_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Readiness v1" in DOC


def test_phase_is_documental_and_no_runtime_changes():
    required = [
        "Esta fase es documental y de preparación comercial",
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


def test_current_known_product_assets_are_listed():
    required = [
        "Scanner local de archivos",
        "Export JSON",
        "Export CSV",
        "Sugerencias de matching",
        "Reporte HTML imprimible",
        "Fixture demo reproducible",
        "Runner demo end-to-end",
        "Demo con metadata real mínima",
    ]
    for text in required:
        assert text in DOC


def test_showable_beta_and_not_to_promise_sections_exist():
    required = [
        "Qué se puede enseñar ya",
        "Qué debe presentarse como beta",
        "Qué no se debe prometer todavía",
        "Sincronización perfecta en todos los casos",
        "Export XML/AAF/EDL definitivo",
        "Transcripción robusta",
        "Detección automática de claqueta",
        "Matching por waveform",
        "Instalador Mac/Windows",
    ]
    for text in required:
        assert text in DOC


def test_demo_structure_for_five_to_seven_minutes_is_defined():
    required = [
        "Demo comercial de 5 a 7 minutos",
        "Minuto 0:00–0:45",
        "Minuto 0:45–1:30",
        "Minuto 1:30–3:30",
        "Minuto 3:30–5:00",
        "Minuto 5:00–6:15",
        "Minuto 6:15–7:00",
    ]
    for text in required:
        assert text in DOC


def test_demo_checklists_are_defined():
    required = [
        "Checklist antes de enseñar a terceros",
        "Checklist técnico de demo",
        "Checklist comercial de demo",
        "Repo limpio",
        "No hay datos personales reales",
        "La demo no depende de red",
        "La demo no depende de GPU",
        "Se evita vender humo",
    ]
    for text in required:
        assert text in DOC


def test_expected_questions_and_safe_answers_are_defined():
    required = [
        "Preguntas esperables",
        "¿Sincroniza audio y vídeo automáticamente?",
        "¿Lee timecode?",
        "¿Funciona sin subir material?",
        "Respuestas recomendadas",
        "no debe venderse todavía como sincronizador perfecto",
        "local-first",
    ]
    for text in required:
        assert text in DOC


def test_ready_and_not_ready_criteria_are_defined():
    required = [
        "Criterios de demo lista",
        "Ejecuta end-to-end sin errores",
        "Produce outputs comprensibles",
        "No promete funciones no implementadas",
        "Criterios para no enseñar todavía",
        "se vende como sincronizador final",
        "No hay material de ejemplo seguro",
    ]
    for text in required:
        assert text in DOC


def test_next_steps_prioritize_gating_before_more_features():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8",
        "La recomendación inmediata es hacer un gating audit",
    ]
    for text in required:
        assert text in DOC


def test_document_does_not_include_implementation_commands():
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
