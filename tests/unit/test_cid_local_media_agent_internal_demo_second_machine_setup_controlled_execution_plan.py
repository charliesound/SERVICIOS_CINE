from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_v1.md")
AUTH_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate_v1.md")
AUTH_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py")
EXECUTION_READINESS_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate_v1.md")
EXECUTION_READINESS_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py")
EXECUTION_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_v1.md")
EXECUTION_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py")
SETUP_PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate_v1.md")
SETUP_PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
SETUP_PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_v1.md")
SETUP_PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
SETUP_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_readiness_v1.md")
SETUP_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_controlled_execution_plan_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_PASS_READY_FOR_PLAN_QA_GATE",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "9f665c1823435084f8a9181e2b3ac9420bc47011",
        "test: add CID Local Media Agent controlled execution authorization gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_PLAN",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        AUTH_GATE_DOC,
        AUTH_GATE_TEST,
        EXECUTION_READINESS_QA_GATE_DOC,
        EXECUTION_READINESS_QA_GATE_TEST,
        EXECUTION_READINESS_DOC,
        EXECUTION_READINESS_TEST,
        SETUP_PLAN_QA_GATE_DOC,
        SETUP_PLAN_QA_GATE_TEST,
        SETUP_PLAN_DOC,
        SETUP_PLAN_TEST,
        SETUP_READINESS_DOC,
        SETUP_READINESS_TEST,
        INTERNAL_DEMO_READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_plan_decision_does_not_execute_or_install() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "PLAN_READY_FOR_CONTROLLED_EXECUTION_PLAN_QA_GATE",
        "This phase does not execute setup.",
        "This phase does not install the product.",
        "This phase does not create an installer.",
        "It does not mean setup execution has happened.",
        "It does not mean installation has happened.",
        "It does not mean an installer exists.",
    ])


def test_execution_plan_scope_is_limited() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "one internal second machine",
        "one project-owner controlled machine",
        "one disposable internal workspace",
        "one repository clone or verified existing clone",
        "one expected HEAD",
        "one virtual environment",
        "one dependency installation inside that virtual environment",
        "one validation sequence",
        "one controlled fixture input",
        "one visible report CLI execution",
        "one generated markdown report",
        "one evidence record",
    ])


def test_machine_preconditions_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "machine owner is project owner",
        "machine is internal only",
        "machine is not client-owned",
        "machine is not productora-owned",
        "machine is not school-owned",
        "machine is not investor-owned",
        "machine does not contain client media",
        "machine does not contain production footage",
        "machine does not contain confidential script material",
        "machine does not contain copied environment secrets",
        "machine does not contain copied database files",
        "workspace is disposable",
        "workspace is outside client media folders",
        "workspace is outside production footage folders",
        "workspace is outside confidential project folders",
    ])


def test_repository_preconditions_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "repository path is controlled",
        "repository remote is expected",
        "current branch is main",
        "local HEAD is expected",
        "remote main is expected",
        "required source tag is present remotely",
        "repository is clean before execution",
        "9f665c1823435084f8a9181e2b3ac9420bc47011",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620",
    ])


def test_controlled_workspace_plan_is_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
        "repository clone or verified repository folder",
        "controlled fixture input",
        "controlled output root",
        "generated visible report",
        "evidence record",
        "real media",
        "production footage",
        "client media",
        "confidential scripts",
        "environment secret files",
        "database files",
        "installer artifacts",
        "license activation files",
        "public demo assets",
        "sales demo assets",
    ])


def test_exact_future_command_plan_includes_expected_sequence() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "mkdir -p /tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
        "git clone https://github.com/charliesound/SERVICIOS_CINE.git SERVICIOS_CINE",
        "git branch --show-current",
        "git rev-parse HEAD",
        "git ls-remote --heads origin main",
        "git ls-remote --tags origin | grep cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-authorization-gate-v1-20260620",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install -U pip",
        "python -m pip install -e \".[test]\"",
        "python scripts/local_media_agent/visible_report_runtime_cli.py",
        "--scanner-result-json /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "--output-root /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output",
        "--print-output-path",
    ])


def test_exact_future_command_plan_includes_approved_validation_tests() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_cli_implementation_qa_gate.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py -q",
        "python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py -q",
    ])


def test_controlled_fixture_and_evidence_plan_are_declared() -> None:
    text = _text(PLAN_DOC)
    _assert_all_present(text, [
        "controlled_scanner_result.json",
        "_valid_scanner_result",
        "controlled_execution_evidence_v1.json",
        "\"internal_only\": True",
        "\"controlled_fixture_only\": True",
        "\"real_media_used\": False",
        "\"client_material_used\": False",
        "\"installer_created\": False",
        "\"client_installation\": False",
        "\"public_demo\": False",
        "\"sales_demo\": False",
        "\"database_write\": False",
        "\"saas_upload\": False",
    ])


def test_required_stop_conditions_are_declared() -> None:
    text = _text(PLAN_DOC)
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
        "any real media is requested",
        "any installer action is requested",
        "any public demo action is requested",
        "any sales demo action is requested",
        "any SaaS upload is requested",
        "any database write is requested",
    ])


def test_explicitly_blocked_commands_are_declared() -> None:
    text = _text(PLAN_DOC)
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
    text = _text(PLAN_DOC)
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


def test_upstream_authorization_gate_names_this_plan_as_next_safe_phase() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.V1",
        "may define the exact command plan for one future controlled internal second-machine setup execution",
        "It must not execute setup.",
        "It must not install the product.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
    ])


def test_visible_report_generation_still_preserves_plan_boundaries(tmp_path: Path) -> None:
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
