from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_schema_contract_v1.md"
)

PREVIOUS_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_contract_qa_gate_v1.md"
)

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_schema_contract_document_exists():
    assert DOC.exists()


def test_referenced_documents_exist():
    assert PREVIOUS_QA_GATE_DOC.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Schema Contract v1" in text


def test_schema_contract_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "leaves actual fixture data creation for a later gated phase",
        "leaves loader code for a later gated phase",
        "leaves report generation code for a later gated phase",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not execute external commands",
        "does not scan folders",
        "does not read video files",
        "does not read audio files",
        "does not modify scanner runtime",
        "does not modify SaaS runtime",
        "does not create installer behavior",
        "does not create licensing or activation behavior",
    ]
    for item in required:
        assert item in text


def test_baseline_and_previous_gate_are_recorded():
    text = read_doc()
    assert "4f0a378" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_schema_identity_values_are_fixed():
    text = read_doc()
    values = [
        "cid_local_media_agent_synthetic_demo_report_fixture_schema_v1",
        "SYNTHETIC_LOCAL_DEMO_001",
        "v1",
        "synthetic_end_to_end_local_demo_report",
        "synthetic_safe_labels_only",
        "synthetic_contract",
        "CID Local Media Agent",
        "CID — Cinematic Intelligence Direction",
    ]
    for value in values:
        assert value in text


def test_root_object_required_fields_are_declared():
    text = read_doc()
    root_fields = [
        "schema_version",
        "fixture_id",
        "fixture_version",
        "fixture_kind",
        "privacy_level",
        "source_mode",
        "created_for_product",
        "created_for_ecosystem",
        "local_input_label",
        "local_output_label",
        "cloud_upload",
        "external_binary_execution",
        "client_material_used",
        "human_review_required",
        "limitations",
        "items",
        "project_summary",
        "suggested_folders",
        "privacy_assertions",
        "validation_rules",
        "next_recommended_phase",
    ]
    for field in root_fields:
        assert field in text
    assert "No extra root field should be allowed" in text


def test_root_field_types_are_declared():
    text = read_doc()
    type_lines = [
        "`schema_version`: string",
        "`fixture_id`: string",
        "`cloud_upload`: boolean",
        "`external_binary_execution`: boolean",
        "`client_material_used`: boolean",
        "`human_review_required`: boolean",
        "`limitations`: array of strings",
        "`items`: array of objects",
        "`project_summary`: object",
        "`suggested_folders`: array of strings",
        "`privacy_assertions`: object",
        "`validation_rules`: object",
    ]
    for line in type_lines:
        assert line in text


def test_required_root_values_are_declared():
    text = read_doc()
    values = [
        "`local_input_label`: `LOCAL_PROJECT_INPUT_SYNTHETIC`",
        "`local_output_label`: `LOCAL_PROJECT_OUTPUT_SYNTHETIC_REPORTS`",
        "`cloud_upload`: `false`",
        "`external_binary_execution`: `false`",
        "`client_material_used`: `false`",
        "`human_review_required`: `true`",
        "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1",
    ]
    for value in values:
        assert value in text


def test_items_array_rules_are_fixed():
    text = read_doc()
    assert "must contain exactly 10 objects" in text
    ids = [
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
    for item_id in ids:
        assert item_id in text
    assert "No duplicate `safe_item_id` is allowed" in text
    assert "No item may use a raw filename" in text
    assert "No item may use a private folder path" in text


def test_item_required_fields_are_declared():
    text = read_doc()
    item_fields = [
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
        "report_notes",
    ]
    for field in item_fields:
        assert field in text
    assert "No extra item field should be allowed" in text


def test_item_field_types_are_declared():
    text = read_doc()
    item_types = [
        "`safe_item_id`: string",
        "`safe_display_label`: string",
        "`category`: string",
        "`container_hint`: string or null",
        "`codec_hint`: string or null",
        "`duration_hint`: string or null",
        "`frame_rate_hint`: string or null",
        "`resolution_hint`: string or null",
        "`audio_channels_hint`: string or null",
        "`sample_rate_hint`: string or null",
        "`timecode_hint`: string or null",
        "`camera_or_recorder_hint`: string or null",
        "`human_review_required`: boolean",
        "`warning_codes`: array of strings",
        "`recommended_department_review`: array of strings",
        "`report_notes`: array of strings",
    ]
    for item in item_types:
        assert item in text


def test_allowed_categories_and_distribution_are_declared():
    text = read_doc()
    categories = [
        "`video`",
        "`audio`",
        "`still_image`",
        "`production_document`",
        "`ignored_non_media`",
        "`video`: 4 items",
        "`audio`: 3 items",
        "`still_image`: 1 item",
        "`production_document`: 1 item",
        "`ignored_non_media`: 1 item",
    ]
    for category in categories:
        assert category in text


def test_allowed_synthetic_groups_are_declared():
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
    assert "`SYNC_GROUP_SYNTHETIC_A`: at least 2 items" in text
    assert "`SYNC_GROUP_SYNTHETIC_B`: at least 2 items" in text


def test_warning_codes_and_required_coverage_are_declared():
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
        "READY_FOR_SUBTITLE_REVIEW",
        "UNSUPPORTED_CONTAINER_HINT",
        "NO_WARNINGS",
    ]
    for warning in warnings:
        assert warning in text
    assert "at least one item must include `MISSING_TIMECODE`" in text
    assert "at least one item must include `UNSUPPORTED_CONTAINER_HINT`" in text


