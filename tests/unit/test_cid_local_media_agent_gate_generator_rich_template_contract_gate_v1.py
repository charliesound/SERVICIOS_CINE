from pathlib import Path

from scripts.local_media_agent.gate_generator import (
    GATE_GENERATOR_HANDLE,
    GATE_GENERATOR_RECORD_ID,
    GateArtifactPlan,
    GateDefinition,
    build_gate_artifact_plan,
    build_gate_document,
    build_gate_test_stub,
    build_validation_plan,
    describe_gate_generator_boundary,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_gate_generator_rich_template_contract_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def test_rich_template_contract_doc_exists():
    assert DOC.exists()


def test_generator_module_exists_and_contract_gate_does_not_modify_it():
    assert GENERATOR.exists()
    assert GATE_GENERATOR_RECORD_ID == "gate_generator_001"
    assert GATE_GENERATOR_HANDLE == "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001"
    assert GateDefinition.__name__ == "GateDefinition"
    assert GateArtifactPlan.__name__ == "GateArtifactPlan"
    assert callable(build_gate_document)
    assert callable(build_gate_test_stub)
    assert callable(build_validation_plan)
    assert callable(build_gate_artifact_plan)
    assert callable(describe_gate_generator_boundary)


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.CONTRACT.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_GATE_V1_CLOSED" in text


def test_starting_state_is_from_template_qa():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_GATE_USE" in text


def test_target_state_is_implementation_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_DEFINED_READY_FOR_IMPLEMENTATION_GATE" in text


def test_source_template_qa_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.TEMPLATE_QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_contract_record_is_declared():
    text = _doc_text()
    required_fields = [
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SOURCE_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SOURCE_HANDLE",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SCOPE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_CODE_CHANGE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_WRITE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_COMMAND_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_MEDIA_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SAAS_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_contract_record_values_are_present():
    text = _doc_text()
    required_values = [
        "gate_generator_rich_template_contract_001",
        "gate_generator_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "contract_only",
        "no_generator_code_changed",
        "no_file_write_performed_by_generator",
        "no_command_execution_performed_by_generator",
        "no_media_access",
        "no_saas_integration",
        "rich_cid_gate_template_contract_defined_for_future_generator_extension",
    ]
    for value in required_values:
        assert value in text


def test_required_rich_template_inputs_are_defined():
    text = _doc_text()
    required_inputs = [
        "`phase_identifier`",
        "`phase_slug`",
        "`title`",
        "`expected_closure_result`",
        "`starting_state`",
        "`target_next_state`",
        "`source_phase_identifier`",
        "`source_closure_result`",
        "`source_state`",
        "`record_id`",
        "`record_handle`",
        "`source_record_id`",
        "`source_record_handle`",
        "`doc_artifact_path`",
        "`test_artifact_path`",
        "`implementation_artifact_paths`",
        "`created_artifacts`",
        "`required_checks`",
        "`forbidden_changes`",
        "`safety_boundaries`",
        "`positive_assertions`",
        "`closure_criteria`",
        "`recommended_next_phase`",
        "`commit_message`",
        "`tag_name`",
    ]
    for item in required_inputs:
        assert item in text


def test_required_rich_template_document_sections_are_defined():
    text = _doc_text()
    sections = [
        "Phase",
        "Expected closure result",
        "Starting state",
        "Target next state",
        "Gate purpose",
        "Source phase",
        "Source result",
        "Source state",
        "Created artifacts",
        "Record table",
        "Safety boundary",
        "Positive assertions",
        "Explicitly forbidden changes",
        "Required checks before closing",
        "Closure",
        "Closing state",
        "Recommended next phase",
    ]
    for section in sections:
        assert section in text


def test_required_rich_template_test_sections_are_defined():
    text = _doc_text()
    required_tests = [
        "Document exists.",
        "Phase identifier is present.",
        "Expected closure result is present.",
        "Starting state is present.",
        "Target next state is present.",
        "Source phase is present.",
        "Source closure result is present.",
        "Source state is present.",
        "Record ID is present.",
        "Record handle is present.",
        "Created artifacts are present.",
        "Required checks are present.",
        "Forbidden changes are present.",
        "Safety boundaries are present.",
        "Positive assertions are present.",
        "Closing state is present.",
        "Recommended next phase is present when provided.",
        "Windows and mount path fragments are absent from generated docs.",
        "Runtime invocation patterns are absent from generated source when source inspection is included.",
        "Generator output remains deterministic.",
    ]
    for item in required_tests:
        assert item in text


def test_standard_forbidden_changes_are_defined():
    text = _doc_text()
    forbidden_changes = [
        "Touching SaaS backend.",
        "Touching SaaS frontend.",
        "Touching databases.",
        "Touching Docker.",
        "Touching Alembic.",
        "Touching Stripe.",
        "Touching AI Jobs.",
        "Touching credits or ledger.",
        "Executing FFmpeg.",
        "Executing ffprobe.",
        "Executing scanner logic.",
        "Reading local media files.",
        "Scanning local folders.",
        "Inspecting real file metadata.",
        "Recording real local paths.",
        "Recording sensitive filenames.",
        "Recording parent folders.",
        "Auto-committing generated files.",
        "Auto-tagging generated files.",
        "Auto-pushing generated files.",
    ]
    for item in forbidden_changes:
        assert item in text


def test_standard_required_checks_are_defined():
    text = _doc_text()
    required_checks = [
        "Current gate test.",
        "Previous gate test.",
        "Previous chain tests.",
        "Generator tests when generator output is used.",
        "WSL repo guard script.",
        "PostgreSQL-only regression guard script.",
        "Explicit git status check.",
        "Explicit HEAD verification.",
        "Explicit staged file list check.",
        "Explicit remote tag verification when closing.",
    ]
    for item in required_checks:
        assert item in text


def test_future_public_api_extension_is_defined():
    text = _doc_text()
    api_items = [
        "`RichGateDefinition`",
        "`RichGateArtifactPlan`",
        "`build_rich_gate_document`",
        "`build_rich_gate_test_stub`",
        "`build_rich_validation_plan`",
        "`build_rich_gate_artifact_plan`",
        "`describe_rich_gate_template_contract`",
    ]
    for item in api_items:
        assert item in text


def test_future_implementation_acceptance_criteria_are_safe():
    text = _doc_text()
    criteria = [
        "Preserve the existing generic generator API.",
        "Remain deterministic.",
        "Return text and structured plans only.",
        "Avoid writing files.",
        "Avoid modifying existing files.",
        "Avoid executing commands.",
        "Avoid subprocess execution.",
        "Avoid media access.",
        "Avoid folder scanning.",
        "Avoid SaaS coupling.",
        "Avoid database coupling.",
        "Avoid Docker coupling.",
        "Avoid Alembic coupling.",
        "Avoid Stripe coupling.",
        "Avoid AI Jobs coupling.",
        "Avoid credits or ledger coupling.",
        "Preserve current generator tests.",
        "Add rich template tests.",
        "Keep manual review mandatory.",
        "Keep explicit commit and tag closure mandatory.",
    ]
    for item in criteria:
        assert item in text


def test_explicitly_forbidden_contract_gate_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Modifying `scripts/local_media_agent/gate_generator.py`.",
        "Auto-writing generated files.",
        "Auto-committing generated files.",
        "Auto-tagging generated files.",
        "Auto-pushing generated files.",
        "Executing generated shell commands.",
        "Modifying existing runtime code.",
        "Modifying existing CLI runtime.",
        "Reading local media files.",
        "Scanning local folders.",
        "Inspecting real file metadata.",
        "Probing media.",
        "Decoding media.",
        "Transcribing media.",
        "Executing FFmpeg.",
        "Executing ffprobe.",
        "Executing scanner logic.",
        "Touching SaaS backend.",
        "Touching SaaS frontend.",
        "Touching databases.",
        "Touching Docker.",
        "Touching Alembic.",
        "Touching Stripe.",
        "Touching AI Jobs.",
        "Touching credits or ledger.",
    ]
    for item in forbidden_items:
        assert item in text


def test_next_phase_boundary_is_rich_template_implementation():
    text = _doc_text()
    assert "The next conservative phase may implement the rich template extension in the generator." in text
    assert "That future implementation phase may modify `scripts/local_media_agent/gate_generator.py` only if explicitly scoped." in text
    assert "That future implementation phase must preserve all existing generator behavior." in text
    assert "That future implementation phase must remain text-only and non-executing." in text


def test_required_checks_reference_previous_chain_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This gate generator rich template contract gate test.",
        "The previous gate generator template QA gate test.",
        "The previous gate generator isolated implementation gate test.",
        "The previous controlled stat implementation dry-run QA gate test.",
        "The previous controlled stat implementation gate test.",
        "The previous controlled stat implementation readiness gate test.",
        "The previous code skeleton isolated contract QA gate test.",
        "The previous code skeleton gate test.",
        "The previous code skeleton readiness gate test.",
        "The previous real media preflight readiness gate test.",
        "The WSL repo guard script.",
        "The PostgreSQL-only regression guard script.",
    ]
    for check in required_checks:
        assert check in text


def test_document_and_generator_do_not_contain_windows_or_mount_paths():
    combined = _doc_text() + "\n" + _generator_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_generator_still_does_not_contain_runtime_or_write_patterns():
    text = _generator_text()
    forbidden_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "open(",
        ".write(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in text


def test_closing_state_is_rich_template_implementation_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_DEFINED_READY_FOR_IMPLEMENTATION_GATE" in text
