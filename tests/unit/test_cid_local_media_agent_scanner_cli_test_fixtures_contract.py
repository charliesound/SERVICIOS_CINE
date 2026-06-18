from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_test_fixtures_contract_v1.md"
)


def _read_doc() -> str:
    assert DOC.exists(), f"Missing expected test fixtures contract: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_declares_phase_and_documentation_only_scope():
    text = _read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.TEST.FIXTURES.CONTRACT.V1" in text
    assert "documentation/test-only" in text
    assert "cid-media-agent scan" in text
    assert "does not implement scanner code" in text


def test_contract_keeps_fixtures_synthetic_and_private():
    text = _read_doc()
    for phrase in [
        "Fixtures must never contain real client media",
        "synthetic file names",
        "tiny placeholder files",
        "deterministic dummy content",
        "must not include copied camera originals",
        "copied sound originals",
        "copied video files",
        "copied audio files",
    ]:
        assert phrase in text


def test_contract_defines_fixture_root_and_families():
    text = _read_doc()
    for phrase in [
        "tests/fixtures/local_media_agent/scanner_cli/",
        "empty_input_root",
        "simple_camera_only",
        "simple_sound_only",
        "mixed_camera_sound_proxy",
        "sidecar_metadata_only",
        "nested_project_tree",
        "ambiguous_unknown_files",
        "unsafe_input_output_overlap",
        "path_policy_examples",
        "json_summary_expected_outputs",
    ]:
        assert phrase in text


def test_contract_defines_placeholder_file_policy():
    text = _read_doc()
    for phrase in [
        ".mov",
        ".mp4",
        ".mxf",
        ".wav",
        ".bwf",
        ".aiff",
        ".flac",
        ".ale",
        ".edl",
        "not playable media",
        "not extracted from real media",
    ]:
        assert phrase in text


def test_contract_forbids_real_sensitive_fixture_content():
    text = _read_doc()
    for phrase in [
        "real project titles",
        "real client names",
        "real crew names",
        "real actor names",
        "real location names",
        "real addresses",
        "real emails",
        "real phone numbers",
        "real GPS coordinates",
        "real transcripts",
        "real subtitles",
    ]:
        assert phrase in text


def test_contract_documents_expected_outputs():
    text = _read_doc()
    for phrase in [
        "media_catalog.json",
        "media_catalog.csv",
        "media_catalog.md",
        "scan_warnings.json",
        "manual_media_review.csv",
        "privacy_report.md",
        "processing_status.json",
        "processing_log.md",
        "privacy_events.json",
    ]:
        assert phrase in text


def test_contract_preserves_scanner_safe_output_restriction():
    text = _read_doc()
    for phrase in [
        "Scanner-safe folders",
        "00_project/",
        "01_media_catalog/",
        "99_logs/",
        "02_sync/",
        "03_transcripts_original/",
        "04_subtitles_spanish/",
        "06_davinci/",
        "Those folders belong to later phases",
    ]:
        assert phrase in text


def test_contract_defines_dry_run_json_and_path_policy_behavior():
    text = _read_doc()
    for phrase in [
        "Dry-run fixture behavior",
        "--dry-run",
        "does not create the full output package",
        "JSON fixture behavior",
        "--json",
        "does not leak full local paths",
        "local_absolute_path",
        "local_relative_path",
        "sanitized_path",
        "hashed_path",
        "redacted_path",
    ]:
        assert phrase in text


def test_contract_defines_unsafe_scenario_fixtures():
    text = _read_doc()
    for phrase in [
        "Unsafe scenario fixtures",
        "input root equals output root",
        "output root is inside input root",
        "input root is missing",
        "input root is unreadable",
        "output root is not writable",
        "path policy is invalid",
        "privacy mode is invalid",
        "SaaS integration is requested",
    ]:
        assert phrase in text


def test_contract_defines_human_review_fixture_behavior():
    text = _read_doc()
    for phrase in [
        "Human review fixture behavior",
        "media type is unknown",
        "source kind is ambiguous",
        "possible duplicate assets exist",
        "filename classification is uncertain",
        "human_review_required",
    ]:
        assert phrase in text


def test_contract_forbidden_behavior_protects_real_media_and_saas():
    text = _read_doc()
    for phrase in [
        "Forbidden behavior",
        "add real media",
        "add playable media",
        "add extracted audio",
        "add thumbnails",
        "add waveform files",
        "call ffprobe",
        "call ffmpeg",
        "call CID SaaS",
        "call Stripe",
        "call AI Jobs",
        "write database rows",
        "touch Docker",
        "touch frontend",
    ]:
        assert phrase in text


def test_contract_acceptance_criteria_cover_fixture_baseline():
    text = _read_doc()
    for phrase in [
        "Acceptance criteria",
        "fixture root is documented",
        "required fixture families are documented",
        "placeholder file policy is documented",
        "forbidden real content is documented",
        "expected scanner outputs are documented",
        "unsafe scenario fixtures are documented",
        "forbidden behavior protects real media and CID SaaS",
    ]:
        assert phrase in text
