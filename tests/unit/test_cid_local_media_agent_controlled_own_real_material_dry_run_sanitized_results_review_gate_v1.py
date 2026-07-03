from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_sanitized_results_review_gate_v1.md"
RESULTS_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_results_review_readiness_gate_v1.md"
RESULTS_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_controlled_own_real_material_dry_run_results_review_readiness_gate_v1.py"
EXEC_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.md"
EXEC_TEST = ROOT / "tests/unit/test_cid_local_media_agent_controlled_own_real_material_dry_run_execution_gate_v1.py"
EXEC_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.md"
EXEC_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_execution_readiness_gate_v1.py"
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.md"
QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_qa_gate_v1.py"
IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md"
IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.py"
MODULE = ROOT / "scripts/local_media_agent/own_real_material_dry_run_intake.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.SANITIZED_RESULTS_REVIEW.GATE.V1"
STARTING_HEAD = "9d9d4573533e87ac635512517755c64fd62804e4"
STARTING_STATE = "CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_RESULTS_REVIEW_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED_OWN_REAL_MATERIAL.DRY_RUN.RESULTS_REVIEW.READINESS.GATE.V1"
TARGET_NEXT_STATE = "CONTROLLED_OWN_REAL_MATERIAL_DRY_RUN_SANITIZED_RESULTS_REVIEW_GATE_PASSED_READY_FOR_MANUAL_EXECUTION_RECORD_GATE"

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
    RESULTS_READINESS_DOC,
    RESULTS_READINESS_TEST,
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

# ---------------------------------------------------------------------------
# Synthetic fixtures — no real paths, no real filenames
# ---------------------------------------------------------------------------

ACCEPTED_FIXTURE_SANITIZED_LABEL = "SANITIZED_OWN_REAL_MATERIAL_INPUT"
SYNTHETIC_ACCEPTED_RESULT: dict[str, object] = {
    "status": "OWN_REAL_MATERIAL_DRY_RUN_INTAKE_ACCEPTED",
    "input_kind": "file",
    "accepted": True,
    "read_only": True,
    "operator_consent": True,
    "real_material_scope": "OWN_CONTROLLED_ONLY",
    "sanitized_input_label": ACCEPTED_FIXTURE_SANITIZED_LABEL,
    "errors": [],
    "warnings": [],
    "next_required_gate": "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.GATE.V1",
}

SYNTHETIC_REJECTED_RESULT: dict[str, object] = {
    "status": "OWN_REAL_MATERIAL_DRY_RUN_INTAKE_REJECTED",
    "input_kind": "unknown",
    "accepted": False,
    "read_only": True,
    "operator_consent": True,
    "real_material_scope": "OWN_CONTROLLED_ONLY",
    "sanitized_input_label": ACCEPTED_FIXTURE_SANITIZED_LABEL,
    "errors": ["INPUT_PATH_EMPTY"],
    "warnings": [],
    "next_required_gate": "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1",
}

UNSANITIZED_KEYS_FIXTURE: dict[str, object] = {
    "status": "OWN_REAL_MATERIAL_DRY_RUN_INTAKE_ACCEPTED",
    "accepted": True,
    "input_path": "/home/user/real_file.mov",
    "absolute_path": "/home/user/real_file.mov",
    "file_name": "real_file.mov",
    "filename": "real_file.mov",
    "source_path": "/home/user/real_file.mov",
    "real_path": "/home/user/real_file.mov",
    "sanitized_input_label": ACCEPTED_FIXTURE_SANITIZED_LABEL,
}


UNSANITIZED_KEYS: set[str] = {
    "input_path",
    "absolute_path",
    "file_name",
    "filename",
    "source_path",
    "real_path",
}

REQUIRED_KEYS: set[str] = {
    "status",
    "accepted",
    "sanitized_input_label",
    "errors",
    "warnings",
    "real_material_scope",
    "read_only",
    "operator_consent",
    "next_required_gate",
}


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
        "This phase reviews only synthetic sanitized fixtures.",
        "This phase does not review real results.",
        "This phase does not execute the planner.",
        "This phase does not use real material.",
        "This phase does not use client material.",
        "This phase does not ask for or store real paths.",
        "This phase does not read external operational logs.",
        "This phase does not create new runtime scripts.",
    ])


# ---------------------------------------------------------------------------
# Document review contract
# ---------------------------------------------------------------------------


def test_document_declares_review_contract() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The review accepts only a sanitized dict structure.",
    ])


def test_document_declares_required_fields() -> None:
    text = _text(DOC)
    for key in REQUIRED_KEYS:
        assert f"`{key}`" in text, f"Required key not found in doc: {key}"


def test_document_declares_sanitized_label() -> None:
    text = _text(DOC)
    assert "`SANITIZED_OWN_REAL_MATERIAL_INPUT`" in text


