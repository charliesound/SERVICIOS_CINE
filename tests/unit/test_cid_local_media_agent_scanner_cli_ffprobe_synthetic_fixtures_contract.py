from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_synthetic_fixtures_contract_v1.md"
)
SCANNER = Path("scripts/cid_media_agent_scan.py")
FUTURE_FIXTURE_DIR = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_synthetic_fixtures_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Synthetic Fixtures Contract v1" in text
    assert "documentation-only and test-only" in text


def test_synthetic_fixtures_contract_does_not_create_fixtures_or_runtime():
    text = _doc_text()
    required = [
        "It does not create media fixtures.",
        "It does not generate video files.",
        "It does not generate audio files.",
        "It does not execute ffprobe.",
        "It does not execute ffmpeg.",
        "It does not modify scanner runtime.",
        "It does not add subprocess execution.",
        "It does not inspect real media.",
    ]
    for phrase in required:
        assert phrase in text


def test_future_fixture_folder_is_documented_but_not_created_in_this_phase():
    text = _doc_text()
    assert "tests/fixtures/local_media_agent/ffprobe_synthetic/" in text
    assert "This contract phase must not create that folder." in text
    assert not FUTURE_FIXTURE_DIR.exists()


def test_allowed_future_fixture_categories_are_explicit():
    text = _doc_text()
    required = [
        "synthetic_video_minimal",
        "synthetic_audio_minimal",
        "synthetic_video_with_audio_minimal",
        "synthetic_unsupported_media_placeholder",
        "synthetic_corrupt_or_invalid_media_placeholder",
        "synthetic_permission_denied_placeholder",
    ]
    for phrase in required:
        assert phrase in text


def test_recommended_future_filenames_are_safe_and_synthetic():
    text = _doc_text()
    required = [
        "synthetic_video_minimal.mp4",
        "synthetic_audio_minimal.wav",
        "synthetic_video_with_audio_minimal.mp4",
        "synthetic_unsupported_media_placeholder.txt",
        "synthetic_invalid_media_placeholder.bin",
        "synthetic_permission_denied_placeholder.dat",
        "must not include client names",
        "project names",
        "people names",
        "location names",
        "camera roll names",
        "sound roll names",
    ]
    for phrase in required:
        assert phrase in text


def test_future_fixture_size_and_duration_limits_are_documented():
    text = _doc_text()
    required = [
        "maximum duration: 2 seconds",
        "maximum individual file size: 512 KiB",
        "maximum total fixture folder size: 2 MiB",
        "minimum resolution sufficient for ffprobe recognition only",
        "minimum audio duration sufficient for ffprobe recognition only",
    ]
    for phrase in required:
        assert phrase in text


def test_future_generation_policy_blocks_real_sources_and_internet():
    text = _doc_text()
    required = [
        "the generation command must be documented",
        "the command must not use real source media",
        "the command must not embed personal metadata",
        "the command must not embed project metadata",
        "the command must not depend on external internet access",
        "the command must be reproducible locally",
    ]
    for phrase in required:
        assert phrase in text


def test_forbidden_fixture_sources_are_exhaustive_for_real_material():
    text = _doc_text()
    required = [
        "real camera originals",
        "real sound rolls",
        "real production proxies",
        "real editorial exports",
        "real dailies",
        "real rushes",
        "real subtitles",
        "real transcripts",
        "real screenshots",
        "real thumbnails",
        "real production documents",
        "private pilot material",
        "client material",
        "downloaded stock media",
        "online videos",
        "copyrighted media samples",
        "mobile phone clips",
        "drone clips",
        "screen recordings from real projects",
    ]
    for phrase in required:
        assert phrase in text


def test_metadata_privacy_requirements_are_documented():
    text = _doc_text()
    required = [
        "personal names",
        "production company names",
        "project names",
        "GPS coordinates",
        "device serial numbers",
        "camera serial numbers",
        "lens serial numbers",
        "local user names",
        "home directory paths",
        "drive labels",
        "cloud paths",
        "network paths",
        "real shoot dates",
        "real location names",
        "must not persist raw ffprobe JSON by default",
        "must not persist full format tags or full stream tags",
    ]
    for phrase in required:
        assert phrase in text


def test_future_fixture_manifest_policy_is_documented():
    text = _doc_text()
    required = [
        "tests/fixtures/local_media_agent/ffprobe_synthetic/fixture_manifest.json",
        "fixture_id",
        "relative_path",
        "fixture_category",
        "synthetic_origin",
        "expected_probe_status",
        "expected_media_kind",
        "expected_has_video",
        "expected_has_audio",
        "expected_duration_policy",
        "expected_privacy_safe",
        "human_reviewed",
        "relative paths only",
        "must not include absolute paths",
    ]
    for phrase in required:
        assert phrase in text


def test_future_statuses_and_path_policy_are_documented():
    text = _doc_text()
    required = [
        "available",
        "unsupported_media",
        "invalid_json",
        "permission_denied",
        "probe_failed",
        "privacy_redacted",
        "missing ffprobe status is already covered",
        "Timeout tests may be simulated",
        "Default output must use sanitized paths.",
        "local_relative_path may be enabled explicitly.",
        "hashed_path may be enabled explicitly.",
        "redacted_path may be enabled explicitly.",
        "local_absolute_path remains explicit opt-in only",
    ]
    for phrase in required:
        assert phrase in text


def test_future_output_policy_blocks_source_modification_and_output_escape():
    text = _doc_text()
    required = [
        "01_media_catalog/media_catalog.json",
        "01_media_catalog/technical_metadata.json",
        "00_project/processing_status.json",
        "99_logs/warnings.json",
        "99_logs/errors.json",
        "99_logs/privacy_events.json",
        "No output may be written beside the fixture source files.",
        "No fixture source file may be modified.",
    ]
    for phrase in required:
        assert phrase in text


def test_future_test_policy_and_human_review_are_documented():
    text = _doc_text()
    required = [
        "fixture manifest validity",
        "fixture file existence",
        "fixture file size limits",
        "relative path only storage",
        "no absolute path leaks",
        "no raw stdout persistence",
        "no raw stderr persistence",
        "no raw ffprobe JSON persistence",
        "allowed metadata schema only",
        "no scanner output outside --output-root",
        "no source fixture modification",
        "human review flag present",
        "the fixture is not real production material",
        "the fixture contains no private metadata",
        "safe to commit if binary",
    ]
    for phrase in required:
        assert phrase in text


def test_real_media_remains_blocked_and_saas_out_of_scope():
    text = _doc_text()
    required = [
        "Real media probing remains blocked after this contract.",
        "A future real media phase must be explicit and separate.",
        "This phase does not touch SaaS runtime.",
        "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger",
    ]
    for phrase in required:
        assert phrase in text


def test_this_phase_does_not_modify_scanner_runtime_or_add_probe_execution():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "shell=true" not in scanner_text
    assert "synthetic_video_minimal" not in scanner_text
    assert "fixture_manifest" not in scanner_text
    assert "technical_metadata.json" not in scanner_text
