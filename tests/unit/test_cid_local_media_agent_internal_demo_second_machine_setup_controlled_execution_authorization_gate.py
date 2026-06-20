from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import _valid_scanner_result


AUTH_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate_v1.md")
EXECUTION_READINESS_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate_v1.md")
EXECUTION_READINESS_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py")
EXECUTION_READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_v1.md")
EXECUTION_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py")
PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate_v1.md")
PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_readiness_v1.md")
READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_authorization_gate_doc_exists_and_declares_phase_and_result() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_PLAN",
    ])


def test_source_traceability_is_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "b5ec8b425847d5df98da9049afd15144349b5a0a",
        "test: add CID Local Media Agent second machine setup execution readiness QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-execution-readiness-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_AUTHORIZATION_GATE",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        EXECUTION_READINESS_QA_GATE_DOC,
        EXECUTION_READINESS_QA_GATE_TEST,
        EXECUTION_READINESS_DOC,
        EXECUTION_READINESS_TEST,
        PLAN_QA_GATE_DOC,
        PLAN_QA_GATE_TEST,
        PLAN_DOC,
        PLAN_TEST,
        READINESS_DOC,
        READINESS_TEST,
        INTERNAL_DEMO_READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_human_authorization_decision_is_explicit_but_not_execution() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "AUTHORIZE_ONE_FUTURE_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_PHASE",
        "This gate does not execute that phase.",
        "The execution phase must be separate.",
        "The execution phase must be evidence-recorded.",
        "The execution phase must remain internal-only.",
        "The execution phase must use controlled fixture input only.",
        "The execution phase must not use real media.",
        "The execution phase must not become an installer phase.",
        "The execution phase must not become a client delivery phase.",
    ])


def test_authorization_scope_is_limited_to_one_future_internal_execution_phase() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "one future controlled execution phase only",
        "one project-owner controlled internal second machine",
        "one controlled internal workspace",
        "one clean shell environment",
        "one repository clone or verified existing clone",
        "one expected HEAD",
        "one virtual environment",
        "one approved validation sequence",
        "one controlled fixture input set",
        "one visible report CLI execution using controlled fixture input",
        "one generated report under controlled output root",
        "one evidence record",
    ])


def test_explicit_non_authorization_is_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "executing setup inside this phase",
        "commercial installation",
        "client installation",
        "productora installation",
        "school installation",
        "investor installation",
        "public demo",
        "sales demo",
        "paid pilot use",
        "production use",
        "installer creation",
        "installer signing",
        "license activation",
        "license server connection",
        "scanner execution on real media",
        "media probing on real files",
        "ffprobe on real files",
        "ffmpeg on real files",
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "subtitle translation",
        "DaVinci Resolve timeline export",
        "Avid timeline export",
        "SaaS upload",
        "database writes",
        "copied environment secrets",
        "copied database files",
        "copied confidential script material",
        "copied client material",
        "copied production footage",
    ])


def test_required_preconditions_before_future_execution_are_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "repository is clean before execution",
        "current branch is main",
        "local HEAD matches expected HEAD",
        "remote main matches expected HEAD",
        "required tag exists remotely",
        "machine owner is project owner",
        "machine is internal only",
        "machine is not client-owned",
        "machine is not a productora machine",
        "machine is not a school machine",
        "machine is not an investor machine",
        "workspace is controlled",
        "workspace is disposable",
        "workspace is outside client media folders",
        "workspace is outside production footage folders",
        "workspace is outside confidential project folders",
        "no environment secret files are copied",
        "no database files are copied",
        "no real media is copied",
        "no production footage is copied",
        "virtual environment is local to the controlled clone",
        "dependency installation is inside the virtual environment",
        "validation tests pass before visible report CLI execution",
        "fixture input is controlled",
        "output root is controlled",
        "generated report remains inside output root",
        "evidence record is written",
    ])


def test_required_evidence_record_is_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "phase name",
        "authorization source phase",
        "source HEAD",
        "source tag",
        "machine type",
        "machine owner confirmation",
        "operating system",
        "shell environment",
        "Python version",
        "Git version",
        "repository remote",
        "repository path",
        "branch",
        "local HEAD",
        "remote main HEAD",
        "virtual environment path",
        "dependency command",
        "validation commands",
        "fixture input path",
        "output root path",
        "visible report command shape",
        "generated report path",
        "generated report existence",
        "boundary compliance result",
        "stop reason if stopped",
        "final result",
    ])


def test_stop_conditions_for_future_execution_are_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "wrong repository path",
        "wrong branch",
        "expected HEAD mismatch",
        "remote main mismatch",
        "missing required remote tag",
        "dirty repository before execution",
        "unauthorized machine owner",
        "non-internal machine",
        "client-owned machine",
        "productora-owned machine",
        "school-owned machine",
        "investor-owned machine",
        "uncontrolled workspace",
        "workspace inside client media folder",
        "workspace inside production footage folder",
        "workspace inside confidential project folder",
        "copied environment secret file detected",
        "copied database file detected",
        "real media detected",
        "production footage detected",
        "confidential script material detected",
        "virtual environment missing",
        "dependency installation failure",
        "validation test failure",
        "fixture input missing",
        "output root missing",
        "output root outside controlled workspace",
        "generated report missing",
        "generated report outside controlled output root",
        "request to run scanner on real media",
        "request to run ffprobe on real files",
        "request to run ffmpeg on real files",
        "request to sync audio",
        "request to transcribe",
        "request to generate subtitles",
        "request to export timelines",
        "request to upload to SaaS",
        "request to write to database",
        "request to install on client machine",
        "request to create installer",
        "request to sign installer",
        "request to activate license",
        "request to show public demo",
        "request to show sales demo",
    ])


def test_allowed_future_execution_command_families_are_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "create controlled workspace",
        "clone repository",
        "enter repository folder",
        "check current branch",
        "check local HEAD",
        "check remote main",
        "check required tag",
        "create virtual environment",
        "activate virtual environment",
        "install documented dependencies inside virtual environment",
        "run approved validation tests",
        "create controlled fixture input",
        "run visible report CLI with controlled fixture input",
        "write report under controlled output root",
        "print generated report path",
        "inspect generated report",
        "write evidence record",
    ])


def test_blocked_future_execution_command_families_are_declared() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "scan real media",
        "probe real media",
        "process production footage",
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


def test_presenter_language_for_future_execution_is_declared() -> None:
    text = _text(AUTH_GATE_DOC)
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


def test_upstream_qa_gate_contains_required_authorization_terms() -> None:
    text = _text(EXECUTION_READINESS_QA_GATE_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1",
        "may decide whether to authorize one controlled internal second-machine setup execution",
        "It must not execute setup.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
    ])


def test_visible_report_generation_still_preserves_authorization_gate_boundaries(tmp_path: Path) -> None:
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
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
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


def test_authorization_gate_blocks_client_public_sales_and_installer_paths() -> None:
    text = _text(AUTH_GATE_DOC)
    _assert_all_present(text, [
        "does not create an installer",
        "does not create a commercial package",
        "does not authorize client-facing demo",
        "does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer",
        "This gate does not execute that phase.",
        "The execution phase must not become an installer phase.",
        "The execution phase must not become a client delivery phase.",
    ])
