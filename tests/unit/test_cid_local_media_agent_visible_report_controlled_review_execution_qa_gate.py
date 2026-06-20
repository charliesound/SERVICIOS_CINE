from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_execution_qa_gate_v1.md")
REVIEW_EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_execution_v1.md")
REVIEW_EXECUTION_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_execution.py")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_readiness_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_readiness.py")
CLI_EXECUTION_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_qa_gate_v1.md")
CLI_EXECUTION_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_cli_execution_qa_gate.py")
CLI_EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_cli_execution_v1.md")
CLI_EXECUTION_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_cli_execution.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    assert QA_GATE_DOC.exists()
    text = _text(QA_GATE_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTROLLED.REVIEW.EXECUTION.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTROLLED_REVIEW_EXECUTION_QA_GATE_PASS_READY_FOR_INTERNAL_DEMO_SCRIPT_PREPARATION" in text


def test_source_review_execution_traceability_is_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTROLLED.REVIEW.EXECUTION.V1",
        "595dd5acd76cb4313bd5080ffd4069303c3bb21d",
        "docs: record CID Local Media Agent controlled visible report review execution",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-controlled-review-execution-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTROLLED_REVIEW_EXECUTION_PASS_READY_FOR_CONTROLLED_REVIEW_EXECUTION_QA_GATE",
    ]

    for item in required:
        assert item in text


def test_files_under_qa_exist_and_are_declared() -> None:
    paths = [
        REVIEW_EXECUTION_DOC,
        REVIEW_EXECUTION_TEST,
        READINESS_DOC,
        READINESS_TEST,
        CLI_EXECUTION_QA_GATE_DOC,
        CLI_EXECUTION_QA_GATE_TEST,
        CLI_EXECUTION_DOC,
        CLI_EXECUTION_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]

    for path in paths:
        assert path.exists()

    text = _text(QA_GATE_DOC)
    for path in paths:
        assert str(path) in text


def test_internal_review_decision_is_preserved() -> None:
    text = _text(QA_GATE_DOC)
    source_text = _text(REVIEW_EXECUTION_DOC)

    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in text
    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in source_text
    assert "acceptable only for controlled internal review and internal producer discussion" in text


def test_authorized_internal_uses_are_preserved() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "controlled internal review",
        "internal producer discussion",
        "development progress evidence",
        "controlled demo-script preparation",
    ]

    for item in required:
        assert item in text


def test_client_facing_and_commercial_use_remain_blocked() -> None:
    text = _text(QA_GATE_DOC)

    blocked = [
        "client-facing demo",
        "public demo",
        "sales presentation",
        "production claim",
        "real media-processing claim",
        "sync deliverable claim",
        "transcription deliverable claim",
        "subtitle deliverable claim",
        "timeline export claim",
        "SaaS integration claim",
    ]

    for item in blocked:
        assert item in text


def test_runtime_expansion_boundaries_are_preserved() -> None:
    text = _text(QA_GATE_DOC)

    blocked = [
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
    ]

    for item in blocked:
        assert item in text


def test_generated_visible_report_still_preserves_boundaries(tmp_path: Path) -> None:
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


def test_human_review_findings_are_declared_stable() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "report explains what was actually generated",
        "report avoids implying real media processing",
        "report preserves local-only privacy boundaries",
        "report exposes warnings and unresolved human-review items",
        "report makes clear that sync, transcription, subtitles, and timeline exports are not generated",
        "report reads like a safe internal producer demo artifact",
        "report remains blocked for client-facing use",
    ]

    for item in required:
        assert item in text


def test_qa_gate_does_not_authorize_runtime_or_commercial_expansion() -> None:
    text = _text(QA_GATE_DOC)

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
        "sales ready",
    ]

    for item in forbidden_claims:
        assert item not in text


def test_validation_evidence_is_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "controlled visible report review execution QA gate test passing",
        "controlled visible report review execution test passing",
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
