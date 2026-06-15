"""Tests for Script-to-Production Breakdown demo visual QA document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_demo_visual_qa_v1.md"
)

REQUIRED_SECTIONS = [
    "## 1. Propósito",
    "## 2. Estado actual",
    "## 3. Criterios visuales generales",
    "## 4. Criterios por hoja Excel",
    "## 5. Revisión del Markdown",
    "## 6. Revisión del Excel",
    "## 7. Revisión comercial",
    "## 8. Señales de riesgo visual",
    "## 9. Checklist manual de QA",
    "## 10. Resultado esperado",
    "## 11. Recomendaciones si LIMITED PASS",
    "## 12. Recomendaciones si PASS",
    "## 13. No-goals",
]

REQUIRED_TERMS = [
    "Proyecto Demo Bruma",
    "JSON",
    "Markdown",
    "Excel",
    "stdlib",
    "sin openpyxl",
    "demo local controlada",
    "No procesa guiones reales",
    "No usa IA real",
    "productor",
    "guion -> producción -> finanzas",
    "revisión humana",
    "no es presupuesto definitivo",
    "organization_id",
    "tenant_id",
    "project_id",
    "film_id",
    "PASS",
    "LIMITED PASS",
    "FAIL",
    "`/tmp`",
    "no PDF/HTML/CSV",
]

EXCEL_SHEETS = [
    "Resumen",
    "Escenas",
    "Personajes",
    "Localizaciones",
    "Riesgos",
    "Viabilidad",
    "Presupuesto",
    "Recomendaciones",
    "Revisión humana",
    "Metadata",
]

FORBIDDEN_PROMISES = [
    "presupuesto exacto",
    "producto final",
    "producto disponible",
    "procesa cualquier guion real",
    "IA real integrada",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _is_positive_claim(text: str, phrase: str) -> bool:
    text_lower = text.lower()
    phrase_lower = phrase.lower()
    negations = (
        "no ",
        "no es ",
        "no debe ",
        "sin ",
        "puede creer que ",
        "confunde ",
        "interpreta que ",
        "interpreta que es ",
        "parezca ",
        "separación entre ",
    )
    for index in _find_all(text_lower, phrase_lower):
        line_start = text_lower.rfind("\n", 0, index) + 1
        line_end = text_lower.find("\n", index)
        if line_end == -1:
            line_end = len(text_lower)
        current_line = text_lower[line_start:line_end]
        negative_context_markers = (
            "posibles problemas visuales",
            "fail",
            "señales de riesgo visual",
            "no-goals",
            "puede creer",
            "interpreta",
            "parezca",
            "separación entre",
        )
        if any(marker in current_line for marker in negative_context_markers):
            continue
        context_before = text_lower[max(0, index - 60):index]
        if any(negation in context_before for negation in negations):
            continue
        return True
    return False


def _find_all(text: str, phrase: str) -> list[int]:
    indexes: list[int] = []
    start = 0
    while True:
        index = text.find(phrase, start)
        if index == -1:
            return indexes
        indexes.append(index)
        start = index + len(phrase)


def test_visual_qa_document_exists() -> None:
    assert DOC_PATH.exists()


def test_visual_qa_has_all_sections(doc_text: str) -> None:
    missing = [section for section in REQUIRED_SECTIONS if section not in doc_text]
    assert not missing


def test_visual_qa_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_visual_qa_mentions_all_excel_sheets(doc_text: str) -> None:
    missing = [sheet for sheet in EXCEL_SHEETS if sheet not in doc_text]
    assert not missing


def test_visual_qa_includes_sheet_criteria(doc_text: str) -> None:
    for sheet in EXCEL_SHEETS:
        assert f"### 4." in doc_text and sheet in doc_text
    for criterion in [
        "Qué debe comunicar",
        "Qué debe verse primero",
        "Posibles problemas visuales",
        "PASS",
        "LIMITED PASS",
        "FAIL",
    ]:
        assert doc_text.count(criterion) >= len(EXCEL_SHEETS)


def test_visual_qa_includes_manual_checklist(doc_text: str) -> None:
    assert "## 9. Checklist manual de QA" in doc_text
    for item in [
        "Generar demo en `/tmp`",
        "Confirmar repo limpio antes y después",
        "Confirmar solo JSON, Markdown y XLSX",
        "Confirmar no PDF/HTML/CSV",
        "Abrir Markdown",
        "Abrir Excel",
        "Registrar incidencias visuales",
    ]:
        assert item in doc_text


@pytest.mark.parametrize("phrase", FORBIDDEN_PROMISES)
def test_visual_qa_no_positive_forbidden_promises(doc_text: str, phrase: str) -> None:
    assert not _is_positive_claim(doc_text, phrase)


@pytest.mark.parametrize("extension", ["*.xlsx", "*.pdf", "*.html", "*.csv"])
def test_visual_qa_no_forbidden_artifacts_created(extension: str) -> None:
    found = []
    for directory in [ROOT / "docs" / "product" / "script_breakdown", ROOT / "tests" / "unit"]:
        found.extend(directory.rglob(extension))
    assert found == []
