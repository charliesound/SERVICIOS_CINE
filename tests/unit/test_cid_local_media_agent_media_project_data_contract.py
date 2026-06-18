from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_media_project_data_contract_v1.md"
)


def _read_doc() -> str:
    assert DOC.exists(), f"Missing expected data contract: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_declares_phase_and_documentation_only_scope():
    text = _read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.MEDIA_PROJECT.DATA_CONTRACT.V1" in text
    assert "documentation/test-only" in text
    assert "does not implement a scanner" in text
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
        "workers",
        "Future SaaS integration requires a separate explicit phase",
    ]:
        assert phrase in text


def test_contract_preserves_media_never_leaves_client_system():
    text = _read_doc()
    for phrase in [
        "Original media never leaves the client system",
        "video files",
        "audio files",
        "camera originals",
        "sound originals",
        "proxies",
        "extracted WAV files",
        "temporary analysis files",
        "explicit client authorization",
    ]:
        assert phrase in text


def test_contract_defines_core_project_entities():
    text = _read_doc()
    for phrase in [
        "ProjectManifest",
        "Path policy",
        "MediaAsset",
        "TechnicalMetadata",
        "VideoClip",
        "AudioClip",
        "SyncCandidate",
        "SyncResult",
        "TranscriptSegment",
        "SubtitleTrack",
        "SpanishSubtitleSegment",
        "EditorialSelect",
        "DavinciExportPackage",
    ]:
        assert phrase in text


def test_contract_defines_sync_and_review_safety():
    text = _read_doc()
    for phrase in [
        "timecode",
        "scene_take_roll_name",
        "waveform",
        "slate",
        "estimated_offset_seconds",
        "confidence",
        "drift_detected",
        "An uncertain sync must not be marked as final",
        "Human review flags",
        "Human review fields must never be removed",
    ]:
        assert phrase in text


def test_contract_defines_multilingual_and_spanish_subtitle_outputs():
    text = _read_doc()
    for phrase in [
        "original-language speech recognition output",
        "detected_language",
        "original_text",
        "The original transcript must be preserved separately from translations",
        "spanish_translation",
        "bilingual_original_plus_spanish",
        "davinci_importable_srt",
        "Spanish translated subtitles must use target language `es`",
        "Automatically generated Spanish subtitles are working subtitles unless human validated",
        "spanish_text",
        "human_validation_required",
    ]:
        assert phrase in text


def test_contract_defines_davinci_rough_cut_assist_outputs():
    text = _read_doc()
    for phrase in [
        "DavinciExportPackage",
        "rough_cut_assist",
        "subtitle_package",
        "marker_package",
        "subtitle_file_es",
        "otio_file",
        "fcpxml_file",
        "is_final_edit",
        "is_rough_cut_assist",
        "not a final automatic edit",
    ]:
        assert phrase in text


def test_contract_non_goals_protect_saas_and_real_media():
    text = _read_doc()
    for phrase in [
        "Non-goals of this phase",
        "Pydantic models",
        "ffprobe calls",
        "ffmpeg calls",
        "real media processing",
        "private disk access",
        "SaaS runtime",
        "database models",
        "Alembic",
        "Docker",
        "frontend",
        "AI Jobs",
        "credits",
        "ledger",
    ]:
        assert phrase in text


def test_contract_acceptance_criteria_cover_core_product_needs():
    text = _read_doc()
    for phrase in [
        "Acceptance criteria",
        "local-only project contract is documented",
        "Spanish translated subtitles are represented separately from original transcripts",
        "DaVinci rough-cut assist outputs are represented",
        "human review is represented",
        "explicit non-goals protect CID SaaS",
    ]:
        assert phrase in text
