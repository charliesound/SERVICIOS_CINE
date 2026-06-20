from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_readiness_v1.md")
EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_v1.md")
QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_qa_gate_v1.md")
EXECUTION_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_cli_execution.py")
QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_cli_execution_qa_gate.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_doc_exists_and_declares_phase_and_result() -> None:
    assert READINESS_DOC.exists()
    text = _text(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTROLLED.REVIEW.READINESS.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTROLLED_REVIEW_READINESS_PASS_READY_FOR_CONTROLLED_VISIBLE_REPORT_REVIEW" in text


def test_readiness_is_traceable_to_current_stable_source() -> None:
    text = _text(READINESS_DOC)

    required = [
        "ea6d884bdd2eb22a4fc5416672e0beb6b1c32cb9",
        "test: add CID Local Media Agent controlled CLI execution QA gate",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-cli-execution-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_EXECUTION_QA_GATE_PASS_READY_FOR_CONTROLLED_VISIBLE_REPORT_REVIEW",
    ]

    for item in required:
        assert item in text


def test_files_under_readiness_review_exist_and_are_declared() -> None:
    for path in [
        EXECUTION_DOC,
        QA_GATE_DOC,
        EXECUTION_TEST,
        QA_GATE_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()

    text = _text(READINESS_DOC)
    for path in [
        EXECUTION_DOC,
        QA_GATE_DOC,
        EXECUTION_TEST,
        QA_GATE_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert str(path) in text


def test_review_readiness_criteria_are_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "producer-readable",
        "clear about local-only privacy",
        "clear about controlled synthetic input",
        "clear about scanner-result summary",
        "clear about accepted media",
        "clear about rejected non-media",
        "clear about human-review items",
        "clear about warnings",
        "clear about created output artifacts",
        "clear about roadmap modules not generated",
        "clear about producer interpretation",
        "clear about next technical actions",
    ]

    for item in required:
        assert item in text


def test_required_human_review_questions_are_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "Does the report explain what was actually generated?",
        "Does the report clearly avoid implying real media processing?",
        "Does the report preserve local-only privacy boundaries?",
        "Does the report expose warnings and unresolved human-review items?",
        "Does the report make clear that sync, transcription, subtitles, and timeline exports are not generated?",
        "Does the report read like a safe internal producer demo artifact?",
        "Does the report remain blocked for client-facing use?",
    ]

    for item in required:
        assert item in text


def test_controlled_visible_report_can_be_generated_for_review(tmp_path: Path) -> None:
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
    required = [
        "# CID Local Media Agent - Controlled Visible Report",
        "Internal demo only. This report renders already-controlled scanner facts.",
        "## Executive Summary",
        "## Local-Only Privacy Confirmation",
        "## Controlled Demo Input Summary",
        "## Scanner Result Summary",
        "## Accepted Media",
        "## Rejected Non-Media",
        "## Human Review Required",
        "## Warnings",
        "## Created Output Artifacts",
        "## Roadmap Modules Not Yet Generated",
        "## Producer Interpretation",
        "## Next Technical Actions",
    ]

    for item in required:
        assert item in report_text


def test_generated_report_preserves_internal_review_boundaries(tmp_path: Path) -> None:
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

    assert result.returncode == 0, result.stderr

    report_text = (output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md").read_text(encoding="utf-8")

    required = [
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
        "Client-facing readiness: false.",
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
        "The report must not be presented as sync, transcription, subtitle, or export output.",
    ]

    for item in required:
        assert item in report_text


def test_readiness_doc_does_not_authorize_runtime_expansion() -> None:
    text = _text(READINESS_DOC)

    forbidden_claims = [
        "real scanner implemented",
        "real media processed",
        "media probing executed",
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


def test_explicit_non_goals_and_validation_evidence_are_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "real scanner implementation",
        "real media scanning",
        "media probing tool execution",
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
        "public demo use",
        "client-facing demo use",
        "controlled visible report review readiness test passing",
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
