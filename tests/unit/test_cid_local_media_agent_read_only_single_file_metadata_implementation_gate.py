from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_GATE_V1_CLOSED"
DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_implementation_gate_v1.md"
IMPL = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
MANIFEST = FIXTURE_ROOT / "manifest.controlled.json"
ALLOWED_RELATIVE = "media/controlled_plain_text_marker.txt"


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


def _manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def _fixture_sha_and_size() -> tuple[str, int]:
    return _sha256(FIXTURE), FIXTURE.stat().st_size


def test_phase_document_exists_and_declares_closure_contract():
    text = DOC.read_text(encoding="utf-8")
    assert PHASE in text
    assert RESULT in text
    assert "python_standard_library_only" in text
    assert "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK" in text
    assert "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_REJECTED" in text


def test_implementation_file_exists_and_exposes_expected_api():
    module = _load_module()
    assert IMPL.exists()
    assert hasattr(module, "collect_read_only_single_file_metadata")
    assert hasattr(module, "run_cli")
    assert module.SCHEMA_VERSION == "cid.local_media_agent.read_only_single_file_metadata.v1"
    assert module.DEFAULT_ALLOWED_RELATIVE_PATH == ALLOWED_RELATIVE


def test_implementation_uses_only_python_standard_library_imports():
    tree = ast.parse(IMPL.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"__future__", "argparse", "hashlib", "json", "pathlib", "typing"}


def test_implementation_source_has_no_external_execution_or_scanner_patterns():
    source = IMPL.read_text(encoding="utf-8").lower()
    forbidden = [
        "ffprobe",
        "ffmpeg",
        "popen",
        "os.system",
        "shell=true",
        "glob(",
        "rglob(",
        "walk(",
    ]
    assert not [token for token in forbidden if token in source]


def test_controlled_fixture_pack_exists_and_manifest_matches_fixture_identity():
    assert FIXTURE_ROOT.is_dir()
    assert FIXTURE.is_file()
    assert MANIFEST.is_file()
    sha, size = _fixture_sha_and_size()
    manifest_text = _manifest_text()
    assert ALLOWED_RELATIVE in manifest_text
    assert "controlled_plain_text_marker_v1" in manifest_text
    assert str(size) in manifest_text
    assert sha in manifest_text


def test_collect_metadata_returns_successful_deterministic_result():
    module = _load_module()
    sha, size = _fixture_sha_and_size()
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=sha,
        expected_bytes=size,
    )
    assert result["ok"] is True
    assert result["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
    assert result["mode"] == "read_only_single_file"
    assert result["tool_policy"] == "python_standard_library_only"
    assert result["metadata"] == {"bytes": size, "sha256": sha, "is_file": True}


def test_collect_metadata_redacts_absolute_paths_and_reports_controlled_relative_path():
    module = _load_module()
    sha, size = _fixture_sha_and_size()
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=sha,
        expected_bytes=size,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert str(REPO_ROOT) not in rendered
    assert result["target"]["relative_path"] == ALLOWED_RELATIVE
    assert result["target"]["redacted_path"] == f"<CONTROLLED_FIXTURE_ROOT>/{ALLOWED_RELATIVE}"
    assert result["target"]["file_name"] == "controlled_plain_text_marker.txt"
    assert result["target"]["extension"] == ".txt"


def test_collect_metadata_rejects_target_outside_controlled_fixture_root(tmp_path):
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
    assert result["reason"] == "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT"
    assert str(outside) not in rendered


def test_collect_metadata_rejects_wrong_relative_path_inside_fixture_root(tmp_path):
    module = _load_module()
    wrong_dir = FIXTURE_ROOT / "media"
    wrong = wrong_dir / "not_allowed_metadata_target.txt"
    try:
        wrong.write_text("wrong", encoding="utf-8")
        result = module.collect_read_only_single_file_metadata(
            target_path=wrong,
            fixture_root=FIXTURE_ROOT,
            expected_sha256=_sha256(wrong),
            expected_bytes=wrong.stat().st_size,
        )
        assert result["ok"] is False
        assert result["reason"] == "TARGET_RELATIVE_PATH_NOT_ALLOWED"
    finally:
        wrong.unlink(missing_ok=True)


def test_collect_metadata_rejects_bytes_mismatch_without_private_path_leak():
    module = _load_module()
    sha, size = _fixture_sha_and_size()
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256=sha,
        expected_bytes=size + 1,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["reason"] == "TARGET_BYTES_MISMATCH"
    assert result["target"]["actual_bytes"] == size
    assert str(REPO_ROOT) not in rendered


def test_collect_metadata_rejects_sha256_mismatch_without_private_path_leak():
    module = _load_module()
    _sha, size = _fixture_sha_and_size()
    result = module.collect_read_only_single_file_metadata(
        target_path=FIXTURE,
        fixture_root=FIXTURE_ROOT,
        expected_sha256="0" * 64,
        expected_bytes=size,
    )
    rendered = json.dumps(result, sort_keys=True)
    assert result["ok"] is False
    assert result["reason"] == "TARGET_SHA256_MISMATCH"
    assert result["target"]["actual_sha256"] != "0" * 64
    assert str(REPO_ROOT) not in rendered


def test_cli_result_json_success_and_rejected_exit_code(capsys, tmp_path):
    module = _load_module()
    sha, size = _fixture_sha_and_size()
    ok_code = module.run_cli([
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        sha,
        "--expected-bytes",
        str(size),
        "--result-json",
    ])
    ok_payload = json.loads(capsys.readouterr().out)
    assert ok_code == 0
    assert ok_payload["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"

    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    rejected_code = module.run_cli([
        "--target-path",
        str(outside),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        _sha256(outside),
        "--expected-bytes",
        str(outside.stat().st_size),
        "--result-json",
    ])
    rejected_payload = json.loads(capsys.readouterr().out)
    assert rejected_code == 2
    assert rejected_payload["reason"] == "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT"
