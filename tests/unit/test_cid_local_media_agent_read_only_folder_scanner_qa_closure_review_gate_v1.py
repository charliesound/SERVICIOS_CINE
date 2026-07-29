from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_qa_closure_review_gate_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_closure_review_gate_v1.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.CLOSURE.REVIEW.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_QA_CLOSURE_REVIEW_GATE_V1_CLOSED"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.READINESS.GATE.V1"

READINESS_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.READINESS.GATE.V1"
IMPLEMENTATION_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1"
FIX_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.RUNTIME_LIMITS.FAIL_CLOSED_FIX.GATE.V1"
QA_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1"

COMMITS = [
    "7c5b3db759ae9f588905d5673c8c13c1f7244d38",
    "d53da68a49c853a343b2f5ba41aa7408944bd4e7",
    "8b51e1cf8dd5f7ae02f4118eef7ac9776be9b1e9",
    "fb8b82eb375370d7aca271846ac181cf9736ba9b",
]

TAGS = [
    "cid-dev-stable-local-media-agent-read-only-folder-scanner-readiness-gate-v1-20260729",
    "cid-dev-stable-local-media-agent-read-only-folder-scanner-implementation-gate-v1-20260729",
    "cid-dev-stable-local-media-agent-read-only-folder-scanner-runtime-limits-fail-closed-fix-gate-v1-20260729",
    "cid-dev-stable-local-media-agent-read-only-folder-scanner-qa-gate-v1-20260729",
]

DEFECTIVE_SHA = "9a10c9dba6d60b359ac5a4c06901b6c9313450ae727f2fb2cb3d761f707bf2fc"
CORRECTED_SHA = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"

AUTHORIZED_FILES = [
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_qa_closure_review_gate_v1.md",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_closure_review_gate_v1.py",
]


def _text() -> str:
    assert DOC.exists(), f"missing doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def _assert_all_present(values: list[str]) -> None:
    text = _text()
    for value in values:
        assert value in text, f"missing expected value: {value!r}"


def test_phase_identity_expected_result_and_files_exist() -> None:
    assert DOC.exists()
    assert TEST.exists()
    _assert_all_present([PHASE, EXPECTED_RESULT])


def test_scope_is_exactly_two_authorized_files() -> None:
    _assert_all_present(AUTHORIZED_FILES)
    _assert_all_present([
        "This phase is documentation-only and QA traceability-only.",
        "This phase does not modify runtime, existing tests, packaging, or project configuration.",
        "This phase is limited to exactly two files:",
    ])


def test_all_required_phases_are_present() -> None:
    _assert_all_present([READINESS_PHASE, IMPLEMENTATION_PHASE, FIX_PHASE, QA_PHASE, PHASE])


def test_all_required_commits_are_present() -> None:
    _assert_all_present(COMMITS)


def test_all_required_tags_are_present() -> None:
    _assert_all_present(TAGS)


def test_defective_and_corrected_runtime_sha_are_present() -> None:
    _assert_all_present([DEFECTIVE_SHA, CORRECTED_SHA])
    assert DEFECTIVE_SHA != CORRECTED_SHA


def test_defect_and_fix_are_documented() -> None:
    _assert_all_present([
        "`MAX_FILES=0` did not fail closed.",
        "The defective runtime SHA was:",
        "The corrected runtime SHA is:",
        "The fix added defensive limit validation before input validation and traversal.",
    ])


def test_final_qa_evidence_is_documented() -> None:
    _assert_all_present([
        "`READ_ONLY_FOLDER_SCANNER_QA_GATE_V1_CLOSED`",
        "82 tests PASS",
        "DB guard PASS",
        "runtime SHA intact",
        "`test_max_files_zero_is_blocked_or_fails_controlled` preserved and PASS",
        "no runtime modified during QA",
    ])


def test_closed_runtime_capability_boundaries_are_documented() -> None:
    _assert_all_present([
        "local Linux read-only folder scanner engine",
        "stdlib-only",
        "does not follow symlinks",
        "`lstat` plus `stat.S_ISLNK`, `stat.S_ISDIR`, and `stat.S_ISREG`",
        "does not read file contents",
        "does not compute hashes",
        "does not use ffprobe",
        "does not use ffmpeg",
        "does not use subprocess",
        "does not use shell execution",
        "does not use network access",
        "does not use DB",
        "does not use SaaS",
        "does not write artifacts",
        "sanitized manifest",
        "fail-closed runtime limits",
        "does not process real material",
        "does not expose a CLI yet",
        "not production-ready yet",
    ])


def test_runtime_cli_and_packaging_remain_prohibited() -> None:
    _assert_all_present([
        "This phase does not modify `scripts/local_media_agent/read_only_folder_scanner.py`.",
        "This phase does not modify `pyproject.toml`.",
        "This phase does not create a CLI, `cid scan`, entrypoints, packaging",
        "backend, frontend, DB, SaaS, Docker, Alembic, Stripe, auth, AI Jobs, or ledger",
    ])


def test_next_allowed_phase_is_cli_readiness_only() -> None:
    _assert_all_present([
        "The next allowed phase is:",
        NEXT_PHASE,
        "must not reinterpret this closure as public CLI, production, SaaS, or customer deployment authorization",
    ])
