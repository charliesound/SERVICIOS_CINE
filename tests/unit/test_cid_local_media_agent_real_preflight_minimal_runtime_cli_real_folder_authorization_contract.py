from __future__ import annotations

from pathlib import Path
import subprocess


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1"

CLEAN_RECOVERY_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-readiness-gate-v1-postgresql-only-recovery-20260619"
CLEAN_RECOVERY_COMMIT = "2cf3d936b6f7f64cfd71bc9dc8e516f37adcd928"
SUPERSEDED_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-readiness-gate-v1-20260619"

PREVIOUS_FILES = [
    Path("scripts/cid_local_media_agent_real_preflight.py"),
    Path("scripts/cid_local_media_agent_real_preflight_cli.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_readiness_gate_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_readiness_gate.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract.py"),
]


def _doc() -> str:
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def _git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def test_contract_document_and_test_exist():
    assert DOC.exists()
    assert TEST.exists()
    assert PHASE in _doc()


def test_contract_is_docs_test_only_and_not_execution():
    text = _doc().lower()
    required = [
        "this phase is docs/test-only",
        "it does not execute the cli against a real folder",
        "it does not authorize a real-folder smoke invocation",
        "it does not authorize real client media",
        "the only purpose is to define what must be true",
    ]
    for item in required:
        assert item in text


def test_previous_prerequisite_files_exist():
    for path in PREVIOUS_FILES:
        assert path.exists(), path


def test_clean_recovery_tag_exists_and_points_to_expected_commit():
    tags = set(_git(["tag", "--list"]).splitlines())
    assert CLEAN_RECOVERY_TAG in tags
    assert _git(["rev-list", "-n", "1", CLEAN_RECOVERY_TAG]) == CLEAN_RECOVERY_COMMIT


def test_clean_recovery_tag_is_ancestor_of_head():
    head = _git(["rev-parse", "HEAD"])
    tag_commit = _git(["rev-list", "-n", "1", CLEAN_RECOVERY_TAG])
    assert _git(["merge-base", head, tag_commit]) == tag_commit


def test_superseded_tag_is_documented_as_not_clean_anchor():
    text = _doc()
    assert SUPERSEDED_TAG in text
    assert "superseded" in text.lower()
    assert "must not be used as the clean stable anchor" in text.lower()


def test_authorization_decision_states_are_documented():
    text = _doc()
    assert "`AUTHORIZATION_PASS`" in text
    assert "`AUTHORIZATION_FAIL`" in text
    assert "`AUTHORIZATION_BLOCKED`" in text


def test_required_human_authorization_fields_are_documented():
    text = _doc()
    required_fields = [
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
    for field in required_fields:
        assert field in text


def test_eligible_folder_class_requirements_are_documented():
    text = _doc().lower()
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


def test_real_media_policy_remains_conservative():
    text = _doc().lower()
    required = [
        "this authorization contract still does not authorize real media execution",
        "no real client media",
        "controlled non-sensitive real media",
        "sensitive real client media",
        "sensitive real client media remains blocked",
        "separate privacy review explicitly authorizes it",
    ]
    for item in required:
        assert item in text


def test_output_behavior_policy_remains_sanitized_and_no_write_by_default():
    text = _doc().lower()
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


def test_blocked_operations_remain_blocked():
    text = _doc().lower()
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


def test_later_required_gates_are_documented_before_execution():
    text = _doc()
    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.V1",
        "This contract alone does not authorize item 3.",
    ]
    for item in required:
        assert item in text


def test_repository_safety_requirements_are_documented():
    text = _doc().lower()
    required = [
        "the contract document must exist",
        "the contract test must exist",
        "the clean prerequisite recovery tag must exist",
        "protected files must not be staged",
        ".env` must not be staged",
        "database files must not be staged",
        "backup files must not be staged",
        "wsl/repository guard must pass",
        "postgresql-only regression guard must pass",
    ]
    for item in required:
        assert item in text


def test_document_does_not_reintroduce_bad_regression_guard_literal():
    text = _doc()
    assert "guard_no_" not in text


def test_acceptance_criteria_are_documented():
    text = _doc().lower()
    required = [
        "this authorization contract document exists",
        "this authorization contract test exists",
        "this phase is documented as docs/test-only",
        "this phase clearly states that it does not execute the cli against real folders",
        "the clean prerequisite recovery tag is documented",
        "the superseded readiness tag is documented as not the clean stable anchor",
        "all required human authorization fields are documented",
        "eligible folder class requirements are documented",
        "blocked folder classes are documented",
        "real media remains not authorized by this contract",
        "output behavior remains sanitized and no-write by default",
        "blocked operations remain blocked",
        "later required gates are documented",
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


def test_origin_main_is_not_ahead_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    origin_main = _git(["rev-parse", "origin/main"])
    assert _git(["merge-base", head, origin_main]) == origin_main
