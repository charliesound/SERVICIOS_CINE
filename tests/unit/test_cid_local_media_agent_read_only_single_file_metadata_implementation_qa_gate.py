from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_QA_GATE_V1_CLOSED"
DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_implementation_qa_gate_v1.md"
IMPL = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
MANIFEST = FIXTURE_ROOT / "manifest.controlled.json"
ALLOWED_RELATIVE = "media/controlled_plain_text_marker.txt"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"


def _load_module():
    spec = importlib.util.spec_from_file_location("cid_lma_read_only_single_file_metadata", IMPL)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _success_result():
    module = _load_module()
    return module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=EXPECTED_SHA256,
        expected_bytes=EXPECTED_BYTES,
    )


def test_qa_gate_document_declares_phase_result_and_acceptance_decision():
    text = DOC.read_text(encoding="utf-8")
    assert PHASE in text
    assert RESULT in text
    assert "IMPLEMENTATION_QA_PASS_FOR_CONTROLLED_SINGLE_FILE_METADATA_ONLY" in text
    assert "python_standard_library_only" in text


def test_controlled_fixture_pack_identity_remains_exact():
    assert FIXTURE_ROOT.is_dir()
    assert FIXTURE.is_file()
    assert MANIFEST.is_file()
    assert FIXTURE.stat().st_size == EXPECTED_BYTES
    assert _sha256(FIXTURE) == EXPECTED_SHA256
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    assert ALLOWED_RELATIVE in manifest_text
    assert EXPECTED_SHA256 in manifest_text


def test_implementation_imports_remain_standard_library_only():
    tree = ast.parse(IMPL.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"__future__", "argparse", "hashlib", "json", "pathlib", "typing"}


def test_implementation_source_has_no_external_tool_or_traversal_patterns():
    source = IMPL.read_text(encoding="utf-8").lower()
    forbidden = [
        "ffprobe",
        "ffmpeg",
        "subprocess",
        "popen",
        "os.system",
        "shell=true",
        "glob(",
        "rglob(",
        "walk(",
        "scandir(",
        "moviepy",
        "cv2",
        "mediainfo",
    ]
    assert not [token for token in forbidden if token in source]


def test_success_result_contains_required_safety_flags_and_metadata():
    result = _success_result()
    assert result["ok"] is True
    assert result["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
    assert result["tool_policy"] == "python_standard_library_only"
    assert result["external_tools_used"] is False
    assert result["scanner_used"] is False
    assert result["recursion_used"] is False
    assert result["batch_used"] is False
    assert result["metadata"] == {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256, "is_file": True}


def test_success_result_redacts_private_paths_and_uses_controlled_relative_path():
    result = _success_result()
    rendered = json.dumps(result, sort_keys=True)
    assert str(REPO_ROOT) not in rendered
    assert str(FIXTURE_ROOT) not in rendered
    assert result["target"]["relative_path"] == ALLOWED_RELATIVE
    assert result["target"]["redacted_path"] == f"<CONTROLLED_FIXTURE_ROOT>/{ALLOWED_RELATIVE}"
    assert result["target"]["file_name"] == "controlled_plain_text_marker.txt"


def test_cli_success_json_is_parseable_and_does_not_leak_absolute_paths(capsys):
    module = _load_module()
    exit_code = module.run_cli([
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--result-json",
    ])
    payload_text = capsys.readouterr().out
    payload = json.loads(payload_text)
    assert exit_code == 0
    assert payload["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
    assert str(REPO_ROOT) not in payload_text


def test_cli_plain_success_outputs_status_only(capsys):
    module = _load_module()
    exit_code = module.run_cli([
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
    ])
    output = capsys.readouterr().out.strip()
    assert exit_code == 0
    assert output == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"


def test_outside_target_rejection_is_deterministic_and_redacted(tmp_path):
    module = _load_module()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    result = module.collect_read_only_single_file_metadata(
        target_path=outside,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=_sha256(outside),
        expected_bytes=outside.stat().st_size,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_REJECTED"
    assert result["reason"] == "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT"
    assert str(outside) not in rendered


def test_missing_target_rejection_is_deterministic_and_has_no_target_payload():
    module = _load_module()
    missing = FIXTURE_ROOT / "media/missing_controlled_marker.txt"
    result = module.collect_read_only_single_file_metadata(
        target_path=missing,
        fixture_root=FIXTURE_ROOT,
        expected_sha256="0" * 64,
        expected_bytes=1,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["reason"] == "TARGET_FILE_NOT_FOUND"
    assert "target" not in result
    assert str(REPO_ROOT) not in rendered


def test_bytes_mismatch_rejection_reports_expected_and_actual_without_private_path():
    module = _load_module()
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=EXPECTED_SHA256,
        expected_bytes=EXPECTED_BYTES + 1,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["reason"] == "TARGET_BYTES_MISMATCH"
    assert result["target"]["expected_bytes"] == EXPECTED_BYTES + 1
    assert result["target"]["actual_bytes"] == EXPECTED_BYTES
    assert result["target"]["redacted_path"] == f"<CONTROLLED_FIXTURE_ROOT>/{ALLOWED_RELATIVE}"
    assert str(REPO_ROOT) not in rendered


def test_sha256_mismatch_rejection_reports_expected_and_actual_without_private_path():
    module = _load_module()
    wrong_sha = "0" * 64
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=wrong_sha,
        expected_bytes=EXPECTED_BYTES,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["reason"] == "TARGET_SHA256_MISMATCH"
    assert result["target"]["expected_sha256"] == wrong_sha
    assert result["target"]["actual_sha256"] == EXPECTED_SHA256
    assert result["target"]["redacted_path"] == f"<CONTROLLED_FIXTURE_ROOT>/{ALLOWED_RELATIVE}"
    assert str(REPO_ROOT) not in rendered
