from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_readiness_gate_v1.md"
CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_contract_v1.md"

PREFLIGHT_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_qa_gate_v1.md"
PREFLIGHT_IMPL_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_v1.md"
CLI_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md"
CLI_IMPL_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"

CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

VERDICT = "READY_FOR_MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_CLI_INTEGRATION_WITH_RESTRICTIONS"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.IMPLEMENTATION.V1"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists_and_declares_verdict() -> None:
    text = _read(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.READINESS.GATE.V1" in text
    assert "documentation and test-only readiness gate" in text
    assert VERDICT in text
    assert NEXT_PHASE in text
    assert "strict restrictions" in text


def test_readiness_gate_dependencies_exist() -> None:
    for path in [
        READINESS_DOC,
        CONTRACT_DOC,
        PREFLIGHT_QA_DOC,
        PREFLIGHT_IMPL_DOC,
        CLI_QA_DOC,
        CLI_IMPL_DOC,
        CLI_SCRIPT,
        PREFLIGHT_SCRIPT,
        RENDERER_SCRIPT,
        SCANNER_SCRIPT,
    ]:
        assert path.exists(), path


def test_readiness_gate_reviews_contract_and_prior_validated_components() -> None:
    text = _read(READINESS_DOC)

    required = [
        "cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_contract_v1.md",
        "cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_qa_gate_v1.md",
        "cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_v1.md",
        "cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md",
        "cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md",
        "scripts/cid_local_media_agent_synthetic_visible_report_cli.py",
        "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py",
        "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py",
        "scripts/cid_media_agent_scan.py",
    ]

    for item in required:
        assert item in text


def test_readiness_gate_allows_only_minimal_future_wrapper_integration() -> None:
    text = _read(READINESS_DOC)

    required = [
        "Modify only the existing development wrapper",
        "scripts/cid_local_media_agent_synthetic_visible_report_cli.py",
        "Add a development-only `--preflight` mode",
        "Delegate preflight behavior to the existing helper",
        "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py",
        "Preserve current report generation behavior when `--preflight` is absent",
        OUTPUT_FILENAME,
    ]

    for item in required:
        assert item in text


def test_readiness_gate_requires_safe_integrated_preflight_behavior() -> None:
    text = _read(READINESS_DOC)

    required = [
        "`synthetic-visible-report --preflight` runs preflight only",
        "Success emits `PREFLIGHT_PASS`",
        "Controlled failure emits `PREFLIGHT_FAIL`",
        "Exit codes remain deterministic",
        "does not generate the Markdown report",
        "does not create output directories",
        "does not mutate fixture files",
        "does not import or execute the scanner",
        "Generation mode remains unchanged when `--preflight` is absent",
        "Unsupported real-media-like options remain rejected",
    ]

    for item in required:
        assert item in text


def test_readiness_gate_blocks_sensitive_output_leakage() -> None:
    text = _read(READINESS_DOC)

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


def test_readiness_gate_keeps_productization_and_real_media_blocked() -> None:
    text = _read(READINESS_DOC)

    blocked = [
        "packaging",
        "installable entry point wiring",
        "command registration",
        "changes to the preflight helper",
        "changes to the renderer",
        "changes to the scanner",
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

    assert "PREFLIGHT_PASS" in preflight_source
    assert "PREFLIGHT_FAIL" in preflight_source
    assert "synthetic-visible-report-preflight" in preflight_source

    assert "--preflight" not in renderer_source
    assert "synthetic-visible-report-preflight" not in renderer_source

    assert "--preflight" not in scanner_source
    assert "synthetic-visible-report-preflight" not in scanner_source


def test_contract_and_readiness_gate_are_consistent() -> None:
    contract = _read(CONTRACT_DOC)
    readiness = _read(READINESS_DOC)

    shared_requirements = [
        "development-only",
        "`--preflight`",
        "PREFLIGHT_PASS",
        "PREFLIGHT_FAIL",
        "does not generate the Markdown report",
        "does not create output directories",
        "does not import or execute the scanner",
        "absolute local paths",
        "raw fixture JSON",
        "stack traces",
        "client media paths",
        "No runtime integration is authorized by this contract",
    ]

    for item in shared_requirements:
        assert item in contract
        assert item in readiness or item == "No runtime integration is authorized by this contract"

    assert "This gate authorizes a future implementation phase" in readiness
    assert NEXT_PHASE in readiness


def test_next_phase_is_implementation_but_not_packaging_or_real_media() -> None:
    text = _read(READINESS_DOC)

    assert NEXT_PHASE in text
    assert "must remain minimal" in text
    assert "must not open packaging" in text
    assert "installable entry point wiring" in text
    assert "scanner integration" in text
    assert "SaaS integration" in text
    assert "real media processing" in text
