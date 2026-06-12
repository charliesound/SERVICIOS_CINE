"""Tests for the AILink Sync Dialogue demo video assembly runbook."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
RUNBOOK = ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_assembly_runbook_v1.md"

REFERENCED_FILES = [
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_script_v1.md",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_subtitles_es_v1.srt",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_voiceover_es_v1.txt",
    ROOT / "docs" / "product" / "video" / "ailink_sync_dialogue_demo_video_subtitles_readme_v1.md",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "hero-report-mockup.png",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "report-summary.png",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "match-suggestions-table.png",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "media-files-table.png",
    ROOT / "docs" / "product" / "assets" / "ailink_sync_dialogue" / "privacy-local-first.png",
]

REQUIRED_HEADINGS = [
    "# AILink Sync Dialogue — Demo Video Assembly Runbook v1",
    "## 1. Objetivo",
    "## 3. Non-goals",
    "## 4. Mensaje central del vídeo",
    "## 5. Claims permitidos",
    "## 6. Claims prohibidos",
    "## 8. Estructura de montaje recomendada",
    "## 9. Capturas recomendadas",
    "## 10. Grabación de pantalla",
    "## 11. Locución",
    "## 12. Subtítulos",
    "## 15. Checklist antes de exportar vídeo real",
    "## 16. Checklist de publicación futura",
    "## 17. Salidas esperadas de una fase futura",
    "## 18. Criterios de aceptación",
]

REQUIRED_TERMS = [
    "No renderiza MP4",
    "No genera audio",
    "No crea nuevos assets visuales",
    "local-first",
    "Sugerencias explicables",
    "Beta privada",
    "report.html",
    "media_files.csv",
    "match_suggestions.csv",
    "scan_result.json",
    "No se debe decir",
    "No se debe prometer waveform sync",
    "No se debe prometer transcripción",
    "No se debe prometer detección de claqueta visual",
    "No se pide subir material audiovisual",
    "No crea vídeo",
    "No toca runtime",
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
    "SUPABASE_SERVICE_ROLE",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "sincroniza todo automáticamente",
    "sustituye al montador",
    "ya integra DaVinci Resolve",
    "ya hace waveform sync",
    "ya transcribe diálogo",
    "ya reconoce claqueta visual",
    "ya es producto final",
    "ya tiene instalador",
    "garantiza resultados perfectos",
]


def _runbook() -> str:
    return RUNBOOK.read_text(encoding="utf-8")


def test_demo_video_assembly_runbook_exists():
    assert RUNBOOK.exists()


def test_demo_video_assembly_runbook_references_existing_inputs():
    for path in REFERENCED_FILES:
        assert path.exists(), path


def test_demo_video_assembly_runbook_has_required_headings():
    content = _runbook()
    for heading in REQUIRED_HEADINGS:
        assert heading in content


def test_demo_video_assembly_runbook_has_required_terms():
    content = _runbook()
    for term in REQUIRED_TERMS:
        assert term in content


def test_demo_video_assembly_runbook_documents_non_goals():
    content = _runbook()
    for text in [
        "Crear MP4",
        "Crear WAV",
        "Crear locución real",
        "Crear capturas nuevas",
        "Crear assets binarios nuevos",
        "Tocar runtime",
        "Tocar backend CID",
        "Tocar frontend",
    ]:
        assert text in content


def test_demo_video_assembly_runbook_documents_allowed_outputs():
    content = _runbook()
    for text in [
        "Genera report.html",
        "Genera media_files.csv",
        "Genera match_suggestions.csv",
        "Genera scan_result.json",
        "score y razones explicables",
    ]:
        assert text in content


def test_demo_video_assembly_runbook_documents_forbidden_claims_as_forbidden():
    content = _runbook()
    assert "## 6. Claims prohibidos" in content
    forbidden_section = content.split("## 6. Claims prohibidos", 1)[1].split("## 7.", 1)[0]
    for claim in FORBIDDEN_POSITIVE_CLAIMS:
        assert claim in forbidden_section


def test_demo_video_assembly_runbook_avoids_runtime_references():
    content = _runbook()
    for pattern in FORBIDDEN_RUNTIME_REFERENCES:
        assert pattern not in content


def test_demo_video_assembly_runbook_has_privacy_and_safety_checklist():
    content = _runbook()
    for text in [
        "no aparece material real de terceros",
        "no aparecen secretos",
        "no se pide subir material audiovisual",
        "subtítulos coinciden con la locución",
        "las salidas mostradas existen en la demo controlada",
    ]:
        assert text in content


def test_demo_video_assembly_runbook_has_publication_checklist():
    content = _runbook()
    for text in [
        "Validar landing de destino",
        "Validar texto legal de la landing",
        "Validar miniatura",
        "Validar copy de LinkedIn",
        "Validar copy de Facebook",
        "no se ofrece acceso inmediato garantizado",
    ]:
        assert text in content


def test_demo_video_assembly_runbook_future_outputs_are_not_current_phase():
    content = _runbook()
    future = content.split("## 17. Salidas esperadas de una fase futura", 1)[1]
    for text in [
        "Vídeo MP4",
        "Audio WAV o MP3 de locución",
        "Archivo de proyecto de montaje",
        "Miniatura",
        "Versión corta vertical",
    ]:
        assert text in future
    assert "Esas salidas no pertenecen a esta fase" in future


def test_demo_video_assembly_runbook_has_no_local_paths_or_windows_paths():
    content = _runbook()
    assert "/mnt/" not in content
    assert "C:\\" not in content
    assert "\\\\wsl.localhost" not in content
