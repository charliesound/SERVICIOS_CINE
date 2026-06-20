from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_qa_gate_v1.md")
EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_v1.md")
EXECUTION_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_cli_execution.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    assert QA_GATE_DOC.exists()
    text = _text(QA_GATE_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.CLI.EXECUTION.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_EXECUTION_QA_GATE_PASS_READY_FOR_CONTROLLED_VISIBLE_REPORT_REVIEW" in text


def test_files_under_qa_exist() -> None:
    assert EXECUTION_DOC.exists()
    assert EXECUTION_TEST.exists()
    assert CLI_FILE.exists()
    assert RUNTIME_FILE.exists()

    text = _text(QA_GATE_DOC)
    required = [
        str(EXECUTION_DOC),
        str(EXECUTION_TEST),
        str(CLI_FILE),
        str(RUNTIME_FILE),
    ]
    for item in required:
        assert item in text


def test_source_traceability_is_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.CLI.EXECUTION.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_EXECUTION_PASS_READY_FOR_CONTROLLED_CLI_EXECUTION_QA_GATE",
        "db2bb4273636e5746909ad14a162db4ef37f9c20",
        "docs: record CID Local Media Agent controlled CLI execution",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-cli-execution-v1-20260620",
    ]

    for item in required:
        assert item in text


def test_controlled_input_and_output_boundaries_are_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "tests.unit.test_cid_local_media_agent_visible_report_runtime_generator._valid_scanner_result",
        "The input must not be real client material.",
        "The input must not come from a real scanner.",
        "The input must not come from media probing tools.",
        "05_reports/cid_local_media_agent_visible_report_v1.md",
        "The only authorized generated artifact",
        "The renderer must not generate editorial outputs.",
    ]

    for item in required:
        assert item in text


def test_local_only_privacy_and_roadmap_boundaries_are_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "original media left client system: false",
        "SaaS upload performed: false",
        "network call performed: false",
        "database write performed: false",
        "audio sync: not_generated",
        "transcription: not_generated",
        "subtitles: not_generated",
        "timeline exports: not_generated",
        "SaaS upload: not_generated",
        "database records: not_generated",
    ]

    for item in required:
        assert item in text


def test_non_goals_and_validation_evidence_are_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "real scanner implementation",
        "real media scanning",
        "media probing tool execution",
        "audio sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS upload",
        "database writes",
        "network calls",
        "frontend/backend SaaS changes",
        "public demo use",
        "client-facing demo use",
        "controlled CLI execution QA gate test passing",
        "controlled CLI execution record test passing",
        "CLI test passing",
        "CLI implementation QA gate passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate passing",
        "supporting implemented runtime chain tests passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
    ]

    for item in required:
        assert item in text


def test_direct_controlled_cli_execution_remains_reproducible(tmp_path: Path) -> None:
    input_root = tmp_path / "01_input"
    output_root = tmp_path / "02_output"
    input_root.mkdir()
    output_root.mkdir()

    scanner_json = input_root / "controlled_scanner_result.json"
    scanner_json.write_text(json.dumps(_valid_scanner_result(), indent=2, sort_keys=True), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CLI_FILE),
            "--scanner-result-json",
            str(scanner_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
    )

    report_path = output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    assert str(report_path) in result.stdout

    report_text = report_path.read_text(encoding="utf-8")
    required_report_items = [
        "# CID Local Media Agent - Controlled Visible Report",
        "Internal demo only. This report renders already-controlled scanner facts.",
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
        "Client-facing readiness: false.",
        "audio sync: not_generated",
        "transcription: not_generated",
        "subtitles: not_generated",
        "timeline exports: not_generated",
        "SaaS upload: not_generated",
        "database records: not_generated",
    ]

    for item in required_report_items:
        assert item in report_text


def test_qa_gate_does_not_claim_runtime_expansion() -> None:
    text = _text(QA_GATE_DOC)

    forbidden_claims = [
        "real scanner implemented",
        "media probing executed",
        "sync generated",
        "transcription generated",
        "subtitles generated",
        "DaVinci export generated",
        "Avid export generated",
        "client-facing ready",
        "SaaS integrated",
        "database write completed",
        "network upload completed",
    ]

    for item in forbidden_claims:
        assert item not in text
