from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_contract_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_contract_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Contract v1" in text


def test_contract_is_not_implementation():
    text = read_doc()
    required = [
        "contract-only",
        "does not implement the report generator",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add external command execution",
        "does not scan real client media",
        "does not read real video files",
        "does not read real audio files",
        "does not modify scanner runtime",
        "does not modify SaaS runtime",
        "does not create an installer",
        "does not create licensing or activation logic",
    ]
    for item in required:
        assert item in text


def test_audited_baseline_and_decision_are_recorded():
    text = read_doc()
    assert "541278a" in text
    assert "CONTINUE_BUT_PIVOT_TOWARD_VISIBLE_SYNTHETIC_DEMO" in text


def test_demo_positioning_message_is_present():
    text = read_doc()
    assert "analiza una carpeta local de material audiovisual sin subir vídeos ni audios a la nube" in text
    assert "radiografía técnica y editorial" in text


def test_intended_demo_audience_is_broad_and_audiovisual():
    text = read_doc()
    roles = [
        "producer",
        "director",
        "assistant director",
        "editor",
        "assistant editor",
        "DIT",
        "postproduction supervisor",
        "sound editor",
        "subtitle coordinator",
        "trusted early commercial contact",
    ]
    for role in roles:
        assert role in text


def test_demo_promise_contains_visible_report_elements():
    text = read_doc()
    required = [
        "local input folder label",
        "local output report label",
        "detected media-like items",
        "synthetic technical metadata",
        "synthetic warnings",
        "suggested folder organization",
        "editorial preparation notes",
        "postproduction preparation notes",
        "privacy confirmation",
        "zero cloud upload confirmation",
        "next-step recommendations",
    ]
    for item in required:
        assert item in text


def test_required_report_formats_are_declared():
    text = read_doc()
    for fmt in ["JSON report", "Markdown report", "HTML report"]:
        assert fmt in text


def test_required_report_sections_are_complete():
    text = read_doc()
    sections = [
        "Executive summary",
        "Local-only privacy notice",
        "Input folder summary",
        "Detected media-like inventory",
        "Synthetic technical metadata summary",
        "Clip grouping proposal",
        "Audio and video relationship hints",
        "Potential sync preparation notes",
        "Editorial preparation notes",
        "Postproduction risk warnings",
        "Suggested folder organization",
        "Subtitle and transcription readiness notes",
        "DaVinci Resolve future export readiness notes",
        "Items requiring human review",
        "Next recommended actions",
        "Report limitations",
    ]
    for section in sections:
        assert section in text


def test_privacy_statements_are_explicit():
    text = read_doc()
    statements = [
        "no video file was uploaded",
        "no audio file was uploaded",
        "no client media left the local machine",
        "no cloud analysis was required",
        "synthetic demo metadata was used",
        "private absolute paths are hidden",
        "raw filenames may be replaced by safe labels",
        "human review is required before production decisions",
    ]
    for statement in statements:
        assert statement in text


def test_synthetic_input_model_is_defined():
    text = read_doc()
    labels = [
        "LOCAL_PROJECT_INPUT_SYNTHETIC",
        "CAM_A_SYNTHETIC_CLIP_001",
        "CAM_A_SYNTHETIC_CLIP_002",
        "CAM_B_SYNTHETIC_CLIP_001",
        "AUDIO_SYNTHETIC_TAKE_001",
        "AUDIO_SYNTHETIC_TAKE_002",
        "STILLS_SYNTHETIC_REFERENCE_001",
        "DOC_SYNTHETIC_NOTES_001",
    ]
    for label in labels:
        assert label in text


def test_synthetic_media_categories_are_complete():
    text = read_doc()
    categories = [
        "video",
        "audio",
        "still image",
        "production document",
        "unknown or unsupported",
        "ignored non-media item",
    ]
    for category in categories:
        assert category in text


def test_synthetic_metadata_fields_are_complete():
    text = read_doc()
    fields = [
        "safe_item_id",
        "safe_display_label",
        "category",
        "container_hint",
        "codec_hint",
        "duration_hint",
        "frame_rate_hint",
        "resolution_hint",
        "audio_channels_hint",
        "sample_rate_hint",
        "timecode_hint",
        "camera_or_recorder_hint",
        "shooting_day_hint",
        "scene_or_block_hint",
        "sync_candidate_group",
        "language_hint",
        "transcription_readiness",
        "subtitle_readiness",
        "human_review_required",
        "warning_codes",
    ]
    for field in fields:
        assert field in text


