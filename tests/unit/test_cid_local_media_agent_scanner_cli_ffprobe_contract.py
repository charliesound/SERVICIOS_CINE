from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_contract_v1.md"
)

SCANNER = Path("scripts/cid_media_agent_scan.py")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_ffprobe_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Contract v1" in text
    assert "contract-only and test-only" in text


def test_ffprobe_contract_keeps_current_scanner_as_future_target_only():
    text = _doc_text()
    assert "scripts/cid_media_agent_scan.py" in text
    assert "future `ffprobe` integration contract" in text
    assert "before any runtime implementation" in text


def test_ffprobe_contract_explicitly_forbids_implementation_in_this_phase():
    text = _doc_text()
    required = [
        "This phase does not implement `ffprobe`.",
        "This phase does not call `ffmpeg`.",
        "This phase does not call `ffprobe`.",
        "This phase does not read real media metadata.",
        "This phase does not transcribe media.",
        "This phase does not create subtitles.",
        "This phase does not create proxies.",
        "This phase does not generate DaVinci files.",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_preserves_local_only_media_rule():
    text = _doc_text()
    required = [
        "All future `ffprobe` execution must happen on the client machine",
        "The scanner must never upload",
        "original video files",
        "original audio files",
        "proxies",
        "waveforms",
        "thumbnails",
        "technical metadata dumps containing absolute local paths",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_requires_safe_subprocess_controls():
    text = _doc_text()
    required = [
        "no shell=True",
        "explicit argv list",
        "timeout",
        "captured stdout and stderr",
        "controlled stderr truncation",
        "no environment secrets in output",
        "no user-controlled command templates",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_defines_timeout_and_failure_behavior():
    text = _doc_text()
    required = [
        "technical_metadata_status=timeout",
        "continue scanning other files",
        "avoid dumping raw command output",
        "ffprobe_missing",
        "ffprobe_timeout",
        "ffprobe_invalid_json",
        "ffprobe_permission_denied",
        "ffprobe_probe_failed",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_defines_metadata_allowlist_and_blocks_raw_json_default():
    text = _doc_text()
    required = [
        "duration_seconds",
        "format_name",
        "codec_type",
        "video_codec",
        "audio_codec",
        "frame_rate",
        "sample_rate",
        "timecode_detected",
        "probe_status",
        "The scanner must not persist full raw `ffprobe` JSON by default.",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_preserves_path_policy_privacy_modes():
    text = _doc_text()
    required = [
        "Default outputs must not expose local absolute paths.",
        "sanitized_path",
        "local_relative_path",
        "hashed_path",
        "redacted_path",
        "`local_absolute_path` may only be emitted with explicit opt-in.",
        "must not bypass the current path-policy",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_limits_output_locations_to_output_root():
    text = _doc_text()
    required = [
        "Future technical metadata may be written only under the configured local output root.",
        "01_media_catalog/media_catalog.json",
        "01_media_catalog/technical_metadata.json",
        "99_logs/privacy_events.jsonl",
        "99_logs/scanner.log",
        "must not create files outside `--output-root`",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_marks_raw_debug_as_explicit_opt_in_and_unsafe_for_sharing():
    text = _doc_text()
    required = [
        "Raw `ffprobe` stdout and stderr must not be stored by default.",
        "explicit opt-in is provided",
        "sensitive path material is redacted",
        "clearly marked as unsafe for sharing",
        "human review is required before external use",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_requires_human_review_before_editorial_or_delivery_use():
    text = _doc_text()
    required = [
        "Human review is required before",
        "editorial decisions",
        "delivery assumptions",
        "conform assumptions",
        "timecode-based sync decisions",
        "DaVinci handoff",
        "external sharing",
    ]
    for phrase in required:
        assert phrase in text


def test_ffprobe_contract_keeps_saas_and_billing_out_of_scope():
    text = _doc_text()
    forbidden_scope = [
        "SaaS runtime",
        "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger",
    ]
    for phrase in forbidden_scope:
        assert phrase in text


def test_scanner_does_not_introduce_ffprobe_media_probe_runtime():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()
    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "ffmpeg" not in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "duration_seconds" not in scanner_text
    assert "format_name" not in scanner_text
    assert "codec_type" not in scanner_text
    assert "streams" not in scanner_text
