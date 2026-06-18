import json
from pathlib import Path


FIXTURE = Path(
    "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json"
)

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_json_create_v1.md"
)

SCHEMA_CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_schema_contract_v1.md"
)

SCHEMA_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_schema_contract_qa_gate_v1.md"
)


EXPECTED_ROOT_KEYS = {
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
}

EXPECTED_ITEM_KEYS = {
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
}

EXPECTED_IDS = {
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
}

ALLOWED_CATEGORIES = {
    "video",
    "audio",
    "still_image",
    "production_document",
    "ignored_non_media",
}

ALLOWED_GROUPS = {
    "SYNC_GROUP_SYNTHETIC_A",
    "SYNC_GROUP_SYNTHETIC_B",
    "ROOMTONE_GROUP_SYNTHETIC",
    "REFERENCE_GROUP_SYNTHETIC",
    "DOCUMENTATION_GROUP_SYNTHETIC",
    "UNSUPPORTED_GROUP_SYNTHETIC",
}

REQUIRED_WARNINGS = {
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
}

ALLOWED_WARNINGS = REQUIRED_WARNINGS | {"NO_WARNINGS"}

REQUIRED_DEPARTMENTS = {
    "EDITORIAL_REVIEW",
    "ASSISTANT_EDITOR_REVIEW",
    "DIT_REVIEW",
    "SOUND_REVIEW",
    "SUBTITLE_REVIEW",
    "PRODUCTION_REVIEW",
    "IGNORE_OR_ARCHIVE_REVIEW",
}


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_and_documentation_exist():
    assert FIXTURE.exists()
    assert DOC.exists()
    assert SCHEMA_CONTRACT_DOC.exists()
    assert SCHEMA_QA_GATE_DOC.exists()


def test_fixture_is_valid_json_object():
    data = load_fixture()
    assert isinstance(data, dict)


def test_root_keys_are_exact():
    data = load_fixture()
    assert set(data) == EXPECTED_ROOT_KEYS


def test_root_identity_values_match_schema_contract():
    data = load_fixture()
    assert data["schema_version"] == "cid_local_media_agent_synthetic_demo_report_fixture_schema_v1"
    assert data["fixture_id"] == "SYNTHETIC_LOCAL_DEMO_001"
    assert data["fixture_version"] == "v1"
    assert data["fixture_kind"] == "synthetic_end_to_end_local_demo_report"
    assert data["privacy_level"] == "synthetic_safe_labels_only"
    assert data["source_mode"] == "synthetic_contract"
    assert data["created_for_product"] == "CID Local Media Agent"
    assert data["created_for_ecosystem"] == "CID — Cinematic Intelligence Direction"


def test_root_safety_booleans_are_strict():
    data = load_fixture()
    assert data["cloud_upload"] is False
    assert data["external_binary_execution"] is False
    assert data["client_material_used"] is False
    assert data["human_review_required"] is True


def test_items_count_and_ids_are_exact():
    data = load_fixture()
    items = data["items"]
    assert isinstance(items, list)
    assert len(items) == 10
    ids = [item["safe_item_id"] for item in items]
    assert len(ids) == len(set(ids))
    assert set(ids) == EXPECTED_IDS


def test_item_keys_are_exact_and_types_are_safe():
    for item in load_fixture()["items"]:
        assert set(item) == EXPECTED_ITEM_KEYS
        assert isinstance(item["safe_item_id"], str)
        assert isinstance(item["safe_display_label"], str)
        assert isinstance(item["category"], str)
        assert item["category"] in ALLOWED_CATEGORIES
        assert isinstance(item["human_review_required"], bool)
        assert item["human_review_required"] is True
        assert isinstance(item["warning_codes"], list)
        assert isinstance(item["recommended_department_review"], list)
        assert isinstance(item["report_notes"], list)
        assert all(isinstance(note, str) for note in item["report_notes"])


def test_category_distribution_matches_contract():
    items = load_fixture()["items"]
    counts = {category: 0 for category in ALLOWED_CATEGORIES}
    for item in items:
        counts[item["category"]] += 1

    assert counts["video"] == 4
    assert counts["audio"] == 3
    assert counts["still_image"] == 1
    assert counts["production_document"] == 1
    assert counts["ignored_non_media"] == 1


def test_sync_groups_are_allowed_and_have_required_coverage():
    groups = [item["sync_candidate_group"] for item in load_fixture()["items"]]
    assert set(groups).issubset(ALLOWED_GROUPS)
    for group in ALLOWED_GROUPS:
        assert group in groups
    assert groups.count("SYNC_GROUP_SYNTHETIC_A") >= 2
    assert groups.count("SYNC_GROUP_SYNTHETIC_B") >= 2