def test_warning_vocabulary_is_complete():
    text = read_doc()
    warnings = [
        "MISSING_AUDIO_PAIR",
        "POSSIBLE_DOUBLE_SYSTEM_SOUND",
        "POSSIBLE_CAMERA_SPLIT",
        "MISSING_TIMECODE",
        "FRAME_RATE_MISMATCH",
        "SAMPLE_RATE_MISMATCH",
        "LOW_AUDIO_CHANNEL_INFORMATION",
        "UNSUPPORTED_CONTAINER_HINT",
        "UNKNOWN_MEDIA_TYPE",
        "NEEDS_HUMAN_REVIEW",
        "READY_FOR_EDITOR_REVIEW",
        "READY_FOR_DIT_REVIEW",
        "READY_FOR_SOUND_REVIEW",
    ]
    for warning in warnings:
        assert warning in text


def test_suggested_folder_organization_is_defined_without_file_mutation():
    text = read_doc()
    folders = [
        "01_VIDEO",
        "02_AUDIO",
        "03_STILLS",
        "04_DOCUMENTS",
        "05_REPORTS",
        "06_REVIEW_NEEDED",
        "07_EXPORTS_FOR_EDIT",
    ]
    for folder in folders:
        assert folder in text
    assert "must not move, rename, delete, or modify files" in text


def test_editorial_and_postproduction_notes_are_safe():
    text = read_doc()
    required = [
        "camera and sound candidate pair",
        "timecode review",
        "waveform sync in a future phase",
        "assistant editor review",
        "DIT verification",
        "sound department review",
        "must avoid pretending that real sync",
        "real transcription",
        "real metadata extraction",
    ]
    for item in required:
        assert item in text


def test_demo_limitations_are_explicit():
    text = read_doc()
    limitations = [
        "this is a synthetic demo",
        "no actual client media was analyzed",
        "no real technical metadata was extracted",
        "no waveform sync was performed",
        "no timecode sync was performed",
        "no slate detection was performed",
        "no transcription was performed",
        "no translation was performed",
        "no DaVinci Resolve timeline was exported",
        "no production decision should be made from the synthetic report alone",
    ]
    for limitation in limitations:
        assert limitation in text


def test_future_implementation_constraints_are_safe():
    text = read_doc()
    constraints = [
        "local-only",
        "deterministic",
        "safe-label based",
        "fixture-driven",
        "free from real media reads",
        "free from external binary execution",
        "free from cloud calls",
        "free from database writes",
        "free from SaaS runtime coupling",
        "suitable for unit tests",
        "suitable for stakeholder demo screenshots",
    ]
    for constraint in constraints:
        assert constraint in text


def test_acceptance_criteria_are_complete():
    text = read_doc()
    criteria = [
        "phase remains documentation/test-only",
        "only this document and its unit test are changed",
        "no scanner runtime file is modified",
        "no SaaS runtime file is modified",
        "no external command execution is introduced",
        "no real media processing is introduced",
        "no installer logic is introduced",
        "no licensing or activation logic is introduced",
        "report sections are fully defined",
        "privacy statements are explicit",
        "synthetic metadata fields are complete",
        "warning vocabulary is complete",
        "limitations are explicit",
        "next phase remains gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_next_phase_and_path_are_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1" in text
    path = [
        "synthetic demo report contract QA",
        "synthetic demo report fixture contract",
        "synthetic demo report generator implementation readiness gate",
        "synthetic demo report generator minimal implementation",
        "synthetic demo report QA",
        "stakeholder-readable demo report package",
    ]
    for item in path:
        assert item in text


def test_final_contract_decision_is_clear():
    text = read_doc()
    assert "SYNTHETIC_END_TO_END_LOCAL_DEMO_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "does not authorize implementation" in text


def test_test_file_does_not_import_external_command_modules():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "o" + "s",
        "from " + "o" + "s",
        "P" + "open(",
        "shell" + "=",
    ]
    for item in forbidden:
        assert item not in source
