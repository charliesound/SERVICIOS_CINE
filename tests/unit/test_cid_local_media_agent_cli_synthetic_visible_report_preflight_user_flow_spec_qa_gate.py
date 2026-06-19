from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_qa_gate_v1.md"
)
SPEC_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_v1.md"
)
SPEC_TEST = REPO_ROOT / "tests" / "unit" / (
    "test_cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec.py"
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
    assert matches, "Approved synthetic fixture is required for QA gate."
    return matches[0]


def test_qa_gate_doc_declares_phase_baseline_scope_and_decision() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.QA.GATE.V1" in text
    assert "Stable HEAD before this phase: `b8bda0b`." in text
    assert "This phase is documentation/test-only." in text
    assert "USER_FLOW_SPEC_QA_GATE_READY_FOR_NEXT_READINESS_PHASE_WITH_RESTRICTIONS" in text
    assert "Allowed files for this phase:" in text
    assert "Runtime files may be audited by tests but must not be modified." in text


def test_qa_gate_references_target_spec_and_existing_spec_test() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.USER.FLOW.SPEC.V1" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_preflight_user_flow_spec.py" in text
    assert SPEC_DOC.exists()
    assert SPEC_TEST.exists()


def test_qa_gate_audits_required_spec_assertions() -> None:
    text = _read(QA_DOC)

    required = [
        "declares the correct phase and stable baseline;",
        "references the previous readiness gate;",
        "defines preflight before generation;",
        "requires an approved synthetic fixture;",
        "requires an existing local output directory;",
        "states that preflight must not create the output directory;",
        "states that preflight must not generate `cid_local_media_agent_synthetic_visible_report_v1.md`;",
        "keeps generation as a separate explicit command;",
        "preserves controlled `PREFLIGHT_PASS` and `PREFLIGHT_FAIL` behavior;",
        "keeps human review mandatory;",
        "keeps renderer, scanner and helper boundaries intact;",
        "keeps all packaging, scanner integration, SaaS and real media work blocked.",
    ]

    for item in required:
        assert item in text


def test_target_spec_contains_all_controlled_user_flow_requirements() -> None:
    text = _read(SPEC_DOC)

    required = [
        "User chooses an approved synthetic fixture.",
        "User chooses an existing local output directory.",
        "User runs preflight before generation.",
        "System returns `PREFLIGHT_PASS` or controlled `PREFLIGHT_FAIL`.",
        "User generates only after `PREFLIGHT_PASS`.",
        "Human review remains mandatory for every generated report.",
        "Run preflight first. Generate only after PREFLIGHT_PASS. Review output manually.",
    ]

    for item in required:
        assert item in text


def test_target_spec_keeps_required_conditions_and_failures_safe() -> None:
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
        "missing fixture returns controlled `PREFLIGHT_FAIL`;",
        "missing output directory returns controlled `PREFLIGHT_FAIL`;",
        "existing output report without overwrite returns controlled `PREFLIGHT_FAIL`;",
        "helper failure returns controlled `PREFLIGHT_FAIL`;",
        "no Python traceback is expected in normal controlled failures;",
        "no raw JSON dump, secret, real media path or client material should be intentionally exposed.",
    ]

    for item in required:
        assert item in text


def test_qa_gate_and_target_spec_keep_all_blocked_scope_closed() -> None:
    combined = _read(QA_DOC) + "\n" + _read(SPEC_DOC)

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
        assert item in combined


def test_existing_spec_test_covers_live_preflight_generation_and_failure_paths() -> None:
    text = _read(SPEC_TEST)

    required_tests = [
        "test_preflight_spec_flow_pass_then_generation_is_explicit",
        "test_preflight_spec_flow_rejects_missing_output_dir_without_creating_it",
        "test_preflight_spec_flow_rejects_existing_report_without_overwrite",
        "test_runtime_boundaries_remain_free_of_packaging_scanner_and_media_processing",
        "test_user_flow_spec_does_not_introduce_client_media_or_external_runtime_terms",
    ]

    for name in required_tests:
        assert name in text


def test_live_preflight_pass_then_generation_remains_controlled(tmp_path, capsys) -> None:
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


def test_live_preflight_failures_remain_safe_and_non_mutating(tmp_path, capsys) -> None:
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

    existing_report = tmp_path / OUTPUT_FILENAME
    existing_report.write_text("existing report", encoding="utf-8")

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
    assert existing_report.read_text(encoding="utf-8") == "existing report"


def test_runtime_boundaries_remain_intact_for_spec_qa_gate() -> None:
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
