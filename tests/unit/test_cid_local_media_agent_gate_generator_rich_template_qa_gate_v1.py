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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_gate_generator_rich_template_qa_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _rich_definition() -> RichGateDefinition:
    return RichGateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.RICH.QA.SAMPLE.GATE.V1",
        phase_slug="rich_qa_sample_gate_v1",
        title="CID Local Media Agent — Rich QA Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_RICH_QA_SAMPLE_GATE_V1_CLOSED",
        starting_state="RICH_QA_SAMPLE_STARTING_STATE",
        target_next_state="RICH_QA_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Rich QA sample deterministic generation.",
        source_phase_identifier="CID.LOCAL_MEDIA_AGENT.RICH.SOURCE.GATE.V1",
        source_closure_result="LOCAL_MEDIA_AGENT_RICH_SOURCE_GATE_V1_CLOSED",
        source_state="RICH_SOURCE_SAMPLE_STATE",
        record_id="rich_qa_sample_record_001",
        record_handle="RICH_QA_SAMPLE_HANDLE_001",
        source_record_id="rich_source_record_001",
        source_record_handle="RICH_SOURCE_HANDLE_001",
        doc_artifact_path="docs/product/local_media_agent/rich_qa_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_rich_qa_sample_gate_v1.py",
        implementation_artifact_paths=(
            "scripts/local_media_agent/gate_generator.py",
        ),
        created_artifacts=(
            "docs/product/local_media_agent/rich_qa_sample_gate_v1.md",
            "tests/unit/test_rich_qa_sample_gate_v1.py",
        ),
        required_checks=(
            "Rich QA sample gate test.",
            "Previous rich sample gate test.",
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
        safety_boundaries=(
            "deterministic",
            "text_only",
            "non_writing",
            "non_executing",
            "no_saas_integration",
        ),
        positive_assertions=(
            "Rich QA sample record is present.",
            "Rich QA sample output is deterministic.",
            "Rich QA sample source continuity is preserved.",
        ),
        closure_criteria=(
            "All rich QA sample tests pass.",
            "Repository guards pass.",
            "Remote tag verification passes.",
        ),
        recommended_next_phase="CID.LOCAL_MEDIA_AGENT.RICH.QA.SAMPLE.NEXT.GATE.V1",
        commit_message="test: add rich QA sample gate",
        tag_name="cid-dev-stable-rich-qa-sample-gate-v1",
    )


def _generic_definition() -> GateDefinition:
    return GateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.GENERIC.QA.SAMPLE.GATE.V1",
        phase_slug="generic_qa_sample_gate_v1",
        title="CID Local Media Agent — Generic QA Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_GENERIC_QA_SAMPLE_GATE_V1_CLOSED",
        starting_state="GENERIC_QA_SAMPLE_STARTING_STATE",
        target_next_state="GENERIC_QA_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Generic QA sample deterministic generation.",
        doc_artifact_path="docs/product/local_media_agent/generic_qa_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_generic_qa_sample_gate_v1.py",
        created_artifacts=(
            "docs/product/local_media_agent/generic_qa_sample_gate_v1.md",
            "tests/unit/test_generic_qa_sample_gate_v1.py",
        ),
        required_checks=(
            "Generic QA sample gate test.",
            "The WSL repo guard script.",
        ),
        forbidden_changes=(
            "Touching SaaS backend.",
            "Executing FFmpeg.",
        ),
    )


def test_rich_template_qa_doc_exists():
    assert DOC.exists()


def test_generator_module_exists():
    assert GENERATOR.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.QA.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_starting_state_is_from_rich_template_implementation_gate():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTED_READY_FOR_QA_GATE" in text


def test_target_state_enables_accelerated_product_gates():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_PRODUCT_GATES" in text