def test_warning_codes_are_allowed_and_cover_required_values():
    seen = set()
    for item in load_fixture()["items"]:
        for warning in item["warning_codes"]:
            assert warning in ALLOWED_WARNINGS
            seen.add(warning)
    assert REQUIRED_WARNINGS.issubset(seen)


def test_department_reviews_are_allowed_and_cover_required_values():
    seen = set()
    for item in load_fixture()["items"]:
        for department in item["recommended_department_review"]:
            assert department in REQUIRED_DEPARTMENTS
            seen.add(department)
    assert REQUIRED_DEPARTMENTS.issubset(seen)


def test_project_summary_matches_fixture_counts():
    data = load_fixture()
    summary = data["project_summary"]
    assert summary["total_items"] == 10
    assert summary["video_like_count"] == 4
    assert summary["audio_like_count"] == 3
    assert summary["still_like_count"] == 1
    assert summary["document_like_count"] == 1
    assert summary["ignored_or_unsupported_count"] == 1
    assert summary["sync_candidate_group_count"] == 6
    assert summary["items_requiring_human_review_count"] == 10
    assert summary["privacy_mode"] == "synthetic_safe_labels_only"
    assert summary["demo_mode"] == "synthetic_end_to_end_local_demo"
    assert summary["limitations_label"] == "synthetic_demo_not_real_media_analysis"


def test_suggested_folders_are_exact():
    assert load_fixture()["suggested_folders"] == [
        "01_VIDEO",
        "02_AUDIO",
        "03_STILLS",
        "04_DOCUMENTS",
        "05_REPORTS",
        "06_REVIEW_NEEDED",
        "07_EXPORTS_FOR_EDIT",
    ]


def test_privacy_assertions_are_strict():
    privacy = load_fixture()["privacy_assertions"]
    assert privacy["uses_synthetic_labels_only"] is True
    assert privacy["contains_real_client_media"] is False
    assert privacy["contains_private_paths"] is False
    assert privacy["contains_raw_filenames"] is False
    assert privacy["contains_client_names"] is False
    assert privacy["contains_person_names"] is False
    assert privacy["contains_real_locations"] is False
    assert privacy["contains_script_content"] is False
    assert privacy["contains_dialogue_content"] is False
    assert privacy["contains_transcription_content"] is False
    assert privacy["requires_cloud_upload"] is False
    assert privacy["requires_external_binary_execution"] is False
    assert privacy["safe_for_public_demo_after_human_review"] is False


def test_validation_rules_are_strict():
    rules = load_fixture()["validation_rules"]
    assert set(rules) == {
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
    }
    assert all(value is True for value in rules.values())


def test_limitations_are_clear_and_do_not_claim_runtime():
    limitations = "\n".join(load_fixture()["limitations"])
    required = [
        "Synthetic demo data only.",
        "No real media analysis has been performed.",
        "Synchronization has not been completed.",
        "Transcription has not been completed.",
        "Subtitle translation has not been completed.",
        "DaVinci export has not been completed.",
        "Human review is required before public-facing use.",
        "The local-first privacy promise remains active.",
        "Future implementation is required before runtime use.",
    ]
    for item in required:
        assert item in limitations


def test_next_recommended_phase_is_qa_gate():
    assert (
        load_fixture()["next_recommended_phase"]
        == "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1"
    )


def test_fixture_contains_no_private_paths_or_raw_filenames():
    text = FIXTURE.read_text(encoding="utf-8")
    forbidden_fragments = [
        "C:" + "\\",
        "/" + "mnt" + "/c",
        "\\" + "\\" + "wsl.localhost",
        "/" + "home" + "/",
        "/" + "Users" + "/",
        "." + "mov",
        "." + "mxf",
        "." + "wav",
        "." + "mp4",
        "." + "mp3",
        "." + "pdf",
        "." + "jpg",
        "." + "jpeg",
        "." + "png",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in text


def test_fixture_contains_no_real_content_markers():
    text = FIXTURE.read_text(encoding="utf-8").lower()
    forbidden_words = [
        "dialogue" + " excerpt",
        "transcription" + " excerpt",
        "script" + " excerpt",
        "real" + " location",
        "client" + " name",
        "person" + " name",
        "production" + " title",
        "project" + " title",
    ]
    for word in forbidden_words:
        assert word not in text


def test_document_records_creation_without_runtime_authorization():
    text = DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_CREATED_READY_FOR_QA" in text
    assert "does not authorize loader implementation" in text
    assert "does not authorize report generation" in text
    assert "does not authorize runtime changes" in text
    assert "fixture loader" in text
    assert "report generator" in text
    assert "client media processing" in text


def test_schema_qa_gate_authorized_json_create():
    text = SCHEMA_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_JSON_CREATE" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1" in text


def test_schema_contract_declares_fixture_path():
    text = SCHEMA_CONTRACT_DOC.read_text(encoding="utf-8")
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text


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
