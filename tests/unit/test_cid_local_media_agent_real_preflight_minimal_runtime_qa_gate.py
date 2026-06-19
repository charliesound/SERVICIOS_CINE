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


QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_qa_gate_v1.md")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime.py")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_contract_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1"


def _load_runtime_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_real_preflight_runtime_qa_gate_under_test",
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


def _runtime_source() -> str:
    return RUNTIME_FILE.read_text(encoding="utf-8")


def test_qa_gate_document_exists_and_contains_phase():
    assert QA_DOC.exists()
    assert PHASE in QA_DOC.read_text(encoding="utf-8")


def test_qa_gate_declares_no_scope_expansion():
    text = QA_DOC.read_text(encoding="utf-8").lower()
    assert "does not add runtime features" in text
    assert "does not widen the implementation scope" in text
    assert "does not process media content" in text


def test_runtime_contract_and_implementation_test_exist():
    assert RUNTIME_FILE.exists()
    assert CONTRACT_DOC.exists()
    assert RUNTIME_TEST.exists()


def test_runtime_public_surface_is_minimal():
    assert hasattr(runtime, "RealPreflightRequest")
    assert hasattr(runtime, "RealPreflightResult")
    assert hasattr(runtime, "run_real_preflight_check")

    public_functions = [
        name
        for name, value in inspect.getmembers(runtime, inspect.isfunction)
        if not name.startswith("_")
    ]
    assert public_functions == ["run_real_preflight_check"]


def test_request_shape_matches_contract():
    fields = set(runtime.RealPreflightRequest.__dataclass_fields__)
    assert fields == {
        "input_folder_path",
        "output_folder_path",
        "max_file_count",
        "max_total_size_bytes",
        "max_scan_depth",
        "accepted_extensions",
        "follow_symlinks",
    }


def test_result_shape_matches_contract():
    fields = set(runtime.RealPreflightResult.__dataclass_fields__)
    assert fields == {
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
    }


def test_result_states_are_exact_contract_states():
    assert runtime.PREFLIGHT_PASS == "PREFLIGHT_PASS"
    assert runtime.PREFLIGHT_FAIL == "PREFLIGHT_FAIL"
    assert runtime.PREFLIGHT_BLOCKED == "PREFLIGHT_BLOCKED"


def test_runtime_import_boundary_is_standard_library_only():
    tree = ast.parse(_runtime_source())
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
        "collections",
        "dataclasses",
        "os",
        "pathlib",
        "typing",
    }

    assert imported_modules <= allowed_modules


def test_runtime_does_not_import_forbidden_runtime_areas():
    tree = ast.parse(_runtime_source())
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
        "socket",
        "urllib",
        "shutil",
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_runtime_source_has_no_blocked_operation_terms():
    source = _runtime_source().lower()
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


