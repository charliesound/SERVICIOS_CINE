"""Tests for Script-to-Production Breakdown producer demo script document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_producer_demo_script_v1.md"
)

REQUIRED_SECTIONS = [
    "## 1. Propósito",
    "## 2. Contexto de la demo",
    "## 3. Mensaje principal",
    "## 4. Guion de demo de 3-5 minutos",
    "## 5. Versión verbal completa",
    "## 6. Versión corta de 60 segundos",
    "## 7. Frases obligatorias",
    "## 8. Frases prohibidas",
    "## 9. Qué mostrar en pantalla",
    "## 10. Qué no mostrar todavía",
    "## 11. Preguntas esperables y respuestas seguras",
    "## 12. Feedback que hay que pedir",
    "## 13. Criterios de lectura del productor",
    "## 14. Conexión con CID",
    "## 15. Conexión con Production Finance Control",
    "## 16. Checklist antes de presentar",
    "## 17. No-goals",
]

REQUIRED_TERMS = [
    "Proyecto Demo Bruma",
    "productor",
    "demo controlada",
    "guion ficticio",
    "JSON",
    "Markdown",
    "Excel",
    "stdlib",
    "sin openpyxl",
    "No es presupuesto definitivo",
    "revisión humana",
    "guion → producción → finanzas",
    "organization_id",
    "tenant_id",
    "project_id",
    "film_id",
    "CID Script Intelligence",
    "CID Production Intelligence",
    "CID Production Finance Control",
    "Production Finance Control",
    "PASS",
    "LIMITED PASS",
    "FAIL",
    "`/tmp`",
]

REQUIRED_PHRASES = [
    "Esto es una demo controlada con un guion ficticio.",
    "No es un presupuesto definitivo.",
    "No sustituye al productor ni al director de producción.",
    "Todo requiere revisión humana.",
    "El valor está en conectar guion, producción y finanzas.",
    "La productora puede tener varias películas separadas sin mezclar datos.",
]

FORBIDDEN_PHRASES = [
    "Presupuesto exacto.",
    "Producto final.",
    "Producto disponible.",
    "Procesa cualquier guion real.",
    "IA real integrada.",
    "Sustituye al productor.",
    "Garantiza la viabilidad.",
    "Automatiza toda la producción.",
    "Ya está integrado con Production Finance Control real.",
    "Ya está integrado con CID SaaS real.",
]

FORBIDDEN_PROMISES = [
    "presupuesto exacto",
    "producto final",
    "producto disponible",
    "procesa cualquier guion real",
    "IA real integrada",
    "integración SaaS real",
    "integración contable real",
]

EXPECTED_QUESTIONS = [
    "¿Puede analizar mi guion real?",
    "¿Esto sustituye a un productor?",
    "¿Esto sustituye a un director de producción?",
    "¿Qué fiabilidad tiene el presupuesto?",
    "¿Se puede exportar a Excel?",
    "¿Se puede usar con varias películas?",
    "¿Se mezclan datos de proyectos?",
    "¿Cómo se protegería la confidencialidad?",
    "¿Cuándo podría probarse?",
    "¿Cuánto costaría?",
    "¿Esto forma parte de CID?",
    "¿Se conectará con facturas/gastos reales?",
]

FEEDBACK_QUESTIONS = [
    "¿Entiendes el valor en menos de 2 minutos?",
    "¿Qué hoja del Excel te parece más útil?",
    "¿Qué dato falta para que un productor lo use?",
    "¿Qué te generaría desconfianza?",
    "¿Lo usarías para una primera reunión interna?",
    "¿Qué necesitarías antes de probarlo con un proyecto real?",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _find_all(text: str, phrase: str) -> list[int]:
    indexes: list[int] = []
    start = 0
    while True:
        index = text.find(phrase, start)
        if index == -1:
            return indexes
        indexes.append(index)
        start = index + len(phrase)


def _is_positive_claim(text: str, phrase: str) -> bool:
    text_lower = text.lower()
    phrase_lower = phrase.lower()
    negative_markers = (
        "no ",
        "no es ",
        "no hay ",
        "no debe ",
        "no prometer",
        "no sustituye",
        "todavía no",
        "sin venderla",
        "sin venderla como",
        "frases a evitar",
        "frases prohibidas",
        "no-goals",
        "fail",
        "cree que es ",
    )
    for index in _find_all(text_lower, phrase_lower):
        preceding_text = text_lower[:index]
        section = ""
        for line in preceding_text.splitlines():
            if line.startswith("## "):
                section = line
        if (
            "frases prohibidas" in section
            or "no-goals" in section
            or "qué no mostrar" in section
        ):
            continue
        line_start = text_lower.rfind("\n", 0, index) + 1
        line_end = text_lower.find("\n", index)
        if line_end == -1:
            line_end = len(text_lower)
        current_line = text_lower[line_start:line_end]
        if any(marker in current_line for marker in negative_markers):
            continue
        context_before = text_lower[max(0, index - 80):index]
        if any(marker in context_before for marker in negative_markers):
            continue
        return True
    return False


def test_producer_demo_script_document_exists() -> None:
    assert DOC_PATH.exists()


def test_producer_demo_script_has_all_sections(doc_text: str) -> None:
    missing = [section for section in REQUIRED_SECTIONS if section not in doc_text]
    assert not missing


def test_producer_demo_script_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_producer_demo_script_contains_required_phrases(doc_text: str) -> None:
    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in doc_text]
    assert not missing


def test_producer_demo_script_contains_forbidden_phrases_as_avoidance(doc_text: str) -> None:
    assert "## 8. Frases prohibidas" in doc_text
    missing = [phrase for phrase in FORBIDDEN_PHRASES if phrase not in doc_text]
    assert not missing


@pytest.mark.parametrize("phrase", FORBIDDEN_PROMISES)
def test_producer_demo_script_no_positive_forbidden_promises(doc_text: str, phrase: str) -> None:
    assert not _is_positive_claim(doc_text, phrase)


def test_producer_demo_script_includes_expected_questions(doc_text: str) -> None:
    missing = [question for question in EXPECTED_QUESTIONS if question not in doc_text]
    assert not missing


def test_producer_demo_script_includes_feedback_questions(doc_text: str) -> None:
    missing = [question for question in FEEDBACK_QUESTIONS if question not in doc_text]
    assert not missing


@pytest.mark.parametrize("extension", ["*.xlsx", "*.pdf", "*.html", "*.csv"])
def test_producer_demo_script_no_forbidden_artifacts_created(extension: str) -> None:
    found = []
    for directory in [ROOT / "docs" / "product" / "script_breakdown", ROOT / "tests" / "unit"]:
        found.extend(directory.rglob(extension))
    assert found == []
