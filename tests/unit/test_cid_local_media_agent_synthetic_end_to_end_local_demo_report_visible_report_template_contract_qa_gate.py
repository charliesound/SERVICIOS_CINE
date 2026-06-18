from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md"
)

UPSTREAM_TEMPLATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md"
)

UPSTREAM_TEMPLATE_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract.py"
)


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists_and_declares_phase():
    text = read(QA_DOC)
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.CONTRACT.QA.GATE.V1"
    ) in text


def test_qa_gate_references_upstream_template_contract_phase():
    text = read(QA_DOC)
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.CONTRACT.V1"
    ) in text
    assert str(UPSTREAM_TEMPLATE_DOC) in text
    assert str(UPSTREAM_TEMPLATE_TEST) in text


def test_qa_gate_records_upstream_commit_and_tag():
    text = read(QA_DOC)
    assert "ea0ea55" in text
    assert (
        "cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-"
        "visible-report-template-contract-v1-20260618"
    ) in text


def test_qa_gate_is_documentation_test_only():
    text = read(QA_DOC).lower()
    assert "documentation/test-only" in text
    assert "does not create a visible report" in text
    assert "does not create html" in text
    assert "does not create" in text
    assert "renderer" in text
    assert "generator" in text
    assert "loader" in text


def test_qa_gate_decision_allows_only_mapping_contract_next():
    text = read(QA_DOC)
    assert "PASS_WITH_CONDITIONS_TO_VISIBLE_REPORT_TEMPLATE_FIXTURE_MAPPING_CONTRACT" in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.V1"
    ) in text


def test_allowed_scope_contains_only_expected_files():
    text = read(QA_DOC)
    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md"
    ) in text
    assert (
        "tests/unit/"
        "test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate.py"
    ) in text


def test_blocked_scope_blocks_report_artifacts():
    text = read(QA_DOC).lower()
    for term in [
        "visible report artifact",
        "rendered report",
        "html report",
        "pdf report",
        "docx report",
        "xlsx report",
        "csv report",
        "markdown report artifact",
    ]:
        assert term in text


def test_blocked_scope_blocks_runtime_and_saas_changes():
    text = read(QA_DOC).lower()
    for term in [
        "report renderer",
        "report generator",
        "fixture loader",
        "template engine runtime",
        "scanner runtime change",
        "saas runtime change",
        "backend change",
        "frontend change",
        "database change",
        "alembic migration",
        "docker change",
        "storage change",
    ]:
        assert term in text


def test_blocked_scope_blocks_ffprobe_ffmpeg_and_media_processing():
    text = read(QA_DOC).lower()
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
    ]:
        assert term in text


def test_blocked_scope_blocks_nle_exports():
    text = read(QA_DOC).lower()
    for term in [
        "davinci resolve export",
        "avid export",
        "premiere export",
        "otio export",
        "edl export",
        "xml export",
        "fcpxml export",
    ]:
        assert term in text


def test_blocked_scope_blocks_private_or_real_media():
    text = read(QA_DOC).lower()
    for term in [
        "client media",
        "real media",
        "private media",
        "source media",
        "client paths",
        "raw ffprobe output",
        "raw scanner output",
        "secrets",
        "credentials",
    ]:
        assert term in text


def test_product_constraints_are_preserved():
    text = read(QA_DOC)
    for term in [
        "Spanish-first",
        "production stakeholders",
        "productor",
        "montaje",
        "ayudante de montaje",
        "DIT",
        "sonido",
        "subtítulos",
        "producción",
        "synthetic data only",
        "local-first",
        "human review mandatory",
    ]:
        assert term in text


def test_required_visible_disclaimers_are_present():
    text = read(QA_DOC)
    for term in [
        "Demo sintética",
        "Datos ficticios",
        "No se ha procesado material real",
        "No se ha ejecutado ffprobe ni ffmpeg",
        "No representa un análisis técnico final",
        "No representa sincronización real",
        "No representa transcripción real",
        "No representa traducción real",
        "No representa exportación real a NLE",
        "Revisión humana obligatoria",
    ]:
        assert term in text


def test_required_template_areas_are_declared():
    text = read(QA_DOC).lower()
    for term in [
        "report title area",
        "executive summary area",
        "local-first privacy notice area",
        "synthetic dataset notice area",
        "project overview area",
        "media inventory summary area",
        "sync readiness summary area",
        "transcription/subtitle readiness summary area",
        "editorial assistance summary area",
        "technical risk summary area",
        "department-facing notes area",
        "blocked claims area",
        "human review area",
        "next steps area",
        "limitations area",
    ]:
        assert term in text


