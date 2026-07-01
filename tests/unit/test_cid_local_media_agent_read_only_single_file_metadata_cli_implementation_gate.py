from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_implementation_gate_v1.md"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
SUCCESS_STATUS = "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
RESULT_TOKEN = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_GATE_V1_CLOSED"


def _load_cli_module():
    spec = importlib.util.spec_from_file_location("cid_lma_read_only_single_file_metadata_cli", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_implementation_gate_files_exist():
    assert CLI_PATH.is_file()
    assert IMPLEMENTATION_PATH.is_file()
    assert DOC_PATH.is_file()
    assert FIXTURE.is_file()


def test_cli_wrapper_exposes_main_and_private_loader_only():
    module = _load_cli_module()
    assert callable(module.main)
    assert callable(module._load_implementation)
    assert module._implementation_path().name == "read_only_single_file_metadata.py"


def test_cli_wrapper_uses_python_standard_library_only_and_no_media_tool_calls():
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "importlib.util" in source
    assert "pathlib" in source or "from pathlib import Path" in source
    forbidden_tokens = ["subprocess", "os.system", "Popen", "requests", "httpx"]
    for token in forbidden_tokens:
        assert token not in source


def test_cli_wrapper_does_not_register_project_wide_entrypoint():
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "pyproject" not in source.lower()
    assert "console_scripts" not in source
    assert "entry_points" not in source


def test_cli_json_success_delegates_to_existing_implementation(capsys):
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(FIXTURE), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", EXPECTED_SHA256, "--expected-bytes", str(EXPECTED_BYTES), "--result-json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["status"] == SUCCESS_STATUS


def test_cli_json_success_preserves_redacted_path_contract(capsys):
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(FIXTURE), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", EXPECTED_SHA256, "--expected-bytes", str(EXPECTED_BYTES), "--result-json"])
    payload = json.loads(capsys.readouterr().out)
    rendered = json.dumps(payload, sort_keys=True)
    assert exit_code == 0
    assert str(REPO_ROOT) not in rendered
    assert payload["target"]["redacted_path"] == "<CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt"
    assert EXPECTED_SHA256 in rendered


def test_cli_plain_success_delegates_to_existing_implementation(capsys):
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(FIXTURE), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", EXPECTED_SHA256, "--expected-bytes", str(EXPECTED_BYTES)])
    assert exit_code == 0
    assert capsys.readouterr().out.strip() == SUCCESS_STATUS


def test_cli_outside_root_rejection_remains_deterministic(capsys, tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(outside), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", EXPECTED_SHA256, "--expected-bytes", str(EXPECTED_BYTES), "--result-json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["ok"] is False
    assert payload["reason"] == "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT"


def test_cli_missing_file_rejection_remains_deterministic(capsys):
    missing = FIXTURE_ROOT / "media/missing.txt"
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(missing), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", EXPECTED_SHA256, "--expected-bytes", str(EXPECTED_BYTES), "--result-json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["ok"] is False
    assert payload["reason"] in {"TARGET_RELATIVE_PATH_NOT_ALLOWED", "TARGET_FILE_NOT_FOUND"}


def test_cli_sha_mismatch_rejection_remains_deterministic(capsys):
    module = _load_cli_module()
    exit_code = module.main(["--target-path", str(FIXTURE), "--fixture-root", str(FIXTURE_ROOT), "--expected-sha256", "0" * 64, "--expected-bytes", str(EXPECTED_BYTES), "--result-json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["ok"] is False
    assert payload["reason"] == "TARGET_SHA256_MISMATCH"
    assert payload["target"]["actual_sha256"] == EXPECTED_SHA256


def test_cli_wrapper_has_no_batch_or_recursion_arguments():
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "--batch" not in source
    assert "--recursive" not in source
    assert "rglob" not in source
    assert "os.walk" not in source


def test_cli_implementation_gate_document_records_boundaries_and_result():
    text = DOC_PATH.read_text(encoding="utf-8")
    assert RESULT_TOKEN in text
    assert "read_only_single_file_metadata_cli.py" in text
    assert "No project-wide CLI registration" in text
    assert "No batch mode" in text
    assert "No recursive traversal" in text
