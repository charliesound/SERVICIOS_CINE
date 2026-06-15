"""Tests for Script-to-Production Breakdown producer test pack document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_producer_test_pack_v1.md"
)

PHASE_ID = "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.PRODUCER.TEST.PACK.PHASE5.5"

REQUIRED_BLOCKS = [
    "## 1. Guion de presentación de 2 minutos",
    "## 2. Orden exacto de hojas que enseñar",
    "## 3. Qué frases decir y qué frases evitar",
    "## 4. Preguntas de feedback",
    "## 5. Criterios PASS / LIMITED PASS / FAIL",
    "## 6. Checklist antes de enseñar",
    "## 7. Registro de feedback para después",
]

REQUIRED_TERMS = [
    PHASE_ID,
    "PASS final",
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "presupuesto preliminar revisable",
    "no presupuesto definitivo",
    "revisión humana",
    "no sustituye al productor",
    "PASS",
    "LIMITED PASS",
    "FAIL",
]

FORBIDDEN_PHRASES_AS_CONTROL = [
    "presupuesto exacto",
    "producto final",
    "procesa cualquier guion real",
    "IA real integrada",
    "automatiza la producción",
    "sustituye dirección de producción",
    "conectado ya al SaaS",
    "listo para clientes",
    "herramienta fiscal",
    "contabilidad real",
]

EXPLICIT_PROHIBITIONS = [
    "no IA real",
    "no guiones reales",
    "no backend SaaS",
    "no DB",
    "no Alembic",
    "no landing",
    "no más colores ni diseño salvo que el productor lo pida",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_producer_test_pack_document_exists() -> None:
    assert DOC_PATH.exists()


def test_producer_test_pack_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_producer_test_pack_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_producer_test_pack_contains_forbidden_phrases_as_control(doc_text: str) -> None:
    assert "Frases prohibidas" in doc_text
    missing = [phrase for phrase in FORBIDDEN_PHRASES_AS_CONTROL if phrase not in doc_text]
    assert not missing


def test_producer_test_pack_contains_explicit_prohibitions(doc_text: str) -> None:
    missing = [prohibition for prohibition in EXPLICIT_PROHIBITIONS if prohibition not in doc_text]
    assert not missing


def test_producer_test_pack_has_feedback_template(doc_text: str) -> None:
    expected_fields = [
        "Fecha:",
        "Persona:",
        "Perfil:",
        "¿Entendió el valor en menos de 2 minutos? Sí/No",
        "Hoja más útil:",
        "Dudas:",
        "Riesgos percibidos:",
        "Qué faltó:",
        "Qué sobró:",
        "¿Entendió que era demo? Sí/No",
        "¿Entendió que no era presupuesto definitivo? Sí/No",
        "¿Entendió que requiere revisión humana? Sí/No",
        "¿Lo usaría en primera reunión? Sí/No",
        "Resultado: PASS / LIMITED PASS / FAIL",
        "Próxima acción recomendada:",
    ]
    missing = [field for field in expected_fields if field not in doc_text]
    assert not missing
