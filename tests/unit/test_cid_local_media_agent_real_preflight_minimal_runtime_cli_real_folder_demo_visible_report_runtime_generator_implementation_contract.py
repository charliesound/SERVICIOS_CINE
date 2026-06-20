from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_contract_v1.md")
READINESS_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_readiness_qa_gate_v1.md")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_implementation_readiness_v1.md")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_implementation_contract_doc_exists_and_source_docs_exist() -> None:
    assert DOC.exists()
    assert READINESS_QA_GATE_DOC.exists()
    assert READINESS_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.READINESS.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT" in text
    assert "8d4f954c4572f326f664d4bbf4f7dfe986708cac" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-implementation-readiness-qa-gate-v1-20260620" in text


def test_contract_phase_is_docs_only_and_non_runtime() -> None:
    text = _text()
    for token in [
        "This phase is docs/test-only.",
        "This phase does not implement the runtime generator.",
        "This phase does not create runtime report artifacts.",
        "This phase does not create scripts, CLI commands, runtime functions, or output artifacts.",
        "This phase does not execute the scanner.",
        "This phase does not use real client media.",
        "This phase does not execute ffprobe or ffmpeg.",
        "This phase does not perform network calls, SaaS upload, or database writes.",
    ]:
        assert token in text


def test_implementation_contract_decision_is_safe() -> None:
    text = _text()
    for token in [
        "minimal runtime generator only if it remains local-only, deterministic, fail-closed, warning-visible, and truthful",
        "internal-demo-only until a separate future phase explicitly authorizes client-facing use",
        "must not expand the current Local Media Agent baseline",
    ]:
        assert token in text


def test_future_module_contract_is_defined_without_scope_creep() -> None:
    text = _text()
    for token in [
        "`visible_report_runtime_generator`",
        "pure rendering component that transforms validated controlled scanner result data into a producer-readable visible report",
        "must not scan folders, probe media, synchronize audio, transcribe content, generate subtitles, export timelines, upload data, write to a database, or call network services",
    ]:
        assert token in text


def test_allowed_future_implementation_files_are_documented_but_not_created() -> None:
    text = _text()
    for token in [
        "A later explicit implementation phase may introduce implementation files only under approved local-only code paths.",
        "`scripts/local_media_agent/visible_report_runtime_generator.py`",
        "`tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py`",
        "This contract does not create those files.",
    ]:
        assert token in text
    assert not Path("scripts/local_media_agent/visible_report_runtime_generator.py").exists()
    assert not Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py").exists()


def test_future_public_interface_contract_is_defined() -> None:
    text = _text()
    for token in [
        "`generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path`",
        "accept already-created controlled scanner result data",
        "validate all required facts before rendering",
        "write one authorized local report artifact only after validation passes",
        "return the created local report path",
        "fail closed before writing output if validation fails",
    ]:
        assert token in text


def test_future_public_interface_must_not_execute_external_work() -> None:
    text = _text()
    for token in [
        "execute scanner code",
        "execute ffprobe",
        "execute ffmpeg",
        "inspect real client media",
        "perform network calls",
        "upload to SaaS",
        "write to any database",
    ]:
        assert token in text


def test_required_future_input_schema_is_defined() -> None:
    text = _text()
    for token in [
        "`report_identity`",
        "`privacy_evidence`",
        "`scanner_summary`",
        "`accepted_media`",
        "`rejected_non_media`",
        "`human_review`",
        "`warnings`",
        "`created_output_artifacts`",
        "`roadmap_modules_not_generated`",
        "Missing required input groups must produce a validation error and no report artifact.",
    ]:
        assert token in text


def test_required_future_input_facts_are_defined() -> None:
    text = _text()
    for token in [
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
    ]:
        assert token in text


def test_required_future_validation_order_is_ordered() -> None:
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
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)
    assert "Any failed validation step must stop rendering and prevent output creation." in text


def test_required_future_output_contract_is_local_and_limited() -> None:
    text = _text()
    for token in [
        "one visible report artifact only under an explicitly authorized local output root",
        "`05_reports/`",
        "`00_project/`",
        "`01_media_catalog/`",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`06_exports/`",
        "database records",
        "SaaS records",
    ]:
        assert token in text


def test_required_future_report_sections_are_ordered() -> None:
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


def test_required_future_privacy_contract_is_defined() -> None:
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


def test_required_future_determinism_contract_is_defined() -> None:
    text = _text()
    for token in [
        "produce deterministic report content for the same controlled input",
        "avoid volatile metadata by default",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths",
        "environment-dependent ordering",
        "sort deterministically",
    ]:
        assert token in text


def test_required_future_failure_contract_is_defined() -> None:
    text = _text()
    for token in [
        "fail closed when required data is missing, inconsistent, unsafe, or unsupported",
        "explicit validation exception",
        "no output file written",
        "clear human-review marker in non-client-facing diagnostic contexts",
        "visible warning preservation when rendering is allowed",
        "silent report generation after missing facts",
        "hiding warnings",
        "converting scanner candidates into finished editorial deliverables",
        "writing partial client-facing reports",
    ]:
        assert token in text


def test_explicit_non_goals_block_runtime_and_roadmap_claims() -> None:
    text = _text()
    for token in [
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
    ]:
        assert token in text


def test_acceptance_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "minimal, local-only, deterministic, fail-closed rendering component",
        "without expanding current product claims",
        "preserve the boundary between scanner facts, visible report rendering, and roadmap-only modules",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_IMPLEMENTATION_CONTRACT_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.QA.GATE.V1",
    ]:
        assert token in text


def test_source_readiness_qa_gate_supports_implementation_contract_transition() -> None:
    text = _text(READINESS_QA_GATE_DOC)
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_RUNTIME_GENERATOR_IMPLEMENTATION_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.IMPLEMENTATION.CONTRACT.V1" in text


def test_source_readiness_still_blocks_runtime_implementation() -> None:
    text = _text(READINESS_DOC)
    assert "This phase does not implement the runtime generator." in text
    assert "This phase does not create a runtime report artifact." in text
    assert "This phase does not execute the scanner." in text
