"""Tests for Script-to-Production Breakdown demo readiness document.

Verifies that the readiness document exists, contains all required sections,
includes allowed/prohibited claims, and does not create forbidden artifacts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

READINESS_DOC = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "product" / "script_breakdown"
    / "ailink_cid_script_to_production_breakdown_demo_readiness_v1.md"
)

REQUIRED_SECTIONS = [
    "Propósito",
    "Estado actual de la demo",
    "Flujo de demo de 5 minutos",
    "Guion verbal de demo",
    "Qué enseñar",
    "Qué NO enseñar todavía",
    "Claims permitidos",
    "Claims prohibidos",
    "Preguntas esperables de productores",
    "Aislamiento productora/película",
    "Conexión con Production Finance Control",
    "Conexión con CID",
    "Checklist antes de enseñar",
    "Criterios de PASS",
    "Próximos pasos tras la demo",
    "No-goals",
]

REQUIRED_KEYWORDS = [
    "Proyecto Demo Bruma",
    "demo controlada",
    "guion ficticio",
    "JSON",
    "Markdown",
    "Excel",
    "stdlib",
    "openpyxl",
    "presupuesto definitivo",
    "revisión humana",
    "productora puede tener varias películas",
    "organization_id",
    "tenant_id",
    "project_id",
    "film_id",
    "Production Finance Control",
    "CID Script Intelligence",
    "CID Production Intelligence",
    "CID Production Finance Control",
    "PASS",
    "LIMITED PASS",
    "FAIL",
]

ALLOWED_CLAIMS = [
    "primer desglose orientativo",
    "presupuesto preliminar revisable",
    "apoyo al productor",
    "detección temprana de riesgos",
    "demo local controlada",
    "requiere revisión humana",
]

PROHIBITED_CLAIMS = [
    "presupuesto exacto",
    "sustituye al productor",
    "sustituye al director de producción",
    "garantiza viabilidad",
    "producto final",
    "producto disponible",
    "IA real ya integrada",
    "procesa cualquier guion real",
    "integración SaaS ya disponible",
]

FORBIDDEN_PROMISES = [
    "presupuesto exacto",
    "producto final",
    "producto disponible",
    "procesa cualquier guion real",
    "IA real integrada",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def readiness_text() -> str:
    """Read readiness document content."""
    return READINESS_DOC.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def readiness_lines() -> list[str]:
    """Read readiness document as lines."""
    return READINESS_TEXT.splitlines()


# ---------------------------------------------------------------------------
# Tests: document existence and structure
# ---------------------------------------------------------------------------


def test_readiness_document_exists():
    """Readiness document must exist."""
    assert READINESS_DOC.exists(), f"Missing: {READINESS_DOC}"


def test_readiness_document_is_nonempty(readiness_text):
    """Readiness document must not be empty."""
    assert len(readiness_text) > 100


def test_readiness_has_all_sections(readiness_text):
    """Document must contain all 16 required sections."""
    missing = [s for s in REQUIRED_SECTIONS if s not in readiness_text]
    assert not missing, f"Missing sections: {missing}"


# ---------------------------------------------------------------------------
# Tests: required keywords
# ---------------------------------------------------------------------------


def test_readiness_contains_demo_bruma(readiness_text):
    assert "Proyecto Demo Bruma" in readiness_text


def test_readiness_contains_controlled_demo(readiness_text):
    assert "demo controlada" in readiness_text


def test_readiness_contains_fiction_script(readiness_text):
    assert "guion ficticio" in readiness_text


def test_readiness_contains_json(readiness_text):
    assert "JSON" in readiness_text


def test_readiness_contains_markdown(readiness_text):
    assert "Markdown" in readiness_text


def test_readiness_contains_excel(readiness_text):
    assert "Excel" in readiness_text


def test_readiness_contains_stdlib(readiness_text):
    assert "stdlib" in readiness_text


def test_readiness_contains_no_openpyxl(readiness_text):
    text_lower = readiness_text.lower()
    assert "openpyxl" in text_lower and (
        "sin openpyxl" in text_lower or "no openpyxl" in text_lower
    )


def test_readiness_contains_no_definitive_budget(readiness_text):
    assert "presupuesto definitivo" in readiness_text


def test_readiness_contains_human_review(readiness_text):
    assert "revisión humana" in readiness_text


def test_readiness_contains_multi_film(readiness_text):
    assert "productora puede tener varias películas" in readiness_text


def test_readiness_contains_org_id(readiness_text):
    assert "organization_id" in readiness_text


def test_readiness_contains_tenant_id(readiness_text):
    assert "tenant_id" in readiness_text


def test_readiness_contains_project_id(readiness_text):
    assert "project_id" in readiness_text


def test_readiness_contains_film_id(readiness_text):
    assert "film_id" in readiness_text


def test_readiness_contains_pfc(readiness_text):
    assert "Production Finance Control" in readiness_text


def test_readiness_contains_cid_script_intelligence(readiness_text):
    assert "CID Script Intelligence" in readiness_text


def test_readiness_contains_cid_production_intelligence(readiness_text):
    assert "CID Production Intelligence" in readiness_text


def test_readiness_contains_cid_production_finance_control(readiness_text):
    assert "CID Production Finance Control" in readiness_text


def test_readiness_contains_pass(readiness_text):
    assert "PASS" in readiness_text


def test_readiness_contains_limited_pass(readiness_text):
    assert "LIMITED PASS" in readiness_text


def test_readiness_contains_fail(readiness_text):
    assert "FAIL" in readiness_text


# ---------------------------------------------------------------------------
# Tests: allowed claims
# ---------------------------------------------------------------------------


def test_readiness_contains_allowed_claims(readiness_text):
    """All 6 allowed claims must appear in the document."""
    text_lower = readiness_text.lower()
    for claim in ALLOWED_CLAIMS:
        assert claim.lower() in text_lower, f"Missing allowed claim: {claim}"


# ---------------------------------------------------------------------------
# Tests: prohibited claims (as warnings, not positive claims)
# ---------------------------------------------------------------------------


def test_readiness_contains_prohibited_claims(readiness_text):
    """All 9 prohibited claims must appear as warnings, not positive claims."""
    text_lower = readiness_text.lower()
    for claim in PROHIBITED_CLAIMS:
        assert claim.lower() in text_lower, f"Missing prohibited claim warning: {claim}"


def _is_positive_claim(text: str, phrase: str) -> bool:
    """Check if phrase appears as a positive claim (not negated or prohibited).

    Returns False if phrase is:
    - Preceded by negation words
    - Inside a prohibited claims list item (starts with "- ")
    - Under a "Claims prohibidos" or "No-goals" section header
    """
    import re
    text_lower = text.lower()
    phrase_lower = phrase.lower()

    negations = [
        "no ", "no es ", "no se ", "sin ",
        "prohibido: ", "prohibido ", "evitar: ",
        "no es un ", "no es una ",
    ]

    lines = text_lower.splitlines()
    in_prohibited_section = False

    for line in lines:
        stripped = line.strip()

        # Track if we're in a prohibited/no-goals section
        if re.match(r"^##\s.*claims prohibidos", stripped) or re.match(r"^##\s.*no-goals", stripped):
            in_prohibited_section = True
            continue
        if re.match(r"^##\s", stripped) and in_prohibited_section:
            in_prohibited_section = False

        # If in prohibited section, phrase is NOT a positive claim
        if in_prohibited_section and phrase_lower in stripped:
            return False

        # If in a list item under prohibited section
        if in_prohibited_section and stripped.startswith("- ") and phrase_lower in stripped:
            return False

    # Check for negation context
    for match in re.finditer(re.escape(phrase_lower), text_lower):
        start = match.start()
        context_before = text_lower[max(0, start - 40):start]
        if any(neg in context_before for neg in negations):
            continue
        # Check if the line starts with "- " (list item in prohibited section)
        line_start = text_lower.rfind("\n", 0, start) + 1
        current_line = text_lower[line_start:start + len(phrase_lower)].strip()
        if current_line.startswith("- "):
            # Check if this is under a prohibited section by scanning backwards
            preceding_text = text_lower[:line_start]
            last_section = ""
            for m in re.finditer(r"^##\s+(.+)$", preceding_text, re.MULTILINE):
                last_section = m.group(1)
            if "prohibido" in last_section or "no-goal" in last_section:
                return False
        return True
    return False


def test_readiness_no_promises_exact_budget(readiness_text):
    """Must not promise 'presupuesto exacto' as a positive claim."""
    assert not _is_positive_claim(readiness_text, "presupuesto exacto")


def test_readiness_no_promises_final_product(readiness_text):
    """Must not promise 'producto final' as a positive claim."""
    assert not _is_positive_claim(readiness_text, "producto final")


def test_readiness_no_promises_available_product(readiness_text):
    """Must not promise 'producto disponible' as a positive claim."""
    assert not _is_positive_claim(readiness_text, "producto disponible")


def test_readiness_no_promises_any_script(readiness_text):
    """Must not promise 'procesa cualquier guion real' as a positive claim."""
    assert not _is_positive_claim(readiness_text, "procesa cualquier guion real")


def test_readiness_no_promises_real_ai(readiness_text):
    """Must not promise 'IA real integrada' as a positive claim."""
    assert not _is_positive_claim(readiness_text, "IA real integrada")


# ---------------------------------------------------------------------------
# Tests: no forbidden artifacts created
# ---------------------------------------------------------------------------


def test_readiness_no_xlsx_created():
    """No .xlsx files should be created in docs/ or tests/ by this phase."""
    docs_dir = READINESS_DOC.parent.parent.parent / "docs"
    tests_dir = READINESS_DOC.parent.parent.parent / "tests"
    for directory in [docs_dir, tests_dir]:
        xlsx_files = list(directory.rglob("*.xlsx"))
        assert not xlsx_files, f"Found .xlsx files: {xlsx_files}"


def test_readiness_no_pdf_created():
    """No .pdf files should be created in docs/ or tests/ by this phase."""
    docs_dir = READINESS_DOC.parent.parent.parent / "docs"
    tests_dir = READINESS_DOC.parent.parent.parent / "tests"
    for directory in [docs_dir, tests_dir]:
        pdf_files = list(directory.rglob("*.pdf"))
        assert not pdf_files, f"Found .pdf files: {pdf_files}"


def test_readiness_no_html_created():
    """No .html files should be created in docs/ or tests/ by this phase."""
    docs_dir = READINESS_DOC.parent.parent.parent / "docs"
    tests_dir = READINESS_DOC.parent.parent.parent / "tests"
    for directory in [docs_dir, tests_dir]:
        html_files = list(directory.rglob("*.html"))
        assert not html_files, f"Found .html files: {html_files}"


def test_readiness_no_csv_created():
    """No .csv files should be created in docs/ or tests/ by this phase."""
    docs_dir = READINESS_DOC.parent.parent.parent / "docs"
    tests_dir = READINESS_DOC.parent.parent.parent / "tests"
    for directory in [docs_dir, tests_dir]:
        csv_files = list(directory.rglob("*.csv"))
        assert not csv_files, f"Found .csv files: {csv_files}"
