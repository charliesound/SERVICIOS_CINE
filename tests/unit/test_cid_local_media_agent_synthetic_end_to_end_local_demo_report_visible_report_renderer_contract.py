from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md"
)

ARTIFACT_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_qa_gate_v1.md"
)

ARTIFACT_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_v1.md"
)

MAPPING_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_contract_declares_phase_and_status():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.CONTRACT.V1" in text
    assert "RENDERER_CONTRACT_READY_FOR_VALIDATION" in text
    assert "documentation/test-only" in text


def test_contract_references_upstream_baseline():
    text = read(DOC)
    assert "ee0d355" in text
    assert "visible-report-artifact-contract-qa-gate-v1-20260618" in text
    for path in [ARTIFACT_QA, ARTIFACT_CONTRACT, MAPPING_CONTRACT, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_contract_defines_future_renderer_without_implementing_it():
    text = read(DOC)
    assert "future minimal visible report renderer" in text
    assert "It does not implement a renderer." in text
    assert "This phase does not create rendering code." in text
    assert "This phase does not create a template engine." in text
    assert "This phase does not create filesystem write behavior." in text


def test_future_renderer_inputs_are_controlled():
    text = read(DOC)
    for term in [
        "validated synthetic report fixture",
        "validated mapping result",
        "visible report template structure",
        "report metadata",
        "demo disclaimer block",
        "human review checklist state",
        "safe rendering options",
    ]:
        assert term in text


def test_future_renderer_cannot_access_real_media_or_network_by_default():
    text = read(DOC)
    for term in [
        "must not read private source-media folders directly",
        "must not scan disks",
        "must not run ffprobe",
        "must not run ffmpeg",
        "must not inspect real media",
        "must not call SaaS services by default",
        "must not perform network calls by default",
    ]:
        assert term in text


def test_future_outputs_are_declared_but_not_created():
    text = read(DOC)
    for term in ["HTML report", "PDF report", "DOCX report", "Markdown report", "XLSX summary"]:
        assert term in text
    assert "This phase does not create any of those outputs." in text


def test_renderer_safety_rules_are_declared():
    text = read(DOC)
    for term in [
        "render only sanitized fields",
        "preserve synthetic demo labeling",
        "preserve local-first privacy notice",
        "preserve no-real-media-processing disclaimer",
        "preserve no-sync-real disclaimer",
        "preserve no-transcription-real disclaimer",
        "preserve no-translation-real disclaimer",
        "preserve no-NLE-export-real disclaimer",
        "preserve mandatory human review block",
        "avoid raw scanner output",
        "avoid raw ffprobe output",
        "avoid raw ffmpeg logs",
        "avoid absolute paths",
        "avoid usernames",
        "avoid machine names",
        "avoid client identifiers",
        "avoid secrets",
        "avoid credentials",
        "avoid tokens",
    ]:
        assert term in text


def test_renderer_claims_policy_blocks_false_capabilities():
    text = read(DOC)
    for term in [
        "analyzed real media",
        "synchronized real audio and video",
        "transcribed real dialogue",
        "translated real subtitles",
        "generated final subtitles",
        "exported to DaVinci Resolve",
        "exported to Avid",
        "exported to Premiere",
        "validated final delivery",
        "completed postproduction",
        "replaced a producer",
        "replaced a director",
        "replaced an editor",
        "replaced an assistant editor",
        "replaced a DIT",
        "replaced a sound team",
        "uploaded client media",
    ]:
        assert term in text


def test_stakeholder_readability_is_spanish_first():
    text = read(DOC)
    for term in [
        "Spanish-first",
        "producción",
        "productor",
        "montaje",
        "ayudante de montaje",
        "DIT",
        "sonido",
        "subtítulos",
        "dirección",
        "postproducción",
        "executive summary",
        "department notes",
        "risks",
        "limitations",
        "next steps",
    ]:
        assert term in text


def test_future_implementation_gate_blocks_unsafe_progression():
    text = read(DOC)
    for term in [
        "Before any renderer implementation",
        "target format",
        "input schema",
        "output path policy",
        "redaction policy",
        "fixture integrity policy",
        "no real media policy",
        "no network default policy",
        "no ffprobe execution policy",
        "no ffmpeg execution policy",
        "no SaaS integration policy",
        "human review policy",
        "manual approval before creating any visible artifact",
    ]:
        assert term in text


def test_blocked_scope_covers_artifacts_runtime_media_and_exports():
    text = read(DOC)
    for term in [
        "renderer code",
        "generator code",
        "loader code",
        "template engine code",
        "report artifact",
        "rendered report",
        "scanner runtime",
        "SaaS runtime",
        "backend",
        "frontend",
        "database",
        "Alembic migration",
        "Docker configuration",
        "ffprobe execution",
        "ffmpeg execution",
        "media probing",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "Premiere export",
        "client media",
        "real media",
        "private media",
        "source media",
    ]:
        assert term in text


def test_next_phase_is_only_documentation_test_qa_gate():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1" in text
    assert "That phase must remain documentation/test-only." in text
    assert "OpenCode should be used as read-only auditor" in text


def test_acceptance_criteria_are_complete():
    text = read(DOC)
    for term in [
        "it declares the correct phase",
        "it references upstream commit `ee0d355`",
        "it defines a future renderer without implementing it",
        "it preserves local-only behavior",
        "it preserves Spanish-first stakeholder readability",
        "it preserves synthetic-only demonstration",
        "it preserves mandatory human review",
        "it preserves CID as assistive and not substitutive",
        "it blocks unsafe real-capability claims",
        "it blocks artifact creation in this phase",
        "it blocks renderer, generator, loader, and runtime implementation",
        "it blocks scanner changes",
        "it blocks SaaS integration",
        "it blocks ffprobe and ffmpeg execution",
        "it blocks real media processing",
    ]:
        assert term in text


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(DOC).lower()
    assert blocked not in read(Path(__file__)).lower()
