from pathlib import Path

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_readiness_gate_v1.md"
)

FILLED_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_filled_qa_gate_v1.md"
)

FILLED_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_filled_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.READINESS.GATE.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_readiness_doc_exists_and_names_phase():
    text = read(READINESS_DOC)
    assert PHASE in text
    assert "Product Semantics Decision Readiness Gate v1" in text


def test_readiness_gate_depends_on_full_prior_chain():
    text = read(READINESS_DOC)
    for required_phase in [
        "OBSERVATION.CLASSIFICATION.QA.GATE.V1",
        "PRODUCT.CLASSIFICATION.DECISION.GATE.V1",
        "HUMAN.DECISION.READINESS.GATE.V1",
        "HUMAN.DECISION.RECORD.TEMPLATE.V1",
        "HUMAN.DECISION.RECORD.TEMPLATE.QA.GATE.V1",
        "HUMAN.DECISION.RECORD.FILL.AUTHORIZATION.GATE.V1",
        "HUMAN.DECISION.RECORD.FILLED.V1",
        "HUMAN.DECISION.RECORD.FILLED.QA.GATE.V1",
    ]:
        assert required_phase in text


def test_prior_filled_docs_exist_and_are_coherent():
    filled_qa_text = read(FILLED_QA_DOC)
    filled_text = read(FILLED_DOC)

    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in filled_qa_text
    assert "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED" in filled_text


def test_required_current_state_is_preserved():
    readiness_text = read(READINESS_DOC)
    filled_qa_text = read(FILLED_QA_DOC)
    filled_text = read(FILLED_DOC)

    for required in [
        "PRODUCT_CLASSIFICATION_DECISION_REQUIRED",
        "PRODUCT_SEMANTICS_SELECTION_DEFERRED",
        "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED",
    ]:
        assert required in readiness_text
        assert required in filled_text or required in filled_qa_text

    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in readiness_text
    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in filled_qa_text


def test_no_product_behavior_is_selected():
    text = read(READINESS_DOC)
    assert "`selected_product_semantics`: `NONE`" in text
    assert "`selected_product_behavior`: `NONE`" in text
    assert "PRODUCT_SEMANTICS_DECISION_READINESS_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in text


def test_no_client_facing_or_clean_classification_claims():
    text = read(READINESS_DOC)
    assert "`client_facing_classification_claim`: `NONE`" in text
    assert "`clean_classification_pass_claim`: `NONE`" in text
    assert "not ready for client-facing claims" in text


def test_observation_counts_are_preserved():
    text = read(READINESS_DOC)
    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in text


def test_txt_and_exe_remain_rejected_not_ignored():
    text = read(READINESS_DOC)
    assert ".txt` and `.exe` are classified as rejected" in text
    assert ".txt` and `.exe` are not classified as ignored" in text


def test_product_options_are_open_but_not_selected():
    text = read(READINESS_DOC)
    for option in [
        "NON_MEDIA_REJECTED",
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text

    forbidden_selection_claims = [
        "selected_product_semantics`: `NON_MEDIA_REJECTED",
        "selected_product_semantics`: `NON_MEDIA_IGNORED",
        "selected_product_semantics`: `NON_MEDIA_SEPARATE_CATEGORY",
        "selected_product_semantics`: `NON_MEDIA_POLICY_CONFIGURABLE",
        "selected_product_semantics`: `OTHER_NAMED_PRODUCT_BEHAVIOR",
        "selected_product_behavior`: `NON_MEDIA_REJECTED",
        "selected_product_behavior`: `NON_MEDIA_IGNORED",
        "selected_product_behavior`: `NON_MEDIA_SEPARATE_CATEGORY",
        "selected_product_behavior`: `NON_MEDIA_POLICY_CONFIGURABLE",
        "selected_product_behavior`: `OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]
    for claim in forbidden_selection_claims:
        assert claim not in text


def test_phase_is_docs_test_only():
    text = read(READINESS_DOC)
    assert "This phase is docs/test-only." in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read(READINESS_DOC)
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


def test_behavior_changes_remain_blocked():
    text = read(READINESS_DOC)
    for blocked in [
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_readiness_result_allows_only_later_explicit_decision_phase():
    text = read(READINESS_DOC)
    assert "`PASS`" in text
    assert "Only a later explicitly authorized product semantics decision phase may select final product behavior." in text
