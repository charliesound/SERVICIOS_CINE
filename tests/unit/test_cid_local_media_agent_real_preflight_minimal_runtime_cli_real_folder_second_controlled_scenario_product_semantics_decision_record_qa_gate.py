from pathlib import Path

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_record_qa_gate_v1.md"
)

DECISION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_record_v1.md"
)

AUTH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_authorization_gate_v1.md"
)

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

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.RECORD.QA.GATE.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_qa_doc_exists_and_names_phase():
    text = read(QA_DOC)
    assert PHASE in text
    assert "Product Semantics Decision Record QA Gate v1" in text


def test_qa_gate_depends_on_decision_record():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.RECORD.V1" in qa_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_FILLED" in qa_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_FILLED" in decision_text
    assert "PRODUCT_SEMANTICS_DECISION_SELECTED" in qa_text
    assert "PRODUCT_SEMANTICS_DECISION_SELECTED" in decision_text


def test_prior_authorization_chain_exists_and_is_coherent():
    qa_text = read(QA_DOC)
    auth_text = read(AUTH_DOC)
    readiness_text = read(READINESS_DOC)
    filled_qa_text = read(FILLED_QA_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.AUTHORIZATION.GATE.V1" in qa_text
    assert "PRODUCT_SEMANTICS_DECISION_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in auth_text

    assert "PRODUCT.SEMANTICS.DECISION.READINESS.GATE.V1" in qa_text
    assert "PRODUCT_SEMANTICS_DECISION_READINESS_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in readiness_text

    assert "HUMAN.DECISION.RECORD.FILLED.QA.GATE.V1" in qa_text
    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in filled_qa_text


def test_selected_semantics_are_non_media_rejected():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for text in [qa_text, decision_text]:
        assert "NON_MEDIA_REJECTED" in text

    assert "`selected_product_semantics`: `NON_MEDIA_REJECTED`" in decision_text
    assert "`selected_product_behavior`: `NON_MEDIA_REJECTED`" in decision_text


def test_selected_behavior_scope_is_documented_only():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    assert "DOCUMENTED_ONLY_NOT_IMPLEMENTED" in qa_text
    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in decision_text
    assert "The decision record is validated as documentation-only." in qa_text


def test_qa_validation_result_is_pass_documented_only():
    text = read(QA_DOC)
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_QA_GATE_PASS_DOCUMENTED_ONLY" in text
    assert "The product semantics decision record is valid." in text
    assert "The selected product semantics are documented as `NON_MEDIA_REJECTED`." in text


def test_observation_counts_are_preserved():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in qa_text
        assert required in decision_text


def test_txt_and_exe_remain_rejected_not_ignored():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for text in [qa_text, decision_text]:
        assert ".txt` and `.exe` are classified as rejected" in text
        assert ".txt` and `.exe` are not classified as ignored" in text


def test_no_client_facing_or_clean_pass_claims_are_authorized():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for required in [
        "`client_facing_classification_claim`: `NONE`",
        "`clean_classification_pass_claim`: `NONE`",
    ]:
        assert required in qa_text
        assert required in decision_text

    assert "clean classification PASS claims" in qa_text
    assert "client-facing claims" in qa_text


def test_runtime_scanner_report_and_cli_changes_remain_unauthorized():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for required in [
        "`runtime_change_authorized`: `false`",
        "`scanner_change_authorized`: `false`",
        "`report_change_authorized`: `false`",
        "`cli_change_authorized`: `false`",
    ]:
        assert required in qa_text
        assert required in decision_text


def test_non_selected_options_remain_not_selected():
    qa_text = read(QA_DOC)
    decision_text = read(DECISION_DOC)

    for option in [
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in qa_text
        assert option in decision_text

    forbidden_selected_claims = [
        "`selected_product_semantics`: `NON_MEDIA_IGNORED`",
        "`selected_product_semantics`: `NON_MEDIA_SEPARATE_CATEGORY`",
        "`selected_product_semantics`: `NON_MEDIA_POLICY_CONFIGURABLE`",
        "`selected_product_semantics`: `OTHER_NAMED_PRODUCT_BEHAVIOR`",
        "`selected_product_behavior`: `NON_MEDIA_IGNORED`",
        "`selected_product_behavior`: `NON_MEDIA_SEPARATE_CATEGORY`",
        "`selected_product_behavior`: `NON_MEDIA_POLICY_CONFIGURABLE`",
        "`selected_product_behavior`: `OTHER_NAMED_PRODUCT_BEHAVIOR`",
    ]
    for claim in forbidden_selected_claims:
        assert claim not in qa_text
        assert claim not in decision_text


def test_behavior_changes_remain_blocked():
    text = read(QA_DOC)
    for blocked in [
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read(QA_DOC)
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


def test_phase_is_docs_test_only():
    text = read(QA_DOC)
    assert "This phase is docs/test-only." in text
    assert "No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase." in text


def test_gate_result_allows_only_later_separate_authorized_implementation_readiness():
    text = read(QA_DOC)
    assert "`PASS`" in text
    assert "Any later implementation-readiness phase must be explicitly authorized separately." in text
