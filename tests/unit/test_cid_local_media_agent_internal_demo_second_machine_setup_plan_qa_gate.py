from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate_v1.md")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
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


def test_second_machine_setup_plan_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_QA_GATE_PASS_READY_FOR_SECOND_MACHINE_SETUP_EXECUTION_READINESS",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "0ff9636d8b40f121dfff22e9eebc2ba1d2a75fb8",
        "docs: add CID Local Media Agent second machine setup plan",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-plan-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN_QA_GATE",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        PLAN_DOC,
        PLAN_TEST,
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


def test_qa_gate_decision_does_not_authorize_execution_or_installer() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "PASS_READY_FOR_CONTROLLED_SECOND_MACHINE_SETUP_EXECUTION_READINESS",
        "does not mean setup execution is authorized",
        "does not mean installation has been performed",
        "does not mean an installer exists",
        "does not mean a client may receive the software",
        "does not mean the product is ready for sales, public demo, paid pilot, or production use",
    ])


def test_plan_completeness_criteria_are_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "phase",
        "objective",
        "source stable state",
        "current decisions",
        "setup plan decision",
        "target machine profile",
        "required machine prerequisites",
        "controlled workspace policy",
        "setup command plan",
        "example command shape",
        "required setup validation",
        "allowed demonstration output",
        "blocked demonstration output",
        "required presenter language",
        "stop conditions",
        "installation boundary",
        "next safe phase",
        "validation evidence",
        "acceptance result",
    ])


def test_safety_boundary_criteria_are_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "actual setup execution by the plan alone",
        "commercial installer creation",
        "client installer creation",
        "client machine use",
        "productora machine use",
        "school machine use",
        "public demo use",
        "sales demo use",
        "paid pilot use",
        "product distribution",
        "installer signing",
        "license activation",
        "real media use",
        "production footage use",
        "scanner execution",
        "ffprobe execution",
        "ffmpeg execution",
        "sync output",
        "transcription output",
        "subtitle output",
        "timeline export",
        "SaaS upload",
        "database write",
    ])


def test_internal_only_criteria_are_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "project-owner controlled machine",
        "internal development laptop",
        "internal review laptop",
        "clean internal WSL Ubuntu environment",
        "clean internal Linux environment",
        "controlled workspace",
        "controlled fixture input",
        "controlled output folder",
        "internal-only disclaimer",
        "internal setup notes",
        "generated markdown visible report from controlled facts",
    ])


def test_technical_scope_criteria_are_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "no media hardware is required",
        "no GPU is required",
        "ffprobe is not required",
        "ffmpeg is not required",
        "DaVinci Resolve is not required",
        "Avid is not required",
        "SaaS credentials are not required",
        "database credentials are not required",
        "the visible report renderer does not scan real media",
        "the visible report renderer does not probe real media",
        "roadmap outputs remain not generated",
    ])


def test_execution_boundary_criteria_are_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "This plan is not an installation record.",
        "A later phase must be created before any actual second-machine setup execution.",
        "No execution is authorized by this plan alone.",
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
    ])


def test_next_safe_phase_boundary_is_declared() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.V1",
        "may prepare readiness for a controlled internal setup execution",
        "must not execute the setup",
        "must not create an installer",
        "must not authorize client installation",
        "must not authorize public demo use",
        "must not authorize sales demo use",
    ])


def test_setup_plan_contains_required_qa_gate_terms() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLAN_ONLY",
        "This plan is not an installation record.",
        "A later phase must be created before any actual second-machine setup execution.",
        "No execution is authorized by this plan alone.",
        "client computer",
        "productora computer",
        "school computer",
        "installer package",
        "license activation evidence",
        "real media analysis",
        "ffprobe metadata from real media",
        "database records",
    ])


def test_setup_plan_command_shape_remains_documentation_only() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "mkdir -p ~/CID_INTERNAL_DEMO_SECOND_MACHINE",
        "git clone <project-remote-url> SERVICIOS_CINE",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install -r requirements.txt",
        "--scanner-result-json <controlled_scanner_result_json>",
        "--output-root <controlled_output_root>",
        "--print-output-path",
        "This is command-shape documentation only. It is not executed by this phase.",
    ])


def test_visible_report_generation_still_preserves_plan_qa_gate_boundaries(tmp_path: Path) -> None:
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
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "second machine setup plan QA gate test passing",
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


def test_qa_gate_is_not_client_or_installer_ready() -> None:
    text = _text(QA_GATE_DOC)
    blocked = [
        "does not create an installer",
        "does not create a commercial package",
        "does not authorize client-facing demo",
        "does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer",
    ]
    _assert_all_present(text, blocked)


def test_no_execution_is_authorized_by_qa_gate() -> None:
    text = _text(QA_GATE_DOC)
    _assert_all_present(text, [
        "This QA gate does not execute the setup on a second machine.",
        "It does not mean setup execution is authorized.",
        "No execution is authorized by this plan alone.",
    ])
