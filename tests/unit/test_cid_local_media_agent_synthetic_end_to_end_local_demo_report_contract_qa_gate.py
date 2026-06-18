from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_contract_qa_gate_v1.md"
)

CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_contract_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_qa_gate_document_exists():
    assert DOC.exists()


def test_referenced_contract_exists():
    assert CONTRACT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Contract QA Gate v1" in text


def test_qa_gate_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not implement the report generator",
        "does not generate reports",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add external command execution",
        "does not scan client media",
        "does not read video files",
        "does not read audio files",
        "does not modify scanner runtime",
        "does not modify SaaS runtime",
        "does not create installer behavior",
        "does not create licensing or activation behavior",
    ]
    for item in required:
        assert item in text


def test_audited_baseline_and_contract_are_recorded():
    text = read_doc()
    assert "b6d0380" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.V1" in text
    assert "SYNTHETIC_END_TO_END_LOCAL_DEMO_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "CONTINUE_BUT_PIVOT_TOWARD_VISIBLE_SYNTHETIC_DEMO" in text


def test_qa_scope_is_complete():
    text = read_doc()
    scope_items = [
        "is still contract-only",
        "defines a visible local demo report",
        "remains synthetic",
        "is understandable by audiovisual professionals",
        "contains privacy statements",
        "avoids client media claims",
        "avoids technical overclaiming",
        "defines JSON, Markdown, and HTML report formats",
        "defines complete report sections",
        "defines synthetic input labels",
        "defines media categories",
        "defines synthetic metadata fields",
        "defines warning vocabulary",
        "defines suggested local organization",
        "includes human review",
        "includes limitations",
        "keeps future implementation gated",
    ]
    for item in scope_items:
        assert item in text


def test_pass_criteria_are_complete():
    text = read_doc()
    criteria = [
        "no runtime implementation is authorized",
        "no report generator is created",
        "no real binary execution is authorized",
        "no client media scan is authorized",
        "no scanner runtime change is authorized",
        "no SaaS runtime change is authorized",
        "no installer work is authorized",
        "no licensing work is authorized",
        "demo audience is clear",
        "commercial message is clear",
        "local-only privacy message is explicit",
        "report structure is complete",
        "synthetic metadata model is complete",
        "warning vocabulary is complete",
        "human review remains required",
        "next phase is gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_reviewed_strengths_are_product_relevant():
    text = read_doc()
    strengths = [
        "visible product direction",
        "production and postproduction people",
        "first visible demo is synthetic",
        "local-only promise",
        "sync, transcription, translation, or DaVinci export",
        "output formats",
        "stakeholder-readable message",
    ]
    for item in strengths:
        assert item in text


def test_product_value_is_clear():
    text = read_doc()
    values = [
        "local project input label",
        "detected media-like items",
        "synthetic technical metadata",
        "warnings",
        "organization suggestions",
        "editorial preparation notes",
        "postproduction preparation notes",
        "local-only privacy confirmation",
        "human review requirements",
        "next recommended actions",
    ]
    for item in values:
        assert item in text


def test_production_language_is_validated():
    text = read_doc()
    assert "analiza una carpeta local de material audiovisual sin subir vídeos ni audios a la nube" in text
    assert "radiografía técnica y editorial" in text
    for role in ["producers", "editors", "assistant editors", "DITs", "sound", "subtitle teams", "post supervisors"]:
        assert role in text


def test_safety_posture_is_explicit():
    text = read_doc()
    safety_items = [
        "synthetic data only",
        "safe labels only",
        "no private absolute paths",
        "no raw client filenames",
        "no cloud upload",
        "no external binary execution",
        "no database writes",
        "no SaaS coupling",
        "no production decisions without human review",
    ]
    for item in safety_items:
        assert item in text


def test_limitations_are_explicit_without_overclaiming():
    text = read_doc()
    limitations = [
        "actual client media analysis",
        "technical metadata extraction from files",
        "waveform sync",
        "timecode sync",
        "slate detection",
        "transcription",
        "translation",
        "DaVinci timeline export",
        "production decision automation",
    ]
    for item in limitations:
        assert item in text


def test_reservations_are_controlled_and_non_blocking():
    text = read_doc()
    reservations = [
        "no blocking QA concerns",
        "controlled reservations",
        "avoid realistic client names",
        "avoid real project titles",
        "avoid private file paths",
        "must not touch scanner runtime",
        "clearly marked as synthetic",
        "must not be sold as a working ffprobe or sync tool",
        "do not block proceeding",
    ]
    for item in reservations:
        assert item in text


def test_decision_matrix_is_declared():
    text = read_doc()
    for label in ["PASS", "LIMITED PASS", "FAIL"]:
        assert label in text
    fail_items = [
        "claims real analysis",
        "authorizes implementation",
        "authorizes binary execution",
        "allows client media use",
        "weakens privacy",
        "skips human review",
        "allows SaaS coupling",
    ]
    for item in fail_items:
        assert item in text


def test_gate_result_allows_only_fixture_contract():
    text = read_doc()
    assert "PASS_SYNTHETIC_DEMO_REPORT_CONTRACT_READY_FOR_FIXTURE_CONTRACT" in text
    assert "authorizes only the next documentation/test-only fixture contract phase" in text
    assert "does not authorize implementation" in text
    assert "does not authorize report generation" in text
    assert "does not authorize real media analysis" in text
    assert "does not authorize external binary execution" in text


def test_next_phase_is_fixture_contract():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1" in text
    assert "synthetic fixture data model" in text
    assert "safe-label based" in text


def test_contract_doc_contains_original_decision():
    contract_text = CONTRACT_DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_END_TO_END_LOCAL_DEMO_REPORT_CONTRACT_READY_FOR_QA" in contract_text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1" in contract_text


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
