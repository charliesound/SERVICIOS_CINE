from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_v1.md")
STATIC_FIXTURE_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_fixture_qa_gate_v1.md")
STATIC_FIXTURE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_fixture_v1.md")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_doc_exists_and_source_docs_exist() -> None:
    assert DOC.exists()
    assert STATIC_FIXTURE_QA_GATE_DOC.exists()
    assert STATIC_FIXTURE_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.FIXTURE.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_STATIC_FIXTURE_QA_GATE_PASS_READY_FOR_RUNTIME_REPORT_GENERATOR_CONTRACT" in text
    assert "33e0ace78cd78c61cd14884c6b549a6ed47a8b6e" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-static-fixture-qa-gate-v1-20260620" in text


def test_runtime_generator_is_explicitly_not_implemented_or_executed() -> None:
    text = _text()
    for token in [
        "Runtime generator implemented: `false`",
        "Runtime generator execution allowed in this phase: `false`",
        "Runtime visible report output generated in this phase: `false`",
        "Scanner execution allowed in this phase: `false`",
        "Real client media allowed in this phase: `false`",
        "This phase does not implement the runtime generator.",
        "This phase does not execute the scanner.",
        "This phase does not modify scanner code.",
        "This phase does not generate a runtime report.",
        "This phase does not use real client media.",
    ]:
        assert token in text


def test_generator_purpose_is_producer_readable_and_truthful() -> None:
    text = _text()
    for token in [
        "transform controlled local scanner result data into a producer-readable visible report",
        "truthful about the current Local Media Agent baseline",
        "what the scanner did, what it rejected, what requires human review, what warnings exist",
        "what modules are still roadmap-only",
        "must not present future modules as current capabilities",
    ]:
        assert token in text


def test_expected_future_inputs_are_defined_without_runtime_authorization() -> None:
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
        "ffprobe execution unless a later explicit phase authorizes it",
        "ffmpeg execution unless a later explicit phase authorizes it",
    ]:
        assert token in text


def test_expected_future_outputs_are_limited_to_report_family_contract() -> None:
    text = _text()
    for token in [
        "`05_reports/`",
        "primary future artifact should be a human-readable internal report",
        "preserve the same visible report structure used by the static fixture",
        "This contract does not create the `05_reports/` runtime output.",
    ]:
        assert token in text


def test_required_visible_report_sections_are_recorded_in_order() -> None:
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


def test_required_report_identity_fields_are_defined() -> None:
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
        "`runtime_generated` only after a later implementation phase exists",
        "`real client media used: false`",
    ]:
        assert token in text


def test_required_scanner_fact_mapping_is_defined() -> None:
    text = _text()
    for token in [
        "Scanner status: completed_with_warnings",
        "Candidate media count: 5",
        "Accepted media count: 4",
        "Rejected non-media count: 3",
        "Human review required count: 1",
        "Warnings count: 1",
        "ffprobe preflight: skipped",
        "fail closed or surface a validation warning if required scanner facts are missing",
    ]:
        assert token in text


def test_required_media_interpretation_is_defined_without_overclaiming() -> None:
    text = _text()
    for token in [
        "Accepted media must be represented as scanner candidates only.",
        "`.mov = 1`",
        "`.mp4 = 2`",
        "`.wav = 1`",
        "`.exe = 1`",
        "`.txt = 2`",
        "not synchronized clips, transcribed clips, subtitled clips, edited deliverables, or exported timelines",
    ]:
        assert token in text


def test_human_review_and_warning_requirements_are_defined() -> None:
    text = _text()
    for token in [
        "keep human review visible when ambiguity exists",
        "Human review required: true",
        "Human review reason: unknown synthetic placeholder",
        "Warning count: 1",
        "Warning detail: unknown synthetic placeholder",
        "Warning severity: controlled_demo_warning",
        "Warnings must not be hidden to make the demo appear cleaner.",
    ]:
        assert token in text


def test_local_only_privacy_requirements_are_defined() -> None:
    text = _text()
    for token in [
        "original media left client system: `false`",
        "SaaS upload performed: `false`",
        "network call performed: `false`",
        "database write performed: `false`",
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


def test_current_outputs_and_roadmap_outputs_are_defined() -> None:
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
        "must not claim that the current baseline creates audio synchronization outputs, transcription outputs, subtitle outputs, translation outputs, DaVinci Resolve exports, or Avid exports.",
    ]:
        assert token in text


def test_determinism_requirement_is_defined() -> None:
    text = _text()
    for token in [
        "Given the same controlled local scanner input",
        "produce the same visible report content",
        "Approved volatile metadata must be avoided",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths",
        "environment-dependent ordering",
    ]:
        assert token in text


def test_failure_behavior_is_fail_closed() -> None:
    text = _text()
    for token in [
        "fail closed when required data is missing or unsafe",
        "must not silently create a polished report",
        "scanner facts, warning records, or privacy evidence are incomplete",
        "explicit validation error",
        "visible warning section",
        "human review required marker",
        "refusal to generate a client-facing artifact",
    ]:
        assert token in text


def test_contract_boundary_blocks_runtime_and_product_scope() -> None:
    text = _text()
    for token in [
        "This contract does not authorize:",
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


def test_acceptance_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "local-only privacy",
        "controlled synthetic demo boundaries",
        "current scanner baseline truthfulness",
        "producer-readable report structure",
        "clear distinction between current outputs and roadmap modules",
        "fail-closed behavior for missing or unsafe data",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_PASS_READY_FOR_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.QA.GATE.V1",
    ]:
        assert token in text
