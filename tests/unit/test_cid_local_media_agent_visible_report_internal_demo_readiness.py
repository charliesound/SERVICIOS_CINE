from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_readiness_v1.md")
SCRIPT_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_qa_gate_v1.md")
SCRIPT_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation_qa_gate.py")
SCRIPT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_v1.md")
SCRIPT_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation.py")
REVIEW_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_controlled_review_execution_qa_gate_v1.md")
REVIEW_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_controlled_review_execution_qa_gate.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_internal_demo_readiness_doc_exists_and_declares_phase_and_result() -> None:
    assert READINESS_DOC.exists()
    text = _text(READINESS_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.INTERNAL.DEMO.READINESS.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_READINESS" in text


def test_source_traceability_is_declared() -> None:
    text = _text(READINESS_DOC)
    required = [
        "7cc4e6b67774291d233b6afe6f17ac20aa80196b",
        "test: add CID Local Media Agent internal demo script QA gate",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-internal-demo-script-preparation-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_SCRIPT_PREPARATION_QA_GATE_PASS_READY_FOR_INTERNAL_DEMO_READINESS",
    ]
    for item in required:
        assert item in text


def test_dependencies_exist() -> None:
    for path in [
        SCRIPT_QA_GATE_DOC,
        SCRIPT_QA_GATE_TEST,
        SCRIPT_DOC,
        SCRIPT_TEST,
        REVIEW_QA_GATE_DOC,
        REVIEW_QA_GATE_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_current_decision_and_readiness_decision_are_declared() -> None:
    text = _text(READINESS_DOC)
    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in text
    assert "READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY" in text


def test_allowed_and_blocked_audiences_are_declared() -> None:
    text = _text(READINESS_DOC)
    allowed = [
        "internal product owner",
        "internal producer reviewer",
        "internal development reviewer",
        "internal planning reviewer",
        "trusted internal technical reviewer",
    ]
    blocked = [
        "client",
        "productora",
        "school",
        "external producer",
        "investor",
        "sales lead",
        "public audience",
        "paid pilot user",
        "production user",
        "support user",
    ]
    for item in allowed + blocked:
        assert item in text


def test_allowed_and_blocked_demo_environments_are_declared() -> None:
    text = _text(READINESS_DOC)
    allowed = [
        "same controlled development machine",
        "controlled internal workstation",
        "local-only repository checkout",
        "controlled fixture input",
        "controlled output folder",
        "no real client material",
        "no production media",
        "no network upload",
        "no external service dependency",
        "no database write requirement",
    ]
    blocked = [
        "client computer",
        "public event computer",
        "sales laptop shown to client",
        "production workstation with real media",
        "shared machine with uncontrolled files",
        "cloud runner",
        "SaaS environment",
        "external demo booth",
        "school classroom machine",
        "productora machine",
    ]
    for item in allowed + blocked:
        assert item in text


def test_demo_can_show_only_controlled_report_flow() -> None:
    text = _text(READINESS_DOC)
    allowed = [
        "controlled JSON input",
        "direct CLI command",
        "generated visible report path",
        "producer-readable report structure",
        "accepted media list from controlled facts",
        "rejected non-media list from controlled facts",
        "human-review-required items from controlled facts",
        "warnings from controlled facts",
        "local-only privacy boundaries represented in the report",
        "roadmap modules marked as not generated",
        "internal demo script boundaries",
    ]
    for item in allowed:
        assert item in text


def test_required_presenter_boundary_language_is_declared() -> None:
    text = _text(READINESS_DOC)
    required = [
        "This is a controlled internal demo.",
        "This is not a client demo.",
        "This is not product delivery.",
        "This is not an installer.",
        "This is not a second-machine installation test.",
        "This does not scan real media.",
        "This does not run media probing tools.",
        "This does not execute ffprobe.",
        "This does not execute ffmpeg.",
        "This does not sync audio.",
        "This does not transcribe.",
        "This does not generate subtitles.",
        "This does not translate subtitles.",
        "This does not export timelines.",
        "This does not integrate with DaVinci Resolve.",
        "This does not integrate with Avid.",
        "This does not upload to SaaS.",
        "This does not write to a database.",
        "This does not prove commercial readiness.",
    ]
    for item in required:
        assert item in text


def test_demo_steps_and_stop_conditions_are_declared() -> None:
    text = _text(READINESS_DOC)
    required_steps = [
        "Show the phase and current status.",
        "Explain that the input is controlled fixture data.",
        "Run or describe the direct CLI command.",
        "Open the generated visible report.",
        "Walk through the executive summary.",
        "Show local-only privacy statements.",
        "Show accepted media, rejected non-media, warnings, and human-review items.",
        "Show roadmap modules marked as not generated.",
        "Close with the internal-only readiness decision.",
        "State the next safe technical step.",
    ]
    stop_conditions = [
        "real client files are requested",
        "real media folder execution is requested",
        "scanner execution is requested",
        "media probing execution is requested",
        "ffprobe or ffmpeg execution is requested",
        "sync output is requested",
        "transcription output is requested",
        "subtitle output is requested",
        "timeline export is requested",
        "SaaS upload is requested",
        "database write is requested",
        "client-facing packaging is requested",
        "installation on external machine is requested",
    ]
    for item in required_steps + stop_conditions:
        assert item in text


def test_required_screen_disclaimer_and_producer_interpretation_are_declared() -> None:
    text = _text(READINESS_DOC)
    required = [
        "Internal controlled demo only.",
        "not client-facing",
        "not production-ready",
        "not a finished Local Media Agent product",
        "renders controlled scanner-result data into a visible report",
        "does not process real media",
        "communication layer of CID Local Media Agent",
        "how the system can explain folder status to a producer",
        "how local-only privacy boundaries can be made visible",
        "how warnings and human-review items can be surfaced",
        "how unavailable roadmap capabilities can be explicitly marked as not generated",
        "not sufficient for customer validation",
    ]
    for item in required:
        assert item in text


def test_next_safe_phase_boundary_is_declared() -> None:
    text = _text(READINESS_DOC)
    required = [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.READINESS.V1",
        "may only prepare a second-machine internal setup plan",
        "must not create a commercial installer",
        "must not authorize client installation",
        "must not authorize public demo use",
        "must not authorize paid pilot use",
    ]
    for item in required:
        assert item in text


def test_visible_report_generation_still_preserves_demo_readiness_boundaries(tmp_path: Path) -> None:
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
    ]
    for item in required:
        assert item in report_text


def test_validation_evidence_is_declared() -> None:
    text = _text(READINESS_DOC)
    required = [
        "internal demo readiness test passing",
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
