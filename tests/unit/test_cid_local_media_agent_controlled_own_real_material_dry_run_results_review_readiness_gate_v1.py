from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_results_review_readiness_gate_v1.md"
EXEC_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.md"
EXEC_TEST = ROOT / "tests/unit/test_cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.py"
EXEC_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.md"
EXEC_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.py"
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md"
QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py"
IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md"
IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.py"
MODULE = ROOT / "scripts/local_media_agent/own_real_material_dry_run_intake.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.RESULTS_REVIEW.READINESS.GATE.V1"
STARTING_HEAD = "1afa0d8e7fc00caa1297d292ed86f3c4ca818f7f"
STARTING_STATE = "CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.GATE.V1"
TARGET_NEXT_STATE = "CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_RESULTS_REVIEW_READINESS_GATE_PASSED_READY_FOR_SANITIZED_RESULTS_REVIEW_GATE"

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

REQUIRED_ARTIFACTS = [
    EXEC_DOC,
    EXEC_TEST,
    EXEC_READINESS_DOC,
    EXEC_READINESS_TEST,
    QA_DOC,
    QA_TEST,
    IMPL_DOC,
    IMPL_TEST,
    MODULE,
]


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
        "This phase prepares the future review of the sanitized result.",
        "This phase does not review any real result yet.",
        "This phase does not execute the planner.",
        "This phase does not use real material.",
        "This phase does not use client material.",
        "This phase does not ask for or store real paths.",
        "This phase does not read external operational logs.",
    ])


def test_document_declares_review_contract() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The future review must accept only a sanitized result from the planner.",
        "The reviewable result must be a sanitized dict/structure.",
        "The reviewable result must include `status`.",
        "The reviewable result must include `accepted`.",
        "The reviewable result must include `sanitized_input_label`.",
        "The reviewable result must include `errors`.",
        "The reviewable result must include `warnings`.",
        "The reviewable result must include `real_material_scope`.",
        "The reviewable result must include `read_only`.",
        "The reviewable result must include `operator_consent`.",
        "The reviewable result must include `next_required_gate`.",
        "The only allowed label for input is: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.",
        "The reviewable result must not contain the real absolute path.",
        "The reviewable result must not contain the real filename.",
        "The reviewable result must not contain Windows paths.",
        "The reviewable result must not contain mount paths.",
        "The reviewable result must not contain UNC paths.",
        "The reviewable result must not contain wsl localhost paths.",
        "If the planner returns a rejection, the review must preserve the rejection and not force it to accepted.",
        "If the planner returns acceptance, the review must confirm:",
        "- `accepted=True`",
        "- `read_only=True`",
        "- `operator_consent=True`",
        "- `real_material_scope=OWN_CONTROLLED_ONLY`",
        "- `sanitized_input_label=SANITIZED_OWN_REAL_MATERIAL_INPUT`",
        "The future review must not infer video/audio metadata.",
        "The future review must not open media.",
        "The future review must not read bytes.",
        "The future review must not execute ffmpeg, ffprobe, subprocess, or shell.",
        "The future review must not create outputs on real material.",
        "The future review must not upload anything to the internet.",
        "Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.",
        "The real path used by the operator, if any, remains documented only outside the repo.",
        "Any versioned evidence must be sanitized.",
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
    for path in REQUIRED_ARTIFACTS:
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
