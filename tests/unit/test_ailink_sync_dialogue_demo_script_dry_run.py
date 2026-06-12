from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_script_dry_run_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_dry_run_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Script Dry Run v1" in DOC


def test_phase_is_documental_dry_run_only():
    required = [
        "Esta fase es documental y de ensayo",
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
        "no graba vídeo público",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_references_complete_phase_chain():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.4",
    ]
    for text in required:
        assert text in DOC


def test_status_and_audience_are_bounded():
    required = [
        "LIMITED PASS",
        "Subir a PASS interno solo si",
        "No subir a PASS público en esta fase",
        "Ensayo individual",
        "Ensayo interno sin público",
        "persona de confianza",
        "Escuelas de cine",
        "Productoras externas",
        "Leads fríos",
        "Vídeo promocional público",
        "Demo comercial con precio cerrado",
    ]
    for text in required:
        assert text in DOC


def test_material_limits_are_explicit():
    required = [
        "Metadata demo controlada",
        "Report HTML controlado",
        "CSV de media files",
        "CSV de match suggestions",
        "Evidence run summary",
        "Material audiovisual de cliente",
        "Datos personales reales",
        "Credenciales",
        ".env",
        "n8n",
        "CRM",
        "CID SaaS",
        "Bases de datos reales",
    ]
    for text in required:
        assert text in DOC


def test_timed_structure_is_defined():
    required = [
        "entre 5 y 7 minutos",
        "0:00-0:40 Apertura",
        "0:40-1:20 Problema",
        "1:20-2:10 Qué hace hoy",
        "2:10-3:10 Evidence run real",
        "3:10-4:20 Lectura del reporte",
        "4:20-5:10 Explicación del e2e dummy",
        "5:10-6:00 Límites honestos",
        "6:00-6:45 Qué feedback pedir",
        "6:45-7:00 Cierre",
    ]
    for text in required:
        assert text in DOC


def test_rehearsal_checklist_covers_risks():
    required = [
        "Se dice LIMITED PASS",
        "Se dice beta controlada",
        "Se dice local-first",
        "Se dice outputs revisables",
        "Se explica que no es sincronización final",
        "Se explica que el e2e dummy puede dar 0 match suggestions",
        "Se explica que 0 match suggestions en dummy no es fallo",
        "Se pide feedback concreto",
        "Se evita vender",
        "Se evita precio cerrado",
    ]
    for text in required:
        assert text in DOC


def test_dangerous_and_required_phrases_are_present():
    required = [
        "Frases peligrosas que obligan a repetir el ensayo",
        "Esto sincroniza automáticamente todo",
        "Ya está listo para productoras",
        "Sustituye al montador",
        "Ya detecta claqueta visual",
        "Ya transcribe diálogos",
        "Ya se integra con DaVinci",
        "Esto ya está para LinkedIn como demo final",
        "Frases obligatorias",
        "No es sincronización automática final",
        "La demo usa material controlado",
        "La metadata demo enseña matching sugerido",
        "La e2e dummy enseña flujo local con outputs",
        "El objetivo de hoy es feedback, no venta",
    ]
    for text in required:
        assert text in DOC


def test_decision_matrix_has_pass_limited_fail():
    required = [
        "PASS interno",
        "LIMITED PASS mantenido",
        "FAIL",
        "Puede enseñarse a una persona de confianza",
        "No puede enseñarse todavía como demo pública",
        "Repetir ensayo",
        "No enseñar",
        "Volver a Phase7.4",
    ]
    for text in required:
        assert text in DOC


def test_dry_run_record_sheet_exists():
    required = [
        "Hoja de registro del dry run",
        "Fecha:",
        "Persona que ensaya:",
        "Duración total:",
        "¿Se dijo LIMITED PASS?: sí/no",
        "¿Se explicó 0 match suggestions en dummy?: sí/no",
        "Resultado: PASS interno / LIMITED PASS mantenido / FAIL",
        "Ajustes necesarios:",
        "Siguiente acción:",
    ]
    for text in required:
        assert text in DOC


def test_screen_order_and_self_control_are_defined():
    required = [
        "Orden de pantalla recomendado",
        "Report HTML controlado",
        "Tabla match suggestions",
        "Resumen evidence run",
        "JSON como primera pantalla",
        "Terminal como primera pantalla",
        "Preguntas de autocontrol después del ensayo",
        "¿La demo se entiende sin explicar código?",
        "¿La explicación de 0 matches queda natural?",
        "¿Está lista para una persona de confianza?",
    ]
    for text in required:
        assert text in DOC


def test_next_phase_is_trusted_person_feedback_or_repeat():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.TRUSTED.PERSON.FEEDBACK.PHASE7.6",
        "Enseñar la demo a una persona de confianza",
        "Registrar feedback real",
        "Repetir Phase7.5 tras ajustar guion",
        "No añadir funcionalidad nueva todavía",
        "El resultado máximo de esta fase es PASS interno",
        "El resultado no puede ser PASS público",
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
