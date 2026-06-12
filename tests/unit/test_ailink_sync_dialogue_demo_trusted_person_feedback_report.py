from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_trusted_person_feedback_report_v1.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_feedback_report_exists() -> None:
    assert DOC_PATH.exists()


def test_feedback_report_records_phase_and_decision() -> None:
    text = _doc()

    assert "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.TRUSTED.PERSON.FEEDBACK.REPORT.PHASE7.8" in text
    assert "PASS INTERNO VALIDADO CON AJUSTE DE IDIOMA RESUELTO" in text
    assert "READY FOR CONTROLLED EXTERNAL DEMO PREPARATION" in text


def test_feedback_report_records_real_feedback_points() -> None:
    text = _doc()

    required = [
        "¿Entendió el problema?",
        "¿Entendió que es beta controlada?",
        "¿Entendió que no es sincronización final?",
        "¿Entendió el 0 match suggestions del dummy?",
        "Sí, pero faltaba opción en español",
        "No sabe inglés",
        "PASS interno validado",
    ]

    for item in required:
        assert item in text


def test_feedback_report_links_spanish_report_resolution() -> None:
    text = _doc()

    required = [
        "report_es.html",
        "escena_take",
        "escena_take_vídeo",
        "escena_take_audio",
        "archivo ↔ escena/toma",
    ]

    for item in required:
        assert item in text


def test_feedback_report_keeps_beta_boundaries() -> None:
    text = _doc()

    required = [
        "No significa lanzamiento público.",
        "No significa venta abierta.",
        "No significa prometer sincronización automática final.",
        "beta controlada",
        "revisión humana",
    ]

    for item in required:
        assert item in text


def test_feedback_report_lists_forbidden_claims() -> None:
    text = _doc()

    forbidden_claims = [
        "Sincronización automática final.",
        "Sustituto de montaje.",
        "Integración ya hecha con DaVinci, Avid o Premiere.",
        "Detección por waveform ya operativa.",
        "Detección visual de claqueta ya operativa.",
        "Transcripción de diálogos ya operativa.",
        "SaaS público listo.",
    ]

    for claim in forbidden_claims:
        assert claim in text


def test_feedback_report_recommends_next_phase() -> None:
    text = _doc()

    assert "AILINK.PRODUCT.SYNC_DIALOGUE.SCHOOL.PRODUCER.DEMO.SCRIPT.PHASE7.9" in text
    assert "guion de demo específico para escuela/productora" in text


def test_feedback_report_is_public_safe_and_no_runtime_scope() -> None:
    text = _doc()

    required_no_goals = [
        "Código nuevo.",
        "UI nueva.",
        "CRM.",
        "n8n.",
        "Integración con CID SaaS.",
        "Docker.",
        "Sistema de pagos.",
    ]

    for item in required_no_goals:
        assert item in text


def test_feedback_report_does_not_reference_runtime_or_secret_material() -> None:
    text = _doc()

    forbidden = [
        "DATABASE_URL",
        "AsyncSessionLocal",
        "FastAPI",
        "APIRouter",
        "@router",
        ".env",
        "stripe",
        "http://",
        "https://",
        "Base.metadata.create_all",
        "sqli" + "te",
    ]

    for item in forbidden:
        assert item not in text
