from pathlib import Path


DOC_PATH = Path(
    "docs/product/finance/ailink_cid_production_finance_control_excel_template_spec_v1.md"
)
ROOT = Path(".")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_excel_template_spec_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Production Finance Control Excel Template Spec v1" in _doc()


def test_excel_template_spec_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito de la plantilla",
        "## 2. Encaje de producto",
        "## 3. Separación de capas",
        "## 4. Hojas previstas",
        "## 5. Resumen ejecutivo",
        "## 6. Movimientos",
        "## 7. Ingresos",
        "## 8. Gastos",
        "## 9. Contratos",
        "## 10. Nóminas",
        "## 11. Asesoría y obligaciones",
        "## 12. Conciliación bancaria",
        "## 13. Presupuesto vs real",
        "## 14. Cashflow",
        "## 15. Proveedores y pagadores",
        "## 16. Personal",
        "## 17. Vencimientos",
        "## 18. Alertas",
        "## 19. Revisión manual",
        "## 20. Evidencias",
        "## 21. Configuración",
        "## 22. Glosario",
        "## 23. Gráficos conceptuales",
        "## 24. Validaciones conceptuales",
        "## 25. Fórmulas conceptuales",
        "## 26. No-goals",
        "## 27. Criterios de aceptación",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_excel_template_spec_contains_required_phrases():
    doc = _doc()
    required = [
        "AILink Production Finance Control",
        "CID Production Finance Control",
        "Excel editable",
        "Esta fase es conceptual/documental",
        "No representa producto disponible",
        "No representa funcionalidad implementada",
        "No genera Excel real",
        "No crea archivo `.xlsx`",
        "No es contrato API ni esquema de base de datos",
        "no es software fiscal certificado",
        "no declara cumplimiento legal automático",
        "No motor de nóminas",
        "No sustituir asesoría",
        "No runtime changes",
        "Resumen ejecutivo",
        "Movimientos",
        "Ingresos",
        "Gastos",
        "Contratos",
        "Nóminas",
        "Asesoría y obligaciones",
        "Conciliación bancaria",
        "Presupuesto vs real",
        "Cashflow",
        "Alertas",
        "Revisión manual",
        "Evidencias",
        "Configuración",
        "Glosario",
        "ingresos totales",
        "gastos totales",
        "resultado neto",
        "pendiente de pago",
        "pendiente de cobro",
        "saldo a 30 días",
        "documentos sin conciliar",
        "revisión humana",
        "trazabilidad documental",
        "gasto por categoría",
        "ingresos por categoría",
        "ranking de proveedores",
        "ranking de pagadores",
        "total = base + IVA - retención",
        "resultado_neto = ingresos_totales - gastos_totales",
        "saldo_acumulado",
        "No generar Excel real",
        "No generar `.xlsx`",
        "3cdd5c5",
        "ailink-cid-dev-stable-production-finance-control-model-contract-phase2-20260613",
    ]

    for phrase in required:
        assert phrase in doc


def test_excel_template_spec_contains_complete_worksheet_lists_and_logic():
    doc = _doc()
    required = [
        "Resumen ejecutivo.",
        "Movimientos.",
        "Ingresos.",
        "Gastos.",
        "Contratos.",
        "Nóminas.",
        "Asesoría y obligaciones.",
        "Conciliación bancaria.",
        "Presupuesto vs real.",
        "Cashflow.",
        "Proveedores.",
        "Pagadores.",
        "Personal.",
        "Vencimientos de pago.",
        "Vencimientos de cobro.",
        "Alertas.",
        "Revisión manual.",
        "Evidencias.",
        "Configuración.",
        "Glosario.",
        "gasto por categoría",
        "ingresos por categoría",
        "evolución semanal de gasto",
        "evolución semanal de ingresos",
        "cashflow acumulado",
        "alertas por gravedad",
        "importes numéricos",
        "fechas válidas",
        "revisión humana obligatoria si confianza es baja",
    ]

    for phrase in required:
        assert phrase in doc


def test_excel_template_spec_does_not_create_spreadsheets_or_related_exports():
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
        if path.suffix.lower() == ".csv" and "production_finance_control_excel" in path.name.lower():
            spreadsheet_artifacts.append(path)

    assert spreadsheet_artifacts == []


def test_excel_template_spec_avoids_unsafe_claims():
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
        "create table",
        "alter table",
        "drop table",
        "sqlalchemy(",
        "base.metadata.create_all",
    ]

    for phrase in forbidden:
        assert phrase not in doc, (
            f"unsafe claim or implementation fragment found: {phrase}"
        )