def test_department_review_values_and_coverage_are_declared():
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
    assert "at least one item must include `EDITORIAL_REVIEW`" in text
    assert "at least one item must include `IGNORE_OR_ARCHIVE_REVIEW`" in text


def test_project_summary_shape_and_values_are_declared():
    text = read_doc()
    summary_fields = [
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
    for field in summary_fields:
        assert field in text
    expected_values = [
        "`total_items`: 10",
        "`video_like_count`: 4",
        "`audio_like_count`: 3",
        "`still_like_count`: 1",
        "`document_like_count`: 1",
        "`ignored_or_unsupported_count`: 1",
        "`sync_candidate_group_count`: 6",
        "`privacy_mode`: `synthetic_safe_labels_only`",
        "`demo_mode`: `synthetic_end_to_end_local_demo`",
        "`limitations_label`: `synthetic_demo_not_real_media_analysis`",
    ]
    for value in expected_values:
        assert value in text


def test_suggested_folders_are_exactly_declared():
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
    assert "must include exactly" in text


def test_privacy_assertions_are_declared():
    text = read_doc()
    privacy_fields = [
        "uses_synthetic_labels_only",
        "contains_real_client_media",
        "contains_private_paths",
        "contains_raw_filenames",
        "contains_client_names",
        "contains_person_names",
        "contains_real_locations",
        "contains_script_content",
        "contains_dialogue_content",
        "contains_transcription_content",
        "requires_cloud_upload",
        "requires_external_binary_execution",
        "safe_for_public_demo_after_human_review",
    ]
    for field in privacy_fields:
        assert field in text
    expected_values = [
        "`uses_synthetic_labels_only`: `true`",
        "`contains_real_client_media`: `false`",
        "`contains_private_paths`: `false`",
        "`contains_raw_filenames`: `false`",
        "`contains_script_content`: `false`",
        "`contains_dialogue_content`: `false`",
        "`contains_transcription_content`: `false`",
        "`requires_cloud_upload`: `false`",
        "`requires_external_binary_execution`: `false`",
        "`safe_for_public_demo_after_human_review`: `false`",
    ]
    for value in expected_values:
        assert value in text


def test_validation_rules_are_declared():
    text = read_doc()
    rules = [
        "exact_item_count_required",
        "unique_safe_item_ids_required",
        "allowed_categories_only",
        "allowed_warning_codes_only",
        "allowed_department_reviews_only",
        "private_paths_rejected",
        "raw_filenames_rejected",
        "real_names_rejected",
        "script_content_rejected",
        "dialogue_content_rejected",
        "transcription_content_rejected",
        "cloud_upload_rejected",
        "external_binary_execution_rejected",
        "human_review_required",
    ]
    for rule in rules:
        assert rule in text
    assert "`exact_item_count_required`: `true`" in text
    assert "`human_review_required`: `true`" in text


def test_limitations_and_future_path_are_declared():
    text = read_doc()
    limitations = [
        "synthetic demo data",
        "no real media analysis",
        "no completed synchronization",
        "no completed transcription",
        "no completed subtitle translation",
        "no completed DaVinci export",
        "human review required",
        "local-first privacy promise",
        "future implementation required",
        "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json",
        "does not create that file",
    ]
    for item in limitations:
        assert item in text


def test_rejection_rules_are_declared():
    text = read_doc()
    rejection_rules = [
        "root required fields are missing",
        "item required fields are missing",
        "item count is not exactly 10",
        "safe item identifiers are duplicated",
        "unknown categories appear",
        "unknown warning codes appear",
        "unknown department review values appear",
        "private paths appear",
        "raw filenames appear",
        "real locations appear",
        "story or script content appears",
        "dialogue content appears",
        "transcription content appears",
        "media upload is required",
        "external binary execution is required",
        "human review is disabled",
        "public demo safety is marked true before human review",
    ]
    for rule in rejection_rules:
        assert rule in text


def test_non_goals_are_explicit():
    text = read_doc()
    non_goals = [
        "fixture JSON creation",
        "fixture loader creation",
        "report generation",
        "runtime code",
        "scanner changes",
        "ffprobe execution",
        "ffmpeg execution",
        "transcription",
        "subtitle translation",
        "DaVinci export",
        "SaaS integration",
        "installer creation",
        "license server integration",
        "payment integration",
        "client media processing",
    ]
    for item in non_goals:
        assert item in text


def test_acceptance_criteria_are_complete():
    text = read_doc()
    criteria = [
        "root schema is defined",
        "item schema is defined",
        "exact item count is defined",
        "safe item identifiers are fixed",
        "allowed categories are constrained",
        "category distribution is defined",
        "allowed synthetic groups are constrained",
        "warning codes are constrained",
        "warning coverage is defined",
        "department review values are constrained",
        "project summary shape is defined",
        "suggested folders are defined",
        "privacy assertions are defined",
        "validation rules are defined",
        "rejection rules are defined",
        "non-goals are explicit",
        "next phase remains gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_next_phase_and_final_decision_are_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.QA.GATE.V1" in text
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_QA" in text
    assert "authorizes only the next documentation/test-only QA gate" in text
    assert "does not authorize fixture JSON creation" in text
    assert "does not authorize a loader" in text
    assert "does not authorize report generation" in text
    assert "does not authorize runtime changes" in text


def test_previous_gate_contains_schema_authorization_result():
    previous = PREVIOUS_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT" in previous
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1" in previous


def test_blueprint_confirms_product_context():
    blueprint = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in blueprint
    assert "must not depend on CID SaaS to work" in blueprint
    assert "must not upload customer video or audio by default" in blueprint


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
