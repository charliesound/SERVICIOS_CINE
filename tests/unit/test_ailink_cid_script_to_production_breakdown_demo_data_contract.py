from pathlib import Path


DOC_PATH = Path(
    "docs/product/script_breakdown/"
    "ailink_cid_script_to_production_breakdown_demo_data_contract_v1.md"
)
ROOT = Path(".")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_demo_data_contract_document_exists():
    assert DOC_PATH.exists()
    assert (
        "AILink/CID Script-to-Production Breakdown Demo Data Contract v1" in _doc()
    )


def test_demo_data_contract_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito",
        "## 2. Nota obligatoria",
        "## 3. Proyecto demo",
        "## 4. Guion ficticio controlado",
        "## 5. Personajes esperados",
        "## 6. Localizaciones esperadas",
        "## 7. Desglose esperado por escena",
        "## 8. Desglose esperado por departamentos",
        "## 9. Riesgos esperados",
        "## 10. Viabilidad esperada",
        "## 11. Presupuesto preliminar esperado",
        "## 12. Recomendaciones esperadas",
        "## 13. Salidas futuras esperadas",
        "## 14. Criterios para futura demo funcional",
        "## 15. No-goals",
        "## 16. Claims permitidos",
        "## 17. Claims prohibidos",
        "## 18. Aislamiento por productora y película",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_demo_data_contract_contains_required_phrases():
    doc = _doc()
    required = [
        "AILink Script-to-Production Breakdown",
        "CID Script-to-Production Breakdown",
        "Proyecto Demo Bruma",
        "guion ficticio",
        "drama thriller rural",
        "desglose esperado por escena",
        "personajes esperados",
        "localizaciones esperadas",
        "riesgos esperados",
        "viabilidad esperada",
        "presupuesto preliminar esperado",
        "recomendaciones esperadas",
        "vista en pantalla",
        "Excel editable",
        "PDF opcional bajo demanda",
        "Production Finance Control",
        "plan de rodaje",
        "call sheet / orden diaria",
        "partes de rodaje",
        "montaje diario",
        "revisión humana",
        "no presupuesto definitivo",
        "No parser real",
        "No IA real",
        "No Excel real",
        "No PDF real",
        "No HTML real",
        "No runtime changes",
        "17ef578",
        "ailink-cid-dev-stable-script-to-production-breakdown-spec-phase1-20260613",
        "productora/cliente puede tener varias películas",
        "propio espacio de datos",
        "no deben mezclarse",
        "organization_id",
        "tenant_id",
        "project_id",
        "film_id",
        "aislamiento",
        "una productora",
        "otra productora",
        "varias películas",
    ]

    for phrase in required:
        assert phrase in doc, f"missing phrase: {phrase}"


def test_demo_data_contract_minimal_demo_ids():
    doc = _doc()

    scene_count = doc.count("SCENE-DEMO-")
    assert scene_count >= 8, (
        f"expected at least 8 SCENE-DEMO- IDs, found {scene_count}"
    )

    char_count = doc.count("CHAR-DEMO-")
    assert char_count >= 5, (
        f"expected at least 5 CHAR-DEMO- IDs, found {char_count}"
    )

    loc_count = doc.count("LOC-DEMO-")
    assert loc_count >= 5, (
        f"expected at least 5 LOC-DEMO- IDs, found {loc_count}"
    )

    risk_count = doc.count("RISK-DEMO-")
    assert risk_count >= 10, (
        f"expected at least 10 RISK-DEMO- IDs, found {risk_count}"
    )

    budget_count = doc.count("BUDGET-DEMO-")
    assert budget_count >= 18, (
        f"expected at least 18 BUDGET-DEMO- IDs, found {budget_count}"
    )


def test_demo_data_contract_no_runtime_artifacts():
    doc = _doc().lower()
    forbidden_fragments = [
        "create a spreadsheet",
        "generated spreadsheet",
        "excel file generated",
        "pdf generated",
        "html generated",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc, f"unexpected artifact mention: {fragment}"

    runtime_artifacts = []
    spec_dir = DOC_PATH.parent
    for path in spec_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".xlsx", ".xls", ".ods", ".numbers"}:
            runtime_artifacts.append(path)
            continue
        if (
            path.suffix.lower() == ".csv"
            and "script_breakdown" in path.name.lower()
        ):
            runtime_artifacts.append(path)
            continue
        if (
            path.suffix.lower() == ".pdf"
            and "script_breakdown" in path.name.lower()
        ):
            runtime_artifacts.append(path)
            continue
        if (
            path.suffix.lower() == ".html"
            and "script_breakdown" in path.name.lower()
        ):
            runtime_artifacts.append(path)

    assert runtime_artifacts == []


def test_demo_data_contract_no_runtime_imports():
    doc = _doc().lower()
    runtime_imports = [
        "import pandas",
        "import openpyxl",
        "import fpdf",
        "import weasyprint",
        "import jinja2",
        "from sqlalchemy",
        "import aiohttp",
        "import httpx",
    ]
    for imp in runtime_imports:
        assert imp not in doc, f"runtime import found in document: {imp}"


def test_demo_data_contract_no_unsafe_claims():
    doc = _doc().lower()
    forbidden = [
        "se ha implementado",
        "producto disponible: sí",
        "funcionalidad implementada: sí",
        "commit creado",
        "tag creado",
        "push realizado",
    ]

    for phrase in forbidden:
        assert phrase not in doc, (
            f"unsafe claim or implementation fragment found: {phrase}"
        )


def test_demo_data_contract_no_real_data():
    doc = _doc().lower()
    real_data_indicators = [
        "iban es",
        "iban:",
        "es66 2100",
        "es91 2100",
        "es79 2100",
        "12345678z",
        "12345678x",
        "12345678y",
        "dni:",
        "nie:",
        "@gmail.com",
        "@hotmail.com",
        "@outlook.com",
        "@yahoo.com",
        "612345678",
        "623456789",
        "912345678",
        "923456789",
    ]

    for indicator in real_data_indicators:
        assert indicator not in doc, f"real data indicator found: {indicator}"
