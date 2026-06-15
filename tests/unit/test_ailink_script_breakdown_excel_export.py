"""Tests for Script-to-Production Breakdown Excel export.

Uses only stdlib (zipfile, xml.etree) to verify .xlsx output.
No openpyxl dependency.
"""

from __future__ import annotations

import inspect
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import fromstring

import pytest

# Ensure src is in path
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ailink_tools.script_breakdown.demo_parser import parse_demo_script
from ailink_tools.script_breakdown.excel_export import (
    ALLOWED_EXTENSIONS,
    SHEET_NAMES,
    export_excel,
)

# ---------------------------------------------------------------------------
# Demo script fixture
# ---------------------------------------------------------------------------

DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE

ANA BRUMA (30 anos) esta sentada en la cocina.
LEO PRADO (25 anos) entra con prisa.

LEO: Han llamado del ayuntamiento.

ESCENA 2. EXT. CAMINO RURAL - AMANECER

Ana y Leo caminan por un camino de tierra.

ANA: El informe dice que necesitamos tres permisos.

ESCENA 3. EXT. PUEBLO DEMO BRUMA - D\xcdA

Ana entra en el BAR DEMO ESTACI\xd3N.

MARA: Ana, ya has hablado con el alcalde?

ESCENA 4. INT. BAR DEMO ESTACI\xd3N - NOCHE

Reunion de produccion.

BRUNO: El sonido va a ser complicado.

ESCENA 5. EXT. CAMPO DE LAVANDA - D\xcdA

Ana camina sola por un campo de lavanda.

ESCENA 6. EXT. CASA DE ANA - D\xcdA

Leo esta reparando una valla.

LEO: Y si el alcalde dice que no?

ESCENA 7. INT. CASA DE ANA - NOCHE

Ana esta sola en la cocina.

ANA: (al telefono) Necesito hablar sobre los permisos.

ESCENA 8. EXT. CAMINO RURAL - NOCHE

Ana y Leo caminan por el camino de noche.

ANA: Manana tenemos que decidir.
"""


@pytest.fixture
def breakdown_result():
    """Parse demo script and return result."""
    return parse_demo_script(DEMO_SCRIPT)


@pytest.fixture
def excel_path(tmp_path):
    """Return Excel output path in tmp_path."""
    return tmp_path / "breakdown.xlsx"


# ---------------------------------------------------------------------------
# Helpers for inspecting xlsx as ZIP/XML
# ---------------------------------------------------------------------------

def _open_xlsx(path: Path) -> zipfile.ZipFile:
    """Open xlsx as ZipFile."""
    return zipfile.ZipFile(str(path))


def _read_workbook(zf: zipfile.ZipFile) -> str:
    """Read workbook.xml content."""
    return zf.read("xl/workbook.xml").decode("utf-8")


def _get_sheet_names(zf: zipfile.ZipFile) -> list[str]:
    """Parse sheet names from workbook.xml."""
    xml = _read_workbook(zf)
    root = fromstring(xml)
    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets = root.findall(".//ns:sheet", ns)
    return [s.attrib["name"] for s in sheets]


def _get_sheet_xml(zf: zipfile.ZipFile, sheet_num: int) -> str:
    """Read sheet XML content."""
    return zf.read(f"xl/worksheets/sheet{sheet_num}.xml").decode("utf-8")


def _count_rows_in_sheet(zf: zipfile.ZipFile, sheet_num: int) -> int:
    """Count <row> elements in a sheet."""
    xml = _get_sheet_xml(zf, sheet_num)
    root = fromstring(xml)
    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return len(root.findall(".//ns:row", ns))


def _get_cell_values(zf: zipfile.ZipFile, sheet_num: int,
                     row: int) -> list[str | None]:
    """Extract cell values from a specific row."""
    xml = _get_sheet_xml(zf, sheet_num)
    root = fromstring(xml)
    ns = {"ns": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    row_el = None
    for r in root.findall(".//ns:row", ns):
        if r.attrib.get("r") == str(row):
            row_el = r
            break
    if row_el is None:
        return []
    values = []
    for c in row_el.findall("ns:c", ns):
        # Try inline string
        is_el = c.find("ns:is", ns)
        if is_el is not None:
            t_el = is_el.find("ns:t", ns)
            values.append(t_el.text if t_el is not None else None)
            continue
        # Try value
        v_el = c.find("ns:v", ns)
        if v_el is not None:
            values.append(v_el.text)
            continue
        # Try formula
        f_el = c.find("ns:f", ns)
        if f_el is not None:
            values.append(f_el.text)
            continue
        values.append(None)
    return values


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_export_excel_creates_file(breakdown_result, excel_path):
    """Excel export must create the file."""
    result = export_excel(breakdown_result, excel_path)
    assert result == excel_path
    assert excel_path.exists()


def test_export_excel_has_10_sheets(breakdown_result, excel_path):
    """Excel must have exactly 10 sheets."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        names = _get_sheet_names(zf)
    assert len(names) == 10


