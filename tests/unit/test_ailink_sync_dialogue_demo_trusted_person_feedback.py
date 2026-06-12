from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_trusted_person_feedback_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_trusted_person_feedback_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Trusted Person Feedback v1" in DOC


def test_phase_is_documental_and_operational_only():
    required = [
        "Esta fase es documental y operativa",
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
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.DRY.RUN.PHASE7.5",
    ]
    for text in required:
        assert text in DOC


def test_input_status_requires_internal_pass():
    required = [
        "Phase7.5 obtuvo PASS interno",
        "El ensayo duró entre 5 y 7 minutos",
        "Se explicó LIMITED PASS",
        "Se explicó beta controlada",
        "Se explicó local-first",
        "no es sincronización automática final",
        "0 match suggestions",
        "No se vendió",
        "No se cerró precio",
        "No se abrió material sensible",
    ]
    for text in required:
        assert text in DOC


def test_output_status_is_bounded_and_not_public():
    required = [
        "PASS interno validado con persona de confianza",
        "PASS interno con ajustes",
        "LIMITED PASS mantenido",
        "FAIL de demo externa",
        "Esta fase no puede producir PASS público",
        "El máximo resultado permitido es PASS interno validado",
        "No puede producir PASS público",
    ]
    for text in required:
        assert text in DOC


def test_trusted_person_definition_is_clear():
    required = [
        "Profesional audiovisual cercano",
        "Montador conocido",
        "Ayudante de montaje conocido",
        "Técnico de sonido cercano",
        "Productor de confianza",
        "Docente cercano",
        "Lead frío",
        "Escuela contactada por primera vez",
        "Productora externa sin confianza previa",
        "Público de LinkedIn",
        "Público de Facebook",
        "Público de YouTube",
    ]
    for text in required:
        assert text in DOC


def test_preconditions_and_allowed_materials_are_explicit():
    required = [
        "Confirmar que se mantiene el estado PASS interno, no PASS público",
        "beta controlada",
        "no se enseñará material real de clientes",
        "no se abrirán credenciales",
        "no se grabará para publicación",
        "objetivo es feedback, no venta",
        "Report HTML controlado",
        "Tabla match suggestions controlada",
        "Evidence run summary",
        "Hoja de feedback",
    ]
    for text in required:
        assert text in DOC


def test_forbidden_materials_are_explicit():
    required = [
        "Material audiovisual de cliente",
        "Datos personales reales",
        "Rutas privadas",
        "Credenciales",
        ".env",
        "Paneles internos",
        "n8n",
        "CRM",
        "CID SaaS",
        "Docker",
        "Bases de datos reales",
        "Facturación",
        "Precios cerrados",
        "Promesas de integración con editores",
    ]
    for text in required:
        assert text in DOC


def test_initial_message_and_session_structure_exist():
    required = [
        "Mensaje inicial recomendado",
        "Te voy a enseñar una beta controlada",
        "No es una demo pública ni un producto final",
        "no es venderte nada",
        "Estructura recomendada de sesión",
        "10 a 20 minutos",
        "Demo hablada: 5 a 7 minutos",
        "Preguntas de comprensión",
        "Feedback abierto",
    ]
    for text in required:
        assert text in DOC


def test_feedback_questions_cover_understanding_value_language_and_next_step():
    required = [
        "Preguntas de comprensión",
        "¿Has entendido qué problema intenta resolver?",
        "¿Has entendido que no es sincronización automática final?",
        "¿Has entendido qué significa local-first?",
        "¿Has entendido por qué el e2e dummy puede dar 0 match suggestions?",
        "Preguntas de valor audiovisual",
        "¿Esto ayudaría en preparación de montaje?",
        "¿Qué dato falta para que el reporte sea más valioso?",
        "Preguntas de lenguaje y credibilidad",
        "¿He prometido demasiado?",
        "¿Alguna frase suena a producto final?",
        "Preguntas de siguiente paso",
        "¿Se puede enseñar a otra persona de confianza?",
    ]
    for text in required:
        assert text in DOC


def test_forbidden_and_allowed_phrases_are_present():
    required = [
        "Frases prohibidas durante esta sesión",
        "Ya está listo para vender",
        "Ya sincroniza automáticamente",
        "Ya sustituye al montador",
        "Ya detecta claqueta visual",
        "Ya transcribe diálogos",
        "Ya se integra con DaVinci",
        "Ya se integra con Avid",
        "Ya se integra con Premiere",
        "Esto ya está para LinkedIn",
        "Frases permitidas",
        "Es una beta controlada",
        "Está en PASS interno, no en PASS público",
        "No es sincronización automática final",
        "El objetivo es feedback, no venta",
        "CID queda fuera de esta demo",
    ]
    for text in required:
        assert text in DOC


def test_feedback_form_exists():
    required = [
        "Formulario de feedback",
        "Fecha:",
        "Persona:",
        "Perfil:",
        "Relación de confianza:",
        "Duración total:",
        "¿Entendió el problema?: sí/no/parcial",
        "¿Entendió que es beta controlada?: sí/no/parcial",
        "¿Entendió local-first?: sí/no/parcial",
        "¿Entendió que no es sincronización final?: sí/no/parcial",
        "¿Entendió el 0 match suggestions del dummy?: sí/no/parcial",
        "Resultado recomendado: PASS interno validado / PASS interno con ajustes / LIMITED PASS mantenido / FAIL",
        "Ajustes necesarios:",
        "Siguiente acción:",
    ]
    for text in required:
        assert text in DOC


def test_decision_matrix_has_all_outcomes():
    required = [
        "PASS interno validado",
        "PASS interno con ajustes",
        "LIMITED PASS mantenido",
        "FAIL",
        "Puede enseñarse a una segunda persona de confianza",
        "Todavía no es PASS público",
        "Todavía no se publica en LinkedIn",
        "No abrir todavía a escuelas/productoras",
        "Volver a Phase7.4 o Phase7.5",
    ]
    for text in required:
        assert text in DOC


def test_advancement_condition_and_next_phase_are_defined():
    required = [
        "Condición para avanzar",
        "No se puede avanzar si",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.TRUSTED.PERSON.FEEDBACK.REPORT.PHASE7.7",
        "Registrar el feedback real",
        "Convertir observaciones en ajustes concretos",
        "Repetir Phase7.5",
        "Ajustar Phase7.4",
        "No abrir demo externa",
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
