"""Tests for CID real project public beta October scope document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_real_project_public_beta_scope_october_v1.md"
)

PHASE_ID = "AILINK.CID.REAL.PROJECT.PUBLIC.BETA.SCOPE.OCTOBER.PHASE6.1"

REQUIRED_BLOCKS = [
    "## 1. Objetivo de octubre",
    "## 2. Producto público mínimo",
    "## 3. Flujo completo de beta",
    "## 4. Casos reales autorizados",
    "## 5. Consentimiento y confidencialidad",
    "## 6. CID como sistema interactivo con vida propia",
    "## 7. Memoria de proyecto y aprendizaje autorizado",
    "## 8. Cuestionarios por rol",
    "## 9. Planificación visual, storyboard textual y shotlist",
    "## 10. Presupuesto preliminar revisable",
    "## 11. Plan de rodaje preliminar para ayudantía de dirección",
    "## 12. Paquete de traspaso a postproducción",
    "## 13. Revisión humana obligatoria",
    "## 14. Qué queda fuera de octubre",
    "## 15. Roadmap primeros de octubre / finales de octubre",
    "## 16. Riesgos y mitigaciones",
    "## 17. Criterios de aceptación de la beta",
]

ROLE_QUESTIONNAIRES = [
    "productor / jefe de producción",
    "ayudante de dirección",
    "director",
    "dirección de fotografía",
    "sonido directo",
    "arte / vestuario / maquillaje",
    "postproducción",
]

FLOW_TERMS = [
    "guion real autorizado",
    "cuestionarios por rol",
    "análisis/desglose de producción",
    "storyboard textual / shotlist preliminar",
    "presupuesto preliminar revisable",
    "plan de rodaje preliminar para ayudantía de dirección",
    "checklist de rodaje",
    "paquete de traspaso a postproducción",
    "revisión humana",
    "entrega beta al cliente",
]

INTERACTIVE_CID_TERMS = [
    "CID debe tener vida propia e interacción continua",
    "pregunta al cliente o equipo cuando faltan datos",
    "marca incertidumbres",
    "aconseja con tacto profesional y mano izquierda",
    "explica por qué recomienda algo",
    "sugiere, no impone",
]

MEMORY_AND_PRIVACY_TERMS = [
    "Aprender significa memoria autorizada del proyecto/cliente",
    "no entrenamiento de modelos",
    "No reutilizar información entre clientes",
    "No entrenar modelos con material de clientes sin permiso explícito",
    "Memoria aislada por tenant/proyecto",
    "organization_id",
    "tenant_id",
    "project_id",
    "film_id",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_october_beta_scope_document_exists() -> None:
    assert DOC_PATH.exists()


def test_october_beta_scope_contains_phase_id(doc_text: str) -> None:
    assert PHASE_ID in doc_text


def test_october_beta_scope_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_october_beta_scope_includes_authorized_real_cases(doc_text: str) -> None:
    assert "Casos reales autorizados" in doc_text
    assert "guion real autorizado" in doc_text


def test_october_beta_scope_defines_first_internal_real_pilot(doc_text: str) -> None:
    expected = [
        "primer caso piloto real",
        "guion propio autorizado",
        "fundador/usuario",
        "primer cliente interno-real",
        "uso privado y controlado",
        "sin incluir el guion real, escenas, diálogos, nombres de personajes confidenciales ni datos reales del proyecto dentro del repo",
        "revisión humana obligatoria",
    ]
    missing = [term for term in expected if term not in doc_text]
    assert not missing


def test_october_beta_scope_requires_explicit_permission_for_real_scripts(doc_text: str) -> None:
    assert "Nada de uso de guiones reales sin permiso explícito" in doc_text
    assert "permiso explícito para el uso beta concreto" in doc_text


def test_october_beta_scope_forbids_real_scripts_or_client_data_in_repo(doc_text: str) -> None:
    assert "Nada de guiones reales ni datos de clientes dentro del repo" in doc_text
    assert "Nada de fragmentos de guion, nombres reales de proyectos ni materiales confidenciales" in doc_text


def test_october_beta_scope_defines_interactive_cid(doc_text: str) -> None:
    missing = [term for term in INTERACTIVE_CID_TERMS if term not in doc_text]
    assert not missing


def test_october_beta_scope_defines_authorized_project_memory(doc_text: str) -> None:
    missing = [term for term in MEMORY_AND_PRIVACY_TERMS if term not in doc_text]
    assert not missing


def test_october_beta_scope_contains_role_questionnaires(doc_text: str) -> None:
    missing = [role for role in ROLE_QUESTIONNAIRES if role not in doc_text]
    assert not missing


def test_october_beta_scope_explains_questionnaires_as_project_intelligence(doc_text: str) -> None:
    assert "parte esencial de la inteligencia del sistema" in doc_text
    assert "CID pregunta para entender la realidad del proyecto, no para cargar burocracia" in doc_text
    assert "adaptar recomendaciones" in doc_text


def test_october_beta_scope_contains_full_flow(doc_text: str) -> None:
    missing = [term for term in FLOW_TERMS if term not in doc_text]
    assert not missing


def test_october_beta_scope_contains_visual_planning_storyboard_and_shotlist(doc_text: str) -> None:
    assert "storyboard textual" in doc_text
    assert "shotlist preliminar" in doc_text


def test_october_beta_scope_contains_preliminary_schedule_budget_and_handoff(doc_text: str) -> None:
    assert "Plan de rodaje preliminar, no definitivo" in doc_text
    assert "Presupuesto preliminar, no definitivo" in doc_text
    assert "Production-to-Post Handoff Package" in doc_text


def test_october_beta_scope_requires_human_review(doc_text: str) -> None:
    assert "Revisión humana obligatoria" in doc_text
    assert "Toda entrega beta requiere revisión humana obligatoria" in doc_text


def test_october_beta_scope_is_limited_beta_not_full_saas(doc_text: str) -> None:
    assert "beta pública limitada" in doc_text
    assert "no SaaS completo" in doc_text


def test_october_beta_scope_contains_october_roadmap(doc_text: str) -> None:
    assert "Primeros de octubre: versión pública/enseñable" in doc_text
    assert "Finales de octubre: beta operativa completa" in doc_text
