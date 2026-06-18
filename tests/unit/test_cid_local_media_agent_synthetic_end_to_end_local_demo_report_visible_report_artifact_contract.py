from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_v1.md"
)

MAPPING_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_qa_gate_v1.md"
)

MAPPING_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md"
)

TEMPLATE_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_contract_declares_phase_and_status():
    text = read(DOC)
    assert "VISIBLE.REPORT.ARTIFACT.CONTRACT.V1" in text
    assert "ARTIFACT_CONTRACT_READY_FOR_VALIDATION" in text
    assert "documentation/test-only" in text


def test_contract_references_upstream_baseline():
    text = read(DOC)
    assert "897f067" in text
    assert "visible-report-template-fixture-mapping-contract-qa-gate-v1-20260618" in text
    for path in [MAPPING_QA, MAPPING_CONTRACT, TEMPLATE_CONTRACT, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_contract_defines_future_artifact_without_creating_it():
    text = read(DOC)
    assert "future visible report artifact" in text
    assert "This phase does not create any visible report artifact." in text
    assert "This phase does not choose a renderer." in text
    assert "This phase does not choose a generator." in text


def test_future_formats_are_declared_but_not_created():
    text = read(DOC)
    for term in ["HTML report", "PDF report", "DOCX report", "Markdown report", "XLSX summary"]:
        assert term in text
    assert "This phase does not create any of those formats." in text


def test_required_visible_disclaimers_are_declared():
    text = read(DOC)
    for term in [
        "Demo sintética",
        "Datos ficticios",
        "No se ha procesado material real",
        "No se ha ejecutado ffprobe ni ffmpeg",
        "No representa sincronización real",
        "No representa transcripción real",
        "No representa traducción real",
        "No representa exportación real a NLE",
        "Revisión humana obligatoria",
    ]:
        assert term in text


def test_artifact_sections_are_declared():
    text = read(DOC)
    for term in [
        "executive summary",
        "local-first privacy notice",
        "synthetic dataset notice",
        "media inventory summary",
        "sync readiness summary",
        "transcription and subtitle readiness summary",
        "editorial assistance summary",
        "technical risk summary",
        "department-facing notes",
        "blocked claims",
        "human review requirements",
        "limitations",
    ]:
        assert term in text


def test_stakeholder_language_is_spanish_first():
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
    ]:
        assert term in text


def test_artifact_safety_rules_block_sensitive_values():
    text = read(DOC)
    for term in [
        "private source-media paths",
        "absolute filesystem paths",
        "usernames",
        "machine names",
        "private client identifiers",
        "credentials",
        "tokens",
        "secrets",
        "raw scanner dumps",
        "raw ffprobe dumps",
        "raw ffmpeg logs",
    ]:
        assert term in text


def test_claims_policy_blocks_false_real_capability_claims():
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
        "created a final edit decision",
        "replaced a DIT",
        "replaced an assistant editor",
        "replaced a sound team",
        "replaced an editor",
        "replaced a producer",
        "replaced a director",
        "uploaded client media",
        "validated final delivery",
        "completed postproduction",
    ]:
        assert term in text


def test_human_review_policy_is_mandatory():
    text = read(DOC)
    for term in [
        "Human review is mandatory",
        "demo status",
        "disclaimers visibility",
        "privacy and redaction safety",
        "sync-readiness interpretation",
        "transcription-readiness interpretation",
        "subtitle-readiness interpretation",
        "editorial interpretation",
        "department-facing interpretation",
    ]:
        assert term in text


def test_blocked_scope_covers_artifacts_runtime_media_and_exports():
    text = read(DOC)
    for term in [
        "visible report artifact",
        "rendered report",
        "HTML report",
        "PDF report",
        "DOCX report",
        "XLSX report",
        "Markdown report artifact",
        "report renderer",
        "report generator",
        "fixture loader",
        "template engine runtime",
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
    assert "VISIBLE.REPORT.ARTIFACT.CONTRACT.QA.GATE.V1" in text
    assert "That phase must remain documentation/test-only." in text


def test_acceptance_criteria_are_complete():
    text = read(DOC)
    for term in [
        "it declares the correct phase",
        "it references upstream commit `897f067`",
        "it references the upstream tag",
        "it defines the future artifact without creating it",
        "it preserves Spanish-first stakeholder readability",
        "it preserves local-first privacy",
        "it preserves synthetic-only demonstration",
        "it preserves mandatory human review",
        "it blocks unsafe real-capability claims",
        "it blocks artifact creation in this phase",
        "it blocks runtime implementation",
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
