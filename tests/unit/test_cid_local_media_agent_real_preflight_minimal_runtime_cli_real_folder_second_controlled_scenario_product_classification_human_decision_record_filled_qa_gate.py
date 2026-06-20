from pathlib import Path

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_filled_qa_gate_v1.md"
)

FILLED_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_filled_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.RECORD.FILLED.QA.GATE.V1"


def read_qa_doc():
    assert QA_DOC.exists()
    return QA_DOC.read_text(encoding="utf-8")


def read_filled_doc():
    assert FILLED_DOC.exists()
    return FILLED_DOC.read_text(encoding="utf-8")


def test_qa_doc_exists_and_names_phase():
    text = read_qa_doc()
    assert PHASE in text
    assert "Human Decision Record Filled QA Gate v1" in text


def test_qa_gate_depends_on_filled_record_phase():
    text = read_qa_doc()
    assert "HUMAN.DECISION.RECORD.FILLED.V1" in text
    assert "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED" in text


def test_filled_record_exists_and_is_readable():
    text = read_filled_doc()
    assert "Human Decision Record Filled v1" in text
    assert "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED" in text


def test_qa_gate_preserves_required_decision_state():
    qa_text = read_qa_doc()
    filled_text = read_filled_doc()

    for required in [
        "PRODUCT_CLASSIFICATION_DECISION_REQUIRED",
        "PRODUCT_SEMANTICS_SELECTION_DEFERRED",
    ]:
        assert required in qa_text
        assert required in filled_text


def test_qa_gate_result_is_pass_with_decision_deferred():
    text = read_qa_doc()
    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in text
    assert "The filled human decision record is valid." in text
    assert "The product semantics decision remains deferred." in text


def test_no_product_semantics_or_behavior_selected_in_filled_record():
    text = read_filled_doc()
    assert "`selected_product_semantics`: `NONE`" in text
    assert "`selected_product_behavior`: `NONE`" in text


def test_no_client_facing_or_clean_classification_claims():
    qa_text = read_qa_doc()
    filled_text = read_filled_doc()

    for required in [
        "`client_facing_classification_claim`: `NONE`",
        "`clean_classification_pass_claim`: `NONE`",
    ]:
        assert required in qa_text
        assert required in filled_text


def test_runtime_scanner_report_and_cli_changes_remain_unauthorized():
    qa_text = read_qa_doc()
    filled_text = read_filled_doc()

    for required in [
        "`runtime_change_authorized`: `false`",
        "`scanner_change_authorized`: `false`",
        "`report_change_authorized`: `false`",
        "`cli_change_authorized`: `false`",
    ]:
        assert required in qa_text
        assert required in filled_text


def test_observation_counts_are_preserved():
    qa_text = read_qa_doc()
    filled_text = read_filled_doc()

    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in qa_text
        assert required in filled_text


def test_txt_and_exe_remain_rejected_not_ignored():
    text = read_qa_doc()
    assert ".txt` and `.exe` are classified as rejected" in text
    assert ".txt` and `.exe` are not classified as ignored" in text


def test_no_named_product_behavior_is_approved():
    text = read_qa_doc()
    for option in [
        "NON_MEDIA_REJECTED",
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text

    forbidden_approval_claims = [
        "approved: NON_MEDIA_REJECTED",
        "approved: NON_MEDIA_IGNORED",
        "approved: NON_MEDIA_SEPARATE_CATEGORY",
        "approved: NON_MEDIA_POLICY_CONFIGURABLE",
        "approved: OTHER_NAMED_PRODUCT_BEHAVIOR",
        "selected_product_semantics`: `NON_MEDIA_REJECTED",
        "selected_product_semantics`: `NON_MEDIA_IGNORED",
        "selected_product_behavior`: `NON_MEDIA_REJECTED",
        "selected_product_behavior`: `NON_MEDIA_IGNORED",
    ]
    for claim in forbidden_approval_claims:
        assert claim not in text


def test_phase_is_docs_test_only():
    text = read_qa_doc()
    assert "This phase is docs/test-only." in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read_qa_doc()
    for blocked_scope in [
        "scanner execution",
        "ffprobe execution",
        "ffmpeg execution",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "NLE export",
        "SaaS backend changes",
        "SaaS frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits changes",
        "ledger changes",
    ]:
        assert blocked_scope in text


def test_qa_gate_does_not_authorize_behavior_changes_or_client_claims():
    text = read_qa_doc()
    for blocked in [
        "clean classification PASS claims",
        "client-facing claims",
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_gate_result_is_pass_but_only_for_qa_validation():
    text = read_qa_doc()
    assert "`PASS`" in text
    assert "only to a later explicitly authorized product semantics decision phase" in text
