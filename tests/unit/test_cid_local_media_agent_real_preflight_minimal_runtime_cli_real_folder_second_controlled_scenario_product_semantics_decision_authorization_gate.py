from pathlib import Path

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

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.AUTHORIZATION.GATE.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_authorization_doc_exists_and_names_phase():
    text = read(AUTH_DOC)
    assert PHASE in text
    assert "Product Semantics Decision Authorization Gate v1" in text


def test_authorization_gate_depends_on_readiness_gate():
    auth_text = read(AUTH_DOC)
    readiness_text = read(READINESS_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.READINESS.GATE.V1" in auth_text
    assert "PRODUCT_SEMANTICS_DECISION_READINESS_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in auth_text
    assert "PRODUCT_SEMANTICS_DECISION_READINESS_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in readiness_text


def test_authorization_result_is_present_without_product_behavior_selection():
    text = read(AUTH_DOC)
    assert "PRODUCT_SEMANTICS_DECISION_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in text
    assert "This gate does not select final product semantics." in text
    assert "This gate does not authorize implementation." in text


def test_authorizes_only_later_controlled_decision_documentation():
    text = read(AUTH_DOC)
    assert "A later explicitly controlled product semantics decision phase is authorized." in text
    assert "limited to documenting a product semantics decision" in text
    assert "does not implement scanner behavior, runtime behavior, report behavior, or CLI behavior" in text


def test_current_preserved_state_remains_deferred():
    auth_text = read(AUTH_DOC)
    filled_qa_text = read(FILLED_QA_DOC)

    for required in [
        "PRODUCT_CLASSIFICATION_DECISION_REQUIRED",
        "PRODUCT_SEMANTICS_SELECTION_DEFERRED",
        "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED",
        "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED",
    ]:
        assert required in auth_text

    assert "HUMAN_DECISION_RECORD_FILLED_QA_GATE_PASS_WITH_DECISION_DEFERRED" in filled_qa_text


def test_no_product_semantics_or_behavior_selected():
    text = read(AUTH_DOC)
    assert "`selected_product_semantics`: `NONE`" in text
    assert "`selected_product_behavior`: `NONE`" in text


def test_no_client_facing_or_clean_classification_claims():
    text = read(AUTH_DOC)
    assert "`client_facing_classification_claim`: `NONE`" in text
    assert "`clean_classification_pass_claim`: `NONE`" in text
    assert "clean classification PASS claims" in text
    assert "client-facing claims" in text


def test_observation_counts_are_preserved():
    text = read(AUTH_DOC)
    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in text


def test_txt_and_exe_remain_rejected_not_ignored():
    text = read(AUTH_DOC)
    assert ".txt` and `.exe` are classified as rejected" in text
    assert ".txt` and `.exe` are not classified as ignored" in text


def test_product_options_are_authorized_only_for_later_evaluation():
    text = read(AUTH_DOC)
    assert "Product options authorized for later evaluation only" in text
    for option in [
        "NON_MEDIA_REJECTED",
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text


def test_no_named_product_behavior_is_selected_by_this_gate():
    text = read(AUTH_DOC)
    for forbidden in [
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
    ]:
        assert forbidden not in text


def test_behavior_changes_remain_blocked():
    text = read(AUTH_DOC)
    for blocked in [
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read(AUTH_DOC)
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
    text = read(AUTH_DOC)
    assert "This phase is docs/test-only." in text
    assert "No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase." in text


def test_gate_result_allows_only_later_separate_decision_phase():
    text = read(AUTH_DOC)
    assert "`PASS`" in text
    assert "Only a later explicitly controlled product semantics decision phase may document final product behavior." in text
    assert "That later phase must still remain separate from any implementation phase." in text
