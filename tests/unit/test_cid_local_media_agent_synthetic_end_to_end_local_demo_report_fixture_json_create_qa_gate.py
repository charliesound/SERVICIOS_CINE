import json
from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_json_create_qa_gate_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

JSON_CREATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_json_create_v1.md"
)

SCHEMA_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_schema_contract_qa_gate_v1.md"
)

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_qa_gate_document_exists():
    assert DOC.exists()


def test_referenced_files_exist():
    assert FIXTURE.exists()
    assert JSON_CREATE_DOC.exists()
    assert SCHEMA_QA_GATE_DOC.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture JSON Create QA Gate v1" in text


def test_qa_gate_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "validates an existing synthetic JSON fixture",
        "keeps fixture loading code blocked",
        "keeps report generation code blocked",
        "keeps runtime code blocked",
        "keeps scanner runtime changes blocked",
        "keeps SaaS integration blocked",
        "keeps ffprobe execution blocked",
        "keeps ffmpeg execution blocked",
        "keeps external command execution blocked",
        "keeps client media processing blocked",
        "keeps installer behavior blocked",
        "keeps licensing or activation behavior blocked",
    ]
    for item in required:
        assert item in text


def test_baseline_and_referenced_decisions_are_recorded():
    text = read_doc()
    assert "87c9f6d" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1" in text
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_CREATED_READY_FOR_QA" in text
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_JSON_CREATE" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_qa_scope_is_complete():
    text = read_doc()
    scope_items = [
        "parses as valid JSON",
        "uses the expected schema version",
        "uses the expected fixture identity",
        "keeps cloud upload disabled",
        "keeps external binary execution disabled",
        "marks client material as absent",
        "keeps human review required",
        "contains exactly 10 items",
        "uses only the expected safe item identifiers",
        "keeps all safe item identifiers unique",
        "follows the expected item schema",
        "has the expected category distribution",
        "has the expected synthetic group coverage",
        "has the expected warning coverage",
        "has the expected department review coverage",
        "has the expected project summary",
        "has the expected suggested folders",
        "has strict privacy assertions",
        "has strict validation rules",
        "contains no private paths",
        "contains no raw media filenames",
        "contains no real names",
        "contains no real locations",
        "contains no script excerpts",
        "contains no dialogue excerpts",
        "contains no transcription excerpts",
        "keeps public demo safety false before human review",
        "points to the next gated phase",
    ]
    for item in scope_items:
        assert item in text


