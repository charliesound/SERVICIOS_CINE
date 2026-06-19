from __future__ import annotations

from pathlib import Path
import subprocess


QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_qa_gate_v1.md")
QA_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_qa_gate.py")

CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract_v1.md")
CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1"
CONTRACT_PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1"
STABLE_CONTRACT_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-authorization-contract-v1-20260619"
STABLE_CONTRACT_COMMIT = "0f31ac90c86d9daa7ebb066d0a89d51baa6f0e73"
SUPERSEDED_READINESS_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-readiness-gate-v1-20260619"


def _qa_doc() -> str:
    assert QA_DOC.exists()
    return QA_DOC.read_text(encoding="utf-8")


def _contract_doc() -> str:
    assert CONTRACT_DOC.exists()
    return CONTRACT_DOC.read_text(encoding="utf-8")


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def test_qa_gate_document_and_test_exist():
    assert QA_DOC.exists()
    assert QA_TEST.exists()
    assert PHASE in _qa_doc()


def test_contract_document_and_test_exist():
    assert CONTRACT_DOC.exists()
    assert CONTRACT_TEST.exists()
    assert CONTRACT_PHASE in _contract_doc()


def test_qa_gate_is_docs_test_only_and_non_executing():
    text = _qa_doc().lower()
    required = [
        "this phase is docs/test-only",
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder smoke invocation",
        "it does not authorize real client media",
        "the only purpose is to verify",
    ]
    for item in required:
        assert item in text


def test_stable_contract_tag_exists_and_points_to_expected_commit():
    tags = set(_git(["tag", "--list"]).splitlines())
    assert STABLE_CONTRACT_TAG in tags
    assert _git(["rev-list", "-n", "1", STABLE_CONTRACT_TAG]) == STABLE_CONTRACT_COMMIT


def test_stable_contract_tag_is_ancestor_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    tag_commit = _git(["rev-list", "-n", "1", STABLE_CONTRACT_TAG])
    assert _git(["merge-base", head, tag_commit]) == tag_commit


def test_origin_main_is_not_ahead_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    origin_main = _git(["rev-parse", "origin/main"])
    assert _git(["merge-base", head, origin_main]) == origin_main


def test_qa_gate_decision_states_are_documented():
    text = _qa_doc()
    assert "`QA_PASS`" in text
    assert "`QA_FAIL`" in text
    assert "`QA_BLOCKED`" in text


def test_contract_authorization_states_remain_documented():
    text = _contract_doc()
    assert "`AUTHORIZATION_PASS`" in text
    assert "`AUTHORIZATION_FAIL`" in text
    assert "`AUTHORIZATION_BLOCKED`" in text


def test_contract_is_verified_as_non_executing():
    text = _contract_doc().lower()
    required = [
        "this phase is docs/test-only",
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder smoke invocation",
        "this authorization contract still does not authorize real media execution",
        "this contract alone does not authorize item 3",
    ]
    for item in required:
        assert item in text


def test_superseded_readiness_tag_remains_documented():
    text = _contract_doc()
    assert SUPERSEDED_READINESS_TAG in text
    assert "superseded" in text.lower()
    assert "must not be used as the clean stable anchor" in text.lower()


def test_required_human_authorization_fields_are_verified():
    text = _contract_doc()
    fields = [
        "authorized_by_human",
        "authorization_timestamp",
        "authorized_phase",
        "approved_folder_purpose",
        "approved_folder_location_class",
        "approved_folder_contains_real_client_media",
        "approved_folder_contains_sensitive_media",
        "approved_folder_contains_personal_data",
        "approved_expected_file_count_range",
        "approved_expected_total_size_range",
        "approved_allowed_extensions",
        "approved_output_behavior",
        "approved_no_media_decoding",
        "approved_no_report_generation",
        "approved_no_network_access",
        "approved_no_scanner_integration",
        "approved_no_ffprobe_or_ffmpeg",
        "approved_rollback_plan",
        "approved_stop_conditions",
    ]
    for field in fields:
        assert field in text


