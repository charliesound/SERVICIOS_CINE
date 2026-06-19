from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
import io
import importlib.util
import json
from pathlib import Path
import sys


CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_contract_v1.md")


def _load_cli_module():
    scripts_dir = str(Path("scripts").resolve())
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_cli_under_test",
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


def test_cli_file_runtime_file_and_contract_exist():
    assert CLI_FILE.exists()
    assert RUNTIME_FILE.exists()
    assert CONTRACT_DOC.exists()


def test_cli_exposes_main_and_parser_only_as_public_functions():
    public_functions = {
        name
        for name, value in vars(cli).items()
        if callable(value) and not name.startswith("_")
    }
    assert "main" in public_functions
    assert "build_parser" in public_functions
    assert "run_real_preflight_check" in public_functions


def test_cli_pass_json_output_is_sanitized(tmp_path):
    input_folder = tmp_path / "PRIVATE_INPUT"
    output_folder = tmp_path / "PRIVATE_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_SCENE_001.mov"
    (input_folder / raw_filename).write_text("placeholder", encoding="utf-8")

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
    assert payload["media_file_count"] == 1
    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_INPUT" not in stdout
    assert "PRIVATE_OUTPUT" not in stdout


def test_cli_fail_json_output_maps_to_exit_code_2(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "notes.txt").write_text("placeholder", encoding="utf-8")

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    payload = json.loads(stdout)

    assert code == 2
    assert stderr == ""
    assert payload["status"] == "PREFLIGHT_FAIL"
    assert payload["exit_code"] == 2
    assert payload["failed_check_identifiers"] == ["ACCEPTED_EXTENSIONS_PRESENT"]


def test_cli_blocked_json_output_maps_to_exit_code_3(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = input_folder / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    payload = json.loads(stdout)

    assert code == 3
    assert stderr == ""
    assert payload["status"] == "PREFLIGHT_BLOCKED"
    assert payload["exit_code"] == 3
    assert payload["failed_check_identifiers"] == ["INPUT_OUTPUT_SEPARATED"]


def test_cli_usage_error_maps_to_exit_code_64_without_path_leak(tmp_path):
    private_path = tmp_path / "PRIVATE_CLIENT_FOLDER"

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(private_path),
        ]
    )

    assert code == 64
    assert stdout == ""
    assert "CLI_USAGE_ERROR" in stderr
    assert str(private_path) not in stderr
    assert "PRIVATE_CLIENT_FOLDER" not in stderr


def test_cli_text_output_is_sanitized(tmp_path):
    input_folder = tmp_path / "PRIVATE_INPUT"
    output_folder = tmp_path / "PRIVATE_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_SCENE_001.mov"
    (input_folder / raw_filename).write_text("placeholder", encoding="utf-8")

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
    assert "PRIVATE_INPUT" not in stdout
    assert "PRIVATE_OUTPUT" not in stdout


def test_cli_accepted_extension_argument_is_forwarded(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "synthetic.custom").write_text("placeholder", encoding="utf-8")

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
            "--accepted-extension",
            ".custom",
        ]
    )

    payload = json.loads(stdout)

    assert code == 0
    assert stderr == ""
    assert payload["status"] == "PREFLIGHT_PASS"
    assert payload["accepted_extension_counts"] == {".custom": 1}


def test_cli_limit_arguments_are_forwarded_fail_closed(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "b.wav").write_text("placeholder", encoding="utf-8")

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
            "--max-file-count",
            "1",
        ]
    )

    payload = json.loads(stdout)

    assert code == 3
    assert stderr == ""
    assert payload["status"] == "PREFLIGHT_BLOCKED"
    assert payload["failed_check_identifiers"] == ["MEDIA_FILE_COUNT_WITHIN_LIMIT"]


def test_cli_never_writes_to_selected_folders(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    before_input = sorted(path.name for path in input_folder.iterdir())
    before_output = sorted(path.name for path in output_folder.iterdir())

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    after_input = sorted(path.name for path in input_folder.iterdir())
    after_output = sorted(path.name for path in output_folder.iterdir())

    assert code == 0
    assert stderr == ""
    assert json.loads(stdout)["status"] == "PREFLIGHT_PASS"
    assert after_input == before_input
    assert after_output == before_output


def test_cli_parser_accepts_only_contract_arguments():
    parser = cli.build_parser()
    actions = {
        option
        for action in parser._actions
        for option in action.option_strings
        if option != "-h" and option != "--help"
    }

    assert actions == {
        "--input-folder",
        "--output-folder",
        "--max-file-count",
        "--max-total-size-bytes",
        "--max-scan-depth",
        "--accepted-extension",
        "--no-follow-symlinks",
        "--format",
    }


def test_cli_import_boundary_is_limited():
    tree = ast.parse(CLI_FILE.read_text(encoding="utf-8"))
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    allowed_modules = {
        "__future__",
        "argparse",
        "dataclasses",
        "json",
        "sys",
        "typing",
        "cid_local_media_agent_real_preflight",
    }

    assert imported_modules <= allowed_modules


def test_cli_source_does_not_reference_blocked_flows_or_tools():
    source = CLI_FILE.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "".join(["ff", "probe"]),
        "".join(["ff", "mpeg"]),
        "scanner",
        "transcription",
        "translation",
        "subtitle",
        "waveform",
        "thumbnail",
        "codec",
        "timecode",
        "davinci",
        "avid",
        "upload",
        "cloud",
        "billing",
        "license",
        "sqlalchemy",
        "requests",
        "httpx",
        "subprocess",
        "socket",
        "urllib",
    ]

    for term in forbidden_terms:
        assert term not in source


def test_cli_output_payload_contains_only_allowed_fields(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

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
    assert set(payload) == {
        "status",
        "sanitized_input_folder_label",
        "sanitized_output_folder_label",
        "media_file_count",
        "total_selected_media_size_bucket",
        "maximum_detected_scan_depth",
        "accepted_extension_counts",
        "ignored_extension_counts",
        "rejected_extension_counts",
        "failed_check_identifiers",
        "remediation_items",
        "exit_code",
    }


def test_cli_main_does_not_raise_system_exit_for_test_invocation(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    stdout = io.StringIO()
    stderr = io.StringIO()

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        code = cli.main(
            [
                "--input-folder",
                str(input_folder),
                "--output-folder",
                str(output_folder),
            ],
            stdout=stdout,
            stderr=stderr,
        )

    assert code == 0
    assert json.loads(stdout.getvalue())["status"] == "PREFLIGHT_PASS"
    assert stderr.getvalue() == ""
