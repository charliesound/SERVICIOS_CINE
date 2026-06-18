from pathlib import Path
import json
import re


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md"
)

FIXTURE = Path(
    "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json"
)

TEMPLATE_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md"
)

TEMPLATE_QA_GATE = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md"
)


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def load_fixture():
    assert FIXTURE.exists(), f"Missing expected fixture: {FIXTURE}"
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_mapping_contract_exists_and_declares_phase():
    text = read(DOC)
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.V1"
    ) in text


def test_mapping_contract_references_upstream_inputs():
    text = read(DOC)
    assert str(FIXTURE) in text
    assert str(TEMPLATE_CONTRACT) in text
    assert str(TEMPLATE_QA_GATE) in text
    assert "1c5b441" in text
    assert (
        "cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-"
        "visible-report-template-contract-qa-gate-v1-20260618"
    ) in text


def test_upstream_files_exist():
    assert FIXTURE.exists()
    assert TEMPLATE_CONTRACT.exists()
    assert TEMPLATE_QA_GATE.exists()


def test_fixture_is_valid_json_and_contract_records_structure_snapshot():
    fixture = load_fixture()
    text = read(DOC)
    assert "Fixture Discovery Snapshot" in text
    assert "This snapshot records only fixture structure." in text
    assert "It does not copy real media values" in text

    if isinstance(fixture, dict):
        assert "`object`" in text
        for key, value in fixture.items():
            assert f"`{key}`" in text
            if isinstance(value, dict):
                assert f"- `{key}` — `object`" in text
            elif isinstance(value, list):
                assert f"- `{key}` — `array`" in text
            elif isinstance(value, str):
                assert f"- `{key}` — `string`" in text
            elif isinstance(value, bool):
                assert f"- `{key}` — `boolean`" in text
            elif isinstance(value, int):
                assert f"- `{key}` — `integer`" in text
            elif isinstance(value, float):
                assert f"- `{key}` — `number`" in text
            elif value is None:
                assert f"- `{key}` — `null`" in text
    elif isinstance(fixture, list):
        assert "`array`" in text
    else:
        assert "Fixture Discovery Snapshot" in text


def test_mapping_contract_is_documentation_test_only():
    text = read(DOC).lower()
    assert "documentation/test-only" in text
    assert "it defines a fixture-to-template mapping contract" in text
    assert "it does not execute the mapping" in text
    assert "it does not load the fixture at runtime" in text
    assert "it does not render any visible report" in text


def test_gate_decision_points_only_to_qa_gate_next():
    text = read(DOC)
    assert "MAPPING_CONTRACT_READY_FOR_VALIDATION" in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.QA.GATE.V1"
    ) in text
    assert "That next phase must remain documentation/test-only." in text


def test_mapping_table_has_required_mapping_ids():
    text = read(DOC)
    ids = set(re.findall(r"`(VRM-\d{3})`", text))
    assert len(ids) >= 15
    for expected in [f"VRM-{i:03d}" for i in range(1, 16)]:
        assert expected in ids


def test_mapping_table_covers_template_areas():
    text = read(DOC).lower()
    for term in [
        "report title area",
        "executive summary area",
        "local-first privacy notice area",
        "synthetic dataset notice area",
        "project overview area",
        "media inventory summary area",
        "sync readiness summary area",
        "transcription and subtitle readiness area",
        "editorial assistance summary area",
        "technical risk summary area",
        "department-facing notes area",
        "blocked claims area",
        "human review area",
        "next steps area",
        "limitations area",
    ]:
        assert term in text


def test_selector_policy_blocks_runtime_behaviour():
    text = read(DOC).lower()
    for term in [
        "this phase does not define executable selectors",
        "non-runtime descriptive bindings only",
        "runtime fixture loading",
        "filesystem traversal",
        "media probing",
        "external binary execution",
        "environment-variable access",
        "network access",
        "database access",
        "saas access",
        "secret lookup",
        "client path exposure",
        "raw source-media path exposure",
    ]:
        assert term in text


def test_missing_data_policy_is_visible_and_safe():
    text = read(DOC)
    for term in [
        "Pendiente de completar en datos sintéticos",
        "No disponible en esta demo sintética",
        "No aplicable a este ejemplo sintético",
        "Requiere revisión humana",
        "No representa un análisis técnico real",
        "Fallback copy must not hide missing data.",
        "Fallback copy must not imply that CID performed real processing.",
    ]:
        assert term in text


