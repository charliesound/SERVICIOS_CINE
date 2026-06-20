from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_qa_gate_v1.md")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan.py")
AUTH_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate_v1.md")
AUTH_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py")
EXECUTION_READINESS_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate_v1.md")
EXECUTION_READINESS_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py")
EXECUTION_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_v1.md")
EXECUTION_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py")
SETUP_PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
SETUP_PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
SETUP_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_plan_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_QA_GATE_PASS_READY_FOR_ONE_CONTROLLED_INTERNAL_EXECUTION",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "056d1b86233a6584e8d85702d2dbadc99dfba257",
        "docs: add CID Local Media Agent controlled execution plan",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-plan-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_PASS_READY_FOR_PLAN_QA_GATE",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        PLAN_DOC,
        PLAN_TEST,
        AUTH_GATE_DOC,
        AUTH_GATE_TEST,
        EXECUTION_READINESS_QA_GATE_DOC,
        EXECUTION_READINESS_QA_GATE_TEST,
        EXECUTION_READINESS_DOC,
        EXECUTION_READINESS_TEST,
        SETUP_PLAN_QA_GATE_TEST,
        SETUP_PLAN_TEST,
        SETUP_READINESS_TEST,
        INTERNAL_DEMO_READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_qa_gate_decision_does_not_execute_or_install() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "PASS_READY_FOR_ONE_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_PHASE",
        "This QA gate does not execute that phase.",
        "The execution phase must be separate.",
        "The execution phase must be evidence-recorded.",
        "The execution phase must remain internal-only.",
        "The execution phase must use controlled fixture input only.",
        "The execution phase must not use real media.",
        "The execution phase must not become an installer phase.",
        "The execution phase must not become a client delivery phase.",
    ])


def test_plan_completeness_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "phase",
        "objective",
        "source stable state",
        "plan decision",
        "execution plan scope",
        "machine preconditions",
        "repository preconditions",
        "controlled workspace plan",
        "exact future command plan",
        "approved validation tests",
        "controlled fixture plan",
        "evidence record plan",
        "required stop conditions",
        "explicitly blocked commands",
        "presenter language",
        "next safe phase",
        "validation evidence",
        "acceptance result",
    ])


def test_exact_command_plan_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "creating a controlled workspace",
        "entering the controlled workspace",
        "cloning the repository",
        "entering the repository",
        "verifying branch",
        "verifying local HEAD",
        "verifying remote main",
        "verifying required remote tag",
        "creating a virtual environment",
        "activating the virtual environment",
        "installing documented dependencies inside the virtual environment",
        "running approved validation tests",
        "creating controlled fixture and output folders",
        "creating a controlled scanner-result fixture",
        "running the visible report CLI with controlled fixture input only",
        "inspecting the generated report path",
        "writing an evidence record",
    ])


def test_required_expected_head_and_tag_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "056d1b86233a6584e8d85702d2dbadc99dfba257",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-plan-v1-20260620",
    ])


def test_controlled_workspace_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
        "The workspace must be disposable.",
        "The workspace must be outside client media folders.",
        "The workspace must be outside production footage folders.",
        "The workspace must be outside confidential project folders.",
        "The workspace must not contain real media.",
        "The workspace must not contain production footage.",
        "The workspace must not contain client media.",
        "The workspace must not contain confidential scripts.",
        "The workspace must not contain environment secret files.",
        "The workspace must not contain database files.",
        "The workspace must not contain installer artifacts.",
        "The workspace must not contain license activation files.",
        "The workspace must not contain public demo assets.",
        "The workspace must not contain sales demo assets.",
    ])


def test_approved_validation_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "controlled execution plan test",
        "controlled execution authorization gate test",
        "execution readiness QA gate test",
        "execution readiness test",
        "setup plan QA gate test",
        "setup plan test",
        "setup readiness test",
        "internal demo readiness test",
        "visible report runtime CLI test",
        "visible report runtime CLI implementation QA gate test",
        "visible report runtime generator test",
        "controlled runtime implementation QA gate test",
    ])


def test_controlled_fixture_and_visible_report_cli_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "controlled scanner-result fixture",
        "_valid_scanner_result",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "scripts/local_media_agent/visible_report_runtime_cli.py",
        "--scanner-result-json /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "--output-root /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output",
        "--print-output-path",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md",
    ])


def test_evidence_record_criteria_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "controlled_execution_evidence_v1.json",
        "internal_only true",
        "controlled_fixture_only true",
        "real_media_used false",
        "client_material_used false",
        "installer_created false",
        "client_installation false",
        "public_demo false",
        "sales_demo false",
        "database_write false",
        "saas_upload false",
        "expected HEAD",
        "source tag",
        "authorization source phase",
        "created UTC timestamp",
    ])


def test_required_stop_conditions_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "machine owner is not project owner",
        "machine is client-owned",
        "machine is productora-owned",
        "machine is school-owned",
        "machine is investor-owned",
        "workspace is not controlled",
        "repository remote is unexpected",
        "branch is not main",
        "local HEAD does not match expected HEAD",
        "remote main does not match expected HEAD",
        "required remote tag is missing",
        "repository is dirty before execution",
        "virtual environment cannot be created",
        "dependency installation fails",
        "approved validation tests fail",
        "controlled fixture cannot be created",
        "output root is not controlled",
        "real media is requested",
        "installer action is requested",
        "public demo action is requested",
        "sales demo action is requested",
        "SaaS upload is requested",
        "database write is requested",
    ])


def test_explicitly_blocked_commands_are_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "run scanner on real media",
        "run media probing on real files",
        "run ffprobe on real files",
        "run ffmpeg on real files",
        "synchronize audio",
        "transcribe audio",
        "generate subtitles",
        "translate subtitles",
        "export DaVinci Resolve timelines",
        "export Avid timelines",
        "upload to SaaS",
        "write to database",
        "copy secrets",
        "copy environment files",
        "copy database files",
        "create installer package",
        "sign installer",
        "activate license",
        "connect license server",
        "install on client computer",
        "present public demo",
        "present sales demo",
    ])


def test_presenter_language_is_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "This is one controlled internal second-machine setup execution.",
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


def test_next_safe_phase_is_declared() -> None:
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.V1",
        "may execute one controlled internal second-machine setup execution using the validated plan",
        "It must remain internal-only.",
        "It must use controlled fixture input only.",
        "It must write an evidence record.",
        "It must stop on any stop condition.",
        "It must not install on a client machine.",
        "It must not create an installer.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
        "It must not use real media.",
    ])


def test_upstream_plan_names_this_qa_gate_as_next_safe_phase() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.QA.GATE.V1",
        "That phase may validate the exact command plan.",
        "It must not execute setup.",
        "It must not install the product.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
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
    text = _text(PLAN_QA_GATE_DOC)
    _assert_all_present(text, [
        "controlled execution plan QA gate test passing",
        "controlled execution plan test passing",
        "controlled execution authorization gate test passing",
        "second machine setup execution readiness QA gate test passing",
        "second machine setup execution readiness test passing",
        "second machine setup plan QA gate test passing",
        "second machine setup plan test passing",
        "second machine setup readiness test passing",
        "internal demo readiness test passing",
        "CLI test passing",
        "CLI implementation QA gate passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate passing",
        "supporting implemented runtime chain tests passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
    ])
