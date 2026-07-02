from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_input_real_file_binding_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_operator_input_real_file_binding_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_REAL_FILE_BINDING.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_REAL_FILE_BINDING_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_comes_from_materialized_operator_input():
    text = _text()
    assert "OPERATOR_INPUT_001_MATERIALIZED_FROM_SANITIZED_VALUES_WITHOUT_REAL_FILE_BINDING" in text


def test_target_next_state_is_ready_for_binding_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_INPUT_REAL_FILE_BINDING_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This gate does not perform the binding." in text
    assert "This gate does not select a real file." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_materialized_input_values_are_preserved():
    text = _text()
    required_values = [
        "operator_input_materialization_001",
        "operator_input_001",
        "safe_capture_001",
        "local_single_file_candidate_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "materialized_from_sanitized_operator_capture_without_real_file_binding",
    ]
    for value in required_values:
        assert value in text


def test_readiness_authorization_scope_is_future_only():
    text = _text()
    assert "This readiness gate authorizes only the preparation of a later gate." in text
    assert "The later gate may define a controlled real-file binding record only if all of the following remain true:" in text


def test_future_binding_readiness_record_is_declared():
    text = _text()
    assert "operator_input_real_file_binding_readiness_001" in text
    assert "READINESS_INPUT_RECORD_ID" in text
    assert "READINESS_SOURCE_MATERIALIZATION_RECORD_ID" in text
    assert "READINESS_VERDICT" in text


def test_no_binding_happens_in_this_gate():
    text = _text()
    assert "not_bound_in_this_gate" in text
    assert "not_selected_in_this_gate" in text
    assert "not_recorded_in_this_gate" in text
    assert "ready_for_operator_input_real_file_binding_gate_without_real_file_binding" in text


def test_no_runtime_or_execution_is_created():
    text = _text()
    assert "no_runtime_created" in text
    assert "no_execution" in text
    assert "Creating runtime implementation." in text
    assert "Modifying existing CLI runtime." in text


def test_real_file_sensitive_data_is_forbidden():
    text = _text()
    forbidden_items = [
        "Selecting a real file.",
        "Recording a real filename.",
        "Recording an absolute path.",
        "Reading filesystem metadata from a media file.",
        "Opening a media file.",
    ]
    for item in forbidden_items:
        assert item in text


def test_media_tooling_is_forbidden():
    text = _text()
    forbidden_items = [
        "Running FFmpeg.",
        "Running ffprobe.",
        "Running a scanner.",
        "Decoding media.",
        "Transcribing media.",
        "Generating thumbnails.",
        "Generating waveforms.",
    ]
    for item in forbidden_items:
        assert item in text


def test_saas_and_platform_boundaries_are_forbidden():
    text = _text()
    forbidden_items = [
        "Creating SaaS backend integration.",
        "Creating SaaS frontend integration.",
        "Changing databases.",
        "Changing Docker.",
        "Changing Alembic.",
        "Changing Stripe.",
        "Changing AI Jobs.",
        "Changing credits or ledger.",
    ]
    for item in forbidden_items:
        assert item in text


def test_required_checks_reference_previous_gates_and_guards():
    text = _text()
    required_checks = [
        "This readiness gate test.",
        "The previous operator input materialization gate test.",
        "The previous operator input materialization readiness gate test.",
        "The previous safe operator value capture gate test.",
        "The previous safe operator value capture readiness gate test.",
        "The previous sanitized candidate input gate test.",
        "The previous sanitized single file candidate gate test.",
        "The previous real media preflight controlled execution gate test.",
        "The previous real media preflight readiness gate test.",
        "bash scripts/dev/guard_wsl_repo.sh",
        "bash scripts/dev/guard_no_sqlite_regressions.sh",
    ]
    for check in required_checks:
        assert check in text


def test_document_does_not_contain_windows_or_mount_paths():
    text = _text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in text


def test_document_does_not_contain_runtime_invocation_patterns():
    text = _text()
    forbidden_runtime_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "Path.stat(",
        ".stat()",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_runtime_patterns:
        assert pattern not in text


def test_closing_state_is_ready_for_later_binding_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_INPUT_REAL_FILE_BINDING_GATE" in text
