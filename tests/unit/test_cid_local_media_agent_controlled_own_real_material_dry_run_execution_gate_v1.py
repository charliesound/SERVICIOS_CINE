from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.md"
EXEC_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.md"
EXEC_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.py"
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md"
QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py"
IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md"
IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.py"
MODULE = ROOT / "scripts/local_media_agent/own_real_material_dry_run_intake.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.GATE.V1"
STARTING_HEAD = "c6c0e95b4c335acf0958bb15731de900786824af"
STARTING_STATE = "OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.READINESS.GATE.V1"
TARGET_NEXT_STATE = "CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_EXECUTION_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_RESULTS_REVIEW_GATE"

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
        "This phase defines the controlled manual execution protocol, but does not execute real material.",
        "This phase does not use client material.",
        "This phase does not connect the real client flow.",
        "No new runtime scripts are created.",
        "The planner `own_real_material_dry_run_intake.py` is not modified.",
    ])


def test_document_declares_execution_protocol() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The future manual execution must use the audited planner directly: `plan_own_real_material_dry_run_intake`.",
        "The future manual execution is allowed only with own/controlled material.",
        "The future manual execution requires a single explicit local Linux file, not a folder.",
        "The future manual execution does not allow folders.",
        "The future manual execution does not allow Windows paths.",
        "The future manual execution does not allow `/mnt` paths.",
        "The future manual execution does not allow UNC paths.",
        "The future manual execution does not allow `wsl.localhost` paths.",
        "The future manual execution requires `operator_consent=True`.",
        "The future manual execution requires `read_only=True`.",
        "The future manual execution requires `allow_real_material=True`.",
        "The real path must be supplied outside Git as `CID_OPERATOR_REAL_MATERIAL_INPUT_PATH`.",
        "The real path must never be written to versioned files.",
        "The real path must be documented only in a local operational note outside the repo.",
        "Any registrable result in the repo, if any in a future phase, must be sanitized.",
        "The sanitized result must not contain the full absolute path.",
        "The sanitized result must not contain the real filename as the final label.",
        "The allowed label is: `SANITIZED_OWN_REAL_MATERIAL_INPUT`.",
        "The future execution stops if the planner returns a rejection.",
        "The planner does not open video or audio files.",
        "The planner does not read media bytes.",
        "The planner does not execute ffmpeg, ffprobe, subprocess, or shell.",
        "The planner does not delete, move, rename, overwrite, or create outputs on real material.",
        "Nothing is uploaded to the internet.",
        "Scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, and ledger are not touched.",
        "Use of real folders/subfolders requires an explicit future phase.",
        "Use of ffprobe/ffmpeg requires an explicit future phase.",
        "Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.",
        "The risk of a future manual execution with own real material is low and bounded because only superficial path validation is performed, not content reading.",
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
