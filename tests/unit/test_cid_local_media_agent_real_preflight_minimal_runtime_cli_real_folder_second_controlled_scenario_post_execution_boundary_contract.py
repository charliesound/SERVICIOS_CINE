from pathlib import Path

BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_post_execution_boundary_contract_v1.md"
)
QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_qa_gate_v1.md"
)
EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_post_execution_boundary_docs_exist():
    assert BOUNDARY_DOC.exists()
    assert QA_DOC.exists()
    assert EXECUTION_DOC.exists()


def test_second_controlled_scenario_post_execution_boundary_phase_declared():
    t = read(BOUNDARY_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.POST.EXECUTION.BOUNDARY.CONTRACT.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.V1" in t
    assert "docs/test-only" in t
    assert "does not repeat CLI execution" in t


def test_second_controlled_scenario_post_execution_boundary_freezes_execution_facts():
    t = read(BOUNDARY_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "qa_status=PASS_WITH_OBSERVATION",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
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


def test_second_controlled_scenario_post_execution_boundary_freezes_observation():
    t = read(BOUNDARY_DOC)
    required = [
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
        "ignored_extension_behavior_is_not_final=true",
        "rejected_extension_behavior_is_current_cli_behavior=true",
        "product_behavior_requires_later_dedicated_contract=true",
        "this execution does not prove ignored versus rejected extension product behavior",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_accepts_only_limited_result():
    t = read(BOUNDARY_DOC)
    required = [
        "Linux-only temporary synthetic scenario was used",
        "dry-run-only execution was used",
        "sanitized result was recorded",
        "QA gate accepted the record only as PASS_WITH_OBSERVATION",
        "privacy and sanitization passed",
        "temporary data was cleaned up",
        "repository remained clean after execution",
        "no runtime code changed",
        "no scanner integration was added",
        "no media tooling was added",
        "no backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger changes were made",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_blocks_unauthorized_work():
    t = read(BOUNDARY_DOC)
    required = [
        "no real client media is authorized",
        "no sensitive media is authorized",
        "no personal data processing is authorized",
        "no mounted Windows path is authorized",
        "no cloud-synced folder is authorized",
        "no network share is authorized",
        "no scanner integration is authorized",
        "no ffprobe or ffmpeg use is authorized",
        "no media probing is authorized",
        "no media decoding is authorized",
        "no report generation is authorized",
        "no transcription is authorized",
        "no translation is authorized",
        "no subtitles are authorized",
        "no sync is authorized",
        "no edit decision output is authorized",
        "no export is authorized",
        "no upload is authorized",
        "no desktop app work is authorized",
        "no installer work is authorized",
        "no licensing work is authorized",
        "no SaaS integration is authorized",
        "no backend changes are authorized",
        "no frontend changes are authorized",
        "no database changes are authorized",
        "no Docker changes are authorized",
        "no Alembic changes are authorized",
        "no Stripe changes are authorized",
        "no AI Jobs changes are authorized",
        "no credits changes are authorized",
        "no ledger changes are authorized",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_privacy_boundary_is_strict():
    t = read(BOUNDARY_DOC)
    required = [
        "repository must not receive raw command output",
        "repository must not receive raw evidence payloads",
        "repository must not receive private paths",
        "repository must not receive machine names",
        "repository must not receive user names",
        "repository must not receive concrete temporary folder names",
        "repository must not receive concrete synthetic file names",
        "repository must not receive project names",
        "repository must not receive client names",
        "repository must not receive stack traces",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_product_boundary_is_narrow():
    t = read(BOUNDARY_DOC)
    required = [
        "this execution proves only that the current minimal preflight CLI can run against a controlled synthetic Linux-only dry-run scenario with sanitized output",
        "this execution does not prove scanner readiness",
        "this execution does not prove media metadata extraction readiness",
        "this execution does not prove ffprobe or ffmpeg readiness",
        "this execution does not prove media probing or decoding readiness",
        "this execution does not prove report generation readiness",
        "this execution does not prove real production folder readiness",
        "this execution does not prove real client deployment readiness",
        "this execution does not prove ignored versus rejected extension product behavior",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_follow_up_is_required():
    t = read(BOUNDARY_DOC)
    required = [
        "keep ignored versus rejected extension behavior visible",
        "do not silently convert PASS_WITH_OBSERVATION into unconditional PASS",
        "create a dedicated later contract if ignored extension behavior must be product-defined",
        "keep all future real-folder execution gated by explicit human authorization",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_post_execution_boundary_next_step_is_limited():
    t = read(BOUNDARY_DOC)
    required = [
        "second controlled scenario post execution boundary QA gate only",
        "no CLI execution",
        "no new temporary folder",
        "no runtime change",
        "no scanner integration",
        "no media tooling integration",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_upstream_docs_support_boundary_contract():
    qa = read(QA_DOC)
    execution = read(EXECUTION_DOC)
    required_qa = [
        "qa_status=PASS_WITH_OBSERVATION",
        "execution_status=PREFLIGHT_PASS",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "follow_up_required=true",
    ]
    required_execution = [
        "execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
    ]
    for item in required_qa:
        assert item in qa
    for item in required_execution:
        assert item in execution


def test_second_controlled_scenario_post_execution_boundary_private_tokens_are_absent():
    combined = read(BOUNDARY_DOC) + "\n" + read(QA_DOC) + "\n" + read(EXECUTION_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["clip_alpha", "sound_alpha", "readme.txt", "reject_alpha"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in combined
