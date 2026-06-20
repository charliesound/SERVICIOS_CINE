from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_v1.md")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_execution_record_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(EXECUTION_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.CLI.EXECUTION.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_EXECUTION_PASS_READY_FOR_CONTROLLED_CLI_EXECUTION_QA_GATE" in text


def test_execution_record_is_traceable_to_stable_source() -> None:
    text = _text(EXECUTION_DOC)
    assert "86745f992b477853468de8ff97e01124b144cf02" in text
    assert "fix: support direct execution for CID visible report runtime CLI" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-cli-direct-script-execution-fix-v1-20260620" in text


def test_controlled_input_output_and_evidence_are_recorded() -> None:
    text = _text(EXECUTION_DOC)
    required = [
        "python scripts/local_media_agent/visible_report_runtime_cli.py",
        "--scanner-result-json",
        "--output-root",
        "--print-output-path",
        "tests.unit.test_cid_local_media_agent_visible_report_runtime_generator._valid_scanner_result",
        "/tmp/cid_local_media_agent_controlled_cli_execution_v1/01_input/controlled_scanner_result.json",
        "/tmp/cid_local_media_agent_controlled_cli_execution_v1/02_output/05_reports/cid_local_media_agent_visible_report_v1.md",
        "CID Local Media Agent - Controlled Visible Report",
        "scanner status: completed_with_warnings",
        "candidate media count: 5",
        "accepted media count: 4",
        "rejected non-media count: 3",
        "human review required count: 1",
        "warnings count: 1",
        "ffprobe preflight: skipped",
    ]
    for item in required:
        assert item in text


def test_non_goals_remain_explicitly_blocked() -> None:
    text = _text(EXECUTION_DOC)
    non_goals = [
        "real media scanning",
        "scanner implementation",
        "ffprobe execution",
        "ffmpeg execution",
        "waveform sync",
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
        "public demo authorization",
        "client-facing demo authorization",
    ]
    for item in non_goals:
        assert item in text


def test_controlled_cli_execution_is_reproducible_from_direct_script(tmp_path: Path) -> None:
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
    assert "# CID Local Media Agent - Controlled Visible Report" in report_text
    assert "audio sync: not_generated" in report_text
    assert "transcription: not_generated" in report_text
    assert "subtitles: not_generated" in report_text
    assert "timeline exports: not_generated" in report_text
    assert "SaaS upload: not_generated" in report_text
    assert "database records: not_generated" in report_text


def test_execution_record_does_not_add_runtime_expansion_claims() -> None:
    text = _text(EXECUTION_DOC)
    forbidden_claims = [
        "real scanner implemented",
        "ffprobe executed",
        "ffmpeg executed",
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
