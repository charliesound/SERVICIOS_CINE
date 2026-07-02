from pathlib import Path

from scripts.local_media_agent.gate_generator import (
    GATE_GENERATOR_HANDLE,
    GATE_GENERATOR_RECORD_ID,
    GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID,
    GateArtifactPlan,
    GateDefinition,
    RichGateArtifactPlan,
    RichGateDefinition,
    build_gate_artifact_plan,
    build_gate_document,
    build_gate_test_stub,
    build_rich_gate_artifact_plan,
    build_rich_gate_document,
    build_rich_gate_test_stub,
    build_rich_validation_plan,
    build_validation_plan,
    describe_gate_generator_boundary,
    describe_rich_gate_template_contract,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_gate_generator_rich_template_implementation_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _rich_definition() -> RichGateDefinition:
    return RichGateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.RICH.SAMPLE.GATE.V1",
        phase_slug="rich_sample_gate_v1",
        title="CID Local Media Agent — Rich Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_RICH_SAMPLE_GATE_V1_CLOSED",
        starting_state="RICH_SAMPLE_STARTING_STATE",
        target_next_state="RICH_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Rich sample deterministic generation.",
        source_phase_identifier="CID.LOCAL_MEDIA_AGENT.SOURCE.GATE.V1",
        source_closure_result="LOCAL_MEDIA_AGENT_SOURCE_GATE_V1_CLOSED",
        source_state="SOURCE_SAMPLE_STATE",
        record_id="rich_sample_record_001",
        record_handle="RICH_SAMPLE_HANDLE_001",
        source_record_id="source_record_001",
        source_record_handle="SOURCE_HANDLE_001",
        doc_artifact_path="docs/product/local_media_agent/rich_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_rich_sample_gate_v1.py",
        implementation_artifact_paths=(
            "scripts/local_media_agent/gate_generator.py",
        ),
        created_artifacts=(
            "docs/product/local_media_agent/rich_sample_gate_v1.md",
            "tests/unit/test_rich_sample_gate_v1.py",
        ),
        required_checks=(
            "Rich sample gate test.",
            "The WSL repo guard script.",
            "The PostgreSQL-only regression guard script.",
        ),
        forbidden_changes=(
            "Touching SaaS backend.",
            "Touching databases.",
            "Executing FFmpeg.",
        ),
        safety_boundaries=(
            "text_only",
            "non_writing",
            "non_executing",
        ),
        positive_assertions=(
            "Rich sample record is present.",
            "Rich sample output is deterministic.",
        ),
        closure_criteria=(
            "All rich sample tests pass.",
            "Repository guards pass.",
        ),
        recommended_next_phase="CID.LOCAL_MEDIA_AGENT.RICH.SAMPLE.QA.GATE.V1",
        commit_message="test: add rich sample gate",
        tag_name="cid-dev-stable-rich-sample-gate-v1",
    )


def _generic_definition() -> GateDefinition:
    return GateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.GENERIC.SAMPLE.GATE.V1",
        phase_slug="generic_sample_gate_v1",
        title="CID Local Media Agent — Generic Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_GENERIC_SAMPLE_GATE_V1_CLOSED",
        starting_state="GENERIC_SAMPLE_STARTING_STATE",
        target_next_state="GENERIC_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Generic sample deterministic generation.",
        doc_artifact_path="docs/product/local_media_agent/generic_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_generic_sample_gate_v1.py",
        created_artifacts=(
            "docs/product/local_media_agent/generic_sample_gate_v1.md",
            "tests/unit/test_generic_sample_gate_v1.py",
        ),
        required_checks=(
            "Generic sample gate test.",
            "The WSL repo guard script.",
        ),
        forbidden_changes=(
            "Touching SaaS backend.",
            "Executing FFmpeg.",
        ),
    )


def test_rich_template_implementation_doc_exists():
    assert DOC.exists()


def test_generator_module_exists():
    assert GENERATOR.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.IMPLEMENTATION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_starting_state_is_from_rich_template_contract():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_DEFINED_READY_FOR_IMPLEMENTATION_GATE" in text


def test_target_state_is_rich_template_qa_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTED_READY_FOR_QA_GATE" in text


def test_source_rich_template_contract_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.CONTRACT.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_GATE_V1_CLOSED" in text


