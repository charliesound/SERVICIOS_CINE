import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path("scripts/cid_media_agent_scan.py")
FIXTURES = Path("tests/fixtures/local_media_agent/scanner_cli")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_safe_baseline_v1.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("cid_media_agent_scan", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_scan(input_root: Path, output_root: Path, *extra: str):
    module = _load_module()
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        *extra,
    ])
    return module.scan(args)


def test_safe_baseline_doc_declares_scope_and_no_goals():
    text = DOC.read_text(encoding="utf-8")
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.SAFE.BASELINE.V1" in text
    assert "scripts/cid_media_agent_scan.py" in text
    assert "does not use ffmpeg" in text
    assert "does not use ffprobe" in text
    assert "does not call CID SaaS" in text
    assert "does not write database rows" in text
    assert "does not touch Docker" in text
    assert "does not touch frontend" in text


def test_script_exists_and_has_no_forbidden_runtime_imports():
    assert SCRIPT_PATH.exists()
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "shutil.which(\"ffprobe\")" in text

    for forbidden in [
        "subprocess",
        "requests",
        "httpx",
        "sqlalchemy",
        "alembic",
        "stripe",
        "ffmpeg",
    ]:
        assert forbidden not in text.lower()


def test_simple_camera_fixture_creates_scanner_safe_outputs(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    exit_code, summary = _run_scan(input_root, output_root)
    assert exit_code == 0
    assert summary["candidate_media_count"] == 1
    assert summary["created_outputs"]
    assert (output_root / "00_project/project_manifest.json").exists()
    assert (output_root / "01_media_catalog/media_catalog.json").exists()
    assert (output_root / "99_logs/processing_log.md").exists()
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    assert catalog["assets"][0]["source_kind"] == "camera_original"
    assert catalog["assets"][0]["privacy"]["original_media_left_client_system"] is False


def test_mixed_fixture_classifies_camera_sound_and_proxy(tmp_path):
    input_root = FIXTURES / "mixed_camera_sound_proxy/input"
    output_root = tmp_path / "out"
    exit_code, summary = _run_scan(input_root, output_root)
    assert exit_code == 0
    assert summary["candidate_media_count"] == 3
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    kinds = {asset["source_kind"] for asset in catalog["assets"]}
    assert kinds == {"camera_original", "production_sound", "proxy"}


def test_ambiguous_fixture_requires_human_review(tmp_path):
    input_root = FIXTURES / "ambiguous_unknown_files/input"
    output_root = tmp_path / "out"
    exit_code, summary = _run_scan(input_root, output_root)
    assert exit_code == 1
    assert summary["human_review_required_count"] == 1
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    assert catalog["assets"][0]["source_kind"] == "unknown"
    assert catalog["assets"][0]["human_review_required"] is True


def test_dry_run_writes_no_output_package(tmp_path):
    input_root = FIXTURES / "mixed_camera_sound_proxy/input"
    output_root = tmp_path / "out"
    exit_code, summary = _run_scan(input_root, output_root, "--dry-run")
    assert exit_code == 0
    assert summary["created_outputs"] == []
    assert summary["planned_outputs"]
    assert not output_root.exists()


def test_refuses_input_output_overlap(tmp_path):
    input_root = tmp_path / "same"
    input_root.mkdir()
    exit_code, summary = _run_scan(input_root, input_root)
    assert exit_code == 2
    assert summary["status"] == "preflight_error"
    assert "input root equals output root" in summary["errors"]


def test_refuses_output_inside_input(tmp_path):
    input_root = tmp_path / "input"
    output_root = input_root / "out"
    input_root.mkdir()
    exit_code, summary = _run_scan(input_root, output_root)
    assert exit_code == 2
    assert "output root is inside input root" in summary["errors"]


def test_default_path_policy_avoids_full_local_paths(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    exit_code, _summary = _run_scan(input_root, output_root)
    assert exit_code == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path.startswith("INPUT_ROOT/")
    assert str(input_root.resolve()) not in stored_path


def test_only_scanner_safe_output_folders_are_created(tmp_path):
    input_root = FIXTURES / "mixed_camera_sound_proxy/input"
    output_root = tmp_path / "out"
    exit_code, _summary = _run_scan(input_root, output_root)
    assert exit_code == 0
    existing = {path.name for path in output_root.iterdir() if path.is_dir()}
    assert existing == {"00_project", "01_media_catalog", "99_logs"}


def test_json_cli_output_is_machine_readable(tmp_path, capsys):
    module = _load_module()
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    exit_code = module.main([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    ])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["privacy_mode"] == "local_only"
    assert payload["candidate_media_count"] == 1
    assert payload["exit_code"] == 0
