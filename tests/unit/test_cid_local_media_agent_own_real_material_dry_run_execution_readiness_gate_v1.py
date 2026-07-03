from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.md"
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md"
QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py"
MODULE = ROOT / "scripts/local_media_agent/own_real_material_dry_run_intake.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.READINESS.GATE.V1"
STARTING_HEAD = "73633d5943837665eb4278425d89585b60107447"
STARTING_STATE = "OWN_REAL_MATERIAL_DRY_RUN_QA_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.QA.GATE.V1"
TARGET_NEXT_STATE = "OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_READINESS_GATE_PASSED_READY_FOR_CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_GATE"

# Forbidden fragments built via concatenation to avoid self-match
UNC_PREFIX = ("\\", "\\", "")
MNT_PREFIX = ("/", "mnt", "/")
WSL_DOMAIN = ("wsl", ".", "localhost")
WIN_DRIVE = ("C", ":", "\\")

EXCLUDED_RENDERER_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)
EXCLUDED_CLI_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text, f"Expected string not found: {value!r}"


# ---------------------------------------------------------------------------
# Document identity
# ---------------------------------------------------------------------------


def test_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
        TARGET_NEXT_STATE,
    ])


# ---------------------------------------------------------------------------
# Document scope
# ---------------------------------------------------------------------------


def test_document_declares_scope() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is documental/test-only.",
        "This phase prepares a future controlled execution, but does not execute it.",
        "This phase does not use real material yet.",
        "This phase does not use client material.",
        "This phase does not connect the real client flow.",
    ])


def test_document_declares_future_execution_conditions() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The future execution must use exclusively own/controlled material.",
        "The future execution must use a single explicit local Linux file, not a folder.",
        "The future execution must require `operator_consent=True`.",
        "The future execution must require `read_only=True`.",
        "The future execution must require `allow_real_material=True`.",
        "The future execution must use the audited planner: `plan_own_real_material_dry_run_intake`.",
        "The future execution must continue to not open video or audio files.",
        "The future execution must continue to not read media bytes.",
        "The future execution must continue to not use ffmpeg, ffprobe, subprocess, or shell.",
        "The future execution must not delete, move, rename, overwrite, or create outputs on real material.",
        "The future execution must not upload anything to the internet.",
        "The future execution must not touch scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        "The future execution must return only a sanitized report.",
        "The future execution must not return the full absolute path or the real filename as the final label.",
        "The future execution must return the fixed label: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.",
        "The future execution must stop if the planner returns a rejection.",
        "The future execution must document the real path used manually outside the repo, not inside Git.",
        "Use of real folders/subfolders requires an explicit future phase.",
        "Use of ffprobe/ffmpeg requires an explicit future phase.",
        "Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.",
    ])


# ---------------------------------------------------------------------------
# Excluded historical tests
# ---------------------------------------------------------------------------


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


# ---------------------------------------------------------------------------
# Required audited artifacts
# ---------------------------------------------------------------------------


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [QA_DOC, QA_TEST, MODULE]:
        assert path.exists(), f"Required artifact missing: {path}"
        rel = str(path.relative_to(ROOT))
        assert rel in text, f"Required artifact not referenced in doc: {rel}"


# ---------------------------------------------------------------------------
# Module existence and API
# ---------------------------------------------------------------------------


def test_module_exists_and_exposes_required_function() -> None:
    assert MODULE.exists()
    source = _text(MODULE)
    assert "plan_own_real_material_dry_run_intake" in source


# ---------------------------------------------------------------------------
# No Windows or mount paths in doc/test
# ---------------------------------------------------------------------------


def test_doc_and_test_contain_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(Path(__file__))
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined
