import json
from pathlib import Path


MANIFEST = Path("tests/fixtures/local_media_agent/ffprobe_synthetic/fixture_manifest.json")
FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
SCANNER = Path("scripts/cid_media_agent_scan.py")


def _manifest() -> dict:
    assert MANIFEST.exists(), f"Missing manifest: {MANIFEST}"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_exists_and_names_phase():
    data = _manifest()
    assert data["manifest_version"] == 1
    assert data["phase"] == "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.MANIFEST.V1"
    assert data["manifest_scope"] == "synthetic_ffprobe_fixtures_only"
    assert data["manifest_mode"] == "declarative_manifest_only_no_binary_fixtures"


def test_manifest_keeps_execution_and_real_media_disabled():
    data = _manifest()
    assert data["binary_fixtures_created"] is False
    assert data["ffprobe_execution_allowed"] is False
    assert data["ffmpeg_execution_allowed"] is False
    assert data["subprocess_execution_allowed"] is False
    assert data["real_media_allowed"] is False


def test_manifest_top_level_policy_values_are_safe():
    data = _manifest()
    assert data["generated_by"] == "local_media_agent_test_fixture_contract"
    assert data["fixture_root"] == "tests/fixtures/local_media_agent/ffprobe_synthetic"
    assert data["path_policy"] == "relative_paths_only"
    assert data["privacy_policy"] == "no_private_metadata_no_real_media"
    assert data["size_policy"] == "tiny_fixtures_only"
    assert data["human_review_policy"] == "required_before_commit"


def test_manifest_fixture_entries_have_required_fields():
    data = _manifest()
    required = {
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
    }
    assert isinstance(data["fixtures"], list)
    assert len(data["fixtures"]) == 6
    for fixture in data["fixtures"]:
        assert required <= set(fixture)


def test_manifest_uses_only_allowed_fixture_categories():
    allowed = {
        "synthetic_video_minimal",
        "synthetic_audio_minimal",
        "synthetic_video_with_audio_minimal",
        "synthetic_unsupported_media_placeholder",
        "synthetic_corrupt_or_invalid_media_placeholder",
        "synthetic_permission_denied_placeholder",
    }
    for fixture in _manifest()["fixtures"]:
        assert fixture["fixture_category"] in allowed


def test_manifest_uses_only_allowed_media_kinds():
    allowed = {
        "video",
        "audio",
        "video_with_audio",
        "unsupported_placeholder",
        "invalid_placeholder",
        "permission_placeholder",
    }
    for fixture in _manifest()["fixtures"]:
        assert fixture["media_kind"] in allowed


def test_manifest_uses_only_allowed_synthetic_origins():
    allowed = {
        "generated_by_test_command",
        "committed_synthetic_binary",
        "committed_text_placeholder",
        "committed_invalid_placeholder",
        "permission_scenario_placeholder",
    }
    for fixture in _manifest()["fixtures"]:
        assert fixture["synthetic_origin"] in allowed


def test_manifest_uses_only_allowed_expected_statuses():
    allowed = {
        "available",
        "unsupported_media",
        "invalid_json",
        "permission_denied",
        "probe_failed",
        "privacy_redacted",
    }
    for fixture in _manifest()["fixtures"]:
        assert fixture["expected_probe_status"] in allowed


def test_manifest_relative_paths_are_safe():
    forbidden_fragments = ["..", "\\", "$", "~", ":", "/home/", "/mnt/", "C:", "D:"]
    for fixture in _manifest()["fixtures"]:
        rel = fixture["relative_path"]
        assert rel
        assert not rel.startswith("/")
        for fragment in forbidden_fragments:
            assert fragment not in rel


def test_manifest_does_not_create_binary_fixture_files():
    files = [path for path in FIXTURE_ROOT.rglob("*") if path.is_file()]
    assert files == [MANIFEST]


def test_manifest_flags_are_booleans_and_commit_blocked_for_future_files():
    for fixture in _manifest()["fixtures"]:
        assert isinstance(fixture["expected_has_video"], bool)
        assert isinstance(fixture["expected_has_audio"], bool)
        assert fixture["expected_privacy_safe"] is True
        assert fixture["human_reviewed"] is False
        assert fixture["commit_allowed"] is False


def test_manifest_size_and_duration_policies_are_manifest_only():
    duration_allowed = {"less_than_or_equal_2_seconds", "placeholder_no_duration"}
    size_allowed = {"manifest_only_no_file"}
    for fixture in _manifest()["fixtures"]:
        assert fixture["expected_duration_policy"] in duration_allowed
        assert fixture["expected_size_policy"] in size_allowed


def test_manifest_contains_no_private_or_absolute_path_terms():
    raw = MANIFEST.read_text(encoding="utf-8")
    forbidden = [
        "/home/",
        "/mnt/",
        "C:",
        "D:",
        "\\",
        "client",
        "production company",
        "gps",
        "serial",
        "raw ffprobe",
        "raw stdout",
        "raw stderr",
    ]
    lowered = raw.lower()
    for token in forbidden:
        assert token.lower() not in lowered


def test_scanner_runtime_is_not_modified_for_manifest_handling():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()
    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "fixture_manifest.json" not in scanner_text
    assert "synthetic_ffprobe_fixtures_only" not in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "shell=true" not in scanner_text