def test_redaction_policy_blocks_private_or_sensitive_values():
    text = read(DOC).lower()
    for term in [
        "client media names",
        "private source-media names",
        "private source-media paths",
        "absolute local filesystem paths",
        "usernames",
        "machine names",
        "credentials",
        "tokens",
        "secrets",
        "raw scanner dumps",
        "raw ffprobe dumps",
        "raw ffmpeg logs",
        "production-sensitive identifiers",
    ]:
        assert term in text


def test_claims_policy_blocks_real_capability_claims():
    text = read(DOC).lower()
    for term in [
        "analyzed real media",
        "synchronized real audio and video",
        "transcribed real dialogue",
        "translated real subtitles",
        "generated final subtitles",
        "exported to davinci resolve",
        "exported to avid",
        "exported to premiere",
        "created a final edit decision",
        "replaced a dit",
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


def test_spanish_first_stakeholder_language_is_preserved():
    text = read(DOC)
    for term in [
        "Spanish-first",
        "productor",
        "producción",
        "montaje",
        "ayudante de montaje",
        "DIT",
        "sonido",
        "subtítulos",
        "dirección",
        "postproducción",
    ]:
        assert term in text


def test_human_review_policy_is_mandatory():
    text = read(DOC).lower()
    for term in [
        "human review is mandatory",
        "whether the demo is clearly synthetic",
        "whether disclaimers are visible",
        "whether mapped fields are understandable",
        "whether no unsafe capability claim appears",
        "whether no private path or private identifier appears",
        "assistive, not substitutive",
    ]:
        assert term in text


def test_blocked_scope_blocks_artifacts_and_runtime():
    text = read(DOC).lower()
    for term in [
        "visible report artifact",
        "rendered report",
        "html report",
        "pdf report",
        "docx report",
        "xlsx report",
        "csv report",
        "markdown report artifact",
        "report renderer",
        "report generator",
        "fixture loader",
        "template engine runtime",
        "scanner runtime",
        "saas runtime",
        "backend",
        "frontend",
        "database",
        "alembic migration",
        "docker configuration",
        "storage integration",
        "billing integration",
        "installer behavior",
        "licensing behavior",
        "payment behavior",
    ]:
        assert term in text


def test_blocked_scope_blocks_media_processing_and_exports():
    text = read(DOC).lower()
    for term in [
        "ffprobe execution",
        "ffmpeg execution",
        "external binary execution",
        "media probing",
        "video analysis",
        "audio analysis",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "davinci resolve export",
        "avid export",
        "premiere export",
        "otio export",
        "edl export",
        "xml export",
        "fcpxml export",
        "client media",
        "real media",
        "private media",
        "source media",
    ]:
        assert term in text


def test_acceptance_criteria_are_complete():
    text = read(DOC).lower()
    for term in [
        "the existing synthetic fixture exists",
        "the visible report template contract exists",
        "the visible report template qa gate exists",
        "the mapping contract declares the correct phase",
        "the mapping contract references the fixture path",
        "the mapping contract records fixture structure without copying values",
        "the mapping contract defines at least 15 mapping ids",
        "the mapping contract preserves spanish-first stakeholder readability",
        "the mapping contract preserves local-first privacy",
        "the mapping contract preserves synthetic-only demonstration",
        "the mapping contract preserves mandatory human review",
        "the mapping contract blocks unsafe real-capability claims",
        "the mapping contract blocks rendering and runtime implementation",
        "the mapping contract does not modify the fixture",
        "the mapping contract allows only a follow-up documentation/test-only qa gate",
    ]:
        assert term in text


def test_qa_status_requires_validation_before_commit():
    text = read(DOC)
    for term in [
        "MAPPING_CONTRACT_READY_FOR_VALIDATION",
        "staged diff check passes",
        "target test passes",
        "related tests pass",
        "staged scope safety check passes",
        "WSL guard passes",
        "PostgreSQL-only regression guard passes",
    ]:
        assert term in text


def test_contract_does_not_contain_blocked_database_engine_label():
    text = read(DOC).lower()
    blocked = "sqli" + "te"
    assert blocked not in text


def test_unit_test_does_not_contain_blocked_database_engine_label():
    text = read(Path(__file__)).lower()
    blocked = "sqli" + "te"
    assert blocked not in text