def test_pass_criteria_are_complete():
    text = read_doc()
    criteria = [
        "the fixture parses successfully",
        "root fields match the schema contract",
        "item fields match the schema contract",
        "item count is exactly 10",
        "all expected safe item identifiers are present",
        "safe item identifiers are unique",
        "category distribution is correct",
        "warning coverage is complete",
        "department review coverage is complete",
        "privacy assertions remain strict",
        "validation rules remain strict",
        "limitations are clear",
        "no private paths appear",
        "no raw file extensions appear",
        "no customer-identifying content appears",
        "no story content appears",
        "no spoken-content excerpt appears",
        "no transcription-like excerpt appears",
        "public demo safety remains false pending human review",
        "next phase remains gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_fixture_json_parses_and_is_object():
    data = load_fixture()
    assert isinstance(data, dict)


def test_fixture_root_identity_is_correct():
    data = load_fixture()
    assert data["schema_version"] == "cid_local_media_agent_synthetic_demo_report_fixture_schema_v1"
    assert data["fixture_id"] == "SYNTHETIC_LOCAL_DEMO_001"
    assert data["fixture_version"] == "v1"
    assert data["fixture_kind"] == "synthetic_end_to_end_local_demo_report"
    assert data["privacy_level"] == "synthetic_safe_labels_only"
    assert data["source_mode"] == "synthetic_contract"
    assert data["created_for_product"] == "CID Local Media Agent"


def test_fixture_safety_flags_are_strict():
    data = load_fixture()
    assert data["cloud_upload"] is False
    assert data["external_binary_execution"] is False
    assert data["client_material_used"] is False
    assert data["human_review_required"] is True


def test_fixture_items_are_exact_and_unique():
    data = load_fixture()
    expected_ids = {
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
    items = data["items"]
    ids = [item["safe_item_id"] for item in items]
    assert len(items) == 10
    assert len(ids) == len(set(ids))
    assert set(ids) == expected_ids


def test_fixture_category_distribution_is_correct():
    categories = [item["category"] for item in load_fixture()["items"]]
    assert categories.count("video") == 4
    assert categories.count("audio") == 3
    assert categories.count("still_image") == 1
    assert categories.count("production_document") == 1
    assert categories.count("ignored_non_media") == 1


def test_fixture_warning_and_department_coverage_is_complete():
    items = load_fixture()["items"]
    warnings = {warning for item in items for warning in item["warning_codes"]}
    departments = {
        department
        for item in items
        for department in item["recommended_department_review"]
    }

    assert {
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
    }.issubset(warnings)

    assert {
        "EDITORIAL_REVIEW",
        "ASSISTANT_EDITOR_REVIEW",
        "DIT_REVIEW",
        "SOUND_REVIEW",
        "SUBTITLE_REVIEW",
        "PRODUCTION_REVIEW",
        "IGNORE_OR_ARCHIVE_REVIEW",
    }.issubset(departments)


def test_fixture_project_summary_and_folders_are_correct():
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

    assert data["suggested_folders"] == [
        "01_VIDEO",
        "02_AUDIO",
        "03_STILLS",
        "04_DOCUMENTS",
        "05_REPORTS",
        "06_REVIEW_NEEDED",
        "07_EXPORTS_FOR_EDIT",
    ]


def test_fixture_privacy_assertions_are_strict():
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


def test_fixture_validation_rules_are_all_true():
    rules = load_fixture()["validation_rules"]
    assert rules
    assert all(value is True for value in rules.values())


def test_fixture_next_phase_is_qa_gate_result():
    assert (
        load_fixture()["next_recommended_phase"]
        == "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1"
    )


def test_fixture_text_has_no_private_or_raw_path_markers():
    text = FIXTURE.read_text(encoding="utf-8")
    forbidden = [
        "C:" + "\\",
        "/" + "mnt" + "/c",
        "\\\\" + "wsl.localhost",
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
    for marker in forbidden:
        assert marker not in text


def test_fixture_text_has_no_story_or_identity_markers():
    text = FIXTURE.read_text(encoding="utf-8").lower()
    forbidden = [
        "dialogue" + " excerpt",
        "transcription" + " excerpt",
        "script" + " excerpt",
        "real" + " location",
        "client" + " name",
        "person" + " name",
        "production" + " title",
        "project" + " title",
    ]
    for marker in forbidden:
        assert marker not in text


def test_reviewed_fixture_strengths_are_declared():
    text = read_doc()
    strengths = [
        "first concrete synthetic data artifact",
        "controlled synthetic project inventory",
        "product-facing demo reports",
        "editorial review explanation",
        "assistant editor review explanation",
        "DIT review explanation",
        "sound review explanation",
        "subtitle review explanation",
        "production review explanation",
        "archive/ignore review explanation",
        "real client media",
    ]
    for item in strengths:
        assert item in text


def test_product_fit_and_privacy_posture_are_declared():
    text = read_doc()
    required = [
        "standalone CID Local Media Agent product direction",
        "stakeholder-readable local report",
        "synthetic demo data",
        "not be presented as real media analysis",
        "synthetic safe labels",
        "avoids private paths",
        "avoids raw filenames",
        "avoids client names",
        "avoids person names",
        "avoids real locations",
        "avoids script content",
        "avoids dialogue content",
        "avoids transcription content",
        "keeps cloud upload false",
        "keeps external binary execution false",
        "keeps public demo safety false",
    ]
    for item in required:
        assert item in text


def test_implementation_boundary_is_blocked():
    text = read_doc()
    blocked = [
        "fixture loader",
        "report generator",
        "report renderer",
        "runtime code",
        "scanner changes",
        "SaaS integration",
        "ffprobe execution",
        "ffmpeg execution",
        "transcription",
        "subtitle translation",
        "DaVinci export",
        "installer creation",
        "license server integration",
        "payment integration",
        "client media processing",
    ]
    for item in blocked:
        assert item in text


def test_gate_result_and_next_phase_are_declared():
    text = read_doc()
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "authorizes only the next documentation/test-only visible report contract phase" in text
    assert "keeps loader implementation blocked" in text
    assert "keeps report generation implementation blocked" in text
    assert "keeps runtime changes blocked" in text


def test_json_create_doc_contains_original_result():
    text = JSON_CREATE_DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_CREATED_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1" in text


def test_schema_qa_gate_contains_authorization_result():
    text = SCHEMA_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_JSON_CREATE" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1" in text


def test_blueprint_confirms_standalone_context():
    text = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in text
    assert "must not depend on CID SaaS to work" in text
    assert "must not upload customer video or audio by default" in text


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
