from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_qa_gate_v1.md"
)
READINESS_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_gate_v1.md"
)
READINESS_TEST = REPO_ROOT / "tests" / "unit" / (
    "test_cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_gate.py"
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
    assert matches, "Approved synthetic fixture is required for packaging readiness QA gate."
    return matches[0]


def test_packaging_readiness_qa_doc_declares_phase_baseline_scope_and_decision() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.PACKAGING.READINESS.QA.GATE.V1" in text
    assert "Stable HEAD before this phase: `468ce98`." in text
    assert "This phase is documentation/test-only." in text
    assert "PACKAGING_READINESS_QA_GATE_READY_FOR_FUTURE_PACKAGING_DISCUSSION_WITH_RESTRICTIONS" in text
    assert "Allowed files for this phase:" in text
    assert "Runtime files may be audited by tests but must not be modified." in text


def test_packaging_readiness_qa_doc_references_target_gate_and_test() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.PACKAGING.READINESS.GATE.V1" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_gate_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_preflight_packaging_readiness_gate.py" in text
    assert READINESS_DOC.exists()
    assert READINESS_TEST.exists()


def test_packaging_readiness_qa_doc_keeps_packaging_non_implemented() -> None:
    text = _read(QA_DOC)

    required = [
        "It does not implement packaging",
        "does not create an installable command",
        "does not create a shell launcher",
        "does not modify runtime code",
        "keeps all packaging implementation and launcher work blocked.",
        "A future phase may discuss packaging implementation only if explicitly opened.",
    ]

    for item in required:
        assert item in text


def test_packaging_readiness_qa_doc_audits_required_assertions() -> None:
    text = _read(QA_DOC)

    required = [
        "declares the correct phase and stable baseline;",
        "references the completed user-flow spec QA gate;",
        "confirms that the controlled user-flow spec exists;",
        "confirms that the controlled user-flow spec QA gate exists;",
        "confirms preflight is required before generation;",
        "confirms generation remains a separate explicit step;",
        "confirms preflight pass does not generate the Markdown report;",
        "confirms preflight failures remain controlled with `PREFLIGHT_FAIL`;",
        "confirms missing output directories are not created by preflight;",
        "confirms existing output reports are not overwritten without explicit overwrite allowance;",
        "confirms generated reports still require human review;",
        "confirms wrapper, helper, renderer and scanner boundaries remain intact;",
    ]

    for item in required:
        assert item in text


def test_target_packaging_readiness_gate_contains_required_decision_and_chain() -> None:
    readiness_text = _read(READINESS_DOC)

    assert "PACKAGING_READINESS_GATE_READY_FOR_TEST_AUDIT_WITH_RESTRICTIONS" in readiness_text
    assert "Stable HEAD before this phase: `c733cc0`." in readiness_text
    assert "the controlled user-flow spec exists;" in readiness_text
    assert "the controlled user-flow spec QA gate exists;" in readiness_text
    assert USER_FLOW_SPEC_DOC.exists()
    assert USER_FLOW_SPEC_QA_DOC.exists()


def test_target_packaging_readiness_gate_preserves_preflight_generation_contract() -> None:
    readiness_text = _read(READINESS_DOC)

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
        assert item in readiness_text


def test_target_packaging_readiness_test_covers_live_and_boundary_assertions() -> None:
    test_text = _read(READINESS_TEST)

    required_tests = [
        "test_live_preflight_packaging_readiness_pass_does_not_generate_report",
        "test_live_generation_remains_separate_from_preflight",
        "test_live_preflight_failures_do_not_create_or_mutate_outputs",
        "test_runtime_sources_do_not_gain_packaging_or_launcher_contracts",
    ]

    for name in required_tests:
        assert name in test_text


def test_packaging_readiness_qa_and_target_gate_keep_all_blocked_scope_closed() -> None:
    combined = _read(QA_DOC) + "\n" + _read(READINESS_DOC)

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
        assert item in combined


def test_live_preflight_pass_does_not_generate_report_for_packaging_qa(tmp_path, capsys) -> None:
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


def test_live_generation_after_preflight_remains_explicit_for_packaging_qa(tmp_path, capsys) -> None:
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


def test_live_preflight_failures_remain_non_mutating_for_packaging_qa(tmp_path, capsys) -> None:
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


def test_runtime_sources_remain_free_of_packaging_entrypoints_and_launchers() -> None:
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
