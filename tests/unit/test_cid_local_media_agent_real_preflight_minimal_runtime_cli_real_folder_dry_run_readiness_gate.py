from __future__ import annotations

from pathlib import Path
import subprocess


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_readiness_gate_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_readiness_gate.py")

AUTH_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_qa_gate_v1.md")
AUTH_QA_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_qa_gate.py")
AUTH_CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract_v1.md")
AUTH_CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1"
AUTH_QA_PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1"
AUTH_CONTRACT_PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1"

STABLE_AUTH_QA_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-authorization-qa-gate-v1-20260619"
STABLE_AUTH_QA_COMMIT = "9cbcc9d8f05f79b27311518457dea23a1201fcb6"


def _doc() -> str:
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def _auth_qa_doc() -> str:
    assert AUTH_QA_DOC.exists()
    return AUTH_QA_DOC.read_text(encoding="utf-8")


def _auth_contract_doc() -> str:
    assert AUTH_CONTRACT_DOC.exists()
    return AUTH_CONTRACT_DOC.read_text(encoding="utf-8")


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def test_dry_run_readiness_document_and_test_exist():
    assert DOC.exists()
    assert TEST.exists()
    assert PHASE in _doc()


def test_authorization_prerequisite_files_exist():
    assert AUTH_QA_DOC.exists()
    assert AUTH_QA_TEST.exists()
    assert AUTH_CONTRACT_DOC.exists()
    assert AUTH_CONTRACT_TEST.exists()
    assert AUTH_QA_PHASE in _auth_qa_doc()
    assert AUTH_CONTRACT_PHASE in _auth_contract_doc()


def test_phase_is_docs_test_only_and_non_executing():
    text = _doc().lower()
    required = [
        "this phase is docs/test-only",
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder dry-run execution",
        "the only purpose is to prove",
        "this readiness gate itself does not run that invocation",
    ]
    for item in required:
        assert item in text


def test_stable_authorization_qa_tag_exists_and_points_to_expected_commit():
    tags = set(_git(["tag", "--list"]).splitlines())
    assert STABLE_AUTH_QA_TAG in tags
    assert _git(["rev-list", "-n", "1", STABLE_AUTH_QA_TAG]) == STABLE_AUTH_QA_COMMIT


def test_stable_authorization_qa_tag_is_ancestor_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    tag_commit = _git(["rev-list", "-n", "1", STABLE_AUTH_QA_TAG])
    assert _git(["merge-base", head, tag_commit]) == tag_commit


def test_origin_main_is_not_ahead_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    origin_main = _git(["rev-parse", "origin/main"])
    assert _git(["merge-base", head, origin_main]) == origin_main


def test_readiness_decision_states_are_documented():
    text = _doc()
    assert "`READINESS_PASS`" in text
    assert "`READINESS_FAIL`" in text
    assert "`READINESS_BLOCKED`" in text


def test_prerequisite_chain_is_documented():
    text = _doc()
    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.READINESS.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1",
        "The future execution phase is not part of this phase.",
    ]
    for item in required:
        assert item in text


def test_required_dry_run_candidate_record_fields_are_documented():
    text = _doc()
    required_fields = [
        "authorized_by_human",
        "authorization_timestamp",
        "authorized_phase",
        "dry_run_candidate_folder_class",
        "dry_run_candidate_folder_is_local_linux_only",
        "dry_run_candidate_folder_is_not_repo_root",
        "dry_run_candidate_folder_is_not_home_root",
        "dry_run_candidate_folder_is_not_mounted_windows_path",
        "dry_run_candidate_folder_is_not_under_mnt",
        "dry_run_candidate_folder_is_not_cloud_synced",
        "dry_run_candidate_folder_is_not_network_share",
        "dry_run_candidate_expected_file_count_range",
        "dry_run_candidate_expected_total_size_range",
        "dry_run_candidate_allowed_extensions",
        "dry_run_candidate_contains_real_client_media",
        "dry_run_candidate_contains_sensitive_media",
        "dry_run_candidate_contains_personal_data",
        "dry_run_candidate_input_snapshot_plan",
        "dry_run_candidate_output_behavior",
        "dry_run_candidate_no_media_decoding",
        "dry_run_candidate_no_report_generation",
        "dry_run_candidate_no_scanner_integration",
        "dry_run_candidate_no_ffprobe_or_ffmpeg",
        "dry_run_candidate_no_network_access",
        "dry_run_candidate_stop_conditions",
        "dry_run_candidate_rollback_plan",
    ]
    for field in required_fields:
        assert field in text


def test_candidate_class_restrictions_are_documented():
    text = _doc().lower()
    required = [
        "local linux folder visible inside wsl",
        "intentionally selected by the human operator",
        "not the repository root",
        "not a home directory root",
        "not the entire disk",
        "not a mounted windows path",
        "not under `/mnt/`",
        "not a /mnt/ path",
        "not a windows drive path",
        "not a cloud-synced directory",
        "not a network share",
        "not a production delivery folder",
        "not a backup folder",
        "not a database folder",
        "small, bounded number of files",
        "snapshotted before execution",
        "abandoned without business impact",
    ]
    for item in required:
        assert item in text


