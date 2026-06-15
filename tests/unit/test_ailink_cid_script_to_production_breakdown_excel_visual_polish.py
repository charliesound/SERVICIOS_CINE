"""Tests for Script-to-Production Breakdown Excel visual polish."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import fromstring

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT / "src"
DOC_PATH = (
    ROOT
    / "docs"
    / "product"
    / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_excel_visual_polish_v1.md"
)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ailink_tools.script_breakdown.demo_parser import parse_demo_script  # noqa: E402
from ailink_tools.script_breakdown.excel_export import SHEET_NAMES, export_excel  # noqa: E402


DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE
ESCENA 2. EXT. CAMINO RURAL - AMANECER
ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA
ESCENA 4. INT. BAR DEMO ESTACIÓN - NOCHE
ESCENA 5. EXT. CAMPO DE LAVANDA - DÍA
ESCENA 6. EXT. CASA DE ANA - DÍA
ESCENA 7. INT. CASA DE ANA - NOCHE
ESCENA 8. EXT. CAMINO RURAL - NOCHE
"""

EXPECTED_SHEET_ORDER = [
    "Resumen",
    "Viabilidad",
    "Presupuesto",
    "Riesgos",
    "Escenas",
    "Personajes",
    "Localizaciones",
    "Recomendaciones",
    "Revisión humana",
    "Metadata",
]

VISIBLE_WORKBOOK_TEXTS = [
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "no presupuesto definitivo",
    "revisión humana",
    "presupuesto preliminar",
    "guion → producción → finanzas",
]


@pytest.fixture()
def excel_path(tmp_path: Path) -> Path:
    result = parse_demo_script(DEMO_SCRIPT)
    path = tmp_path / "script_breakdown_demo_bruma.xlsx"
    export_excel(result, path)
    return path


def _sheet_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        root = fromstring(zf.read("xl/workbook.xml").decode("utf-8"))
    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return [sheet.attrib["name"] for sheet in root.findall(".//ns:sheet", ns)]


def _all_sheet_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        return "\n".join(
            zf.read(f"xl/worksheets/sheet{i}.xml").decode("utf-8")
            for i in range(1, 11)
        )


def test_visual_polish_document_exists() -> None:
    assert DOC_PATH.exists()


def test_visual_polish_document_contains_scope() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for expected in [
        "LIMITED PASS",
        "Proyecto Demo Bruma",
        "demo controlada",
        "guion ficticio",
        "no presupuesto definitivo",
        "revisión humana",
        "presupuesto preliminar",
        "stdlib-only",
        "sin openpyxl",
        "No se toca CreditBalance",
    ]:
        assert expected in text


def test_excel_sheet_order_for_presentation(excel_path: Path) -> None:
    assert SHEET_NAMES == EXPECTED_SHEET_ORDER
    assert _sheet_names(excel_path) == EXPECTED_SHEET_ORDER


def test_excel_contains_visible_demo_limit_texts(excel_path: Path) -> None:
    xml = _all_sheet_xml(excel_path)
    for expected in VISIBLE_WORKBOOK_TEXTS:
        assert expected in xml


def test_excel_contains_viability_legend(excel_path: Path) -> None:
    xml = _all_sheet_xml(excel_path)
    assert "Leyenda semáforos" in xml
    assert "atención prioritaria" in xml


def test_excel_keeps_metadata_at_end(excel_path: Path) -> None:
    assert _sheet_names(excel_path)[-1] == "Metadata"
    xml = _all_sheet_xml(excel_path)
    for expected in ["organization_id", "tenant_id", "project_id", "film_id"]:
        assert expected in xml


def test_excel_visual_polish_no_forbidden_formats(tmp_path: Path) -> None:
    result = parse_demo_script(DEMO_SCRIPT)
    export_excel(result, tmp_path / "demo.xlsx")
    assert list(tmp_path.rglob("*.pdf")) == []
    assert list(tmp_path.rglob("*.html")) == []
    assert list(tmp_path.rglob("*.csv")) == []