def test_data_binding_rules_prevent_real_or_sensitive_values():
    text = read(QA_DOC).lower()
    for term in [
        "separate template structure from fixture values",
        "must not hard-code real media names",
        "client names",
        "project names",
        "personal names",
        "filesystem paths",
        "source-media paths",
        "secrets",
        "credentials",
        "does not modify that fixture",
    ]:
        assert term in text


def test_existing_synthetic_fixture_is_referenced_but_not_modified():
    text = read(QA_DOC)
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "This phase does not modify that fixture." in text


def test_claim_safety_rules_block_real_capability_claims():
    text = read(QA_DOC)
    forbidden_claims = [
        "CID has analyzed real media.",
        "CID has synchronized real audio and video.",
        "CID has transcribed real dialogue.",
        "CID has translated real subtitles.",
        "CID has generated final subtitles.",
        "CID has exported to DaVinci Resolve.",
        "CID has exported to Avid.",
        "CID has exported to Premiere.",
        "CID has produced final editorial decisions.",
        "CID has processed client footage.",
        "CID has uploaded client footage.",
        "CID has validated final delivery.",
    ]
    for claim in forbidden_claims:
        assert claim in text


def test_local_first_privacy_rules_are_explicit():
    text = read(QA_DOC).lower()
    for term in [
        "source media remains on the client's controlled machine",
        "no upload by default",
        "no saas dependency for local operation",
        "only authorized metadata or reports may be shared",
        "no raw client media paths",
        "no raw technical dumps",
        "no private source media names",
    ]:
        assert term in text


def test_human_review_rules_cover_core_departments_and_decisions():
    text = read(QA_DOC).lower()
    for term in [
        "human review remains mandatory",
        "synchronization quality",
        "transcription quality",
        "subtitle quality",
        "editorial use",
        "delivery decisions",
        "production decisions",
        "client-facing interpretation",
        "publication",
    ]:
        assert term in text


def test_acceptance_criteria_cover_safety_and_scope():
    text = read(QA_DOC).lower()
    for term in [
        "the upstream template contract exists",
        "the upstream template contract declares its phase identifier",
        "the upstream template contract remains documentation/test-only",
        "this qa gate blocks artifact creation",
        "this qa gate blocks runtime implementation",
        "this qa gate blocks media processing",
        "this qa gate blocks ffprobe and ffmpeg execution",
        "this qa gate blocks saas integration",
        "this qa gate preserves spanish-first stakeholder readability",
        "this qa gate preserves local-first privacy",
        "this qa gate preserves synthetic-only demonstration",
        "this qa gate preserves mandatory human review",
        "this qa gate blocks unsafe claims",
    ]:
        assert term in text


def test_explicit_non_goals_are_comprehensive():
    text = read(QA_DOC).lower()
    for term in [
        "implement report rendering",
        "implement template loading",
        "implement fixture loading",
        "implement fixture-to-template mapping",
        "implement report generation",
        "create a report artifact",
        "create a stakeholder pdf",
        "create a stakeholder html file",
        "create a stakeholder docx file",
        "create a stakeholder xlsx file",
        "create a stakeholder markdown file",
        "modify scanner code",
        "execute ffprobe",
        "execute ffmpeg",
        "inspect media files",
        "process media files",
        "create subtitles",
        "translate subtitles",
        "export to an nle",
        "integrate with cid saas",
        "touch billing",
        "touch licensing",
        "touch installers",
    ]:
        assert term in text


def test_qa_status_requires_full_validation_before_commit():
    text = read(QA_DOC)
    for term in [
        "QA_GATE_READY_FOR_VALIDATION",
        "staged diff check passes",
        "target test passes",
        "related tests pass",
        "staged scope safety check passes",
        "WSL guard passes",
        "PostgreSQL-only regression guard passes",
    ]:
        assert term in text


def test_upstream_template_contract_file_exists_and_declares_phase():
    text = read(UPSTREAM_TEMPLATE_DOC)
    assert (
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT."
        "VISIBLE.REPORT.TEMPLATE.CONTRACT.V1"
    ) in text


def test_upstream_template_contract_remains_documentation_test_only():
    text = read(UPSTREAM_TEMPLATE_DOC).lower()
    assert "documentation/test-only" in text
    assert "template contract" in text


def test_upstream_template_test_file_exists():
    text = read(UPSTREAM_TEMPLATE_TEST)
    assert "visible_report_template_contract" in text
