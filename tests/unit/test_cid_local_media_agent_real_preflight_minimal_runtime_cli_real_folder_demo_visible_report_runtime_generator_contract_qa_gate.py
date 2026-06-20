from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_qa_gate_v1.md")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_v1.md")
STATIC_FIXTURE_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_fixture_qa_gate_v1.md")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_exists_and_source_docs_exist() -> None:
    assert DOC.exists()
    assert CONTRACT_DOC.exists()
    assert STATIC_FIXTURE_QA_GATE_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_PASS_READY_FOR_QA_GATE" in text
    assert "e8539e8556d10b482b7e3825b6de35249ac7a921" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-contract-v1-20260620" in text


def test_files_under_qa_are_recorded() -> None:
    text = _text()
    assert "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_v1.md" in text
    assert "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_fixture_qa_gate_v1.md" in text


def test_all_qa_checks_are_defined() -> None:
    text = _text()
    checks = [
        "Check 1 - Runtime generator remains explicitly not implemented",
        "Check 2 - Future inputs are controlled and local-only",
        "Check 3 - Future outputs stay limited to report family",
        "Check 4 - Required visible report sections are complete and ordered",
        "Check 5 - Required identity fields are defined",
        "Check 6 - Scanner fact mapping is complete",
        "Check 7 - Media interpretation avoids over-claiming",
        "Check 8 - Human review and warnings remain visible",
        "Check 9 - Local-only privacy requirements are strict",
        "Check 10 - Current outputs and roadmap outputs remain separated",
        "Check 11 - Determinism is required",
        "Check 12 - Failure behavior is fail-closed",
        "Check 13 - Boundary blocks implementation and product scope creep",
    ]
    for check in checks:
        assert check in text
    assert text.count("### Check ") == 13


def test_runtime_generator_non_implementation_is_gated() -> None:
    text = _text()
    for token in [
        "Runtime generator implemented: false",
        "Runtime generator execution allowed in this phase: false",
        "Runtime visible report output generated in this phase: false",
        "Scanner execution allowed in this phase: false",
        "Real client media allowed in this phase: false",
        "This phase does not implement the runtime generator.",
        "This phase does not execute the scanner.",
        "This phase does not modify scanner code.",
        "This phase does not generate a runtime report.",
        "This phase does not use real client media.",
    ]:
        assert token in text


def test_future_inputs_are_controlled_and_local_only() -> None:
    text = _text()
    for token in [
        "scanner summary data",
        "accepted media candidates",
        "rejected non-media entries",
        "human review flags",
        "warning records",
        "output artifact inventory",
        "local-only privacy evidence",
        "network access",
        "SaaS upload",
        "database writes",
        "real client media outside an explicitly authorized future phase",
        "ffprobe execution unless later authorized",
        "ffmpeg execution unless later authorized",
    ]:
        assert token in text


def test_future_outputs_are_limited_to_report_family() -> None:
    text = _text()
    for token in [
        "`05_reports/`",
        "does not create the `05_reports/` runtime output",
        "Future outputs stay limited to report family",
    ]:
        assert token in text


def test_required_visible_report_sections_are_gated() -> None:
    text = _text()
    sections = [
        "1. `Executive Summary`",
        "2. `Local-Only Privacy Confirmation`",
        "3. `Controlled Demo Input Summary`",
        "4. `Scanner Result Summary`",
        "5. `Accepted Media`",
        "6. `Rejected Non-Media`",
        "7. `Human Review Required`",
        "8. `Warnings`",
        "9. `Created Output Artifacts`",
        "10. `Roadmap Modules Not Yet Generated`",
        "11. `Producer Interpretation`",
        "12. `Next Technical Actions`",
    ]
    positions = [text.index(section) for section in sections]
    assert positions == sorted(positions)


def test_identity_fields_are_gated() -> None:
    text = _text()
    for token in [
        "report title",
        "report audience",
        "report status",
        "privacy mode",
        "scenario identifier",
        "generator mode",
        "runtime generation status",
        "real client media usage status",
        "CID Local Media Agent - Internal Demo Visible Report",
        "producer_product_post_internal_review",
        "internal_demo_only",
        "local_only",
        "approved_synthetic_controlled_demo",
        "real client media used: false",
    ]:
        assert token in text


