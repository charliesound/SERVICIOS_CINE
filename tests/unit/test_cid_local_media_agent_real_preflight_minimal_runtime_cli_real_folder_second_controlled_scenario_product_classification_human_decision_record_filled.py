from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_filled_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.RECORD.FILLED.V1"


def read_doc():
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def test_doc_exists_and_names_phase():
    text = read_doc()
    assert PHASE in text
    assert "Human Decision Record Filled v1" in text


def test_requires_previous_fill_authorization_gate():
    text = read_doc()
    assert "HUMAN_DECISION_RECORD_FILL_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_OPTION_SELECTED" in text
    assert "FILL.AUTHORIZATION.GATE.V1" in text


def test_filled_record_status_is_present():
    text = read_doc()
    assert "HUMAN_DECISION_RECORD_FILLED_WITH_NO_PRODUCT_OPTION_SELECTED" in text
    assert "PRODUCT_CLASSIFICATION_DECISION_REQUIRED" in text
    assert "PRODUCT_SEMANTICS_SELECTION_DEFERRED" in text


def test_no_product_semantics_are_selected():
    text = read_doc()
    assert "`selected_product_semantics`: `NONE`" in text
    assert "`selected_product_behavior`: `NONE`" in text
    assert "Final product semantics remain unselected." in text


def test_no_client_facing_or_clean_pass_claims_are_made():
    text = read_doc()
    assert "`client_facing_classification_claim`: `NONE`" in text
    assert "`clean_classification_pass_claim`: `NONE`" in text
    assert "clean classification PASS claims" in text
    assert "client-facing claims" in text


def test_preserves_rejected_not_ignored_evidence():
    text = read_doc()
    assert "rejected_extension_counts=.exe:1,.txt:1" in text
    assert "ignored_extension_counts={}" in text
    assert "They are not classified as ignored." in text


def test_rationale_defers_product_semantics_selection():
    text = read_doc()
    assert "The safest controlled decision is to preserve the current evidence" in text
    assert "keep final product semantics open" in text
    assert "later explicit product decision phase" in text


def test_does_not_select_any_named_product_behavior():
    text = read_doc()
    for option in [
        "NON_MEDIA_REJECTED",
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text

    forbidden_claims = [
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
    for claim in forbidden_claims:
        assert claim not in text


def test_runtime_scanner_report_and_cli_changes_remain_unauthorized():
    text = read_doc()
    assert "`runtime_change_authorized`: `false`" in text
    assert "`scanner_change_authorized`: `false`" in text
    assert "`report_change_authorized`: `false`" in text
    assert "`cli_change_authorized`: `false`" in text


def test_phase_is_docs_test_only():
    text = read_doc()
    assert "This phase is docs/test-only." in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read_doc()
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


def test_gate_result_is_pass_with_decision_deferred():
    text = read_doc()
    assert "PASS_WITH_DECISION_DEFERRED" in text
    assert "The human decision record is filled." in text
    assert "Final product semantics remain unselected." in text
