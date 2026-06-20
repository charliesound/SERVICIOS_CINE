from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_readiness_v1.md")
INTERNAL_DEMO_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_readiness_v1.md")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
SCRIPT_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_qa_gate_v1.md")
SCRIPT_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation_qa_gate.py")
SCRIPT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_v1.md")
SCRIPT_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_second_machine_setup_readiness_doc_exists_and_declares_phase_and_result() -> None:
    assert READINESS_DOC.exists()
    text = _text(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.READINESS.V1" in text
    assert "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN" in text


def test_source_traceability_is_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "9c0f77127b12be387c1421b9e5f5620c8c0a8625",
        "docs: add CID Local Media Agent internal demo readiness",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-internal-demo-readiness-v1-20260620",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_READINESS",
    ]

    for item in required:
        assert item in text


def test_dependencies_exist() -> None:
    for path in [
        INTERNAL_DEMO_READINESS_DOC,
        INTERNAL_DEMO_READINESS_TEST,
        SCRIPT_QA_GATE_DOC,
        SCRIPT_QA_GATE_TEST,
        SCRIPT_DOC,
        SCRIPT_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_current_decision_and_second_machine_readiness_decision_are_declared() -> None:
    text = _text(READINESS_DOC)

    assert "READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY" in text
    assert "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY" in text
    assert "READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLANNING_ONLY" in text


def test_readiness_does_not_claim_installation_or_portability() -> None:
    text = _text(READINESS_DOC)

    required = [
        "does not mean installation has been tested",
        "does not mean the demo is portable",
        "does not mean there is a finished installer",
        "does not mean a client may receive the software",
    ]

    for item in required:
        assert item in text


def test_allowed_and_blocked_target_machines_are_declared() -> None:
    text = _text(READINESS_DOC)

    allowed = [
        "a machine owned or controlled by the project owner",
        "an internal development workstation",
        "an internal review workstation",
        "a controlled laptop used only for internal demo preparation",
        "a clean internal WSL environment",
        "a clean internal Linux environment",
    ]

    blocked = [
        "client computer",
        "productora computer",
        "school computer",
        "external producer computer",
        "investor computer",
        "sales event machine",
        "public demo machine",
        "production workstation with real media",
        "paid pilot machine",
        "unmanaged third-party machine",
    ]

    for item in allowed + blocked:
        assert item in text


def test_allowed_and_blocked_setup_purposes_are_declared() -> None:
    text = _text(READINESS_DOC)

    allowed = [
        "repository clone feasibility",
        "virtual environment creation",
        "dependency installation readiness",
        "controlled test execution",
        "controlled fixture availability",
        "direct CLI execution with controlled input",
        "visible report generation from controlled input",
        "local-only boundary messaging",
        "internal demo script consistency",
        "no real media dependency",
        "no network upload requirement",
        "no database write requirement",
    ]

    blocked = [
        "commercial installer readiness",
        "client installation readiness",
        "product distribution readiness",
        "public demo readiness",
        "sales demo readiness",
        "paid pilot readiness",
        "real scanner readiness",
        "real media processing readiness",
        "media probing readiness",
        "ffprobe execution readiness",
        "ffmpeg execution readiness",
        "sync readiness",
        "transcription readiness",
        "subtitle readiness",
        "timeline export readiness",
        "SaaS integration readiness",
        "license activation readiness",
    ]

    for item in allowed + blocked:
        assert item in text


def test_required_setup_boundaries_are_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "no real client files",
        "no production media",
        "no uncontrolled media folders",
        "no external uploads",
        "no database writes",
        "no SaaS connection",
        "no secret files copied",
        "no environment files copied",
        "no local database files copied",
        "no private client data copied",
        "no claim that this is an installer",
        "no claim that this is product-ready",
    ]

    for item in required:
        assert item in text


def test_allowed_and_blocked_setup_inputs_are_declared() -> None:
    text = _text(READINESS_DOC)

    allowed = [
        "repository checkout",
        "project source files",
        "controlled fixture JSON",
        "controlled visible report output folder",
        "Python virtual environment",
        "documented setup commands",
        "internal demo script",
        "internal disclaimer text",
    ]

    blocked = [
        "real client media",
        "production footage",
        "original camera files",
        "original sound files",
        "confidential script material",
        "private project data",
        "secret environment files",
        "local database files",
        "SaaS credentials",
        "license keys",
        "third-party customer data",
    ]

    for item in allowed + blocked:
        assert item in text


def test_required_setup_verification_is_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "repository path is controlled",
        "Python environment is isolated",
        "dependencies are installed from documented project requirements",
        "CLI help or direct execution works",
        "controlled fixture can generate a visible report",
        "generated report stays inside a controlled output folder",
        "generated report states client-facing readiness is false",
        "generated report states scanner execution by this renderer is false",
        "generated report states media probing by this renderer is false",
        "generated report states roadmap outputs are not generated",
        "local-only privacy language is visible",
        "internal-only disclaimer is visible",
    ]

    for item in required:
        assert item in text


def test_required_presenter_language_and_stop_conditions_are_declared() -> None:
    text = _text(READINESS_DOC)

    presenter_language = [
        "This is a controlled internal second-machine setup plan.",
        "This is not a commercial installer.",
        "This is not a client installation.",
        "This is not a finished product package.",
        "This is not a public demo.",
        "This is not a sales demo.",
        "This does not scan real media.",
        "This does not execute media probing tools.",
        "This does not execute ffprobe.",
        "This does not execute ffmpeg.",
        "This does not sync audio.",
        "This does not transcribe.",
        "This does not generate subtitles.",
        "This does not export timelines.",
        "This does not upload to SaaS.",
        "This does not write to a database.",
    ]

    stop_conditions = [
        "a client machine is proposed",
        "public demo use is proposed",
        "commercial installation is proposed",
        "product distribution is proposed",
        "real media is requested",
        "production footage is requested",
        "scanner execution is requested",
        "media probing execution is requested",
        "ffprobe or ffmpeg execution is requested",
        "sync output is requested",
        "transcription output is requested",
        "subtitle output is requested",
        "timeline export is requested",
        "SaaS upload is requested",
        "database write is requested",
        "license activation is requested",
        "installer signing is requested",
    ]

    for item in presenter_language + stop_conditions:
        assert item in text


def test_next_phase_boundary_is_declared() -> None:
    text = _text(READINESS_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.V1",
        "may create setup instructions for a controlled internal machine",
        "must not create an installer",
        "must not execute installation on a client machine",
        "must not package the product for distribution",
        "must not add real media capabilities",
    ]

    for item in required:
        assert item in text


def test_visible_report_generation_still_preserves_second_machine_readiness_boundaries(tmp_path: Path) -> None:
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
        "second machine setup readiness test passing",
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
