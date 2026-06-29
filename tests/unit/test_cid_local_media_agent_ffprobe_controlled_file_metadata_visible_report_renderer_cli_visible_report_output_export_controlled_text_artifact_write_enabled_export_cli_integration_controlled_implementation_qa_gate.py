from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.V1"

IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
QA_DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate_v1.md"

ALLOWED_OPTIONS = {
    "--visible-report-text",
    "--controlled-output-root",
    "--write-authorization",
    "--result-json",
    "--dry-run",
}

UNSAFE_ALIASES = {
    "--output",
    "--output-path",
    "--path",
    "--root",
    "--media-root",
    "--scanner-root",
    "--ffprobe-path",
    "--ffmpeg-path",
    "--force",
    "--overwrite",
    "--mkdir",
    "--create-dirs",
    "--cleanup",
    "--recursive",
    "--real-media",
    "--production",
    "--network",
    "--backend",
    "--frontend",
}

AUTHORIZATION_TOKEN = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
EXPECTED_ARTIFACT_NAME = "controlled_visible_report.controlled.txt"
EXPECTED_CLI_EXTENSION = ".txt"
DRY_RUN_STATUS = "DRY_RUN_ONLY"
VERIFIED_STATUS = "VERIFIED"
REJECTED_STATUS = "REJECTED"