def test_source_rich_template_implementation_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.IMPLEMENTATION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_rich_template_qa_record_is_declared():
    text = _doc_text()
    required_fields = [
        "GATE_GENERATOR_RICH_TEMPLATE_QA_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_SOURCE_IMPLEMENTATION_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_SOURCE_GENERATOR_RECORD_ID",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_SOURCE_GENERATOR_HANDLE",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_MODULE_PATH",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_MODULE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_IMPORT_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_GENERIC_API_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_RICH_API_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_DOCUMENT_TEMPLATE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_TEST_TEMPLATE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_VALIDATION_PLAN_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_ARTIFACT_PLAN_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_WRITE_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_COMMAND_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_MEDIA_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_SAAS_STATUS",
        "GATE_GENERATOR_RICH_TEMPLATE_QA_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_rich_template_qa_record_values_are_present():
    text = _doc_text()
    required_values = [
        "gate_generator_rich_template_qa_001",
        "gate_generator_rich_template_implementation_001",
        "gate_generator_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "present_and_compile_checked",
        "import_safe_no_runtime_side_effects_detected",
        "existing_generic_generator_api_preserved",
        "rich_gate_definition_artifact_plan_and_helpers_present",
        "deterministic_rich_document_generation_verified",
        "deterministic_rich_test_stub_generation_verified",
        "structured_rich_validation_plan_generation_verified",
        "combined_rich_artifact_plan_generation_verified",
        "no_file_write_performed_by_generator",
        "no_command_execution_performed_by_generator",
        "no_media_access",
        "no_saas_integration",
        "qa_passed_for_deterministic_rich_text_only_gate_generation",
    ]
    for value in required_values:
        assert value in text


def test_generic_api_remains_compatible():
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


def test_rich_api_is_available():
    assert GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID == "gate_generator_rich_template_implementation_001"
    assert RichGateDefinition.__name__ == "RichGateDefinition"
    assert RichGateArtifactPlan.__name__ == "RichGateArtifactPlan"
    assert callable(build_rich_gate_document)
    assert callable(build_rich_gate_test_stub)
    assert callable(build_rich_validation_plan)
    assert callable(build_rich_gate_artifact_plan)
    assert callable(describe_rich_gate_template_contract)


def test_rich_document_template_is_deterministic_and_complete():
    definition = _rich_definition()

    first = build_rich_gate_document(definition)
    second = build_rich_gate_document(definition)

    assert first == second
    assert "# CID Local Media Agent — Rich QA Sample Gate V1" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.QA.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_QA_SAMPLE_GATE_V1_CLOSED" in first
    assert "RICH_QA_SAMPLE_STARTING_STATE" in first
    assert "RICH_QA_SAMPLE_TARGET_NEXT_STATE" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.SOURCE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_SOURCE_GATE_V1_CLOSED" in first
    assert "RICH_SOURCE_SAMPLE_STATE" in first
    assert "rich_qa_sample_record_001" in first
    assert "RICH_QA_SAMPLE_HANDLE_001" in first
    assert "rich_source_record_001" in first
    assert "RICH_SOURCE_HANDLE_001" in first
    assert "docs/product/local_media_agent/rich_qa_sample_gate_v1.md" in first
    assert "tests/unit/test_rich_qa_sample_gate_v1.py" in first
    assert "scripts/local_media_agent/gate_generator.py" in first
    assert "Touching SaaS backend." in first
    assert "Touching databases." in first
    assert "Executing FFmpeg." in first
    assert "Executing ffprobe." in first
    assert "Executing scanner logic." in first
    assert "deterministic" in first
    assert "text_only" in first
    assert "non_writing" in first
    assert "non_executing" in first
    assert "Rich QA sample output is deterministic." in first
    assert "All rich QA sample tests pass." in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.QA.SAMPLE.NEXT.GATE.V1" in first
    assert "test: add rich QA sample gate" in first
    assert "cid-dev-stable-rich-qa-sample-gate-v1" in first


def test_rich_test_stub_template_is_deterministic_and_source_aware():
    definition = _rich_definition()

    first = build_rich_gate_test_stub(definition)
    second = build_rich_gate_test_stub(definition)

    assert first == second
    assert "from pathlib import Path" in first
    assert "DOC = ROOT" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.QA.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_QA_SAMPLE_GATE_V1_CLOSED" in first
    assert "RICH_QA_SAMPLE_STARTING_STATE" in first
    assert "RICH_QA_SAMPLE_TARGET_NEXT_STATE" in first
    assert "CID.LOCAL_MEDIA_AGENT.RICH.SOURCE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_RICH_SOURCE_GATE_V1_CLOSED" in first
    assert "RICH_SOURCE_SAMPLE_STATE" in first
    assert "rich_qa_sample_record_001" in first
    assert "RICH_QA_SAMPLE_HANDLE_001" in first


def test_rich_validation_plan_preserves_all_inputs():
    definition = _rich_definition()

    plan = build_rich_validation_plan(definition)

    assert plan["created_artifacts"] == definition.created_artifacts
    assert plan["implementation_artifact_paths"] == definition.implementation_artifact_paths
    assert plan["required_checks"] == definition.required_checks
    assert plan["forbidden_changes"] == definition.forbidden_changes
    assert plan["safety_boundaries"] == definition.safety_boundaries
    assert plan["positive_assertions"] == definition.positive_assertions
    assert plan["closure_criteria"] == definition.closure_criteria


def test_rich_artifact_plan_combines_all_outputs_without_writing():
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
    assert plan.validation_plan["forbidden_changes"] == definition.forbidden_changes
    assert plan.validation_plan["safety_boundaries"] == definition.safety_boundaries
    assert plan.validation_plan["positive_assertions"] == definition.positive_assertions
    assert plan.validation_plan["closure_criteria"] == definition.closure_criteria


def test_rich_artifact_plan_is_deterministic():
    definition = _rich_definition()

    first = build_rich_gate_artifact_plan(definition)
    second = build_rich_gate_artifact_plan(definition)

    assert first == second


def test_rich_template_boundary_reports_static_safe_statuses():
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


def test_doc_qa_assertions_are_documented():
    text = _doc_text()
    required_assertions = [
        "The generator module exists.",
        "The generator module compiles.",
        "The existing generic generator API remains available.",
        "The rich generator API is available.",
        "`RichGateDefinition` is stable.",
        "`RichGateArtifactPlan` is stable.",
        "`build_rich_gate_document` returns deterministic Markdown text.",
        "`build_rich_gate_test_stub` returns deterministic pytest text.",
        "`build_rich_validation_plan` returns deterministic structured data.",
        "`build_rich_gate_artifact_plan` returns all rich generated text without writing files.",
        "`describe_rich_gate_template_contract` returns static safety statuses.",
        "Rich generated documents contain source phase continuity.",
        "Rich generated documents contain source result continuity.",
        "Rich generated documents contain source state continuity.",
        "Rich generated documents contain record IDs and handles.",
        "Rich generated documents contain implementation artifact paths.",
        "Rich generated documents contain safety boundaries.",
        "Rich generated documents contain positive assertions.",
        "Rich generated documents contain closure criteria.",
        "Rich generated documents contain recommended next phase.",
        "The rich generator remains suitable for accelerated product gates.",
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
        "Modifying the generator implementation.",
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


def test_accelerated_product_gate_boundary_is_documented():
    text = _doc_text()
    required_items = [
        "After this QA gate, the rich generator template may be used to prepare repetitive product gate artifacts faster.",
        "Generated artifacts still require human review.",
        "Generated artifacts still require tests.",
        "Generated artifacts still require repository guards.",
        "Generated artifacts still require explicit commit and tag closure.",
        "The generator must not write files directly.",
        "The generator must not push directly to `main`.",
        "The generator must not create stable tags directly.",
        "The generator must not bypass repository guards.",
    ]
    for item in required_items:
        assert item in text


def test_required_checks_reference_previous_chain_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This gate generator rich template QA gate test.",
        "The previous gate generator rich template implementation gate test.",
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


def test_closing_state_is_accelerated_product_gate_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_PRODUCT_GATES" in text
