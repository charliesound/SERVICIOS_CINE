from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

READINESS_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_gate_v1.md"
)
USER_FLOW_SPEC_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_v1.md"
)
USER_FLOW_SPEC_QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_qa_gate_v1.md"
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
    assert matches, "Approved synthetic fixture is required for packaging readiness gate."
    return matches[0]


def test_packaging_readiness_doc_declares_phase_baseline_and_decision() -> None:
    text = _read(READINESS_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.PACKAGING.READINESS.GATE.V1" in text
    assert "Stable HEAD before this phase: `c733cc0`." in text
    assert "This phase is documentation/test-only." in text
    assert "PACKAGING_READINESS_GATE_READY_FOR_TEST_AUDIT_WITH_RESTRICTIONS" in text
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.QA.GATE.V1" in text


def test_packaging_readiness_doc_explicitly_blocks_packaging_implementation() -> None:
    text = _read(READINESS_DOC)

    required = [
        "It does not implement packaging",
        "does not create an installable entry point",
        "does not add a shell launcher",
        "does not modify runtime code",
        "None of those concerns are implemented in this phase.",
        "packaging implementation;",
        "installable entry point;",
        "shell launcher;",
    ]

    for item in required:
        assert item in text


def test_packaging_readiness_doc_references_current_components_and_output() -> None:
    text = _read(READINESS_DOC)

    required = [
        "scripts/cid_local_media_agent_synthetic_visible_report_cli.py",
        "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py",
        "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py",
        "scripts/cid_media_agent_scan.py",
        "cid_local_media_agent_synthetic_visible_report_v1.md",
    ]

    for item in required:
        assert item in text


def test_packaging_readiness_requires_completed_user_flow_spec_chain() -> None:
    text = _read(READINESS_DOC)

    assert USER_FLOW_SPEC_DOC.exists()
    assert USER_FLOW_SPEC_QA_DOC.exists()
    assert "the controlled user-flow spec exists;" in text
    assert "the controlled user-flow spec QA gate exists;" in text

    spec_text = _read(USER_FLOW_SPEC_DOC)
    qa_text = _read(USER_FLOW_SPEC_QA_DOC)

    assert "USER_FLOW_SPEC_READY_FOR_QA_GATE_WITH_RESTRICTIONS" in spec_text
    assert "USER_FLOW_SPEC_QA_GATE_READY_FOR_NEXT_READINESS_PHASE_WITH_RESTRICTIONS" in qa_text


def test_packaging_readiness_conditions_preserve_preflight_user_flow() -> None:
    text = _read(READINESS_DOC)

    required = [
        "preflight is required before generation;",
        "generation remains a separate explicit step;",
        "preflight pass does not generate the Markdown report;",
        "preflight failure remains controlled with `PREFLIGHT_FAIL`;",
        "missing output directory is not created by preflight;",
        "existing output report is not overwritten without explicit overwrite allowance;",
        "generated reports still require human review;",
        "runtime wrapper, helper, renderer and scanner boundaries remain intact.",
    ]

    for item in required:
        assert item in text


def test_packaging_readiness_may_describe_future_concerns_without_implementing_them() -> None:
    text = _read(READINESS_DOC)

    future_concerns = [
        "command naming;",
        "install location;",
        "dependency declaration;",
        "offline/local-only messaging;",
        "overwrite policy visibility;",
        "fixture/output-dir validation messaging;",
        "human-review warning visibility.",
    ]

    for item in future_concerns:
        assert item in text

    assert "This readiness gate may describe future packaging concerns, but must not implement them." in text


def test_packaging_readiness_keeps_all_blocked_scope_closed() -> None:
    text = _read(READINESS_DOC)

    blocked = [
        "packaging implementation;",
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


def test_live_preflight_packaging_readiness_pass_does_not_generate_report(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()

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
    assert exit_code == 0
    assert "PREFLIGHT_PASS" in captured.out
    assert "OK: generado" not in captured.out
    assert not (tmp_path / OUTPUT_FILENAME).exists()


def test_live_generation_remains_separate_from_preflight(tmp_path, capsys) -> None:
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


def test_live_preflight_failures_do_not_create_or_mutate_outputs(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()

    missing_output_dir = tmp_path / "missing-output"

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
    assert "Traceback" not in missing_capture.err
    assert not missing_output_dir.exists()

    report = tmp_path / OUTPUT_FILENAME
    report.write_text("existing report", encoding="utf-8")

    existing_code = cli.main(
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
    existing_capture = capsys.readouterr()

    assert existing_code == 4
    assert "PREFLIGHT_FAIL" in existing_capture.err
    assert "reason=OUTPUT_ALREADY_EXISTS" in existing_capture.err
    assert "Traceback" not in existing_capture.err
    assert report.read_text(encoding="utf-8") == "existing report"


def test_runtime_sources_do_not_gain_packaging_or_launcher_contracts() -> None:
    cli_source = _read(CLI_SCRIPT)
    helper_source = _read(PREFLIGHT_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "--preflight" in cli_source
    assert "PREFLIGHT_PASS" in helper_source
    assert "PREFLIGHT_FAIL" in helper_source

    for source in [cli_source, helper_source, renderer_source, scanner_source]:
        assert "entry_points" not in source
        assert "console_scripts" not in source
        assert "setup(" not in source
        assert "pyproject" not in source.lower()
        assert "subprocess.run" not in source
        assert "ffprobe -" not in source.lower()
        assert "ffmpeg -" not in source.lower()
        assert "sqlalchemy" not in source.lower()
        assert "stripe" not in source.lower()

    assert "cid_media_agent_scan" not in cli_source
    assert "--preflight" not in renderer_source
    assert "--preflight" not in scanner_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source