def test_implementation_record_is_declared():
    text = _doc_text()
    required_fields = [
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_SOURCE_CONTRACT_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_SOURCE_GENERATOR_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_SOURCE_GENERATOR_HANDLE",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_MODULE_PATH",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_SCOPE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_API_COMPATIBILITY_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_WRITE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_COMMAND_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_MEDIA_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_SAAS_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_implementation_record_values_are_present():
    text = _doc_text()
    required_values = [
        "gate_generator_rich_template_implementation_001",
        "gate_generator_rich_template_contract_001",
        "gate_generator_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "rich_template_extension_only",
        "existing_generic_generator_api_preserved",
        "no_file_write_performed_by_generator",
        "no_command_execution_performed_by_generator",
        "no_media_access",
        "no_saas_integration",
        "rich_cid_gate_template_implemented_as_deterministic_text_only_generator_extension",
    ]
    for value in required_values:
        assert value in text


def test_existing_generic_generator_api_is_preserved():
    assert GATE_GENERATOR_RECORD_ID == "gate_generator_001"
    assert GATE_GENERATOR_HANDLE == "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001"
    assert GateDefinition.__name__ == "GateDefinition"
    assert GateArtifactPlan.__name__ == "GateArtifactPlan"
    assert callable(build_gate_document)
    assert callable(build_gate_test_stub)
    assert callable(build_validation_plan)
    assert callable(build_gate_artifact_plan)
    assert callable(describe_gate_generator_boundary)

    definition = _generic_definition()
    plan = build_gate_artifact_plan(definition)
    assert isinstance(plan, GateArtifactPlan)
    assert definition.phase_identifier in plan.document_text
    assert definition.phase_identifier in plan.test_stub_text


def test_rich_generator_public_api_is_available():
    assert GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID == "gate_generator_rich_template_implementation_001"
    assert RichGateDefinition.__name__ == "RichGateDefinition"
    assert RichGateArtifactPlan.__name__ == "RichGateArtifactPlan"
    assert callable(build_rich_gate_document)
    assert callable(build_rich_gate_test_stub)
    assert callable(build_rich_validation_plan)
    assert callable(build_rich_gate_artifact_plan)
    assert callable(describe_rich_gate_template_contract)


def test_rich_gate_document_is_deterministic_and_complete():
    definition = _rich_definition()

    first = build_rich_gate_document(definition)
    second = build_rich_gate_document(definition)

    assert first == second
    assert "# CID Local Media Agent — Rich Sample Gate V1" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_SAMPLE_GATE_V1_CLOSED" in first
    assert "RICH_SAMPLE_STARTING_STATE" in first
    assert "RICH_SAMPLE_TARGET_NEXT_STATE" in first
    assert "CID.LOCAL_MEDIA_AGENT.SOURCE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_SOURCE_GATE_V1_CLOSED" in first
    assert "SOURCE_SAMPLE_STATE" in first
    assert "rich_sample_record_001" in first
    assert "RICH_SAMPLE_HANDLE_001" in first
    assert "source_record_001" in first
    assert "SOURCE_HANDLE_001" in first
    assert "docs/product/local_media_agent/rich_sample_gate_v1.md" in first
    assert "tests/unit/test_rich_sample_gate_v1.py" in first
    assert "scripts/local_media_agent/gate_generator.py" in first
    assert "Touching SaaS backend." in first
    assert "Touching databases." in first
    assert "Executing FFmpeg." in first
    assert "Rich sample record is present." in first
    assert "All rich sample tests pass." in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.SAMPLE.QA.GATE.V1" in first
    assert "test: add rich sample gate" in first
    assert "cid-dev-stable-rich-sample-gate-v1" in first


def test_rich_gate_test_stub_is_deterministic_and_rich():
    definition = _rich_definition()

    first = build_rich_gate_test_stub(definition)
    second = build_rich_gate_test_stub(definition)

    assert first == second
    assert "from pathlib import Path" in first
    assert "DOC = ROOT" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_SAMPLE_GATE_V1_CLOSED" in first
    assert "RICH_SAMPLE_STARTING_STATE" in first
    assert "RICH_SAMPLE_TARGET_NEXT_STATE" in first
    assert "CID.LOCAL_MEDIA_AGENT.SOURCE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_SOURCE_GATE_V1_CLOSED" in first
    assert "SOURCE_SAMPLE_STATE" in first
    assert "rich_sample_record_001" in first
    assert "RICH_SAMPLE_HANDLE_001" in first


def test_rich_validation_plan_preserves_all_structured_inputs():
    definition = _rich_definition()

    plan = build_rich_validation_plan(definition)

    assert plan["created_artifacts"] == definition.created_artifacts
    assert plan["implementation_artifact_paths"] == definition.implementation_artifact_paths
    assert plan["required_checks"] == definition.required_checks
    assert plan["forbidden_changes"] == definition.forbidden_changes
    assert plan["safety_boundaries"] == definition.safety_boundaries
    assert plan["positive_assertions"] == definition.positive_assertions
    assert plan["closure_criteria"] == definition.closure_criteria


def test_rich_gate_artifact_plan_combines_outputs_without_writing():
    definition = _rich_definition()

    plan = build_rich_gate_artifact_plan(definition)

    assert isinstance(plan, RichGateArtifactPlan)
    assert plan.phase_identifier == definition.phase_identifier
    assert plan.phase_slug == definition.phase_slug
    assert plan.doc_artifact_path == definition.doc_artifact_path
    assert plan.test_artifact_path == definition.test_artifact_path
    assert plan.implementation_artifact_paths == definition.implementation_artifact_paths
    assert definition.phase_identifier in plan.document_text
    assert definition.phase_identifier in plan.test_stub_text
    assert plan.validation_plan["required_checks"] == definition.required_checks


def test_rich_gate_artifact_plan_is_deterministic():
    definition = _rich_definition()

    first = build_rich_gate_artifact_plan(definition)
    second = build_rich_gate_artifact_plan(definition)

    assert first == second


def test_rich_template_contract_boundary_is_safe():
    boundary = describe_rich_gate_template_contract()

    expected = {
        "record_id": "gate_generator_rich_template_implementation_001",
        "source_record_id": "gate_generator_001",
        "source_handle": "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "determinism": "required",
        "output_mode": "text_and_structured_plans_only",
        "filesystem_write": "not_performed",
        "existing_file_modification": "not_performed",
        "command_execution": "not_performed",
        "subprocess_execution": "not_performed",
        "media_access": "not_performed",
        "folder_scan": "not_performed",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
        "database": "not_touched",
        "docker": "not_touched",
        "alembic": "not_touched",
        "stripe": "not_touched",
        "ai_jobs": "not_touched",
        "credits_ledger": "not_touched",
    }
    assert boundary == expected


def test_implemented_public_api_extension_is_documented():
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


def test_compatibility_requirements_are_documented():
    text = _doc_text()
    compatibility_items = [
        "`GateDefinition`",
        "`GateArtifactPlan`",
        "`build_gate_document`",
        "`build_gate_test_stub`",
        "`build_validation_plan`",
        "`build_gate_artifact_plan`",
        "`describe_gate_generator_boundary`",
    ]
    for item in compatibility_items:
        assert item in text


def test_rich_template_capabilities_are_documented():
    text = _doc_text()
    capabilities = [
        "Phase identifier.",
        "Phase slug.",
        "Title.",
        "Expected closure result.",
        "Starting state.",
        "Target next state.",
        "Source phase identifier.",
        "Source closure result.",
        "Source state.",
        "Record ID.",
        "Record handle.",
        "Source record ID.",
        "Source record handle.",
        "Document artifact path.",
        "Test artifact path.",
        "Implementation artifact paths.",
        "Created artifacts.",
        "Required checks.",
        "Forbidden changes.",
        "Safety boundaries.",
        "Positive assertions.",
        "Closure criteria.",
        "Recommended next phase.",
        "Commit message.",
        "Tag name.",
    ]
    for capability in capabilities:
        assert capability in text


def test_rich_template_safety_boundary_is_documented():
    text = _doc_text()
    boundary_items = [
        "deterministic",
        "text_only",
        "non_writing",
        "non_executing",
        "no_command_execution",
        "no_subprocess_execution",
        "no_media_access",
        "no_folder_scan",
        "no_ffmpeg_execution",
        "no_ffprobe_execution",
        "no_scanner_execution",
        "no_saas_integration",
        "no_database_coupling",
        "no_docker_coupling",
        "no_alembic_coupling",
        "no_stripe_coupling",
        "no_ai_jobs_coupling",
        "no_credits_ledger_coupling",
    ]
    for item in boundary_items:
        assert item in text


def test_positive_assertions_are_documented():
    text = _doc_text()
    assertions = [
        "The generator module is extended with rich CID template dataclasses.",
        "The existing generic generator API remains available.",
        "The rich document helper returns deterministic Markdown text.",
        "The rich test stub helper returns deterministic pytest text.",
        "The rich validation helper returns deterministic structured data.",
        "The rich artifact plan helper combines document, test stub, and validation plan.",
        "The rich template contract helper returns static non-runtime statuses.",
        "The implementation does not write files.",
        "The implementation does not execute commands.",
        "The implementation does not execute subprocesses.",
        "The implementation does not access media.",
        "The implementation does not scan folders.",
        "The implementation does not touch SaaS.",
        "The implementation does not touch databases.",
        "The implementation does not touch Docker.",
        "The implementation does not touch Alembic.",
        "The implementation does not touch Stripe.",
        "The implementation does not touch AI Jobs.",
        "The implementation does not touch credits or ledger.",
    ]
    for item in assertions:
        assert item in text


def test_forbidden_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Auto-writing generated files.",
        "Auto-committing generated files.",
        "Auto-tagging generated files.",
        "Auto-pushing generated files.",
        "Executing generated shell commands.",
        "Modifying existing runtime code outside the scoped generator module.",
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


def test_next_phase_boundary_is_rich_template_qa():
    text = _doc_text()
    assert "The next conservative phase should be a rich template QA gate." in text
    assert "That QA gate should validate deterministic rich output, API compatibility, and safety boundaries." in text
    assert "After that QA gate, the rich template may be used for accelerated product gates." in text


def test_required_checks_reference_previous_chain_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This gate generator rich template implementation gate test.",
        "The previous gate generator rich template contract gate test.",
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


def test_closing_state_is_rich_template_qa_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTED_READY_FOR_QA_GATE" in text
