from __future__ import annotations

import io
import importlib.util
import json
from pathlib import Path
import sys


CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md")


def _load_cli_module():
    scripts_dir = str(Path("scripts").resolve())
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_cli_smoke_demo_under_test",
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


def test_smoke_demo_prerequisite_files_exist():
    assert CLI_FILE.exists()
    assert RUNTIME_FILE.exists()
    assert CONTRACT_DOC.exists()


def test_smoke_demo_json_pass_case_is_sanitized(tmp_path):
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
    assert payload["media_file_count"] == 1
    assert payload["sanitized_input_folder_label"] == "selected_input_folder"
    assert payload["sanitized_output_folder_label"] == "selected_output_folder"

    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout
    assert "CLIENT_SECRET" not in stdout

    assert _folder_snapshot(input_folder) == input_before
    assert _folder_snapshot(output_folder) == output_before


def test_smoke_demo_text_pass_case_is_sanitized(tmp_path):
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


def test_smoke_demo_fail_case_with_no_accepted_extension(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "synthetic_notes.txt").write_text("synthetic placeholder", encoding="utf-8")

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
    assert "synthetic_notes.txt" not in stdout


def test_smoke_demo_blocked_case_output_inside_input(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = input_folder / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()

    raw_filename = "CLIENT_SECRET_SCENE_001.mov"
    (input_folder / raw_filename).write_text("synthetic placeholder", encoding="utf-8")

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

    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout


def test_smoke_demo_custom_accepted_extension_forwarding_is_sanitized(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()

    raw_filename = "CLIENT_SECRET_CAMERA_CARD.custom"
    (input_folder / raw_filename).write_text("synthetic placeholder", encoding="utf-8")

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
    assert raw_filename not in stdout
    assert "PRIVATE_CLIENT" not in stdout
    assert str(input_folder) not in stdout
    assert str(output_folder) not in stdout


def test_smoke_demo_file_count_limit_forwarding_blocks_safely(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "synthetic_a.mov").write_text("synthetic placeholder", encoding="utf-8")
    (input_folder / "synthetic_b.wav").write_text("synthetic placeholder", encoding="utf-8")

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
    assert payload["exit_code"] == 3
    assert payload["failed_check_identifiers"] == ["MEDIA_FILE_COUNT_WITHIN_LIMIT"]
    assert "synthetic_a.mov" not in stdout
    assert "synthetic_b.wav" not in stdout


def test_smoke_demo_invalid_usage_error_is_sanitized(tmp_path):
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
    assert "Traceback" not in stderr
    assert str(private_path) not in stderr
    assert "PRIVATE_CLIENT_INPUT" not in stderr


def test_smoke_demo_output_folder_remains_empty_after_invocation(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "synthetic.mov").write_text("synthetic placeholder", encoding="utf-8")

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
    assert list(output_folder.iterdir()) == []


def test_smoke_demo_input_folder_contains_only_precreated_fixtures_after_invocation(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "synthetic.mov").write_text("synthetic placeholder", encoding="utf-8")
    (input_folder / "synthetic.wav").write_text("synthetic placeholder", encoding="utf-8")

    input_before = _folder_snapshot(input_folder)

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


def test_smoke_demo_source_does_not_reference_real_media_or_integration_flows():
    source = Path(__file__).read_text(encoding="utf-8").lower()

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
        "".join(["c", ":\\\\"]),
    ]

    for term in forbidden_terms:
        assert term not in source
