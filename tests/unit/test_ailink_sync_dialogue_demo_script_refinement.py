from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_script_refinement_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_script_refinement_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Script Refinement v1" in DOC


def test_phase_is_documental_script_only():
    required = [
        "Esta fase es documental y de guion",
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


def test_references_previous_phase_chain():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3",
    ]
    for text in required:
        assert text in DOC


def test_limited_pass_status_and_allowed_audience_are_explicit():
    required = [
        "LIMITED PASS",
        "Demo interna permitida",
        "Demo con persona de confianza permitida",
        "Demo pública no recomendada todavía",
        "Contacto con escuelas o productoras no recomendado todavía como demo final",
        "No recomendado todavía",
        "LinkedIn público como demo final",
    ]
    for text in required:
        assert text in DOC


def test_demo_objective_and_non_goals_are_clear():
    required = [
        "Hay un problema real antes de montaje",
        "El prototipo ya puede escanear o generar una muestra controlada",
        "El reporte permite leer la situación",
        "La beta necesita feedback real",
        "Sincronización automática final",
        "Waveform sync",
        "Transcripción",
        "Detección visual de claqueta",
        "Integración directa con editores",
        "Instalador final",
        "Funcionamiento SaaS CID",
    ]
    for text in required:
        assert text in DOC


def test_material_selection_and_dummy_explanation_are_present():
    required = [
        "Metadata demo controlada para enseñar matching sugerido",
        "Report HTML generado",
        "CSV de media files",
        "CSV de match suggestions",
        "0 match suggestions",
        "archivos dummy sin metadata real",
        "No es un fallo de ejecución",
        "La metadata demo enseña el matching; la e2e dummy enseña que el flujo local genera outputs sin material real",
    ]
    for text in required:
        assert text in DOC


def test_full_5_to_7_minute_script_sections_exist():
    required = [
        "0:00–0:40 — Apertura",
        "0:40–1:20 — Problema",
        "1:20–2:10 — Qué hace hoy",
        "2:10–3:10 — Evidence run real",
        "3:10–4:20 — Lectura del reporte",
        "4:20–5:10 — Explicación del e2e dummy",
        "5:10–6:00 — Límites honestos",
        "6:00–6:45 — Qué feedback pedir",
        "6:45–7:00 — Cierre",
    ]
    for text in required:
        assert text in DOC


def test_evidence_run_numbers_are_in_script():
    required = [
        "3 vídeos",
        "4 audios",
        "5 sugerencias de matching",
        "2 sugerencias de alta confianza",
        "7 media rows",
        "5 match rows",
        "No decir que estos números representan material real de cliente",
        "No decir que la precisión está validada en rodajes reales",
    ]
    for text in required:
        assert text in DOC


def test_shared_name_tokens_explanation_is_safe():
    required = [
        "shared_name_tokens",
        "no es un token secreto",
        "no es una credencial",
        "vídeo y audio comparten partes del nombre",
    ]
    for text in required:
        assert text in DOC


def test_prohibited_and_allowed_phrases_are_present():
    required = [
        "Frases prohibidas",
        "Sincroniza automáticamente todo el material",
        "Ya está listo para productoras",
        "Reemplaza el trabajo del montador",
        "Funciona con cualquier cámara y cualquier grabador",
        "Frases permitidas",
        "Beta controlada",
        "Demo local-first",
        "Outputs revisables",
        "Sugerencias de matching",
        "No sustituye la revisión humana",
        "No es sincronización final",
    ]
    for text in required:
        assert text in DOC


def test_prepared_answers_cover_expected_questions():
    required = [
        "Si preguntan si ya sincroniza automáticamente",
        "Si preguntan por DaVinci, Avid o Premiere",
        "Si preguntan por transcripción",
        "Si preguntan por claqueta visual",
        "Si preguntan por privacidad",
        "Si preguntan por precio",
        "Si preguntan por escuelas o productoras",
    ]
    for text in required:
        assert text in DOC


def test_checklist_feedback_and_next_phase_are_present():
    required = [
        "Checklist antes de ensayar",
        "Plantilla de feedback post-demo",
        "¿Has entendido que no es sincronización final?",
        "¿Qué salida necesitarías para montaje?",
        "¿Qué no debería enseñar todavía?",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.DRY.RUN.PHASE7.5",
        "Ensayar el guion sin grabar vídeo público",
        "Detectar frases peligrosas",
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
