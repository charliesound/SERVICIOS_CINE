from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_contract_v1.md"
)

QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_contract_qa_gate_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_fixture_contract_document_exists():
    assert DOC.exists()


def test_referenced_qa_gate_exists():
    assert QA_GATE_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Contract v1" in text


def test_contract_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not produce report artifacts",
        "does not implement a fixture loader",
        "does not implement a report generator",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not execute external commands",
        "does not scan client folders",
        "does not read video files",
        "does not read audio files",
        "does not modify scanner runtime",
        "does not modify SaaS runtime",
        "does not create installer behavior",
        "does not create licensing or activation behavior",
    ]
    for item in required:
        assert item in text


def test_audited_baseline_and_previous_gate_are_recorded():
    text = read_doc()
    assert "2556383" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_CONTRACT_READY_FOR_FIXTURE_CONTRACT" in text


def test_fixture_purpose_is_visible_and_stakeholder_ready():
    text = read_doc()
    required = [
        "believable audiovisual project data",
        "without exposing or implying any actual client material",
        "local input label",
        "safe media-like inventory",
        "synthetic technical hints",
        "warning codes",
        "camera and audio grouping hints",
        "editorial preparation notes",
        "postproduction preparation notes",
        "suggested folder organization",
        "human review requirements",
        "demo limitations",
        "local-only privacy confirmations",
        "stakeholder-readable demo",
    ]
    for item in required:
        assert item in text


def test_fixture_identity_is_complete():
    text = read_doc()
    fields = [
        "SYNTHETIC_LOCAL_DEMO_001",
        "fixture_version",
        "fixture_kind",
        "synthetic_end_to_end_local_demo_report",
        "synthetic_safe_labels_only",
        "LOCAL_PROJECT_INPUT_SYNTHETIC",
        "LOCAL_PROJECT_OUTPUT_SYNTHETIC_REPORTS",
        "cloud_upload",
        "external_binary_execution",
        "client_material_used",
        "human_review_required",
    ]
    for field in fields:
        assert field in text


def test_forbidden_fixture_content_is_complete():
    text = read_doc()
    forbidden_items = [
        "actual project titles",
        "actual client names",
        "actual personal names",
        "actual company names",
        "private folder paths",
        "raw camera card names from a client",
        "raw sound card names from a client",
        "actual shooting locations",
        "actual script content",
        "actual dialogue",
        "actual audio transcription",
        "actual filenames from production",
        "actual technical metadata extracted from files",
        "GPS data",
        "email addresses",
        "phone numbers",
        "payment data",
        "license keys",
        "secrets",
        "credentials",
    ]
    for item in forbidden_items:
        assert item in text


def test_required_item_count_is_defined():
    text = read_doc()
    assert "exactly 10 synthetic inventory items" in text
    counts = [
        "4 video-like items",
        "3 audio-like items",
        "1 still-image-like item",
        "1 production-document-like item",
        "1 ignored or unsupported item",
    ]
    for item in counts:
        assert item in text


def test_required_safe_item_identifiers_are_complete():
    text = read_doc()
    identifiers = [
        "CAM_A_SYNTHETIC_CLIP_001",
        "CAM_A_SYNTHETIC_CLIP_002",
        "CAM_B_SYNTHETIC_CLIP_001",
        "CAM_B_SYNTHETIC_CLIP_002",
        "AUDIO_SYNTHETIC_TAKE_001",
        "AUDIO_SYNTHETIC_TAKE_002",
        "AUDIO_SYNTHETIC_ROOMTONE_001",
        "STILLS_SYNTHETIC_REFERENCE_001",
        "DOC_SYNTHETIC_NOTES_001",
        "UNSUPPORTED_SYNTHETIC_ITEM_001",
    ]
    for identifier in identifiers:
        assert identifier in text
    assert "These identifiers are not filenames" in text


def test_required_item_fields_are_complete():
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
        "recommended_department_review",
    ]
    for field in fields:
        assert field in text


def test_required_categories_are_defined():
    text = read_doc()
    categories = [
        "video",
        "audio",
        "still_image",
        "production_document",
        "ignored_non_media",
    ]
    for category in categories:
        assert category in text


def test_required_groups_are_defined_without_sync_claim():
    text = read_doc()
    groups = [
        "SYNC_GROUP_SYNTHETIC_A",
        "SYNC_GROUP_SYNTHETIC_B",
        "ROOMTONE_GROUP_SYNTHETIC",
        "REFERENCE_GROUP_SYNTHETIC",
        "DOCUMENTATION_GROUP_SYNTHETIC",
        "UNSUPPORTED_GROUP_SYNTHETIC",
    ]
    for group in groups:
        assert group in text
    assert "must not claim that synchronization has been performed" in text


