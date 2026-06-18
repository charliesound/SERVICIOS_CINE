from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_v1.md"
)

READINESS_GATE = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md"
)

RENDERER_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md"
)

RENDERER_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_contract_declares_phase_status_and_upstream_baseline():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.V1" in text
    assert "RENDERER_INPUT_OUTPUT_CONTRACT_READY_FOR_VALIDATION" in text
    assert "3b26916" in text
    assert "visible-report-renderer-implementation-readiness-gate-v1-20260618" in text
    assert "documentation/test-only" in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(DOC)
    for path in [READINESS_GATE, RENDERER_QA, RENDERER_CONTRACT, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_contract_decision_selects_markdown_but_does_not_create_it():
    text = read(DOC)
    assert "INPUT_OUTPUT_CONTRACT_STATUS=READY_FOR_VALIDATION" in text
    assert "controlled Markdown report artifact" in text
    assert "markdown_visible_report_v1" in text
    assert ".md" in text
    assert "This phase does not create that Markdown report artifact." in text
    assert "This phase does not create a renderer." in text
    assert "This phase does not create filesystem write behavior." in text


def test_future_input_schema_sections_are_exact():
    text = read(DOC)
    for term in [
        "report_identity",
        "demo_status",
        "disclaimer_block",
        "source_fixture_reference",
        "project_overview",
        "media_inventory_summary",
        "sync_readiness_summary",
        "transcription_subtitle_readiness_summary",
        "editorial_assistance_summary",
        "technical_risk_summary",
        "department_notes",
        "blocked_claims",
        "human_review_requirements",
        "limitations",
        "next_steps",
        "render_options",
    ]:
        assert term in text


def test_required_input_fields_are_declared():
    text = read(DOC)
    for term in [
        "report_title",
        "report_language",
        "synthetic_demo_label",
        "local_first_privacy_notice",
        "no_real_media_processed_notice",
        "no_ffprobe_executed_notice",
        "no_ffmpeg_executed_notice",
        "no_real_sync_notice",
        "no_real_transcription_notice",
        "no_real_translation_notice",
        "no_real_nle_export_notice",
        "mandatory_human_review_notice",
        "assistive_not_substitutive_notice",
        "generated_from_synthetic_fixture_id",
        "fixture_version",
        "report_sections",
        "review_checklist",
    ]:
        assert term in text


def test_input_must_be_synthetic_sanitized_and_not_raw():
    text = read(DOC)
    for term in [
        "The input must be synthetic.",
        "The input must be sanitized.",
        "The input must be validated before rendering.",
        "must not contain raw scanner dumps",
        "must not contain raw ffprobe dumps",
        "must not contain raw ffmpeg logs",
        "must not contain real source-media paths",
        "must not contain client identifiers",
        "must not contain secrets, credentials, tokens, or private machine data",
    ]:
        assert term in text


def test_render_plan_order_is_locked():
    text = read(DOC)
    for term in [
        "1. title",
        "2. synthetic demo disclaimer",
        "3. executive summary",
        "4. local-first privacy notice",
        "5. project overview",
        "6. media inventory summary",
        "7. sync readiness summary",
        "8. transcription and subtitle readiness summary",
        "9. editorial assistance summary",
        "10. technical risk summary",
        "11. department notes",
        "12. blocked claims",
        "13. limitations",
        "14. human review checklist",
        "15. next steps",
    ]:
        assert term in text
    assert "The renderer must not infer real technical results." in text
    assert "The renderer must not hide disclaimers." in text


def test_output_path_policy_blocks_unsafe_targets():
    text = read(DOC)
    for term in [
        "explicit controlled output directory",
        "output path must be deterministic",
        "source media folders",
        "private workspace folders",
        "user home root",
        "system directories",
        "repository root",
        "backend directories",
        "frontend directories",
        "database directories",
        "Alembic directories",
        "Docker directories",
        "fixture directories",
        "scanner source directories",
        "safe temporary directory in automated tests",
    ]:
        assert term in text


def test_artifact_naming_policy_avoids_real_identifiers():
    text = read(DOC)
    for term in [
        "cid_local_media_agent_synthetic_visible_report_v1.md",
        "client names",
        "production names",
        "real project titles",
        "usernames",
        "machine names",
        "source folder names",
        "media filenames",
        "dates that imply real delivery",
        "final delivery labels",
    ]:
        assert term in text


def test_redaction_policy_blocks_sensitive_values():
    text = read(DOC)
    for term in [
        "absolute paths",
        "private source paths",
        "usernames",
        "machine names",
        "client identifiers",
        "production-sensitive identifiers",
        "media filenames if not synthetic",
        "credentials",
        "tokens",
        "secrets",
        "raw scanner dumps",
        "raw ffprobe dumps",
        "raw ffmpeg logs",
    ]:
        assert term in text


def test_safe_overwrite_policy_is_default_false():
    text = read(DOC)
    assert "The default future behavior must be no overwrite." in text
    assert "fail safely" in text
    assert "safe overwrite option is provided" in text
    assert "safe overwrite option must be false by default" in text


def test_render_options_are_allowlisted_and_blocklisted():
    text = read(DOC)
    for term in [
        "output_dir",
        "output_filename",
        "language",
        "include_department_notes",
        "include_human_review_checklist",
        "include_limitations",
        "safe_overwrite",
        "scan_source_media",
        "run_ffprobe",
        "run_ffmpeg",
        "call_saaS",
        "upload_media",
        "inspect_real_media",
        "generate_final_subtitles",
        "export_nle",
        "hide_disclaimers",
        "mark_as_final_delivery",
    ]:
        assert term in text


def test_claims_policy_blocks_false_real_capabilities():
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


def test_human_review_policy_is_visible_and_not_final():
    text = read(DOC)
    for term in [
        "visible human review checklist",
        "report is synthetic",
        "not a final technical diagnosis",
        "not a final postproduction report",
        "real client use requires human verification",
    ]:
        assert term in text


def test_blocked_scope_covers_artifacts_runtime_media_and_exports():
    text = read(DOC)
    for term in [
        "renderer code",
        "generator code",
        "loader code",
        "template engine code",
        "runtime code",
        "report artifact",
        "rendered report",
        "Markdown report artifact",
        "HTML report",
        "PDF report",
        "DOCX report",
        "XLSX report",
        "CSV report",
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


def test_next_phase_is_qa_gate_only():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.QA.GATE.V1" in text
    assert "That phase must remain documentation/test-only." in text
    assert "OpenCode should be used as read-only auditor" in text


def test_acceptance_criteria_are_complete():
    text = read(DOC)
    for term in [
        "it declares the correct phase",
        "it references upstream commit `3b26916`",
        "it chooses Markdown as the first future controlled output format",
        "it defines exact future input sections",
        "it defines required input fields",
        "it defines render order",
        "it defines output path policy",
        "it defines artifact naming policy",
        "it defines redaction policy",
        "it defines safe overwrite policy",
        "it defines allowed render options",
        "it defines blocked render options",
        "it preserves local-only behavior",
        "it preserves synthetic-only demonstration",
        "it preserves Spanish-first stakeholder readability",
        "it preserves mandatory human review",
        "it blocks unsafe real-capability claims",
        "it blocks artifact creation in this phase",
        "it blocks renderer implementation in this phase",
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
