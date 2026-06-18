import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path("scripts/cid_media_agent_scan.py")
FIXTURES = Path("tests/fixtures/local_media_agent/scanner_cli")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_execution_hardening_v1.md"
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_execution_hardening_doc_declares_scope_and_no_goals():
    text = DOC.read_text(encoding="utf-8")
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.EXECUTION.HARDENING.V1" in text
    assert "subprocess execution" in text
    assert "real process exit codes" in text
    assert "does not implement ffmpeg" in text
    assert "does not implement ffprobe" in text
    assert "does not call CID SaaS" in text
    assert "does not write database rows" in text
    assert "does not touch Docker" in text
    assert "does not touch frontend" in text


def test_script_exists_and_remains_local_only_without_forbidden_imports():
    assert SCRIPT.exists()
    text = SCRIPT.read_text(encoding="utf-8").lower()
    assert "shutil.which(\"ffprobe\")" in text

    for forbidden in [
        "requests",
        "httpx",
        "urllib",
        "socket",
        "sqlalchemy",
        "alembic",
        "stripe",
        "ffmpeg",
        "database",
        "fastapi",
        "docker",
    ]:
        assert forbidden not in text


def test_cli_requires_input_root_and_output_root_arguments():
    result = _run_cli()
    assert result.returncode == 2
    assert "--input-root" in result.stderr
    assert "--output-root" in result.stderr


def test_cli_json_success_is_machine_readable(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["privacy_mode"] == "local_only"
    assert payload["candidate_media_count"] == 1
    assert payload["human_review_required_count"] == 0
    assert payload["exit_code"] == 0
    assert result.stderr == ""


def test_cli_human_review_warning_exits_one_with_json(tmp_path):
    input_root = FIXTURES / "ambiguous_unknown_files/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed_with_warnings"
    assert payload["human_review_required_count"] == 1
    assert payload["warnings_count"] == 1
    assert payload["exit_code"] == 1


def test_cli_preflight_missing_input_root_exits_two_with_json(tmp_path):
    input_root = tmp_path / "missing"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "preflight_error"
    assert payload["exit_code"] == 2
    assert "--input-root does not exist" in payload["errors"]


def test_cli_refuses_input_output_same_path(tmp_path):
    input_root = tmp_path / "same"
    input_root.mkdir()
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(input_root),
        "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "input root equals output root" in payload["errors"]


def test_cli_refuses_output_root_inside_input_root(tmp_path):
    input_root = tmp_path / "input"
    output_root = input_root / "out"
    input_root.mkdir()
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "output root is inside input root" in payload["errors"]


def test_cli_dry_run_does_not_create_output_package(tmp_path):
    input_root = FIXTURES / "mixed_camera_sound_proxy/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--dry-run",
        "--json",
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["created_outputs"] == []
    assert payload["planned_outputs"]
    assert not output_root.exists()


def test_cli_writes_only_scanner_safe_output_directories(tmp_path):
    input_root = FIXTURES / "mixed_camera_sound_proxy/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 0
    created_dirs = {path.name for path in output_root.iterdir() if path.is_dir()}
    assert created_dirs == {"00_project", "01_media_catalog", "99_logs"}
    forbidden_dirs = {
        "02_sync",
        "03_transcripts_original",
        "04_subtitles_spanish",
        "05_editorial_summary",
        "06_davinci",
        "90_temp",
    }
    assert forbidden_dirs.isdisjoint(created_dirs)


def test_cli_default_catalog_paths_do_not_leak_absolute_input_root(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )
    assert result.returncode == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path.startswith("INPUT_ROOT/")
    assert str(input_root.resolve()) not in stored_path


def test_cli_local_relative_path_policy_is_explicit_opt_in(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--path-policy",
        "local_relative_path",
        "--json",
    )
    assert result.returncode == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path == "A001/SC001_TK001_CAM_A_PLACEHOLDER.mov"
    assert str(input_root.resolve()) not in stored_path


def test_cli_hashed_and_redacted_path_policies_do_not_expose_input_root(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"

    hashed_out = tmp_path / "hashed_out"
    hashed = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(hashed_out),
        "--path-policy",
        "hashed_path",
        "--json",
    )
    assert hashed.returncode == 0
    hashed_catalog = json.loads((hashed_out / "01_media_catalog/media_catalog.json").read_text())
    assert hashed_catalog["assets"][0]["path"].startswith("hash_")

    redacted_out = tmp_path / "redacted_out"
    redacted = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(redacted_out),
        "--path-policy",
        "redacted_path",
        "--json",
    )
    assert redacted.returncode == 0
    redacted_catalog = json.loads((redacted_out / "01_media_catalog/media_catalog.json").read_text())
    assert redacted_catalog["assets"][0]["path"].startswith("[REDACTED_LOCAL_PATH]/")

    assert str(input_root.resolve()) not in hashed.stdout
    assert str(input_root.resolve()) not in redacted.stdout


def test_cli_invalid_privacy_mode_is_preflight_error(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--privacy-mode",
        "connected_metadata_allowed_future",
        "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "privacy mode is not local_only" in payload["errors"]


def test_cli_invalid_path_policy_is_preflight_error(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--path-policy",
        "unsafe_full_path_dump",
        "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "path policy is invalid" in payload["errors"]