def test_document_declares_acceptance_conditions() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "`accepted=True`",
        "`read_only=True`",
        "`operator_consent=True`",
        "`real_material_scope=OWN_CONTROLLED_ONLY`",
        "`sanitized_input_label=SANITIZED_OWN_REAL_MATERIAL_INPUT`",
        "`errors=[]`",
    ])


def test_document_declares_rejection_conditions() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "A valid rejected result must preserve:",
        "`accepted=False`",
        "`status` indicating rejection",
        "`errors` non-empty or equivalent sanitized reason",
        "`sanitized_input_label=SANITIZED_OWN_REAL_MATERIAL_INPUT`",
    ])


def test_document_declares_no_rejection_to_acceptance_conversion() -> None:
    text = _text(DOC)
    assert "A planner rejection must never be converted to acceptance during review." in text


def test_document_declares_forbidden_content() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "a real absolute path",
        "a real filename",
        "Windows paths",
        "mount paths",
        "UNC paths",
        "wsl localhost paths",
        "`input_path`, `absolute_path`, `file_name`, `filename`, `source_path`, `real_path`",
    ])


def test_document_declares_no_media_operations() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The review must not infer video/audio metadata.",
        "The review must not open media.",
        "The review must not read bytes.",
        "The review must not execute ffmpeg, ffprobe, subprocess, or shell.",
        "The review must not create outputs on real material.",
        "The review must not upload anything to the internet.",
    ])


def test_document_declares_sanitized_evidence() -> None:
    text = _text(DOC)
    assert "Any versioned evidence must be sanitized." in text


def test_document_declares_client_real_blocked() -> None:
    text = _text(DOC)
    assert "Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`." in text


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
# Synthetic fixture validation
# ---------------------------------------------------------------------------


def test_accepted_fixture_has_all_required_keys() -> None:
    for key in REQUIRED_KEYS:
        assert key in SYNTHETIC_ACCEPTED_RESULT, f"Missing key in accepted fixture: {key}"


def test_accepted_fixture_has_correct_values() -> None:
    assert SYNTHETIC_ACCEPTED_RESULT["accepted"] is True
    assert SYNTHETIC_ACCEPTED_RESULT["read_only"] is True
    assert SYNTHETIC_ACCEPTED_RESULT["operator_consent"] is True
    assert SYNTHETIC_ACCEPTED_RESULT["real_material_scope"] == "OWN_CONTROLLED_ONLY"
    assert SYNTHETIC_ACCEPTED_RESULT["sanitized_input_label"] == ACCEPTED_FIXTURE_SANITIZED_LABEL
    assert SYNTHETIC_ACCEPTED_RESULT["errors"] == []


def test_accepted_fixture_contains_no_unsanitized_keys() -> None:
    for key in SYNTHETIC_ACCEPTED_RESULT:
        assert key not in UNSANITIZED_KEYS, f"Unsanitized key found in accepted fixture: {key}"


def test_accepted_fixture_contains_no_real_path() -> None:
    result_keys = " ".join(str(k) for k in SYNTHETIC_ACCEPTED_RESULT)
    result_values = " ".join(str(v) for v in SYNTHETIC_ACCEPTED_RESULT.values())
    combined = result_keys + " " + result_values
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
        "/" + "home",
        "/" + "Users",
        ".mov",
        ".mp4",
        ".avi",
        ".mkv",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined


def test_rejected_fixture_has_all_required_keys() -> None:
    for key in REQUIRED_KEYS:
        assert key in SYNTHETIC_REJECTED_RESULT, f"Missing key in rejected fixture: {key}"


def test_rejected_fixture_preserves_rejection() -> None:
    assert SYNTHETIC_REJECTED_RESULT["accepted"] is False
    assert isinstance(SYNTHETIC_REJECTED_RESULT["errors"], list)
    assert len(SYNTHETIC_REJECTED_RESULT["errors"]) > 0


def test_rejected_fixture_is_not_forcibly_accepted() -> None:
    modified = dict(SYNTHETIC_REJECTED_RESULT)
    modified["accepted"] = True
    assert modified["accepted"] is True
    assert SYNTHETIC_REJECTED_RESULT["accepted"] is False


# ---------------------------------------------------------------------------
# Unsanitized keys fixture validation
# ---------------------------------------------------------------------------


def test_unsanitized_keys_fixture_flagged_unsuitable() -> None:
    keys_present = set(UNSANITIZED_KEYS_FIXTURE.keys())
    unsanitized_found = keys_present & UNSANITIZED_KEYS
    assert len(unsanitized_found) > 0, "Unsanitized keys fixture should contain unsanitized keys"
    for key in unsanitized_found:
        assert key in UNSANITIZED_KEYS


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
