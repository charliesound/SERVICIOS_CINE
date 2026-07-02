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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_gate_generator_template_qa_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _definition() -> GateDefinition:
    return GateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.ACCELERATED.SAMPLE.GATE.V1",
        phase_slug="accelerated_sample_gate_v1",
        title="CID Local Media Agent — Accelerated Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_ACCELERATED_SAMPLE_GATE_V1_CLOSED",
        starting_state="ACCELERATED_SAMPLE_STARTING_STATE",
        target_next_state="ACCELERATED_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Accelerated sample deterministic text generation.",
        doc_artifact_path="docs/product/local_media_agent/accelerated_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_accelerated_sample_gate_v1.py",
        created_artifacts=(
            "docs/product/local_media_agent/accelerated_sample_gate_v1.md",
            "tests/unit/test_accelerated_sample_gate_v1.py",
        ),
        required_checks=(
            "Accelerated sample gate test.",
            "The WSL repo guard script.",
            "The PostgreSQL-only regression guard script.",
        ),
        forbidden_changes=(
            "Touching SaaS backend.",
            "Touching databases.",
            "Executing FFmpeg.",
            "Executing ffprobe.",
            "Executing scanner logic.",
        ),
    )


def test_template_qa_doc_exists():
    assert DOC.exists()


def test_generator_module_exists():
    assert GENERATOR.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.TEMPLATE_QA.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_starting_state_is_from_generator_implementation_gate():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_CREATED_READY_FOR_TEMPLATE_QA_GATE" in text


def test_target_state_allows_accelerated_gate_use():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_GATE_USE" in text


