from pathlib import Path


QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract_v1.md"
)
CONTRACT_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract.py"
)


def _text(path: Path = QA_GATE_DOC) -> str:
    return path.read_text(encoding="utf-8")


def _assert_tokens(text: str, tokens: list[str]) -> None:
    for token in tokens:
        assert token in text


def _assert_ordered(text: str, tokens: list[str]) -> None:
    positions = [text.index(token) for token in tokens]
    assert positions == sorted(positions)


def test_qa_gate_doc_and_source_files_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert CONTRACT_DOC.exists()
    assert CONTRACT_TEST.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    _assert_tokens(_text(), [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_IMPLEMENTATION_CONTRACT_QA_GATE",
        "8fcb79a1289a43809b74392e9783ca34db1090f8",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-implementation-contract-v1-20260620",
    ])


def test_qa_gate_remains_docs_test_only_and_non_runtime() -> None:
    _assert_tokens(_text(), [
        "This phase is docs/test-only.",
        "This phase does not implement the runtime generator.",
        "This phase does not create runtime report artifacts.",
        "This phase does not create scripts, CLI commands, runtime functions, or output artifacts.",
        "This phase does not execute the scanner.",
        "This phase does not use real client media.",
        "This phase does not execute ffprobe or ffmpeg.",
        "This phase does not perform network calls, SaaS upload, or database writes.",
    ])


def test_all_16_qa_checks_are_present_and_ordered() -> None:
    text = _text()
    checks = [
        "## QA Check 1 - Contract Remains Docs/Test Only",
        "## QA Check 2 - Source Traceability Is Complete",
        "## QA Check 3 - Implementation Decision Is Properly Limited",
        "## QA Check 4 - Future Module Contract Is Explicit",
        "## QA Check 5 - Future Implementation Files Are Planned But Not Created",
        "## QA Check 6 - Future Public Interface Is Narrow",
        "## QA Check 7 - Required Future Input Schema Is Complete",
        "## QA Check 8 - Required Scanner Fact Baseline Is Preserved",
        "## QA Check 9 - Required Future Validation Order Is Complete",
        "## QA Check 10 - Future Output Contract Is Local And Limited",
        "## QA Check 11 - Required Future Report Sections Are Preserved",
        "## QA Check 12 - Privacy Contract Is Strict",
        "## QA Check 13 - Determinism Contract Is Strict",
        "## QA Check 14 - Failure Contract Is Fail-Closed",
        "## QA Check 15 - Explicit Non-Goals Block Scope Creep",
        "## QA Check 16 - Acceptance Criteria Are Implementation-Safe",
    ]
    assert text.count("## QA Check ") == 16
    _assert_ordered(text, checks)


def test_implementation_decision_is_limited_to_later_phase() -> None:
    _assert_tokens(_text(), [
        "later implementation phase may create only a minimal runtime generator",
        "local-only",
        "deterministic",
        "fail-closed",
        "warning-visible",
        "truthful about current versus roadmap capabilities",
        "internal-demo-only until separately authorized",
        "must not expand the current Local Media Agent baseline",
        "does not authorize runtime code in this phase",
    ])


def test_future_module_is_pure_rendering_only() -> None:
    _assert_tokens(_text(), [
        "`visible_report_runtime_generator`",
        "pure rendering component",
        "validated controlled scanner result data",
        "producer-readable visible report",
        "scan folders",
        "probe media",
        "synchronize audio",
        "transcribe content",
        "generate subtitles",
        "export timelines",
        "upload data",
        "write to a database",
        "call network services",
    ])


def test_future_runtime_files_are_planned_but_not_created() -> None:
    text = _text()
    _assert_tokens(text, [
        "`scripts/local_media_agent/visible_report_runtime_generator.py`",
        "`tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`",
        "those files are not created in the contract phase",
    ])
    assert not Path("scripts/local_media_agent/visible_report_runtime_generator.py").exists()
    assert not Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py").exists()


def test_future_interface_is_narrow_and_non_executing() -> None:
    _assert_tokens(_text(), [
        "`generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path`",
        "accept already-created controlled scanner result data",
        "validate all required facts before rendering",
        "write one authorized local report artifact only after validation passes",
        "return the created local report path",
        "fail closed before writing output if validation fails",
        "execute scanner code",
        "execute ffprobe",
        "execute ffmpeg",
        "inspect real client media",
        "perform network calls",
        "upload to SaaS",
        "write to any database",
    ])


