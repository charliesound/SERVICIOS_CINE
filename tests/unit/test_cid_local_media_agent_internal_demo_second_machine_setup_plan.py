from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_v1.md")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_readiness_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_readiness_v1.md")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
SCRIPT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_script_preparation_v1.md")
SCRIPT_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_script_preparation.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_second_machine_setup_plan_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN_QA_GATE",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "bccd5c794f8fa293e68964fbf9fbab05533ed6c8",
        "docs: add CID Local Media Agent second machine setup readiness",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-readiness-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN",
    ])


def test_dependencies_exist() -> None:
    for path in [
        READINESS_DOC,
        READINESS_TEST,
        INTERNAL_DEMO_READINESS_DOC,
        INTERNAL_DEMO_READINESS_TEST,
        SCRIPT_DOC,
        SCRIPT_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_current_decisions_and_plan_decision_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLANNING_ONLY",
        "READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY",
        "APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY",
        "CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLAN_ONLY",
    ])


def test_plan_does_not_claim_execution_or_installer_status() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "does not mean the setup has been executed",
        "does not mean the setup has passed on another machine",
        "does not mean there is a portable installer",
        "does not mean there is a client installer",
        "does not mean the product is ready for sales or public demonstration",
    ])


def test_target_machine_profile_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "project-owner controlled machine",
        "internal development laptop",
        "internal review laptop",
        "clean internal WSL Ubuntu environment",
        "clean internal Linux environment",
        "client computer",
        "productora computer",
        "school computer",
        "public demo computer",
        "sales event computer",
        "paid pilot computer",
        "production workstation with real footage",
    ])


def test_machine_prerequisites_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "Git available",
        "Python 3 available",
        "Python virtual environment support available",
        "shell access available",
        "local write access to a controlled workspace",
        "network access only for repository clone and dependency installation",
        "no need for media hardware",
        "no need for GPU",
        "no need for ffprobe",
        "no need for ffmpeg",
        "no need for DaVinci Resolve",
        "no need for Avid",
        "no need for SaaS credentials",
        "no need for database credentials",
    ])


def test_controlled_workspace_policy_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "a clean internal folder",
        "outside any client media folder",
        "outside any production footage folder",
        "outside any confidential project folder",
        "separate from user downloads",
        "separate from desktop clutter",
        "dedicated to this controlled internal setup",
        "disposable after the internal demo",
        "free of .env files copied from the main machine",
        "free of database files copied from the main machine",
    ])


def test_setup_command_plan_and_command_shape_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "Create a clean internal workspace.",
        "Clone the repository from the project remote.",
        "Check that the current branch is main.",
        "Check that HEAD matches the approved stable commit or an explicitly approved later commit.",
        "Create a local Python virtual environment.",
        "Activate the virtual environment.",
        "Install project dependencies from documented project requirements.",
        "Run the approved validation tests.",
        "Run the visible report CLI only with controlled fixture input.",
        "Write output only to a controlled output folder.",
        "mkdir -p ~/CID_INTERNAL_DEMO_SECOND_MACHINE",
        "git clone <project-remote-url> SERVICIOS_CINE",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install --upgrade pip",
        "python -m pip install -r requirements.txt",
        "--scanner-result-json <controlled_scanner_result_json>",
        "--output-root <controlled_output_root>",
        "--print-output-path",
        "This is command-shape documentation only. It is not executed by this phase.",
    ])


def test_required_setup_validation_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "repository clone completed",
        "repository path is controlled",
        "HEAD is approved",
        "virtual environment exists",
        "virtual environment is active",
        "project dependencies installed inside the virtual environment",
        "approved test subset passes",
        "controlled fixture input exists",
        "output root is controlled",
        "visible report CLI returns success",
        "generated visible report exists",
        "generated visible report is inside the controlled output root",
        "generated visible report declares client-facing readiness false",
        "generated visible report declares scanner execution by this renderer false",
        "generated visible report declares media probing by this renderer false",
        "generated visible report declares roadmap outputs not generated",
        "generated visible report includes internal-only disclaimer",
    ])


def test_allowed_and_blocked_outputs_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "generated markdown visible report",
        "terminal output showing test pass results",
        "terminal output showing generated report path",
        "internal setup notes",
        "internal demo checklist",
        "internal-only disclaimer",
        "real media analysis",
        "real scanner result from client material",
        "ffprobe metadata from real media",
        "ffmpeg output",
        "synchronized audio",
        "transcription",
        "subtitles",
        "translated subtitles",
        "timeline export",
        "SaaS upload result",
        "database records",
        "installer package",
        "license activation evidence",
        "public demo material",
        "sales deck claim",
    ])


def test_presenter_language_and_stop_conditions_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "This is a controlled internal second-machine setup plan.",
        "This is not a finished installation.",
        "This is not a commercial installer.",
        "This is not a client installer.",
        "This is not a public demo.",
        "This is not a sales demo.",
        "This uses controlled fixture input only.",
        "This does not scan real media.",
        "This does not execute ffprobe.",
        "This does not execute ffmpeg.",
        "This does not sync audio.",
        "This does not transcribe.",
        "This does not generate subtitles.",
        "This does not export timelines.",
        "This does not upload to SaaS.",
        "This does not write to a database.",
        "a client machine is proposed",
        "a school machine is proposed",
        "a productora machine is proposed",
        "installer creation is requested",
        "installer signing is requested",
        "license activation is requested",
        "real media is requested",
        "production footage is requested",
        "scanner execution is requested",
        "database write is requested",
    ])


def test_installation_boundary_and_next_phase_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "This plan is not an installation record.",
        "A later phase must be created before any actual second-machine setup execution.",
        "machine type",
        "operating system",
        "workspace path",
        "repository clone status",
        "HEAD validation",
        "virtual environment status",
        "dependency install status",
        "test results",
        "visible report generation result",
        "output path",
        "boundary compliance result",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.QA.GATE.V1",
        "No execution is authorized by this plan alone.",
    ])


def test_visible_report_generation_still_preserves_setup_plan_boundaries(tmp_path: Path) -> None:
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
    _assert_all_present(report_text, [
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
    ])


def test_validation_evidence_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "second machine setup plan test passing",
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
    ])
