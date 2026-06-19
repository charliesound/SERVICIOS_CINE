from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

SPEC_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_v1.md"
)
READINESS_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_readiness_gate_v1.md"
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
    assert matches, "Approved synthetic fixture is required for user-flow spec."
    return matches[0]


def test_user_flow_spec_declares_phase_baseline_and_decision() -> None:
    text = _read(SPEC_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.V1" in text
    assert "Stable HEAD before this phase: `0ed4c8e`." in text
    assert "This phase is documentation/test-only." in text
    assert "USER_FLOW_SPEC_READY_FOR_QA_GATE_WITH_RESTRICTIONS" in text


def test_user_flow_spec_references_previous_readiness_gate() -> None:
    text = _read(SPEC_DOC)
    readiness_text = _read(READINESS_DOC)

    previous_phase = (
        "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT."
        "PREFLIGHT.USER.FLOW.READINESS.GATE.V1"
    )

    assert previous_phase in text
    assert previous_phase in readiness_text


def test_user_flow_spec_defines_preflight_before_generation() -> None:
    text = _read(SPEC_DOC)

    assert "User runs preflight before generation." in text
    assert "User generates only after `PREFLIGHT_PASS`." in text
    assert "Run preflight first. Generate only after PREFLIGHT_PASS. Review output manually." in text
    assert "synthetic-visible-report --preflight --fixture <fixture-json>" in text
    assert "synthetic-visible-report --fixture <fixture-json> --output-dir <existing-dir> --format markdown" in text


def test_user_flow_spec_requires_synthetic_fixture_and_existing_local_output_dir() -> None:
    text = _read(SPEC_DOC)

    required = [
        "fixture exists;",
        "fixture is synthetic;",
        "fixture is not real client media;",
        "fixture is not scanner output from real material;",
        "output directory exists before preflight;",
        "preflight must not create the output directory;",
        "preflight must not generate `cid_local_media_agent_synthetic_visible_report_v1.md`;",
        "generation remains a separate explicit command.",
    ]

    for item in required:
        assert item in text


def test_user_flow_spec_documents_safe_controlled_failures() -> None:
    text = _read(SPEC_DOC)

    required = [
        "missing fixture returns controlled `PREFLIGHT_FAIL`;",
        "missing output directory returns controlled `PREFLIGHT_FAIL`;",
        "existing output report without overwrite returns controlled `PREFLIGHT_FAIL`;",
        "helper failure returns controlled `PREFLIGHT_FAIL`;",
        "no Python traceback is expected in normal controlled failures;",
        "no raw JSON dump, secret, real media path or client material should be intentionally exposed.",
    ]

    for item in required:
        assert item in text


def test_user_flow_spec_keeps_blocked_scope_closed() -> None:
    text = _read(SPEC_DOC)

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


def test_preflight_spec_flow_pass_then_generation_is_explicit(tmp_path, capsys) -> None:
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
    assert "OK: generado" not in preflight_capture.out
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


def test_preflight_spec_flow_rejects_missing_output_dir_without_creating_it(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()
    missing_output_dir = tmp_path / "missing-output"

    exit_code = cli.main(
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

    captured = capsys.readouterr()
    assert exit_code == 3
    assert "PREFLIGHT_FAIL" in captured.err
    assert "reason=OUTPUT_DIR_NOT_FOUND" in captured.err
    assert "Traceback" not in captured.err
    assert not missing_output_dir.exists()


def test_preflight_spec_flow_rejects_existing_report_without_overwrite(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()

    report = tmp_path / OUTPUT_FILENAME
    report.write_text("existing report", encoding="utf-8")

    exit_code = cli.main(
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

    captured = capsys.readouterr()
    assert exit_code == 4
    assert "PREFLIGHT_FAIL" in captured.err
    assert "reason=OUTPUT_ALREADY_EXISTS" in captured.err
    assert "Traceback" not in captured.err
    assert report.read_text(encoding="utf-8") == "existing report"


def test_runtime_boundaries_remain_free_of_packaging_scanner_and_media_processing() -> None:
    cli_source = _read(CLI_SCRIPT)
    helper_source = _read(PREFLIGHT_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "--preflight" in cli_source
    assert "PREFLIGHT_PASS" in helper_source
    assert "PREFLIGHT_FAIL" in helper_source

    for source in [cli_source, renderer_source, scanner_source]:
        assert "entry_points" not in source
        assert "console_scripts" not in source
        assert "sqlalchemy" not in source.lower()
        assert "stripe" not in source.lower()
        assert "ffprobe -" not in source.lower()
        assert "ffmpeg -" not in source.lower()

    assert "cid_media_agent_scan" not in cli_source
    assert "--preflight" not in renderer_source
    assert "--preflight" not in scanner_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source

def test_user_flow_spec_does_not_introduce_client_media_or_external_runtime_terms() -> None:
    combined = "\n".join(
        [
            _read(SPEC_DOC),
            _read(CLI_SCRIPT),
        ]
    ).lower()

    forbidden = [
        "client.mov",
        "customer.mov",
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
