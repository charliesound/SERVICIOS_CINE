from __future__ import annotations

import ast
import io
import importlib.util
import json
from pathlib import Path
import sys


QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate_v1.md")
SMOKE_DEMO_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py")
SMOKE_DEMO_CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md")
CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.QA.GATE.V1"


def _qa_doc_text() -> str:
    assert QA_DOC.exists()
    return QA_DOC.read_text(encoding="utf-8")


def _smoke_source() -> str:
    assert SMOKE_DEMO_TEST.exists()
    return SMOKE_DEMO_TEST.read_text(encoding="utf-8")


def _load_cli_module():
    scripts_dir = str(Path("scripts").resolve())
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_cli_smoke_demo_qa_gate_under_test",
        CLI_FILE,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cli = _load_cli_module()


def _run_cli(args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cli.main(args, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def _folder_snapshot(folder: Path) -> tuple[tuple[str, int], ...]:
    return tuple(sorted((path.name, path.stat().st_size) for path in folder.iterdir()))


def test_smoke_demo_qa_gate_document_exists_and_contains_phase():
    assert QA_DOC.exists()
    assert PHASE in _qa_doc_text()


def test_smoke_demo_qa_gate_declares_no_scope_expansion():
    text = _qa_doc_text().lower()
    assert "does not add smoke/demo features" in text
    assert "does not widen cli scope" in text
    assert "does not use real client media" in text
    assert "does not process media content" in text


def test_prerequisite_files_exist():
    assert SMOKE_DEMO_TEST.exists()
    assert SMOKE_DEMO_CONTRACT_DOC.exists()
    assert CLI_FILE.exists()
    assert RUNTIME_FILE.exists()


def test_smoke_demo_source_import_boundary_is_limited():
    tree = ast.parse(_smoke_source())
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    assert imported_modules <= {
        "__future__",
        "io",
        "importlib.util",
        "json",
        "pathlib",
        "sys",
    }


def test_smoke_demo_source_has_no_blocked_operation_terms():
    source = _smoke_source().lower()
    forbidden_terms = [
        "".join(["ff", "probe"]),
        "".join(["ff", "mpeg"]),
        "".join(["scan", "ner"]),
        "".join(["trans", "cription"]),
        "".join(["trans", "lation"]),
        "".join(["sub", "title"]),
        "".join(["wave", "form"]),
        "".join(["thumb", "nail"]),
        "".join(["co", "dec"]),
        "".join(["time", "code"]),
        "".join(["da", "vinci"]),
        "".join(["av", "id"]),
        "".join(["up", "load"]),
        "".join(["cl", "oud"]),
        "".join(["bill", "ing"]),
        "".join(["lic", "ense"]),
        "".join(["sql", "alchemy"]),
        "".join(["re", "quests"]),
        "".join(["ht", "tpx"]),
        "".join(["sub", "process"]),
        "".join(["/m", "nt/"]),
        "".join(["c", ":\\"]),
    ]

    for term in forbidden_terms:
        assert term not in source


def test_smoke_demo_source_uses_only_synthetic_temporary_fixtures():
    source = _smoke_source().lower()

    assert "tmp_path" in source
    assert "synthetic placeholder" in source
    assert "client_secret" in source
    assert "private_client" in source

    forbidden_real_path_markers = [
        "/home/harliesound/",
        "/opt/servicios_cine/",
        "c:\\",
        "onedrive",
        "dropbox",
        "google drive",
        "network share",
    ]
    for marker in forbidden_real_path_markers:
        assert marker not in source


def test_json_pass_case_is_sanitized_and_no_write(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_SCENE_001.mov"
    (input_folder / raw_filename).write_text("synthetic placeholder", encoding="utf-8")

    input_before = _folder_snapshot(input_folder)
    output_before = _folder_snapshot(output_folder)

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    payload = json.loads(stdout)

    assert code == 0
    assert stderr == ""
    assert payload["status"] == "PREFLIGHT_PASS"
    assert payload["exit_code"] == 0
    assert payload["sanitized_input_folder_label"] == "selected_input_folder"
    assert payload["sanitized_output_folder_label"] == "selected_output_folder"
    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout
    assert "CLIENT_SECRET" not in stdout
    assert _folder_snapshot(input_folder) == input_before
    assert _folder_snapshot(output_folder) == output_before


def test_text_pass_case_is_sanitized(tmp_path):
    input_folder = tmp_path / "PRIVATE_PROJECT_INPUT"
    output_folder = tmp_path / "PRIVATE_PROJECT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_AUDIO.wav"
    (input_folder / raw_filename).write_text("synthetic placeholder", encoding="utf-8")

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
            "--format",
            "text",
        ]
    )

    assert code == 0
    assert stderr == ""
    assert "status=PREFLIGHT_PASS" in stdout
    assert "exit_code=0" in stdout
    assert "selected_input_folder" in stdout
    assert "selected_output_folder" in stdout
    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_PROJECT" not in stdout
    assert "CLIENT_SECRET" not in stdout


def test_exit_code_mapping_for_fail_blocked_and_invalid_usage(tmp_path):
    fail_input = tmp_path / "fail_input"
    fail_output = tmp_path / "fail_output"
    fail_input.mkdir()
    fail_output.mkdir()
    (fail_input / "synthetic_notes.txt").write_text("synthetic placeholder", encoding="utf-8")

    fail_code, fail_stdout, fail_stderr = _run_cli(
        ["--input-folder", str(fail_input), "--output-folder", str(fail_output)]
    )

    blocked_input = tmp_path / "blocked_input"
    blocked_output = blocked_input / "blocked_output"
    blocked_input.mkdir()
    blocked_output.mkdir()
    (blocked_input / "synthetic.mov").write_text("synthetic placeholder", encoding="utf-8")

    blocked_code, blocked_stdout, blocked_stderr = _run_cli(
        ["--input-folder", str(blocked_input), "--output-folder", str(blocked_output)]
    )

    private_path = tmp_path / "PRIVATE_CLIENT_INPUT"
    usage_code, usage_stdout, usage_stderr = _run_cli(
        ["--input-folder", str(private_path)]
    )

    assert fail_code == 2
    assert fail_stderr == ""
    assert json.loads(fail_stdout)["status"] == "PREFLIGHT_FAIL"

    assert blocked_code == 3
    assert blocked_stderr == ""
    assert json.loads(blocked_stdout)["status"] == "PREFLIGHT_BLOCKED"

    assert usage_code == 64
    assert usage_stdout == ""
    assert "CLI_USAGE_ERROR" in usage_stderr
    assert str(private_path) not in usage_stderr
    assert "PRIVATE_CLIENT_INPUT" not in usage_stderr
    assert "Traceback" not in usage_stderr


def test_custom_extension_and_file_count_limit_remain_sanitized(tmp_path):
    custom_input = tmp_path / "PRIVATE_CLIENT_CUSTOM_INPUT"
    custom_output = tmp_path / "PRIVATE_CLIENT_CUSTOM_OUTPUT"
    custom_input.mkdir()
    custom_output.mkdir()
    raw_filename = "CLIENT_SECRET_CAMERA_CARD.custom"
    (custom_input / raw_filename).write_text("synthetic placeholder", encoding="utf-8")

    custom_code, custom_stdout, custom_stderr = _run_cli(
        [
            "--input-folder",
            str(custom_input),
            "--output-folder",
            str(custom_output),
            "--accepted-extension",
            ".custom",
        ]
    )

    limit_input = tmp_path / "limit_input"
    limit_output = tmp_path / "limit_output"
    limit_input.mkdir()
    limit_output.mkdir()
    (limit_input / "synthetic_a.mov").write_text("synthetic placeholder", encoding="utf-8")
    (limit_input / "synthetic_b.wav").write_text("synthetic placeholder", encoding="utf-8")

    limit_code, limit_stdout, limit_stderr = _run_cli(
        [
            "--input-folder",
            str(limit_input),
            "--output-folder",
            str(limit_output),
            "--max-file-count",
            "1",
        ]
    )

    custom_payload = json.loads(custom_stdout)
    limit_payload = json.loads(limit_stdout)

    assert custom_code == 0
    assert custom_stderr == ""
    assert custom_payload["accepted_extension_counts"] == {".custom": 1}
    assert raw_filename not in custom_stdout
    assert "PRIVATE_CLIENT" not in custom_stdout

    assert limit_code == 3
    assert limit_stderr == ""
    assert limit_payload["status"] == "PREFLIGHT_BLOCKED"
    assert limit_payload["failed_check_identifiers"] == ["MEDIA_FILE_COUNT_WITHIN_LIMIT"]
    assert "synthetic_a.mov" not in limit_stdout
    assert "synthetic_b.wav" not in limit_stdout


def test_output_folder_remains_empty_and_input_is_unchanged(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("synthetic placeholder", encoding="utf-8")
    (input_folder / "synthetic.wav").write_text("synthetic placeholder", encoding="utf-8")

    input_before = _folder_snapshot(input_folder)
    output_before = _folder_snapshot(output_folder)

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    assert code == 0
    assert stderr == ""
    assert json.loads(stdout)["status"] == "PREFLIGHT_PASS"
    assert _folder_snapshot(input_folder) == input_before
    assert _folder_snapshot(output_folder) == output_before
    assert list(output_folder.iterdir()) == []


def test_qa_doc_acceptance_criteria_are_present():
    text = _qa_doc_text().lower()
    required = [
        "the smoke/demo qa gate document exists",
        "the smoke/demo implementation test exists",
        "the smoke/demo contract document exists",
        "the cli file exists",
        "the runtime file exists",
        "the smoke/demo remains synthetic-only",
        "the smoke/demo uses temporary folders",
        "the smoke/demo uses placeholder files only",
        "json output sanitization is verified",
        "text output sanitization is verified",
        "exit code mapping is verified",
        "no private path leakage is verified",
        "no raw filename leakage is verified",
        "selected output folder no-write behavior is verified",
        "selected input folder no-change-after-fixture-setup behavior is verified",
        "smoke/demo source import boundaries are verified",
        "blocked operation terms are absent from smoke/demo source",
        "previous smoke/demo implementation tests still pass",
        "previous smoke/demo contract tests still pass",
        "previous cli qa tests still pass",
        "previous cli implementation tests still pass",
        "previous runtime tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
