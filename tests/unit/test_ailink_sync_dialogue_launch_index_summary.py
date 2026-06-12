"""Tests for the AILink Sync Dialogue launch index summary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
DOC = ROOT / "docs" / "product" / "launch" / "ailink_sync_dialogue_launch_index_summary_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "assets_manifest.json",
    ROOT / "docs" / "product" / "social" / "ailink_sync_dialogue_social_launch_pack_v1.md",
    ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_beta_leads_operations_runbook_v1.md",
    ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_legal_web_texts_spec_v1.md",
    ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_landing_legal_integration_spec_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_production_pack_spec_v1.md",
]

REQUIRED = [
    "# AILink Sync Dialogue — Launch Index Summary v1",
    "## 2. Estado actual estable",
    "## 3. Documentos principales",
    "## 4. Qué se puede enseñar ya",
    "## 5. Qué no se debe enseñar como producto terminado",
    "## 6. Mensaje comercial aprobado",
    "## 7. Público objetivo prioritario",
    "## 8. Orden recomendado de uso comercial",
    "## 9. Checklist antes de enseñar a terceros",
    "## 10. Checklist antes de publicar landing real",
    "## 11. Próximas decisiones",
    "## 13. Relación con CID",
    "landing estática exportable",
    "reporte HTML",
    "social launch pack",
    "flujo manual de leads",
    "beta privada",
    "local-first",
    "No vender AILink Sync Dialogue como CID",
    "No implementar CRM",
    "No crea formulario",
    "No crea Supabase",
]

FORBIDDEN = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "STRIPE_SECRET",
    "/mnt/",
    "C:\\",
    "\\\\wsl.localhost",
]


def _doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_launch_index_summary_exists():
    assert DOC.exists()


def test_launch_index_summary_references_existing_files():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_launch_index_summary_has_required_content():
    content = _doc()
    for text in REQUIRED:
        assert text in content


def test_launch_index_summary_keeps_product_and_cid_separate():
    content = _doc()
    assert "AILink Sync Dialogue es una herramienta independiente" in content
    assert "CID sigue siendo el SaaS integral de AILinkCinema" in content
    assert "No usar cuenta CID como requisito" in content


def test_launch_index_summary_contains_no_forbidden_runtime_terms():
    content = _doc()
    for text in FORBIDDEN:
        assert text not in content


def test_launch_index_summary_does_not_claim_finished_product():
    content = _doc().lower()
    for text in [
        "presentar como producto final listo",
        "saaas público listo",
        "formulario funcional disponible",
        "crm implementado",
        "supabase conectado",
        "waveform sync disponible",
        "transcripción disponible",
        "claqueta visual disponible",
    ]:
        assert text not in content
