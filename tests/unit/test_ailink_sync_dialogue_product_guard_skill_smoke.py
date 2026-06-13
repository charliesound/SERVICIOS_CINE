from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_product_guard_skill_smoke_v1.md")
APPROVED_SKILL_PATH = Path(
    ".agents/skills/ailink-sync-dialogue-product-guard/SKILL.md"
)
SKILLS_ROOT = Path(".agents/skills")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_product_guard_skill_smoke_document_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue Product Guard Skill Smoke v1" in _doc()


def test_product_guard_skill_smoke_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito del smoke test",
        "## 2. Qué skill se está probando",
        "## 3. Último HEAD/tag estable",
        "## 4. Escenario de prueba",
        "## 5. Qué debe permitir la skill",
        "## 6. Qué debe bloquear o advertir",
        "## 7. Claims permitidos, claims prohibidos y guardrails operativos",
        "## 8. Señales de uso correcto",
        "## 9. Señales de fallo",
        "## 10. Resultado esperado del smoke test",
        "## 11. Próximas fases recomendadas",
        "## 12. Criterios de aceptación",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_product_guard_skill_smoke_contains_required_terms():
    doc = _doc()
    required = [
        "AILink Sync Dialogue",
        "ailink-sync-dialogue-product-guard",
        "fb7bb2c",
        "ailink-cid-dev-stable-sync-dialogue-product-guard-skill-phase4-20260613",
        "local-first",
        "beta/demo controlada",
        "No runtime changes",
        "No production public release",
        "No promises of unimplemented features",
        "no subir material audiovisual real",
        "no cloud",
        "sincronización automática final",
        "edición automática final",
        "DaVinci",
        "Avid",
        "Premiere",
        "CID SaaS",
        "CRM",
        "pagos",
        "landing pública",
        "VPS productivo",
        "un agente escribe, otro audita",
    ]

    for phrase in required:
        assert phrase in doc


def test_product_guard_skill_smoke_declares_documental_scope():
    doc = _doc()
    required = [
        "Este smoke test valida el uso documental de la skill",
        "No modifica la skill",
        "no crea nuevas skills",
        "no modifica `.agents/skills`",
        "La fase queda estrictamente documental/test-only",
        "Esta fase no modifica la skill; solo valida su uso documental",
    ]

    for phrase in required:
        assert phrase in doc


def test_product_guard_skill_smoke_verifies_approved_skill_exists():
    assert APPROVED_SKILL_PATH.exists()
    text = APPROVED_SKILL_PATH.read_text(encoding="utf-8")
    assert "name: ailink-sync-dialogue-product-guard" in text
    assert "AILink Sync Dialogue" in text
    assert "local-first" in text
    assert "beta/demo" in text
    assert "un agente escribe, otro audita" in text


def test_product_guard_skill_smoke_does_not_create_new_sync_dialogue_skills():
    doc = _doc()
    assert "La fase declara que no crea nuevas skills" in doc
    assert "La fase declara que no modifica `.agents/skills`" in doc

    sync_dialogue_skill_dirs = [
        path
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir()
        and (
            "sync-dialogue" in path.name
            or "sync_dialogue" in path.name
            or path.name.startswith("ailink-sync")
        )
    ]

    # Currently only the approved Sync Dialogue skill should exist; future
    # Sync Dialogue skills require their own explicit phase.
    assert sync_dialogue_skill_dirs == [APPROVED_SKILL_PATH.parent]


def test_product_guard_skill_smoke_avoids_runtime_claims():
    doc = _doc().lower()
    forbidden = [
        "fase implementa backend",
        "fase implementa frontend",
        "se ha refactorizado",
        "se ha corregido runtime",
        "production public release: yes",
        "cloud habilitado",
        "sincronización automática final implementada",
        "edición automática final implementada",
        "integración real con davinci implementada",
        "integración real con avid implementada",
        "integración real con premiere implementada",
        "commit creado",
        "tag creado",
        "push realizado",
    ]

    for phrase in forbidden:
        assert phrase not in doc, (
            f"unsafe claim or implementation fragment found: {phrase}"
        )