def test_later_dry_run_behavior_is_minimal_and_sanitized():
    text = _doc().lower()
    required = [
        "minimal cli preflight invocation",
        "local filesystem metadata checks only",
        "sanitized stdout",
        "sanitized stderr",
        "deterministic exit code mapping",
        "no selected output folder writes unless separately authorized",
        "no selected input folder changes",
        "no raw private path leakage",
        "no raw filename leakage",
        "no client name leakage",
        "no project name leakage",
        "no stack trace leakage",
    ]
    for item in required:
        assert item in text


def test_explicit_non_authorization_is_documented():
    text = _doc().lower()
    required = [
        "real-folder dry-run execution",
        "real-folder smoke invocation",
        "broad real project scan",
        "whole-disk scan",
        "real client media execution",
        "sensitive media execution",
        "mounted windows paths",
        "`/mnt/` paths",
        "/mnt/ paths",
        "windows drive paths",
        "cloud-synced folders",
        "network shares",
        "scanner integration",
        "ffprobe",
        "ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "visible report integration",
        "waveform analysis",
        "audio sync",
        "clap detection",
        "timecode extraction",
        "transcription",
        "translation",
        "subtitle generation",
        "davinci resolve integration",
        "avid integration",
        "edl generation",
        "xml generation",
        "aaf generation",
        "otio generation",
        "timeline generation",
        "upload",
        "cloud transfer",
        "desktop app",
        "installer",
        "packaging",
        "licensing activation",
        "saas integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "docker changes",
        "alembic changes",
        "stripe changes",
        "ai jobs changes",
        "credits changes",
        "ledger changes",
    ]
    for item in required:
        assert item in text


def test_required_test_matrix_is_documented():
    text = _doc().lower()
    required = [
        "real folder dry-run readiness gate",
        "real folder authorization qa gate",
        "real folder authorization contract",
        "smoke/demo readiness gate",
        "smoke/demo qa gate",
        "smoke/demo implementation",
        "smoke/demo contract",
        "cli qa gate",
        "cli implementation",
        "cli contract",
        "minimal runtime qa gate",
        "minimal runtime implementation",
        "minimal runtime contract",
        "wsl/repository guard",
        "postgresql-only regression guard",
    ]
    for item in required:
        assert item in text


def test_repository_safety_requirements_are_documented():
    text = _doc().lower()
    required = [
        "this readiness gate document must exist",
        "this readiness gate test must exist",
        "the real folder authorization qa gate document must exist",
        "the real folder authorization qa gate test must exist",
        "the real folder authorization contract document must exist",
        "the real folder authorization contract test must exist",
        "the latest real folder authorization qa gate stable tag must exist",
        "protected files must not be staged",
        ".env` must not be staged",
        "database files must not be staged",
        "backup files must not be staged",
        "wsl/repository guard must pass",
        "postgresql-only regression guard must pass",
    ]
    for item in required:
        assert item in text


def test_no_bad_regression_guard_literal_is_reintroduced():
    combined = _doc() + "\n" + _auth_qa_doc() + "\n" + _auth_contract_doc()
    assert "guard_no_" not in combined


def test_authorization_contract_still_blocks_execution():
    text = _auth_contract_doc().lower()
    required = [
        "it does not execute the cli against a real folder",
        "this authorization contract still does not authorize real media execution",
        "this contract alone does not authorize item 3",
        "sensitive real client media remains blocked",
    ]
    for item in required:
        assert item in text


def test_authorization_qa_gate_still_blocks_execution():
    text = _auth_qa_doc().lower()
    required = [
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder smoke invocation",
        "it does not authorize real client media",
        "the only purpose is to verify",
    ]
    for item in required:
        assert item in text


def test_acceptance_criteria_are_documented():
    text = _doc().lower()
    required = [
        "this dry-run readiness gate document exists",
        "this dry-run readiness gate test exists",
        "this phase is documented as docs/test-only",
        "this phase clearly states that it does not execute the cli against real folders",
        "this phase clearly states that it does not authorize dry-run execution",
        "the latest real folder authorization qa gate stable tag is documented",
        "the latest real folder authorization qa gate stable tag points to the expected commit",
        "the prerequisite chain is documented",
        "the required dry-run candidate record fields are documented",
        "eligible candidate class restrictions are documented",
        "dry-run behavior remains minimal and sanitized",
        "explicit non-authorization is documented",
        "blocked operations remain blocked",
        "the required test matrix is documented",
        "previous real folder authorization qa gate tests still pass",
        "previous real folder authorization contract tests still pass",
        "previous smoke/demo readiness tests still pass",
        "previous smoke/demo qa gate tests still pass",
        "previous smoke/demo implementation tests still pass",
        "previous smoke/demo contract tests still pass",
        "previous cli tests still pass",
        "previous runtime tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
