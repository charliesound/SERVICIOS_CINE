"""Tests for CID real project intake questionnaires document."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_real_project_intake_questionnaires_v1.md"
)

PHASE_ID = "AILINK.CID.REAL.PROJECT.INTAKE.QUESTIONNAIRES.PHASE6.2"

REQUIRED_BLOCKS = [
    "## 1. Objetivo del intake",
    "## 2. Reglas de privacidad del primer piloto real",
    "## 3. Datos mínimos del proyecto",
    "## 4. Confirmación de autorización y titularidad",
    "## 5. Cuestionario de productor / jefe de producción",
    "## 6. Cuestionario de ayudante de dirección",
    "## 7. Cuestionario de director",
    "## 8. Cuestionario de dirección de fotografía",
    "## 9. Cuestionario de sonido directo",
    "## 10. Cuestionario de arte / vestuario / maquillaje",
    "## 11. Cuestionario de postproducción",
    "## 12. Preguntas de prioridades creativas y productivas",
    "## 13. Preguntas para detectar restricciones críticas",
    "## 14. Preguntas que CID debe hacer si faltan datos",
    "## 15. Nivel de confianza del análisis",
    "## 16. Tono de recomendación de CID",
    "## 17. Qué queda fuera de esta fase",
    "## 18. Criterios de aceptación",
]

PRIVACY_TERMS = [
    "Primer piloto real con guion propio autorizado",
    "Plantillas genéricas de cuestionario, no respuestas reales",
    "No rellenar el repo con respuestas reales del guion propio",
    "No incluir guion real en el repo",
    "No incluir título real, escenas, diálogos, personajes confidenciales, localizaciones reales, nombres de personas, datos reales del proyecto ni outputs reales versionados",
]

PRODUCER_TERMS = [
    "presupuesto objetivo o rango",
    "número máximo de jornadas",
    "fechas deseadas",
    "localizaciones confirmadas o pendientes",
    "permisos",
    "transporte",
    "alojamiento",
    "equipo disponible",
    "restricciones económicas",
    "prioridades de producción",
]

AD_TERMS = [
    "disponibilidad de actores",
    "restricciones de calendario",
    "escenas críticas",
    "agrupación por localización",
    "día/noche",
    "menores, animales, vehículos, armas, agua, noche, exteriores complejos",
    "dependencias entre escenas",
    "prioridades del plan",
]

DIRECTOR_TERMS = [
    "escenas emocionalmente prioritarias",
    "tono",
    "referencias visuales",
    "estilo de puesta en escena",
    "escenas que necesitan más tiempo",
    "escenas que pueden simplificarse",
    "prioridades creativas",
]

CINEMATOGRAPHY_TERMS = [
    "estilo visual",
    "formato/cámara",
    "ópticas si aplica",
    "movimientos de cámara",
    "iluminación compleja",
    "exteriores dependientes de luz",
    "necesidades especiales",
]

SOUND_TERMS = [
    "diálogos críticos",
    "localizaciones ruidosas",
    "vehículos",
    "multitudes",
    "playback",
    "wild tracks",
    "ambientes",
    "posibles ADR",
    "riesgos de viento, tráfico, maquinaria, agua, ropa o acción física",
]

ART_TERMS = [
    "decorados complejos",
    "atrezzo clave",
    "cambios de vestuario",
    "continuidad",
    "época/estilo",
    "maquillaje especial",
    "duplicados necesarios",
]

POST_TERMS = [
    "necesidades de montaje",
    "VFX/grafismos/pantallas",
    "ADR previsto",
    "música/diseño sonoro",
    "color",
    "entregables",
    "riesgos de postproducción",
]


@pytest.fixture(scope="module")
def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_intake_questionnaires_document_exists() -> None:
    assert DOC_PATH.exists()


def test_intake_questionnaires_contains_phase_id(doc_text: str) -> None:
    assert PHASE_ID in doc_text


def test_intake_questionnaires_contains_required_blocks(doc_text: str) -> None:
    missing = [block for block in REQUIRED_BLOCKS if block not in doc_text]
    assert not missing


def test_intake_questionnaires_defines_first_authorized_internal_real_pilot(doc_text: str) -> None:
    assert "primer piloto real con guion propio autorizado" in doc_text.lower()
    assert "Intake privado y controlado" in doc_text


def test_intake_questionnaires_forbids_real_script_and_confidential_repo_data(doc_text: str) -> None:
    missing = [term for term in PRIVACY_TERMS if term not in doc_text]
    assert not missing
    assert "No incluir presupuesto real" in doc_text
    assert "No incluir fixtures reales" in doc_text


def test_intake_questionnaires_requires_authorization_and_ownership_confirmation(doc_text: str) -> None:
    assert "Confirmación de autorización y titularidad" in doc_text
    assert "autorización del titular" in doc_text
    assert "titularidad o permiso suficiente" in doc_text


def test_intake_questionnaires_explains_questionnaires_as_system_intelligence(doc_text: str) -> None:
    assert "Los cuestionarios no son burocracia" in doc_text
    assert "son la forma de que CID entienda la realidad del proyecto" in doc_text


def test_intake_questionnaires_contains_producer_questions(doc_text: str) -> None:
    missing = [term for term in PRODUCER_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_ad_questions(doc_text: str) -> None:
    missing = [term for term in AD_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_director_questions(doc_text: str) -> None:
    missing = [term for term in DIRECTOR_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_cinematography_questions(doc_text: str) -> None:
    missing = [term for term in CINEMATOGRAPHY_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_sound_questions(doc_text: str) -> None:
    missing = [term for term in SOUND_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_art_wardrobe_makeup_questions(doc_text: str) -> None:
    missing = [term for term in ART_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_contains_postproduction_questions(doc_text: str) -> None:
    missing = [term for term in POST_TERMS if term not in doc_text]
    assert not missing


def test_intake_questionnaires_requires_missing_data_questions(doc_text: str) -> None:
    assert "CID debe preguntar cuando falten datos" in doc_text
    assert "no debe inventar respuestas" in doc_text


def test_intake_questionnaires_requires_confidence_and_uncertainty_marking(doc_text: str) -> None:
    assert "CID debe marcar incertidumbres" in doc_text
    assert "CID debe asignar nivel de confianza al análisis" in doc_text
    assert "Alto:" in doc_text and "Medio:" in doc_text and "Bajo:" in doc_text


def test_intake_questionnaires_requires_diplomatic_recommendations(doc_text: str) -> None:
    assert "CID debe aconsejar con mano izquierda" in doc_text
    assert "CID debe sugerir, no imponer" in doc_text
    assert "CID debe explicar por qué recomienda algo" in doc_text


def test_intake_questionnaires_requires_human_review(doc_text: str) -> None:
    assert "Revisión humana obligatoria" in doc_text
    assert "Toda recomendación requiere revisión humana obligatoria" in doc_text


def test_intake_questionnaires_forbids_training_and_cross_project_reuse(doc_text: str) -> None:
    assert "No entrenamiento de modelos con el material" in doc_text
    assert "No reutilización fuera del proyecto" in doc_text
    assert "memoria de proyecto autorizada" in doc_text.lower()
