from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_readiness_gate_v1.md"
SAFE_INTAKE_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_safe_intake_readiness_gate_v1.md"
SAFE_INTAKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_safe_intake_readiness_gate_v1.py"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_V1_CLOSED"
)
STARTING_HEAD = "af14cc8367e8a18a20881e765798020323fe4763"
STARTING_STATE = "REAL_MEDIA_SAFE_INTAKE_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_SAFE_INTAKE.READINESS.GATE.V1"
)
TARGET_NEXT_STATE = (
    "OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE"
)
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
        assert value in text


def test_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
        TARGET_NEXT_STATE,
    ])


def test_document_declares_scope() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is documentation-only and test-only.",
        "This phase does not use real media yet.",
        "This phase prepares a future test with operator-controlled real material, not client material.",
        "Real client material remains blocked.",
    ])


def test_document_declares_dry_run_conditions() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The future dry-run must be read-only.",
        "The future dry-run must use a working copy, not unique originals.",
        "The future dry-run must require explicit operator consent.",
        "The future dry-run must require an explicit and controlled local Linux path.",
        "The future dry-run must reject Windows paths, `/mnt` paths, UNC paths, and `wsl.localhost` paths.",
        "The future dry-run must reject ambiguous or non-absolute paths.",
        "The future dry-run must first be limited to a single file or small subfolder.",
        "The future dry-run must not delete, move, rename, or overwrite original material.",
        "The future dry-run must not upload material to the internet.",
        "The future dry-run must not touch SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        "The future dry-run must emit sanitized reports.",
        "The future dry-run must sanitize filenames, absolute paths, tokens, and sensitive metadata.",
        "The future dry-run must not execute ffmpeg or ffprobe except by explicit future phase.",
        "The future dry-run must not use subprocess except by explicit future phase.",
        "The future implementation gate must remain minimal and controlled.",
        "Use of real client material requires an explicit future `CLIENT_REAL_PILOT.READINESS.GATE` phase, not this one.",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [SAFE_INTAKE_DOC, SAFE_INTAKE_TEST]:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


def test_safe_intake_gate_feeds_this_readiness_gate() -> None:
    text = _text(SAFE_INTAKE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_SAFE_INTAKE.READINESS.GATE.V1",
    ])


def test_safe_intake_gate_test_exists() -> None:
    assert SAFE_INTAKE_TEST.exists()


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
