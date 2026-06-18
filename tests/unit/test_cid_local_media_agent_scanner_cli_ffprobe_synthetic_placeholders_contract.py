from pathlib import Path

def _allowed_fixture_files_after_later_placeholder_create_phase():
    return {
        "fixture_manifest.json",
        "synthetic_invalid_media_placeholder.bin",
        "synthetic_permission_denied_placeholder.dat",
        "synthetic_unsupported_media_placeholder.txt",
    }


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_contract_v1.md"
)
FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
SCANNER = Path("scripts/cid_media_agent_scan.py")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_placeholders_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PLACEHOLDERS.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Synthetic Placeholders Contract v1" in text
    assert "documentation-only and test-only" in text


def test_placeholders_contract_does_not_create_files_or_runtime():
    text = _doc_text()
    required = [
        "It does not create placeholder files.",
        "It does not create video files.",
        "It does not create audio files.",
        "It does not create binary fixtures.",
        "It does not execute ffprobe.",
        "It does not execute ffmpeg.",
        "It does not add subprocess runtime.",
        "It does not modify scanner runtime.",
        "It does not inspect real media.",
    ]
    for phrase in required:
        assert phrase in text


def test_only_manifest_exists_in_fixture_folder_during_contract_phase():
    assert FIXTURE_ROOT.exists(), "manifest phase should have created the fixture folder"
    files = sorted(path.relative_to(FIXTURE_ROOT).as_posix() for path in FIXTURE_ROOT.rglob("*") if path.is_file())
    assert set(files) == _allowed_fixture_files_after_later_placeholder_create_phase()


def test_allowed_future_placeholder_files_are_documented():
    text = _doc_text()
    required = [
        "synthetic_unsupported_media_placeholder.txt",
        "synthetic_invalid_media_placeholder.bin",
        "synthetic_permission_denied_placeholder.dat",
        "No other placeholder filename is allowed",
    ]
    for phrase in required:
        assert phrase in text


def test_placeholder_purposes_are_failure_paths_only():
    text = _doc_text()
    required = [
        "unsupported media status",
        "invalid or corrupt media status",
        "permission denied status",
        "must not be used to claim real technical probing",
        "editorial intelligence",
        "media sync",
        "conform",
        "delivery readiness",
        "DaVinci/Avid/Premiere integration",
    ]
    for phrase in required:
        assert phrase in text


def test_placeholder_size_policy_is_tiny():
    text = _doc_text()
    required = [
        "maximum text placeholder size: 4 KiB",
        "maximum invalid binary placeholder size: 4 KiB",
        "maximum permission placeholder size: 4 KiB",
        "maximum total placeholder size: 16 KiB",
    ]
    for phrase in required:
        assert phrase in text


def test_placeholder_content_policy_blocks_real_material():
    text = _doc_text()
    required = [
        "real video",
        "real audio",
        "real image",
        "real subtitle",
        "real transcript",
        "real camera original",
        "real sound roll",
        "real editorial export",
        "client material",
        "private pilot material",
        "downloaded stock media",
        "copyrighted media samples",
        "mobile phone clips",
        "drone clips",
        "screen recordings from real projects",
    ]
    for phrase in required:
        assert phrase in text


def test_placeholder_privacy_restrictions_are_documented():
    text = _doc_text()
    required = [
        "client names",
        "project names",
        "personal names",
        "production company names",
        "real location names",
        "real shoot dates",
        "GPS coordinates",
        "camera serial numbers",
        "lens serial numbers",
        "device serial numbers",
        "local user names",
        "home directory paths",
        "drive labels",
        "network paths",
        "cloud paths",
        "raw ffprobe output",
        "raw stdout",
        "raw stderr",
        "shell commands",
        "full argv",
    ]
    for phrase in required:
        assert phrase in text


def test_manifest_relationship_is_documented():
    text = _doc_text()
    required = [
        "synthetic_unsupported_media_placeholder.txt -> synthetic_unsupported_media_placeholder",
        "synthetic_invalid_media_placeholder.bin -> synthetic_invalid_media_placeholder",
        "synthetic_permission_denied_placeholder.dat -> synthetic_permission_denied_placeholder",
        "relative-path only",
        "must not contain absolute paths",
        "must not authorize real media",
    ]
    for phrase in required:
        assert phrase in text


def test_future_test_policy_and_human_review_are_documented():
    text = _doc_text()
    required = [
        "placeholder file existence",
        "exact allowed filenames only",
        "size limits",
        "no real media extensions",
        "no absolute path leaks",
        "no private metadata terms",
        "manifest alignment",
        "Human review is required",
        "placeholders are safe to commit",
    ]
    for phrase in required:
        assert phrase in text


def test_runtime_and_saas_non_goals_are_documented():
    text = _doc_text()
    required = [
        "This phase does not implement placeholder creation.",
        "This phase does not create .txt, .bin or .dat placeholder files.",
        "This phase does not execute ffprobe.",
        "This phase does not execute ffmpeg.",
        "This phase does not add subprocess runtime.",
        "This phase does not modify scripts/cid_media_agent_scan.py.",
        "This phase does not touch SaaS runtime.",
        "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger",
    ]
    for phrase in required:
        assert phrase in text


def test_scanner_runtime_is_not_modified_for_placeholders():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()
    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "synthetic_unsupported_media_placeholder" not in scanner_text
    assert "synthetic_invalid_media_placeholder" not in scanner_text
    assert "synthetic_permission_denied_placeholder" not in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "shell=true" not in scanner_text
