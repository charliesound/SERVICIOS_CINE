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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_gate_generator_isolated_implementation_gate_v1.md"
IMPL = ROOT / "scripts/local_media_agent/gate_generator.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _impl_text() -> str:
    return IMPL.read_text(encoding="utf-8")


def _sample_definition() -> GateDefinition:
    return GateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1",
        phase_slug="sample_gate_v1",
        title="CID Local Media Agent — Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_SAMPLE_GATE_V1_CLOSED",
        starting_state="SAMPLE_STARTING_STATE",
        target_next_state="SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Sample deterministic gate generation.",
        doc_artifact_path="docs/product/local_media_agent/sample_gate_v1.md",
        test_artifact_path="tests/unit/test_sample_gate_v1.py",
        created_artifacts=(
            "docs/product/local_media_agent/sample_gate_v1.md",
            "tests/unit/test_sample_gate_v1.py",
        ),
        required_checks=(
            "Sample gate test.",
            "The WSL repo guard script.",
            "The PostgreSQL-only regression guard script.",
        ),
        forbidden_changes=(
            "Touching SaaS backend.",
            "Touching databases.",
            "Executing FFmpeg.",
        ),
    )


def test_gate_generator_doc_exists():
    assert DOC.exists()


def test_gate_generator_module_exists():
    assert IMPL.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.ISOLATED_IMPLEMENTATION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_ISOLATED_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_starting_state_is_current_product_state():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_DRY_RUN_QA_PASSED_READY_FOR_SANITIZED_REPORT_READINESS_GATE" in text


def test_target_state_is_template_qa_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_CREATED_READY_FOR_TEMPLATE_QA_GATE" in text


def test_gate_generator_record_is_documented():
    text = _doc_text()
    assert "gate_generator_001" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001" in text
    assert "isolated_gate_generator_created_for_repetitive_gate_acceleration" in text


def test_public_api_contract_is_documented():
    text = _doc_text()
    required_items = [
        "GateDefinition",
        "GateArtifactPlan",
        "build_gate_document",
        "build_gate_test_stub",
        "build_validation_plan",
        "build_gate_artifact_plan",
        "describe_gate_generator_boundary",
    ]
    for item in required_items:
        assert item in text


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


def test_build_gate_document_is_deterministic():
    definition = _sample_definition()

    first = build_gate_document(definition)
    second = build_gate_document(definition)

    assert first == second
    assert "CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_SAMPLE_GATE_V1_CLOSED" in first
    assert "SAMPLE_STARTING_STATE" in first
    assert "SAMPLE_TARGET_NEXT_STATE" in first
    assert "Sample deterministic gate generation." in first
    assert "Touching SaaS backend." in first
    assert "Touching databases." in first
    assert "Executing FFmpeg." in first


def test_build_gate_test_stub_is_deterministic():
    definition = _sample_definition()

    first = build_gate_test_stub(definition)
    second = build_gate_test_stub(definition)

    assert first == second
    assert "from pathlib import Path" in first
    assert "CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1" in first
    assert "LOCAL_MEDIA_AGENT_SAMPLE_GATE_V1_CLOSED" in first
    assert "SAMPLE_STARTING_STATE" in first
    assert "SAMPLE_TARGET_NEXT_STATE" in first


def test_build_validation_plan_preserves_inputs():
    definition = _sample_definition()

    plan = build_validation_plan(definition)

    assert plan["required_checks"] == definition.required_checks
    assert plan["created_artifacts"] == definition.created_artifacts
    assert plan["forbidden_changes"] == definition.forbidden_changes


def test_build_gate_artifact_plan_returns_all_text_without_writing():
    definition = _sample_definition()

    plan = build_gate_artifact_plan(definition)

    assert isinstance(plan, GateArtifactPlan)
    assert plan.phase_identifier == "CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1"
    assert plan.phase_slug == "sample_gate_v1"
    assert plan.doc_artifact_path == "docs/product/local_media_agent/sample_gate_v1.md"
    assert plan.test_artifact_path == "tests/unit/test_sample_gate_v1.py"
    assert "CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1" in plan.document_text
    assert "CID.LOCAL_MEDIA_AGENT.SAMPLE.GATE.V1" in plan.test_stub_text
    assert plan.validation_plan["required_checks"] == definition.required_checks


def test_gate_generator_boundary_reports_safe_statuses():
    boundary = describe_gate_generator_boundary()

    expected = {
        "record_id": "gate_generator_001",
        "handle": "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
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


def test_safety_boundary_is_documented():
    text = _doc_text()
    required_items = [
        "No filesystem writes.",
        "No modification of existing files.",
        "No shell command execution.",
        "No subprocess execution.",
        "No media access.",
        "No folder scanning.",
        "No local operator material access.",
        "No FFmpeg execution.",
        "No ffprobe execution.",
        "No scanner execution.",
        "No SaaS coupling.",
        "No database coupling.",
        "No Docker coupling.",
        "No Alembic coupling.",
        "No Stripe coupling.",
        "No AI Jobs coupling.",
        "No credits or ledger coupling.",
        "Deterministic output for the same input.",
    ]
    for item in required_items:
        assert item in text


def test_codex_or_opencode_constraints_are_documented():
    text = _doc_text()
    required_items = [
        "They must not push directly to `main`.",
        "They must not create stable tags directly.",
        "They must not bypass repository guards.",
        "They must not touch forbidden areas.",
        "They should work only on temporary branches or reviewable diffs.",
    ]
    for item in required_items:
        assert item in text


def test_required_checks_reference_previous_chain_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This gate generator isolated implementation gate test.",
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
    combined = _doc_text() + "\n" + _impl_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_generator_does_not_contain_runtime_invocation_patterns():
    text = _impl_text()
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


def test_document_does_not_authorize_forbidden_changes():
    text = _doc_text()
    forbidden_items = [
        "Auto-committing generated files.",
        "Auto-tagging generated files.",
        "Auto-pushing generated files.",
        "Writing generated files to disk.",
        "Modifying existing product code.",
        "Modifying existing runtime code.",
        "Executing shell commands from the generator.",
        "Executing subprocesses from the generator.",
        "Reading local media files.",
        "Scanning local folders.",
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


def test_closing_state_is_template_qa_readiness():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_CREATED_READY_FOR_TEMPLATE_QA_GATE" in text
