from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_local_output_contract_v1.md"
)


def _read_doc() -> str:
    assert DOC.exists(), f"Missing expected local output contract: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_declares_phase_and_documentation_only_scope():
    text = _read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.LOCAL_OUTPUT.CONTRACT.V1" in text
    assert "documentation/test-only" in text
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


def test_contract_preserves_local_only_privacy():
    text = _read_doc()
    for phrase in [
        "Original media never leaves the client system",
        "must not contain copied camera originals",
        "must not contain copied sound originals",
        "must not rename, move, delete, rewrite, or modify original media",
        "Temporary files must remain local",
        "Temporary files must not be uploaded",
    ]:
        assert phrase in text


def test_contract_defines_required_top_level_layout():
    text = _read_doc()
    for folder in [
        "00_project/",
        "01_media_catalog/",
        "02_sync/",
        "03_transcripts_original/",
        "04_subtitles_spanish/",
        "05_editorial_summary/",
        "06_davinci/",
        "90_temp/",
        "99_logs/",
    ]:
        assert folder in text


def test_contract_defines_project_and_media_catalog_outputs():
    text = _read_doc()
    for phrase in [
        "project_manifest.json",
        "processing_status.json",
        "privacy_report.md",
        "human_review_index.md",
        "media_catalog.json",
        "media_catalog.csv",
        "media_catalog.md",
        "ffprobe_summary.json",
        "manual_media_review.csv",
    ]:
        assert phrase in text


def test_contract_defines_sync_outputs_and_uncertain_sync_rule():
    text = _read_doc()
    for phrase in [
        "sync_candidates.json",
        "sync_results.json",
        "sync_report.md",
        "sync_confidence.csv",
        "manual_sync_review.csv",
        "An uncertain sync must not be marked as final",
    ]:
        assert phrase in text


def test_contract_defines_transcripts_and_spanish_subtitles():
    text = _read_doc()
    for phrase in [
        "03_transcripts_original/",
        "transcripts_original.json",
        "clip_001_original.en.txt",
        "The original transcript must be preserved separately from translations",
        "04_subtitles_spanish/",
        "subtitles_es_working.json",
        "clip_001_es_trabajo.srt",
        "timeline_subtitles_es_trabajo.srt",
        "Spanish translated subtitles must use target language `es`",
        "Automatically generated Spanish subtitles are working subtitles unless human validated",
    ]:
        assert phrase in text


def test_contract_defines_editorial_and_davinci_outputs():
    text = _read_doc()
    for phrase in [
        "05_editorial_summary/",
        "editorial_selects.json",
        "resumen_general.md",
        "mejores_momentos.md",
        "translator_review.md",
        "06_davinci/",
        "rough_cut_selects.otio",
        "rough_cut_markers.csv",
        "timeline_subtitles_es.srt",
        "import_instructions.md",
        "davinci_package_manifest.json",
        "rough-cut assist, not a final automatic edit",
    ]:
        assert phrase in text


def test_contract_defines_temp_and_logs_safely():
    text = _read_doc()
    for phrase in [
        "90_temp/",
        "audio_analysis/",
        "waveform_cache/",
        "transcription_cache/",
        "ffprobe_cache/",
        "safe cleanup mode",
        "99_logs/",
        "processing_log.md",
        "errors.json",
        "license_events.json",
        "privacy_events.json",
        "Logs must avoid full local paths",
        "Logs must not include video frames",
    ]:
        assert phrase in text


def test_contract_requires_human_review_outputs():
    text = _read_doc()
    for phrase in [
        "Human review index",
        "scan review",
        "sync review",
        "transcript review",
        "translation review",
        "subtitle review",
        "editorial select review",
        "DaVinci export review",
        "Human review files must not be removed",
    ]:
        assert phrase in text


def test_contract_defines_naming_and_safety_rules():
    text = _read_doc()
    for phrase in [
        "File naming rules",
        "_es_trabajo",
        "_original.<language>",
        "Safety requirements",
        "copy original video files",
        "copy original audio files",
        "send full local paths to CID SaaS",
        "mark working subtitles as final",
        "mark rough-cut assist as final edit",
    ]:
        assert phrase in text


def test_contract_acceptance_and_non_goals_protect_runtime():
    text = _read_doc()
    for phrase in [
        "Acceptance criteria",
        "all required top-level folders are documented",
        "original media copying is forbidden",
        "temporary files are constrained to `90_temp/`",
        "logs are constrained to `99_logs/`",
        "Spanish working subtitle outputs are defined",
        "DaVinci rough-cut assist outputs are defined",
        "Non-goals of this phase",
        "filesystem creation",
        "ffprobe calls",
        "ffmpeg calls",
        "SaaS runtime",
        "database models",
        "Alembic",
        "Docker",
        "AI Jobs",
        "credits",
        "ledger",
    ]:
        assert phrase in text
