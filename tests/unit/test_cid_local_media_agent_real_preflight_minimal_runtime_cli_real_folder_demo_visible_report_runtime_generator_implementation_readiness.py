from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_readiness_v1.md")
CONTRACT_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_qa_gate_v1.md")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_contract_v1.md")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_doc_exists_and_source_docs_exist() -> None:
    assert DOC.exists()
    assert CONTRACT_QA_GATE_DOC.exists()
    assert CONTRACT_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTRACT.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_QA_GATE_PASS_READY_FOR_IMPLEMENTATION_READINESS" in text
    assert "be7ba6f22c9e42d167032b2a589893a874d534fb" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-contract-qa-gate-v1-20260620" in text


def test_readiness_phase_is_docs_only_and_non_runtime() -> None:
    text = _text()
    for token in [
        "This phase is docs/test-only.",
        "This phase does not implement the runtime generator.",
        "This phase does not create a runtime report artifact.",
        "This phase does not execute the scanner.",
        "This phase does not use real client media.",
        "This phase does not execute ffprobe or ffmpeg.",
        "This phase does not perform network calls, SaaS upload, or database writes.",
    ]:
        assert token in text


def test_implementation_readiness_decision_preserves_internal_scope() -> None:
    text = _text()
    for token in [
        "limited to controlled local scanner result data and synthetic demo fixtures",
        "internal technical generator, not as a client-facing product feature",
        "must not expand the current Local Media Agent baseline claims",
    ]:
        assert token in text


def test_proposed_future_module_and_responsibilities_are_defined() -> None:
    text = _text()
    for token in [
        "`visible_report_runtime_generator`",
        "load controlled scanner result data",
        "validate required scanner facts",
        "validate local-only privacy evidence",
        "validate warning and human-review fields",
        "render a deterministic producer-readable visible report",
        "fail closed when required data is missing, ambiguous, or unsafe",
    ]:
        assert token in text


def test_future_entry_point_remains_uncreated() -> None:
    text = _text()
    for token in [
        "Future CLI or callable entry point may be planned only after a later explicit implementation phase.",
        "accept controlled local input data and write only authorized local report artifacts",
        "does not create any script, CLI command, runtime function, or output artifact",
    ]:
        assert token in text


def test_required_future_input_contract_is_defined() -> None:
    text = _text()
    for token in [
        "scanner summary data",
        "accepted media candidates",
        "rejected non-media entries",
        "human review flags",
        "warning records",
        "output artifact inventory",
        "local-only privacy evidence",
        "reject input that is missing required sections, has unsafe path leakage, or claims unsupported capabilities",
    ]:
        assert token in text


def test_required_future_validation_pipeline_is_ordered() -> None:
    text = _text()
    steps = [
        "1. input schema presence",
        "2. local-only privacy evidence",
        "3. scanner fact completeness",
        "4. accepted and rejected media counts",
        "5. warning and human review records",
        "6. current-output versus roadmap-output separation",
        "7. forbidden local-environment markers",
        "8. deterministic rendering safety",
        "9. final client-facing boundary status",
    ]
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)
    assert "fail closed before producing a client-facing artifact" in text


def test_required_future_output_contract_is_defined() -> None:
    text = _text()
    for token in [
        "authorized local output family",
        "The future report family remains roadmap-only in this readiness phase:",
        "`05_reports/`",
        "The future report must preserve these visible sections:",
    ]:
        assert token in text


def test_required_visible_report_sections_are_ordered() -> None:
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


def test_required_future_scanner_fact_baseline_is_defined() -> None:
    text = _text()
    for token in [
        "Scanner status: completed_with_warnings",
        "Candidate media count: 5",
        "Accepted media count: 4",
        "Rejected non-media count: 3",
        "Human review required count: 1",
        "Warnings count: 1",
        "ffprobe preflight: skipped",
        "must not infer missing scanner facts",
        "must not hide warnings",
        "must not convert scanner candidates into synchronized, transcribed, subtitled, edited, or exported deliverables",
    ]:
        assert token in text


def test_required_future_privacy_controls_are_defined() -> None:
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


def test_required_future_determinism_controls_are_defined() -> None:
    text = _text()
    for token in [
        "generate deterministic report content for the same controlled local scanner input",
        "avoid volatile metadata by default",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths",
        "environment-dependent ordering",
    ]:
        assert token in text


def test_explicit_non_goals_block_runtime_and_scope_creep() -> None:
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


def test_acceptance_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "defines how the future implementation must be constrained before any runtime code exists",
        "local-only, deterministic, fail-closed, warning-visible, human-review-visible, and truthful",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.QA.GATE.V1",
    ]:
        assert token in text


def test_source_qa_gate_supports_readiness_transition() -> None:
    text = _text(CONTRACT_QA_GATE_DOC)
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTRACT_QA_GATE_PASS_READY_FOR_IMPLEMENTATION_READINESS" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.V1" in text


def test_source_contract_still_blocks_runtime_implementation() -> None:
    text = _text(CONTRACT_DOC)
    assert "This contract does not authorize:" in text
    assert "runtime report generator implementation" in text
    assert "This phase does not implement the runtime generator." in text
    assert "Runtime generator implemented: `false`" in text
