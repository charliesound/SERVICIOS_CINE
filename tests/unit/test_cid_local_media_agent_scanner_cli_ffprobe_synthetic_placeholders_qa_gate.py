from pathlib import Path
import json


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.QA.GATE.V1"

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_qa_gate_v1.md")
FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
MANIFEST = FIXTURE_ROOT / "fixture_manifest.json"
CREATE_TEST = Path("tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_create.py")
SCANNER = Path("scripts/cid_media_agent_scan.py")

EXPECTED_PLACEHOLDERS = {
    "synthetic_invalid_media_placeholder.bin",
    "synthetic_permission_denied_placeholder.dat",
    "synthetic_unsupported_media_placeholder.txt",
}

FORBIDDEN_MEDIA_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mxf",
    ".wav",
    ".aif",
    ".aiff",
    ".mp3",
}


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _placeholder_files():
    return sorted(
        path for path in FIXTURE_ROOT.iterdir()
        if path.is_file() and path.name != "fixture_manifest.json"
    )


def _private_tokens():
    return [
        "/" + "home" + "/",
        "/" + "mnt" + "/",
        "c:" + "\\",
        "\\\\wsl",
        "." + "env",
        "." + "sq" + "lite",
        "." + "db",
    ]


def test_qa_gate_document_exists_and_declares_scope():
    text = _doc_text()

    assert "Synthetic Placeholders QA Gate v1" in text
    assert PHASE in text
    assert "This phase is QA/test-only." in text
    assert "It does not authorize actual ffprobe execution yet." in text


def test_qa_gate_document_keeps_runtime_and_media_out_of_scope():
    text = _doc_text()

    required = [
        "This QA gate does not execute ffprobe.",
        "This QA gate does not execute ffmpeg.",
        "This QA gate does not add subprocess runtime.",
        "This QA gate does not inspect real media.",
        "This QA gate does not modify scanner runtime.",
        "This QA gate does not modify CID SaaS runtime.",
    ]

    for phrase in required:
        assert phrase in text


def test_manifest_is_valid_and_tracks_three_placeholders():
    manifest = _manifest()

    assert manifest["synthetic_placeholders_phase"] == (
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.CREATE.V1"
    )

    entries = manifest["synthetic_placeholders"]
    assert len(entries) == 3

    paths = {entry["relative_path"] for entry in entries}
    assert paths == EXPECTED_PLACEHOLDERS


def test_manifest_placeholder_policy_is_conservative():
    policy = _manifest()["synthetic_placeholders_policy"]

    assert policy["contains_real_media"] is False
    assert policy["contains_video"] is False
    assert policy["contains_audio"] is False
    assert policy["executes_ffprobe"] is False
    assert policy["executes_ffmpeg"] is False
    assert policy["adds_subprocess_runtime"] is False
    assert set(policy["allowed_extensions"]) == {".txt", ".bin", ".dat"}
    assert set(policy["forbidden_extensions"]) == FORBIDDEN_MEDIA_EXTENSIONS


def test_placeholder_entries_are_not_media_and_do_not_authorize_execution():
    for entry in _manifest()["synthetic_placeholders"]:
        assert entry["media_kind"] == "not_media"
        assert entry["must_not_be_valid_media"] is True
        assert entry["must_not_execute_ffprobe"] is True
        assert entry["must_not_execute_ffmpeg"] is True

        rel = entry["relative_path"].lower()
        assert not any(ext in rel for ext in FORBIDDEN_MEDIA_EXTENSIONS)


def test_fixture_root_contains_only_manifest_and_expected_placeholders():
    files = sorted(path.name for path in FIXTURE_ROOT.iterdir() if path.is_file())

    assert files == sorted({"fixture_manifest.json", *EXPECTED_PLACEHOLDERS})


def test_placeholder_files_are_tiny_synthetic_non_media_payloads():
    files = _placeholder_files()
    assert {path.name for path in files} == EXPECTED_PLACEHOLDERS

    for path in files:
        data = path.read_bytes()

        assert 0 < path.stat().st_size < 1024
        assert b"CID_SYNTHETIC" in data
        assert b"NOT_MEDIA" in data
        assert b"ftyp" not in data
        assert b"WAVE" not in data
        assert b"RIFF" not in data


def test_no_forbidden_media_extensions_in_real_paths():
    for path in FIXTURE_ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(FIXTURE_ROOT).as_posix().lower()
        assert not any(rel.endswith(ext) for ext in FORBIDDEN_MEDIA_EXTENSIONS)


def test_no_private_or_sensitive_tokens_in_placeholder_package():
    combined = MANIFEST.read_text(encoding="utf-8").lower()

    for path in _placeholder_files():
        combined += "\n" + path.read_text(encoding="utf-8", errors="ignore").lower()

    for token in _private_tokens():
        assert token not in combined


def test_create_test_exists_and_does_not_contain_database_literal():
    assert CREATE_TEST.exists()

    text = CREATE_TEST.read_text(encoding="utf-8").lower()

    assert "test_placeholder_phase_creates_only_expected_minimal_files" in text
    assert "sq" + "lite" not in text


def test_scanner_runtime_still_has_no_media_execution_subprocess():
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "ffmpeg" not in scanner_text


def test_qa_gate_does_not_modify_runtime_files():
    assert SCANNER.exists()
    assert DOC.exists()
    assert MANIFEST.exists()
