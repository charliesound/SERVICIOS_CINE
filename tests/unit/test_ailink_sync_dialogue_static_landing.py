"""Tests for the AILink Sync Dialogue exportable static landing."""

import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
LANDING = ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html"
README = ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing_README.md"
ASSET_DIR = ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue"

EXPECTED_ASSETS = {
    "../assets/ailink_sync_dialogue/hero-report-mockup.png",
    "../assets/ailink_sync_dialogue/report-summary.png",
    "../assets/ailink_sync_dialogue/match-suggestions-table.png",
    "../assets/ailink_sync_dialogue/media-files-table.png",
    "../assets/ailink_sync_dialogue/privacy-local-first.png",
    "../assets/ailink_sync_dialogue/linkedin-beta-card.png",
}

REQUIRED_SECTION_IDS = {
    "top",
    "problema",
    "que-hace",
    "como-funciona",
    "outputs",
    "privacidad",
    "para-quien",
    "beta",
    "faq",
    "final",
}

FORBIDDEN_STRINGS = [
    "http://",
    "https://",
    "/mnt/",
    "\\\\wsl.localhost",
    "C:",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "FastAPI",
    "APIRouter",
    "CreditLedger",
    "AIJob",
    "ComfyUI",
    "Docker",
    "Alembic",
    "Stripe",
    "Supabase",
    "cid_test",
    "sqli" + "te",
]

REQUIRED_COPY = [
    "Prepara el material de rodaje para montaje en minutos.",
    "Solicitar acceso beta",
    "El material permanece en el disco del cliente. Sin cloud en la versión actual.",
    "No envía datos y no conecta con CRM.",
    "scan_result.json",
    "media_files.csv",
    "match_suggestions.csv",
    "report.html",
]


class LandingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.img_srcs = []
        self.img_alts = []
        self.hrefs = []
        self.forms = []
        self.scripts = []
        self.iframes = []
        self.meta_viewport = False
        self.title_seen = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "img":
            self.img_srcs.append(attrs.get("src", ""))
            self.img_alts.append(attrs.get("alt", ""))
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))
        if tag == "form":
            self.forms.append(attrs)
        if tag == "script":
            self.scripts.append(attrs)
        if tag == "iframe":
            self.iframes.append(attrs)
        if tag == "meta" and attrs.get("name") == "viewport":
            self.meta_viewport = True
        if tag == "title":
            self.title_seen = True


def _html() -> str:
    return LANDING.read_text(encoding="utf-8")


def _readme() -> str:
    return README.read_text(encoding="utf-8")


def _parser() -> LandingParser:
    parser = LandingParser()
    parser.feed(_html())
    return parser


def test_static_landing_files_exist():
    assert LANDING.exists()
    assert README.exists()


def test_static_landing_has_expected_sections():
    parser = _parser()
    missing = REQUIRED_SECTION_IDS - parser.ids
    assert not missing


def test_static_landing_references_only_expected_assets():
    parser = _parser()
    assert set(parser.img_srcs) == EXPECTED_ASSETS


def test_static_landing_asset_files_exist_on_disk():
    for relative_src in EXPECTED_ASSETS:
        asset_name = Path(relative_src).name
        assert (ASSET_DIR / asset_name).exists(), asset_name


def test_static_landing_images_have_alt_text():
    parser = _parser()
    assert parser.img_alts
    for alt in parser.img_alts:
        assert alt.strip()


def test_static_landing_has_mobile_viewport():
    assert _parser().meta_viewport is True


def test_static_landing_uses_internal_anchor_links_only():
    parser = _parser()
    assert parser.hrefs
    for href in parser.hrefs:
        assert href.startswith("#"), href


def test_static_landing_has_no_real_form_or_submission():
    parser = _parser()
    html = _html().lower()
    assert parser.forms == []
    assert "method=" not in html
    assert "action=" not in html


def test_static_landing_has_no_javascript_or_embeds():
    parser = _parser()
    assert parser.scripts == []
    assert parser.iframes == []


def test_static_landing_has_no_external_urls_or_forbidden_strings():
    combined = "\n".join([_html(), _readme()])
    for pattern in FORBIDDEN_STRINGS:
        assert pattern not in combined, f"Forbidden string found: {pattern}"


def test_static_landing_contains_required_copy():
    html = _html()
    for text in REQUIRED_COPY:
        assert text in html


def test_static_landing_declares_exportable_no_tracking_contract():
    readme = _readme()
    assert "Formulario real" in readme
    assert "Tracking" in readme
    assert "Cloud" in readme
    assert "URLs externas" in readme
    assert "Scripts JavaScript" in readme


def test_static_landing_has_css_embedded_not_linked():
    html = _html()
    assert "<style>" in html
    assert "</style>" in html
    assert "<link" not in html.lower()


def test_static_landing_html_has_basic_document_shape():
    html = _html().strip()
    assert html.startswith("<!doctype html>")
    assert '<html lang="es">' in html
    assert "</html>" in html
    assert '<main id="top">' in html
    assert "</main>" in html


def test_static_landing_does_not_use_absolute_repo_paths():
    combined = "\n".join([_html(), _readme()])
    assert "/opt/SERVICIOS_CINE" not in combined
    assert str(ROOT) not in combined


def test_static_landing_buttons_target_existing_ids():
    parser = _parser()
    ids = parser.ids
    href_ids = {href[1:] for href in parser.hrefs if href.startswith("#") and len(href) > 1}
    assert href_ids <= ids


def test_static_landing_has_no_empty_heading_tags():
    html = _html()
    headings = re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html, flags=re.DOTALL)
    assert headings
    for heading in headings:
        assert re.sub(r"<[^>]+>", "", heading).strip()


def test_static_landing_readme_references_created_html():
    readme = _readme()
    assert "ailink_sync_dialogue_static_landing.html" in readme
    assert "AILink Sync Dialogue" in readme


def test_static_landing_has_accessible_nav_label():
    assert 'aria-label="Navegación principal"' in _html()


def test_static_landing_is_export_pack_not_production_page():
    combined = "\n".join([_html(), _readme()])
    assert "pack estático exportable" in combined.lower()
    assert "no envía datos" in combined.lower()
    assert "no conecta con CRM" in combined
