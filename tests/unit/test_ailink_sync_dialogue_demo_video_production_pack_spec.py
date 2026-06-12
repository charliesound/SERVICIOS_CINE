"""Tests for the AILink Sync Dialogue demo video production pack spec."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_production_pack_spec_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_subtitles_es_v1.srt",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_voiceover_es_v1.txt",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_assembly_runbook_v1.md",
    ROOT / "docs" / "product" / "social" / "ailink_sync_dialogue_social_launch_pack_v1.md",
    ROOT / "docs" / "product" / "beta" / "ailink_sync_dialogue_beta_leads_operations_runbook_v1.md",
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "assets_manifest.json",
]

REQUIRED = [
    "# AILink Sync Dialogue — Demo Video Production Pack Spec v1",
    "## 3. Non-goals",
    "## 5. Nombres de archivo recomendados",
    "## 6. Versiones recomendadas",
    "## 7. Subtítulos",
    "## 8. Locución",
    "## 9. Miniaturas",
    "## 10. Metadatos de publicación",
    "## 12. Checklist de revisión editorial",
    "## 13. Checklist técnico",
    "## 14. Checklist legal/comercial",
    "## 17. Criterios de aceptación de esta fase",
    "No crea MP4",
    "No crea audio",
    "No crea miniaturas",
    "ailink_sync_dialogue_demo_master_1920x1080_es_v1.mp4",
    "ailink_sync_dialogue_demo_short_1920x1080_es_v1.mp4",
    "ailink_sync_dialogue_demo_square_1080x1080_es_v1.mp4",
    "ailink_sync_dialogue_demo_vertical_1080x1920_es_v1.mp4",
    "ailink_sync_dialogue_demo_publication_metadata_v1.json",
    "1920x1080",
    "1080x1080",
    "1080x1920",
    "Landing AILinkCinema",
    "LinkedIn",
    "Facebook",
    "beta privada",
    "No publicar automáticamente",
    "No activar automatizaciones",
    "El vídeo no confunde AILink Sync Dialogue con CID",
    "El vídeo no pide subir material audiovisual",
    "El vídeo no muestra secretos",
    "Resolución correcta",
    "Audio claro",
    "Subtítulos revisados",
    "landing legal revisada",
]

FORBIDDEN = [
    "FastAPI",
    "APIRouter",
    "AsyncSession",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "STRIPE_SECRET",
    "payment intent",
    "checkout session",
    "/mnt/",
    "C:\\",
    "\\\\wsl.localhost",
]


def _spec() -> str:
    return SPEC.read_text(encoding="utf-8")


def test_demo_video_production_pack_spec_exists():
    assert SPEC.exists()


def test_demo_video_production_pack_spec_references_existing_files():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_demo_video_production_pack_spec_has_required_content():
    content = _spec()
    for text in REQUIRED:
        assert text in content


def test_demo_video_production_pack_spec_has_metadata_fields():
    content = _spec()
    for field in [
        "title",
        "short_title",
        "description",
        "language",
        "duration_seconds",
        "version",
        "target_audience",
        "publication_channels",
        "landing_url",
        "beta_status",
        "limitations",
        "cta",
        "source_assets",
        "review_status",
        "approved_by",
        "approved_at",
    ]:
        assert field in content


def test_demo_video_production_pack_spec_avoids_forbidden_terms():
    content = _spec()
    for text in FORBIDDEN:
        assert text not in content


def test_demo_video_production_pack_spec_avoids_unsafe_claims():
    content = _spec().lower()
    for text in [
        "edición automática garantizada",
        "reemplaza al montador",
        "producto final garantizado",
        "acceso inmediato garantizado",
        "cumplimiento legal garantizado",
    ]:
        assert text not in content
