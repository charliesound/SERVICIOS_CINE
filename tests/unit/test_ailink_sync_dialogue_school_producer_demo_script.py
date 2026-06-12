from pathlib import Path

DOC = Path("docs/product/ailink_sync_dialogue_school_producer_demo_script_v1.md")


def _text() -> str:
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def test_phase_status_and_report_are_declared():
    text = _text()
    assert "AILINK.PRODUCT.SYNC_DIALOGUE.SCHOOL.PRODUCER.DEMO.SCRIPT.PHASE7.9" in text
    assert "PASS INTERNO VALIDADO CON AJUSTE DE IDIOMA RESUELTO" in text
    assert "report_es.html" in text


def test_safe_claims_are_present():
    text = _text()
    assert "beta controlada" in text
    assert "analiza una carpeta local de rodaje" in text
    assert "No sustituye la revisión humana" in text
    assert "no promete sincronización automática final" in text
    assert "proposes relationships, not final sync" in text


def test_unimplemented_scope_is_blocked():
    text = _text()
    for phrase in [
        "No hay integración cerrada con DaVinci, Avid o Premiere",
        "No hay detección visual de claqueta operativa",
        "No hay matching por waveform operativo",
        "No hay transcripción automática de diálogos operativa",
        "This phase is documentary/test-only.",
        "CID SaaS changes",
        "Public frontend",
        "Docker changes",
        "n8n",
        "CRM",
        "Real database changes",
        "DaVinci/Avid/Premiere integration",
        "Waveform matching",
        "Visual slate detection",
        "Transcription",
        "Installer",
        "Payments",
    ]:
        assert phrase in text
