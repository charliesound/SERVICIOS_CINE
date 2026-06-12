"""Tests for the AILink Sync Dialogue legal web texts spec."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "docs" / "product" / "legal" / "ailink_sync_dialogue_legal_web_texts_spec_v1.md"


REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Legal Web Texts Spec v1",
    "## 4. Datos pendientes para completar legalmente",
    "## 6. Primera capa RGPD para formulario beta",
    "## 7. Checkbox obligatorio — permiso de contacto beta",
    "## 8. Checkbox obligatorio — aceptación de privacidad",
    "## 9. Checkbox opcional — comunicaciones comerciales",
    "## 10. Política de privacidad — estructura mínima",
    "## 12. Aviso legal — estructura mínima",
    "## 14. Cookies — escenario actual sin tracking",
    "## 15. Cookies — escenario futuro con analítica",
    "## 16. Disclaimer de beta/prototipo",
    "## 17. Texto “no subir material audiovisual”",
    "## 20. Checklist antes de publicar landing con formulario",
    "## 21. Non-goals de esta fase",
]

REQUIRED_TERMS = [
    "RGPD",
    "LOPDGDD",
    "LSSI",
    "AEPD",
    "responsable del tratamiento",
    "consentimiento",
    "encargados de tratamiento",
    "plazo de conservación",
    "derechos",
    "cookies técnicas",
    "cookies analíticas",
    "comunicaciones comerciales",
    "PENDIENTE_RELLENAR",
    "No subas ni envíes material audiovisual",
    "Completar el formulario no garantiza acceso inmediato",
]

FORBIDDEN_CLAIMS = [
    "garantizamos cumplimiento legal",
    "cumplimiento legal automático",
    "cumple automáticamente",
    "no necesita revisión legal",
    "texto legal definitivo listo para publicar",
    "puede publicarse sin revisión",
    "usar casillas premarcadas por defecto",
    "acceso inmediato garantizado",
    "sube tu vídeo",
    "sube tu audio",
    "envíanos tu material audiovisual",
]


def _spec() -> str:
    return SPEC.read_text(encoding="utf-8")


def test_legal_web_texts_spec_exists():
    assert SPEC.exists()


def test_legal_web_texts_spec_has_required_headings():
    content = _spec()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_legal_web_texts_spec_has_required_terms():
    content = _spec()
    for term in REQUIRED_TERMS:
        assert term in content


def test_legal_web_texts_spec_has_pending_placeholders():
    content = _spec()
    assert content.count("PENDIENTE_RELLENAR") >= 8


def test_legal_web_texts_spec_states_not_final_legal_advice():
    content = _spec()
    assert "No es asesoría legal definitiva" in content
    assert "revisión posterior por asesoría legal" in content


def test_legal_web_texts_spec_separates_consents():
    content = _spec()
    assert "Checkbox obligatorio — permiso de contacto beta" in content
    assert "Checkbox obligatorio — aceptación de privacidad" in content
    assert "Checkbox opcional — comunicaciones comerciales" in content
    assert "No debe mezclarse con consentimiento comercial" in content


def test_legal_web_texts_spec_covers_no_tracking_and_future_analytics():
    content = _spec()
    assert "escenario actual sin tracking" in content
    assert "escenario futuro con analítica" in content
    assert "aceptar, rechazar o configurar" in content


def test_legal_web_texts_spec_forbids_media_upload():
    content = _spec()
    assert "No pedir subida de vídeo" in content
    assert "No pedir subida de audio" in content
    assert "No subas ni envíes material audiovisual" in content
    assert "La solicitud de beta solo recoge información sobre tu perfil" in content


def test_legal_web_texts_spec_has_prepublication_checklist():
    content = _spec()
    for item in [
        "Completar datos del titular",
        "Revisar si hay cookies reales",
        "Separar consentimiento beta y comunicaciones comerciales",
        "Confirmar que no se piden archivos audiovisuales",
        "Validar textos con asesoría legal antes de publicación",
    ]:
        assert item in content


def test_legal_web_texts_spec_has_no_forbidden_claims():
    content = _spec().lower()
    for claim in FORBIDDEN_CLAIMS:
        assert claim.lower() not in content


def test_legal_web_texts_spec_has_no_runtime_or_backend_references():
    content = _spec()
    forbidden = [
        "DATABASE_URL",
        "TEST_DATABASE_URL",
        "AsyncSessionLocal",
        "FastAPI",
        "APIRouter",
        "CreditLedger",
        "AIJobRepository",
        "/mnt/",
        "\\\\wsl.localhost",
        "C:\\",
    ]
    for pattern in forbidden:
        assert pattern not in content
