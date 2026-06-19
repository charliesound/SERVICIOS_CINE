from __future__ import annotations

from pathlib import Path
import subprocess


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_readiness_gate_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_readiness_gate.py")

RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
SMOKE_CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md")
SMOKE_CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract.py")
SMOKE_IMPLEMENTATION_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py")
SMOKE_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate_v1.md")
SMOKE_QA_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.READINESS.GATE.V1"
LATEST_STABLE_TAG = "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-qa-gate-v1-20260619"
LATEST_STABLE_COMMIT = "edb1600c87e34e0cff8ed830118f3214a48161c4"


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


def test_readiness_gate_document_and_test_exist():
    assert DOC.exists()
    assert TEST.exists()
    assert PHASE in _doc()


def test_readiness_gate_is_docs_test_only_and_not_execution_authorization():
    text = _doc().lower()
    required = [
        "this phase is docs/test-only",
        "it does not execute the cli against real folders",
        "it does not authorize real client media",
        "it does not authorize mounted windows paths",
        "it does not authorize cloud-synced folders",
        "it does not authorize network shares",
        "it does not authorize scanner integration",
        "it does not authorize ffprobe or ffmpeg",
        "it does not authorize report generation",
    ]
    for item in required:
        assert item in text


def test_required_local_files_exist():
    required_files = [
        RUNTIME_FILE,
        CLI_FILE,
        SMOKE_CONTRACT_DOC,
        SMOKE_CONTRACT_TEST,
        SMOKE_IMPLEMENTATION_TEST,
        SMOKE_QA_DOC,
        SMOKE_QA_TEST,
    ]
    for path in required_files:
        assert path.exists(), path


def test_latest_stable_tag_exists_and_points_to_expected_commit():
    tags = set(_git(["tag", "--list"]).splitlines())
    assert LATEST_STABLE_TAG in tags
    assert _git(["rev-list", "-n", "1", LATEST_STABLE_TAG]) == LATEST_STABLE_COMMIT


def test_latest_stable_tag_is_ancestor_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    tag_commit = _git(["rev-list", "-n", "1", LATEST_STABLE_TAG])
    merge_base = _git(["merge-base", head, tag_commit])
    assert merge_base == tag_commit


def test_origin_main_is_not_ahead_of_current_head():
    head = _git(["rev-parse", "HEAD"])
    origin_main = _git(["rev-parse", "origin/main"])
    merge_base = _git(["merge-base", head, origin_main])
    assert merge_base == origin_main


def test_prerequisite_phase_chain_is_documented():
    text = _doc()
    required_phases = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.QA.GATE.V1",
    ]
    for phase in required_phases:
        assert phase in text


def test_repository_prechecks_are_documented():
    text = _doc().lower()
    required = [
        "git status --short --untracked-files=all",
        "current `head` is known",
        "origin/main",
        "latest stable smoke/demo qa gate tag exists",
        "protected files are not staged",
        ".env is not staged",
        "database files are not staged",
        "backups are not staged",
        "guard_wsl_repo.sh",
        "postgresql-only regression guard",
    ]
    for item in required:
        assert item in text


def test_required_test_matrix_is_documented():
    text = _doc().lower()
    required = [
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


def test_privacy_boundary_is_documented():
    text = _doc().lower()
    required = [
        "synthetic temporary folders only",
        "synthetic placeholder files only",
        "no real client media",
        "no real project folders",
        "no raw private paths in cli output",
        "no raw filenames in cli output",
        "no client names in cli output",
        "no project names in cli output",
        "sanitized json output only",
        "sanitized text output only",
        "no selected output folder writes",
        "no selected input folder changes after fixture setup",
    ]
    for item in required:
        assert item in text


def test_explicit_non_authorization_is_documented():
    text = _doc().lower()
    required = [
        "real-folder smoke invocation",
        "real client media",
        "mounted windows paths",
        "/mnt/ paths",
        "c:\\ paths",
        "cloud-synced folders",
        "network shares",
        "scanner integration",
        "ffprobe",
        "ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "synthetic visible report integration",
        "transcription",
        "translation",
        "subtitle generation",
        "davinci resolve integration",
        "avid integration",
        "upload",
        "desktop app",
        "installer",
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


def test_allowed_readiness_decision_states_are_documented():
    text = _doc()
    assert "`READINESS_PASS`" in text
    assert "`READINESS_FAIL`" in text
    assert "`READINESS_BLOCKED`" in text


def test_smoke_demo_implementation_remains_synthetic_in_source():
    source = SMOKE_IMPLEMENTATION_TEST.read_text(encoding="utf-8").lower()
    required = [
        "tmp_path",
        "synthetic placeholder",
        "selected_input_folder",
        "selected_output_folder",
        "client_secret",
        "private_client",
        "json.loads",
    ]
    for item in required:
        assert item in source


def test_smoke_demo_qa_gate_remains_present_and_boundary_focused():
    source = SMOKE_QA_TEST.read_text(encoding="utf-8").lower()
    required = [
        "synthetic placeholder",
        "tmp_path",
        "import_boundary",
        "blocked_operation_terms",
        "does not add smoke/demo features",
        "does not widen cli scope",
        "does not use real client media",
        "does not process media content",
    ]
    for item in required:
        assert item in source


def test_acceptance_criteria_are_documented():
    text = _doc().lower()
    required = [
        "this readiness gate document exists",
        "this readiness gate test exists",
        "all prerequisite smoke/demo files exist",
        "the latest smoke/demo qa gate stable tag exists",
        "the latest smoke/demo qa gate stable tag is an ancestor of current `head`",
        "the prerequisite phase chain is documented",
        "the repository prechecks are documented",
        "the required test matrix is documented",
        "the privacy boundary is documented",
        "explicit non-authorization is documented",
        "blocked operations remain blocked",
        "previous smoke/demo qa gate tests still pass",
        "previous smoke/demo implementation tests still pass",
        "previous smoke/demo contract tests still pass",
        "previous cli tests still pass",
        "previous runtime tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
