from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

READINESS_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_readiness_gate_v1.md"
)
QA_GATE_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_qa_gate_v1.md"
)
IMPLEMENTATION_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_implementation_v1.md"
)

CLI_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
APPROVED_FIXTURE_BASENAME = "synthetic_demo_report_fixture_v1.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_cli_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_cli",
        CLI_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_path() -> Path:
    matches = sorted(REPO_ROOT.rglob(APPROVED_FIXTURE_BASENAME))
    assert matches, "Approved synthetic fixture is required for readiness gate."
    return matches[0]


def test_user_flow_readiness_doc_declares_phase_baseline_and_decision() -> None:
    text = _read(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.READINESS.GATE.V1" in text
    assert "Stable HEAD before this phase: `bf09fa8`." in text
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.QA.GATE.V1" in text
    assert "READY_FOR_CONTROLLED_PREFLIGHT_USER_FLOW_SPEC_WITH_RESTRICTIONS" in text


def test_user_flow_readiness_references_current_command_and_previous_gates() -> None:
    text = _read(READINESS_DOC)
    qa_text = _read(QA_GATE_DOC)
    implementation_text = _read(IMPLEMENTATION_DOC)

    command = (
        "synthetic-visible-report --preflight --fixture <fixture-json> "
        "--output-dir <existing-dir> --format markdown [--allow-overwrite]"
    )

    assert command in text
    assert command in qa_text
    assert command in implementation_text
    assert "development CLI invocation, not an installable product command" in text


def test_user_flow_definition_is_descriptive_not_runtime_or_packaging_work() -> None:
    text = _read(READINESS_DOC)

    required_steps = [
        "User selects or receives an approved synthetic fixture.",
        "User selects an existing local output directory.",
        "User runs preflight before report generation.",
        "System returns `PREFLIGHT_PASS` or safe `PREFLIGHT_FAIL`.",
        "User may only proceed to generation after a pass.",
        "Human review remains mandatory for all generated outputs.",
    ]

    for step in required_steps:
        assert step in text

    assert "A future controlled user flow may be allowed to describe, but not yet implement" in text


def test_user_flow_readiness_documents_all_blocked_scope() -> None:
    text = _read(READINESS_DOC)

    blocked = [
        "packaging;",
        "installable entry point;",
        "shell launcher;",
        "desktop app;",
        "installer;",
        "licensing;",
        "scanner integration;",
        "ffprobe/ffmpeg execution;",
        "real media analysis;",
        "sync;",
        "transcription;",
        "translation;",
        "subtitle generation;",
        "NLE/export;",
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work;",
        "upload or processing of client material.",
    ]

    for item in blocked:
        assert item in text


def test_current_cli_supports_preflight_user_flow_without_packaging_or_scanner() -> None:
    cli_source = _read(CLI_SCRIPT)

    assert "--preflight" in cli_source
    assert "def _run_preflight" in cli_source
    assert "preflight.main(preflight_args)" in cli_source
    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in cli_source

    assert "entry_points" not in cli_source
    assert "console_scripts" not in cli_source
    assert "cid_media_agent_scan" not in cli_source
    assert "ffprobe" not in cli_source.lower()
    assert "ffmpeg" not in cli_source.lower()
    assert "sqlalchemy" not in cli_source.lower()
    assert "alembic" not in cli_source.lower()
    assert "stripe" not in cli_source.lower()


def test_preflight_user_flow_pass_does_not_generate_report_or_create_output_dir(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()
    existing_output_dir = tmp_path / "existing-output"
    existing_output_dir.mkdir()
    missing_output_dir = tmp_path / "missing-output"

    pass_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(fixture),
            "--output-dir",
            str(existing_output_dir),
            "--format",
            "markdown",
        ]
    )

    pass_capture = capsys.readouterr()
    assert pass_code == 0
    assert "PREFLIGHT_PASS" in pass_capture.out
    assert not (existing_output_dir / OUTPUT_FILENAME).exists()

    missing_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(fixture),
            "--output-dir",
            str(missing_output_dir),
            "--format",
            "markdown",
        ]
    )

    missing_capture = capsys.readouterr()
    assert missing_code == 3
    assert "PREFLIGHT_FAIL" in missing_capture.err
    assert "reason=OUTPUT_DIR_NOT_FOUND" in missing_capture.err
    assert not missing_output_dir.exists()


def test_generation_after_preflight_pass_remains_separate_explicit_step(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()

    preflight_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    preflight_capture = capsys.readouterr()
    assert preflight_code == 0
    assert "PREFLIGHT_PASS" in preflight_capture.out
    assert not (tmp_path / OUTPUT_FILENAME).exists()

    generation_code = cli.main(
        [
            "--fixture",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    generation_capture = capsys.readouterr()
    assert generation_code == 0
    assert "OK: generado" in generation_capture.out
    assert (tmp_path / OUTPUT_FILENAME).exists()


def test_renderer_scanner_and_helper_boundaries_remain_intact_for_user_flow_readiness() -> None:
    helper_source = _read(PREFLIGHT_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "PREFLIGHT_PASS" in helper_source
    assert "PREFLIGHT_FAIL" in helper_source

    assert "--preflight" not in renderer_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source

    assert "--preflight" not in scanner_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source
    assert "synthetic-visible-report-preflight" not in scanner_source


def test_user_flow_readiness_does_not_introduce_client_media_or_external_runtime_terms() -> None:
    combined = "\n".join(
        [
            _read(READINESS_DOC),
            _read(CLI_SCRIPT),
        ]
    ).lower()

    forbidden = [
        "client.mov",
        "customer.mov",
        "real_project",
        "ffprobe -",
        "ffmpeg -",
        "upload endpoint",
        "stripe checkout",
        "create_engine",
        "sessionmaker",
        "op.create_table",
        "alembic revision",
    ]

    for item in forbidden:
        assert item not in combined