def test_export_excel_sheet_names(breakdown_result, excel_path):
    """Excel sheet names must match expected list."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        names = _get_sheet_names(zf)
    assert names == SHEET_NAMES


def test_export_excel_resumen_content(breakdown_result, excel_path):
    """Resumen sheet must have project title and viability."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        # Sheet 1 = Resumen
        row2 = _get_cell_values(zf, 1, 2)
        xml = _get_sheet_xml(zf, 1)
    assert "Proyecto Demo Bruma" in row2
    assert "Viabilidad global" in xml
    assert "5.5/10" in xml


def test_export_excel_resumen_has_visible_demo_limits(breakdown_result, excel_path):
    """Resumen must make demo limitations visible."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        xml = _get_sheet_xml(zf, 1)
    assert "demo controlada" in xml
    assert "guion ficticio" in xml
    assert "no presupuesto definitivo" in xml
    assert "revisión humana" in xml
    assert "presupuesto preliminar" in xml
    assert "guion → producción → finanzas" in xml


def test_export_excel_escenas_row_count(breakdown_result, excel_path):
    """Escenas sheet must have 8 data rows + header = 9 rows."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        count = _count_rows_in_sheet(zf, 5)  # Sheet 5 = Escenas
    assert count == 9


def test_export_excel_personajes_row_count(breakdown_result, excel_path):
    """Personajes sheet must have 5 data rows + header = 6 rows."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        count = _count_rows_in_sheet(zf, 6)  # Sheet 6 = Personajes
    assert count == 6


def test_export_excel_presupuesto_has_total(breakdown_result, excel_path):
    """Presupuesto sheet must include total row and visible total block."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        count = _count_rows_in_sheet(zf, 3)  # Sheet 3 = Presupuesto
    assert count == 26  # 1 header + 18 data + 1 total + 6 visible block rows


def test_export_excel_presupuesto_total_formula(breakdown_result, excel_path):
    """Presupuesto TOTAL row must have SUM formulas."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        row20 = _get_cell_values(zf, 3, 20)  # Sheet 3, row 20 = total
    assert row20[0] == "TOTAL"
    # Check that columns C, D, E (indices 2, 3, 4) have SUM formulas
    for idx in [2, 3, 4]:
        val = row20[idx]
        assert val is not None, f"Missing formula at index {idx}"
        assert str(val).startswith("="), f"Col {idx} not a formula: {val}"


def test_export_excel_presupuesto_has_visible_total_block(breakdown_result, excel_path):
    """Presupuesto must show producer-facing total labels and warnings."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        xml = _get_sheet_xml(zf, 3)
    for expected in [
        "Total bajo",
        "Total medio",
        "Total alto",
        "presupuesto preliminar revisable",
        "No presupuesto definitivo",
        "Requiere revisión humana",
    ]:
        assert expected in xml


def test_export_excel_metadata_ids(breakdown_result, excel_path):
    """Metadata sheet must have all 4 isolation IDs."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        # Sheet 10 = Metadata
        metadata = {}
        for row_num in range(2, 10):
            vals = _get_cell_values(zf, 10, row_num)
            if vals and len(vals) >= 2 and vals[0]:
                metadata[vals[0]] = vals[1]
    assert "organization_id" in metadata
    assert "tenant_id" in metadata
    assert "project_id" in metadata
    assert "film_id" in metadata
    assert metadata["organization_id"] == "ORG-DEMO-001"
    assert metadata["tenant_id"] == "TENANT-DEMO-001"
    assert metadata["project_id"] == "PROJECT-DEMO-001"
    assert metadata["film_id"] == "FILM-DEMO-001"


def test_export_excel_viabilidad_has_traffic_light_legend(breakdown_result, excel_path):
    """Viabilidad sheet must include a textual semáforo legend."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        xml = _get_sheet_xml(zf, 2)
    assert "Leyenda semáforos" in xml
    assert "verde" in xml
    assert "amarillo" in xml
    assert "naranja" in xml
    assert "rojo" in xml
    assert "riesgo bajo" in xml
    assert "riesgo medio" in xml
    assert "riesgo alto" in xml