def test_folder_class_restrictions_are_verified():
    text = _contract_doc().lower()
    required = [
        "local linux folder visible inside wsl",
        "intentionally selected by the human operator",
        "not the entire disk",
        "not the repository root",
        "not a home directory root",
        "not a cloud-synced directory",
        "not a network share",
        "not a mounted windows path",
        "not under `/mnt/`",
        "not a windows drive path",
        "not a production delivery folder",
        "not a backup folder",
        "not a database folder",
        "small, bounded number of files",
        "snapshotted before the dry-run",
    ]
    for item in required:
        assert item in text


def test_real_media_policy_remains_not_authorized():
    text = _contract_doc().lower()
    required = [
        "this authorization contract still does not authorize real media execution",
        "sensitive real client media remains blocked",
        "separate privacy review explicitly authorizes it",
    ]
    for item in required:
        assert item in text


def test_output_policy_remains_sanitized_and_no_write_by_default():
    text = _contract_doc().lower()
    required = [
        "no report generation",
        "no selected output folder writes unless separately authorized",
        "sanitized stdout only",
        "sanitized stderr only",
        "no raw private path leakage",
        "no raw filename leakage",
        "no client name leakage",
        "no project name leakage",
        "no stack trace leakage",
        "deterministic exit codes only",
    ]
    for item in required:
        assert item in text


def test_path_and_folder_blocks_are_verified_by_qa_doc():
    text = _qa_doc().lower()
    required = [
        "entire disk",
        "repository root",
        "home directory root",
        "mounted windows path",
        "`/mnt/` path",
        "/mnt/ path",
        "windows drive path",
        "cloud-synced directory",
        "network share",
        "production delivery folder",
        "backup folder",
        "database folder",
    ]
    for item in required:
        assert item in text


def test_operation_blocks_remain_in_contract():
    text = _contract_doc().lower()
    blocked = [
        "real-folder smoke invocation",
        "broad real project scan",
        "whole-disk scan",
        "mounted windows paths",
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
    for item in blocked:
        assert item in text


def test_later_required_gates_remain_before_execution():
    text = _contract_doc()
    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.V1",
        "This contract alone does not authorize item 3.",
    ]
    for item in required:
        assert item in text


def test_no_bad_regression_guard_literal_is_reintroduced():
    combined = _qa_doc() + "\n" + _contract_doc()
    assert "guard_no_" not in combined


def test_repository_safety_requirements_are_documented():
    text = _qa_doc().lower()
    required = [
        "this qa gate document must exist",
        "this qa gate test must exist",
        "the authorization contract document must exist",
        "the authorization contract test must exist",
        "the latest authorization contract stable tag must exist",
        "protected files must not be staged",
        ".env` must not be staged",
        "database files must not be staged",
        "backup files must not be staged",
        "wsl/repository guard must pass",
        "postgresql-only regression guard must pass",
    ]
    for item in required:
        assert item in text


def test_acceptance_criteria_are_documented():
    text = _qa_doc().lower()
    required = [
        "this qa gate document exists",
        "this qa gate test exists",
        "this phase is documented as docs/test-only",
        "this phase clearly states that it does not execute the cli against real folders",
        "the authorization contract document exists",
        "the authorization contract test exists",
        "the clean stable authorization contract tag is documented",
        "the clean stable authorization contract tag points to the expected commit",
        "the authorization contract is verified as non-executing",
        "all required authorization fields are verified",
        "eligible folder restrictions are verified",
        "blocked folder classes are verified",
        "real media remains not authorized by the contract",
        "output behavior remains sanitized and no-write by default",
        "blocked operations remain blocked",
        "later required gates are verified",
        "previous authorization contract tests still pass",
        "previous readiness gate tests still pass",
        "previous smoke/demo qa gate tests still pass",
        "previous smoke/demo implementation tests still pass",
        "previous smoke/demo contract tests still pass",
        "previous cli tests still pass",
        "previous runtime tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
