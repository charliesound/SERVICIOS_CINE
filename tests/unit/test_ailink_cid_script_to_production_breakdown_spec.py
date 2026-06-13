from pathlib import Path


DOC_PATH = Path(
    "docs/product/script_breakdown/"
    "ailink_cid_script_to_production_breakdown_spec_v1.md"
)
ROOT = Path(".")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_breakdown_spec_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Script-to-Production Breakdown Spec v1" in _doc()


def test_breakdown_spec_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Nombre provisional",
        "## 2. Propósito",
        "## 3. Flujo conceptual",
        "## 4. Datos que debe extraer del guion",
        "## 5. Desglose por escena",
        "## 6. Desglose por departamentos",
        "## 7. Análisis de viabilidad",
        "## 8. Semáforos de viabilidad",
        "## 9. Presupuesto preliminar",
        "## 10. Recomendaciones automáticas conceptuales",
        "## 11. Salidas futuras",
        "## 12. Encaje con Production Finance Control",
        "## 13. Encaje con AILink Sync Dialogue",
        "## 14. Encaje con presentación agosto/septiembre",
        "## 15. No-goals",
        "## 16. Claims permitidos",
        "## 17. Claims prohibidos",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_breakdown_spec_contains_required_phrases():
    doc = _doc()
    required = [
        "AILink Script-to-Production Breakdown",
        "CID Script-to-Production Breakdown",
        "CID Script Intelligence",
        "CID Production Intelligence",
        "CID Production Finance Control",
        "guion",
        "desglose de producción",
        "análisis de viabilidad",
        "presupuesto preliminar",
        "Production Finance Control",
        "AILink Sync Dialogue",
        "escenas",
        "personajes",
        "localizaciones",
        "interior/exterior",
        "día/noche",
        "arte",
        "vestuario",
        "maquillaje",
        "atrezzo",
        "vehículos",
        "animales",
        "menores",
        "VFX",
        "stunts",
        "permisos",
        "viajes",
        "complejidad logística",
        "complejidad artística",
        "complejidad técnica",
        "complejidad financiera",
        "riesgo de cashflow",
        "viabilidad global",
        "estimación baja",
        "estimación media",
        "estimación alta",
        "revisión humana",
        "beta/controlada",
        "no presupuesto definitivo",
        "no sustituto de productor",
        "no sustituto de director de producción",
        "no integración real con Production Finance Control",
        "no integración real con Sync Dialogue",
        "No runtime changes",
        "a73628f",
        "ailink-cid-dev-stable-production-finance-control-demo-data-contract-phase4-20260613",
        "vista en pantalla",
        "Excel editable",
        "salida principal",
        "PDF opcional",
        "bajo demanda",
        "No generar PDF real",
        "No generar HTML real",
        "No PDF automático",
    ]

    for phrase in required:
        assert phrase in doc, f"missing phrase: {phrase}"


def test_breakdown_spec_no_runtime_artifacts():
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
        if path.suffix.lower() == ".csv" and "script_breakdown" in path.name.lower():
            runtime_artifacts.append(path)
            continue
        if path.suffix.lower() == ".pdf" and "script_breakdown" in path.name.lower():
            runtime_artifacts.append(path)
            continue
        if path.suffix.lower() == ".html" and "script_breakdown" in path.name.lower():
            runtime_artifacts.append(path)

    assert runtime_artifacts == []


def test_breakdown_spec_no_unsafe_claims():
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


def test_breakdown_spec_no_runtime_imports():
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
