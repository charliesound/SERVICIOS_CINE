from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_synthetic_fixtures_manifest_contract_v1.md"
)
SCANNER = Path("scripts/cid_media_agent_scan.py")
FUTURE_FIXTURE_DIR = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
FUTURE_MANIFEST = FUTURE_FIXTURE_DIR / "fixture_manifest.json"


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_manifest_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.MANIFEST.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Synthetic Fixtures Manifest Contract v1" in text
    assert "documentation-only and test-only" in text


def test_manifest_contract_does_not_create_media_fixtures_or_runtime_and_allows_later_manifest_only_phase():
    text = _doc_text()
    required = [
        "It does not create fixture_manifest.json.",
        "It does not create fixture folders.",
        "It does not create media fixtures.",
        "It does not create video files.",
        "It does not create audio files.",
        "It does not execute ffprobe.",
        "It does not execute ffmpeg.",
        "It does not modify scanner runtime.",
        "It does not add subprocess execution.",
        "It does not inspect real media.",
    ]
    for phrase in required:
        assert phrase in text

    if FUTURE_FIXTURE_DIR.exists():
        files = sorted(path.relative_to(FUTURE_FIXTURE_DIR).as_posix() for path in FUTURE_FIXTURE_DIR.rglob("*") if path.is_file())
        assert files == ["fixture_manifest.json"]


def test_future_manifest_path_is_documented_but_not_created():
    text = _doc_text()
    assert "tests/fixtures/local_media_agent/ffprobe_synthetic/fixture_manifest.json" in text
    assert "This contract phase must not create that file." in text
    assert "This contract phase must not create the tests/fixtures/local_media_agent/ffprobe_synthetic/ folder." in text


def test_required_manifest_top_level_fields_are_documented():
    text = _doc_text()
    required = [
        "manifest_version",
        "phase",
        "manifest_scope",
        "generated_by",
        "fixture_root",
        "path_policy",
        "privacy_policy",
        "size_policy",
        "human_review_policy",
        "fixtures",
    ]
    for phrase in required:
        assert phrase in text


def test_required_manifest_top_level_values_are_documented():
    text = _doc_text()
    required = [
        "manifest_version: 1",
        "phase: CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.MANIFEST.V1",
        "manifest_scope: synthetic_ffprobe_fixtures_only",
        "generated_by: local_media_agent_test_fixture_contract",
        "fixture_root: tests/fixtures/local_media_agent/ffprobe_synthetic",
        "path_policy: relative_paths_only",
        "privacy_policy: no_private_metadata_no_real_media",
        "size_policy: tiny_fixtures_only",
        "human_review_policy: required_before_commit",
    ]
    for phrase in required:
        assert phrase in text


def test_required_fixture_entry_fields_are_documented():
    text = _doc_text()
    required = [
        "fixture_id",
        "relative_path",
        "fixture_category",
        "media_kind",
        "synthetic_origin",
        "expected_probe_status",
        "expected_has_video",
        "expected_has_audio",
        "expected_duration_policy",
        "expected_size_policy",
        "expected_privacy_safe",
        "human_reviewed",
        "commit_allowed",
        "notes",
    ]
    for phrase in required:
        assert phrase in text


def test_fixture_identifier_policy_blocks_real_project_identifiers():
    text = _doc_text()
    required = [
        "fixture_id must be stable, lowercase and descriptive.",
        "client names",
        "project names",
        "people names",
        "production company names",
        "real locations",
        "shoot dates",
        "camera roll names",
        "sound roll names",
        "drive names",
        "local user names",
    ]
    for phrase in required:
        assert phrase in text


def test_relative_path_policy_blocks_absolute_and_escape_paths():
    text = _doc_text()
    required = [
        "relative_path must be relative to tests/fixtures/local_media_agent/ffprobe_synthetic",
        "relative_path must not be absolute.",
        "..",
        "leading slash",
        "drive letters",
        "home directory paths",
        "user names",
        "network paths",
        "cloud paths",
        "backslashes",
        "environment variable syntax",
    ]
    for phrase in required:
        assert phrase in text


