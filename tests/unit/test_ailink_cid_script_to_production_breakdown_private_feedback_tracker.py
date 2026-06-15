"""Tests for Script-to-Production Breakdown private feedback tracker."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_private_feedback_tracker_v1.md"
)

PHASE_ID = "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.PRIVATE.FEEDBACK.TRACKER.PHASE5.9"

REQUIRED_BLOCKS = [
    "## 1. Objetivo del tracker privado",
    "## 2. Qué se puede registrar",
    "## 3. Qué NO se debe registrar",
    "## 4. Contactos recomendados",
    "## 5. Plantilla de registro por contacto",
    "## 6. Preguntas de feedback recomendadas",
    "## 7. Señales de validación",
    "## 8. Señales de alerta",
    "## 9. Criterios de decisión",
    "## 10. Resumen acumulado de 3-5 contactos",
    "## 11. Límites de uso",
    "## 12. Próximo paso prudente",
]

PRIVATE_MANUAL_SCOPE = [
    "tracker privado, no CRM",
    "Registro manual, no automatización",
]

FORBIDDEN_TOOLS_AND_CHANNELS = [
    "No Supabase",
    "No n8n",
    "No formulario público",
    "No base de datos",
    "No landing pública",
    "No scraping",
]

PRIVACY_TERMS = [
    "No datos sensibles innecesarios",
    "Registrar feedback útil de producción, no datos personales excesivos",
    "Priorizar identificador o iniciales antes que nombre completo",
    "No registrar nombre completo, teléfono, email, empresa u otros datos personales",
]

TEMPLATE_FIELDS = [
    "Identificador o iniciales del contacto:",
    "Perfil: productor / escuela / director de producción / colaborador / técnico / otro",
    "Fecha de contacto:",
    "Qué se le enseñó: ficha / Excel / demo verbal / otra cosa",
    "Reacción inicial:",
    "¿Entendió el valor? Sí/No",
    "¿Entendió los límites? Sí/No",
    "Preguntas que hizo:",
    "Objeciones o dudas:",
    "Frases literales útiles:",
    "Nivel de interés: alto / medio / bajo",
    "Potencial siguiente paso:",
    "Riesgo detectado:",
    "Decisión: seguir / esperar / descartar / revisar mensaje",
]

PRODUCT_LIMITS = [
    "demo controlada",
    "guion ficticio",
    "revisión humana",
    "no producto final",
    "no presupuesto definitivo",
    "No IA real",
    "No guiones reales",
    "No SaaS abierto",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_private_feedback_tracker_document_exists() -> None:
    assert DOC_PATH.exists()


def test_private_feedback_tracker_contains_phase_id(doc_text: str) -> None:
    assert PHASE_ID in doc_text


def test_private_feedback_tracker_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_private_feedback_tracker_defines_private_manual_scope(doc_text: str) -> None:
    missing = [term for term in PRIVATE_MANUAL_SCOPE if term not in doc_text]
    assert not missing


def test_private_feedback_tracker_contains_forbidden_tools_and_channels(doc_text: str) -> None:
    missing = [term for term in FORBIDDEN_TOOLS_AND_CHANNELS if term not in doc_text]
    assert not missing


def test_private_feedback_tracker_recommends_qualified_contacts(doc_text: str) -> None:
    assert "Usar solo con contactos cualificados" in doc_text
    assert "3-5 contactos cualificados" in doc_text


def test_private_feedback_tracker_avoids_unnecessary_sensitive_data(doc_text: str) -> None:
    missing = [term for term in PRIVACY_TERMS if term not in doc_text]
    assert not missing


def test_private_feedback_tracker_contains_contact_template(doc_text: str) -> None:
    missing = [field for field in TEMPLATE_FIELDS if field not in doc_text]
    assert not missing


def test_private_feedback_tracker_contains_feedback_questions(doc_text: str) -> None:
    expected_questions = [
        "¿Se entiende el valor sin explicación técnica?",
        "¿Qué parte resulta más útil para una primera reunión de producción?",
        "¿Qué falta para confiar más en el presupuesto preliminar revisable?",
        "¿Se entiende que requiere revisión humana?",
    ]
    missing = [question for question in expected_questions if question not in doc_text]
    assert not missing


def test_private_feedback_tracker_contains_validation_and_alert_signals(doc_text: str) -> None:
    assert "## 7. Señales de validación" in doc_text
    assert "## 8. Señales de alerta" in doc_text
    assert "Entiende el valor en menos de 2 minutos" in doc_text
    assert "Cree que ya procesa guiones reales" in doc_text


def test_private_feedback_tracker_keeps_product_limits(doc_text: str) -> None:
    missing = [limit for limit in PRODUCT_LIMITS if limit not in doc_text]
    assert not missing


def test_private_feedback_tracker_recommends_no_technical_opening_yet(doc_text: str) -> None:
    assert "No abrir todavía IA real, backend, DB, landing pública ni SaaS" in doc_text
