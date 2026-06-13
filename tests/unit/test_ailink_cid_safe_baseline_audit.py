from pathlib import Path


DOC_PATH = Path("docs/project/ailink_cid_safe_baseline_audit_v1.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_safe_baseline_audit_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Safe Baseline Audit v1" in _doc()


def test_safe_baseline_audit_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Objetivo",
        "## 3. Último HEAD/tag estable conocido",
        "## 4. Estado general del repo",
        "## 5. Inventario de módulos principales",
        "## 6. Estado de CID SaaS",
        "## 7. Estado de AILink Sync Dialogue",
        "## 8. Estado de tests y guards",
        "## 9. Zonas sensibles",
        "## 10. Código que parece estable",
        "## 11. Código que requiere revisión futura",
        "## 12. Posibles fuentes de ruido",
        "## 13. Riesgos de tocar runtime",
        "## 14. Próximas fases recomendadas",
        "## 15. Criterios para decidir cuándo refactorizar",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_safe_baseline_audit_records_known_stable_head_and_tag():
    doc = _doc()
    required = [
        "15e8bc1",
        "ailink-cid-dev-stable-codex-skills-base-phase1-20260613",
        "chore: add Codex skills base for AILinkCinema CID",
        "Codex Skills",
    ]

    for text in required:
        assert text in doc


def test_safe_baseline_audit_is_documental_test_only():
    doc = _doc()
    required = [
        "auditoría documental y test-only",
        "No runtime changes",
        "no modifica comportamiento runtime",
        "No refactorizar",
        "No borrar archivos",
        "No arreglar código",
        "No cambiar lógica",
        "No hacer commit, tag ni push",
        "No declarar producción pública lista",
    ]

    for text in required:
        assert text in doc


def test_safe_baseline_audit_identifies_critical_boundaries():
    doc = _doc()
    lower_doc = doc.lower()
    required = [
        "AILinkCinema",
        "CID — Cinematic Intelligence Direction",
        "producción pública",
        "beta/demo controlada",
        "CID SaaS",
        "AILink Sync Dialogue",
        "Sync Dialogue queda separado de CID SaaS",
        "PostgreSQL-only",
        "local-first",
        "tenant context",
        "module access",
        "billing real",
        "pagos",
        "ComfyUI",
        "landing",
    ]

    for text in required:
        assert text in doc

    assert "no declarar producción pública lista" in lower_doc


def test_safe_baseline_audit_avoids_runtime_implementation_claims():
    doc = _doc().lower()
    assert "No promises of unimplemented features" in _doc()
    assert "observadas/inventariadas, no validadas para producción" in _doc()
    assert "fotografía de esta auditoría" in _doc()

    forbidden = [
        "fase implementa backend",
        "fase implementa frontend",
        "se ha refactorizado",
        "se ha corregido runtime",
        "producción pública lista: sí",
        "produccion publica lista: si",
        "full production-ready: yes",
        "payment lifecycle exists",
        "commit creado",
        "tag creado",
        "push realizado",
        "create table",
        "alter table",
        "drop table",
        "op.create_table",
        "base.metadata.create_all",
        "fastapi(",
        "@router.",
        "app.post(",
        "app.get(",
        "usestate(",
        "useeffect(",
    ]

    for text in forbidden:
        assert text not in doc, f"unsafe claim or implementation fragment found: {text}"
