from pathlib import Path
import json


ROOT = Path("tests/fixtures/local_media_agent/scanner_cli")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_test_fixtures_baseline_v1.md"
)


REQUIRED_FAMILIES = {
    "empty_input_root",
    "simple_camera_only",
    "simple_sound_only",
    "mixed_camera_sound_proxy",
    "sidecar_metadata_only",
    "nested_project_tree",
    "ambiguous_unknown_files",
    "unsafe_input_output_overlap",
    "excluded_dirs",
    "path_policy_examples",
    "dry_run_expected_outputs",
    "json_summary_expected_outputs",
}


FORBIDDEN_TEXT = [
    "Juan Carlos",
    "Cid Torrejón",
    "cid.jcc@gmail.com",
    "C:\\",
    "/mnt/c/",
    "/home/harliesound/",
    "/opt/SERVICIOS_CINE",
    "real client",
    "real actor",
    "real transcript",
    "real subtitle",
]


MEDIA_LIKE_SUFFIXES = {
    ".mov",
    ".mp4",
    ".mxf",
    ".wav",
    ".bwf",
    ".aif",
    ".aiff",
    ".flac",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_baseline_doc_declares_scope_and_no_goals():
    text = _read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.TEST.FIXTURES.BASELINE.V1" in text
    assert "does not implement the scanner" in text
    assert "does not call ffmpeg" in text
    assert "does not call ffprobe" in text
    assert "does not call CID SaaS" in text
    assert "does not touch database models" in text
    assert "does not touch Docker" in text
    assert "does not touch frontend" in text


def test_fixture_root_and_manifest_exist():
    assert ROOT.exists()
    manifest_path = ROOT / "fixtures_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(_read(manifest_path))
    assert manifest["phase"] == "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.TEST.FIXTURES.BASELINE.V1"
    assert manifest["synthetic_only"] is True
    assert set(manifest["families"]) == REQUIRED_FAMILIES


def test_required_fixture_families_exist():
    for family in REQUIRED_FAMILIES:
        family_root = ROOT / family
        assert family_root.exists(), family
        assert (family_root / "README.md").exists(), family


def test_media_like_placeholders_are_tiny_and_not_playable_headers():
    files = [
        path for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in MEDIA_LIKE_SUFFIXES
    ]
    assert files, "Expected media-like placeholder files"
    forbidden_headers = [b"ftyp", b"RIFF", b"\x06\x0e\x2b\x34"]
    for path in files:
        data = path.read_bytes()
        assert len(data) < 1024, path
        assert b"SYNTHETIC_PLACEHOLDER_NOT_MEDIA" in data, path
        for header in forbidden_headers:
            assert header not in data[:32], path


def test_no_forbidden_real_content_or_absolute_user_paths():
    for path in ROOT.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_TEXT:
                assert forbidden not in text, f"{forbidden} found in {path}"


def test_expected_outputs_are_synthetic_json():
    expected_jsons = list(ROOT.rglob("expected/*.json"))
    assert expected_jsons, "Expected synthetic expected-output JSON files"
    for path in expected_jsons:
        payload = json.loads(_read(path))
        assert payload.get("synthetic") is True, path


def test_no_later_phase_output_folders_are_created():
    forbidden_dirs = {
        "02_sync",
        "03_transcripts_original",
        "04_subtitles_spanish",
        "05_editorial_summary",
        "06_davinci",
        "90_temp",
    }
    existing_names = {path.name for path in ROOT.rglob("*") if path.is_dir()}
    assert forbidden_dirs.isdisjoint(existing_names)


def test_dry_run_and_json_expected_outputs_exist():
    assert (ROOT / "dry_run_expected_outputs/expected/planned_actions.json").exists()
    assert (ROOT / "json_summary_expected_outputs/expected/scan_summary.json").exists()
    summary = json.loads(_read(ROOT / "json_summary_expected_outputs/expected/scan_summary.json"))
    assert summary["privacy_mode"] == "local_only"
    assert summary["exit_code"] == 1
    assert summary["human_review_required_count"] == 1


def test_path_policy_examples_avoid_real_absolute_paths():
    payload = json.loads(_read(ROOT / "path_policy_examples/expected/path_policy_examples.json"))
    examples = payload["examples"]
    assert examples["local_relative_path"].startswith("input/")
    assert "PROJECT_ROOT" in examples["sanitized_path"]
    assert examples["hashed_path"].startswith("hash_placeholder_")
    assert "[REDACTED_LOCAL_PATH]" in examples["redacted_path"]


def test_unsafe_overlap_fixture_is_refusal_scenario():
    payload = json.loads(_read(ROOT / "unsafe_input_output_overlap/scenario.json"))
    assert payload["synthetic"] is True
    assert payload["input_root"] == payload["output_root"]
    assert payload["expected_exit_code"] == 2
    assert "input root equals output root" in payload["expected_refusal"]


def test_baseline_does_not_create_real_scanner_code():
    forbidden_code_paths = [
        Path("src/local_media_agent"),
        Path("src/services/local_media_agent"),
        Path("src/routes/local_media_agent_routes.py"),
        Path("scripts/local_media_agent"),
    ]
    for path in forbidden_code_paths:
        assert not path.exists(), f"Unexpected scanner implementation path exists: {path}"
