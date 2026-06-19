from __future__ import annotations

import ast
from dataclasses import asdict
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys

import pytest


RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_contract_v1.md")


def _load_runtime_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_runtime_under_test",
        RUNTIME_FILE,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runtime = _load_runtime_module()


def _make_request(input_folder, output_folder, **kwargs):
    return runtime.RealPreflightRequest(
        input_folder_path=input_folder,
        output_folder_path=output_folder,
        **kwargs,
    )


def _serialized_result(result) -> str:
    return json.dumps(asdict(result), sort_keys=True)


def test_runtime_file_exists_and_contract_exists():
    assert RUNTIME_FILE.exists()
    assert CONTRACT_DOC.exists()


def test_runtime_exposes_contract_objects_and_single_public_function():
    assert hasattr(runtime, "RealPreflightRequest")
    assert hasattr(runtime, "RealPreflightResult")
    assert hasattr(runtime, "run_real_preflight_check")

    public_functions = [
        name
        for name, value in inspect.getmembers(runtime, inspect.isfunction)
        if not name.startswith("_")
    ]
    assert public_functions == ["run_real_preflight_check"]


def test_runtime_uses_contract_result_states():
    assert runtime.PREFLIGHT_PASS == "PREFLIGHT_PASS"
    assert runtime.PREFLIGHT_FAIL == "PREFLIGHT_FAIL"
    assert runtime.PREFLIGHT_BLOCKED == "PREFLIGHT_BLOCKED"


def test_preflight_passes_with_synthetic_accepted_placeholders(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "synthetic_a.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "synthetic_b.WAV").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_PASS
    assert result.media_file_count == 2
    assert result.accepted_extension_counts == {".mov": 1, ".wav": 1}
    assert result.failed_check_identifiers == ()
    assert result.sanitized_input_folder_label == "selected_input_folder"
    assert result.sanitized_output_folder_label == "selected_output_folder"


def test_result_does_not_expose_private_paths_or_raw_filenames(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_PROJECT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_PROJECT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()

    private_filename = "CLIENT_SECRET_SCENE_001_TAKE_002.mov"
    (input_folder / private_filename).write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))
    serialized = _serialized_result(result)

    assert result.status == runtime.PREFLIGHT_PASS
    assert private_filename not in serialized
    assert str(input_folder) not in serialized
    assert str(output_folder) not in serialized
    assert "PRIVATE_CLIENT_PROJECT" not in serialized


def test_mixed_extensions_are_counted_without_filename_leak(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "accepted.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "rejected.txt").write_text("placeholder", encoding="utf-8")
    (input_folder / "ignored").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))
    serialized = _serialized_result(result)

    assert result.status == runtime.PREFLIGHT_PASS
    assert result.accepted_extension_counts == {".mov": 1}
    assert result.rejected_extension_counts == {".txt": 1}
    assert result.ignored_extension_counts == {"<no_extension>": 1}
    assert "accepted.mov" not in serialized
    assert "rejected.txt" not in serialized


def test_no_accepted_media_like_files_returns_fail_not_pass(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "notes.txt").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_FAIL
    assert result.media_file_count == 0
    assert result.failed_check_identifiers == ("ACCEPTED_EXTENSIONS_PRESENT",)


def test_missing_input_folder_blocks(tmp_path):
    output_folder = tmp_path / "output"
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(
        _make_request(tmp_path / "missing_input", output_folder)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_FOLDER_EXISTS",)


def test_input_path_that_is_file_blocks(tmp_path):
    input_file = tmp_path / "not_a_folder.mov"
    output_folder = tmp_path / "output"
    input_file.write_text("placeholder", encoding="utf-8")
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(_make_request(input_file, output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_FOLDER_IS_DIRECTORY",)


def test_output_inside_input_blocks(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = input_folder / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_OUTPUT_SEPARATED",)


def test_output_file_blocks_as_not_preparable(tmp_path):
    input_folder = tmp_path / "input"
    output_file = tmp_path / "output.txt"
    input_folder.mkdir()
    output_file.write_text("placeholder", encoding="utf-8")
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_file))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("OUTPUT_FOLDER_PREPARABLE",)


def test_missing_output_parent_blocks(tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, tmp_path / "missing_parent" / "output")
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("OUTPUT_FOLDER_PREPARABLE",)


def test_request_to_follow_symlinks_blocks(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, follow_symlinks=True)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SYMLINKS_NOT_FOLLOWED",)


def test_symlink_inside_input_blocks_without_following(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    target_folder = tmp_path / "target"
    input_folder.mkdir()
    output_folder.mkdir()
    target_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    try:
        os.symlink(target_folder, input_folder / "linked_folder")
    except OSError:
        pytest.skip("symlinks are not available on this platform")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SYMLINKS_NOT_FOLLOWED",)


def test_scan_depth_limit_blocks(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    nested_folder = input_folder / "level_1"
    nested_folder.mkdir(parents=True)
    output_folder.mkdir()
    (nested_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_scan_depth=0)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SCAN_DEPTH_WITHIN_LIMIT",)
    assert result.maximum_detected_scan_depth == 1


def test_file_count_limit_blocks(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "one.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "two.wav").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_file_count=1)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("MEDIA_FILE_COUNT_WITHIN_LIMIT",)
    assert result.media_file_count == 2


def test_total_size_limit_blocks_using_metadata_only(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_total_size_bytes=1)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("TOTAL_MEDIA_SIZE_WITHIN_LIMIT",)


def test_windows_style_path_blocks_as_not_local(tmp_path):
    output_folder = tmp_path / "output"
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(
        _make_request("C:\\PRIVATE\\PROJECT", output_folder)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_FOLDER_LOCAL_ONLY",)


def test_mounted_path_blocks_as_not_local(tmp_path):
    output_folder = tmp_path / "output"
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(
        _make_request("/mnt/c/PRIVATE/PROJECT", output_folder)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_FOLDER_LOCAL_ONLY",)


def test_invalid_request_type_blocks_fail_closed():
    result = runtime.run_real_preflight_check(object())

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SANITIZED_PAYLOAD_READY",)


def test_invalid_numeric_limits_block_fail_closed(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_file_count=0)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("MEDIA_FILE_COUNT_WITHIN_LIMIT",)


def test_runtime_does_not_create_outputs_or_write_inside_selected_folders(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "synthetic.mov").write_text("placeholder", encoding="utf-8")

    input_before = sorted(path.name for path in input_folder.iterdir())
    output_before = sorted(path.name for path in output_folder.iterdir())

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    input_after = sorted(path.name for path in input_folder.iterdir())
    output_after = sorted(path.name for path in output_folder.iterdir())

    assert result.status == runtime.PREFLIGHT_PASS
    assert input_after == input_before
    assert output_after == output_before


def test_runtime_import_boundary_avoids_blocked_modules():
    tree = ast.parse(RUNTIME_FILE.read_text(encoding="utf-8"))
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    forbidden_imports = {
        ".".join(["scripts", "cid_media_agent_scan"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_cli"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_preflight_check"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_renderer"]),
        "subprocess",
        "requests",
        "httpx",
        "sqlalchemy",
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_runtime_source_does_not_reference_media_processing_tools_or_flows():
    source = RUNTIME_FILE.read_text(encoding="utf-8").lower()
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
    ]

    for term in forbidden_terms:
        assert term not in source
