from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_safe_intake_readiness_gate_v1.md"
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_qa_gate_v1.md"
QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_qa_gate_v1.py"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_SAFE_INTAKE.READINESS.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_SAFE_INTAKE_READINESS_GATE_V1_CLOSED"
)
STARTING_HEAD = "4a8488b014b6c9b9f97111001f30405eb4b94633"
STARTING_STATE = "CONTROLLED_SMOKE_QA_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION."
    "CONTROLLED_SMOKE.QA.GATE.V1"
)
TARGET_NEXT_STATE = (
    "REAL_MEDIA_SAFE_INTAKE_READINESS_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE"
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
        "This phase does not use real media.",
        "This phase does not implement new runtime.",
        "This phase does not modify the smoke script.",
        "This phase does not modify the CLI.",
        "This phase does not modify the exporter.",
        "This phase does not modify the renderer.",
        "This phase does not modify historical CLIs.",
        "This phase does not connect the real client flow.",
        "Real client material remains blocked.",
    ])


def test_document_declares_safe_intake_conditions() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The first real material allowed in future phases must be operator-controlled material, not client material.",
        "Any future test with real material must be read-only initially.",
        "Any future test must use a working copy, not unique originals.",
        "Any future test must require explicit operator consent.",
        "Any future test must require an explicit and controlled local path.",
        "Any future test must reject Windows paths, `/mnt` paths, UNC paths, and `wsl.localhost` paths.",
        "Any future test must reject ambiguous or non-absolute paths.",
        "Any future test must first be limited to a single file or small subfolder.",
        "Any future test must not delete, move, rename, or overwrite original material.",
        "Any future test must not upload material to the internet.",
        "Any future test must not touch SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        "Any future report must sanitize filenames, paths, tokens, and sensitive metadata.",
        "Any future extraction with ffprobe or ffmpeg requires an explicit future phase, not this one.",
        "Any future real folder reading requires an explicit future phase, not this one.",
        "Any future use with real client material requires an explicit `CLIENT_REAL_PILOT.READINESS.GATE` phase, not this one.",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [QA_DOC, QA_TEST]:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


def test_qa_gate_feeds_this_readiness_gate() -> None:
    qa = _text(QA_DOC)
    _assert_all_present(qa, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.CONTROLLED_SMOKE.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_QA_GATE_V1_CLOSED",
        "CONTROLLED_SMOKE_QA_GATE_PASSED_READY_FOR_REAL_MEDIA_SAFE_INTAKE_READINESS_GATE",
    ])


def test_qa_gate_test_exists() -> None:
    assert QA_TEST.exists()


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
