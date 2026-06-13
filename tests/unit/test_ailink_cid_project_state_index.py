from pathlib import Path


DOC_PATH = Path("docs/project/ailink_cid_project_state_index_v1.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_project_state_index_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Project State Index v1" in _doc()


def test_project_state_index_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito del índice maestro",
        "## 2. Último HEAD/tag estable conocido",
        "## 3. Documentos de referencia principales",
        "## 4. Estado general de AILinkCinema",
        "## 5. Estado general de CID SaaS",
        "## 6. Estado de AILink Sync Dialogue",
        "## 7. Estado comercial/demo/beta",
        "## 8. Estado legal/landing/leads",
        "## 9. Estado de infraestructura/VPS",
        "## 10. Estado de Codex Skills",
        "## 11. Módulos o zonas sensibles",
        "## 12. Qué está validado",
        "## 13. Qué no existe todavía",
        "## 14. Qué no debe tocarse sin fase explícita",
        "## 15. Próximas fases recomendadas",
        "## 16. Criterios para decidir la siguiente fase",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_project_state_index_records_stable_head_and_tag():
    doc = _doc()
    required = [
        "c536367",
        "fotografía del estado en HEAD `c536367`",
        "no representa estado permanente",
        "Debe actualizarse cuando cambie el HEAD estable",
        "ailink-cid-dev-stable-project-safe-baseline-audit-phase1-20260613",
    ]

    for text in required:
        assert text in doc


def test_project_state_index_contains_critical_product_boundaries():
    doc = _doc()
    lower_doc = doc.lower()
    required = [
        "AILinkCinema",
        "CID — Cinematic Intelligence Direction",
        "AILink Sync Dialogue",
        "PostgreSQL-only",
        "Codex Skills",
        "No runtime changes",
        "No production public release",
        "local-first",
        "beta/demo",
    ]

    for text in required:
        assert text in doc

    assert "no tocar runtime sin fase explícita" in lower_doc


def test_project_state_index_keeps_documental_scope_and_no_runtime_claims():
    doc = _doc()
    lower_doc = doc.lower()

    required = [
        "Este índice no sustituye tests reales ni auditorías runtime",
        "no sustituye una auditoría runtime",
        "no valida la existencia real de todos los documentos referenciados",
        "no introduce runtime",
        "no hay producción pública completa",
        "no validadas para producción",
    ]
    for text in required:
        assert text in doc

    forbidden = [
        "fase implementa backend",
        "fase implementa frontend",
        "se ha refactorizado",
        "se ha corregido runtime",
        "producción pública completa: sí",
        "production public release: yes",
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
        assert text not in lower_doc, (
            f"unsafe claim or implementation fragment found: {text}"
        )


def test_project_state_index_explains_phase2_name_and_deferred_evidence_matrix():
    doc = _doc()
    required = [
        "El cambio de nombre frente a la recomendación previa es intencional",
        "Phase 1 recomendaba una fase de evidence/index",
        "en Phase 2 se crea primero el índice maestro operativo",
        "la matriz/evidencia queda desplazada a una fase posterior recomendada",
        "AILINK/CID.PROJECT.EVIDENCE.MATRIX.PHASE3",
    ]

    for text in required:
        assert text in doc
