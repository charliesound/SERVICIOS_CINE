"""Tests for CID real project pilot processing flow document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_real_project_pilot_processing_flow_v1.md"
)

PHASE_ID = "AILINK.CID.REAL.PROJECT.PILOT.PROCESSING.PHASE6.3"

REQUIRED_BLOCKS = [
    "## 1. Objetivo del piloto real privado",
    "## 2. Materiales permitidos y prohibidos",
    "## 3. Ubicación privada fuera del repo",
    "## 4. Preparación del intake privado",
    "## 5. Cumplimentación de cuestionarios fuera del repo",
    "## 6. Flujo de procesamiento controlado",
    "## 7. Revisión humana del founder",
    "## 8. Entregables privados esperados",
    "## 9. Qué no debe versionarse",
    "## 10. Registro de feedback sin material confidencial",
    "## 11. Criterios de éxito del piloto",
    "## 12. Decisiones posteriores al piloto",
    "## 13. Riesgos y mitigaciones",
    "## 14. Criterios de aceptación",
]

PRIVACY_TERMS = [
    "guion real",
    "título real",
    "escenas reales",
    "diálogos reales",
    "personajes reales",
    "localizaciones reales",
    "nombres de personas reales",
    "presupuesto real",
    "outputs reales",
    "material confidencial",
]

DELIVERABLE_TERMS = [
    "resumen de producción privado",
    "desglose preliminar privado",
    "storyboard textual / shotlist preliminar privado",
    "presupuesto preliminar revisable privado",
    "plan de rodaje preliminar para ayudantía privado",
    "checklist de rodaje privado",
    "paquete de traspaso a postproducción privado",
    "notas de incertidumbre y revisión humana",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_pilot_flow_document_exists() -> None:
    assert DOC_PATH.exists()


def test_pilot_flow_contains_phase_id(doc_text: str) -> None:
    assert PHASE_ID in doc_text


def test_pilot_flow_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_pilot_flow_defines_first_real_authorized_pilot(doc_text: str) -> None:
    assert "primer piloto real" in doc_text.lower()
    assert "guion propio autorizado" in doc_text.lower()


def test_pilot_flow_founder_as_first_internal_real_client(doc_text: str) -> None:
    assert "fundador" in doc_text.lower() or "founder" in doc_text.lower()
    assert "primer cliente interno-real" in doc_text.lower()


def test_pilot_flow_script_and_outputs_outside_repo(doc_text: str) -> None:
    assert "fuera del repo" in doc_text.lower()
    assert "fuera del repositorio" in doc_text.lower()


def test_pilot_flow_forbids_real_title_scenes_dialogues(doc_text: str) -> None:
    assert "título real" in doc_text.lower()
    assert "escenas reales" in doc_text.lower()
    assert "diálogos reales" in doc_text.lower()
    assert "personajes reales" in doc_text.lower()


def test_pilot_flow_forbids_real_locations_names_budget(doc_text: str) -> None:
    assert "localizaciones reales" in doc_text.lower()
    assert "nombres de personas reales" in doc_text.lower()
    assert "presupuesto real" in doc_text.lower()


def test_pilot_flow_no_real_script_processing_in_this_phase(doc_text: str) -> None:
    assert "no procesa el guion real" in doc_text.lower()
    assert "solo documenta el flujo" in doc_text.lower()


def test_pilot_flow_documents_flow_not_content(doc_text: str) -> None:
    assert "documenta el flujo" in doc_text.lower()
    assert "no el contenido" in doc_text.lower()


def test_pilot_flow_logical_structure_outside_repo(doc_text: str) -> None:
    assert "estructura lógica" in doc_text.lower()
    assert "intake/" in doc_text
    assert "questionnaires/" in doc_text
    assert "processing/" in doc_text
    assert "outputs/" in doc_text
    assert "feedback/" in doc_text
    assert "no debe crearse físicamente" in doc_text.lower()


def test_pilot_flow_private_and_controlled_processing(doc_text: str) -> None:
    assert "procesamiento privado" in doc_text.lower()
    assert "controlado" in doc_text.lower()


def test_pilot_flow_mandatory_human_review(doc_text: str) -> None:
    assert "revisión humana obligatoria" in doc_text.lower()
    assert "toda entrega" in doc_text.lower()


def test_pilot_flow_confidence_and_uncertainty_marking(doc_text: str) -> None:
    assert "incertidumbres" in doc_text.lower()
    assert "nivel de confianza" in doc_text.lower()
    assert "alto" in doc_text.lower()
    assert "medio" in doc_text.lower()
    assert "bajo" in doc_text.lower()


def test_pilot_flow_diplomatic_left_hand_recommendations(doc_text: str) -> None:
    assert "mano izquierda" in doc_text.lower()
    assert "sugerir" in doc_text.lower() or "sugiere" in doc_text.lower()
    assert "no imponer" in doc_text.lower()
    assert "no sustituir" in doc_text.lower()


def test_pilot_flow_no_training_no_cross_project_reuse(doc_text: str) -> None:
    assert "no se entrenan modelos" in doc_text.lower() or "entrenamiento" in doc_text.lower()
    assert "reutilización" in doc_text.lower()


def test_pilot_flow_expected_private_deliverables(doc_text: str) -> None:
    missing = [term for term in DELIVERABLE_TERMS if term.lower() not in doc_text.lower()]
    assert not missing


def test_pilot_flow_success_criteria_defined(doc_text: str) -> None:
    assert "criterios de éxito" in doc_text.lower()
    assert "flujo completo" in doc_text.lower()
