"""Tests for the AILink Sync Dialogue landing legal integration spec."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_landing_legal_integration_spec_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing.html",
    ROOT / "docs" / "product" / "landing" / "ailink_sync_dialogue_static_landing_README.md",
    ROOT / "docs" / "product" / "ailink_sync_dialogue_beta_form_spec_v1.md",
    ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_legal_web_texts_spec_v1.md",
    ROOT / "docs" / "product" / "social" / "ailink_sync_dialogue_social_launch_pack_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_subtitles_readme_v1.md",
]

REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Landing Legal Integration Spec v1",
    "## 5. Principio de integración legal",
    "## 6. Ubicación recomendada del formulario",
    "## 10. Primera capa RGPD en la landing",
    "## 11. Checkboxes obligatorios",
    "## 12. Checkbox opcional de comunicaciones comerciales",
    "## 14. Cookies y tracking",
    "## 17. Datos que deben registrarse en implementación futura",
    "## 18. Datos que no deben pedirse",
    "## 19. Integración futura con Supabase o CRM",
    "## 20. Relación con CID",
    "## 22. Checklist antes de activar formulario real",
    "## 23. Tests recomendados para implementación futura",
    "## 24. Criterios de aceptación",
]

REQUIRED_TERMS = [
    "beta-form",
    "primera capa RGPD",
    "PENDIENTE_RELLENAR",
    "Aviso legal",
    "Política de privacidad",
    "Política de cookies",
    "No subas ni envíes material audiovisual",
    "No premarcado",
    "comunicaciones comerciales",
    "Supabase",
    "CRM",
    "no se mezclan con la base core de CID",
    "No decir que AILink Sync Dialogue es CID",
    "No usar “CID” como nombre de la herramienta independiente",
]

FORBIDDEN_RUNTIME_REFERENCES = [
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "AsyncSessionLocal",
    "FastAPI",
    "APIRouter",
    "CreditLedger",
    "AIJobRepository",
    "STRIPE_SECRET",
]

FORBIDDEN_COMMITMENT_CLAIMS = [
    "cumplimiento legal garantizado",
    "puede publicarse sin revisión",
    "no necesita asesoría legal",
    "usar casillas premarcadas por defecto",
    "enviar material audiovisual obligatorio",
    "teléfono obligatorio como requisito",
    "DNI obligatorio como requisito",
]


def _spec() -> str:
    return SPEC.read_text(encoding="utf-8")


def test_landing_legal_integration_spec_exists():
    assert SPEC.exists()


def test_landing_legal_integration_spec_references_existing_files():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_landing_legal_integration_spec_has_required_headings():
    content = _spec()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_landing_legal_integration_spec_has_required_terms():
    content = _spec()
    for term in REQUIRED_TERMS:
        assert term in content


def test_landing_legal_integration_spec_has_pending_placeholders():
    content = _spec()
    assert content.count("PENDIENTE_RELLENAR") >= 2


def test_landing_legal_integration_spec_separates_consents():
    content = _spec()
    assert "Permiso de contacto beta" in content
    assert "Aceptación de política de privacidad" in content
    assert "Checkbox opcional de comunicaciones comerciales" in content
    assert "No deben mezclarse consentimientos distintos en una sola casilla" in content


def test_landing_legal_integration_spec_defines_cookie_modes():
    content = _spec()
    assert "Escenario sin tracking" in content
    assert "Escenario con analítica futura" in content
    assert "aceptar" in content
    assert "rechazar" in content
    assert "configurar" in content


def test_landing_legal_integration_spec_forbids_sensitive_media_collection():
    content = _spec()
    for text in [
        "Subida de vídeo",
        "Subida de audio",
        "Enlaces a material audiovisual sensible",
        "Datos bancarios",
        "Tarjeta",
        "Contraseña",
        "Acceso a discos del usuario",
    ]:
        assert text in content


def test_landing_legal_integration_spec_keeps_ailink_and_cid_separate():
    content = _spec()
    assert "AILink Sync Dialogue es una herramienta independiente" in content
    assert "No decir que AILink Sync Dialogue es CID" in content
    assert "No debe requerirse cuenta CID" in content


def test_landing_legal_integration_spec_has_future_implementation_tests():
    content = _spec()
    for text in [
        "Existe id beta-form",
        "Los checkboxes obligatorios no están premarcados",
        "El checkbox comercial es opcional",
        "El envío falla sin privacidad",
        "El envío falla sin contacto beta",
        "No hay secretos en frontend",
    ]:
        assert text in content


def test_landing_legal_integration_spec_avoids_runtime_references():
    content = _spec()
    for pattern in FORBIDDEN_RUNTIME_REFERENCES:
        assert pattern not in content


def test_landing_legal_integration_spec_avoids_unsafe_commitment_claims():
    content = _spec().lower()
    for claim in FORBIDDEN_COMMITMENT_CLAIMS:
        assert claim.lower() not in content


def test_landing_legal_integration_spec_has_no_local_paths_or_windows_paths():
    content = _spec()
    assert "/mnt/" not in content
    assert "C:\\" not in content
    assert "\\\\wsl.localhost" not in content
