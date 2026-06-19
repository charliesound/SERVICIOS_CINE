from pathlib import Path

QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_post_execution_boundary_qa_gate_v1.md"
)
BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_post_execution_boundary_contract_v1.md"
)
EXECUTION_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_qa_gate_v1.md"
)
EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_post_execution_boundary_qa_docs_exist():
    assert QA_GATE_DOC.exists()
    assert BOUNDARY_DOC.exists()
    assert EXECUTION_QA_DOC.exists()
    assert EXECUTION_DOC.exists()


def test_second_controlled_scenario_post_execution_boundary_qa_phase_declared():
    t = read(QA_GATE_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.POST.EXECUTION.BOUNDARY.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.POST.EXECUTION.BOUNDARY.CONTRACT.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.V1" in t
    assert "docs/test-only" in t
    assert "does not repeat CLI execution" in t


def test_second_controlled_scenario_post_execution_boundary_qa_status_is_correct():
    t = read(QA_GATE_DOC)
    required = [
        "qa_status=PASS",
        "boundary_contract_status=PASS",
        "execution_status=PREFLIGHT_PASS",
        "execution_qa_status=PASS_WITH_OBSERVATION",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_validates_frozen_facts():
    t = read(QA_GATE_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "media_file_count=2",
        "accepted_extension_counts=.mov:1,.wav:1",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "maximum_detected_scan_depth=3",
        "total_selected_media_size_bucket=LE_100MB",
        "failed_check_identifiers=[]",
        "remediation_items=[]",
        "sanitized_input_folder_label=selected_input_folder",
        "sanitized_output_folder_label=selected_output_folder",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_preserves_observation():
    t = read(QA_GATE_DOC)
    required = [
        "ignored_extension_behavior_is_not_final=true",
        "rejected_extension_behavior_is_current_cli_behavior=true",
        "product_behavior_requires_later_dedicated_contract=true",
        "do not silently convert PASS_WITH_OBSERVATION into unconditional PASS",
        "keep ignored versus rejected extension behavior visible",
        "second controlled scenario line can be closed only with the observation preserved",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_privacy_boundary_is_strict():
    t = read(QA_GATE_DOC)
    required = [
        "no raw command output may be committed",
        "no raw evidence payload may be committed",
        "no private path may be committed",
        "no machine name may be committed",
        "no user name may be committed",
        "no concrete temporary folder name may be committed",
        "no concrete synthetic file name may be committed",
        "no project name may be committed",
        "no client name may be committed",
        "no stack trace may be committed",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_product_boundary_is_narrow():
    t = read(QA_GATE_DOC)
    required = [
        "proves only controlled synthetic Linux-only dry-run minimal preflight CLI execution with sanitized output",
        "does not prove scanner readiness",
        "does not prove media metadata extraction readiness",
        "does not prove ffprobe or ffmpeg readiness",
        "does not prove media probing or decoding readiness",
        "does not prove report generation readiness",
        "does not prove real production folder readiness",
        "does not prove real client deployment readiness",
        "does not prove ignored versus rejected extension product behavior",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_blocks_scope_expansion():
    t = read(QA_GATE_DOC)
    required = [
        "This QA gate does not authorize:",
        "real client media",
        "sensitive media",
        "personal data processing",
        "mounted Windows paths",
        "cloud-synced folders",
        "network shares",
        "scanner integration",
        "ffprobe or ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "edit decision output",
        "export",
        "upload",
        "desktop app",
        "installer",
        "licensing",
        "SaaS integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits",
        "ledger changes",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_allowed_next_step_is_limited():
    t = read(QA_GATE_DOC)
    required = [
        "close this second controlled scenario line as stable",
        "optionally prepare a later dedicated ignored-versus-rejected extension behavior contract",
        "no CLI execution unless explicitly authorized in a later phase",
        "no runtime change unless explicitly scoped in a later phase",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_upstream_boundary_supports_qa_gate():
    boundary = read(BOUNDARY_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "qa_status=PASS_WITH_OBSERVATION",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "ignored_extension_behavior_is_not_final=true",
        "product_behavior_requires_later_dedicated_contract=true",
        "this execution does not prove ignored versus rejected extension product behavior",
    ]
    for item in required:
        assert item in boundary


def test_second_controlled_scenario_upstream_execution_qa_supports_boundary_qa_gate():
    t = read(EXECUTION_QA_DOC)
    required = [
        "qa_status=PASS_WITH_OBSERVATION",
        "execution_status=PREFLIGHT_PASS",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "follow_up_required=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_upstream_execution_record_supports_boundary_qa_gate():
    t = read(EXECUTION_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_qa_private_tokens_are_absent():
    combined = (
        read(QA_GATE_DOC)
        + "\n"
        + read(BOUNDARY_DOC)
        + "\n"
        + read(EXECUTION_QA_DOC)
        + "\n"
        + read(EXECUTION_DOC)
    )
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["clip_alpha", "sound_alpha", "readme.txt", "reject_alpha"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in combined