def test_runtime_does_not_read_or_write_file_contents():
    source = _runtime_source()
    forbidden_snippets = [
        "open(",
        ".read(",
        ".read_text(",
        ".read_bytes(",
        ".write(",
        ".write_text(",
        ".write_bytes(",
        ".touch(",
        ".mkdir(",
        ".unlink(",
        ".rename(",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in source


def test_runtime_passes_synthetic_local_filesystem_metadata_case(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "b.wav").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_PASS
    assert result.media_file_count == 2
    assert result.accepted_extension_counts == {".mov": 1, ".wav": 1}


def test_runtime_fail_case_for_no_supported_files_is_not_pass(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()

    (input_folder / "notes.txt").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_FAIL
    assert result.failed_check_identifiers == ("ACCEPTED_EXTENSIONS_PRESENT",)


def test_runtime_block_case_for_invalid_request_is_fail_closed():
    result = runtime.run_real_preflight_check({"not": "a request"})

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SANITIZED_PAYLOAD_READY",)


def test_runtime_blocks_output_inside_input(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = input_folder / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_OUTPUT_SEPARATED",)


def test_runtime_blocks_non_local_path_patterns(tmp_path):
    output_folder = tmp_path / "output"
    output_folder.mkdir()

    result = runtime.run_real_preflight_check(_make_request("/mnt/c/private/project", output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("INPUT_FOLDER_LOCAL_ONLY",)


def test_runtime_blocks_depth_limit_exceeded(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    nested = input_folder / "level_1"
    nested.mkdir(parents=True)
    output_folder.mkdir()
    (nested / "a.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_scan_depth=0)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SCAN_DEPTH_WITHIN_LIMIT",)


def test_runtime_blocks_file_count_limit_exceeded(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")
    (input_folder / "b.wav").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_file_count=1)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("MEDIA_FILE_COUNT_WITHIN_LIMIT",)


def test_runtime_blocks_total_size_limit_exceeded_using_metadata(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(
        _make_request(input_folder, output_folder, max_total_size_bytes=1)
    )

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("TOTAL_MEDIA_SIZE_WITHIN_LIMIT",)


def test_runtime_blocks_symlink_without_following_when_supported(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    target = tmp_path / "target"
    input_folder.mkdir()
    output_folder.mkdir()
    target.mkdir()

    try:
        os.symlink(target, input_folder / "linked_folder")
    except OSError:
        pytest.skip("symlinks are not available on this platform")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_BLOCKED
    assert result.failed_check_identifiers == ("SYMLINKS_NOT_FOLLOWED",)


def test_runtime_does_not_write_to_selected_input_or_output(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    input_before = sorted(path.name for path in input_folder.iterdir())
    output_before = sorted(path.name for path in output_folder.iterdir())

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    input_after = sorted(path.name for path in input_folder.iterdir())
    output_after = sorted(path.name for path in output_folder.iterdir())

    assert result.status == runtime.PREFLIGHT_PASS
    assert input_after == input_before
    assert output_after == output_before


def test_runtime_result_never_leaks_private_paths_or_raw_filenames(tmp_path):
    input_folder = tmp_path / "PRIVATE_CLIENT_PROJECT_INPUT"
    output_folder = tmp_path / "PRIVATE_CLIENT_PROJECT_OUTPUT"
    input_folder.mkdir()
    output_folder.mkdir()

    raw_filename = "CLIENT_SECRET_SCENE_001_TAKE_004.mov"
    (input_folder / raw_filename).write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))
    serialized = _serialized_result(result)

    assert result.status == runtime.PREFLIGHT_PASS
    assert raw_filename not in serialized
    assert str(input_folder) not in serialized
    assert str(output_folder) not in serialized
    assert "PRIVATE_CLIENT_PROJECT" not in serialized


def test_runtime_reports_only_coarse_size_buckets(tmp_path):
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    output_folder.mkdir()
    (input_folder / "a.mov").write_text("placeholder", encoding="utf-8")

    result = runtime.run_real_preflight_check(_make_request(input_folder, output_folder))

    assert result.status == runtime.PREFLIGHT_PASS
    assert result.total_selected_media_size_bucket in {"0B", "<=100MB", "<=1GB", "<=10GB", ">10GB"}
    assert result.total_selected_media_size_bucket == "<=100MB"


def test_qa_doc_acceptance_criteria_are_present():
    text = QA_DOC.read_text(encoding="utf-8").lower()
    required = [
        "the qa gate document exists",
        "the qa gate states that it does not widen runtime scope",
        "the runtime file exists",
        "the implementation test file exists",
        "the contract file exists",
        "the public function boundary is verified",
        "request and result shapes are verified",
        "result states are verified",
        "import boundaries are verified",
        "blocked operation terms are absent from runtime source",
        "synthetic fixtures prove pass, fail, and blocked behavior",
        "synthetic fixtures prove no private path or filename leakage",
        "synthetic fixtures prove no writes in selected folders",
        "previous implementation and contract tests still pass",
        "repository guards still pass",
    ]
    for item in required:
        assert item in text
