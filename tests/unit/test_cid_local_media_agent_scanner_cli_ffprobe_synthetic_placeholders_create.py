from pathlib import Path
import json


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.CREATE.V1"

FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
MANIFEST = FIXTURE_ROOT / "fixture_manifest.json"

EXPECTED_PLACEHOLDERS = {
    "synthetic_invalid_media_placeholder.bin": "synthetic_invalid_media_placeholder",
    "synthetic_permission_denied_placeholder.dat": "synthetic_permission_denied_placeholder",
    "synthetic_unsupported_media_placeholder.txt": "synthetic_unsupported_media_placeholder",
}

FORBIDDEN_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mxf",
    ".wav",
    ".aif",
    ".aiff",
    ".mp3",
}


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _placeholder_files():
    return sorted(
        path for path in FIXTURE_ROOT.iterdir()
        if path.is_file() and path.name != "fixture_manifest.json"
    )


def test_placeholder_phase_creates_only_expected_minimal_files():
    files = _placeholder_files()
    assert {path.name for path in files} == set(EXPECTED_PLACEHOLDERS)

    for path in files:
        assert path.suffix not in FORBIDDEN_EXTENSIONS
        assert path.stat().st_size > 0
        assert path.stat().st_size < 1024


def test_placeholders_are_explicitly_not_media_files():
    for path in _placeholder_files():
        data = path.read_bytes()
        assert b"CID_SYNTHETIC" in data
        assert b"NOT_MEDIA" in data
        assert b"ftyp" not in data
        assert b"WAVE" not in data
        assert b"RIFF" not in data


def test_manifest_existing_fixture_entries_align_with_created_placeholders():
    manifest = _manifest()
    entries = {entry["fixture_id"]: entry for entry in manifest["fixtures"]}

    for filename, fixture_id in EXPECTED_PLACEHOLDERS.items():
        assert fixture_id in entries
        entry = entries[fixture_id]
        assert entry["relative_path"] == filename
        assert entry["expected_privacy_safe"] is True
        assert entry["commit_allowed"] is False
        assert entry["human_reviewed"] is False


def test_created_placeholders_do_not_turn_manifest_into_runtime_authorization():
    manifest = _manifest()

    assert manifest["manifest_mode"] == "declarative_manifest_only_no_binary_fixtures"
    assert manifest["binary_fixtures_created"] is False
    assert manifest["ffprobe_execution_allowed"] is False
    assert manifest["ffmpeg_execution_allowed"] is False
    assert manifest["subprocess_execution_allowed"] is False
    assert manifest["real_media_allowed"] is False


def test_no_private_paths_or_sensitive_files_in_manifest_or_placeholders():
    combined = MANIFEST.read_text(encoding="utf-8").lower()
    for path in _placeholder_files():
        combined += "\n" + path.read_text(encoding="utf-8", errors="ignore").lower()

    forbidden = [
        "/home/",
        "/mnt/",
        "c:\\",
        "\\wsl",
        ".env",
        "." + "sq" + "lite",
        ".db",
    ]

    for item in forbidden:
        assert item not in combined


def test_phase_does_not_add_runtime_execution_to_scanner():
    scanner = Path("scripts/cid_media_agent_scan.py")
    assert scanner.exists()

    scanner_text = scanner.read_text(encoding="utf-8").lower()
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "ffmpeg" not in scanner_text
    assert "synthetic_invalid_media_placeholder" not in scanner_text
    assert "synthetic_permission_denied_placeholder" not in scanner_text
    assert "synthetic_unsupported_media_placeholder" not in scanner_text
