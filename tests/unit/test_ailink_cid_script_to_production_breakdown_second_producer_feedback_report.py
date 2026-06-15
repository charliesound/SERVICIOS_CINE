"""Tests for Script-to-Production Breakdown second producer feedback report."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_second_producer_feedback_report_v1.md"
)

PHASE_ID = "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.SECOND.PRODUCER.FEEDBACK.REPORT.PHASE5.7"

REQUIRED_BLOCKS = [
    "## 1. Objetivo del informe",
    "## 2. Estado de la demo antes de la segunda prueba",
    "## 3. Resultado de la primera prueba profesional",
    "## 4. Resultado de la segunda prueba profesional",
    "## 5. Señales de validación acumulada",
    "## 6. Límites que siguen vigentes",
    "## 7. Riesgos si se avanza demasiado rápido",
    "## 8. Decisión recomendada",
    "## 9. Opciones de siguiente paso",
    "## 10. Criterio de no avanzar todavía a IA real/backend/landing",
    "## 11. Resumen ejecutivo",
]

REQUIRED_TERMS = [
    PHASE_ID,
    "PASS",
    "dos pruebas profesionales",
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "presupuesto preliminar",
    "presupuesto preliminar revisable",
    "no presupuesto definitivo",
    "no producto final",
    "no IA real",
    "no guiones reales",
    "no SaaS",
    "no landing",
    "revisión humana",
    "ficha comercial privada",
    "material autorizado",
    "guion ficticio ampliado",
    "No tocar código inmediatamente",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_second_producer_feedback_report_document_exists() -> None:
    assert DOC_PATH.exists()


def test_second_producer_feedback_report_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_second_producer_feedback_report_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_second_producer_feedback_report_contains_accumulated_pass(doc_text: str) -> None:
    assert "primera prueba `PASS`, segunda prueba `PASS`" in doc_text
    assert "Dos pruebas profesionales con resultado `PASS`" in doc_text


def test_second_producer_feedback_report_recommends_private_sheet(doc_text: str) -> None:
    assert "Opción A: ficha comercial privada de una página." in doc_text
    assert "elegir Opción A como siguiente paso más prudente" in doc_text


def test_second_producer_feedback_report_recommends_no_immediate_code(doc_text: str) -> None:
    assert "No tocar código inmediatamente." in doc_text
    assert "no desarrollo técnico inmediato" in doc_text
