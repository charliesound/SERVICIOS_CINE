"""Tests for AILink Sync Dialogue commercial readiness QA."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DOC = ROOT / "docs" / "product" / "launch" / "ailink_sync_dialogue_commercial_readiness_qa_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "launch" / "ailink_sync_dialogue_launch_index_summary_v1.md",
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "linkedin-beta-card.png",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "hero-report-mockup.png",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_assembly_runbook_v1.md",
    ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_beta_leads_operations_runbook_v1.md",
]

REQUIRED = [
    "# AILink Sync Dialogue — Commercial Readiness QA v1",
    "## 4. Qué se puede enseñar ya",
    "## 5. Qué no se puede prometer",
    "## 6. Qué archivo usar para demo",
    "## 7. Qué imagen usar primero",
    "## 8. Qué post publicar primero",
    "## 9. Qué decir a una escuela de cine",
    "## 10. Qué decir a una productora",
    "## 11. Qué pedir a un beta tester",
    "## 12. Qué falta antes de publicar landing real",
    "## 13. Qué falta antes de contactar gente",
    "## 14. Decisión recomendada ahora",
    "## 18. Próxima acción recomendada",
    "Contactar manualmente con 5 a 10 leads cualificados",
    "No implementar todavía CRM, Supabase, formulario ni pagos",
    "AILink Sync Dialogue",
    "CID",
    "local-first",
    "beta privada",
    "escuelas de cine",
    "productoras",
]

FORBIDDEN = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "STRIPE_SECRET",
    "SUPABASE_SERVICE_ROLE",
    "C:\\",
    "/mnt/",
    "\\\\wsl.localhost",
]


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_commercial_readiness_qa_exists():
    assert DOC.exists()


def test_commercial_readiness_qa_references_existing_files():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_commercial_readiness_qa_has_required_sections_and_phrases():
    content = _doc()
    for text in REQUIRED:
        assert text in content


def test_commercial_readiness_qa_keeps_no_goals_clear():
    content = _doc()
    for text in [
        "Esta fase no implementa frontend",
        "No prometer:",
        "No pedir todavía:",
        "No implementar todavía CRM",
        "No abrir fase técnica de CRM/Supabase/formulario",
    ]:
        assert text in content


def test_commercial_readiness_qa_keeps_ailink_and_cid_separate():
    content = _doc()
    assert "La separación entre AILink Sync Dialogue y CID" in content
    assert "Confundir AILink Sync Dialogue con CID" in content


def test_commercial_readiness_qa_has_no_forbidden_runtime_terms():
    content = _doc()
    for text in FORBIDDEN:
        assert text not in content


def test_commercial_readiness_qa_does_not_claim_finished_capabilities():
    content = _doc().lower()
    for text in [
        "producto público completo disponible",
        "formulario real funcionando ya",
        "crm funcionando ya",
        "pago online activo ya",
        "instalador disponible",
        "waveform sync disponible",
        "transcripción disponible",
        "reconocimiento visual de claqueta disponible",
        "integración directa disponible",
    ]:
        assert text not in content
