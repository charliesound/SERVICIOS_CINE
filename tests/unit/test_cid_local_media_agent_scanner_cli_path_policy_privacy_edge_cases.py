import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path("scripts/cid_media_agent_scan.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_path_policy_privacy_edge_cases_v1.md"
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def _write_placeholder(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "CID_LOCAL_MEDIA_AGENT_SYNTHETIC_PLACEHOLDER_NOT_MEDIA\n",
        encoding="utf-8",
    )


def _make_edge_input(tmp_path: Path) -> tuple[Path, Path]:
    input_root = tmp_path / "Proyecto Sintetico con Espacios" / "input raíz"
    media_file = input_root / "DIA 01" / "CAM A" / "SC 001_TK 001_CÁMARA_PLACEHOLDER.mov"
    _write_placeholder(media_file)
    return input_root, media_file


def _read_output_files(output_root: Path) -> dict[str, str]:
    files = {}
    for path in output_root.rglob("*"):
        if path.is_file():
            files[path.relative_to(output_root).as_posix()] = path.read_text(encoding="utf-8")
    return files


def test_path_policy_edge_doc_declares_scope_and_no_goals():
    text = DOC.read_text(encoding="utf-8")
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.PATH_POLICY.PRIVACY.EDGE_CASES.V1" in text
    assert "JSON stdout" in text
    assert "media_catalog.json" in text
    assert "paths with spaces" in text
    assert "paths with non-ASCII characters" in text
    assert "does not implement ffprobe" in text
    assert "does not implement ffmpeg" in text
    assert "does not call CID SaaS" in text
    assert "does not write database rows" in text
    assert "does not touch Docker" in text
    assert "does not touch frontend" in text


def test_default_json_stdout_does_not_leak_absolute_input_or_output_paths(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "output with spaces"

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
    assert payload["candidate_media_count"] == 1
    assert str(input_root.resolve()) not in result.stdout
    assert str(output_root.resolve()) not in result.stdout
    assert "Proyecto Sintetico con Espacios" not in result.stdout


def test_default_generated_outputs_do_not_leak_absolute_paths(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )

    assert result.returncode == 0
    output_text = "\n".join(_read_output_files(output_root).values())
    assert str(input_root.resolve()) not in output_text
    assert str(output_root.resolve()) not in output_text
    assert "Proyecto Sintetico con Espacios" not in output_text
    assert "INPUT_ROOT/" in output_text


def test_default_catalog_uses_sanitized_path_policy(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )

    assert result.returncode == 0
    manifest = json.loads((output_root / "00_project/project_manifest.json").read_text())
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())

    assert manifest["path_policy"] == "sanitized_path"
    stored_path = catalog["assets"][0]["path"]
    assert stored_path.startswith("INPUT_ROOT/")
    assert "DIA 01/CAM A/" in stored_path
    assert str(input_root.resolve()) not in stored_path


def test_local_relative_path_policy_is_explicit_and_relative(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
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
    assert stored_path.startswith("DIA 01/CAM A/")
    assert "INPUT_ROOT/" not in stored_path
    assert str(input_root.resolve()) not in stored_path


def test_hashed_path_policy_hides_file_and_folder_names(tmp_path):
    input_root, media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--path-policy",
        "hashed_path",
        "--json",
    )

    assert result.returncode == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path.startswith("hash_")
    assert media_file.name not in stored_path
    assert "DIA 01" not in stored_path
    assert str(input_root.resolve()) not in stored_path


def test_redacted_path_policy_keeps_filename_but_hides_parent_dirs(tmp_path):
    input_root, media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--path-policy",
        "redacted_path",
        "--json",
    )

    assert result.returncode == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path == f"[REDACTED_LOCAL_PATH]/{media_file.name}"
    assert "DIA 01" not in stored_path
    assert str(input_root.resolve()) not in stored_path


def test_local_absolute_path_policy_is_explicit_opt_in(tmp_path):
    input_root, media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--path-policy",
        "local_absolute_path",
        "--json",
    )

    assert result.returncode == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    stored_path = catalog["assets"][0]["path"]
    assert stored_path == str(media_file.resolve())
    assert str(input_root.resolve()) in stored_path


def test_preflight_missing_input_does_not_dump_missing_absolute_path(tmp_path):
    input_root = tmp_path / "missing input root with spaces"
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
    assert "--input-root does not exist" in payload["errors"]
    assert str(input_root.resolve()) not in result.stdout
    assert str(output_root.resolve()) not in result.stdout


def test_preflight_invalid_policy_does_not_dump_absolute_paths(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
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
    assert str(input_root.resolve()) not in result.stdout
    assert str(output_root.resolve()) not in result.stdout


def test_no_outputs_are_created_outside_output_root(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"
    sibling = tmp_path / "unexpected_sibling"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--json",
    )

    assert result.returncode == 0
    assert output_root.exists()
    assert not sibling.exists()

    allowed_top_level = {"00_project", "01_media_catalog", "99_logs"}
    existing_top_level = {path.name for path in output_root.iterdir() if path.is_dir()}
    assert existing_top_level == allowed_top_level


def test_non_json_human_output_stays_minimal_and_omits_paths(tmp_path):
    input_root, _media_file = _make_edge_input(tmp_path)
    output_root = tmp_path / "out"

    result = _run_cli(
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
    )

    assert result.returncode == 0
    assert "status=completed" in result.stdout
    assert "candidate_media_count=1" in result.stdout
    assert str(input_root.resolve()) not in result.stdout
    assert str(output_root.resolve()) not in result.stdout
