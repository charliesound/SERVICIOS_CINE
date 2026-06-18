from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_status_roadmap_audit_v1.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_audit_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.STATUS.ROADMAP.AUDIT.V1" in text
    assert "CID Local Media Agent — Status Roadmap Audit v1" in text


def test_audit_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not implement runtime behavior",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add subprocess usage",
        "does not scan real media",
        "does not modify scanner runtime",
    ]
    for item in required:
        assert item in text


def test_current_head_and_latest_phase_are_recorded():
    text = read_doc()
    assert "a1db7dc" in text
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1" in text


def test_strengths_are_listed():
    text = read_doc()
    strengths = [
        "local-only product positioning",
        "privacy-by-design constraints",
        "scanner CLI contract design",
        "local output contract design",
        "media project data contract design",
        "ffprobe metadata schema planning",
        "failure path vocabulary",
        "command wrapper contract",
        "test double contract",
        "minimal implementation planning",
    ]
    for item in strengths:
        assert item in text


def test_not_yet_functional_items_are_explicit():
    text = read_doc()
    missing = [
        "real folder scan with full media classification",
        "real ffprobe execution",
        "real technical metadata extraction",
        "real waveform sync",
        "real timecode sync",
        "real slate/clap detection",
        "real transcription",
        "real subtitle generation",
        "real DaVinci Resolve export",
        "real installer",
        "real licensing or activation",
    ]
    for item in missing:
        assert item in text


def test_status_classification_is_clear():
    text = read_doc()
    assert "ARCHITECTURE_AND_SAFETY_FOUNDATION_READY" in text
    assert "FUNCTIONAL_LOCAL_DEMO_READY" in text
    assert "COMMERCIAL_BETA_READY" in text


def test_product_levels_are_declared():
    text = read_doc()
    levels = [
        "Level 1 — Architecture and safety foundation",
        "Level 2 — Synthetic local prototype",
        "Level 3 — Functional local scanner demo",
        "Level 4 — ffprobe real metadata demo",
        "Level 5 — Editing Intelligence demo",
        "Level 6 — Private beta product",
    ]
    for item in levels:
        assert item in text


def test_roadmap_blocks_are_declared():
    text = read_doc()
    blocks = [
        "Block A — Finish synthetic foundation",
        "Block B — Local scanner demo",
        "Block C — Controlled ffprobe metadata",
        "Block D — Editing workflow intelligence",
        "Block E — Speech, subtitles, translation",
        "Block F — Beta packaging",
    ]
    for item in blocks:
        assert item in text


def test_effort_estimate_is_present_without_fixed_calendar_promise():
    text = read_doc()
    assert "FOUNDATION 35-45% OF A LOCAL DEMO" in text
    assert "10-15% OF A COMMERCIAL PRIVATE BETA" in text
    assert "SMALL_TO_MEDIUM" in text
    assert "MEDIUM_TO_HIGH" in text
    assert "HIGH" in text


def test_immediate_next_phase_is_recommended():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.QA.GATE.V1" in text


def test_pivot_to_visible_demo_is_recommended():
    text = read_doc()
    required = [
        "SYNTHETIC END-TO-END LOCAL DEMO REPORT",
        "input folder",
        "detected media-like items",
        "synthetic technical metadata",
        "safe labels",
        "suggested organization",
        "local output report",
        "zero cloud upload",
    ]
    for item in required:
        assert item in text


def test_commercial_message_is_present():
    text = read_doc()
    assert "analiza una carpeta local de material audiovisual sin subir vídeos ni audios a la nube" in text
    assert "radiografía técnica y editorial" in text


def test_final_audit_decision_is_clear():
    text = read_doc()
    assert "CONTINUE_BUT_PIVOT_TOWARD_VISIBLE_SYNTHETIC_DEMO" in text


def test_test_file_does_not_import_external_command_modules():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "o" + "s",
        "from " + "o" + "s",
        "P" + "open(",
        "shell" + "=",
    ]
    for item in forbidden:
        assert item not in source
