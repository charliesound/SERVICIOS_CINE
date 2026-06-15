"""Tests for Script-to-Production Breakdown private commercial one-pager."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_private_commercial_one_pager_v1.md"
)

PHASE_ID = "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.PRIVATE.COMMERCIAL.ONE.PAGER.PHASE5.8"

REQUIRED_BLOCKS = [
    "## 1. Título comercial privado",
    "## 2. Problema que resuelve",
    "## 3. Qué hace la demo",
    "## 4. Para quién es útil",
    "## 5. Qué entrega actualmente la demo",
    "## 6. Qué valor aporta en una primera reunión de producción",
    "## 7. Estado actual de validación",
    "## 8. Límites actuales",
    "## 9. Qué NO promete",
    "## 10. Uso recomendado",
    "## 11. Próximo paso prudente",
    "## 12. Versión breve para enviar por mensaje",
]

REQUIRED_TERMS = [
    PHASE_ID,
    "ficha privada",
    "no landing pública",
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "Excel",
    ".xlsx",
    "presupuesto preliminar revisable",
    "dos pruebas profesionales",
    "PASS final",
    "PASS",
]

LIMIT_TERMS = [
    "no producto final",
    "no presupuesto definitivo",
    "no IA real",
    "no guiones reales",
    "no SaaS abierto",
    "revisión humana obligatoria",
]

NO_PROMISE_TERMS = [
    "no sustituye al productor",
    "no sustituye al director de producción",
    "no es herramienta fiscal",
    "no es software contable",
]

NEXT_STEP_TERMS = [
    "3-5 contactos cualificados",
    "no abrir todavía IA real, backend, DB, landing pública ni SaaS",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_private_commercial_one_pager_document_exists() -> None:
    assert DOC_PATH.exists()


def test_private_commercial_one_pager_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_private_commercial_one_pager_contains_required_terms(doc_text: str) -> None:
    missing = [term for term in REQUIRED_TERMS if term not in doc_text]
    assert not missing


def test_private_commercial_one_pager_declares_limits(doc_text: str) -> None:
    missing = [term for term in LIMIT_TERMS if term not in doc_text]
    assert not missing


def test_private_commercial_one_pager_declares_no_replacement_or_fiscal_claims(doc_text: str) -> None:
    missing = [term for term in NO_PROMISE_TERMS if term not in doc_text]
    assert not missing


def test_private_commercial_one_pager_contains_private_message_version(doc_text: str) -> None:
    assert "Texto breve para WhatsApp, email o LinkedIn privado" in doc_text
    assert "Estoy validando una demo privada para producción audiovisual" in doc_text
    assert "Me gustaría enseñártela en 10 minutos" in doc_text


def test_private_commercial_one_pager_recommends_prudent_next_steps(doc_text: str) -> None:
    missing = [term for term in NEXT_STEP_TERMS if term not in doc_text]
    assert not missing
