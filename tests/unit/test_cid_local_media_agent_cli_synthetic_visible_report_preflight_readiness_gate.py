from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_readiness_gate_v1.md"
CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_contract_v1.md"
CLI_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md"
CLI_IMPL_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"

CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
VERDICT = "READY_FOR_MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_IMPLEMENTATION_WITH_RESTRICTIONS"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists_and_declares_phase() -> None:
    text = _read(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.READINESS.GATE.V1" in text
    assert "documentation and test-only readiness gate" in text
    assert "does not implement preflight runtime behavior" in text
    assert VERDICT in text


def test_readiness_gate_reviews_expected_prior_artifacts() -> None:
    text = _read(READINESS_DOC)

    for path in [
        CONTRACT_DOC,
        CLI_QA_DOC,
        CLI_IMPL_DOC,
        CLI_SCRIPT,
        RENDERER_SCRIPT,
    ]:
        assert str(path.relative_to(REPO_ROOT)) in text
        assert path.exists()

    assert SCANNER_SCRIPT.exists()


def test_readiness_gate_authorizes_only_minimal_synthetic_local_preflight() -> None:
    text = _read(READINESS_DOC)

    allowed = [
        "Python standard library only",
        "Remain local-only",
        "Validate only synthetic fixture/report readiness",
        "Check the approved fixture path",
        "basic JSON readability",
        "Check the output directory contract",
        OUTPUT_FILENAME,
        "overwrite safety",
        "safe terminal output",
        "deterministic exit codes",
    ]

    for item in allowed:
        assert item in text


def test_readiness_gate_blocks_real_media_and_external_media_processing() -> None:
    text = _read(READINESS_DOC)

    blocked = [
        "read real media",
        "analyze real media",
        "synchronize audio/video",
        "transcribe audio",
        "translate dialogue",
        "generate subtitles",
        "export NLE files",
        "call external media probing binaries",
        "import or execute the scanner",
    ]

    for item in blocked:
        assert item in text


def test_readiness_gate_blocks_productization_and_saas_scope() -> None:
    text = _read(READINESS_DOC)

    blocked = [
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database runtime behavior",
        "Docker changes",
        "Alembic changes",
        "installer behavior",
        "licensing behavior",
        "upload client files",
        "packaging",
        "installable entry point wiring",
    ]

    for item in blocked:
        assert item in text


def test_readiness_gate_requires_safe_output_and_no_leakage() -> None:
    text = _read(READINESS_DOC)

    required = [
        "Avoid stack traces",
        "raw JSON",
        "absolute path leakage",
        "secrets",
        "environment values",
        "database strings",
        "network endpoint details",
        "client media paths",
    ]

    for item in required:
        assert item in text


def test_readiness_gate_requires_future_preflight_qa_coverage() -> None:
    text = _read(READINESS_DOC)

    required = [
        "PREFLIGHT_PASS",
        "PREFLIGHT_FAIL",
        "exit codes follow the preflight contract",
        "no generated report artifact is created by preflight",
        "no local absolute path is printed",
        "raw fixture JSON is not printed",
        "stack traces are not printed",
        "scanner is not imported or executed",
        "current renderer behavior remains unchanged",
        "current CLI report generation remains unchanged",
    ]

    for item in required:
        assert item in text


def test_preflight_contract_and_readiness_gate_are_consistent() -> None:
    contract = _read(CONTRACT_DOC)
    readiness = _read(READINESS_DOC)

    assert "PREFLIGHT_PASS" in contract
    assert "PREFLIGHT_FAIL" in contract
    assert "`0`: preflight passed" in contract
    assert "`2`: user input or contract validation failed" in contract
    assert "`3`: safe local environment validation failed" in contract
    assert "`4`: output safety validation failed" in contract
    assert "`1`: unexpected controlled failure" in contract

    assert "PREFLIGHT_PASS" in readiness
    assert "PREFLIGHT_FAIL" in readiness
    assert "deterministic exit codes" in readiness


def test_current_runtime_files_are_not_preflight_implementations_yet() -> None:
    cli_source = _read(CLI_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)

    assert "PREFLIGHT_PASS" not in cli_source
    assert "PREFLIGHT_FAIL" not in cli_source
    assert "--preflight" not in cli_source
    assert "preflight" not in cli_source.lower()

    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "preflight" not in renderer_source.lower()


def test_no_preflight_runtime_file_exists_yet() -> None:
    forbidden_runtime_files = [
        REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_preflight.py",
        REPO_ROOT / "scripts/cid_local_media_agent_preflight.py",
    ]

    for path in forbidden_runtime_files:
        assert not path.exists()
