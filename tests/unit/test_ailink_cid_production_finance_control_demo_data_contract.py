from pathlib import Path


DOC_PATH = Path(
    "docs/product/finance/ailink_cid_production_finance_control_demo_data_contract_v1.md"
)
ROOT = Path(".")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_demo_data_contract_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Production Finance Control Demo Data Contract v1" in _doc()


def test_demo_data_contract_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito",
        "## 2. Nota obligatoria",
        "## 3. Proyecto demo ficticio",
        "## 4. Datos demo de ingresos",
        "## 5. Datos demo de gastos",
        "## 6. Datos demo de contratos",
        "## 7. Datos demo de nóminas",
        "## 8. Datos demo de pagos y cobros",
        "## 9. Datos demo de conciliación bancaria",
        "## 10. Datos demo de presupuesto vs real",
        "## 11. Datos demo de cashflow",
        "## 12. Alertas demo",
        "## 13. Criterios visuales de la futura demo",
        "## 14. Gráficos conceptuales de demo",
        "## 15. Criterios de seguridad",
        "## 16. No-goals",
        "## 17. Encaje con presentación agosto/septiembre",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_demo_data_contract_contains_required_phrases():
    doc = _doc()
    required = [
        "AILink Production Finance Control",
        "CID Production Finance Control",
        "Proyecto Demo Aurora",
        "datos ficticios",
        "no datos reales",
        "no facturas reales",
        "no nóminas reales",
        "no contratos reales",
        "no cuentas bancarias reales",
        "Excel editable",
        "Resumen ejecutivo",
        "ingresos",
        "gastos",
        "contratos",
        "nóminas",
        "pagos",
        "cobros",
        "conciliación bancaria",
        "presupuesto vs real",
        "cashflow",
        "revisión humana",
        "trazabilidad documental",
        "gasto por categoría",
        "ingresos por categoría",
        "cashflow acumulado",
        "ranking de proveedores",
        "ranking de pagadores",
        "alertas por gravedad",
        "vencimientos próximos",
        "factura sin contrato",
        "nómina sin pago",
        "pago sin documento",
        "ingreso previsto no cobrado",
        "saldo semanal negativo",
        "baja confianza OCR futura",
        "No generar Excel real",
        "No generar `.xlsx`",
        "No generar `.csv`",
        "No runtime changes",
        "no software fiscal certificado",
        "no cumplimiento legal automático",
        "no motor de nóminas",
        "no sustituir asesoría",
        "5caf6aa",
        "ailink-cid-dev-stable-production-finance-control-excel-template-spec-phase3-20260613",
    ]

    for phrase in required:
        assert phrase in doc, f"missing phrase: {phrase}"


def test_demo_data_contract_no_spreadsheets_created():
    doc = _doc().lower()
    forbidden_fragments = [
        "create a spreadsheet",
        "generated spreadsheet",
        "excel file generated",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc, f"unexpected spreadsheet artifact mention: {fragment}"

    spreadsheet_artifacts = []
    finance_dir = DOC_PATH.parent
    for path in finance_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".xlsx", ".xls", ".ods", ".numbers"}:
            spreadsheet_artifacts.append(path)
            continue
        if (
            path.suffix.lower() == ".csv"
            and "production_finance_control" in path.name.lower()
            and "demo" in path.name.lower()
        ):
            spreadsheet_artifacts.append(path)

    assert spreadsheet_artifacts == []


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


def test_demo_data_contract_minimal_demo_ids():
    doc = _doc()

    inc_count = doc.count("INC-DEMO-")
    assert inc_count >= 8, f"expected at least 8 INC-DEMO- IDs, found {inc_count}"

    exp_count = doc.count("EXP-DEMO-")
    assert exp_count >= 14, f"expected at least 14 EXP-DEMO- IDs, found {exp_count}"

    con_count = doc.count("CON-DEMO-")
    assert con_count >= 8, f"expected at least 8 CON-DEMO- IDs, found {con_count}"

    payroll_count = doc.count("PAYROLL-DEMO-")
    assert payroll_count >= 6, (
        f"expected at least 6 PAYROLL-DEMO- IDs, found {payroll_count}"
    )

    bank_count = doc.count("BANK-DEMO-")
    assert bank_count >= 8, f"expected at least 8 BANK-DEMO- IDs, found {bank_count}"

    cf_count = doc.count("CF-DEMO-")
    assert cf_count >= 8, f"expected at least 8 CF-DEMO- IDs, found {cf_count}"


def test_demo_data_contract_avoids_unsafe_claims():
    doc = _doc().lower()
    forbidden = [
        "se ha implementado",
        "producto disponible: sí",
        "funcionalidad implementada: sí",
        "software fiscal certificado disponible",
        "cumplimiento legal automático garantizado",
        "certifica cumplimiento legal automático",
        "motor de nóminas implementado",
        "sí ejecuta pagos reales",
        "pago real",
        "billing runtime activo",
        "commit creado",
        "tag creado",
        "push realizado",
        "datos bancarios reales",
        "factura real",
        "contrato real",
        "nómina real",
        "dni real",
        "nie real",
        "iban real",
    ]

    for phrase in forbidden:
        assert phrase not in doc, (
            f"unsafe claim or implementation fragment found: {phrase}"
        )
