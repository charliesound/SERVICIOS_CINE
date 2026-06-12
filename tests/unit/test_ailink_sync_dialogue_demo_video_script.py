"""Tests for the AILink Sync Dialogue demo video script document."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md"
ASSET_DIR = ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue"

EXPECTED_ASSETS = [
    "hero-report-mockup.png",
    "report-summary.png",
    "match-suggestions-table.png",
    "media-files-table.png",
    "privacy-local-first.png",
    "linkedin-beta-card.png",
]

REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Demo Video Script v1",
    "## 7. Guion principal — 60–90 segundos",
    "## 8. Guion ampliado — 2 minutos",
    "## 9. Versión corta — 30–45 segundos",
    "## 10. Capturas recomendadas",
    "## 12. CTA final",
    "## 18. Checklist final antes de publicar",
    "## 19. Non-goals de esta fase",
    "## 20. Criterios de aceptación",
]

REQUIRED_TERMS = [
    "Prepara el material de rodaje para montaje en minutos.",
    "local-first",
    "Sin cloud en la versión actual",
    "beta privada",
    "caso controlado",
    "report.html",
    "media_files.csv",
    "match_suggestions.csv",
    "scan_result.json",
    "score",
    "razones",
    "timecode",
    "ffprobe",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "promete sincronizar todo automáticamente",
    "sincronización automática completa disponible",
    "reemplaza al montador",
    "reemplaza al ayudante de montaje",
    "automatiza todo el trabajo del montador",
    "waveform sync ya disponible",
    "transcripción ya disponible",
    "claqueta visual ya disponible",
    "instalador final ya disponible",
    "integración directa ya disponible",
    "producto final listo para publicar",
    "sube tu material audiovisual",
    "envíanos tu material audiovisual",
]

FORBIDDEN_TECH_REFERENCES = [
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "FastAPI",
    "APIRouter",
    "AsyncSessionLocal",
    "CreditLedger",
    "AIJobRepository",
    "/mnt/",
    "\\\\wsl.localhost",
    "C:\\",
]


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_demo_video_script_exists():
    assert SCRIPT.exists()


def test_demo_video_script_has_required_headings():
    content = _script()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_demo_video_script_references_existing_assets():
    content = _script()
    for asset in EXPECTED_ASSETS:
        assert asset in content
        assert (ASSET_DIR / asset).exists(), asset


def test_demo_video_script_contains_required_terms():
    content = _script()
    for term in REQUIRED_TERMS:
        assert term in content


def test_demo_video_script_contains_all_outputs():
    content = _script()
    for output in ["report.html", "media_files.csv", "match_suggestions.csv", "scan_result.json"]:
        assert output in content


def test_demo_video_script_has_three_duration_versions():
    content = _script()
    assert "60–90 segundos" in content
    assert "2 minutos" in content
    assert "30–45 segundos" in content


def test_demo_video_script_has_storyboard_timing_blocks():
    content = _script()
    for marker in [
        "0–8 segundos",
        "8–18 segundos",
        "18–35 segundos",
        "35–52 segundos",
        "52–66 segundos",
        "66–78 segundos",
        "78–90 segundos",
    ]:
        assert marker in content


def test_demo_video_script_has_honest_limitations():
    content = _script()
    for limitation in [
        "No se debe decir:",
        "Que sincroniza todo automáticamente.",
        "Que sustituye al montador.",
        "Que ya tiene waveform sync.",
        "Que ya tiene transcripción.",
        "Que ya detecta claqueta visual.",
        "Que ya tiene instalador final.",
        "Que ya se integra directamente",
    ]:
        assert limitation in content


def test_demo_video_script_has_cta_and_beta_context():
    content = _script()
    assert "Solicita acceso a la beta privada" in content
    assert "escuelas, productoras y equipos de postproducción" in content
    assert "casos controlados" in content


def test_demo_video_script_has_prepublication_checklist():
    content = _script()
    for item in [
        "El vídeo dice beta privada.",
        "El vídeo dice local-first.",
        "El vídeo dice sin cloud en la versión actual.",
        "El vídeo no promete waveform sync.",
        "El vídeo no pide subir material audiovisual.",
        "El vídeo no muestra datos reales.",
    ]:
        assert item in content


def test_demo_video_script_avoids_positive_forbidden_claims():
    content = _script().lower()
    for claim in FORBIDDEN_POSITIVE_CLAIMS:
        assert claim.lower() not in content


def test_demo_video_script_avoids_runtime_and_backend_references():
    content = _script()
    for pattern in FORBIDDEN_TECH_REFERENCES:
        assert pattern not in content
