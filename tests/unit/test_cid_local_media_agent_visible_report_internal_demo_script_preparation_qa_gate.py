from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_qa_gate_v1.md")
SCRIPT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_v1.md")
SCRIPT_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation.py")
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


def test_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    assert QA_GATE_DOC.exists()
    text = _text(QA_GATE_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.INTERNAL.DEMO.SCRIPT.PREPARATION.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_SCRIPT_PREPARATION_QA_GATE_PASS_READY_FOR_INTERNAL_DEMO_READINESS" in text


def test_source_demo_script_preparation_traceability_is_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.INTERNAL.DEMO.SCRIPT.PREPARATION.V1",
        "3779962fdff0d06472f697a3b4d44447cb133368",
        "docs: prepare CID Local Media Agent internal demo script",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-internal-demo-script-preparation-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_SCRIPT_PREPARATION_PASS_READY_FOR_INTERNAL_DEMO_SCRIPT_PREPARATION_QA_GATE",
    ]

    for item in required:
        assert item in text


def test_files_under_qa_exist_and_are_declared() -> None:
    paths = [
        SCRIPT_DOC,
        SCRIPT_TEST,
        REVIEW_QA_GATE_DOC,
        REVIEW_QA_GATE_TEST,
        REVIEW_EXECUTION_DOC,
        REVIEW_EXECUTION_TEST,
        READINESS_DOC,
        READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]

    for path in paths:
        assert path.exists()

    text = _text(QA_GATE_DOC)
    for path in paths:
        assert str(path) in text


def test_review_decision_is_preserved() -> None:
    text = _text(QA_GATE_DOC)
    source_text = _text(SCRIPT_DOC)

    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in text
    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in source_text


def test_internal_scope_is_preserved() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "internal product review",
        "internal producer review",
        "development planning",
        "controlled internal progress explanation",
        "internal demo planning",
    ]

    for item in required:
        assert item in text


def test_external_scope_remains_blocked() -> None:
    text = _text(QA_GATE_DOC)

    blocked = [
        "client-facing demo",
        "public demo",
        "sales presentation",
        "investor claim",
        "finished product claim",
        "live production use",
        "production delivery",
        "client onboarding",
        "paid pilot",
        "product launch",
    ]

    for item in blocked:
        assert item in text


def test_allowed_claims_are_limited_to_internal_controlled_evidence() -> None:
    text = _text(QA_GATE_DOC)

    safe_claims = [
        "controlled JSON input can generate a producer-readable visible report",
        "direct CLI execution is proven",
        "local-only privacy boundaries are represented in the report",
        "unresolved warnings and human-review items remain visible",
        "roadmap modules are explicitly marked as not generated",
        "the current result is useful for internal product discussion",
    ]

    for item in safe_claims:
        assert item in text


def test_capability_overclaims_remain_blocked() -> None:
    text = _text(QA_GATE_DOC)

    blocked = [
        "real scanner implementation",
        "real media processing",
        "media probing execution",
        "ffprobe execution",
        "ffmpeg execution",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription generation",
        "subtitle generation",
        "translation generation",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS integration",
        "database write capability",
        "network upload capability",
        "client-facing readiness",
        "sales readiness",
    ]

    for item in blocked:
        assert item in text


def test_presenter_safe_language_is_required() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "this is an internal controlled demo artifact",
        "this is not client material",
        "this is not a finished media-processing product",
        "this does not scan real media",
        "this does not run media probing tools",
        "this does not sync audio",
        "this does not transcribe",
        "this does not create subtitles",
        "this does not export timelines",
        "this does not upload to SaaS",
        "this does not write to a database",
    ]

    for item in required:
        assert item in text


def test_producer_interpretation_and_next_step_boundary_are_safe() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "useful for internal product review",
        "producer-readable report",
        "controlled media-folder facts",
        "not yet useful as a client deliverable",
        "does not process real media",
        "does not generate editorial outputs",
        "internal-demo readiness",
        "controlled internal demo review",
        "must not be client demo, public demo, sales demo, SaaS integration, or real media implementation",
    ]

    for item in required:
        assert item in text


def test_visible_report_generation_still_preserves_internal_demo_boundaries(tmp_path: Path) -> None:
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
        "Client-facing readiness: false.",
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
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


def test_validation_evidence_is_declared() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "internal demo script preparation QA gate test passing",
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
