"""Tests for Script-to-Production Breakdown demo parser."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure src is in path
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ailink_tools.script_breakdown.demo_parser import (
    DEMO_MARKERS,
    parse_demo_script,
)
from ailink_tools.script_breakdown.schemas import BreakdownResult

# ---------------------------------------------------------------------------
# Demo script fixture – contains all required markers
# ---------------------------------------------------------------------------

DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE

ANA BRUMA (30 años) está sentada en la cocina de su casa rural.
Su hermano LEO PRADO (25 años) entra con prisa.

LEO: Han llamado del ayuntamiento.

ESCENA 2. EXT. CAMINO RURAL - AMANECER

Ana y Leo caminan por un camino de tierra.
Un perro (BISCA) los acompaña.

ANA: El informe dice que necesitamos tres permisos.

ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA

Ana entra en el BAR DEMO ESTACIÓN.
MARA SOL (45 años) está detrás de la barra.
NORA CERECO (60 años) está sentada leyendo.

MARA: Ana, ¿ya has hablado con el alcalde?

ESCENA 4. INT. BAR DEMO ESTACIÓN - NOCHE

Reunión de producción. Ana, Leo, Mara y BRUNO VALLE (35 años).
BRUNO: El sonido va a ser complicado.

ESCENA 5. EXT. CAMPO DE LAVANDA - DÍA

Ana camina sola por un campo de lavanda.
ANA (V.O.): Este lugar puede ser perfecto.

ESCENA 6. EXT. CASA DE ANA - DÍA

Leo está reparando una valla.
Un gato (NIEBLA) pasa cerca.
LEO: ¿Y si el alcalde dice que no?

ESCENA 7. INT. CASA DE ANA - NOCHE

Ana está sola en la cocina.
ANA: (al teléfono) Necesito hablar sobre los permisos.

ESCENA 8. EXT. CAMINO RURAL - NOCHE

Ana y Leo caminan por el camino de noche.
Un rayo ilumina el cielo.
ANA: Mañana tenemos que decidir.
"""


def test_parser_detects_8_scenes():
    """Parser must detect at least 8 scenes."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert isinstance(result, BreakdownResult)
    assert len(result.scenes) >= 8


def test_parser_detects_5_characters():
    """Parser must detect at least 5 characters."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert len(result.characters) >= 5


def test_parser_detects_5_locations():
    """Parser must detect at least 5 locations."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert len(result.locations) >= 5


def test_parser_generates_risks():
    """Parser must generate at least 10 risks."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert len(result.risks) >= 10


def test_parser_generates_18_budget_categories():
    """Parser must generate 18 budget categories."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert len(result.preliminary_budget) >= 18


def test_parser_includes_viability_global():
    """Parser must include global viability."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert "viability" in result.to_dict()
    assert "global_score" in result.viability
    assert "global_traffic_light" in result.viability


def test_parser_includes_human_review():
    """Parser must include human review notes."""
    result = parse_demo_script(DEMO_SCRIPT)
    assert len(result.human_review_notes) > 0
    for note in result.human_review_notes:
        assert isinstance(note, str)
        assert len(note) > 0


def test_parser_includes_isolation_ids():
    """Parser must include organization_id, tenant_id, project_id, film_id."""
    result = parse_demo_script(DEMO_SCRIPT)
    meta = result.metadata
    assert "organization_id" in meta
    assert "tenant_id" in meta
    assert "project_id" in meta
    assert "film_id" in meta
    assert meta["organization_id"].startswith("ORG-DEMO-")
    assert meta["tenant_id"].startswith("TENANT-DEMO-")
    assert meta["project_id"].startswith("PROJECT-DEMO-")
    assert meta["film_id"].startswith("FILM-DEMO-")


def test_parser_rejects_non_demo_input():
    """Parser must reject input that is not the controlled demo script."""
    with pytest.raises(ValueError, match="no soportado"):
        parse_demo_script("This is not a demo script")


def test_parser_rejects_partial_input():
    """Parser must reject partial input missing some markers."""
    with pytest.raises(ValueError, match="no soportado"):
        parse_demo_script("ESCENA 1. INT. CASA DE ANA - NOCHE\nSome text")


def test_parser_no_ai_ocr_pdf():
    """Parser must not use AI, OCR, PDF, Final Draft, or Fountain."""
    import inspect

    source = inspect.getsource(parse_demo_script)
    forbidden = ["import openai", "import pytesseract", "import fitz",
                  "import fountain", "import final_draft"]
    for term in forbidden:
        assert term not in source, f"forbidden import found: {term}"


def test_parser_scene_ids_are_stable():
    """Parser must generate stable scene IDs."""
    result1 = parse_demo_script(DEMO_SCRIPT)
    result2 = parse_demo_script(DEMO_SCRIPT)
    ids1 = [s.scene_id for s in result1.scenes]
    ids2 = [s.scene_id for s in result2.scenes]
    assert ids1 == ids2


def test_parser_character_ids_are_stable():
    """Parser must generate stable character IDs."""
    result1 = parse_demo_script(DEMO_SCRIPT)
    result2 = parse_demo_script(DEMO_SCRIPT)
    ids1 = [c.character_id for c in result1.characters]
    ids2 = [c.character_id for c in result2.characters]
    assert ids1 == ids2


def test_parser_budget_ids_are_stable():
    """Parser must generate stable budget IDs."""
    result1 = parse_demo_script(DEMO_SCRIPT)
    result2 = parse_demo_script(DEMO_SCRIPT)
    ids1 = [b.budget_id for b in result1.preliminary_budget]
    ids2 = [b.budget_id for b in result2.preliminary_budget]
    assert ids1 == ids2


def test_parser_json_serializable():
    """Parser result must be JSON serializable."""
    import json

    result = parse_demo_script(DEMO_SCRIPT)
    json_str = result.to_json()
    parsed = json.loads(json_str)
    assert "project" in parsed
    assert "scenes" in parsed
    assert "characters" in parsed
    assert "locations" in parsed
    assert "risks" in parsed
    assert "viability" in parsed
    assert "preliminary_budget" in parsed
    assert "recommendations" in parsed
    assert "human_review_notes" in parsed
    assert "metadata" in parsed
