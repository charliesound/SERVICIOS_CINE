"""Tests for Script-to-Production Breakdown budget total Phase 5.4."""

from __future__ import annotations

import inspect
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
    / "ailink_cid_script_to_production_breakdown_budget_total_v1.md"
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


def _sheet_xml(path: Path, sheet_num: int) -> str:
    with zipfile.ZipFile(path) as zf:
        return zf.read(f"xl/worksheets/sheet{sheet_num}.xml").decode("utf-8")


def _all_sheet_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        return "\n".join(
            zf.read(f"xl/worksheets/sheet{i}.xml").decode("utf-8")
            for i in range(1, 11)
        )


def test_budget_total_document_exists() -> None:
    assert DOC_PATH.exists()


def test_budget_total_document_contains_scope() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for expected in [
        "AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.EXCEL.BUDGET.TOTAL.PHASE5.4",
        "Total bajo",
        "Total medio",
        "Total alto",
        "Presupuesto preliminar revisable",
        "No presupuesto definitivo",
        "Requiere revisión humana",
        "No se importa openpyxl",
        "No se toca CreditBalance",
    ]:
        assert expected in text


def test_budget_total_xlsx_is_valid_zip(excel_path: Path) -> None:
    assert zipfile.is_zipfile(excel_path)


def test_budget_total_keeps_sheet_order(excel_path: Path) -> None:
    assert SHEET_NAMES == EXPECTED_SHEET_ORDER
    assert _sheet_names(excel_path) == EXPECTED_SHEET_ORDER


def test_budget_total_presupuesto_visible_block(excel_path: Path) -> None:
    xml = _sheet_xml(excel_path, 3)
    for expected in [
        "Total bajo",
        "Total medio",
        "Total alto",
        "presupuesto preliminar revisable",
        "No presupuesto definitivo",
        "Requiere revisión humana",
    ]:
        assert expected in xml


def test_budget_total_keeps_sum_formulas(excel_path: Path) -> None:
    xml = _sheet_xml(excel_path, 3)
    assert "SUM(C2:C19)" in xml
    assert "SUM(D2:D19)" in xml
    assert "SUM(E2:E19)" in xml


def test_budget_total_alert_styles_are_basic(excel_path: Path) -> None:
    with zipfile.ZipFile(excel_path) as zf:
        styles = zf.read("xl/styles.xml").decode("utf-8")
    assert "FFC6EFCE" in styles
    assert "FFFFEB9C" in styles
    assert "FFFFC7CE" in styles


def test_budget_total_visible_alert_texts_remain(excel_path: Path) -> None:
    xml = _all_sheet_xml(excel_path)
    for expected in [
        "verde",
        "amarillo",
        "rojo",
        "riesgo bajo",
        "riesgo medio",
        "riesgo alto",
        "revisar",
        "alerta",
    ]:
        assert expected in xml


def test_budget_total_no_openpyxl_in_source() -> None:
    source = inspect.getsource(
        __import__("ailink_tools.script_breakdown.excel_export", fromlist=["excel_export"])
    )
    assert "openpyxl" not in source


def test_budget_total_no_forbidden_formats(tmp_path: Path) -> None:
    result = parse_demo_script(DEMO_SCRIPT)
    export_excel(result, tmp_path / "demo.xlsx")
    assert list(tmp_path.rglob("*.pdf")) == []
    assert list(tmp_path.rglob("*.html")) == []
    assert list(tmp_path.rglob("*.csv")) == []