class _DoubleDashOptionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.options: set[str] = set()

    def visit_Call(self, node: ast.Call) -> Any:
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("--"):
                self.options.add(arg.value)
        self.generic_visit(node)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _implementation_source() -> str:
    assert IMPLEMENTATION_PATH.exists(), f"Missing implementation module: {IMPLEMENTATION_PATH}"
    return _read(IMPLEMENTATION_PATH)


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("cid_lma_controlled_export_cli_under_qa", IMPLEMENTATION_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect_declared_cli_options(source: str) -> set[str]:
    tree = ast.parse(source)
    collector = _DoubleDashOptionCollector()
    collector.visit(tree)
    return collector.options


def _controlled_root(tmp_path: Path) -> Path:
    root = tmp_path / "fixture_owned_controlled_output_root"
    root.mkdir()
    return root


def _normalize_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if hasattr(result, "to_dict") and callable(result.to_dict):
        return result.to_dict()
    if hasattr(result, "__dict__") and not isinstance(result, type):
        return dict(result.__dict__)
    raise AssertionError(f"Unsupported result type: {type(result)!r}")


def _call_signature_runner(
    module: Any,
    *,
    visible_report_text: str,
    controlled_output_root: Path,
    write_authorization: str,
    dry_run: bool,
) -> dict[str, Any]:
    preferred_names = (
        "run_controlled_visible_report_write_enabled_export_cli",
        "run_visible_report_write_enabled_export_cli",
        "run_controlled_export_cli",
        "execute_controlled_visible_report_write_enabled_export",
        "execute_controlled_export",
        "run_cli",
        "execute",
        "run",
    )
    required = {"visible_report_text", "controlled_output_root", "write_authorization", "dry_run"}

    for name in preferred_names:
        candidate = getattr(module, name, None)
        if not callable(candidate):
            continue

        try:
            signature = inspect.signature(candidate)
        except (TypeError, ValueError):
            continue

        parameters = set(signature.parameters)
        if required <= parameters:
            kwargs: dict[str, Any] = {
                "visible_report_text": visible_report_text,
                "controlled_output_root": controlled_output_root,
                "write_authorization": write_authorization,
                "dry_run": dry_run,
            }
            if "result_json" in parameters:
                kwargs["result_json"] = True
            return _normalize_result(candidate(**kwargs))

    raise AssertionError("No callable runner with the authorized controlled export signature was found")


def _call_main_runner(
    module: Any,
    *,
    visible_report_text: str,
    controlled_output_root: Path,
    write_authorization: str,
    dry_run: bool,
) -> dict[str, Any]:
    main = getattr(module, "main", None)
    if not callable(main):
        raise AssertionError("No main(argv) runner is available")

    argv = [
        "--visible-report-text",
        visible_report_text,
        "--controlled-output-root",
        str(controlled_output_root),
        "--write-authorization",
        write_authorization,
        "--result-json",
    ]

    if dry_run:
        argv.append("--dry-run")

    stdout = io.StringIO()
    stderr = io.StringIO()

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            result = main(argv)
        except SystemExit as exc:
            result = exc.code

    printed = stdout.getvalue().strip()
    assert printed, f"Expected JSON output from CLI. stderr={stderr.getvalue()!r}, result={result!r}"

    payload = json.loads(printed.splitlines()[-1])
    assert isinstance(payload, dict)
    return payload


def _invoke_controlled_export(
    module: Any,
    *,
    visible_report_text: str,
    controlled_output_root: Path,
    write_authorization: str,
    dry_run: bool,
) -> dict[str, Any]:
    try:
        return _call_signature_runner(
            module,
            visible_report_text=visible_report_text,
            controlled_output_root=controlled_output_root,
            write_authorization=write_authorization,
            dry_run=dry_run,
        )
    except AssertionError:
        return _call_main_runner(
            module,
            visible_report_text=visible_report_text,
            controlled_output_root=controlled_output_root,
            write_authorization=write_authorization,
            dry_run=dry_run,
        )


def test_qa_gate_doc_and_test_exist_and_declare_phase() -> None:
    assert QA_DOC_PATH.exists()
    assert Path(__file__).exists()
    doc = _read(QA_DOC_PATH)
    test = _read(Path(__file__))
    assert PHASE in doc
    assert PHASE in test
    assert "doc/test-only" in doc
    assert "database regression guard" in doc


def test_authorized_implementation_and_previous_test_exist() -> None:
    assert IMPLEMENTATION_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()


def test_parser_surface_is_exactly_the_authorized_isolated_cli_surface() -> None:
    declared_options = _collect_declared_cli_options(_implementation_source())
    assert ALLOWED_OPTIONS.issubset(declared_options)
    assert declared_options <= ALLOWED_OPTIONS
    assert not (declared_options & UNSAFE_ALIASES)


def test_runtime_contract_keeps_authorization_token_artifact_name_and_cli_extension() -> None:
    module = _load_module()
    assert getattr(module, "WRITE_AUTHORIZATION") == AUTHORIZATION_TOKEN
    assert getattr(module, "FILENAME") == EXPECTED_ARTIFACT_NAME
    assert getattr(module, "EXTENSION") == EXPECTED_CLI_EXTENSION


def test_static_contract_keeps_dry_run_and_verified_statuses() -> None:
    source = _implementation_source()
    assert DRY_RUN_STATUS in source
    assert VERIFIED_STATUS in source
    assert "verification_status" in source


def test_static_contract_does_not_import_forbidden_modules() -> None:
    tree = ast.parse(_implementation_source())
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp"}
    forbidden.add("sub" + "process")

    assert imported_names.isdisjoint(forbidden)


def test_static_contract_does_not_expose_directory_creation_or_overwrite_controls() -> None:
    declared_options = _collect_declared_cli_options(_implementation_source())
    assert "--mkdir" not in declared_options
    assert "--create-dirs" not in declared_options
    assert "--overwrite" not in declared_options
    assert "--force" not in declared_options


def test_dry_run_result_is_non_writing_and_deterministic(tmp_path: Path) -> None:
    module = _load_module()
    root = _controlled_root(tmp_path)

    payload = _invoke_controlled_export(
        module,
        visible_report_text="# Controlled visible report\n\nFixture-only QA dry run.\n",
        controlled_output_root=root,
        write_authorization=AUTHORIZATION_TOKEN,
        dry_run=True,
    )

    assert payload.get("verification_status") == DRY_RUN_STATUS
    assert payload.get("write_performed") is False
    assert not (root / EXPECTED_ARTIFACT_NAME).exists()
    assert list(root.iterdir()) == []


def test_controlled_write_result_is_fixture_owned_single_artifact_and_verified(tmp_path: Path) -> None:
    module = _load_module()
    root = _controlled_root(tmp_path)
    visible_report_text = "# Controlled visible report\n\nFixture-only QA write.\n"
    expected_sha256 = hashlib.sha256(visible_report_text.encode("utf-8")).hexdigest()

    payload = _invoke_controlled_export(
        module,
        visible_report_text=visible_report_text,
        controlled_output_root=root,
        write_authorization=AUTHORIZATION_TOKEN,
        dry_run=False,
    )
    artifact_path = root / EXPECTED_ARTIFACT_NAME

    assert payload.get("verification_status") == VERIFIED_STATUS
    assert artifact_path.exists()
    assert artifact_path.read_text(encoding="utf-8") == visible_report_text
    assert hashlib.sha256(artifact_path.read_bytes()).hexdigest() == expected_sha256
    assert [path.name for path in root.iterdir()] == [EXPECTED_ARTIFACT_NAME]
    assert payload.get("extension") == EXPECTED_CLI_EXTENSION or EXPECTED_CLI_EXTENSION in json.dumps(payload)


def test_controlled_write_rejects_wrong_authorization_without_writing(tmp_path: Path) -> None:
    module = _load_module()
    root = _controlled_root(tmp_path)

    payload = _invoke_controlled_export(
        module,
        visible_report_text="Not authorized\n",
        controlled_output_root=root,
        write_authorization="WRONG_AUTHORIZATION",
        dry_run=False,
    )

    assert payload.get("verification_status") == REJECTED_STATUS
    assert payload.get("write_performed") is False
    assert list(root.iterdir()) == []


def test_result_json_flag_is_controlled_and_does_not_replace_artifact_contract(tmp_path: Path) -> None:
    module = _load_module()
    root = _controlled_root(tmp_path)

    payload = _invoke_controlled_export(
        module,
        visible_report_text="# Controlled visible report\n",
        controlled_output_root=root,
        write_authorization=AUTHORIZATION_TOKEN,
        dry_run=False,
    )

    assert (root / EXPECTED_ARTIFACT_NAME).exists()
    assert payload.get("verification_status") == VERIFIED_STATUS
    assert EXPECTED_ARTIFACT_NAME in json.dumps(payload) or payload.get("artifact_name") is None
