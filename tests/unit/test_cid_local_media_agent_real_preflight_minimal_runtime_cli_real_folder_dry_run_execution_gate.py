from __future__ import annotations

from pathlib import Path
import subprocess


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_execution_gate_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_execution_gate.py")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_readiness_gate_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_readiness_gate.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.GATE.V1"
READINESS_PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1"
STABLE_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-dry-run-readiness-gate-v1-20260619"
STABLE_COMMIT = "38401c4b7b79c3b1b14bc3bb8cbb53a89edfca16"


def _doc() -> str:
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def _readiness_doc() -> str:
    assert READINESS_DOC.exists()
    return READINESS_DOC.read_text(encoding="utf-8")


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.strip()


def test_execution_gate_document_and_test_exist():
    assert DOC.exists()
    assert TEST.exists()
    assert PHASE in _doc()


def test_readiness_prerequisite_files_exist():
    assert READINESS_DOC.exists()
    assert READINESS_TEST.exists()
    assert READINESS_PHASE in _readiness_doc()


def test_phase_is_docs_test_only_and_non_executing():
    text = _doc().lower()
    for item in [
        "this phase is docs/test-only",
        "it does not execute the cli",
        "it does not run against a real folder",
        "it does not authorize immediate execution",
        "this gate alone does not execute the command",
    ]:
        assert item in text


def test_stable_readiness_tag_exists_and_points_to_expected_commit():
    assert STABLE_TAG in set(_git(["tag", "--list"]).splitlines())
    assert _git(["rev-list", "-n", "1", STABLE_TAG]) == STABLE_COMMIT


def test_origin_main_is_not_ahead_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    origin_main = _git(["rev-parse", "origin/main"])
    assert _git(["merge-base", head, origin_main]) == origin_main


def test_execution_gate_decision_states_are_documented():
    text = _doc()
    for item in ["`EXECUTION_GATE_PASS`", "`EXECUTION_GATE_FAIL`", "`EXECUTION_GATE_BLOCKED`"]:
        assert item in text


def test_required_human_execution_authorization_fields_are_documented():
    text = _doc()
    for field in [
        "authorized_by_human",
        "authorization_timestamp",
        "authorized_phase",
        "execution_candidate_folder_class",
        "execution_candidate_folder_is_local_linux_only",
        "execution_candidate_folder_is_synthetic_or_non_sensitive",
        "execution_candidate_folder_contains_real_client_media",
        "execution_candidate_folder_contains_sensitive_media",
        "execution_candidate_folder_contains_personal_data",
        "execution_candidate_folder_is_not_repo_root",
        "execution_candidate_folder_is_not_home_root",
        "execution_candidate_folder_is_not_entire_disk",
        "execution_candidate_folder_is_not_mounted_windows_path",
        "execution_candidate_folder_is_not_under_mnt",
        "execution_candidate_folder_is_not_cloud_synced",
        "execution_candidate_folder_is_not_network_share",
        "execution_candidate_expected_file_count_range",
        "execution_candidate_expected_total_size_range",
        "execution_candidate_allowed_extensions",
        "execution_candidate_input_snapshot_confirmed",
        "execution_candidate_output_folder_empty_or_nonexistent",
        "execution_candidate_no_media_decoding",
        "execution_candidate_no_report_generation",
        "execution_candidate_no_scanner_integration",
        "execution_candidate_no_ffprobe_or_ffmpeg",
        "execution_candidate_no_network_access",
        "execution_candidate_expected_exit_codes",
        "execution_candidate_stop_conditions",
        "execution_candidate_rollback_plan",
    ]:
        assert field in text


def test_candidate_restrictions_are_documented():
    text = _doc().lower()
    for item in [
        "local linux folder visible inside wsl",
        "synthetic or non-sensitive",
        "contains no real client media",
        "contains no sensitive media",
        "contains no personal data",
        "not the repository root",
        "not a home directory root",
        "not the entire disk",
        "not a mounted windows path",
        "not under `/mnt/`",
        "not a /mnt/ path",
        "not a windows drive path",
        "not a cloud-synced directory",
        "not a network share",
        "not a backup folder",
        "not a database folder",
        "small, bounded number of files",
        "snapshotted before execution",
    ]:
        assert item in text


def test_command_template_and_allowed_behavior_are_documented():
    text = _doc()
    for item in [
        "python scripts/cid_local_media_agent_real_preflight_cli.py",
        "--input-folder",
        "--output-folder",
        "--max-file-count 25",
        "--max-total-size-bytes 104857600",
        "--max-scan-depth 3",
        "--accepted-extension .mp4",
        "--accepted-extension .mov",
        "--accepted-extension .wav",
        "--accepted-extension .mxf",
        "--format json",
        "--no-follow-symlinks",
        "<AUTHORIZED_LOCAL_LINUX_SYNTHETIC_OR_NON_SENSITIVE_FOLDER>",
        "<AUTHORIZED_LOCAL_LINUX_EMPTY_OUTPUT_FOLDER>",
    ]:
        assert item in text


def test_required_output_expectations_are_documented():
    text = _doc()
    for field in [
        "status",
        "sanitized_input_folder_label",
        "sanitized_output_folder_label",
        "media_file_count",
        "total_selected_media_size_bucket",
        "maximum_detected_scan_depth",
        "accepted_extension_counts",
        "ignored_extension_counts",
        "rejected_extension_counts",
        "failed_check_identifiers",
        "remediation_items",
        "exit_code",
    ]:
        assert field in text


def test_stop_conditions_are_documented():
    text = _doc().lower()
    for item in [
        "wsl/repository guard fails",
        "postgresql-only regression guard fails",
        "candidate folder is under `/mnt/`",
        "candidate folder is a /mnt/ path",
        "candidate folder is a mounted windows path",
        "candidate folder is a windows drive path",
        "candidate folder contains real client media",
        "candidate folder contains sensitive media",
        "candidate folder contains personal data",
        "output policy would write reports",
        "command would invoke scanner integration",
        "command would invoke ffprobe",
        "command would invoke ffmpeg",
        "command would decode media",
        "command would probe media bytes",
        "command would call a network service",
    ]:
        assert item in text


def test_no_bad_regression_guard_literal_is_reintroduced():
    forbidden = "guard" + "_no_"
    assert forbidden not in (_doc() + "\n" + _readiness_doc())


def test_previous_readiness_gate_still_blocks_execution():
    text = _readiness_doc().lower()
    for item in [
        "this phase is docs/test-only",
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder dry-run execution",
        "this readiness gate itself does not run that invocation",
    ]:
        assert item in text
