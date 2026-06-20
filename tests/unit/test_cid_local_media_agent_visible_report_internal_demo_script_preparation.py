from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


SCRIPT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_v1.md")
REVIEW_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_execution_qa_gate_v1.md")
REVIEW_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_execution_qa_gate.py")
REVIEW_EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_execution_v1.md")
REVIEW_EXECUTION_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_execution.py")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_readiness_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_internal_demo_script_doc_exists_and_declares_phase_and_result() -> None:
    assert SCRIPT_DOC.exists()
    text = _text(SCRIPT_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.INTERNAL.DEMO.SCRIPT.PREPARATION.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_SCRIPT_PREPARATION_PASS_READY_FOR_INTERNAL_DEMO_SCRIPT_PREPARATION_QA_GATE" in text


def test_source_traceability_is_declared() -> None:
    text = _text(SCRIPT_DOC)

    required = [
        "cc3b000b74b3ba3ed215c6753f098cc89c4bc8ae",
        "test: add CID Local Media Agent controlled visible report review execution QA gate",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-controlled-review-execution-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTROLLED_REVIEW_EXECUTION_QA_GATE_PASS_READY_FOR_INTERNAL_DEMO_SCRIPT_PREPARATION",
    ]

    for item in required:
        assert item in text


def test_dependencies_exist() -> None:
    for path in [
        REVIEW_QA_GATE_DOC,
        REVIEW_QA_GATE_TEST,
        REVIEW_EXECUTION_DOC,
        REVIEW_EXECUTION_TEST,
        READINESS_DOC,
        READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_review_decision_is_preserved() -> None:
    text = _text(SCRIPT_DOC)
    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in text


def test_script_purpose_and_audience_are_declared() -> None:
    text = _text(SCRIPT_DOC)

    required = [
        "what has been built",
        "what is proven",
        "what is only controlled fixture data",
        "what is not yet implemented",
        "internal product review",
        "internal producer review",
        "development planning",
        "controlled internal progress explanation",
    ]

    for item in required:
        assert item in text


def test_not_intended_audience_is_blocked() -> None:
    text = _text(SCRIPT_DOC)

    blocked = [
        "client-facing demo",
        "public demo",
        "sales presentation",
        "investor claim",
        "finished product claim",
        "live production use",
    ]

    for item in blocked:
        assert item in text


def test_demo_structure_is_declared() -> None:
    text = _text(SCRIPT_DOC)

    required = [
        "Section 1 - Context",
        "Section 2 - What Is Proven",
        "Section 3 - What The Report Shows",
        "Section 4 - What Must Be Said Clearly",
        "Section 5 - What Can Be Claimed",
        "Section 6 - What Cannot Be Claimed",
        "Section 7 - Producer Interpretation",
        "Section 8 - Closing Statement",
        "5 to 7 minutes",
    ]

    for item in required:
        assert item in text


def test_safe_claims_and_blocked_claims_are_declared() -> None:
    text = _text(SCRIPT_DOC)

    safe_claims = [
        "controlled JSON input can generate a producer-readable visible report",
        "direct CLI execution is proven",
        "local-only privacy boundaries are represented in the report",
        "unresolved warnings and human-review items remain visible",
        "roadmap modules are explicitly marked as not generated",
        "the current result is useful for internal product discussion",
    ]

    blocked_claims = [
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

    for item in safe_claims + blocked_claims:
        assert item in text


def test_presenter_safe_script_contains_required_boundary_language() -> None:
    text = _text(SCRIPT_DOC)

    required = [
        "This is not a client demo",
        "not a finished media-processing product",
        "does not scan real media",
        "does not run media probing tools",
        "does not sync audio",
        "does not transcribe",
        "does not create subtitles",
        "does not export timelines",
        "does not upload to SaaS",
        "does not write to a database",
        "blocked for clients, public demo, sales, and production claims",
    ]

    for item in required:
        assert item in text


def test_visible_report_can_still_be_generated_for_internal_script_context(tmp_path: Path) -> None:
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

    report_text = report_path.read_text(encoding="utf-8")
    required = [
        "# CID Local Media Agent - Controlled Visible Report",
        "Internal demo only. This report renders already-controlled scanner facts.",
        "Client-facing readiness: false.",
        "audio sync: not_generated",
        "transcription: not_generated",
        "subtitles: not_generated",
        "timeline exports: not_generated",
        "SaaS upload: not_generated",
        "database records: not_generated",
    ]

    for item in required:
        assert item in report_text


def test_validation_evidence_is_declared() -> None:
    text = _text(SCRIPT_DOC)

    required = [
        "internal demo script preparation test passing",
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