def test_source_gate_generator_implementation_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.ISOLATED_IMPLEMENTATION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_ISOLATED_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_template_qa_record_is_declared():
    text = _doc_text()
    required_fields = [
        "GATE_GENERATOR_TEMPLATE_QA_RECORD_ID",
        "GATE_GENERATOR_TEMPLATE_QA_SOURCE_RECORD_ID",
        "GATE_GENERATOR_TEMPLATE_QA_SOURCE_HANDLE",
        "GATE_GENERATOR_TEMPLATE_QA_MODULE_PATH",
        "GATE_GENERATOR_TEMPLATE_QA_MODULE_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_IMPORT_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_PUBLIC_API_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_DOCUMENT_TEMPLATE_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_TEST_TEMPLATE_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_VALIDATION_PLAN_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_ARTIFACT_PLAN_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_WRITE_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_COMMAND_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_MEDIA_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_SAAS_STATUS",
        "GATE_GENERATOR_TEMPLATE_QA_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_template_qa_record_values_are_passed():
    text = _doc_text()
    required_values = [
        "gate_generator_template_qa_001",
        "gate_generator_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "present_and_compile_checked",
        "import_safe_no_runtime_side_effects_detected",
        "expected_gate_definition_artifact_plan_and_helpers_present",
        "deterministic_document_generation_verified",
        "deterministic_test_stub_generation_verified",
        "structured_validation_plan_generation_verified",
        "combined_artifact_plan_generation_verified",
        "no_file_write_performed_by_generator",
        "no_command_execution_performed_by_generator",
        "qa_passed_for_deterministic_text_only_gate_generation",
    ]
    for value in required_values:
        assert value in text


def test_generator_public_api_is_available():
    assert GATE_GENERATOR_RECORD_ID == "gate_generator_001"
    assert GATE_GENERATOR_HANDLE == "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001"
    assert GateDefinition.__name__ == "GateDefinition"
    assert GateArtifactPlan.__name__ == "GateArtifactPlan"
    assert callable(build_gate_document)
    assert callable(build_gate_test_stub)
    assert callable(build_validation_plan)
    assert callable(build_gate_artifact_plan)
    assert callable(describe_gate_generator_boundary)


def test_document_template_is_deterministic_and_complete():
    definition = _definition()

    first = build_gate_document(definition)
    second = build_gate_document(definition)

    assert first == second
    assert "# CID Local Media Agent — Accelerated Sample Gate V1" in first
    assert "CID.LOCAL_MEDIA_AGENT.ACCELERATED.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_ACCELERATED_SAMPLE_GATE_V1_CLOSED" in first
    assert "ACCELERATED_SAMPLE_STARTING_STATE" in first
    assert "ACCELERATED_SAMPLE_TARGET_NEXT_STATE" in first
    assert "Accelerated sample deterministic text generation." in first
    assert "docs/product/local_media_agent/accelerated_sample_gate_v1.md" in first
    assert "tests/unit/test_accelerated_sample_gate_v1.py" in first
    assert "The WSL repo guard script." in first
    assert "The PostgreSQL-only regression guard script." in first
    assert "Touching SaaS backend." in first
    assert "Touching databases." in first
    assert "Executing FFmpeg." in first
    assert "Executing ffprobe." in first


def test_test_stub_template_is_deterministic_and_document_assertion_only():
    definition = _definition()

    first = build_gate_test_stub(definition)
    second = build_gate_test_stub(definition)

    assert first == second
    assert "from pathlib import Path" in first
    assert "DOC = ROOT" in first
    assert "def _doc_text() -> str:" in first
    assert "def test_gate_document_exists():" in first
    assert "def test_phase_identifier_is_present():" in first
    assert "CID.LOCAL_MEDIA_AGENT.ACCELERATED.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_ACCELERATED_SAMPLE_GATE_V1_CLOSED" in first
    assert "ACCELERATED_SAMPLE_STARTING_STATE" in first
    assert "ACCELERATED_SAMPLE_TARGET_NEXT_STATE" in first


def test_validation_plan_template_preserves_structured_inputs():
    definition = _definition()

    plan = build_validation_plan(definition)

    assert plan["required_checks"] == definition.required_checks
    assert plan["created_artifacts"] == definition.created_artifacts
    assert plan["forbidden_changes"] == definition.forbidden_changes


def test_gate_artifact_plan_combines_document_test_stub_and_validation_plan():
    definition = _definition()

    plan = build_gate_artifact_plan(definition)

    assert isinstance(plan, GateArtifactPlan)
    assert plan.phase_identifier == definition.phase_identifier
    assert plan.phase_slug == definition.phase_slug
    assert plan.doc_artifact_path == definition.doc_artifact_path
    assert plan.test_artifact_path == definition.test_artifact_path
    assert definition.phase_identifier in plan.document_text
    assert definition.phase_identifier in plan.test_stub_text
    assert plan.validation_plan["required_checks"] == definition.required_checks
    assert plan.validation_plan["created_artifacts"] == definition.created_artifacts
    assert plan.validation_plan["forbidden_changes"] == definition.forbidden_changes


def test_gate_artifact_plan_is_deterministic():
    definition = _definition()

    first = build_gate_artifact_plan(definition)
    second = build_gate_artifact_plan(definition)

    assert first == second


def test_generator_boundary_remains_non_runtime_and_non_writing():
    boundary = describe_gate_generator_boundary()

    assert boundary["filesystem_write"] == "not_performed"
    assert boundary["existing_file_modification"] == "not_performed"
    assert boundary["command_execution"] == "not_performed"
    assert boundary["subprocess_execution"] == "not_performed"
    assert boundary["media_access"] == "not_performed"
    assert boundary["folder_scan"] == "not_performed"
    assert boundary["ffmpeg"] == "not_executed"
    assert boundary["ffprobe"] == "not_executed"
    assert boundary["scanner"] == "not_executed"
    assert boundary["saas"] == "no_saas_integration"
    assert boundary["database"] == "not_touched"
    assert boundary["docker"] == "not_touched"
    assert boundary["alembic"] == "not_touched"
    assert boundary["stripe"] == "not_touched"
    assert boundary["ai_jobs"] == "not_touched"
    assert boundary["credits_ledger"] == "not_touched"


def test_qa_assertions_are_documented():
    text = _doc_text()
    required_assertions = [
        "The generator module exists.",
        "The generator module compiles.",
        "The generator public API is available.",
        "`GateDefinition` is stable.",
        "`GateArtifactPlan` is stable.",
        "`build_gate_document` returns deterministic Markdown text.",
        "`build_gate_test_stub` returns deterministic pytest text.",
        "`build_validation_plan` returns deterministic structured data.",
        "`build_gate_artifact_plan` returns all generated text without writing files.",
        "`describe_gate_generator_boundary` returns static safety statuses.",
        "Generated documents contain the phase identifier.",
        "Generated documents contain the expected closure result.",
        "Generated documents contain the starting state.",
        "Generated documents contain the target state.",
        "Generated documents contain created artifacts.",
        "Generated documents contain required checks.",
        "Generated documents contain forbidden changes.",
        "The generator remains suitable for accelerated repetitive gate creation.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_forbidden_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
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


def test_accelerated_use_boundary_is_documented():
    text = _doc_text()
    required_items = [
        "After this QA gate, the generator may be used to prepare repetitive gate artifacts faster.",
        "Generated artifacts still require human review.",
        "Generated artifacts still require tests.",
        "Generated artifacts still require repository guards.",
        "Generated artifacts still require explicit commit and tag closure.",
        "The generator must not push directly to `main`.",
        "The generator must not create stable tags directly.",
        "The generator must not bypass repository guards.",
    ]
    for item in required_items:
        assert item in text


def test_required_checks_reference_previous_chain_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This gate generator template QA gate test.",
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


def test_generator_does_not_contain_runtime_or_write_patterns():
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


def test_closing_state_is_accelerated_gate_use():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_GATE_USE" in text
