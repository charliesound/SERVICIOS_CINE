"""Tests for the AILink Sync Dialogue social launch pack."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
PACK = ROOT / "docs" / "product" / "social" / "ailink_sync_dialogue_social_launch_pack_v1.md"
ASSET_DIR = ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue"

EXPECTED_ASSETS = {
    "linkedin-beta-card.png",
    "hero-report-mockup.png",
    "report-summary.png",
    "match-suggestions-table.png",
    "media-files-table.png",
    "privacy-local-first.png",
}

REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Social Launch Pack v1",
    "## 6. Post LinkedIn 1 — Teaser corto",
    "## 7. Post LinkedIn 2 — Problema / solución",
    "## 8. Post LinkedIn 3 — Beta privada",
    "## 9. Post LinkedIn 4 — Privacidad",
    "## 10. Post Facebook — Versión cercana",
    "## 12. Carrusel LinkedIn — 8 slides",
    "## 13. Guion de vídeo demo — 60 a 90 segundos",
    "## 18. Checklist antes de publicar",
]

REQUIRED_COPY = [
    "Prepara el material de rodaje para montaje en minutos.",
    "No sustituye al montador.",
    "No promete sincronizarlo todo automáticamente.",
    "El material permanece en el disco del cliente.",
    "Sin cloud en la versión actual.",
    "beta privada",
    "casos controlados",
    "report.html",
    "media_files.csv",
    "match_suggestions.csv",
    "scan_result.json",
]

FORBIDDEN_COPY = [
    "sincroniza automáticamente todo",
    "ya es un producto final",
    "es un producto final cerrado",
    "reemplaza al montador",
    "reemplaza al ayudante",
    "automatiza el trabajo del montador",
    "automatiza todo el montaje",
    "sube tu material",
    "envíanos tu vídeo",
    "garantiza acceso inmediato",
    "waveform sync disponible",
    "transcripción disponible",
    "claqueta visual disponible",
    "instalador disponible",
    "http://",
    "https://",
    "/mnt/",
    "\\\\wsl.localhost",
]


def _pack() -> str:
    return PACK.read_text(encoding="utf-8")


def test_social_launch_pack_exists():
    assert PACK.exists()


def test_social_launch_pack_has_required_headings():
    content = _pack()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_social_launch_pack_references_expected_assets():
    content = _pack()
    for asset in EXPECTED_ASSETS:
        assert asset in content


def test_social_launch_pack_asset_files_exist():
    for asset in EXPECTED_ASSETS:
        assert (ASSET_DIR / asset).exists(), asset


def test_social_launch_pack_contains_required_copy():
    content = _pack()
    for text in REQUIRED_COPY:
        assert text in content


def test_social_launch_pack_avoids_forbidden_copy():
    content = _pack().lower()
    for text in FORBIDDEN_COPY:
        assert text.lower() not in content


def test_social_launch_pack_contains_four_linkedin_posts():
    content = _pack()
    assert content.count("Post LinkedIn") >= 4


def test_social_launch_pack_contains_facebook_post():
    assert "Post Facebook" in _pack()


def test_social_launch_pack_contains_eight_carousel_slides():
    content = _pack()
    for idx in range(1, 9):
        assert f"### Slide {idx}" in content


def test_social_launch_pack_contains_demo_script_timing():
    content = _pack()
    for marker in [
        "0–10 segundos",
        "10–25 segundos",
        "25–45 segundos",
        "45–65 segundos",
        "65–80 segundos",
        "80–90 segundos",
    ]:
        assert marker in content


def test_social_launch_pack_has_private_beta_message():
    content = _pack().lower()
    assert "beta privada" in content
    assert "limitada" in content
    assert "feedback" in content


def test_social_launch_pack_does_not_request_media_upload():
    content = _pack().lower()
    assert "no pedimos que subas vídeo ni audio" in content
    assert "no pedimos que envíes material audiovisual" in content
