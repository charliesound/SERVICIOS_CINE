from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_contract_qa_gate_v1.md"
)

FIXTURE_CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_contract_v1.md"
)

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_qa_gate_document_exists():
    assert DOC.exists()


def test_referenced_documents_exist():
    assert FIXTURE_CONTRACT_DOC.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Contract QA Gate v1" in text


def test_qa_gate_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not create fixture JSON",
        "does not create a fixture loader",
        "does not create a reporting generator component",
        "does not produce report artifacts",
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


def test_baseline_and_referenced_decisions_are_recorded():
    text = read_doc()
    assert "580eed8" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1" in text
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text
    assert "CID_LOCAL_MEDIA_AGENT_STANDALONE_PRODUCT_BLUEPRINT_READY_FOR_QA" in text


def test_qa_scope_is_complete():
    text = read_doc()
    scope_items = [
        "remains documentation/test-only",
        "defines a safe synthetic fixture identity",
        "defines exactly 10 synthetic inventory items",
        "defines all required safe item identifiers",
        "defines item fields needed for a future visible report",
        "defines allowed categories",
        "defines synthetic grouping hints",
        "defines warning distribution",
        "defines department review labels",
        "defines project summary fields",
        "defines report-ready narrative notes",
        "defines suggested local folder organization",
        "defines privacy assertions",
        "defines validation rules",
        "avoids client material",
        "avoids private paths",
        "avoids raw filenames",
        "avoids story or script content",
        "avoids dialogue content",
        "avoids transcription content",
        "keeps fixture implementation gated",
    ]
    for item in scope_items:
        assert item in text


def test_pass_criteria_are_complete():
    text = read_doc()
    criteria = [
        "no fixture JSON is authorized in this phase",
        "no report generation is authorized in this phase",
        "no runtime change is authorized",
        "no scanner runtime change is authorized",
        "no SaaS runtime change is authorized",
        "no external binary execution is authorized",
        "client material remains absent",
        "synthetic safe labels are mandatory",
        "fixture identity is complete",
        "item count is fixed at exactly 10",
        "all required item identifiers are present",
        "item fields are complete",
        "categories are constrained",
        "synthetic groups are constrained",
        "warning distribution is defined",
        "department review values are defined",
        "privacy assertions are explicit",
        "validation rules are explicit",
        "human review remains required",
        "next phase is gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_reviewed_strengths_are_product_relevant():
    text = read_doc()
    strengths = [
        "concrete data shape",
        "synthetic audiovisual material",
        "camera-like",
        "audio-like",
        "still-image-like",
        "document-like",
        "unsupported items",
        "warning codes that matter to postproduction",
        "department review labels",
        "local-first product promise",
    ]
    for item in strengths:
        assert item in text


def test_product_fit_is_clear():
    text = read_doc()
    values = [
        "standalone product direction",
        "editors",
        "producers",
        "post supervisors",
        "DITs",
        "sound teams",
        "subtitle teams",
        "schools",
        "early commercial contacts",
        "visible product demo",
        "synthetic screenshots",
        "synthetic Markdown report",
        "synthetic HTML report",
        "future product walkthrough",
    ]
    for item in values:
        assert item in text


def test_safety_posture_is_explicit():
    text = read_doc()
    safety_items = [
        "synthetic labels only",
        "no client media",
        "no private folder paths",
        "no raw production filenames",
        "no project title leakage",
        "no client name leakage",
        "no person name leakage",
        "no location leakage",
        "no script content",
        "no dialogue content",
        "no transcription content",
        "no secrets",
        "no credentials",
        "no upload requirement",
        "no external binary execution",
    ]
    for item in safety_items:
        assert item in text


def test_reviewed_fixture_shape_is_complete():
    text = read_doc()
    shape_items = [
        "fixture identity",
        "item count",
        "item identifiers",
        "item fields",
        "allowed categories",
        "synthetic review groups",
        "warning distribution",
        "department review values",
        "project summary fields",
        "narrative notes",
        "suggested folders",
        "privacy assertions",
        "future JSON file shape",
        "validation rules",
        "acceptance criteria",
        "next gated phase",
    ]
    for item in shape_items:
        assert item in text


def test_reservations_are_controlled_and_non_blocking():
    text = read_doc()
    reservations = [
        "no blocking QA concerns",
        "controlled reservations",
        "future schema must keep the exact item count",
        "future schema must reject unexpected categories",
        "future schema must reject unsafe paths",
        "future schema must reject raw filenames",
        "future JSON must remain synthetic",
        "future JSON must not include realistic client titles",
        "future JSON must not include real locations",
        "future JSON must not imply completed sync",
        "future JSON must not imply completed transcription",
        "future JSON must not imply completed DaVinci export",
        "future generator must display limitations clearly",
        "do not block proceeding",
    ]
    for item in reservations:
        assert item in text


def test_decision_matrix_is_declared():
    text = read_doc()
    for label in ["PASS", "LIMITED PASS", "FAIL"]:
        assert label in text
    fail_items = [
        "permits client material",
        "permits private paths",
        "permits raw filenames",
        "permits story or script content",
        "permits dialogue or transcription content",
        "permits report generation now",
        "permits runtime changes",
        "permits scanner changes",
        "permits SaaS coupling",
        "skips human review",
    ]
    for item in fail_items:
        assert item in text


def test_gate_result_allows_schema_contract_only():
    text = read_doc()
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT" in text
    assert "authorizes only the next documentation/test-only schema contract phase" in text
    assert "does not authorize fixture JSON creation" in text
    assert "does not authorize report generation" in text
    assert "does not authorize runtime changes" in text
    assert "does not authorize scanner changes" in text
    assert "does not authorize SaaS integration" in text


def test_next_phase_is_schema_contract():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1" in text
    assert "exact JSON schema contract for the synthetic fixture" in text
    assert "must not create the JSON fixture yet" in text
    assert "must not create a loader" in text
    assert "must not create a report generator" in text


def test_previous_fixture_contract_contains_original_decision():
    fixture_text = FIXTURE_CONTRACT_DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_QA" in fixture_text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in fixture_text


def test_blueprint_confirms_standalone_direction():
    blueprint_text = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in blueprint_text
    assert "must not depend on CID SaaS to work" in blueprint_text
    assert "must not upload customer video or audio by default" in blueprint_text


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