def test_required_future_input_schema_is_complete() -> None:
    _assert_tokens(_text(), [
        "`report_identity`",
        "`privacy_evidence`",
        "`scanner_summary`",
        "`accepted_media`",
        "`rejected_non_media`",
        "`human_review`",
        "`warnings`",
        "`created_output_artifacts`",
        "`roadmap_modules_not_generated`",
        "Missing required input groups must produce validation error and no report artifact.",
    ])


def test_required_scanner_fact_baseline_is_preserved() -> None:
    _assert_tokens(_text(), [
        "Scanner status: completed_with_warnings",
        "Candidate media count: 5",
        "Accepted media count: 4",
        "Rejected non-media count: 3",
        "Human review required count: 1",
        "Warnings count: 1",
        "ffprobe preflight: skipped",
        "must not infer missing facts",
        "must not hide warnings",
        "must not silently correct inconsistent counts",
    ])


def test_validation_order_is_complete_and_ordered() -> None:
    text = _text()
    steps = [
        "1. input object type",
        "2. required top-level groups",
        "3. report identity values",
        "4. local-only privacy evidence",
        "5. forbidden local-environment markers",
        "6. scanner fact completeness",
        "7. accepted and rejected media count consistency",
        "8. human review and warning visibility",
        "9. current-output versus roadmap-output separation",
        "10. deterministic rendering safety",
        "11. final output path authorization",
    ]
    _assert_ordered(text, steps)
    assert "Any failed validation step must stop rendering and prevent output creation." in text


def test_future_output_contract_is_local_limited_and_report_only() -> None:
    _assert_tokens(_text(), [
        "one visible report artifact under an explicitly authorized local output root",
        "`05_reports/`",
        "`00_project/`",
        "`01_media_catalog/`",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`06_exports/`",
        "database records",
        "SaaS records",
    ])


def test_required_report_sections_are_ordered() -> None:
    _assert_ordered(_text(), [
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
    ])


def test_privacy_determinism_and_failure_contracts_are_strict() -> None:
    _assert_tokens(_text(), [
        "original media left client system: `false`",
        "SaaS upload performed: `false`",
        "network call performed: `false`",
        "database write performed: `false`",
        "`/mnt/`",
        "Windows drive paths",
        "UNC paths",
        "`DESKTOP-`",
        "`harliesound`",
        "`SERVICIOS_CINE`",
        "produce deterministic report content for the same controlled input",
        "avoid volatile metadata by default",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths",
        "environment-dependent ordering",
        "sort deterministically",
        "fail closed when required data is missing, inconsistent, unsafe, or unsupported",
        "explicit validation exception",
        "no output file written",
        "visible warning preservation when rendering is allowed",
        "silent report generation after missing facts",
        "hiding warnings",
        "writing partial client-facing reports",
    ])


def test_explicit_non_goals_block_scope_creep() -> None:
    _assert_tokens(_text(), [
        "implementation in this phase",
        "scanner implementation changes",
        "scanner execution",
        "real media scanning",
        "public demo use",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS upload",
        "database writes",
        "network calls",
        "Docker or Alembic changes",
        "frontend/backend SaaS changes",
        "Stripe, AI Jobs, credits, or ledger changes",
    ])


def test_acceptance_result_and_next_phase_are_recorded() -> None:
    _assert_tokens(_text(), [
        "ready for a later controlled implementation phase without allowing runtime code in this QA gate phase",
        "keep the runtime generator unimplemented",
        "keep the Local Media Agent local-only and private",
        "prevent over-claiming of sync, transcription, subtitles, exports, SaaS integration, or client-facing demo readiness",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_READY_FOR_CONTROLLED_RUNTIME_IMPLEMENTATION",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.V1",
    ])


def test_source_contract_supports_qa_gate_transition() -> None:
    _assert_tokens(_text(CONTRACT_DOC), [
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_IMPLEMENTATION_CONTRACT_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.QA.GATE.V1",
    ])
