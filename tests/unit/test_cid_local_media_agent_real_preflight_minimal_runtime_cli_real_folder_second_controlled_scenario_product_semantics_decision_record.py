from pathlib import Path

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

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.RECORD.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_decision_record_doc_exists_and_names_phase():
    text = read(DECISION_DOC)
    assert PHASE in text
    assert "Product Semantics Decision Record v1" in text


def test_decision_record_depends_on_authorization_gate():
    decision_text = read(DECISION_DOC)
    auth_text = read(AUTH_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.AUTHORIZATION.GATE.V1" in decision_text
    assert "PRODUCT_SEMANTICS_DECISION_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in decision_text
    assert "PRODUCT_SEMANTICS_DECISION_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in auth_text


def test_prior_readiness_gate_exists_and_remains_unimplemented():
    readiness_text = read(READINESS_DOC)
    assert "PRODUCT_SEMANTICS_DECISION_READINESS_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED" in readiness_text
    assert "This phase is docs/test-only." in readiness_text


def test_product_semantics_decision_is_selected_as_non_media_rejected():
    text = read(DECISION_DOC)
    assert "`decision_record_status`: `PRODUCT_SEMANTICS_DECISION_RECORD_FILLED`" in text
    assert "`decision_status`: `PRODUCT_SEMANTICS_DECISION_SELECTED`" in text
    assert "`selected_product_semantics`: `NON_MEDIA_REJECTED`" in text
    assert "`selected_product_behavior`: `NON_MEDIA_REJECTED`" in text


def test_selected_behavior_is_documented_only_not_implemented():
    text = read(DECISION_DOC)
    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in text
    assert "This phase is documentation-only." in text
    assert "It does not authorize implementation." in text
    assert "Implementation remains unauthorized." in text


def test_no_client_facing_or_clean_pass_claims_are_authorized():
    text = read(DECISION_DOC)
    assert "`client_facing_classification_claim`: `NONE`" in text
    assert "`clean_classification_pass_claim`: `NONE`" in text
    assert "Client-facing claims remain unauthorized." in text
    assert "Clean classification PASS claims remain unauthorized." in text


def test_runtime_scanner_report_and_cli_changes_remain_unauthorized():
    text = read(DECISION_DOC)
    for required in [
        "`runtime_change_authorized`: `false`",
        "`scanner_change_authorized`: `false`",
        "`report_change_authorized`: `false`",
        "`cli_change_authorized`: `false`",
    ]:
        assert required in text


def test_observation_counts_are_preserved():
    text = read(DECISION_DOC)
    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in text


def test_txt_and_exe_remain_rejected_not_ignored():
    text = read(DECISION_DOC)
    assert ".txt` and `.exe` are classified as rejected" in text
    assert ".txt` and `.exe` are not classified as ignored" in text


def test_decision_rationale_preserves_rejected_evidence():
    text = read(DECISION_DOC)
    assert "preserves the observed evidence instead of rewriting it as ignored" in text
    assert "not selected media inputs" in text
    assert "outside the selected media set" in text


def test_non_selected_options_are_listed_but_not_selected():
    text = read(DECISION_DOC)
    for option in [
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text

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
        assert claim not in text


def test_behavior_changes_remain_blocked():
    text = read(DECISION_DOC)
    for blocked in [
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read(DECISION_DOC)
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
    text = read(DECISION_DOC)
    assert "This phase is docs/test-only." in text
    assert "No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase." in text


def test_gate_result_documents_only_and_does_not_implement():
    text = read(DECISION_DOC)
    assert "PASS_WITH_PRODUCT_SEMANTICS_DOCUMENTED_ONLY" in text
    assert "Final product semantics for this controlled scenario are documented as `NON_MEDIA_REJECTED`." in text
    assert "Implementation remains unauthorized." in text
