"""Tests for Script-to-Production Breakdown demo exports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure src is in path
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ailink_tools.script_breakdown.demo_parser import parse_demo_script
from ailink_tools.script_breakdown.exports import (
    export_json,
    export_markdown,
)

# ---------------------------------------------------------------------------
# Demo script fixture
# ---------------------------------------------------------------------------

DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE

ANA BRUMA (30 años) está sentada en la cocina.
LEO PRADO (25 años) entra con prisa.

LEO: Han llamado del ayuntamiento.

ESCENA 2. EXT. CAMINO RURAL - AMANECER

Ana y Leo caminan por un camino de tierra.
Un perro (BISCA) los acompaña.

ANA: El informe dice que necesitamos tres permisos.

ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA

Ana entra en el BAR DEMO ESTACIÓN.
MARA SOL (45 años) está detrás de la barra.

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

ESCENA 7. INT. CASA DE ANA - NOCHE

Ana está sola en la cocina.
ANA: (al teléfono) Necesito hablar sobre los permisos.

ESCENA 8. EXT. CAMINO RURAL - NOCHE

Ana y Leo caminan por el camino de noche.
Un rayo ilumina el cielo.
ANA: Mañana tenemos que decidir.
"""


@pytest.fixture
def breakdown_result():
    """Parse demo script and return result."""
    return parse_demo_script(DEMO_SCRIPT)


def test_export_json(breakdown_result, tmp_path):
    """JSON export must work in tmp_path."""
    json_path = tmp_path / "breakdown.json"
    result_path = export_json(breakdown_result, json_path)
    assert result_path == json_path
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "project" in data
    assert "scenes" in data
    assert len(data["scenes"]) >= 8


def test_export_markdown(breakdown_result, tmp_path):
    """Markdown export must work in tmp_path."""
    md_path = tmp_path / "breakdown.md"
    result_path = export_markdown(breakdown_result, md_path)
    assert result_path == md_path
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "revisión humana" in content.lower()
    assert "presupuesto preliminar" in content.lower()
    assert "viabilidad" in content.lower()


def test_no_xlsx_generated(breakdown_result, tmp_path):
    """Export must not generate .xlsx files."""
    json_path = tmp_path / "breakdown.json"
    md_path = tmp_path / "breakdown.md"
    export_json(breakdown_result, json_path)
    export_markdown(breakdown_result, md_path)

    xlsx_files = list(tmp_path.rglob("*.xlsx"))
    assert xlsx_files == []


def test_no_pdf_generated(breakdown_result, tmp_path):
    """Export must not generate .pdf files."""
    json_path = tmp_path / "breakdown.json"
    md_path = tmp_path / "breakdown.md"
    export_json(breakdown_result, json_path)
    export_markdown(breakdown_result, md_path)

    pdf_files = list(tmp_path.rglob("*.pdf"))
    assert pdf_files == []


def test_no_html_generated(breakdown_result, tmp_path):
    """Export must not generate .html files."""
    json_path = tmp_path / "breakdown.json"
    md_path = tmp_path / "breakdown.md"
    export_json(breakdown_result, json_path)
    export_markdown(breakdown_result, md_path)

    html_files = list(tmp_path.rglob("*.html"))
    assert html_files == []


def test_export_json_wrong_extension(breakdown_result, tmp_path):
    """JSON export must reject wrong extension."""
    wrong_path = tmp_path / "breakdown.txt"
    with pytest.raises(ValueError, match="Extensión no permitida"):
        export_json(breakdown_result, wrong_path)


def test_export_markdown_wrong_extension(breakdown_result, tmp_path):
    """Markdown export must reject wrong extension."""
    wrong_path = tmp_path / "breakdown.txt"
    with pytest.raises(ValueError, match="Extensión no permitida"):
        export_markdown(breakdown_result, wrong_path)


def test_markdown_contains_isolation_ids(breakdown_result, tmp_path):
    """Markdown must contain isolation IDs."""
    md_path = tmp_path / "breakdown.md"
    export_markdown(breakdown_result, md_path)
    content = md_path.read_text(encoding="utf-8")
    assert "organization_id" in content
    assert "tenant_id" in content
    assert "project_id" in content
    assert "film_id" in content
