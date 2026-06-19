from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_contract_v1.md"
CLI_IMPLEMENTATION_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"
CLI_QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md"

CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preflight_contract_document_exists_and_declares_phase() -> None:
    text = _read(CONTRACT_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CONTRACT.V1" in text
    assert "documentation and test-only phase" in text
    assert "does not implement preflight runtime behavior" in text
    assert "PREFLIGHT_CONTRACT_DEFINED_FOR_FUTURE_SYNTHETIC_VISIBLE_REPORT_ONLY" in text
    assert "No runtime implementation is authorized by this contract" in text


def test_preflight_contract_references_current_audited_cli_without_modifying_runtime() -> None:
    text = _read(CONTRACT_DOC)

    assert "scripts/cid_local_media_agent_synthetic_visible_report_cli.py" in text
    assert "synthetic-visible-report" in text
    assert "--fixture" in text
    assert "--output-dir" in text
    assert "--allow-overwrite" in text
    assert "--format markdown" in text
    assert OUTPUT_FILENAME in text

    assert CLI_IMPLEMENTATION_DOC.exists()
    assert CLI_QA_DOC.exists()
    assert CLI_SCRIPT.exists()
    assert RENDERER_SCRIPT.exists()
    assert SCANNER_SCRIPT.exists()


def test_preflight_contract_defines_allowed_future_checks_only_for_synthetic_workflow() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "fixture argument is present",
        "fixture path exists",
        "parsed as JSON",
        "minimum fields required by the synthetic Markdown renderer",
        "output directory argument is present",
        "output directory is a directory",
        "output filename is exactly",
        "does not already exist unless overwrite is explicitly allowed",
        "requested format is exactly `markdown`",
        "renderer script exists",
        "scanner script is not imported or executed",
        "No real media path is accepted",
    ]

    for item in required:
        assert item in text


def test_preflight_contract_defines_safe_terminal_output_and_exit_codes() -> None:
    text = _read(CONTRACT_DOC)

    assert "PREFLIGHT_PASS" in text
    assert "PREFLIGHT_FAIL" in text
    assert "short stable reason code" in text
    assert "synthetic/local-first notice" in text
    assert "human review notice" in text

    assert "`0`: preflight passed" in text
    assert "`2`: user input or contract validation failed" in text
    assert "`3`: safe local environment validation failed" in text
    assert "`4`: output safety validation failed" in text
    assert "`1`: unexpected controlled failure" in text


def test_preflight_contract_blocks_path_secret_and_client_media_leakage() -> None:
    text = _read(CONTRACT_DOC)

    blocked_outputs = [
        "absolute local paths",
        "raw fixture JSON",
        "stack traces",
        "environment variables",
        "secrets",
        "client media paths",
        "personal data",
        "database connection information",
        "network endpoint details",
    ]

    for blocked in blocked_outputs:
        assert blocked in text


def test_preflight_contract_blocks_runtime_integrations_and_real_media_scope() -> None:
    text = _read(CONTRACT_DOC)

    blocked = [
        "implementing the preflight command",
        "adding CLI arguments",
        "changing the current CLI wrapper",
        "changing the renderer",
        "changing the scanner",
        "adding packaging",
        "installable entry point wiring",
        "backend or frontend integration",
        "database runtime behavior",
        "Docker or Alembic changes",
        "calling external media probing binaries",
        "reading real media files",
        "synchronizing audio and video",
        "transcribing audio",
        "translating dialogue",
        "generating subtitle files",
        "exporting to NLE formats",
        "installer behavior",
        "licensing behavior",
        "uploading client files",
    ]

    for item in blocked:
        assert item in text


def test_preflight_contract_keeps_human_review_and_assistive_cid_boundaries() -> None:
    text = _read(CONTRACT_DOC)

    assert "synthetic demo artifact requiring human review" in text
    assert "CID remains assistive" in text
    assert "does not replace the producer" in text
    assert "editor" in text
    assert "assistant editor" in text
    assert "post supervisor" in text
    assert "human reviewer" in text


def test_preflight_contract_does_not_modify_current_cli_source_contract() -> None:
    source = _read(CLI_SCRIPT)

    assert "COMMAND_NAME = \"synthetic-visible-report\"" in source
    assert "OUTPUT_FILENAME = \"cid_local_media_agent_synthetic_visible_report_v1.md\"" in source

    assert "--preflight" in source
    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in source
    assert "def _run_preflight" in source
    assert "synthetic-visible-report-preflight" not in source
    assert "PREFLIGHT_PASS" not in source
    assert "PREFLIGHT_FAIL" in source
    assert "reason=UNEXPECTED_CONTROLLED_FAILURE" in source
    assert "cid_media" + "_agent_scan" not in source


def test_preflight_contract_does_not_introduce_new_runtime_files() -> None:
    staged_runtime_candidates = [
        REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_preflight.py",
        REPO_ROOT / "scripts/cid_local_media_agent_preflight.py",
    ]

    for path in staged_runtime_candidates:
        assert not path.exists()
