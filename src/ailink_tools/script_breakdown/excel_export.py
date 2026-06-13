"""Excel export for Script-to-Production Breakdown demo.

Generates valid .xlsx files using only Python stdlib (zipfile, xml.etree).
No external dependencies required.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring, parse
from xml.sax.saxutils import escape

from .schemas import BreakdownResult

ALLOWED_EXTENSIONS = {".xlsx"}


# ---------------------------------------------------------------------------
# XML constants for Office Open XML structure
# ---------------------------------------------------------------------------

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet4.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet5.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet6.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet7.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet8.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet9.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet10.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

RELS_ROOT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

WORKBOOK_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet4.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet5.xml"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet6.xml"/>
  <Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet7.xml"/>
  <Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet8.xml"/>
  <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet9.xml"/>
  <Relationship Id="rId10" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet10.xml"/>
  <Relationship Id="rId11" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="3">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><name val="Calibri"/></font>
  </fonts>
  <fills count="4">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF4472C4"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFD9E2F3"/></patternFill></fill>
  </fills>
  <borders count="1">
    <border><left/><right/><top/><bottom/><diagonal/></border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="4">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1"/>
    <xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
  </cellXfs>
</styleSheet>"""


# ---------------------------------------------------------------------------
# XML builders
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape XML text."""
    return escape(str(text))


def _col_letter(col: int) -> str:
    """Convert 1-based column number to Excel letter (1=A, 2=B, ...)."""
    result = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _make_cell_xml(col: int, row: int, value: object, style: int = 0,
                   formula: str | None = None) -> str:
    """Build XML string for a single cell."""
    ref = f"{_col_letter(col)}{row}"
    if formula is not None:
        return f'<c r="{ref}" s="{style}"><f>{_esc(formula)}</f></c>'
    if value is None:
        return f'<c r="{ref}" s="{style}"/>'
    if isinstance(value, (int, float)):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t>{_esc(str(value))}</t></is></c>'


def _make_sheet_xml(headers: list[str], rows: list[list],
                    total_row: list | None = None) -> str:
    """Build complete worksheet XML."""
    col_count = len(headers)
    row_count = len(rows) + 1  # +1 for header
    if total_row is not None:
        row_count += 1

    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        f'<dimension ref="A1:{_col_letter(col_count)}{row_count}"/>',
        '<sheetViews><sheetView tabSelected="0" workbookViewId="0">',
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>',
        '</sheetView></sheetViews>',
        '<sheetData>',
    ]

    # Header row (style 1 = bold blue)
    lines.append('<row r="1">')
    for ci, h in enumerate(headers, 1):
        lines.append(_make_cell_xml(ci, 1, h, style=1))
    lines.append('</row>')

    # Data rows
    for ri, row_data in enumerate(rows, 2):
        lines.append(f'<row r="{ri}">')
        for ci, val in enumerate(row_data, 1):
            style = 2 if (ri % 2 == 0) else 0  # alternating row fill
            lines.append(_make_cell_xml(ci, ri, val, style=style))
        lines.append('</row>')

    # Total row (if provided)
    if total_row is not None:
        tr = len(rows) + 2
        lines.append(f'<row r="{tr}">')
        for ci, val in enumerate(total_row, 1):
            style = 3  # bold
            if isinstance(val, str) and val.startswith("="):
                lines.append(_make_cell_xml(ci, tr, None, style=style, formula=val))
            else:
                lines.append(_make_cell_xml(ci, tr, val, style=style))
        lines.append('</row>')

    lines.append('</sheetData>')
    lines.append('<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>')
    lines.append('</worksheet>')
    return "\n".join(lines)


def _make_workbook_xml(sheet_names: list[str]) -> str:
    """Build workbook.xml with sheet references."""
    sheets = ""
    for i, name in enumerate(sheet_names, 1):
        sheets += f'<sheet name="{_esc(name)}" sheetId="{i}" r:id="rId{i}"/>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{sheets}</sheets>'
        '</workbook>'
    )


# ---------------------------------------------------------------------------
# Data builders
# ---------------------------------------------------------------------------

def _build_resumen(result: BreakdownResult) -> list[list]:
    v = result.viability
    return [
        ["Título", result.project["title"]],
        ["Tipo", result.project["type"]],
        ["Género", result.project["genre"]],
        ["Duración (min)", result.project["duration_minutes"]],
        ["Semanas de rodaje", result.project["shooting_weeks"]],
        ["Moneda", result.project["currency"]],
        ["Viabilidad global", f"{v['global_score']}/{10}"],
        ["Semáforo", v["global_traffic_light"]],
        ["Resumen viabilidad", v["summary"]],
    ]


def _build_escenas(result: BreakdownResult) -> list[list]:
    return [
        [s.scene_id, s.number, s.header, s.location, s.int_ext,
         s.day_night, ", ".join(s.characters), s.complexity, s.notes]
        for s in result.scenes
    ]


def _build_personajes(result: BreakdownResult) -> list[list]:
    return [
        [c.character_id, c.name, c.role, ", ".join(str(x) for x in c.scenes),
         c.age, c.complexity, c.notes]
        for c in result.characters
    ]


def _build_localizaciones(result: BreakdownResult) -> list[list]:
    return [
        [loc.location_id, loc.name, loc.type, loc.int_ext,
         ", ".join(str(x) for x in loc.scenes), loc.permits, loc.complexity]
        for loc in result.locations
    ]


def _build_riesgos(result: BreakdownResult) -> list[list]:
    return [
        [r.risk_id, r.description, r.impact, r.probability, r.mitigation]
        for r in result.risks
    ]


def _build_viabilidad(result: BreakdownResult) -> list[list]:
    return [
        [ind["indicator"], ind["score"], ind["max_score"],
         ind["traffic_light"], ind["justification"], ind["recommendation"]]
        for ind in result.viability["indicators"]
    ]


def _build_presupuesto(result: BreakdownResult) -> list[list]:
    return [
        [b.budget_id, b.category, b.low, b.mid, b.high,
         b.confidence, b.assumptions]
        for b in result.preliminary_budget
    ]


def _build_recomendaciones(result: BreakdownResult) -> list[list]:
    return [[i, rec] for i, rec in enumerate(result.recommendations, 1)]


def _build_revision_humana(result: BreakdownResult) -> list[list]:
    return [[note] for note in result.human_review_notes]


def _build_metadata(result: BreakdownResult) -> list[list]:
    m = result.metadata
    return [
        ["organization_id", m["organization_id"]],
        ["tenant_id", m["tenant_id"]],
        ["project_id", m["project_id"]],
        ["film_id", m["film_id"]],
        ["productora", m["organization_name"]],
        ["parser_version", m["parser_version"]],
        ["parser_type", m["parser_type"]],
        ["is_demo", str(m["is_demo"])],
    ]


def _presupuesto_total_row(rows: list[list]) -> list:
    """Build TOTAL row with SUM formulas."""
    total_baja = sum(r[2] for r in rows if isinstance(r[2], (int, float)))
    total_media = sum(r[3] for r in rows if isinstance(r[3], (int, float)))
    total_alta = sum(r[4] for r in rows if isinstance(r[4], (int, float)))
    n = len(rows) + 1  # last data row number (1-based, +1 for header)
    return [
        "TOTAL",
        "",
        f"=SUM(C2:C{n})",
        f"=SUM(D2:D{n})",
        f"=SUM(E2:E{n})",
        "",
        "",
    ]


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------

def _validate_path(path: Path) -> None:
    if not path.name:
        raise ValueError("Ruta vacía no permitida")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Extensión no permitida: {path.suffix}. "
            f"Permitidas: {ALLOWED_EXTENSIONS}"
        )


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

SHEET_NAMES = [
    "Resumen", "Escenas", "Personajes", "Localizaciones",
    "Riesgos", "Viabilidad", "Presupuesto", "Recomendaciones",
    "Revisión humana", "Metadata",
]


def export_excel(result: BreakdownResult, path: Path) -> Path:
    """Export breakdown result to Excel file using only stdlib.

    Args:
        result: The breakdown result to export.
        path: The output file path (must end in .xlsx).

    Returns:
        The path to the created file.

    Raises:
        ValueError: If the path is invalid or has wrong extension.
    """
    _validate_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Build sheet data
    sheets_data: list[tuple[str, list[str], list[list], list | None]] = [
        ("Resumen", ["Campo", "Valor"], _build_resumen(result), None),
        ("Escenas", ["ID", "Número", "Header", "Localización", "INT/EXT",
         "Día/Noche", "Personajes", "Complejidad", "Notas"],
         _build_escenas(result), None),
        ("Personajes", ["ID", "Nombre", "Rol", "Escenas", "Edad",
         "Complejidad", "Notas"], _build_personajes(result), None),
        ("Localizaciones", ["ID", "Nombre", "Tipo", "INT/EXT", "Escenas",
         "Permisos", "Complejidad"], _build_localizaciones(result), None),
        ("Riesgos", ["ID", "Descripción", "Impacto", "Probabilidad",
         "Mitigación"], _build_riesgos(result), None),
        ("Viabilidad", ["Indicador", "Puntuación", "Máximo", "Semáforo",
         "Justificación", "Recomendación"], _build_viabilidad(result), None),
        ("Presupuesto", ["ID", "Categoría", "Baja", "Media", "Alta",
         "Confianza", "Supuestos"], _build_presupuesto(result),
         _presupuesto_total_row(_build_presupuesto(result))),
        ("Recomendaciones", ["Número", "Recomendación"],
         _build_recomendaciones(result), None),
        ("Revisión humana", ["Nota"], _build_revision_humana(result), None),
        ("Metadata", ["Campo", "Valor"], _build_metadata(result), None),
    ]

    # Write ZIP
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS_ROOT)
        zf.writestr("xl/workbook.xml", _make_workbook_xml(SHEET_NAMES))
        zf.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS)
        zf.writestr("xl/styles.xml", STYLES)

        for i, (name, headers, rows, total) in enumerate(sheets_data, 1):
            xml = _make_sheet_xml(headers, rows, total)
            zf.writestr(f"xl/worksheets/sheet{i}.xml", xml)

    return path