def test_allowed_fixture_categories_and_media_kinds_are_documented():
    text = _doc_text()
    required = [
        "synthetic_video_minimal",
        "synthetic_audio_minimal",
        "synthetic_video_with_audio_minimal",
        "synthetic_unsupported_media_placeholder",
        "synthetic_corrupt_or_invalid_media_placeholder",
        "synthetic_permission_denied_placeholder",
        "video",
        "audio",
        "video_with_audio",
        "unsupported_placeholder",
        "invalid_placeholder",
        "permission_placeholder",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_origin_policy_blocks_real_and_downloaded_sources():
    text = _doc_text()
    required = [
        "generated_by_test_command",
        "committed_synthetic_binary",
        "committed_text_placeholder",
        "committed_invalid_placeholder",
        "permission_scenario_placeholder",
        "real media",
        "client media",
        "downloaded stock media",
        "online videos",
        "mobile phone clips",
        "drone clips",
        "screen recordings",
        "private pilot material",
    ]
    for phrase in required:
        assert phrase in text


def test_expected_probe_status_policy_is_documented():
    text = _doc_text()
    required = [
        "available",
        "unsupported_media",
        "invalid_json",
        "permission_denied",
        "probe_failed",
        "privacy_redacted",
        "missing ffprobe status is handled by availability preflight",
        "Timeout behavior should be tested through mocked execution",
    ]
    for phrase in required:
        assert phrase in text


def test_boolean_duration_and_size_policies_are_documented():
    text = _doc_text()
    required = [
        "expected_has_video",
        "expected_has_audio",
        "expected_privacy_safe",
        "human_reviewed",
        "commit_allowed",
        "less_than_or_equal_2_seconds",
        "placeholder_no_duration",
        "less_than_or_equal_512_kib",
        "placeholder_tiny_file",
        "manifest_only_no_file",
        "must not exceed 2 MiB total",
    ]
    for phrase in required:
        assert phrase in text


def test_manifest_privacy_restrictions_are_documented():
    text = _doc_text()
    required = [
        "absolute input paths",
        "absolute output paths",
        "local user names",
        "home directory paths",
        "drive labels",
        "network paths",
        "cloud paths",
        "GPS coordinates",
        "real location names",
        "real shoot dates",
        "project names",
        "client names",
        "production company names",
        "camera serial numbers",
        "lens serial numbers",
        "device serial numbers",
        "raw ffprobe JSON",
        "raw stdout",
        "raw stderr",
        "shell commands",
        "full argv",
    ]
    for phrase in required:
        assert phrase in text


def test_manifest_output_and_source_file_restrictions_are_documented():
    text = _doc_text()
    required = [
        "Future probe outputs must still be written under --output-root.",
        "The manifest must not authorize outputs beside fixture source files.",
        "The manifest must not authorize modifying fixture source files.",
    ]
    for phrase in required:
        assert phrase in text


def test_human_review_and_real_media_block_are_documented():
    text = _doc_text()
    required = [
        "The manifest must require human review before fixture acceptance.",
        "the fixture is synthetic",
        "the fixture is not derived from real production material",
        "the fixture contains no private metadata",
        "safe to commit if binary",
        "the fixture does not create product claims",
        "Real media probing remains blocked after this contract.",
        "A future real media phase must be explicit and separate.",
    ]
    for phrase in required:
        assert phrase in text


def test_saas_database_and_runtime_non_goals_are_documented():
    text = _doc_text()
    required = [
        "This phase does not implement ffprobe probing.",
        "This phase does not implement fixture generation.",
        "This phase does not add fixture binary files.",
        "This phase does not add fixture_manifest.json.",
        "This phase does not call ffprobe.",
        "This phase does not call ffmpeg.",
        "This phase does not add subprocess runtime.",
        "This phase does not modify scripts/cid_media_agent_scan.py.",
        "This phase does not touch SaaS runtime.",
        "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger",
    ]
    for phrase in required:
        assert phrase in text


def test_this_phase_does_not_modify_scanner_runtime_or_add_manifest_handling():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "shell=true" not in scanner_text
    assert "fixture_manifest.json" not in scanner_text
    assert "synthetic_ffprobe_fixtures_only" not in scanner_text
    assert "expected_probe_status" not in scanner_text
    assert "committed_synthetic_binary" not in scanner_text
