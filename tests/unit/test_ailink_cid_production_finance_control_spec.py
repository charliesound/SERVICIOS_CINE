from pathlib import Path


DOC_PATH = Path("docs/product/finance/ailink_cid_production_finance_control_spec_v1.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_production_finance_control_spec_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Production Finance Control Spec v1" in _doc()


def test_production_finance_control_spec_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Nombre provisional",
        "## 2. Propósito",
        "## 3. Encaje en AILinkCinema y CID",
        "## 4. Flujo audiovisual cubierto",
        "## 5. Principios",
        "## 6. Bloques funcionales",
        "## 7. Campos principales para gastos",
        "## 8. Campos principales para ingresos",
        "## 9. Contratos",
        "## 10. Nóminas y personal",
        "## 11. Asesoría y obligaciones",
        "## 12. Conciliación bancaria",
        "## 13. Excel editable futuro",
        "## 14. KPIs",
        "## 15. Alertas",
        "## 16. Roadmap",
        "## 17. No-goals",
        "## 18. Criterios de aceptación",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_production_finance_control_spec_contains_core_terms():
    doc = _doc()
    required = [
        "AILink Production Finance Control",
        "CID Production Finance Control",
        "CID Production Intelligence",
        "ingresos",
        "gastos",
        "contratos",
        "nóminas",
        "asesoría",
        "conciliación bancaria",
        "presupuesto vs real",
        "cashflow",
        "Excel editable",
        "revisión humana",
        "trazabilidad documental",
        "local-first",
        "No sustituye a la asesoría",
        "No runtime changes",
        "No fiscal certification claim",
        "No payroll engine claim",
        "No automatic legal compliance claim",
        "No tocar AILink Sync Dialogue",
        "No tocar CID SaaS actual",
        "5256f76",
        "ailink-cid-dev-stable-sync-dialogue-product-guard-smoke-phase4-1-20260613",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_spec_separates_sensitive_runtime_areas():
    doc = _doc()
    required = [
        "No tocar CID AI Jobs",
        "No tocar credit ledger",
        "No tocar billing",
        "No tocar pasarelas de pago, pagos reales ni billing runtime",
        "No tocar worker mock",
        "No tocar frontend actual",
        "No tocar PostgreSQL actual",
        "No tocar cualquier runtime existente",
        "No implementar OCR",
        "No implementar Excel real todavía",
        "No implementar importación PDF",
        "No implementar conciliación bancaria real",
        "No implementar app móvil/PWA",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_spec_clarifies_conceptual_status_and_payments():
    doc = _doc()
    required = [
        "Esta fase es conceptual/documental",
        "no representa un producto disponible ni una funcionalidad implementada",
        "control documental/financiero de pagos de producción",
        "No se refiere a pasarelas de pago, Stripe, checkout, billing runtime ni pagos reales del SaaS",
        "OCR, PWA, Excel, PDF y conciliación bancaria no son claim comercial",
        "producto disponible ni disponibilidad actual",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_spec_contains_finance_fields_and_outputs():
    doc = _doc()
    required = [
        "fecha",
        "número de documento",
        "proveedor",
        "NIF/CIF",
        "base imponible",
        "IVA soportado",
        "IVA repercutido",
        "estado de pago",
        "estado de cobro",
        "confianza de extracción",
        "Resumen ejecutivo",
        "Movimientos",
        "Pagadores",
        "Vencimientos de pago",
        "Vencimientos de cobro",
        "Evidencias",
        "Configuración",
    ]

    for phrase in required:
        assert phrase in doc


def test_production_finance_control_spec_avoids_unsafe_claims():
    doc = _doc().lower()
    forbidden = [
        "fase implementa backend",
        "fase implementa frontend",
        "se ha implementado ocr",
        "se ha implementado excel",
        "se ha implementado importación pdf",
        "se ha implementado conciliación bancaria real",
        "es software fiscal certificado",
        "cumplimiento legal automático garantizado",
        "sí sustituye a la asesoría",
        "sí sustituye a gestoría",
        "sí sustituye a contabilidad oficial",
        "payroll engine implementado",
        "el producto es software fiscal certificado",
        "software fiscal certificado disponible",
        "declara cumplimiento legal automático",
        "cumplimiento legal automático disponible",
        "producto disponible en esta fase",
        "funcionalidad implementada en esta fase",
        "ocr disponible",
        "excel disponible",
        "conciliación bancaria disponible",
        "commit creado",
        "tag creado",
        "push realizado",
    ]

    for phrase in forbidden:
        assert phrase not in doc, (
            f"unsafe claim or implementation fragment found: {phrase}"
        )
