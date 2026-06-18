from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_contract_v1.md"
)


def _read_doc() -> str:
    assert DOC.exists(), f"Missing expected scanner CLI contract: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_declares_phase_and_documentation_only_scope():
    text = _read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.CONTRACT.V1" in text
    assert "documentation/test-only" in text
    assert "does not implement scanner code" in text
    assert "CID Local Media Agent" in text
    assert "CID Editing Intelligence" in text


def test_contract_is_isolated_from_cid_saas_runtime():
    text = _read_doc()
    for phrase in [
        "SaaS isolation rule",
        "must not touch CID SaaS runtime",
        "backend routes",
        "database models",
        "Alembic migrations",
        "Docker configuration",
        "frontend code",
        "Stripe/payment code",
        "AI Jobs runtime",
        "credits",
        "ledger",
        "Future SaaS integration requires a separate explicit phase",
    ]:
        assert phrase in text


def test_contract_preserves_local_only_privacy_and_original_media():
    text = _read_doc()
    for phrase in [
        "Original media never leaves the client system",
        "must not upload, copy, move, rename, delete, rewrite, transcode, proxy, extract audio from, or modify original camera media",
        "original sound media",
        "Full local paths",
        "explicit client authorization",
    ]:
        assert phrase in text


def test_contract_defines_command_and_arguments():
    text = _read_doc()
    for phrase in [
        "cid-media-agent scan",
        "--input-root",
        "--output-root",
        "--project-id",
        "--project-name",
        "--privacy-mode",
        "--path-policy",
        "--dry-run",
        "--json",
        "--strict-local-only",
        "local_only",
    ]:
        assert phrase in text


def test_contract_defines_candidate_file_types_and_classification():
    text = _read_doc()
    for phrase in [
        ".mov",
        ".mp4",
        ".mxf",
        ".wav",
        ".bwf",
        ".aiff",
        ".ale",
        "camera_original",
        "production_sound",
        "proxy",
        "sidecar_metadata",
        "human_review_required",
    ]:
        assert phrase in text


def test_contract_defines_preflight_checks():
    text = _read_doc()
    for phrase in [
        "Preflight checks",
        "--input-root exists",
        "--input-root is readable",
        "--output-root can be created or is writable",
        "--input-root is not equal to `--output-root`",
        "privacy mode",
        "path policy is valid",
        "no SaaS integration is required",
    ]:
        assert phrase in text


def test_contract_limits_scanner_outputs_to_safe_folders():
    text = _read_doc()
    for phrase in [
        "The scanner may write only to these local output areas",
        "00_project/",
        "01_media_catalog/",
        "99_logs/",
        "must not write to sync, transcript, subtitle, editorial, DaVinci, or temp folders",
    ]:
        assert phrase in text


def test_contract_defines_required_scan_outputs():
    text = _read_doc()
    for phrase in [
        "project_manifest.json",
        "processing_status.json",
        "privacy_report.md",
        "media_catalog.json",
        "media_catalog.csv",
        "media_catalog.md",
        "scan_warnings.json",
        "manual_media_review.csv",
        "processing_log.md",
        "privacy_events.json",
    ]:
        assert phrase in text


def test_contract_defines_media_catalog_fields():
    text = _read_doc()
    for phrase in [
        "asset_id",
        "media_type",
        "source_kind",
        "path_policy",
        "file_size_bytes",
        "technical_metadata",
        "warnings",
        "human_review_required",
        "conceptual fields only",
    ]:
        assert phrase in text


def test_contract_defines_dry_run_json_and_exit_codes():
    text = _read_doc()
    for phrase in [
        "Dry-run behavior",
        "must not write the full output package",
        "JSON output behavior",
        "files_seen",
        "candidate_media_count",
        "warnings_count",
        "human_review_required_count",
        "Exit codes",
        "`0`: scan completed successfully",
        "`3`: privacy or safety violation",
    ]:
        assert phrase in text


def test_contract_requires_human_review_for_uncertain_results():
    text = _read_doc()
    for phrase in [
        "Human review",
        "human_review_index.md",
        "manual_media_review.csv",
        "media type is unknown",
        "source kind is ambiguous",
        "possible duplicate assets exist",
        "classification is uncertain",
    ]:
        assert phrase in text


def test_contract_forbidden_behavior_protects_media_and_saas():
    text = _read_doc()
    for phrase in [
        "Forbidden behavior",
        "copy original video files",
        "copy original audio files",
        "modify original media",
        "transcode media",
        "extract audio",
        "transcribe audio",
        "translate subtitles",
        "create DaVinci timelines",
        "upload files",
        "call CID SaaS",
        "call Stripe",
        "call AI Jobs",
        "write database rows",
        "touch Docker",
        "touch frontend",
    ]:
        assert phrase in text


def test_contract_acceptance_criteria_cover_scanner_cli_baseline():
    text = _read_doc()
    for phrase in [
        "Acceptance criteria",
        "scanner CLI command contract is documented",
        "preflight checks are documented",
        "supported candidate file types are documented",
        "local-only privacy is preserved",
        "output folders are limited to scanner-safe areas",
        "dry-run and JSON behaviors are documented",
        "forbidden behavior protects original media and CID SaaS",
    ]:
        assert phrase in text
