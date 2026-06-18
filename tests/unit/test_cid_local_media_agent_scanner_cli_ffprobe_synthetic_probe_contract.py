from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_synthetic_probe_contract_v1.md"
)
SCANNER = Path("scripts/cid_media_agent_scan.py")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_synthetic_probe_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.PROBE.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Synthetic Probe Contract v1" in text
    assert "contract-only and test-only" in text


def test_synthetic_probe_contract_explicitly_blocks_runtime_implementation():
    text = _doc_text()
    required = [
        "It does not execute ffprobe.",
        "It does not modify scanner runtime.",
        "It does not parse media metadata.",
        "It does not inspect real video or audio files.",
        "This phase does not implement ffprobe probing.",
        "This phase does not add subprocess runtime.",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_keeps_saas_and_billing_out_of_scope():
    text = _doc_text()
    assert "This phase does not touch SaaS runtime." in text
    assert "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger" in text


def test_synthetic_probe_contract_limits_future_fixtures_to_synthetic_only():
    text = _doc_text()
    required = [
        "synthetic fixture assets only",
        "generated for tests",
        "no client content",
        "no production content",
        "no personal names",
        "no project names",
        "no real locations",
        "no embedded private metadata",
        "documented as synthetic",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_forbids_real_project_material():
    text = _doc_text()
    required = [
        "real camera originals",
        "real sound files",
        "real editorial exports",
        "real client proxies",
        "real subtitle files from projects",
        "real screenshots",
        "real thumbnails",
        "real transcripts",
        "private production documents",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_defines_future_safe_execution_controls():
    text = _doc_text()
    required = [
        "explicit argv list",
        "no shell=True",
        "timeout",
        "captured stdout",
        "captured stderr",
        "stderr truncation",
        "no command template expansion",
        "no environment secret exposure",
        "no executable path exposure in persisted output",
        "no raw stdout persistence by default",
        "no raw stderr persistence by default",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_limits_future_outputs_to_output_root():
    text = _doc_text()
    required = [
        "01_media_catalog/media_catalog.json",
        "01_media_catalog/technical_metadata.json",
        "00_project/processing_status.json",
        "99_logs/warnings.json",
        "99_logs/errors.json",
        "99_logs/privacy_events.json",
        "must not create outputs outside --output-root",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_preserves_metadata_schema_restrictions():
    text = _doc_text()
    required = [
        "probe_status",
        "probe_warning_code",
        "duration_seconds",
        "format_name",
        "stream_count",
        "video",
        "audio",
        "codec_name",
        "codec_type",
        "width",
        "height",
        "frame_rate",
        "timecode_detected",
        "sample_rate",
        "channel_count",
        "must not persist full raw ffprobe JSON",
        "must not persist full stream tags or full format tags",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_preserves_privacy_restrictions():
    text = _doc_text()
    required = [
        "absolute input paths",
        "absolute output paths",
        "ffprobe executable path",
        "local user names",
        "home directory paths",
        "environment variables",
        "shell commands",
        "raw argv",
        "raw stdout",
        "raw stderr",
        "device names",
        "volume names",
        "network paths",
        "cloud URLs",
        "The existing path-policy remains authoritative.",
        "local_absolute_path must remain explicit opt-in only.",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_defines_failure_statuses_and_warnings():
    text = _doc_text()
    required = [
        "skipped",
        "missing",
        "timeout",
        "invalid_json",
        "permission_denied",
        "unsupported_media",
        "probe_failed",
        "privacy_redacted",
        "ffprobe_missing",
        "ffprobe_timeout",
        "ffprobe_invalid_json",
        "ffprobe_permission_denied",
        "ffprobe_unsupported_media",
        "ffprobe_probe_failed",
        "ffprobe_privacy_redacted",
        "ffprobe_metadata_incomplete",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_probe_contract_requires_human_review_and_blocks_real_media():
    text = _doc_text()
    required = [
        "Human review is required",
        "editorial decisions",
        "sync decisions",
        "timecode decisions",
        "conform decisions",
        "delivery assumptions",
        "DaVinci handoff",
        "Avid handoff",
        "Premiere handoff",
        "external production reports",
        "Real media probing remains blocked after this contract.",
        "A future real media phase must be explicit and separate.",
    ]
    for phrase in required:
        assert phrase in text


def test_this_phase_does_not_modify_scanner_into_probe_runtime():
    assert SCANNER.exists(), f"Missing scanner script: {SCANNER}"
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "shutil.which(\"ffprobe\")" in scanner_text
    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "shell=true" not in scanner_text
    assert "duration_seconds" not in scanner_text
    assert "format_name" not in scanner_text
    assert "codec_name" not in scanner_text
    assert "codec_type" not in scanner_text
    assert "stream_count" not in scanner_text
    assert "sample_rate" not in scanner_text
    assert "channel_count" not in scanner_text
    assert "timecode_detected" not in scanner_text
