from __future__ import annotations

import ast
import io
import importlib.util
import json
from pathlib import Path
import sys


QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_qa_gate_v1.md")
CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
CLI_IMPL_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli.py")
CLI_CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_contract.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1"


def _load_cli_module():
    scripts_dir = str(Path("scripts").resolve())
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_cli_qa_gate_under_test",
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


def _qa_doc_text() -> str:
    assert QA_DOC.exists()
    return QA_DOC.read_text(encoding="utf-8")


def _cli_source() -> str:
    assert CLI_FILE.exists()
    return CLI_FILE.read_text(encoding="utf-8")


def test_cli_qa_gate_document_exists_and_contains_phase():
    assert QA_DOC.exists()
    assert PHASE in _qa_doc_text()


def test_cli_qa_gate_declares_no_scope_expansion():
    text = _qa_doc_text().lower()
    assert "does not add cli features" in text
    assert "does not widen cli scope" in text
    assert "does not process media content" in text


def test_prerequisite_files_exist():
    assert CLI_FILE.exists()
    assert CLI_IMPL_TEST.exists()
    assert CLI_CONTRACT_TEST.exists()
    assert RUNTIME_FILE.exists()


def test_cli_parser_accepts_only_approved_arguments():
    parser = cli.build_parser()
    actions = {
        option
        for action in parser._actions
        for option in action.option_strings
        if option not in {"-h", "--help"}
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


def test_cli_parser_output_formats_are_limited():
    parser = cli.build_parser()
    format_actions = [
        action
        for action in parser._actions
        if "--format" in action.option_strings
    ]
    assert len(format_actions) == 1
    assert tuple(format_actions[0].choices) == ("json", "text")
    assert format_actions[0].default == "json"


def test_cli_import_boundary_is_limited_to_approved_modules():
    tree = ast.parse(_cli_source())
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
        "argparse",
        "dataclasses",
        "json",
        "sys",
        "typing",
        "cid_local_media_agent_real_preflight",
    }


def test_cli_source_does_not_reference_blocked_operations_or_integrations():
    source = _cli_source().lower()
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


def test_cli_source_has_no_file_creation_or_deletion_calls():
    source = _cli_source()
    forbidden_snippets = [
        ".write_text(",
        ".write_bytes(",
        ".read_text(",
        ".read_bytes(",
        ".touch(",
        ".mkdir(",
        ".unlink(",
        ".rename(",
        ".replace(",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in source


def test_cli_json_pass_output_is_sanitized_and_exit_code_zero(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_SCENE_001_TAKE_004.mov"
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
    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout


def test_cli_text_pass_output_is_sanitized(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET_SCENE_001_TAKE_004.mov"
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
    assert "PRIVATE_CLIENT" not in stdout


def test_cli_fail_output_maps_to_exit_code_two(tmp_path):
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


def test_cli_blocked_output_maps_to_exit_code_three(tmp_path):
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


def test_cli_invalid_usage_maps_to_exit_code_sixty_four_without_leak(tmp_path):
    private_path = tmp_path / "PRIVATE_CLIENT_INPUT"

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
    assert "PRIVATE_CLIENT_INPUT" not in stderr
    assert "Traceback" not in stderr


def test_cli_internal_error_maps_to_exit_code_seventy_without_leak(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    original = cli.run_real_preflight_check

    def _raise_error(_request):
        raise RuntimeError("PRIVATE_CLIENT_INTERNAL_PATH_SHOULD_NOT_LEAK")

    try:
        cli.run_real_preflight_check = _raise_error
        code, stdout, stderr = _run_cli(
            [
                "--input-folder",
                str(input_folder),
                "--output-folder",
                str(output_folder),
            ]
        )
    finally:
        cli.run_real_preflight_check = original

    assert code == 70
    assert stdout == ""
    assert "CLI_INTERNAL_ERROR" in stderr
    assert "PRIVATE_CLIENT" not in stderr
    assert str(input_folder) not in stderr
    assert str(output_folder) not in stderr
    assert "Traceback" not in stderr


def test_cli_json_payload_contains_only_approved_fields(tmp_path):
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


def test_cli_forwards_accepted_extension_without_filename_leak(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()
    raw_filename = "CLIENT_SECRET.custom"
    (input_folder / raw_filename).write_text("placeholder", encoding="utf-8")

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
    assert payload["accepted_extension_counts"] == {".custom": 1}
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout


def test_cli_forwards_limit_arguments_fail_closed(tmp_path):
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


def test_cli_does_not_write_to_selected_folders(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    input_before = sorted(path.name for path in input_folder.iterdir())
    output_before = sorted(path.name for path in output_folder.iterdir())

    code, stdout, stderr = _run_cli(
        [
            "--input-folder",
            str(input_folder),
            "--output-folder",
            str(output_folder),
        ]
    )

    input_after = sorted(path.name for path in input_folder.iterdir())
    output_after = sorted(path.name for path in output_folder.iterdir())

    assert code == 0
    assert stderr == ""
    assert json.loads(stdout)["status"] == "PREFLIGHT_PASS"
    assert input_after == input_before
    assert output_after == output_before


def test_cli_qa_doc_acceptance_criteria_are_present():
    text = _qa_doc_text().lower()
    required = [
        "the cli qa gate document exists",
        "the cli implementation file exists",
        "the cli implementation test exists",
        "the cli contract test exists",
        "the runtime file exists",
        "the cli accepts only approved arguments",
        "the cli import boundary is verified",
        "blocked operation terms are absent from cli source",
        "json output is sanitized",
        "text output is sanitized",
        "private paths are never printed",
        "raw filenames are never printed",
        "exit code mapping is verified",
        "invalid usage returns sanitized exit code `64`",
        "internal errors return sanitized exit code `70`",
        "selected input and output folders are not modified by the cli",
        "previous cli implementation tests still pass",
        "previous cli contract tests still pass",
        "previous runtime qa tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