def test_scanner_fact_mapping_is_gated() -> None:
    text = _text()
    for token in [
        "Scanner status: completed_with_warnings",
        "Candidate media count: 5",
        "Accepted media count: 4",
        "Rejected non-media count: 3",
        "Human review required count: 1",
        "Warnings count: 1",
        "ffprobe preflight: skipped",
        "fail-closed behavior or validation warning when required scanner facts are missing",
    ]:
        assert token in text


def test_media_interpretation_avoids_overclaiming() -> None:
    text = _text()
    for token in [
        "accepted media are scanner candidates only",
        "`.mov = 1`",
        "`.mp4 = 2`",
        "`.wav = 1`",
        "`.exe = 1`",
        "`.txt = 2`",
        "not synchronized clips, transcribed clips, subtitled clips, edited deliverables, or exported timelines",
    ]:
        assert token in text


def test_human_review_and_warnings_are_gated() -> None:
    text = _text()
    for token in [
        "Human review required: true",
        "Human review reason: unknown synthetic placeholder",
        "Warning count: 1",
        "Warning detail: unknown synthetic placeholder",
        "Warning severity: controlled_demo_warning",
        "warnings must not be hidden to make the demo appear cleaner",
    ]:
        assert token in text


def test_local_only_privacy_requirements_are_strict() -> None:
    text = _text()
    for token in [
        "original media left client system: false",
        "SaaS upload performed: false",
        "network call performed: false",
        "database write performed: false",
        "local user names",
        "machine names",
        "absolute system paths",
        "repository paths",
        "real client material",
        "real shoot names",
        "private project titles",
        "private filenames from real shoots",
        "`/mnt/`",
        "Windows drive paths",
        "UNC paths",
        "`DESKTOP-`",
        "`harliesound`",
        "`SERVICIOS_CINE`",
    ]:
        assert token in text


def test_current_outputs_and_roadmap_outputs_remain_separated() -> None:
    text = _text()
    for token in [
        "`00_project/`",
        "`01_media_catalog/`",
        "`99_logs/`",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
        "must not claim current audio synchronization, transcription, subtitles, translation, DaVinci Resolve export, or Avid export",
    ]:
        assert token in text


def test_determinism_is_required() -> None:
    text = _text()
    for token in [
        "deterministic output for the same controlled local scanner input",
        "avoid volatile metadata by default",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths",
        "environment-dependent ordering",
    ]:
        assert token in text


def test_failure_behavior_is_fail_closed() -> None:
    text = _text()
    for token in [
        "fail-closed behavior when data is missing or unsafe",
        "explicit validation error",
        "visible warning section",
        "human review required marker",
        "refusal to generate a client-facing artifact",
    ]:
        assert token in text


def test_boundary_blocks_implementation_and_scope_creep() -> None:
    text = _text()
    for token in [
        "runtime report generator implementation",
        "scanner implementation changes",
        "real media scanning",
        "public demo use",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "SaaS upload",
        "database writes",
        "network calls",
        "Docker or Alembic changes",
        "frontend/backend SaaS changes",
        "Stripe, AI Jobs, credits, or ledger changes",
    ]:
        assert token in text


def test_contract_doc_does_not_authorize_runtime_implementation() -> None:
    text = _text(CONTRACT_DOC)
    assert "This contract does not authorize:" in text
    assert "runtime report generator implementation" in text
    assert "This phase does not implement the runtime generator." in text
    assert "Runtime generator implemented: `false`" in text


def test_acceptance_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "defines the future generator without implementing it",
        "without expanding current product claims",
        "local-only privacy",
        "controlled synthetic demo boundaries",
        "current scanner baseline truthfulness",
        "deterministic report generation requirements",
        "fail-closed behavior",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_QA_GATE_PASS_READY_FOR_IMPLEMENTATION_READINESS",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.V1",
    ]:
        assert token in text
