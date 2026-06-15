"""Tests for Script-to-Production Breakdown second producer demo pack."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_second_producer_demo_pack_v1.md"
)

PHASE_ID = "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.SECOND.PRODUCER.DEMO.PACK.PHASE5.6"

REQUIRED_BLOCKS = [
    "## 1. Objetivo de la segunda prueba profesional",
    "## 2. Estado validado de la demo",
    "## 3. Qué se debe enseñar",
    "## 4. Qué NO se debe enseñar",
    "## 5. Guion refinado de presentación de 2 minutos",
    "## 6. Preguntas específicas para un segundo productor",
    "## 7. Comparación con feedback de la primera prueba",
    "## 8. Señales de validación fuerte",
    "## 9. Señales de alerta",
    "## 10. Plantilla de registro de segunda prueba",
    "## 11. Decisión posterior recomendada",
]

REQUIRED_TERMS = [
    PHASE_ID,
    "PASS final",
    "PASS",
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "presupuesto preliminar revisable",
    "no presupuesto definitivo",
    "no producto final",
    "revisión humana",
    "PASS / LIMITED PASS / FAIL",
]

EXPLICIT_PROHIBITIONS = [
    "no IA real",
    "no guiones reales",
    "no backend",
    "no DB",
    "no Alembic",
    "no landing",
    "no código",
    "no terminal",
]

TEMPLATE_FIELDS = [
    "Fecha:",
    "Persona:",
    "Perfil:",
    "Productora/ámbito:",
    "¿Entendió el valor en menos de 2 minutos? Sí/No",
    "Hoja más útil:",
    "Dato que faltó:",
    "Riesgo mejor detectado:",
    "Riesgo que faltó:",
    "Dudas:",
    "¿Lo usaría en primera reunión? Sí/No",
    "¿Lo enseñaría a dirección de producción? Sí/No",
    "¿Lo probaría con guion real futuro? Sí/No",
    "¿Entendió que era demo controlada? Sí/No",
    "¿Entendió que no era presupuesto definitivo? Sí/No",
    "Resultado: PASS / LIMITED PASS / FAIL",
    "Próxima acción recomendada:",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_second_producer_demo_pack_document_exists() -> None:
    assert DOC_PATH.exists()


def test_second_producer_demo_pack_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_second_producer_demo_pack_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_second_producer_demo_pack_contains_explicit_prohibitions(doc_text: str) -> None:
    missing = [prohibition for prohibition in EXPLICIT_PROHIBITIONS if prohibition not in doc_text]
    assert not missing


def test_second_producer_demo_pack_contains_registration_template(doc_text: str) -> None:
    missing = [field for field in TEMPLATE_FIELDS if field not in doc_text]
    assert not missing


def test_second_producer_demo_pack_keeps_scope_documental(doc_text: str) -> None:
    expected = [
        "No se busca vender todavía.",
        "No se busca prometer producto final.",
        "No se busca usar guiones reales.",
        "No se busca abrir SaaS real.",
        "No se busca añadir IA real.",
    ]
    missing = [phrase for phrase in expected if phrase not in doc_text]
    assert not missing
