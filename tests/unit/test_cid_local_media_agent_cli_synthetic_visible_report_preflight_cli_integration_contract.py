from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_contract_v1.md"

PREFLIGHT_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_qa_gate_v1.md"
PREFLIGHT_IMPL_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_v1.md"
PREFLIGHT_READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_readiness_gate_v1.md"
PREFLIGHT_CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_contract_v1.md"
CLI_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md"
CLI_IMPL_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"

CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
VERDICT = "PREFLIGHT_CLI_INTEGRATION_CONTRACT_DEFINED_FOR_FUTURE_DEVELOPMENT_ONLY_MODE"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_integration_contract_document_exists_and_declares_phase() -> None:
    text = _read(CONTRACT_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.CONTRACT.V1" in text
    assert "documentation and test-only contract phase" in text
    assert "does not modify the current CLI wrapper" in text
    assert VERDICT in text
    assert "No runtime integration is authorized by this contract" in text


def test_integration_contract_references_current_components_and_prior_gates() -> None:
    text = _read(CONTRACT_DOC)

    for path in [
        PREFLIGHT_QA_DOC,
        PREFLIGHT_IMPL_DOC,
        PREFLIGHT_READINESS_DOC,
        PREFLIGHT_CONTRACT_DOC,
        CLI_QA_DOC,
        CLI_IMPL_DOC,
        CLI_SCRIPT,
        PREFLIGHT_SCRIPT,
        RENDERER_SCRIPT,
        SCANNER_SCRIPT,
    ]:
        assert path.exists(), path

    assert "scripts/cid_local_media_agent_synthetic_visible_report_cli.py" in text
    assert "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py" in text
    assert "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py" in text
    assert "scripts/cid_media_agent_scan.py" in text


def test_integration_contract_defines_future_preflight_mode_without_authorizing_it_now() -> None:
    text = _read(CONTRACT_DOC)

    assert "synthetic-visible-report --preflight --fixture <fixture-json> --output-dir <existing-dir> --format markdown [--allow-overwrite]" in text
    assert "development-only mode" in text
    assert "may delegate to the existing isolated helper" in text
    assert "--preflight is absent" in text
    assert "--preflight` is not implemented" in text
    assert "implementing the integration" in text
    assert "No runtime integration is authorized by this contract" in text


def test_integration_contract_requires_preserving_existing_generation_behavior() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "report generation behavior when `--preflight` is absent",
        "report generation mode remains unchanged when `--preflight` is absent",
        "existing allowed generation arguments continue to work",
        "--fixture",
        "--output-dir",
        "--format markdown",
        "--allow-overwrite",
        OUTPUT_FILENAME,
    ]

    for item in required:
        assert item in text


def test_integration_contract_requires_safe_preflight_mode_behavior() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "`--preflight` runs preflight only",
        "PREFLIGHT_PASS",
        "PREFLIGHT_FAIL",
        "deterministic exit codes from the preflight contract",
        "does not generate the Markdown report",
        "does not create output directories",
        "does not mutate fixtures",
        "does not leak absolute paths",
        "does not print raw fixture JSON",
        "does not print stack traces",
        "does not import or execute the scanner",
    ]

    for item in required:
        assert item in text


def test_integration_contract_blocks_sensitive_output_leakage() -> None:
    text = _read(CONTRACT_DOC)

    blocked_outputs = [
        "absolute local paths",
        "raw fixture JSON",
        "stack traces",
        "environment variables",
        "secrets",
        "database strings",
        "network endpoint details",
        "client media paths",
        "personal data",
    ]

    for item in blocked_outputs:
        assert item in text


def test_integration_contract_blocks_productization_and_real_media_scope() -> None:
    text = _read(CONTRACT_DOC)

    blocked = [
        "packaging",
        "installable command wiring",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database runtime behavior",
        "Docker changes",
        "Alembic changes",
        "external media probing binary execution",
        "real media analysis",
        "audio/video sync",
        "transcription",
        "translation",
        "subtitle generation",
        "NLE export",
        "installer behavior",
        "licensing behavior",
        "client media upload",
    ]

    for item in blocked:
        assert item in text


def test_runtime_sources_are_integrated_only_through_cli_after_implementation_phase() -> None:
    cli_source = _read(CLI_SCRIPT)
    preflight_source = _read(PREFLIGHT_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "--preflight" in cli_source
    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in cli_source
    assert "def _run_preflight" in cli_source
    assert "synthetic-visible-report-preflight" not in cli_source
    assert "PREFLIGHT_PASS" not in cli_source

    assert "synthetic-visible-report-preflight" in preflight_source
    assert "PREFLIGHT_PASS" in preflight_source
    assert "PREFLIGHT_FAIL" in preflight_source

    assert "synthetic-visible-report-preflight" not in renderer_source
    assert "synthetic-visible-report-preflight" not in scanner_source


def test_integration_contract_requires_readiness_gate_before_implementation() -> None:
    text = _read(CONTRACT_DOC)

    assert "Before implementation, a readiness gate" in text
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.READINESS.GATE.V1" in text
