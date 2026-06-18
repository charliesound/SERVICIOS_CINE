from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_metadata_schema_contract_v1.md"
)
SCANNER = Path("scripts/cid_media_agent_scan.py")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_metadata_schema_contract_document_exists_and_names_phase():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.METADATA.SCHEMA.CONTRACT.V1" in text
    assert "Scanner CLI ffprobe Metadata Schema Contract v1" in text
    assert "contract-only and test-only" in text


def test_metadata_schema_contract_blocks_runtime_media_probe_scope():
    text = _doc_text()
    required = [
        "This phase does not implement media probing.",
        "This phase does not execute ffprobe against video files.",
        "This phase does not execute ffprobe against audio files.",
        "This phase does not call ffmpeg.",
        "This phase does not parse real technical metadata.",
        "This phase does not create proxies.",
        "This phase does not transcribe media.",
        "This phase does not create subtitles.",
        "This phase does not create DaVinci files.",
    ]
    for phrase in required:
        assert phrase in text


def test_metadata_schema_contract_keeps_saas_and_billing_out_of_scope():
    text = _doc_text()
    assert "This phase does not touch SaaS runtime." in text
    assert "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger" in text


def test_metadata_schema_contract_defines_allowed_fields():
    text = _doc_text()
    required = [
        "technical_metadata",
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
    ]
    for phrase in required:
        assert phrase in text


def test_metadata_schema_contract_defines_statuses_and_warning_codes():
    text = _doc_text()
    required = [
        "not_requested",
        "skipped",
        "available",
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


def test_metadata_schema_contract_forbids_sensitive_persisted_data():
    text = _doc_text()
    required = [
        "full raw ffprobe JSON",
        "raw stdout",
        "raw stderr",
        "absolute input paths",
        "absolute output paths",
        "executable path to ffprobe",
        "local user names",
        "home directory paths",
        "environment variables",
        "shell command strings",
        "original command argv",
        "complete stream tags",
        "complete format tags",
        "device names",
        "volume names",
        "network paths",
        "cloud URLs",
    ]
    for phrase in required:
        assert phrase in text


def test_metadata_schema_contract_preserves_path_policy_and_output_root():
    text = _doc_text()
    required = [
        "must not bypass scanner path-policy",
        "Default scanner outputs must still avoid local absolute paths.",
        "sanitized_path",
        "local_relative_path",
        "hashed_path",
        "redacted_path",
        "local_absolute_path",
        "local_absolute_path must remain explicit opt-in only.",
        "01_media_catalog/media_catalog.json",
        "01_media_catalog/technical_metadata.json",
        "00_project/processing_status.json",
        "must not create outputs outside --output-root",
    ]
    for phrase in required:
        assert phrase in text


def test_metadata_schema_contract_requires_human_review_and_blocks_real_media():
    text = _doc_text()
    required = [
        "Technical metadata is production assistance, not final truth.",
        "editorial decisions",
        "sync decisions",
        "timecode decisions",
        "conform decisions",
        "delivery assumptions",
        "DaVinci handoff",
        "Avid handoff",
        "Premiere handoff",
        "external production reports",
        "synthetic placeholder fixtures only",
        "Real media probing must remain blocked until a later explicit phase.",
        "use bounded subprocess execution",
        "avoid shell=True",
        "avoid raw output persistence",
    ]
    for phrase in required:
        assert phrase in text


def test_this_phase_does_not_modify_scanner_into_media_probe_runtime():
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
