from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_schema_contract_qa_gate_v1.md"
)

SCHEMA_CONTRACT_DOC = Path(
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


def test_qa_gate_document_exists():
    assert DOC.exists()


def test_referenced_documents_exist():
    assert SCHEMA_CONTRACT_DOC.exists()
    assert PREVIOUS_QA_GATE_DOC.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.QA.GATE.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Fixture Schema Contract QA Gate v1" in text


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


def test_baseline_and_referenced_decisions_are_recorded():
    text = read_doc()
    assert "c507f3a" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1" in text
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_qa_scope_is_complete():
    text = read_doc()
    scope_items = [
        "remains documentation/test-only",
        "defines the root JSON object",
        "defines required root fields",
        "defines root field types",
        "defines exact root values",
        "defines the items array rules",
        "fixes the item count at exactly 10",
        "fixes all safe item identifiers",
        "defines item required fields",
        "defines item field types",
        "constrains allowed categories",
        "defines category distribution",
        "constrains synthetic groups",
        "defines warning codes",
        "defines warning coverage",
        "constrains department review values",
        "defines department review coverage",
        "defines project summary shape",
        "defines suggested folders",
        "defines privacy assertions",
        "defines validation rules",
        "defines limitations",
        "documents future fixture path without creating it",
        "defines rejection rules",
        "keeps future JSON creation gated",
    ]
    for item in scope_items:
        assert item in text


def test_pass_criteria_are_complete():
    text = read_doc()
    criteria = [
        "no fixture JSON is created in this phase",
        "no loader is created in this phase",
        "no report generator is created in this phase",
        "no runtime change is authorized",
        "no scanner runtime change is authorized",
        "no SaaS runtime change is authorized",
        "external binary execution remains unauthorized",
        "root schema is complete",
        "item schema is complete",
        "item count is exactly 10",
        "safe item identifiers are fixed",
        "categories are constrained",
        "warning codes are constrained",
        "department reviews are constrained",
        "privacy assertions are strict",
        "rejection rules are explicit",
        "human review remains required",
        "public demo safety remains false before human review",
        "next phase is gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_reviewed_schema_strengths_are_declared():
    text = read_doc()
    strengths = [
        "precise JSON shape",
        "exact root fields",
        "exact root values",
        "item-level fields",
        "allowed values",
        "coverage requirements",
        "rejection rules",
        "local-first CID Local Media Agent product promise",
        "prevents silent drift",
        "rejecting unsafe or incomplete demo fixture data",
    ]
    for item in strengths:
        assert item in text


def test_standalone_product_fit_is_clear():
    text = read_doc()
    values = [
        "standalone product",
        "local-first media analysis report",
        "editors",
        "assistant editors",
        "DITs",
        "post supervisors",
        "sound teams",
        "subtitle teams",
        "producers",
        "film schools",
        "early trusted commercial contacts",
        "product walkthrough",
        "clearly synthetic",
    ]
    for item in values:
        assert item in text


def test_privacy_posture_is_strict():
    text = read_doc()
    privacy_items = [
        "synthetic safe labels",
        "no private paths",
        "no raw filenames",
        "no client names",
        "no person names",
        "no real locations",
        "no script content",
        "no dialogue content",
        "no transcription content",
        "no cloud upload",
        "no external binary execution",
        "human review before public-facing demo use",
        "`safe_for_public_demo_after_human_review` false",
    ]
    for item in privacy_items:
        assert item in text


def test_future_fixture_readiness_is_documented_without_implementation():
    text = read_doc()
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "This QA gate does not create that file" in text
    assert "This QA gate does not authorize any loader" in text
    assert "This QA gate does not authorize any report renderer" in text
    assert "This QA gate does not authorize runtime behavior" in text


def test_reservations_are_controlled_and_non_blocking():
    text = read_doc()
    reservations = [
        "no blocking QA concerns",
        "controlled reservations",
        "future JSON must match the exact schema",
        "future JSON must include exactly 10 items",
        "future JSON must keep safe item identifiers unique",
        "future JSON must keep all values synthetic",
        "future JSON must reject private paths",
        "future JSON must reject raw filenames",
        "future JSON must reject realistic client titles",
        "future JSON must reject real names",
        "future JSON must reject real locations",
        "future JSON must reject dialogue-like content",
        "future JSON must reject transcription-like content",
        "future JSON must keep cloud upload false",
        "future JSON must keep external binary execution false",
        "future JSON must keep public demo safety false until human review",
        "future loader and generator remain blocked",
        "do not block proceeding",
    ]
    for item in reservations:
        assert item in text


def test_decision_matrix_is_declared():
    text = read_doc()
    for label in ["PASS", "LIMITED PASS", "FAIL"]:
        assert label in text
    fail_items = [
        "schema permits client media",
        "schema permits private paths",
        "schema permits raw filenames",
        "schema allows story content",
        "schema allows script content",
        "schema permits dialogue content",
        "schema permits transcription content",
        "schema permits cloud upload",
        "schema allows external binary execution",
        "schema skips human review",
        "schema permits public demo safety before human review",
        "schema authorizes runtime implementation",
        "schema authorizes scanner changes",
        "schema authorizes SaaS coupling",
    ]
    for item in fail_items:
        assert item in text


def test_gate_result_authorizes_json_create_only():
    text = read_doc()
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_JSON_CREATE" in text
    assert "authorizes only the next gated fixture JSON creation phase" in text
    assert "does not authorize loader implementation" in text
    assert "does not authorize report generation" in text
    assert "does not authorize runtime changes" in text
    assert "does not authorize scanner changes" in text
    assert "does not authorize SaaS integration" in text
    assert "keeps ffprobe execution unauthorized" in text
    assert "keeps ffmpeg execution unauthorized" in text


def test_next_phase_is_json_create():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.V1" in text
    assert "may create the synthetic JSON fixture file" in text
    assert "must remain local-only and synthetic-only" in text
    assert "must not create a loader" in text
    assert "must not create a report generator" in text
    assert "must not process client media" in text
    assert "must not execute external binaries" in text


def test_schema_contract_contains_original_decision():
    schema_text = SCHEMA_CONTRACT_DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_DEMO_REPORT_FIXTURE_SCHEMA_CONTRACT_READY_FOR_QA" in schema_text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.QA.GATE.V1" in schema_text


def test_previous_fixture_qa_gate_contains_schema_authorization():
    previous_text = PREVIOUS_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_CONTRACT_READY_FOR_SCHEMA_CONTRACT" in previous_text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.SCHEMA.CONTRACT.V1" in previous_text


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