def test_required_warning_distribution_is_defined():
    text = read_doc()
    warnings = [
        "MISSING_TIMECODE",
        "POSSIBLE_DOUBLE_SYSTEM_SOUND",
        "FRAME_RATE_MISMATCH",
        "SAMPLE_RATE_MISMATCH",
        "NEEDS_HUMAN_REVIEW",
        "READY_FOR_EDITOR_REVIEW",
        "READY_FOR_DIT_REVIEW",
        "READY_FOR_SOUND_REVIEW",
        "UNSUPPORTED_CONTAINER_HINT",
    ]
    for warning in warnings:
        assert warning in text
    assert "Warnings are not confirmed errors" in text


def test_department_review_values_are_defined():
    text = read_doc()
    values = [
        "EDITORIAL_REVIEW",
        "ASSISTANT_EDITOR_REVIEW",
        "DIT_REVIEW",
        "SOUND_REVIEW",
        "SUBTITLE_REVIEW",
        "PRODUCTION_REVIEW",
        "IGNORE_OR_ARCHIVE_REVIEW",
    ]
    for value in values:
        assert value in text


def test_project_summary_fields_are_defined():
    text = read_doc()
    fields = [
        "total_items",
        "video_like_count",
        "audio_like_count",
        "still_like_count",
        "document_like_count",
        "ignored_or_unsupported_count",
        "sync_candidate_group_count",
        "items_requiring_human_review_count",
        "privacy_mode",
        "demo_mode",
        "limitations_label",
    ]
    for field in fields:
        assert field in text


def test_report_ready_notes_are_defined():
    text = read_doc()
    notes = [
        "executive summary note",
        "local-only privacy note",
        "editorial preparation note",
        "postproduction risk note",
        "suggested organization note",
        "subtitle readiness note",
        "DaVinci future export readiness note",
        "limitations note",
        "next recommended actions note",
    ]
    for note in notes:
        assert note in text
    assert "must not include story, script, client, location, or production-specific details" in text


def test_suggested_folders_are_defined_without_mutation():
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
    assert "must not authorize moving, renaming, deleting, copying, or modifying files" in text


def test_privacy_assertions_are_explicit():
    text = read_doc()
    assertions = [
        "no video upload",
        "no audio upload",
        "no client material used",
        "no cloud processing",
        "no external binary execution",
        "no private path exposure",
        "safe labels only",
        "human review required",
    ]
    for assertion in assertions:
        assert assertion in text


def test_future_fixture_file_shape_is_declared_but_not_created():
    text = read_doc()
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "This phase does not create that JSON file" in text


def test_fixture_validation_rules_are_complete():
    text = read_doc()
    rules = [
        "item count is not exactly 10",
        "required safe item identifiers are missing",
        "categories are outside the allowed set",
        "required warning distribution is missing",
        "a private path appears",
        "a raw client-like filename appears",
        "dialogue content appears",
        "transcription content appears",
        "actual project names appear",
        "local-only assertions are missing",
        "human review is not required",
        "claims completed sync",
        "claims completed transcription",
        "claims completed translation",
        "claims completed DaVinci export",
    ]
    for rule in rules:
        assert rule in text


def test_acceptance_criteria_are_complete():
    text = read_doc()
    criteria = [
        "phase remains documentation/test-only",
        "only this document and its unit test are changed",
        "no fixture JSON is created",
        "no reporting generator component is created",
        "no runtime file is modified",
        "no scanner runtime file is modified",
        "no SaaS runtime file is modified",
        "no external command execution is introduced",
        "no client material is included",
        "fixture identity is defined",
        "required item list is complete",
        "required item fields are complete",
        "warning distribution is defined",
        "department review labels are defined",
        "privacy assertions are explicit",
        "validation rules are explicit",
        "next phase remains gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_next_phase_and_path_are_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in text
    path = [
        "fixture contract QA gate",
        "synthetic fixture schema contract",
        "synthetic fixture JSON implementation readiness gate",
        "synthetic fixture JSON minimal implementation",
        "synthetic fixture QA",
        "synthetic demo report generator readiness gate",
    ]
    for item in path:
        assert item in text


def test_final_contract_decision_is_clear():
    text = read_doc()
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_QA" in text
    assert "does not authorize fixture implementation" in text
    assert "does not authorize report generation" in text


def test_previous_qa_gate_authorized_fixture_contract_only():
    qa_text = QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_CONTRACT_READY_FOR_FIXTURE_CONTRACT" in qa_text
    assert "authorizes only the next documentation/test-only fixture contract phase" in qa_text


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
