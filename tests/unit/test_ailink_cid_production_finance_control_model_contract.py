from pathlib import Path


DOC_PATH = Path(
    "docs/product/finance/ailink_cid_production_finance_control_model_contract_v1.md"
)


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_production_finance_control_model_contract_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Production Finance Control Model Contract v1" in _doc()


def test_production_finance_control_model_contract_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito del contrato de modelo",
        "## 2. Encaje de producto",
        "## 3. Alcance",
        "## 4. Entidades principales",
        "## 5. Campos mínimos compartidos",
        "## 6. Campos por entidad",
        "## 7. Relaciones",
        "## 8. Estados",
        "## 9. Invariantes",
        "## 10. Categorías iniciales de gasto",
        "## 11. Categorías iniciales de ingreso",
        "## 12. Alertas",
        "## 13. Límites",
        "## 14. Encaje futuro",
        "## 15. No-goals",
        "## 16. Criterios de aceptación",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_production_finance_control_model_contract_contains_core_entities():
    doc = _doc()
    required = [
        "ProductionFinanceProject",
        "Budget",
        "BudgetCategory",
        "FinancialMovement",
        "Income",
        "Expense",
        "Contract",
        "InvoiceReceived",
        "InvoiceIssued",
        "PayrollItem",
        "Supplier",
        "Worker",
        "Payer",
        "Payment",
        "Collection",
        "BankStatement",
        "BankStatementLine",
        "ReconciliationMatch",
        "FinancialAlert",
        "DocumentEvidence",
        "ManualReviewItem",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_model_contract_contains_shared_model_fields():
    doc = _doc()
    required = [
        "logical_id",
        "project_id",
        "fechas",
        "importes",
        "moneda",
        "estado",
        "categoría",
        "documento origen",
        "confianza de extracción futura",
        "revisión humana",
        "timestamps conceptuales",
        "notas",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_model_contract_contains_relationships_and_states():
    doc = _doc()
    required = [
        "proyecto → presupuesto",
        "proyecto → movimientos",
        "gasto → proveedor",
        "ingreso → pagador",
        "contrato → proveedor/trabajador/pagador",
        "factura recibida → gasto",
        "factura emitida → ingreso",
        "nómina → trabajador",
        "pago → gasto/factura/nómina/contrato",
        "cobro → ingreso/factura emitida/contrato",
        "extracto bancario → líneas",
        "línea bancaria → conciliación",
        "documento → evidencia",
        "alerta → entidad afectada",
        "revisión manual → campo dudoso",
        "draft",
        "pending_review",
        "reviewed",
        "approved",
        "pending_payment",
        "paid",
        "partially_paid",
        "overdue",
        "cancelled",
        "reconciled",
        "unmatched",
        "disputed",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_model_contract_contains_complete_categories():
    doc = _doc()
    required = [
        "equipo técnico",
        "reparto",
        "cámara",
        "sonido",
        "arte",
        "vestuario",
        "maquillaje",
        "localizaciones",
        "transporte",
        "catering",
        "postproducción",
        "VFX",
        "música",
        "seguros",
        "legal",
        "administración",
        "distribución",
        "marketing",
        "otros",
        "aportación productor",
        "coproducción",
        "subvención",
        "preventas",
        "distribución",
        "ventas internacionales",
        "televisión/plataforma",
        "patrocinio",
        "product placement",
        "crowdfunding",
        "inversión privada",
        "anticipo",
        "otros ingresos",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_model_contract_contains_limits_and_no_goals():
    doc = _doc()
    required = [
        "Esta fase es conceptual/documental",
        "no representa un producto disponible",
        "no representa una funcionalidad implementada",
        "No runtime changes",
        "no software fiscal certificado",
        "no cumplimiento legal automático",
        "no motor de nóminas",
        "no sustituye a asesoría, gestoría, contabilidad oficial ni revisión humana",
        "no ejecuta pagos reales",
        "no toca pasarelas, Stripe, checkout ni billing runtime",
        "No tocar Docker",
        "No tocar Alembic",
        "No tocar `.env`",
        "No tocar modelos",
        "No tocar base de datos / DB",
        "No tocar configuración",
        "No tocar scripts operativos",
        "No tocar pasarelas de pago, pagos reales ni billing runtime",
        "No tocar CID SaaS actual",
        "No tocar AILink Sync Dialogue",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_model_contract_avoids_unsafe_claims():
    doc = _doc().lower()
    forbidden = [
        "producto disponible: sí",
        "funcionalidad implementada: sí",
        "el producto es software fiscal certificado",
        "cumplimiento legal automático garantizado",
        "cumplimiento legal automático disponible",
        "certifica cumplimiento legal automático",
        "motor de nóminas implementado",
        "sí ejecuta pagos reales",
        "ejecuta pagos reales de forma automatizada",
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