def test_export_excel_has_basic_alert_styles(breakdown_result, excel_path):
    """Workbook styles must include separate green/yellow/orange/red fills."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        styles = zf.read("xl/styles.xml").decode("utf-8")
        viability_xml = _get_sheet_xml(zf, 2)
        risks_xml = _get_sheet_xml(zf, 4)
        resumen_xml = _get_sheet_xml(zf, 1)
    assert "FFC6EFCE" in styles  # green
    assert "FFFFEB9C" in styles  # yellow
    assert "FFF4B183" in styles  # orange
    assert "FFFFC7CE" in styles  # red
    assert 's="4"' in viability_xml
    assert 's="5"' in viability_xml or 's="5"' in resumen_xml
    assert 's="6"' in viability_xml
    assert 's="7"' in viability_xml or 's="7"' in risks_xml or 's="7"' in resumen_xml


def test_export_excel_orange_semaphore_is_not_yellow(breakdown_result, excel_path):
    """Naranja must use its own fill/style and remain visible as text."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        styles = zf.read("xl/styles.xml").decode("utf-8")
        viability_xml = _get_sheet_xml(zf, 2)
    assert "FFFFEB9C" in styles
    assert "FFF4B183" in styles
    assert styles.index("FFFFEB9C") != styles.index("FFF4B183")
    assert "naranja" in viability_xml
    assert "atención prioritaria" in viability_xml
    assert 's="6"' in viability_xml


def test_export_excel_is_valid_zip(breakdown_result, excel_path):
    """Excel file must be a valid ZIP archive."""
    export_excel(breakdown_result, excel_path)
    assert zipfile.is_zipfile(excel_path)


def test_export_excel_has_required_xml_files(breakdown_result, excel_path):
    """Excel must contain required XML files."""
    export_excel(breakdown_result, excel_path)
    with _open_xlsx(excel_path) as zf:
        names = zf.namelist()
    assert "[Content_Types].xml" in names
    assert "_rels/.rels" in names
    assert "xl/workbook.xml" in names
    assert "xl/_rels/workbook.xml.rels" in names
    assert "xl/styles.xml" in names
    for i in range(1, 11):
        assert f"xl/worksheets/sheet{i}.xml" in names


def test_export_excel_no_pdf_generated(breakdown_result, tmp_path):
    """Excel export must not generate .pdf files."""
    excel_path = tmp_path / "breakdown.xlsx"
    export_excel(breakdown_result, excel_path)
    pdf_files = list(tmp_path.rglob("*.pdf"))
    assert pdf_files == []


def test_export_excel_no_html_generated(breakdown_result, tmp_path):
    """Excel export must not generate .html files."""
    excel_path = tmp_path / "breakdown.xlsx"
    export_excel(breakdown_result, excel_path)
    html_files = list(tmp_path.rglob("*.html"))
    assert html_files == []


def test_export_excel_no_csv_generated(breakdown_result, tmp_path):
    """Excel export must not generate .csv files."""
    excel_path = tmp_path / "breakdown.xlsx"
    export_excel(breakdown_result, excel_path)
    csv_files = list(tmp_path.rglob("*.csv"))
    assert csv_files == []


def test_export_excel_wrong_extension(breakdown_result, tmp_path):
    """Excel export must reject wrong extension."""
    wrong_path = tmp_path / "breakdown.txt"
    with pytest.raises(ValueError, match="Extensión no permitida"):
        export_excel(breakdown_result, wrong_path)


def test_no_openpyxl_in_source():
    """excel_export.py must not import openpyxl."""
    source = inspect.getsource(
        __import__("ailink_tools.script_breakdown.excel_export",
                    fromlist=["excel_export"])
    )
    assert "openpyxl" not in source, "openpyxl found in excel_export.py source"
