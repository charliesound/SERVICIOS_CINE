from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


EXECUTION_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_v1.md")
PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate_v1.md")
PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_readiness_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_internal_demo_readiness_v1.md")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_execution_readiness_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_PASS_READY_FOR_EXECUTION_READINESS_QA_GATE",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "982d4e9bdbebc55678bebf482a18e3ee5fa6eed9",
        "test: add CID Local Media Agent second machine setup plan QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-plan-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_QA_GATE_PASS_READY_FOR_SECOND_MACHINE_SETUP_EXECUTION_READINESS",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        PLAN_QA_GATE_DOC,
        PLAN_QA_GATE_TEST,
        PLAN_DOC,
        PLAN_TEST,
        READINESS_DOC,
        READINESS_TEST,
        INTERNAL_DEMO_READINESS_DOC,
        INTERNAL_DEMO_READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_readiness_decision_does_not_authorize_execution_or_installation() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_READINESS_QA_GATE",
        "It does not mean setup execution is authorized.",
        "It does not mean setup execution has happened.",
        "It does not mean installation has happened.",
        "It does not mean an installer exists.",
        "It does not mean a client may receive the software.",
        "It does not mean a public or sales demonstration is authorized.",
    ])


def test_allowed_target_machine_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "project-owner controlled internal machine",
        "internal development laptop",
        "internal review laptop",
        "clean internal WSL Ubuntu environment",
        "clean internal Linux environment",
        "machine without client material",
        "machine without production footage",
        "machine without confidential script material",
        "machine without copied environment secrets",
        "machine without copied local database files",
        "machine with a disposable internal workspace",
    ])


def test_blocked_target_machine_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "client computer",
        "productora computer",
        "school computer",
        "investor computer",
        "public demo computer",
        "sales event computer",
        "paid pilot computer",
        "production workstation with real footage",
        "unmanaged third-party machine",
        "machine containing confidential client material",
        "machine containing real production media",
    ])


def test_required_target_machine_evidence_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "machine owner confirmation",
        "machine type",
        "operating system",
        "shell environment",
        "Python version",
        "Git version",
        "workspace path",
        "workspace creation command",
        "repository remote used",
        "cloned repository path",
        "checked branch",
        "local HEAD",
        "expected HEAD",
        "virtual environment path",
        "dependency installation command",
        "validation commands",
        "visible report command shape",
        "output root path",
        "generated report path",
        "boundary compliance result",
    ])


def test_controlled_workspace_requirements_are_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "created only for this internal setup",
        "outside any client media folder",
        "outside any production footage folder",
        "outside any confidential project folder",
        "outside desktop clutter",
        "outside downloads clutter",
        "disposable after review",
        "free of copied secrets",
        "free of copied database files",
        "free of real media",
        "free of production footage",
        "dedicated to controlled fixture input and generated internal output",
    ])


def test_allowed_execution_command_families_are_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "create controlled workspace",
        "clone repository",
        "enter repository folder",
        "check current branch",
        "check HEAD",
        "create virtual environment",
        "activate virtual environment",
        "install documented dependencies inside the virtual environment",
        "run approved validation tests",
        "create controlled fixture input",
        "run visible report CLI with controlled fixture input",
        "write generated report to controlled output root",
        "print generated report path",
        "inspect generated markdown report",
    ])


def test_blocked_execution_command_families_are_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "scanning real media",
        "probing real media",
        "processing production footage",
        "running ffprobe on real files",
        "running ffmpeg on real files",
        "synchronizing audio",
        "transcribing audio",
        "generating subtitles",
        "translating subtitles",
        "exporting DaVinci timelines",
        "exporting Avid timelines",
        "uploading to SaaS",
        "writing to database",
        "copying secrets",
        "copying environment files",
        "copying database files",
        "installing on client machine",
        "creating installer package",
        "signing installer",
        "activating license",
        "connecting license server",
        "presenting as public demo",
        "presenting as sales demo",
    ])


def test_required_readiness_checklist_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "target machine is allowed",
        "target machine is internal",
        "target machine has no client material",
        "target machine has no production footage",
        "workspace is controlled",
        "workspace is disposable",
        "repository clone is from approved remote",
        "HEAD is approved",
        "branch is main",
        "virtual environment is local",
        "dependencies are installed only inside virtual environment",
        "validation tests pass",
        "fixture input is controlled",
        "visible report output is controlled",
        "generated report declares client-facing readiness false",
        "generated report declares scanner execution by this renderer false",
        "generated report declares media probing by this renderer false",
        "generated report declares roadmap outputs not generated",
        "operator confirms no real media was used",
    ])


def test_required_failure_handling_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "If any readiness condition fails, the future execution must stop.",
        "wrong machine type",
        "unauthorized machine owner",
        "non-internal machine",
        "client material detected",
        "production footage detected",
        "confidential script material detected",
        "workspace path not controlled",
        "expected HEAD mismatch",
        "branch mismatch",
        "virtual environment missing",
        "dependency installation failure",
        "validation test failure",
        "fixture input missing",
        "output root not controlled",
        "generated report missing",
        "generated report outside controlled output root",
        "any request to use real media",
        "any request to create an installer",
        "any request to show a public demo",
        "any request to show a sales demo",
        "any request to install on a client computer",
    ])


def test_presenter_boundary_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "This is a controlled internal setup execution.",
        "This is not a commercial installation.",
        "This is not a client installation.",
        "This is not an installer.",
        "This is not a public demo.",
        "This is not a sales demo.",
        "This uses controlled fixture input only.",
        "This does not scan real media.",
        "This does not probe real media.",
        "This does not sync audio.",
        "This does not transcribe.",
        "This does not generate subtitles.",
        "This does not export timelines.",
        "This does not upload to SaaS.",
        "This does not write to a database.",
    ])


def test_execution_authorization_boundary_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "This readiness phase does not authorize setup execution.",
        "A later QA gate must validate this execution readiness before any controlled execution phase.",
        "The future execution phase must be separate.",
        "The future execution phase must record evidence.",
        "The future execution phase must still be internal-only.",
        "The future execution phase must still use controlled fixture input only.",
        "The future execution phase must not become an installer phase.",
        "The future execution phase must not become a client delivery phase.",
    ])


def test_next_safe_phase_is_declared() -> None:
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.QA.GATE.V1",
        "That phase may validate this readiness.",
        "It must not execute setup.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
    ])


def test_visible_report_generation_still_preserves_execution_readiness_boundaries(tmp_path: Path) -> None:
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
    text = _text(EXECUTION_READINESS_DOC)
    _assert_all_present(text, [
        "second machine setup execution readiness test passing",
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
